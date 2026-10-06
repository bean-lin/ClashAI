# Extended fit audit gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/extended_fit_audit/**, icebow/data/bench/extended_fit_audit_20261006/**

- [ ] P1: Bind both reviewed checkpoints/caches, source/labels and original draw schedule; controls pass.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/extended_fit_audit/prepare.py
  EXPECT: EXTENDED_FIT_PREPARED
  EVIDENCE: pending
- [ ] C1: Once-only training views for both fixed models, no optimization or development inference.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/extended_fit_audit/collect.py
  EXPECT: EXTENDED_FIT_COLLECTED
  EVIDENCE: pending
- [ ] V1: Independent raw labels, schedule, masks, scalar counts and every replay reconcile for both models.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/extended_fit_audit/verify.py
  EXPECT: EXTENDED_FIT_VERIFIED
  EVIDENCE: pending
- [ ] R1: Outside review binds all three receipts and interpretations, publishes accurate handoff.
  MANUAL: Inspect artifacts and run review_extended_fit.py once via fresh l72-extended-fit-reviewed receipt.
  EVIDENCE: pending
