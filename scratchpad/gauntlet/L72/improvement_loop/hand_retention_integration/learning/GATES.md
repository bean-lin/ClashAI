# Paired hand learning gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/hand_retention_integration/learning/**

- [ ] P1: Source-bound schedule and qualified public inputs exist before optimization.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/hand_retention_integration/learning/prepare.py
  EXPECT: HAND_LEARNING_PREPARED
  EVIDENCE: pending
- [ ] T1: Both registered arms complete exactly1000 finite updates with final-only artifacts.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/hand_retention_integration/learning/train.py
  EXPECT: HAND_LEARNING_TRAINED
  EVIDENCE: pending
- [ ] V1: Independent full schedule/log/tensor/optimizer reconciliation passes.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/hand_retention_integration/learning/verify_training.py
  EXPECT: HAND_LEARNING_TRAINING_VERIFIED
  EVIDENCE: pending
- [ ] E1: Each final arm produces exactly54723 development predictions.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/hand_retention_integration/learning/evaluate.py
  EXPECT: HAND_LEARNING_EVALUATED
  EVIDENCE: pending
- [ ] V2: Independent original-label and per-replay results establish every required verdict and audit slice.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/hand_retention_integration/learning/verify_results.py
  EXPECT: HAND_LEARNING_RESULTS_VERIFIED
  EVIDENCE: pending
- [ ] R1: Evidence, once-only model report and handoff are reviewed/published.
  EVIDENCE: pending
