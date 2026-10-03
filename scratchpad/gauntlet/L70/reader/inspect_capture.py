"""Offline evidence extraction. No adb. Discard unregistered/reused objects."""
import collections
import json
from pathlib import Path
import sys
from probe_host import i32,u64

HERE=Path(__file__).resolve().parent

def frames(path):
    base=None
    with Path(path).open() as f:
        for line in f:
            try: row=json.loads(line)
            except json.JSONDecodeError: continue  # active collector's last partial line
            if row['event']=='meta':
                base=row['libg_base']; continue
            blocks={a:bytes.fromhex(h) for a,n,h,e in row['blocks'] if h is not None}
            def read(a,n):
                if a in blocks and len(blocks[a])>=n: return blocks[a][:n]
                for p,b in blocks.items():
                    if p<=a and a+n<=p+len(b): return b[a-p:a-p+n]
                return b''
            def ptr(a): return u64(read(a,8))
            root=ptr(base+0x1aeef98); context=ptr(root+0x18); battle=ptr(context+0x90)
            ps=ptr(battle+0xa8); reg=ptr(ps+8); col=ptr(reg+0x40)
            data=ptr(col+8); n=i32(read(col+0x14,4)); tick=i32(read(battle+0x60,4))
            if not (0<=n<=2048): continue
            ticks=[i32(bytes.fromhex(h)) for a,l,h,e in row['blocks'] if a==battle+0x60 and h]
            objects=[]; missing=0
            arr=read(data,n*8)
            if len(arr)!=n*8:
                # A growing registry can exceed the previous batch's request
                # length. Its captured prefix still proves membership; count
                # the uncaptured suffix explicitly instead of dropping evidence.
                arr=blocks.get(data,b'')[:n*8]
                missing+=n-len(arr)//8
            for j in range(len(arr)//8):
                addr=u64(arr,j*8); raw=read(addr,0x128)
                if not raw: missing+=1; continue
                vt=u64(raw)-base; cat=i32(raw,8)
                if not (0<vt<0x3000000 and 3000000<=cat<6000000): continue
                # Recover the longest captured raw window.
                raw=blocks.get(addr,raw)
                dptr=u64(raw,0x48); db=read(dptr,0x44); name=''
                length=i32(db,0x2c)
                if 0<length<8: name=db[0x30:0x30+length].decode('ascii','replace')
                elif 8<=length<=128: name=read(u64(db,0x30),length).decode('ascii','replace')
                o=dict(address=addr,vtable_rva=hex(vt),category=cat,side=i32(raw,0x78),x=i32(raw,0x7c),y=i32(raw,0x80),card_id=i32(raw,0xac),kind=i32(raw,0x30),data_ptr=dptr,data_id=i32(db,0x40),name=name,raw=raw.hex())
                objects.append(o)
            yield dict(capture=Path(path).name,seq=row['seq'],wall_time=row['wall_time'],duration=row['duration'],battle=battle,tick=tick,ticks=ticks,coherent=len(ticks)==2 and ticks[0]==ticks[1],objects=objects,missing=missing,blocks=blocks,base=base,containers=row['container_candidates'])

def summarize(paths):
    lifetimes={}; counts=collections.Counter(); missing=0; nf=0; coherent=0
    for path in paths:
        for f in frames(path):
            nf+=1; missing+=f['missing']; coherent+=f['coherent']
            for o in f['objects']:
                counts[(o['vtable_rva'],o['category']//1000000,o['card_id'],o['name'])]+=1
                k=(f['battle'],o['address'],o['category'])
                rec=lifetimes.setdefault(k,dict(battle=f['battle'],address=o['address'],category=o['category'],vtable_rva=o['vtable_rva'],card_id=o['card_id'],side=o['side'],name=o['name'],samples=[]))
                if o['name']: rec['name']=o['name']
                rec['samples'].append(dict(capture=f['capture'],tick=f['tick'],wall_time=f['wall_time'],coherent=f['coherent'],seq=f['seq'],x=o['x'],y=o['y'],raw=o['raw']))
    return dict(frames=nf,coherent_frames=coherent,missing_object_reads=missing,classes=[dict(vtable=k[0],series=k[1],card=k[2],name=k[3],samples=v) for k,v in counts.most_common()],lifetimes=list(lifetimes.values()))

if __name__=='__main__':
    result=summarize(sys.argv[1:])
    dest=HERE/'analysis_latest.json'
    dest.write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='lifetimes'},indent=2))
    print('wrote',dest)
