#!/bin/bash
# Overnight ladder run (owner 2026-10-02 evening): league1c_u0075 (the only RL checkpoint with a measured gain), tau 0.35
# (the live setting since 09-30), Trophy Road via ladder_nav (Play Again; after the day's 4th win OK -> chests -> Battle),
# overlaid replays OFF except one 60-s clip to Discord at the start and every 30 min. Restarts after a stop, max 5,
# each stop posted to Discord. Ends at 09:00 or when $L/STOP exists (touch it to stop between matches).
cd /c/Users/benpe/ClashBot
L=scratchpad/gauntlet/L70/live
PY=icebow/.venv/Scripts/python.exe
post() { printf '%s\n' "$1" > $L/_msg.txt; $PY scratchpad/gauntlet/L69/discord/post.py $L/_msg.txt >> $L/supervisor.log 2>&1; }
( sleep $(( $(date -d 'tomorrow 09:00' +%s) - $(date +%s) )); touch $L/STOP ) &
post "ClashAI overnight ladder run starting $(date +%H:%M): league1c_u0075, tau 0.35, auto Play Again + daily chests, clip now and every 30 min. Note: gen_v2 training shares the GPU until ~23:30, decisions ~100 ms instead of ~40."
for i in 1 2 3 4 5 6; do
  [ -e $L/STOP ] && break
  echo "[sup] start $i $(date)" >> $L/supervisor.log
  $PY -u scratchpad/gauntlet/L68/live_reader/live_play.py --ladder --matches 400 \
    --ckpt icebow/data/bench/rl_royale/league1c/league1c_u0075.pt --tau 0.35 --max-seconds 600 \
    --clip-every 1800 --overlay reader --stop-file $L/STOP >> $L/overnight.out 2>&1
  rc=$?
  why=$(grep -aE '\[live\] run stopped|\[nav\] run stopped|\[ladder\] STOP|stop file' $L/overnight.out | tail -1)
  echo "[sup] exit $rc $(date): $why" >> $L/supervisor.log
  st=$(cat scratchpad/gauntlet/L68/live_reader/ladder_state.json 2>/dev/null)
  [ -e $L/STOP ] && break
  [ $i -lt 6 ] && post "ClashAI live run stopped $(date +%H:%M) (rc $rc): ${why:-no reason logged}. State $st. Restart $i/5 in 60 s." && sleep 60
done
post "ClashAI overnight ladder run ended $(date +%H:%M). Tally $(cat scratchpad/gauntlet/L68/live_reader/ladder_state.json 2>/dev/null)"
echo "[sup] done $(date)" >> $L/supervisor.log
