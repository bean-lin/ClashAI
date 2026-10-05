# Gates: global aim-only learning

- [x] A1: Prior diagnosis independently passes and exact frozen decision path, trainable aim reach, original data/loss and portable checkpoint smoke are verified.
  CHECK: icebow/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_8/preflight.py
  EXPECT: AIM_HEADS_PREFLIGHT_COMPLETE
- [ ] A2: Exactly1000 finite updates and all54723 fixed development predictions complete with unchanged frozen tensors.
  MANUAL: Inspect receipts and full logs, sources and runtime bindings, no other GPU chain or active-source edits.
- [ ] A3: Independent original-label/cache/per-replay recount and every frozen filter are reviewed, the model report delivered once and handoff published.
  MANUAL: Preserve numerical/execution failures; no acceptance from development alone.

A1 l72-development8-preflight exit0/token matched94.36s. Initial loss/output
equality, two original training-batch steps5.106794834136963/5.102773189544678,
all frozen tensors and timing/card/wait/value heads exact, six aim gradient paths,
no-target aim changes, frozen-head corruption rejection and standard weights-only
roundtrip pass. No checkpoint saved; smoke is not full training. A2/A3 ACTIVE,
launcher60876 started17:37:19, serial GPU lock. No duplicate/source edits/resume.
