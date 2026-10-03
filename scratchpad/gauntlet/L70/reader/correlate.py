"""Align captured live bytes with existing bot logs; writes only reader/ outputs."""
import collections
import datetime
import json
from pathlib import Path
import sys
from inspect_capture import frames,summarize
from probe_host import i32,u64

HERE=Path(__file__).resolve().parent
LOGS=HERE.parents[1]/'L68'/'live_reader'
CARDS={'Knight':(26000000,13000000),'Tesla':(27000006,13000102),'Rocket':(28000003,),'Log':(28000011,),'Tornado':(28000012,)}

def correlate(paths):
    anchor=json.loads((HERE/'clock_anchor.json').read_text())
    delta=(anchor['host_before']+anchor['host_after'])/2-float(anchor['uptime'].split()[0])
    allframes=[f for p in paths for f in frames(p)]
    first=min(f['wall_time'] for f in allframes); last=max(f['wall_time'] for f in allframes)
    logs={}; pairs=[]
    for p in sorted(LOGS.glob('live_play_*.jsonl')):
        stamp=datetime.datetime.strptime(p.stem.removeprefix('live_play_'),'%Y%m%d_%H%M%S').timestamp()
        if stamp<first-900 or stamp>last+60: continue
        pending=None; ordinal=collections.Counter(); evs=[]
        for line in p.read_text().splitlines():
            try: e=json.loads(line)
            except json.JSONDecodeError: continue
            if e.get('event')=='play': pending=e
            if e.get('event') in ('confirmed','unconfirmed') and pending and e.get('name')==pending.get('name'):
                if e['event']=='confirmed': ordinal[e['name']]+=1
                pair=dict(log=p.name,play=pending,result=e,ordinal=ordinal[e['name']])
                pairs.append(pair); pending=None
            if e.get('event') in ('start','play','confirmed','unconfirmed','end','stop'): evs.append(e)
        logs[p.name]=evs
    # Clock fit must agree in both tick and device monotonic time. A stale battle
    # pointer/address cannot associate frames with an unrelated match.
    bybattle=collections.defaultdict(list)
    for f in allframes: bybattle[f['battle']].append(f)
    battle_logs={}
    fits=[]
    for battle,fs in bybattle.items():
        errors=collections.defaultdict(list)
        for f in fs:
            for p in pairs:
                e=p['play']; dt=f['wall_time']-delta-e['t_dev']
                if abs(dt)<500:
                    errors[p['log']].append(abs((f['tick']-e['tick'])-20*dt))
        med={k:sorted(v)[len(v)//2] for k,v in errors.items()}
        if med:
            name=min(med,key=med.get)
            if med[name]<30: battle_logs[battle]=name
            fits.append(dict(battle=battle,log=name,median_tick_error=med[name],accepted=med[name]<30))
    summary=summarize(paths)
    evidence=[]; evo=[]
    for o in summary['lifetimes']:
        name=battle_logs.get(o['battle'])
        if not name: continue
        group=next((k for k,v in CARDS.items() if o['card_id'] in v),None)
        if not group: continue
        samples=o['samples']; first_tick=samples[0]['tick']
        candidates=[p for p in pairs if p['log']==name and p['play']['name']==group and p['result']['event']=='confirmed' and -10<=first_tick-p['result']['tick']<=150]
        if not candidates: continue
        p=min(candidates,key=lambda p:abs(first_tick-p['result']['tick']))
        xy=p['result']['intended']; side=o['side']
        native=[round(xy[0]*18000),round((1-xy[1])*32000)] if side==0 else [round((1-xy[0])*18000),round(xy[1]*32000)]
        rec=dict(log=name,battle=o['battle'],card=group,card_id=o['card_id'],data_name=o['name'],side=side,address=o['address'],generation=o['category'],vtable=o['vtable_rva'],play_tick=p['play']['tick'],confirmed_tick=p['result']['tick'],cast_ordinal=p['ordinal'],native_target=native,samples=[])
        for s in samples:
            raw=bytes.fromhex(s['raw'])
            sample=dict(capture=s['capture'],tick=s['tick'],seq=s['seq'],coherent=s['coherent'],x=s['x'],y=s['y'])
            if o['category']//1000000==4: sample.update(target_x=i32(raw,0x120),target_y=i32(raw,0x124))
            elif o['category']//1000000==3: sample.update(remaining_ms=i32(raw,0x100),life_override_ms_raw=i32(raw,0x114))
            rec['samples'].append(sample)
        if group in ('Knight','Tesla') and o['category']//1000000==5:
            rec['evo_by_card_table']=int(o['card_id']//1000000==13)
            rec['evo_by_data_name']=int('ev1' in o['name'].lower()) if o['name'] else None
            rec['cycle_hypothesis_evo']=int(p['ordinal']%3==0)
            evo.append(rec)
        elif o['category']//1000000 in (3,4): evidence.append(rec)
    result=dict(inputs=[str(p) for p in paths],clock_host_minus_uptime=delta,clock_uncertainty_s=(anchor['host_after']-anchor['host_before'])/2,frames=summary['frames'],coherent_frames=summary['coherent_frames'],missing_object_reads=summary['missing_object_reads'],battle_fits=fits,cast_evidence=evidence,evo_evidence=evo,log_events=logs)
    (HERE/'correlation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(frames=result['frames'],battle_fits=fits,spell_objects=collections.Counter(e['card'] for e in evidence),evo_bodies={f'{card}/{form}':sum(e['card']==card and e['evo_by_card_table']==form for e in evo) for card in ('Knight','Tesla') for form in (0,1)}),indent=2))
    return result

if __name__=='__main__': correlate(sys.argv[1:])
