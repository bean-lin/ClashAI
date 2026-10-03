"""Lead-side comparison of independently collected v1/v2 DEFAULT JSON streams.
Reports raw byte equality separately; same-tick payload comparison strips only
process-specific timing/identity. This is not a byte-equal formatter fixture test.
"""
import argparse
import collections
import json
from pathlib import Path

VOLATILE={'reader_pid','sequence','sample_monotonic_us','read_us'}
def load(path):
    rows=collections.defaultdict(list)
    for line in Path(path).read_text().splitlines():
        f=json.loads(line)
        if not f.get('battle_active') or not f.get('coherent'): continue
        if 'extension' in f or 'projectiles' in f or 'effects' in f or any('evo' in e for e in f.get('entities',[])):
            raise ValueError('default comparison received extended fields')
        key=(f['pid'],f['chain']['battle'],f['game_tick'])
        rows[key].append({k:v for k,v in f.items() if k not in VOLATILE})
    return rows

def main():
    p=argparse.ArgumentParser(); p.add_argument('v1'); p.add_argument('v2'); p.add_argument('--min-pairs',type=int,default=100); a=p.parse_args()
    old,new=load(a.v1),load(a.v2); common=old.keys()&new.keys(); mismatch=[]
    for k in common:
        if not any(x==y for x in old[k] for y in new[k]): mismatch.append(k)
    report=dict(raw_byte_equal=Path(a.v1).read_bytes()==Path(a.v2).read_bytes(),
                volatile_exclusions=sorted(VOLATILE),common_ticks=len(common),
                mismatching_ticks=len(mismatch),examples=mismatch[:10],
                v1_unpaired_ticks=len(old.keys()-new.keys()),v2_unpaired_ticks=len(new.keys()-old.keys()))
    print(json.dumps(report,indent=2))
    if mismatch or len(common)<a.min_pairs: raise SystemExit(1)

if __name__=='__main__': main()
