"""gen_v3.1 re-drive (2026-10-03): every recording of the 6 IL corpora again, WITH ability presses driven, the full
observation (projectiles / effects / kind) and native entity ids (evo/hero FORM ids). Whole corpora are assigned to
the 4 engine slots longest-first (summary.jsonl per output dir must not be shared by two slots). Resumable.
Run on the VM from ~/cb:  nohup setsid python3 run_abil.py > run_abil.log 2>&1 < /dev/null &"""
import json, os, subprocess, threading, time
from collections import defaultdict
os.chdir(os.path.expanduser("~/cb"))
jobs = json.load(open("scratchpad/gauntlet/ext/ability_redrive_manifests/jobs.json"))
by_out = defaultdict(list)
for j in jobs:
    by_out[j["out"]].append(j)
size = {o: sum(len(json.load(open(j["tags"]))) for j in js) for o, js in by_out.items()}
slots = [[] for _ in range(4)]
load = [0] * 4
for o in sorted(size, key=size.get, reverse=True):
    k = load.index(min(load))
    slots[k].append(o)
    load[k] += size[o]
print("assignment", [(k, slots[k], load[k]) for k in range(4)], flush=True)
env = dict(os.environ, PYTHONPATH=os.path.expanduser("~/cb") + ":" + os.path.expanduser("~/cb/research/ext/cr-native-sandbox"))
stamp = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run(k):
    for o in slots[k]:
        for j in by_out[o]:
            cmd = ["python3", "research/sandbox_tools/replay_batch.py", "--crawl", j["crawl"], "--plays-file",
                   j["plays_file"], "--tags", j["tags"], "--out", j["out"], "--port", str(37031 + k), "--seed", "424242",
                   "--level", "11", "--elixir-slack", "40", "--tail-cap", "7200", "--drive-abilities", "--record-full",
                   "--record-native", "--record-every", "20", "--record-plays", "--determinism-every", "0"]
            with open("abil_slot%d.log" % k, "a") as log:
                log.write("=== %s %s -> %s\n" % (stamp(), j["tags"], o))
                log.flush()
                rc = subprocess.call(cmd, stdout=log, stderr=subprocess.STDOUT, env=env)
                log.write("=== rc %d\n" % rc)
    open("abil_slot%d.done" % k, "w").write(stamp())


ts = [threading.Thread(target=run, args=(k,)) for k in range(4)]
for t in ts:
    t.start()
for t in ts:
    t.join()
open("ABIL_DONE", "w").write(stamp())
