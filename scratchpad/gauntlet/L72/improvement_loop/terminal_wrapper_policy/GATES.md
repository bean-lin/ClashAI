# Terminal policy-driver gates

- [ ] P1: All32 initial setup/form pairs match before prediction; fixed serial collection completes with source/runtime bindings and every raw record.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/terminal_wrapper_policy/collect.py
  EXPECT: TERMINAL_POLICY_COLLECTION_COMPLETE
- [ ] P2: Independent exact-command/native-state/public-prefix/pending accounting passes for all16 pairs and rejects corruptions; actual fulltime coverage is explicit.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/terminal_wrapper_policy/verify.py
  EXPECT: TERMINAL_POLICY_VERIFIED
- [ ] P3: Publish bounded engineering conclusion and preserve all final model gates and owner STOP.
  MANUAL: No performance/deployment claim or duplicate model report.
