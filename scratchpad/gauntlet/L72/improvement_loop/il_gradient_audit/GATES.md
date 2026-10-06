# Imitation gradient audit gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/il_gradient_audit/**, icebow/data/bench/il_gradient_audit_20261006/**

- [ ] C1: Collect all32 fixed model/batch gradients with original losses, unchanged weights and controls.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/il_gradient_audit/collect.py
  EXPECT: IL_GRADIENT_COLLECTED
  EVIDENCE: pending
- [ ] V1: Independently reconcile original draws and labels, all vector reductions and corruption controls.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/il_gradient_audit/verify.py
  EXPECT: IL_GRADIENT_VERIFIED
  EVIDENCE: pending
- [ ] R1: All receipts and bindings reconcile and interpretation preserves limitations and model rejections.
  MANUAL: Inspect both successful stages, run outside once-only review and publish qualified results.
  EVIDENCE: pending
