# Additional ordinary imitation gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/development_iteration_9/**, icebow/data/bench/development_iteration_9_20261006/**

- [ ] P1: Frozen training-only schedule and new-driver controls reconcile.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_9/prepare.py
  EXPECT: ORDINARY_EXTENDED_PREPARED
  EVIDENCE: pending
- [ ] T1: Exactly8000 finite updates produce only the final candidate under frozen bindings.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_9/train.py
  EXPECT: ORDINARY_EXTENDED_TRAINED
  EVIDENCE: pending
- [ ] V1: Independent training evidence and corruption controls reconcile before development inference.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_9/verify_training.py
  EXPECT: ORDINARY_EXTENDED_TRAINING_VERIFIED
  EVIDENCE: pending
- [ ] E1: The final candidate predicts once on the registered development rows.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_9/evaluate.py
  EXPECT: ORDINARY_EXTENDED_EVALUATED
  EVIDENCE: pending
- [ ] V2: Independent counts, controls and every continuation verdict reconcile.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_9/verify_results.py
  EXPECT: ORDINARY_EXTENDED_RESULTS_VERIFIED
  EVIDENCE: pending
- [ ] R1: Evidence review and the single model report are bound with an accurate deployment verdict.
  MANUAL: Inspect every receipt, final counts, message and confirmed delivery; preserve all final floors.
  EVIDENCE: pending
