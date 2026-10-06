# Local cell mechanism assay gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/local_cell_fit/**, icebow/data/bench/local_cell_fit_20261006/**

- [ ] P1: Mapping, initial parity, roundtrip, mechanism and finite unchanged-weight backward controls pass.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/local_cell_fit/prepare.py
  EXPECT: LOCAL_CELL_FIT_PREPARED
  EVIDENCE: pending
- [ ] T1: Exactly4096 finite updates produce the quarantined final diagnostic checkpoint.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/local_cell_fit/train.py
  EXPECT: LOCAL_CELL_FIT_TRAINED
  EVIDENCE: pending
- [ ] V1: Independent training/draw/optimizer evidence passes before inference.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/local_cell_fit/verify_training.py
  EXPECT: LOCAL_CELL_FIT_TRAINING_VERIFIED
  EVIDENCE: pending
- [ ] E1: Only the new final model predicts once on each fixed training orientation.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/local_cell_fit/evaluate.py
  EXPECT: LOCAL_CELL_FIT_EVALUATED
  EVIDENCE: pending
- [ ] V2: Independent original-label counts, criteria and corruptions reconcile with cached controls.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/local_cell_fit/verify_results.py
  EXPECT: LOCAL_CELL_FIT_RESULTS_VERIFIED
  EVIDENCE: pending
- [ ] R1: Review and one delivered report retain quarantine and final deployment criteria.
  MANUAL: Inspect all receipts and final results; bind exact report and delivery.
  EVIDENCE: pending
