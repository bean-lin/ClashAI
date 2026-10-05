# Frozen-base projectile trial launched

October5 17:03 EDT. B1 complete; B2/B3 active. Launcher42584/chain51696 runs a serial1000-step
training/evaluation/independent-recount chain under the existing GPU file lock.
Inspect launch.json,chain_started/progress.json,chain.out/.err and ignored
icebow/data/bench/development_iteration_7_20261005/frozen_base_projectile_v6/train.jsonl.
Fail closed; no automatic resume, duplicate launch or bound Python/PLAN/METRICS edits.
Place future reporting helpers outside this frozen directory.

The completed gameplay comparison rejected ordinary_v6's overall continuation:
39/64 wins vs v5 42/64 and original R1e45/64. Its offline Barrel benefit remains
a component observation. The independent common-state audit finds both aim and
card/timing differences after shared-base training. This new experiment tests
whether freezing all v5 base weights can isolate useful projectile learning.
It does not establish the cause of losses or rescue the earlier candidate.

Start from verified ordinary_v5 portable weights, not R1e or ordinary_v6. Add
the same zero-initialized generic target residual and train only its five tensors.
Frozen base in eval mode, no dropout in the new modules. Original expert losses,
all213995train/1573groups and54723dev/405groups, original ordinary1000x128 draws/
mirror bits,seed20261005,targetLR1e-3,AdamWwd.01,clip1,fp32,final-only. No pipeline,
live, runtime, labels, target-rule, sampling or loss-weight change. Parent exposure
remains explicit; no reserved/old-validation/owner-bot expert training.

New preflight68.08s exit0/token matched. Exact migration reproduces all v5 outputs
and loss. Two training-only smoke losses5.106794834136963/5.106081962585449, finite
nonzero residual output/upstream gradients; every base tensor unchanged after both
updates. Gate/card/value/WAIT outputs exact with nonzero learned branch. No-valid
target, padding and unknown coordinates give zero residual and full v5 equality.
Standard weights-only metadata/tensor roundtrip passes. No smoke checkpoint saved.
Existing data/schedule/mask/source/runtime prerequisites checked, not rerun.

Fixed continuation versus v5: Barrel correct responses+15pp, wrong lanes at least
halved, full Barrel actions nondecreasing; exact gate/card logits across all54723;
no Rocket aim/action/late-Rocket, late-all, W/NW/F or defensive-action decline.
Independent recount includes same-corrected-input R1e and end-to-end v6 references.
All final untouched/material-component/gameplay/statistical/Q4/Q5 gates remain.
No new-model report due at launch; review the final checkpoint and all receipts
before reporting once to Discord. No accepted replacement or live restart.
