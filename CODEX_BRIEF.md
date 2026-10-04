# CODEX BRIEF -- continue ClashBot until Claude's usage resets (Tuesday 2026-10-06)

Written by the lead (Claude) on 2026-10-04. Read this file first, then `README.md` (the project overview) and the TOP of
`HANDOFF.md` (the blocks dated 2026-10-04: every number below comes from there, with its context). The owner will talk
to you directly. This brief tells you what was done, what was measured, what to do next, and -- most important -- HOW
the work is done here, so the project does not drift.

## 1. How we work (non-negotiable; this is what keeps the project on course)

1. **Measure, then claim.** Every claim is labelled *measured* (cite the number + file), *untested* (say so, propose the
   measurement) or *contradicted* (give the evidence). Never present a guess as a result. The owner is a student who
   asks to be corrected: if the owner's diagnosis or idea is wrong or untested, say so plainly, with evidence, before
   acting on it.
2. **Acceptance instruments, not impressions.** A model or setting is better only on:
   - the **paired ghost screen** (`scratchpad/gauntlet/L68/generalist/screen_gen/run_screen.py`, 299 pinned replays,
     flags exactly as in `scratchpad/gauntlet/L71/gen_v31/accept_v31a.sh`: `--split train --noise-off all --opp-elixir
     counter --action-delay 26 --extrapolate 26 --seeds 0 --device cuda --forms-mode deck --tau 0.27 --only-tags-from
     scratchpad/gauntlet/L68/generalist/lat26/screens/train_C.jsonl --behaviour-telemetry`), scored with `--pair A B`
     (paired pp with a 95% bootstrap CI), AND
   - **reactive play** (`python -m pipeline.search_s0 --seeds 0:24 --opps gen,s1 --arms plain ...`, wins out of 24), AND
   - the **behaviour telemetry** (Rocket share, tower Rockets, finish-offs, multi-Rocket cycles, defensive Rockets, both
     Rocket/Tornado orders, X-Bow cells/lanes, pre-emptive Log) -- compare with the pro baselines in HANDOFF.
   Always pair against a baseline run with the SAME code (a code change between two screens invalidates the pairing --
   see the R8 mistake in HANDOFF 14:5x). Write the decision rule BEFORE you see the result.
3. **One change per experiment.** Each run changes one thing so its effect is attributable. New behaviour goes behind an
   opt-in flag/config key whose default is byte-identical to today, with a test proving that.
4. **No hand-written playstyles.** The owner's rule: the bot learns from pros (imitation from re-driven pro replays,
   weighting of pro situations, RL). Do not add rules like "Rocket when tower < X HP". The only hand-written rule
   allowed is the owner-ordered interim Hero Ice Wizard ability rule (`hero_button.py`), until pro data exists.
5. **Public information only.** The opponent's hand, next card, elixir and ability readiness are NEVER model inputs.
   Measurements may use recorded hidden state; models may not.
6. **Machine discipline.** One GPU job at a time (check `nvidia-smi` and running python first). The laptop is shared.
   Never kill or edit a running script (write a `_v2` file instead). Kill processes only by exact command-line match in
   a command that does not itself contain the pattern. Long jobs: write a launcher script, log to a file, poll it.
7. **Live play.** Never start, stop or reconfigure live unless the owner asks (the owner starts it with
   `bash scratchpad/gauntlet/L70/live/start_live.sh`, stops with `stop_live.sh`; the model is the path in
   `scratchpad/gauntlet/L70/live/CKPT_OVERRIDE`). Never deploy a checkpoint without the owner's explicit approval:
   post "APPROVAL NEEDED: <what>" to Discord with the evidence and wait.
8. **Owner decisions.** Anything the owner would decide (deploys, live settings, spending, deleting data, changing an
   acceptance rule, changing the experiment plan) -> write it to `.foreman/codex_autopilot/BLOCKERS.md` (what, why,
   options, your recommendation, evidence) and continue with unblocked work. Do not decide it yourself.
9. **Record everything.** After every change batch: update `HANDOFF.md` (a dated block at the top, numbers + paths),
   commit and push to `main` with a clear message ending `Co-Authored-By: Codex (autopilot)`. NEVER stage `icebow/data/`
   (secrets incl. `discord_webhook.txt`; never print the webhook URL). Post a short Discord report after each milestone
   (`icebow/.venv/Scripts/python.exe scratchpad/gauntlet/L69/discord/post.py <msg.txt>`): what was done, the numbers and
   what they mean, next steps.
10. **Stay in scope.** Do the queue in section 4. No refactors, no new frameworks, no re-auditing finished work, no long
    reports. If a gate blocks you, try the obvious fix first, then record the question and move to the next item.

## 2. State at the time of writing (2026-10-04 ~15:50 EDT)

- **Data:** full real-engine re-drive of 14,818 pro recordings (0 failures) with public observations: projectiles +
  time-to-impact, spell areas + timers, exact evo/hero ids, driven abilities. Dataset
  `icebow/data/pipeline/gen_dataset_v31_public.npz`: 3,517,863 rows, 14,661 replays, 4,283 decks, v3val 12,237.
- **Imitation models (feature version 4):** gen_v3.1a (inputs only), 3.1b (+ six-target pro-context weighting 2.0),
  3.1c (weight 4.0). **gen_v3.1c is the best gen model**: vs 3.1b +1.2 [-2.2, +4.5]; vs live-best RL u0155 -1.7
  [-4.7, +1.3]; reactive gen 13/24, S1 19/24.
