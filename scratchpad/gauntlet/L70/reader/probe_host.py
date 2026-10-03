"""Read-only, bounded, <=2 Hz adb/re_peek collector. No game calls or input.

One adb call per batch: stdin -> re_req_*; re_peek -> re_out_*; cat result.
Dependent pointers resolve in successive batches; every block has its own batch
number. Never mistake the accumulated discovery cache for an atomic snapshot.
"""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import time

HERE = Path(__file__).resolve().parent
ADB = r"C:\Program Files\Netease\MuMuPlayer\nx_device\15.0\shell\adb.exe"

def u64(b, o=0):
    return struct.unpack_from('<Q', b, o)[0] if len(b) >= o+8 else 0

def i32(b, o=0):
    return struct.unpack_from('<i', b, o)[0] if len(b) >= o+4 else -1

def parse_peek(text):
    rows = []
    for line in text.splitlines():
        p = line.split()
        if len(p) < 3:
            raise ValueError('truncated re_peek line: '+repr(line))
        a, n = int(p[0], 0), int(p[1], 0)
        if p[2] == 'ERR':
            rows.append((a, n, None, int(p[3])))
        else:
            b = bytes.fromhex(p[2])
            if len(b) != n:
                raise ValueError('short re_peek payload')
            rows.append((a, n, b, None))
    return rows

class Peek:
    def __init__(self, tag):
        self.tag = tag
        self.calls = 0
        self.bytes = 0
        self.env = dict(os.environ, MSYS_NO_PATHCONV='1')
        p = self.adb('shell', 'pidof com.supercell.clashroyale').strip().split()
        if len(p) != 1 or not p[0].isdigit():
            raise RuntimeError('ambiguous/missing PID: '+repr(p))
        self.pid = int(p[0])
        self.maps_text = self.adb('shell', f'cat /proc/{self.pid}/maps')
        self.maps = []
        libg = []
        for line in self.maps_text.splitlines():
            p = line.split()
            lo, hi = (int(x, 16) for x in p[0].split('-'))
            self.maps.append((lo, hi, p[1]))
            if '/libg.so' in line:
                libg.append((lo, hi, int(p[2],16)))
        if not libg:
            raise RuntimeError('libg.so not mapped')
        self.base = min(a-o for a,b,o in libg)
        self.libg_ranges = [(a,b) for a,b,o in libg]

    def adb(self, *args, input=None):
        p = subprocess.run([ADB, '-s', '127.0.0.1:16384', *args], input=input,
                           text=True, capture_output=True, timeout=20, env=self.env)
        self.calls += 1
        self.bytes += len(p.stdout)+len(p.stderr)+(len(input) if input else 0)
        if p.returncode:
            raise RuntimeError(f'adb exit {p.returncode}: {p.stderr.strip()} {p.stdout.strip()}')
        return p.stdout

    def valid(self, a, n=8):
        return a >= 0x10000 and not a & 7 and any(lo <= a and a+n <= hi and perm[0]=='r' for lo,hi,perm in self.maps)

    def in_libg(self, a):
        return any(lo <= a < hi for lo,hi in self.libg_ranges)

    def batch(self, req):
        req = list(req)
        if not req or len(req)>1024 or sum(n for a,n in req)>262144:
            raise ValueError('batch budget exceeded/empty')
        payload = ''.join(f'{a:#x} {n}\n' for a,n in req)
        name = '/data/local/tmp/re_'+self.tag
        out = self.adb('shell', f'cat > {name}_req; /data/local/tmp/re_peek {self.pid} < {name}_req > {name}_out && cat {name}_out', input=payload)
        rows = parse_peek(out)
        if [(a,n) for a,n,b,e in rows] != req:
            raise RuntimeError('re_peek response/request mismatch')
        return rows

