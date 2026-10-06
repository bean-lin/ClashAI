# Dropout-free development gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/development_iteration_10/**, icebow/data/bench/development_iteration_10_20261006/**

- [x] P1: Prepared bindings, exact prior schedule, unchanged initial EVAL and finite dropout-free backward pass.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_10/prepare.py
  EXPECT: ORDINARY_NO_DROPOUT_PREPARED
  EVIDENCE: prepared.json and l72-development10-prepare.json/.out; exit0/token,72.823836s;93source bindings,original1024000draws exact,initial EVAL/roundtrip exact,finite backward with unchanged weights and0optimizer.
- [ ] T1: Exactly8000 finite updates start fresh ordinary_v5 and disable only training dropout.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_10/train.py
  EXPECT: ORDINARY_NO_DROPOUT_TRAINED
  EVIDENCE: pending
- [ ] V1: Independent full draw/log/final-state/optimizer reconciliation passes before inference.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_10/verify_training.py
  EXPECT: ORDINARY_NO_DROPOUT_TRAINING_VERIFIED
  EVIDENCE: pending
- [ ] E1: Only the final new model predicts original54723 development rows once.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_10/evaluate.py
  EXPECT: ORDINARY_NO_DROPOUT_EVALUATED
  EVIDENCE: pending
- [ ] V2: Independent original-label/mask/per-replay recount decides all original filters against both controls.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_10/verify_results.py
  EXPECT: ORDINARY_NO_DROPOUT_RESULTS_VERIFIED
  EVIDENCE: pending
- [ ] R1: Outside review and one delivered model report bind every receipt, exact message and verdict.
  MANUAL: Review all artifacts, run outside evidence review, send once with stable ID model-ordinary-no-dropout-v5-final, then bind confirmed delivery.
  EVIDENCE: pending
