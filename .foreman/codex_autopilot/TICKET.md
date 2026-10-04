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

## RUN LENGTH (owner, 2026-10-03 14:00): nobody can re-launch you until Tuesday 2026-10-06 (the scheduler was not
## allowed and the owner is travelling). So DO NOT stop after one step: keep working through the plan in this single
## run -- check the live run between steps, wait for long jobs (training / VM) by polling at sensible intervals, and
## only finish when every item is done or blocked or your context is nearly exhausted. Before finishing, ALWAYS write
## the JOURNAL entry and commit+push.

## FIRST, THIS RUN ONLY (lead, 2026-10-03 ~15:10; restarted twice to deliver brief updates): the previous run was STOPPED by the lead mid-work to deliver this
## updated brief. Run `git status` / `git diff`: it left UNCOMMITTED edits in pipeline/{dataset_gen,e1_eval,eval_gen,
## live_gen,model_gen,rl_royale,train_gen}.py and scratchpad/gauntlet/L69/rl/r1_rl_royale.yaml. Read the last JOURNAL
## entries + the stopped run's log (newest-but-one in runs/), then FINISH or cleanly REVERT those edits (tests must pass;
## every v1/v2/v3 default path byte-identical). CAUTION: R1t from gen_v3 is TRAINING NOW (started 14:55) and imported
## rl_royale.py at its start -- do not change behaviour R1t depends on; never touch its run dirs.

## OWNER DECISIONS 2026-10-03 22:3x (answers to BLOCKERS.md -- apply them; mark those entries RESOLVED)
## 1. Rocket-hit / area-effect labels: use B NOW (a documented proxy label + an error audit) so gen_v3.1 is not stuck,
##    AND start A in parallel: fix + validate the native recorder (public area effects, causal Rocket hits on troops /
##    towers) for a NEW VM re-drive. The VM is powered off; the owner starts it and gives the IP to the lead (it
##    changes) -- prepare everything so the re-drive starts the moment it is up (runbook + jobs + a 20-replay check
##    that EVERY requested field is present and sane BEFORE the full run).
## 2. Projectile time-to-impact: ESTIMATE it now from observed motion (past frames only); ALSO record it in the
##    option-1A re-drive.
## 3. Ability calibration: A (re-measure on the ability-driven native recordings) THEN B (add a timing term; report
##    share and delay error per ability).
## 4. X-Bow defensive label: review examples first (pull audited examples from the native census into a short report
##    with board context; the lead / owner approve the label on Tuesday unless it is unambiguous).
## 5. Opponent ability state: own-side ability state + visible effects only; opponent internal readiness = unknown.
## 6. Opponent-elixir leak: AUDIT + RELABEL every historical IL / pro-agreement result that used true opponent elixir
##    (list datasets, checkpoints, numbers affected), THEN the clean public-input retrain (gen_v3.1 uses ONLY the
##    public counter; with reader-v2 spells the public estimate should be close to the truth -- MEASURE its error).
## 7. POST-MORTEM (owner): "I made it very explicit what needs to be included in the re-drives and trainings, yet so
##    many things were missed." Write `.foreman/codex_autopilot/POSTMORTEM.md`: every requested item that was missed
##    or caught late (re-drive fields: area effects, Rocket hit causality, time-to-impact; training inputs), WHO missed
##    it (the lead's re-drive spec/validation vs your implementation/checks), WHY each check did not catch it, and the
##    concrete pre-flight checklist you will run from now on before any re-drive / dataset build / training (verify
##    every requested field end-to-end on a small sample first). Post a short summary to Discord.

