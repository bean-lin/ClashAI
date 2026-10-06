# Lattice-label diagnostic correction gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/lattice_label_audit/**, icebow/data/bench/lattice_label_audit_20261006/**

- [ ] C1: Cached geometry and score descriptors use the dataset's actual lattice training labels, preserving original aim decisions.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/lattice_label_audit/collect.py
  EXPECT: LATTICE_LABEL_AUDIT_COLLECTED
  EVIDENCE: pending
- [ ] V1: Independent raw-label reconstruction, per-replay recount and corruption controls verify the correction without model inference.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/lattice_label_audit/verify.py
  EXPECT: LATTICE_LABEL_AUDIT_VERIFIED
  EVIDENCE: pending
- [ ] R1: Reviewed receipts and the explicit diagnostic correction preserve every original fit verdict and quarantine.
  MANUAL: Review original sources and both receipts, then bind the correction in reviewed.json.
  EVIDENCE: pending
