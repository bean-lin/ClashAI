# Cached small-set aim audit gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/small_set_aim_audit/**, icebow/data/bench/small_set_aim_audit_20261006/**

- [ ] C1: Every saved PLAY aim row and subgroup is bound to the original assay caches.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/small_set_aim_audit/collect.py
  EXPECT: SMALL_SET_AIM_COLLECTED
  EVIDENCE: pending
- [ ] V1: Independent raw-label geometry, per-replay counts, patch algebra and corruption controls reconcile.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/small_set_aim_audit/verify.py
  EXPECT: SMALL_SET_AIM_VERIFIED
  EVIDENCE: pending
- [ ] R1: Reviewed evidence distinguishes descriptive geometry from cause and preserves all failed criteria.
  MANUAL: Review original bindings, both receipts, counts, controls and limitations.
  EVIDENCE: pending
