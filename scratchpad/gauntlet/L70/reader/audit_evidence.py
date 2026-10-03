"""Recount evidence and verify bounds directly; no device access or compilation."""
import collections
import hashlib
import json
from pathlib import Path
import statistics
from inspect_capture import frames
from probe_host import i32,u64

HERE=Path(__file__).resolve().parent
paths=[HERE/'capture_a.jsonl',HERE/'capture_b.jsonl']
stats=[]; countdowns=[]; tracks=collections.defaultdict(list); candidates={}
for path in paths:
    metadata=None; rows=[]
    for line in path.read_text().splitlines():
        row=json.loads(line)
        if row['event']=='meta': metadata=row
        else: rows.append(row)
    starts=[r['wall_time']-r['duration'] for r in rows]
    diffs=[b-a for a,b in zip(starts,starts[1:])]
    assert metadata['interval']>=.5
    # Windows monotonic and wall clocks have different rounding; tolerance 3ms.
    assert min(diffs)>=.497, min(diffs)
    stats.append(dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      batches=len(rows),read_requests=sum(len(r['blocks']) for r in rows),
                      failed_read_requests=sum(h is None for r in rows for a,n,h,e in r['blocks']),
                      min_start_interval_s=min(diffs),median_start_interval_s=statistics.median(diffs),
                      adb_bytes=rows[-1]['adb_bytes'],adb_calls=rows[-1]['adb_calls'],
                      estimated_kib_per_s=rows[-1]['adb_bytes']/(starts[-1]-starts[0])/1024,
                      max_batch_duration_s=max(r['duration'] for r in rows)))
    for f in frames(path):
        for o in f['objects']:
            if o['category']//1000000==3 and f['coherent']:
                tracks[(f['battle'],o['address'],o['category'])].append((f['tick'],i32(bytes.fromhex(o['raw']),0x100),o['name']))
        for c in f['containers']:
            for parent,off in c['paths']:
                key=f'{parent}+{off:#x}/{c["layout"]}/pointer+{c.get("pointer_offset",0):#x}'
                rec=candidates.setdefault(key,dict(batches=0,vtable_rvas=collections.Counter()))
                rec['batches']+=1
                for a in c['objects']:
                    b=f['blocks'].get(a,b'')
                    if len(b)>=8 and 0<u64(b)-f['base']<0x3000000:
                        rec['vtable_rvas'][hex(u64(b)-f['base'])]+=1
for key,rows in tracks.items():
    for (t0,v0,n0),(t1,v1,n1) in zip(rows,rows[1:]):
        if 0<t1-t0<=40 and 0<=v0<1000000 and 0<=v1<1000000:
            countdowns.append(dict(battle=key[0],address=key[1],generation=key[2],name=n1 or n0,
                                   ticks=[t0,t1],timers=[v0,v1],matches_50ms=v1-v0==-50*(t1-t0)))
corr=json.loads((HERE/'correlation.json').read_text())
evo_counts={}
for card in ('Knight','Tesla'):
    for form in (0,1):
        es=[e for e in corr['evo_evidence'] if e['card']==card and e['evo_by_card_table']==form]
        verified=[e for e in es if e['evo_by_data_name']==form and e['cycle_hypothesis_evo']==form and any(s['coherent'] for s in e['samples'])]
        evo_counts[f'{card}/{form}']=dict(matched_bodies=len(es),name_cycle_coherent_verified=len(verified),examples=[dict(log=e['log'],tick=e['samples'][0]['tick'],address=hex(e['address']),generation=e['generation'],cast_ordinal=e['cast_ordinal']) for e in verified[:5]])
        assert len(verified)>=5,(card,form,len(verified))
report=dict(captures=stats,decoded_frames=corr['frames'],tick_coherent_frames=corr['coherent_frames'],
            missing_object_observations=corr['missing_object_reads'],evo_counts=evo_counts,
            spell_counts=dict(collections.Counter(e['card'] for e in corr['cast_evidence'] if e['card'] in ('Rocket','Log','Tornado'))),
            effect_countdown_pairs=len(countdowns),effect_countdown_matching=sum(e['matches_50ms'] for e in countdowns),
            effect_countdowns=countdowns,container_candidates=candidates,
            source_sha256=hashlib.sha256((HERE/'live_sampler2.c').read_bytes()).hexdigest())
assert all(report['spell_counts'].get(card,0)>=1 for card in ('Rocket','Log','Tornado'))
assert report['effect_countdown_pairs']>0 and report['effect_countdown_matching']==report['effect_countdown_pairs']
(HERE/'evidence_audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('effect_countdowns','container_candidates')},indent=2))
print('EVIDENCE_AUDIT_PASSED')