## OVERNIGHT GOAL (owner 2026-10-03 22:5x): "When I wake up tomorrow, I expect gen_v3.1 set up with all the new
## components, trained, and deployed on live (you have my authorization to deploy immediately when it's ready)."
## - VM is UP again: ssh -i ~/.ssh/clashbot_gcp clashbot-gauntlet@34.73.26.199 (NEW IP). Run decision 1A's re-drive on
##   it once the recorder passes the 20-replay field check; gen_v3.1 does NOT wait for it (decision 1B proxies now).
##   Power it off after fetching (sudo poweroff).
## - gen_v3.1 training is single-process (train_gen + --amp bf16) -> run it yourself when the GPU is free. Acceptance:
##   run_screen + search_s0 with `--workers 1` (multiprocessing is blocked in your sandbox; workers 1 runs in-process).
## - DEPLOY when READY = trained + acceptance done (ghost screen paired vs u0155 + reactive + behaviour metrics) + a live
##   smoke (live_gen decisions on recorded reader-v2 frames, scratchpad/gauntlet/L70/reader/sidebyside/re_v2xb.jsonl,
##   no crash, v3.1 features non-empty) + NOT clearly worse than u0155 (paired ghost CI not entirely below 0). Deploy =
##   write the checkpoint path (one line) to scratchpad/gauntlet/L70/live/CKPT_OVERRIDE; live_play ends its run between
##   matches and the supervisor restarts on it (rollback: write the u0155 path back). Then post Discord "DEPLOYED
##   <ckpt>" with the evidence, and watch the next few matches in overnight.out (crash -> roll back + Discord).

## DISCORD REPORTS (owner, 2026-10-03 15:2x) -- post with `icebow/.venv/Scripts/python.exe
## scratchpad/gauntlet/L69/discord/post.py <msg.txt>` (never print the URL) after EVERY MAJOR MILESTONE (e.g. stopped-run
## edits reconciled, VM data fetched + VM off, pro tower-Rocket mining report, behaviour baselines, gen_v3.1 code done,
## dataset built, training done, acceptance results, ability models wired): plain language, <= ~1500 chars: what was
## achieved, the measured results AND what they mean, the next steps. Plus the daily summary at ~20:47.
## BETTER CHECKPOINT: if any checkpoint beats the LIVE one (rseries_r1_u0155: ghost +3.0 pp [-0.3, 6.4] vs the gen_v1
## evo base, reactive gen 14/24, S1 24/24) on the acceptance instruments (paired ghost screen CI and reactive play, plus
## the behaviour metrics), post a Discord message headed "APPROVAL NEEDED: deploy <checkpoint> live?" with the evidence.
## NEVER deploy it yourself -- the owner approves.

