"""Pure Python decoder of NEW fields, from re_peek bytes (never calls adb).

Usage: python -B reference_fields.py --capture capture_a.jsonl --out decoded_a.jsonl
   or: python -B reference_fields.py --peek re_output.txt --base 0x... --out one.jsonl
Output is a reference extension, not a replacement for the complete v1 frame.
Missing reads are explicit; no cache is used to fill missing current bytes.
"""
import argparse
import json
from pathlib import Path
from probe_host import parse_peek,i32,u64

PROJECTILE_VT=0x19f7370
AREA_VT=0x19f6a28

class MissingRead(Exception): pass

class Memory:
    def __init__(self, rows):
        self.rows=list(rows)
        self.blocks={a:b for a,n,b,e in self.rows if b is not None}
    def read(self,a,n):
        b=self.blocks.get(a)
        if b is not None and len(b)>=n: return b[:n]
        for p,b in self.blocks.items():
            if p<=a and a+n<=p+len(b): return b[a-p:a-p+n]
        raise MissingRead(f'{a:#x}+{n:#x}')
    def ptr(self,a): return u64(self.read(a,8))
    def integer(self,a): return i32(self.read(a,4))

def evo(card_id): return int(13000000<=card_id<14000000)

def decode_object(memory,base,address):
    raw=memory.read(address,0x128)
    category=i32(raw,8); vt=u64(raw)-base; side=i32(raw,0x78)
    card=i32(raw,0xac); x=i32(raw,0x7c); y=i32(raw,0x80)
    if side not in (0,1): return None,None
    if 5000000<=category<6000000:
        kind=i32(raw,0x30); level=i32(raw,0x120)
        supported=card==-1 or 20000000<=card<1000000000 or evo(card)
        if not (10<=kind<=20 and 0<=level<=16 and 0<=x<=18000 and 0<=y<=32000 and supported): return None,None
        return 'entities',dict(address=hex(address),card_id=card,evo=evo(card))
    obj=dict(address=hex(address),generation_key=category,vtable_rva=hex(vt),side=side,x=x,y=y,card_id=card)
    if 4000000<=category<5000000 and vt==PROJECTILE_VT:
        obj.update(target_x=i32(raw,0x120),target_y=i32(raw,0x124),
                   source=hex(u64(raw,0x100)) if u64(raw,0x100) else None,
                   target=hex(u64(raw,0x108)) if u64(raw,0x108) else None,
                   attached_owner=hex(u64(raw,0x118)) if u64(raw,0x118) else None)
        return 'projectiles',obj
    if 3000000<=category<4000000 and vt==AREA_VT:
        data=u64(raw,0x48); timer=i32(raw,0x100); override=i32(raw,0x114)
        # Measured live countdown, not the other build's elapsed-time formula.
        obj.update(data_ptr=hex(data),level_raw=i32(raw,0xfc),timer_ms_raw=timer,
                   life_override_ms_raw=override,remaining_ms=timer if timer>=0 else None)
        return 'effects',obj
    return ('unknown_nonunits',obj) if 3000000<=category<5000000 else (None,None)

def decode(rows,base):
    m=Memory(rows)
    out=dict(game_tick=-1,coherent=False,entities=[],projectiles=[],effects=[],
             extension=dict(build=160402012,valid=False,evo_basis='card_id_table_13',unknown_nonunits=0,read_errors=0),missing=[])
    try:
        root=m.ptr(base+0x1aeef98); context=m.ptr(root+0x18); battle=m.ptr(context+0x90)
        ps=m.ptr(battle+0xa8); reg=m.ptr(ps+8); collection=m.ptr(reg+0x40)
        data=m.ptr(collection+8); count=m.integer(collection+0x14)
        out['game_tick']=m.integer(battle+0x60)
        if not 0<=count<=2048: raise ValueError('invalid registry count')
        try: arr=m.read(data,count*8) if count else b''
        except MissingRead:
            arr=m.blocks.get(data,b'')[:count*8]
            out['missing'].append(f'registry suffix: {count-len(arr)//8} uncaptured entries')
        ticks=[i32(b) for a,n,b,e in m.rows if a==battle+0x60 and n==4 and b is not None]
        out['coherent']=len(ticks)==2 and ticks[0]==ticks[1] and ticks[1]==out['game_tick']
        for index in range(len(arr)//8):
            a=u64(arr,index*8)
            try: key,value=decode_object(m,base,a)
            except MissingRead as e:
                out['missing'].append(str(e)); continue
            if key=='unknown_nonunits': out['extension'][key]+=1
            elif key: out[key].append(value)
    except (MissingRead,ValueError) as e: out['missing'].append(str(e))
    out['extension']['read_errors']=len(out['missing'])
    out['extension']['valid']=out['coherent'] and not out['missing']
    # Preserve partial decoded evidence for research, unlike C emission which
    # suppresses nonunits when the complete frame is invalid. Consumers MUST
    # inspect extension.valid. This deliberate diagnostic difference is explicit.
    return out

def run(args):
    dest=Path(args.out).resolve()
    if dest.parent!=Path(__file__).resolve().parent: raise ValueError('output outside reader write set')
    with dest.open('x',encoding='utf-8') as out:
        if args.peek:
            rows=parse_peek(Path(args.peek).read_text())
            out.write(json.dumps(decode(rows,args.base))+'\n')
        else:
            base=None
            with Path(args.capture).open() as src:
                for line in src:
                    f=json.loads(line)
                    if f['event']=='meta': base=f['libg_base']; continue
                    rows=[(a,n,bytes.fromhex(h) if h is not None else None,e) for a,n,h,e in f['blocks']]
                    decoded=decode(rows,base); decoded['seq']=f['seq']
                    out.write(json.dumps(decoded,separators=(',',':'))+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--capture'); g.add_argument('--peek'); p.add_argument('--base',type=lambda s:int(s,0))
    p.add_argument('--out',required=True); a=p.parse_args()
    if a.peek and a.base is None: p.error('--base required with --peek')
    run(a)
