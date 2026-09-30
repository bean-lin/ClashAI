#!/bin/bash
# Owner-chosen PERMANENT deletions, 2026-09-29 (~16 GB). Run from Git Bash:  bash scratchpad/delete_owner_20260929.sh
# Literal paths only; the operating detector is backed up first and never deleted.
set -eu
cd /c/Users/benpe/ClashBot

# 1. Back up the operating detector (config pins runs/detect/board-24-5) + the dataset's small metadata files
mkdir -p icebow/detector_backup_20260929
cp icebow/runs/detect/board-24-5/weights/best.pt icebow/detector_backup_20260929/board-24-5_best.pt
cp icebow/data/detect/classes.txt icebow/data/detect/data.yaml icebow/data/detect/holdout_val.yaml \
   icebow/data/detect/label_priority.txt icebow/data/detect/val_board15.txt icebow/detector_backup_20260929/
echo "backed up: $(ls icebow/detector_backup_20260929 | tr '\n' ' ')"

# 2. Delete (live_play recreates overlayed_replays/raw on the next recording)
rm -rf icebow/data/overlayed_replays/raw          # ~3.3 GB raw match clips
rm -rf icebow/data/detect                         # ~10.9 GB detector training data
rm -rf hogeq/data/overlayed_replays               # ~1.3 GB hogeq-era overlay videos
rm -rf scratchpad/gauntlet/L66/clips scratchpad/gauntlet/L66/clips180 scratchpad/gauntlet/L66/sweep180 \
       scratchpad/clips scratchpad/sweep          # ~0.6 GB experiment clips + sweeps
rm -f scratchpad/gauntlet/L66/ctrl_hunter1_180s.mp4 scratchpad/gauntlet/L66/ctrl_hunter1_20s.mp4 \
      scratchpad/gauntlet/L66/ctrl_hunter2_180s.mp4 scratchpad/gauntlet/L66/ctrl_hunter3_180s.mp4

echo "done"
df -h /c | tail -1
