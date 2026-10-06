# Paired late curriculum gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/development_rl_3/**, icebow/data/bench/development_rl_3_20261006/**

- [x] P1: All1024initial setups and draw/projection controls bound before learning.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_rl_3/prepare.py
  EXPECT: LATE_CURRICULUM_PREPARED
  EVIDENCE: prepared.json;1024native setups,7positive8corruptions; l72-late-curriculum-prepare exit0/token,15.206882s. No optimizer.
- [ ] T1: Both final-only16update runs complete without guards or nonfinite steps.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_rl_3/train.py
  EXPECT: LATE_CURRICULUM_TRAINED
  EVIDENCE: pending
- [ ] V1: Independent full training membership, native outcomes, probabilities, returns, draws and corruption checks.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_rl_3/verify_training.py
  EXPECT: LATE_CURRICULUM_TRAINING_VERIFIED
  EVIDENCE: pending
- [ ] E1: Both final checkpoints evaluated once on fixed development rows.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_rl_3/evaluate.py
  EXPECT: LATE_CURRICULUM_EVALUATED
  EVIDENCE: pending
- [ ] V2: Independent counts and both-control continuation verdict reconcile.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_rl_3/verify_results.py
  EXPECT: LATE_CURRICULUM_RESULTS_VERIFIED
  EVIDENCE: pending
- [ ] R1: Outside receipt review, report both new models once, bind delivery and deployment verdict.
  MANUAL: Review complete frozen evidence before one compound model report. No policy acceptance from development alone.
  EVIDENCE: pending
