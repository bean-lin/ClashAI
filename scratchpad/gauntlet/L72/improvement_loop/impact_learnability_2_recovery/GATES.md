# Gates: Representation-corrected effect assay recovery

OWNS: scratchpad/gauntlet/L72/improvement_loop/impact_learnability_2_recovery/**, icebow/data/bench/impact_learnability_2_20261005/r*_a*, icebow/data/bench/impact_learnability_2_20261005/r*_wait*, icebow/data/bench/impact_learnability_2_20261005/dataset.json, icebow/data/bench/impact_learnability_2_20261005/*public_*, icebow/data/bench/impact_learnability_2_20261005/draws_*

- [ ] D1: All prepared roots restore exactly and produce complete qualified trajectories.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/impact_learnability_2_recovery/collect.py
  EXPECT: IMPACT_LEARNING_DATA_COLLECTED
  EVIDENCE: pending
- [ ] D2: All public features, labels and grouped memberships independently reconcile.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/impact_learnability_2_recovery/verify_data.py
  EXPECT: IMPACT_LEARNING_DATA_VERIFIED
  EVIDENCE: pending
- [ ] L1: Six models complete the original1000updates each and fixed inference.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/impact_learnability_2_recovery/train.py
  EXPECT: IMPACT_LEARNING_TRAINED
  EVIDENCE: pending
- [ ] L2: Saved results and original continuation filters independently reconcile.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/impact_learnability_2_recovery/verify_results.py
  EXPECT: IMPACT_LEARNING_RESULTS_VERIFIED
  EVIDENCE: pending
- [ ] R1: Original failures, six successful receipts, reviewed results and single report delivery are handed off.
  MANUAL: Verify outside closeout, report every seed/control and limits once; do not claim a playable model or R1e superiority.
  EVIDENCE: pending
