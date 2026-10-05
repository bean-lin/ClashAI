# Defensive-sequence preparation

C1/C2 completed October 5. The new schedule intersects the previously verified
sequence union with the same whole-replay inner splits as iteration1. Training
has 32187 defensive rows from 856 replays (12385 PLAY,19802 WAIT,767 expert
Rockets); development has 8183 rows from 212 replays (3152 PLAY,5031 WAIT,223
expert Rockets). Labels and original historical binding are unchanged.

The fixed schedule replaces 25221 of128000 ordinary draws. Defensive draws rise
from19429 to40899. Independent regeneration matches every row, replacement bit
and mirror bit; one positive and three corruption controls pass. Receipts are
l72-development2-schedule and l72-development2-schedule-independent, exit0.
C3 passed l72-development2-preflight,106.14s, exit0/token matched. The isolated
trainer uses frozen iteration1 loading/augmentation/loss/optimizer; only its
scheduled row exposure differs. A first-batch CPU smoke is not full training;
its in-memory plain metadata roundtrip proves identical saved tensors without
writing a checkpoint. Original masks independently match, and fixed defensive
development/defensive expert-Rocket masks have8183/223 rows. No confirmation
data or live actions enter training. prelaunch.json explicitly activates only
this registered candidate, leaving the original historical binding unchanged.

C4 ACTIVE: launcher39500 runs train/eval/independent recount serially using the
same held GPU-chain lock. launch.json/chain_started.json bind current workers.
Preserve active sources and all process receipts; no new-model report is due
until the full candidate and its developmental statistics are reviewed. Final
acceptance, gameplay, physical attribution and statistical floors remain open.