## THE PLAN (priority order; skip what is blocked or already done per JOURNAL)
1. Live run health check every run (supervisor.log, overnight.out results tally, restarts used); keep it alive.
2. VM re-drive (ssh -i ~/.ssh/clashbot_gcp clashbot-gauntlet@136.108.166.193): when `~/cb/ABIL_DONE` exists, fetch the
   6 `<corpus>_abil` dirs (tar|gzip over ssh as in scratchpad/gauntlet/L68/generalist/pilot/../pilot_drive.md "Fetch";
   local paths mirror the VM's), verify replay_*.json counts == ok rows in summary.jsonl, THEN `sudo poweroff` the VM.
   Record counts + failures. Do not delete the old VM (owner).
3. gen_v3 results: `scratchpad/gauntlet/L70/gen_v3/chain.log` (ghost screen vs gen_v1 base, reactive) -> HANDOFF.
   gen_v3 live = OWNER decision (blocker) even if it looks better.
4. R1t from gen_v3 (`scratchpad/gauntlet/L70/rl/run_r1t_v3.sh`, log night3.log): record its acceptance when done.
5. gen_v3.1 = THE major gap-closer retrain (owner 2026-10-03: "major gap closers, get this done soon"). It MUST
   include, besides the items below: (a) PROJECTILE INPUT -- tokens for projectiles in flight (card, side, x, y,
   target_x, target_y, time-to-impact) and spell area effects (card, x, y, remaining ms), consistently in TRAINING (the
   re-drive's --record-full frames), SIM (RoyaleSim PROJECTILE_FIELDS / SPELL_FIELDS in research/ext/Royale/RoyaleSim/
   crates/royalesim/src/py.rs) and LIVE (reader v2 `projectiles` / `effects`, scratchpad/gauntlet/L70/reader/
   FINDINGS.md) -- so the model can learn the pros' PREEMPTIVE LOG on a Goblin Barrel / Skeleton Barrel near the end of
   its flight; parity tests across the three paths. (b) ROCKET ON TOWERS, learned from PROS (owner 2026-10-03: a Rocket is NOT only a one-shot finish below 497 HP --
   pros cycle 2-3 Rockets over a longer span to finish a fairly low tower, and Rocket-cycle a tower purely to build a
   tower-damage lead and let the end-of-match TIEBREAKER decide). Do NOT hand-define when to Rocket. First MINE every
   pro Rocket that hits an enemy crown tower (replays + the re-drive's projectile records): tower HP before, time left /
   phase / overtime, crowns and total tower-HP difference, elixir, the number of Rockets already on that tower and the
   gap between them, and whether the match was decided by the tiebreaker. Report the distributions (multi-Rocket
   sequences, tiebreak-driven Rockets vs finishes). Then give MORE WEIGHT in the IL loss to states that resemble pro
   tower-Rocket contexts (e.g. a per-row weight from a small classifier P(pro Rockets a tower here | public state); a
   knob tuned on a held-out set and reported) -- the model learns WHEN, no scripted rule -- and keep the elixir-banking
   signal (median elixir at a Rocket play: bot 6.8 vs pros 8.7, scratchpad/gauntlet/L70/audit/audit.md).
   (b2) X-BOW LANE + DEFENSIVE X-BOWS, mined the same way and in the SAME weighting (owner 2026-10-03: defensive
   X-Bows and Rocket cycling come hand in hand). Audit (scratchpad/gauntlet/L70/audit/audit.md): once an enemy princess
   is down the bot puts 10/18 X-Bows in the DEAD lane (1-1: 5/8), and it uses only 2 X-Bow rows. Mine pro X-Bow
   placements by tower state (enemy princess alive/dead per lane, crowns 1-0 / 0-1 / 1-1, time left / overtime),
   placement (lane; defensive vs bridge row; the board-y direction trap: forward = DECREASING y), and what follows (a
   Rocket on a tower within ~10 s, i.e. defensive X-Bow + Rocket cycle). Weight pro-like X-Bow contexts in the IL loss
   with the tower-Rocket contexts; no scripted rule.
   (b3) DEFENSIVE ROCKETS + ROCKET-TORNADO SYNERGY (owner 2026-10-03 21:0x; your native audit covered only Rockets on
   towers: ~6,307 of 10,045 pro Rockets). Mine the other ~37%: Rockets on enemy troops (what units, how much elixir
   value hit, own side vs enemy side, phase), and BOTH combo orders -- Rocket -> Tornado (owner: likely the MORE common timing; Tornado cast while the
   Rocket is in flight/landing to pull units into it) AND Tornado -> Rocket (Rocket landing on a Tornado-pulled group
   within ~2.5 s of the Tornado); report each order's rate separately; HANDOFF_ARCHIVE rocket_nado_window 2.5 s / radius 0.11 is a prior to check against
   the data). Same treatment: pro-like contexts weighted in the IL loss, no scripted rule; metrics: defensive-Rocket
   rate and the rate of EACH combo order vs pros.
   (c) ACCEPTANCE adds behaviour metrics next to the ghost screen and reactive play, for gen_v3.1 AND every later RL run:
   Rocket share of plays (pros 5.8%); Rocket-on-tower rate in the contexts where pros Rocket towers (from (b));
   multi-Rocket sequences on one tower; X-Bow dead-lane share once a princess is down (baseline 10/18) and defensive-X-Bow share in late game vs pros; X-Bow -> Rocket-cycle sequences; the end-of-match tower-HP margin in tiebreak finishes; the one-Rocket finish
   conversion (<= 497 HP, >= 6 elixir; baseline 0/14) as ONE of these, not the definition; and a preemptive-Log metric
   vs Goblin/Skeleton Barrel (Log cast while the barrel is in flight or within 0.5 s of landing, as a share of opponent
   barrels). Measure them for gen_v1, u0155 and gen_v3 first as baselines.
   gen_v3.1 data (needs step 2): dataset_gen must read the re-drive's native ids (entity rows end
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
