# Controlled outcome-driven development gates

- [x] O1: Readiness evidence and all fixed native training setups/data/control/source bindings pass preflight; an excluded ephemeral PPO step is finite without changing parent or reading old validation.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_rl_1/prepare.py
  EXPECT: OUTCOME_RL_PREPARED
- [ ] O2: Registered32 updates/256 games complete with valid on-policy gradients, native outcomes and final portable checkpoint.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_rl_1/train.py
  EXPECT: OUTCOME_RL_TRAIN_COMPLETE
- [ ] O3: Final development predictions and independent row/replay recount reconcile without threshold changes.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_rl_1/verify.py
  EXPECT: OUTCOME_RL_VERIFIED
- [ ] O4: Review receipts, report new model once and publish verdict; only pass supports separately registered gameplay.
  MANUAL: No accepted deployment claim from development; owner STOP intact.

O1 receipt l72-outcome-rl-prepare:49.55s exit0/token matched.
O2 original attempt FAILED before first policy decision: integer/string JSON side
keys compared directly. Do not rerun this command. Recovery R1 passed34.37s with
strict form normalization; R2 carries unchanged O2/O3 learning/metric obligations
under separate driver and receipt. See ../development_rl_1_recovery/GATES.md.
O2/O3/O4 remain unmet until that chain and review finish; original failure retained.
