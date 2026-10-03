# Gates: gen_v3 SIM continuation

OWNS: pipeline/eval_gen.py, pipeline/royale_env.py, pipeline/e1_view.py, pipeline/rl_royale.py, pipeline/e1_eval.py, pipeline/search_s0.py, scratchpad/gauntlet/L68/generalist/screen_gen/run_screen.py, pipeline/tests/gen_v3/**

Scope: Complete versioned SIM features without training, GPU, live play, git, agents, or edits outside the write set.

- [ ] G1: Production SIM and training features agree, including forms and public history; noise and extrapolation preserve alignment.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider pipeline/tests/gen_v3/test_sim_contract.py pipeline/tests/gen_v3/test_sim_integration.py
  EXPECT: passed
  EVIDENCE: pending
- [ ] G2: Legacy snapshots and the active rseries checkpoint remain byte identical, including RNG states.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider pipeline/tests/gen_v3/test_legacy.py pipeline/tests/gen_v3/test_sim_legacy.py
  EXPECT: passed
  EVIDENCE: pending
- [ ] G3: One ghost match, one plain reactive match against gen_v1, and tiny RL collate/GAE run on CPU with measured features.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe -m pipeline.tests.gen_v3.sim_smoke
  EXPECT: SIM_SMOKE_OK
  EVIDENCE: pending
- [ ] G4: All requested CPU regression suites pass, excluding only tests that perform forbidden training.
  CHECK: research/ext/Royale/.venv/Scripts/python.exe -m pipeline.tests.gen_v3.run_sim_tests
  EXPECT: SIM_TESTS_OK
  EVIDENCE: pending
- [ ] G5: Reviewed scope, commands and evidence; no prohibited actions or edits.
  EVIDENCE: pending