- **R8 (look-ahead advances projectiles/effects, inference-only):** measured on 3.1a: pre-emptive Log 23.5% -> 49.8%
  (pros 39.1% same deck/definition); ghost +1.0 [-1.7, +3.7]. On by default for v4.
- **RL:** R1e = PPO from gen_v3.1c (5 actors, evo/hero census opponents, calibrated per-ability press models v2,
  R8), launched 15:06 by `scratchpad/gauntlet/L71/rl/run_r1e_v3.sh`; log `scratchpad/gauntlet/L71/rl/r1e.log`. Its
  verdict and the live decision are appended in section 6 when they arrive.
- **Live:** see section 6 (the lead starts live on the winner of R1e vs 3.1c before handing over).
- **Abilities in the sim:** `ability_policy: v2` (royale_env / e1_eval / rl_royale / search_s0 `--ability-policy`).
  Calibrated models: `scratchpad/gauntlet/L70/abilities/ability_models_v2.json` (held-out share error <= 3 pp for 17/22).
- **Live ability:** Hero Ice Wizard = owner's interim rule (freeze clumps of >= 3 troops, or a win condition on our
  half when Tesla is not in hand / < 4 elixir). Reader v2 reports hero units as 203000000 + n (fixed lookup).

## 3. Findings that steer the next steps (all measured; files in HANDOFF)

- **Rocket is the biggest gap:** ~0.9% of plays vs pros ~5.8%; tower Rockets ~8-10 per 299 games; finish-offs 0;
  multi-Rocket cycles 0. Weighting 2x/4x barely moved it. Diagnosis (`scratchpad/gauntlet/L71/rocket_diag/`): at pro
  Rocket moments the model gives Rocket P = .24 (AUC .84, well calibrated) but **argmax** picks it only 22%; the gate is
  not the blocker (87% pass); and when Rocket IS chosen the **argmax cell hits a tower only 28.5%** (overtime-behind
  6.9%) because the cell distribution mixes troop and tower targets.
- **X-Bow:** pros use 2 offensive rows and ~24 cells; the model's distribution is spread (80% mass on lock-capable cells)
  but argmax collapses it to 2 cells; sampling X-Bow cells lowered agreement (not adopted). Dead-lane X-Bows: pros' are
  mostly POCKET plays; the bot's are mostly own-half (n = 30, weak). X-Bow reach for labels = 13.0384 tiles
  centre-to-centre (98.2% hit recall).
- **RL so far never increased Rocket use** (u0155 50 Rockets vs gen_v1 72 in the same 299 games). Hypothesis
  (untested): sampled Rockets with poor aim waste elixir, so RL learns to avoid them -- fix aim before expecting RL to help.
- **RL determinism:** results are now sorted before learning (actor count / timing no longer change runs).

## 4. Next steps (do in this order)

- **Q1 (CPU) Card-choice sampling, opt-in.** `card_choice: argmax | sample` + `card_T` in `pipeline/e1_eval.py`
  `live_decide` (SIM) and `pipeline/live_gen.py` (live); default byte-identical (test). Gate and cell rules unchanged.
- **Q2 (CPU) Area-aware spell aim, opt-in.** For area spells, choose the cell that maximises the model's cell-probability
  mass inside the spell's catalog radius instead of the single argmax cell (same flag pattern, SIM + live). Test: a
  sharp off-target cell vs a broad on-tower cluster must pick the cluster.
- **Q3 (GPU, only when no other GPU job runs)** ghost-screen A/Bs on the live model (or gen_v3.1c), paired against its
  saved screen run with the SAME code: (a) card sample T=0.7, (b) T=1.0, (c) area aim, (d) area aim + the better T.
  Report win value CIs + the behaviour telemetry. If an option is not worse on win value (CI not entirely below 0) and
  raises Rocket use / tower-Rocket hits toward the pro numbers -> "APPROVAL NEEDED: enable <option> live?".
- **Q4** Re-run the diagnostics (`scratchpad/gauntlet/L71/rocket_diag/rocket_diag.py`,
  `scratchpad/gauntlet/L70/xbow_diversity/xbow_diversity.py`) on the live model and report what changed.
- **Q5 Small fixes:** `pipeline/tests/test_dataset_spool.py` (KeyError 'own_ability' in the model_gen mmap path);
  `scratchpad/gauntlet/L70/live/run_live.sh` `last_stop()` should also match "new checkpoint deployed" (edit only if no
  run_live.sh process is running; otherwise make `run_live_v2.sh`).
- **Not for you (owner/lead):** the Hero Ice Wizard pro-data crawl (RoyaleAPI needs the owner's Cloudflare click);
  any deploy; R1e follow-up RL runs (propose them in BLOCKERS with a one-change design; do not launch).

## 5. Where things are

`README.md` (pipeline + how to run), `HANDOFF.md` (state, numbers, traps), `.foreman/codex_autopilot/LEAD_RULINGS.md`
(the lead's rulings R1-R8 on labels, TTI, look-ahead -- follow them), `scratchpad/gauntlet/L71/` (today's scripts and
outputs: gen_v31/, rl/, rocket_diag/, barrel_log/), `pipeline/` (all model/data/sim/RL code, tests in
`pipeline/tests/`; run with `research/ext/Royale/.venv/Scripts/python.exe -m pytest`).

## 6. R1e verdict and live decision

(Pending at the time of writing; the lead appends it here before handing over.)
