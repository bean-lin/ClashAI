# Small fixed-set fit assay gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/small_set_fit/**, icebow/data/bench/small_set_fit_20261006/**

- [ ] P1: Original sample labels, fixed schedule and finite unchanged-weight preparation probe reconcile.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/small_set_fit/prepare.py
  EXPECT: SMALL_SET_FIT_PREPARED
  EVIDENCE: pending
- [ ] T1: Exactly 4096 finite updates produce the quarantined final assay model.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/small_set_fit/train.py
  EXPECT: SMALL_SET_FIT_TRAINED
  EVIDENCE: pending
- [ ] V1: Independent training and corruption controls pass before final assay inference.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/small_set_fit/verify_training.py
  EXPECT: SMALL_SET_FIT_TRAINING_VERIFIED
  EVIDENCE: pending
- [ ] E1: The three fixed checkpoints predict once per sample orientation.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/small_set_fit/evaluate.py
  EXPECT: SMALL_SET_FIT_EVALUATED
  EVIDENCE: pending
- [ ] V2: Independent original-label, prediction, per-replay and criterion counts reconcile.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/small_set_fit/verify_results.py
  EXPECT: SMALL_SET_FIT_RESULTS_VERIFIED
  EVIDENCE: pending
- [ ] R1: Evidence review and one diagnostic-model report retain quarantine and all deployment floors.
  MANUAL: Inspect every receipt, final counts, exact report and confirmed delivery.
  EVIDENCE: pending
