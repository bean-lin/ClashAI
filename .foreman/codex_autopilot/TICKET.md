# ClashBot Codex autopilot (2026-10-03 -> 2026-10-06). You continue the lead's plan while the lead (Claude) is out of
# usage until Tuesday 2026-10-06. You are re-invoked every 3 h. Each run: READ this file, `.foreman/codex_autopilot/
# JOURNAL.md` (your own previous runs), `BLOCKERS.md`, and the TOP of `HANDOFF.md` (the 13:45 RESTART NOTE and the
# 2026-10-03 blocks under it). Then do the most valuable unblocked next step(s), verify them, record them, and stop.

## HARD RULES (owner)
- If you are unsure about a DECISION (anything the owner would decide: what goes live, changing an experiment's
  design or acceptance rule, spending money, stopping/replacing the live run, deleting data, anything in a grey zone of
  the owner's no-cheating rule), DO NOT decide. Append it to `.foreman/codex_autopilot/BLOCKERS.md` (what, why, options,
  your recommendation, evidence paths) and continue with work that is not blocked.
- The LIVE ladder run (`scratchpad/gauntlet/L70/live/run_live.sh`, rseries_r1_u0155, reader v2 since 13:42) must keep
  running. Never stop it on purpose. If it has STOPPED or PAUSED: a pause on 'another device' stays paused (record
  it); a stop on a NEW unrecognised screen -> look at the saved frames, wire a template fix like trophy_road / conn_lost
  in `scratchpad/gauntlet/L68/live_reader/ladder_nav.py` (test_ladder_nav.py must pass), restart the supervisor per
  HANDOFF. A crash caused by reader v2: roll back with `--reader v1` ONLY by relaunching run_live.sh after editing the
  default in live_play.py (record it as a blocker too).
- Opponent HIDDEN state (hand, next card, elixir, deck evo slots) is NEVER fed to any model. Public information only.
- One GPU job at a time (check nvidia-smi / running python before starting one). The laptop is shared: CPU-heavy work
  must not starve the live bot (it logs CPU-STARVED lines in overnight.out).
- Never stage icebow/data/ (secrets: discord_webhook.txt). Commit + push verified work to main with a clear message
  ending "Co-Authored-By: Codex gpt-6-astra (autopilot)"; update HANDOFF.md in the same commit. Never force-push.
- Measurements: paired comparisons with CIs; never quote a pro-agreement number without a play rate; label claims
  measured / untested / contradicted. One change per experiment unless the owner already said otherwise (HANDOFF).
- Discord: post ONE short daily summary per day at ~20:47 local through 2026-10-05 with
  `icebow/.venv/Scripts/python.exe scratchpad/gauntlet/L69/discord/post.py <msg.txt>` (never print the URL), plus a
  post for anything that needs the owner urgently (live run dead and not recoverable).

## THE PLAN (priority order; skip what is blocked or already done per JOURNAL)
1. Live run health check every run (supervisor.log, overnight.out results tally, restarts used); keep it alive.
2. VM re-drive (ssh -i ~/.ssh/clashbot_gcp clashbot-gauntlet@136.108.166.193): when `~/cb/ABIL_DONE` exists, fetch the
   6 `<corpus>_abil` dirs (tar|gzip over ssh as in scratchpad/gauntlet/L68/generalist/pilot/../pilot_drive.md "Fetch";
   local paths mirror the VM's), verify replay_*.json counts == ok rows in summary.jsonl, THEN `sudo poweroff` the VM.
   Record counts + failures. Do not delete the old VM (owner).
3. gen_v3 results: `scratchpad/gauntlet/L70/gen_v3/chain.log` (ghost screen vs gen_v1 base, reactive) -> HANDOFF.
   gen_v3 live = OWNER decision (blocker) even if it looks better.
4. R1t from gen_v3 (`scratchpad/gauntlet/L70/rl/run_r1t_v3.sh`, log night3.log): record its acceptance when done.
5. gen_v3.1 data (needs step 2): dataset_gen must read the re-drive's native ids (entity rows end
   [native card_id, entity_id]; evolution-form ids 13000xxx = evolved, hero_form_id = hero) for EXACT per-unit forms with
   stable ids; opp_past = live-detectable plays only (bodies + spells seen as projectiles/effects by reader v2); add the
   derived full-cycle opponent input (public plays only); tests + parity with the reader v2 live path
   (pipeline/live_gen.py must build the same features from reader v2 frames). Build the dataset, train gen_v3.1 with
   gen_v1's recipe + `--amp bf16` (scratchpad/gauntlet/L69/gen_v2/_train_every_epoch.py wrapper), run the same
   acceptance as gen_v3 (accept_v3.sh pattern). Live = owner decision.
6. Ability press models (scratchpad/gauntlet/L70/abilities/): calibrate per-ability intercepts so pressed share and
   median delay match phase 1 (abilities.md); wire them into pipeline/royale_env.py `hero_abilities` for heroes AND
   champions (Boss Bandit charges, all others one use); tests; then R1e from gen_v3 (or gen_v3.1 if ready) on the evo
   census (scratchpad/gauntlet/L70/pool_forms/loadable_decks.json) per the pre-registered rule in HANDOFF.
7. Reader v2 next fields (only after 1-6 are moving): status effects / buffs, ability state, deploying units -- record
   findings; do not change the live path without a blocker entry.

## EVERY RUN ENDS WITH
Append to `.foreman/codex_autopilot/JOURNAL.md`: timestamp, what you checked, what you did, MEASURED results (numbers,
paths), commits, what is running now, the next step. Keep it factual and short.
