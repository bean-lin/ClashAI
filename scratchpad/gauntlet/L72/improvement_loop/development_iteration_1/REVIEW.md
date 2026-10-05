# Development comparison launched after verified preflight

October5 13:26 EDT: D3 passes; D4 is active. Launcher38268, chain42456 holds a
file lock across all subprocess gaps. It runs corrected-input R1e development
evaluation, ordinary_v5 training/evaluation, ordinary_v6 training/evaluation and
independent raw-source prediction recount serially. Final model reports require
review after completion; no new checkpoint is accepted or deployed.

The checkpoint-free CPU smoke confirms exactly equal initial output tensors,
base dropout stream and loss5.335096836090088 for both arms; finite backward
steps and a nonzero learning path into the initially zero spatial residual pass.
Shared augmentation preserves unknown projectile coordinates for both arms,
removing the old feature-version-dependent mirroring difference. Its loss equals
the original v6 mirrored loss exactly. Original expert loss weights/labels remain.
See METRICS.md for predeclared definitions and prelaunch.json for all source,
runtime, data, draw-schedule and metric-mask hashes. This is IL; no simulator
runtime or updated-engine gameplay result is claimed by it.

Frozen development denominators:54723 rows/405 replays,17192 PLAY; Witch726rows/
20replays, Night Witch373/12, Furnace1174/20. Primary Barrel63rows/26replays,
other PLAY36/22, WAIT55/25; ambiguous/multiple cases retained.955 expert Rocket
rows/336replays; old narrow finish31rows/13replays and combo320/75. Original
spawner membership and corrected-parent/child-only subgroups are both retained.
These repeated rows are not independent samples or enough for final acceptance.

Independent data-mask reconstruction, four index corruption checks and one
positive/four negative counter controls pass. Process receipt
l72-development1-prelaunch is exit0/token matched in178.88seconds. AST inspection
confirms train.py calls only load_part('train'), evaluate.py only
load_part('development'), neither calls the old validation evaluator. No pipeline
source or live configuration changed. Do not edit bound sources or relaunch.

The preparation record below remains historical provenance.

The preregistered whole-replay hash assignment yields213995 training rows from
1573 replay groups and54723 development rows from405 groups. All268718 original
ordinary expert rows are accounted for. Training has67106 PLAY/146889 WAIT;
development has17192 PLAY/37531 WAIT. No reweighting or labels changed.

All38317 old validation pool rows are excluded. Membership is disjoint from all
239939 reserved raw replay groups. Both observer sides stay together; the parent
R1e model's earlier exposure to these historical examples remains disclosed.
The independent verifier reconstructs indices/counts from the original sources
without importing the producer, trainer or model. One positive and eight leakage/
missing/duplicate/order corruption controls pass. Data, context, corrected-label
binding, initial checkpoint, recipe and reservation hashes are frozen.

D1/D2 were complete before D3 launch. The planned isolated ordinary_v5 versus
ordinary_v6 driver freezes subgroup definitions, verifies zero-residual
migration and identical batch/mirror draws, and uses a checkpoint-free smoke.
The old trainer cannot be reused unchanged because it predicts on historical
validation. Then perform the registered serial1000-update arms, independently
recount development results, and send the owner's model reports with the verdict
NOT ACCEPTED pending final evidence. This split does not authorize deployment.

No optimizer updates, candidate checkpoints, policy predictions, GPU job launch
or Discord report occurred during preparation. The live owner farming run was
left operating with its selected checkpoint.
