# Local-cell contribution gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/local_cell_contribution/**, icebow/data/bench/local_cell_contribution_20261006/**

- [ ] C1: Fixed-checkpoint base/residual scores and cache anchors are preserved for both orientations.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/local_cell_contribution/collect.py
  EXPECT: LOCAL_CELL_CONTRIBUTION_COLLECTED
  EVIDENCE: pending
- [ ] V1: Independent score reconstruction, labels, per-replay counts and corruption controls pass.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/local_cell_contribution/verify.py
  EXPECT: LOCAL_CELL_CONTRIBUTION_VERIFIED
  EVIDENCE: pending
- [ ] R1: Reviewed evidence binds both receipts and preserves failed fit criteria and quarantine.
  MANUAL: Review collected/verified original artifacts, sources and receipts; save a bound review.
  EVIDENCE: pending
