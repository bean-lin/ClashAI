# Setup recovery gates

- [x] R1: First native setup proves JSON-only mismatch; original failure and zero candidate outputs preserved; malformed form maps rejected.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_rl_1_recovery/diagnose.py
  EXPECT: OUTCOME_RL_SETUP_RECOVERY_VERIFIED
- [ ] R2: Original bounded learning and evaluation finish under the corrected serialization check, followed by independent recount.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_rl_1_recovery/run_chain.py
  EXPECT: OUTCOME_RL_RECOVERY_CHAIN_COMPLETE
- [ ] R3: Publish measured completion/failure and preserve all original gates, receipts and model-report uniqueness.
  MANUAL: No acceptance or model performance claim from setup repair.

R1 l72-outcome-rl-setup-recovery34.37s exit0/token matched;1positive5corruptions.
R2 ACTIVE19:07:30 launcher25612/chain34060. No completed upstream jobs repeated.
