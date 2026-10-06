# Hand and retention integration gates

OWNS: pipeline/model_tower.py, pipeline/model_gen.py, pipeline/opponent_hand_v2.py, pipeline/model_hand_belief.py, pipeline/tests/test_hand_integration.py, scratchpad/gauntlet/L72/improvement_loop/hand_retention_integration/**

- [x] L1: Explicit candidate loading preserves frozen tower predictions and legacy behavior and rejects malformed architecture state.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/hand_retention_integration/check_loader.py
  EXPECT: TOWER_LIVE_LOADER_VERIFIED
  EVIDENCE: loader_verified.json; l72-tower-live-loader and l72-tower-live-check-v2 exit0/token.
- [x] H1: Mirror/event/hand features respect current memory schemas, uncertainty, causality and privacy.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/hand_retention_integration/check_hand.py
  EXPECT: HAND_SUCCESSOR_VERIFIED
  EVIDENCE: l72-hand-successor exit0/token, eight tests; live event completeness remains conditional.
- [ ] S1: Original expert sequences and public beliefs are joined and independently verified without future/private input.
  EVIDENCE: pending; freeze membership and metrics before collection.
- [ ] M1: Versioned learned representation preserves initial eligible-parent predictions and supports strict load/save/live inputs.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/hand_retention_integration/check_model.py
  EXPECT: HAND_MODEL_QUALIFIED
  EVIDENCE: pending; MODEL_METRICS.md froze representation before implementation.
- [ ] T1: Frozen matched training/evaluation and independent recount establish the candidate's complete verdict.
  EVIDENCE: pending; recipe and commands must be registered before optimization.
- [ ] R1: Publish verified results, once-only new-model report and accurate remaining work.
  EVIDENCE: pending