def collect(seconds, interval, tag, census_every=1):
    peek = Peek(tag)
    cache = {}
    output = HERE / (tag+'.jsonl')
    def get(a): return cache.get(a, b'')
    def ptr(a, o=0): return u64(get(a),o)
    start = time.monotonic()
    with output.open('x', encoding='utf-8') as f:
        f.write(json.dumps(dict(event='meta', pid=peek.pid, libg_base=peek.base,
                               libg_ranges=peek.libg_ranges, maps=peek.maps_text,
                               interval=interval, wall_time=time.time()))+'\n')
        seq=0
        while time.monotonic()-start < seconds:
            t = time.monotonic()
            req = {}
            def add(a,n):
                if peek.valid(a,n): req[a]=max(req.get(a,0),n)
            glob=peek.base+0x1aeef98
            add(glob,8)
            root=ptr(glob); add(root,0x60)
            context=ptr(root,0x18); add(context,0xa0)
            battle=ptr(context,0x90); add(battle,0x600)
            ps=ptr(battle,0xa8); add(ps,0x600)
            registry=ptr(ps,8); add(registry,0x100)
            collection=ptr(registry,0x40); add(collection,0x30)
            data=ptr(collection,8); count=i32(get(collection),0x14)
            if 0<count<=2048: add(data, count*8)
            entities=[]
            if 0<count<=2048:
                for j in range(min(count,len(get(data))//8)):
                    a=ptr(data,j*8)
                    if peek.valid(a,0x200):
                        add(a,0x200); entities.append(a)
                        b=get(a)
                        # Character data, component vectors, effect data.
                        for off,n in ((0x10,0x200),(0x18,0x80),(0x48,0x200)):
                            add(u64(b,off),n)
                        for off in (0x10,0x48):
                            d=get(u64(b,off)); length=i32(d,0x2c)
                            if 8<=length<=128: add(u64(d,0x30),136)
            # Bounded first-hop container census. Scan *all* aligned slots in
            # 0x600 windows, not arbitrary memory or recursive pointer graphs.
            # Four consecutive census batches resolve header -> array -> object.
            census = census_every == 1 or seq % census_every < 4
            parents=[('battle',battle),('player_state',ps),('registry',registry)] if census else []
            headers={}
            for label,parent in parents:
                b=get(parent)
                for off in range(0,min(len(b),0x600)-7,8):
                    a=u64(b,off)
                    if peek.valid(a,0x30) and not peek.in_libg(a):
                        headers.setdefault(a,[]).append([label,off])
            candidates=[]
            for a,paths in list(headers.items())[:160]:
                add(a,0x30); b=get(a)
                # Supercell vectors: pointer, capacity, count; plus STL triple.
                for off in (0,8,0x10,0x18):
                    p=u64(b,off); cap=i32(b,off+8); n=i32(b,off+12)
                    if peek.valid(p) and 0<n<=256 and n<=cap<=4096:
                        add(p,n*8); objs=[]
                        for j in range(min(n,len(get(p))//8)):
                            obj=ptr(p,j*8)
                            if peek.valid(obj,0x200):
                                add(obj,0x200)
                                if peek.in_libg(ptr(obj)): objs.append(obj)
                        candidates.append(dict(header=a,paths=paths,pointer_offset=off,data=p,count=n,objects=objs,layout='ptr_cap_count'))
                p,end,cap=(u64(b,o) for o in (0,8,16))
                if peek.valid(p) and p<end<=cap and (end-p)%8==0 and end-p<=2048 and cap-p<=32768:
                    add(p,end-p)
                    objs=[]
                    for j in range(min((end-p)//8,len(get(p))//8)):
                        obj=ptr(p,j*8)
                        if peek.valid(obj,0x200):
                            add(obj,0x200)
                            if peek.in_libg(ptr(obj)): objs.append(obj)
                    candidates.append(dict(header=a,paths=paths,data=p,count=(end-p)//8,objects=objs,layout='stl_triple'))
            # Read tick before/after current request set; chain and registry in
            # every frame. Cache is only a request planner; offline decoding uses
            # current successful blocks exclusively.
            requests=list(req.items())
            if battle and peek.valid(battle+0x60,4): requests=[(battle+0x60,4)]+requests+[(battle+0x60,4)]
            rows=peek.batch(requests)
            blocks=[]
            for a,n,b,e in rows:
                if b is None: cache.pop(a,None)
                else: cache[a]=b
                blocks.append([a,n,b.hex() if b is not None else None,e])
            frame=dict(event='batch',seq=seq,wall_time=time.time(),duration=time.monotonic()-t,
                       planned_chain=dict(root=root,context=context,battle=battle,player_state=ps,registry=registry,collection=collection,data=data,count=count),
                       planned_entities=entities,container_candidates=candidates,blocks=blocks,
                       adb_calls=peek.calls,adb_bytes=peek.bytes)
            f.write(json.dumps(frame,separators=(',',':'))+'\n'); f.flush()
            if seq%30==0:
                cats={}
                for a in entities:
                    b=get(a); key=f'{ptr(a)-peek.base:#x}/{i32(b,8)//1000000}'
                    cats[key]=cats.get(key,0)+1
                print(json.dumps(dict(seq=seq,tick=i32(get(battle),0x60),objects=len(entities),classes=cats,bytes=peek.bytes)),flush=True)
            seq+=1
            time.sleep(max(0,interval-(time.monotonic()-t)))
    print(json.dumps(dict(output=str(output),frames=seq,adb_calls=peek.calls,adb_bytes=peek.bytes)),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--seconds',type=float,default=600)
    p.add_argument('--interval',type=float,default=1.0)
    p.add_argument('--tag',default='probe_'+time.strftime('%Y%m%d_%H%M%S'))
    p.add_argument('--census-every',type=int,default=1)
    a=p.parse_args()
    if a.interval<0.5 or a.seconds<=0 or a.census_every<1 or not a.tag.replace('_','').isalnum(): p.error('invalid rate/duration/tag')
    collect(a.seconds,a.interval,a.tag,a.census_every)
