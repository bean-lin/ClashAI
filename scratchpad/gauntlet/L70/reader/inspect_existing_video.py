"""Extract a few frames from an ALREADY RECORDED host video. No adb/capture/GPU."""
import json
from pathlib import Path
import cv2
from inspect_capture import frames

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
log=REPO/'scratchpad/gauntlet/L68/live_reader/live_play_20261003_124226.jsonl'
events=[json.loads(s) for s in log.read_text().splitlines()]
recording=next(e['segments'] for e in events if e['event']=='recording')
logged=[e for e in events if e['event']=='frame']
selected={}
for f in frames(HERE/'capture_a.jsonl'):
    if f['battle']!=0x74b519b83880: continue
    for o in f['objects']:
        if o['side']==0 and o['category']//1000000==5 and 13000000<=o['card_id']<14000000 and o['name']:
            selected.setdefault(o['name'],(f,o))
    if len(selected)>=2: break
meta=[]
for index,(name,(f,o)) in enumerate(selected.items()):
    nearest=min(logged,key=lambda e:abs(e['tick']-f['tick']))
    t=nearest['t_dev']+(f['tick']-nearest['tick'])*.05
    segment,begin=max((s for s in recording if s[1]<=t),key=lambda s:s[1])
    video=Path(segment)
    cap=cv2.VideoCapture(str(video)); cap.set(cv2.CAP_PROP_POS_MSEC,(t-begin)*1000)
    ok,img=cap.read(); pts=cap.get(cv2.CAP_PROP_POS_MSEC)/1000; cap.release()
    if not ok: raise RuntimeError('existing video decode failed')
    target=HERE/f'video_evidence_{index}.png'
    if target.exists(): raise FileExistsError(target)
    cv2.imwrite(str(target),img)
    meta.append(dict(image=target.name,video=str(video),video_seconds=pts,requested_seconds=t-begin,
                     tick=f['tick'],log_tick=nearest['tick'],name=name,address=hex(o['address']),
                     side=o['side'],card_id=o['card_id'],x=o['x'],y=o['y'],
                     caveat='Encoder startup delay is not independently calibrated; image is supporting evidence.'))
(HERE/'video_evidence.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(meta,indent=2))
