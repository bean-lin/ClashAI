# Decisions Codex must not make -- for the owner/lead (newest last)

## 2026-10-03 15:38 EDT -- native area effects omitted, Rocket hit labels/behaviour coverage incomplete

- MEASURED source defect: native `effects` comes from the bridge's generic observed_effects list (jni_bridge.cpp:1988), while real area effects are separately exported at2099 as `area_effects`. replay_drive.py:452 records generic effects and discards area_effects. Three completed diagnostic re-drive samples have exact projectile-to-generic-effect aliases on every sampled frame and no area_effects field. Version4 now ignores generic aliases and refuses training with `native_area_effects_unavailable`. Earlier native_timing_evidence.json counted aliases as effects and is SUPERSEDED by native_source_audit.json.
- What: validate a corrected public area/timing recorder before any additional re-drive; choose whether/how to attribute Rocket tower hits from replay evidence and define the pro-context classifier's verified target labels. No new VM spending or live reader change authorized by this discovery.
- Evidence: `L70/gen_v31/native_source_audit.json`, `native_sample_mining_1510_v2/`, diagnostic receipt under `runs/rocket_native_samples_1510/`; bridge and recorder source above. Six near-tower Rocket flights in three native samples align with342-HP drops; that is compatible damage, not independent causal attribution. No universal497-HP damage threshold was applied to training.
- Legacy mining:14661 unique replays /9176 Rockets /5557 near-tower candidates,1349 multi-Rocket candidate sequences;157 duplicate-tag variants excluded in the same first-corpus order as dataset_gen. Most candidates are above497HP (5091/5557). These are geometric candidates, not all confirmed hits; full `_abil` mining is pending retrieval.
- Baseline gap: the pinned299 ghost logs measure Rocket share/play rate/elixir, but omit tower context, barrel flight/landing traces and final HP. The remaining five behaviour metrics are null/UNMEASURED in `behavior_baselines.json`. New instrumented baseline matches require resources and IPC currently unavailable while R1t/live run. The currently running R1t acceptance is unchanged; do not call it full updated behaviour acceptance.
- Options: (A) validate public recorder fields and add passive telemetry, then remeasure/fit on verified native data; (B) explicitly approve a documented proxy target (and its error audit) for the classifier. Recommendation:A. Keep gen_v3.1 training/live and R1e blocked; retain the required current live run and R1t.

## 2026-10-03 15:38 EDT -- publication retry denied

- Explicit scoped `git add` again failed creating `.git/index.lock` (Permission denied); staged diff remains empty. HEAD is lead commit `9e0b85b`. No commit or push occurred. A reviewed patch/manifest will be refreshed after the final evidence checkpoint. This is the same read-only metadata restriction, not a Git conflict.

## 2026-10-03 15:20 EDT -- required projectile timing is absent from source data

- What: complete and validate timing sources before the mandated gen_v3.1 retrain. No permission to omit the required timing inputs is inferred.
- Why: `research/sandbox_tools/replay_drive.py` snapshot stores six-column projectile rows and four-column effect rows, losing time-to-impact and remaining lifetime. `py.rs` PROJECTILE_FIELDS omits impact time; Flight.delay_ticks is pre-flight delay, not impact time. Reader v2 exposes target coordinates and effect remaining_ms, but no projectile time-to-impact. The ongoing VM job cannot retroactively recover discarded timing.
- Options: extend/validate public timing extraction and authorize any required additional re-drive cost; or approve a named public-trajectory estimate and its cross-source validation. Recommendation: validate a causal estimate using only observed motion before deciding whether another re-drive is necessary. Do not use future landing frames as model input or silently treat unknown as zero. This run retains unknown masks and rejects full training with missing timing.
- Evidence: `pipeline/projectile_observation.py`, `pipeline/tests/test_projectile_observation.py`, `research/sandbox_tools/replay_drive.py:438`, `research/ext/Royale/RoyaleSim/crates/royalesim/src/py.rs:310`, `scratchpad/gauntlet/L70/reader/FINDINGS.md`.

## 2026-10-03 15:20 EDT -- active R1t contention and publication restriction persist

- What: whether to change the resource allocation of the already-running R1t if live starvation persists. It was launched by the lead and its recipe/run directories remain untouched.
- Why: LIVE logs report median decisions 101-103 ms while R1t advances; this run has launched no GPU job. Changing/stopping the inherited training is an owner decision under the brief.
- Options: keep the lead's run; approve lower actor count/priority on a later launch; approve intervention. Recommendation: no additional heavy work, retain both required running jobs, and record the observed contention.
- Publication: this session still declares `.git` read-only with escalation disabled. The existing index.lock permission blocker remains; do not route the Git write through another tool to bypass it.
- Evidence: `L70/live/overnight.out`, `L70/rl/r1t_v3_gpu.out` u0010, current environment permissions; prior publication blocker.

## 2026-10-03 13:53 EDT -- ability intercepts do not establish both requested matches

- What: whether to allow a timing-dependent calibration (e.g. intercept plus age term), or accept declared residuals after intercept-only calibration. No calibration acceptance tolerance was registered. R1e and production ability-policy replacement remain blocked.
- Why: offline intercept candidates fitted on 11,728 non-test replay tags; evaluated on the existing 2,933 test tags. Fit-share residual at most 0.1241 pp, but heldout share residuals span -5.8175 to +6.7104 pp. Archer Queen presses 84.3% vs phase-1 79.6%, median all-press delay 7.60 s vs 10.65 s. Its paired delay change vs uncalibrated is only +0.25 s, 95% replay-bootstrap CI [0.00, 0.851]. Tombstone hero median 13.45 vs 10.575 s. These are reconstructed-board measurements, not engine-accepted presses or live performance.
- Options: (A) retain offline candidates and remeasure on ability-driven/native-id recordings; (B) approve adding a timing parameter and specify acceptable share/delay error; (C) approve these residuals explicitly. Recommendation: A, then B if residuals persist. Do not relax the R1e primary rule.
- Additional limits: phase-1 targets include test tags; denominator is inferred card deployments rather than confirmed eligible living controllers; Boss Bandit phase-1 all-press median is 11.65 s (first-press median 9.8 s). Existing phase-2 cadence/cooldown proxies are retained, not engine-validated.
- Evidence: `scratchpad/gauntlet/L70/abilities/calibration_report.json`, `calibration.py`, `test_calibration.py`, `abilities.json`, `abilities_phase2.md`. Original `ability_models.json` and runtime remain unchanged.

## 2026-10-03 13:53 EDT -- gen_v3 / gen_v3.1 live selection reserved

- What: choosing either new checkpoint for ladder play remains the owner's decision, regardless of offline results.
- Why: live is rseries_r1_u0155 with reader v2; gen_v3 finished training 13:49 and acceptance is in progress. VM native-id/ability re-drive is still running.
- Options: keep current live checkpoint; authorize a named new checkpoint after reviewing paired acceptance and input parity. Recommendation: keep the current run until the owner reviews evidence.
- Evidence: `scratchpad/gauntlet/L70/gen_v3/chain.log`, `scratchpad/gauntlet/L70/live/supervisor.log`, this run's JOURNAL entry.

## 2026-10-03 14:07 EDT -- R1t cannot create its multiprocessing queue in Codex sandbox

- What: relaunch the corrected authorized R1t chain from a process with normal Windows IPC permissions. No change to experiment design is needed.
- Why: the original 13:59 launch rejected `gae_terminal_gap` because the copied R1 YAML lacked its default. That is fixed and all 31 launch/terminal-gap/gamma tests pass. Native relaunch 14:06 parsed the exact recipe and completed startup pro-agreement, but `multiprocessing.connection.Pipe(duplex=False)` failed at `_winapi.CreateFile` with WinError 5 while constructing ActorPool. No actor or training update started. Git Bash itself also fails CreateFileMapping in this sandbox.
- Options: owner/lead launches `scratchpad/gauntlet/L70/rl/run_r1t_v3.sh` outside this sandbox after checking GPU availability; or provide an execution environment allowing Windows IPC. Recommendation: relaunch the existing shell chain with the corrected YAML. Do not alter the actor count, transport or training algorithm merely to bypass this permission restriction. The native helper intentionally refuses overwriting existing checkpoint artifacts.
- Evidence: `scratchpad/gauntlet/L70/rl/r1t_v3_gpu.out`, `.out.err`, preserved `.saved_*` initial failures; `.foreman/codex_autopilot/runs/r1t_tests_acl.out` (31 passed); `icebow/data/bench/rl_royale/rseries_r1t_v3/rseries_r1t_v3_crash_u0000_1791050795.pt`. GPU training is stopped; live remains running.

## 2026-10-03 14:09 EDT -- publishing is blocked by read-only Git metadata

- What: stage, commit and push the verified work to main with the required trailer, including HANDOFF, JOURNAL and BLOCKERS.
- Why: `git add -- HANDOFF.md ...` fails `Unable to create '.git/index.lock': Permission denied`. This session explicitly has read-only access to `.git` and no permission escalation. No files were staged by this attempt.
- Options: owner/lead commits the reviewed paths from a write-enabled environment, or provide Git write permission. Recommendation: commit only the autopilot's explicit paths after review; never stage `icebow/data/` or the numerous unrelated dirty/untracked files.
- Evidence: current working tree, `.foreman/codex_autopilot/JOURNAL.md`; HANDOFF describes each batch. Required trailer: `Co-Authored-By: Codex gpt-6-astra (autopilot)`. Push remains unattempted because no commit could be created.

## 2026-10-03 14:19 EDT -- opponent ability readiness is not established as public

- What: scope of any future opponent ability-state input (cooldown, charges, readiness). This does not block observing visible ability effects or the player's own button.
- Why: the older sandbox bridge exposes internal ability components, but availability in memory does not establish public observability. Owner's no-hidden-state rule applies; no such field was added or read from the live process.
- Options: own-side ability state only; public-effect-derived opponent history; or owner-approved specific publicly visible opponent fields after evidence. Recommendation: own side plus visible effects, retaining unknown for internal opponent readiness.
- Evidence: `scratchpad/gauntlet/L70/reader/NEXT_FIELDS_AUTOPILOT.md`, sandbox bridge lines 1535-1566. New live offsets remain untested.

## 2026-10-03 14:58 EDT -- legacy IL/pro-agreement opponent-elixir input audit

- What: owner/lead review of legacy datasets/checkpoints and how to label prior acceptance numbers. Do not silently redesign R1t, replace the live checkpoint, or invalidate prior experiments by declaration.
- Why (MEASURED): the generic dataset adapter fills scalar columns 5/6 from recorded opponent elixir and the legacy generalist builder retains them. The real native sample has 281/281 truth-known legacy rows; the public-only replacement differs in 262. A bounded read of stored `gen_dataset_v3.npz` confirms its first 1,024 scalar rows all mark opponent elixir known. This is an input/provenance issue; it does NOT establish that the current live runtime reads hidden opponent elixir (live uses a public counter).
- Options: audit and relabel historical IL/pro-agreement results; authorize a clean public-input baseline/retrain; decide separately whether any ongoing experiment should stop. Recommendation: retain the required live run, use the public counter in gen_v3.1, and review historical claims before any new live selection. Current R1t was externally relaunched at14:55; this Codex process did not launch or stop it.
- Evidence: `L70/gen_v31/legacy_privacy_audit.json`, `sample_evidence.json`, `pipeline/tests/test_gen_v31.py::test_real_dataset_privacy_and_exact_forms`. Opponent hand/next/deck-form/elixir mutations leave new side-zero features unchanged; a legacy positive control changes the elixir scalar. No ability policy or live checkpoint changed.

## 2026-10-03 16:05 EDT -- source-recorder preparation, validation still required

- Prepared an opt-in public-object evidence recorder locally;26 offline tests pass. It retains separate area exports,
  projectile identities and raw source timers under unvalidated names. Default output is HEAD-identical in tests.
- This does not resolve the existing area/timing blocker: the ongoing VM job uses its existing remote code, and the
  bridge's area timer interpretation is still unverified. No additional paid capture or live path change was made.
- Options remain: approve a bounded high-cadence validation capture/new corpus after reviewing the recorder; or
  explicitly approve a tested causal timing estimate. Recommendation: validate raw source semantics first, then
  choose capture scope using the completed corpus's coverage. Evidence/runbook: `research/sandbox_tools/PUBLIC_OBJECT_RECORDING.md`.

## 2026-10-03 19:21 EDT -- decisions remaining after verified native retrieval

- Retrieval is no longer blocked: all14818 files verified, both VMs independently confirmed Stopped in the
  authenticated cloud console; neither deleted. Full native Rocket/Barrel audits and ability-event coverage are complete.
- Full data DOES contain native tiebreak HP-drain labels. This corrects the early sample-only coverage limitation;
  it is not proof of original human intent. Native Rocket candidates6307, multi-Rocket sequences1552; causal hit
  labels and the held-out pro-context classifier/weight remain absent. Keep the existing label-validation decision open.
- Native timing and true area-effect retention remain deficient for the required gen_v3.1 input. Options remain
  validated corrected capture (any additional cost/scope needs owner choice) or a separately approved, validated
  public-motion estimate. Recommendation: source validation first; do not silently omit the required fields.
- Accepted ability-controller coverage is now measured:40496/40496 accepted activations have a fresh matching
  living native entity. Eligible lifetimes/readiness and exact deployment delay are not established by this audit.
  The intercept share/delay tradeoff and calibration tolerance/extra-parameter decision remain open; no runtime
  ability model replacement or R1e launch. Recommendation: adapt/revalidate extraction using the native IDs and
  accepted activations before choosing calibration acceptance. Existing legacy-calibration candidates are not approved.
- Baseline model behaviour metrics beyond Rocket share are still missing; pro corpus audits do not substitute for
  gen_v1/u0155/gen_v3 instrumented baselines. Legacy hidden-elixir provenance and publication/IPC decisions remain open.
- Evidence: `L70/gen_v31/NATIVE_ROCKET_REPORT.md`, `NATIVE_BARREL_REPORT.md`, `L70/abilities/NATIVE_EVIDENCE.md`,
  `runs/native_audits_1552.receipt.json`, `runs/vm_cloud_status_1819.json`, and the earlier blocker entries.

## 2026-10-03 20:35 EDT -- X-Bow geometry is not a validated defensive label

- What: validate the intended defensive-versus-bridge label before fitting joint Rocket/X-Bow context weights or claiming the defensive behaviour metric.
- Why: the inherited audit's y>0.58 rule labels the common y=.609375 row as defensive (3.5 tiles behind river). Exact pro/bot rows can be measured, but that bucket alone does not establish tactical role. Forward is decreasing normalized y on both sides. No strategic label was inferred from the player's future hidden state or from lane death.
- Options: owner/lead approves a reviewed public geometry/board-context label with audited examples; or use declared geometric buckets only and leave strategic intent unmeasured. Recommendation: inspect exact placement and public board examples from the native census before fitting. Do not silently redefine acceptance or add an X-Bow action rule.
- Evidence: `L70/audit/play_audit.py:347`, `L70/gen_v31/XBOW_BASELINES.md`, `xbow_baselines_2020.json`, `mine_xbows.py`. The latter reports exact rows, public princess/crown state and same-side10s tower-Rocket candidates; causal hits and joint classifier remain blocked by the earlier entries.

## 2026-10-03 20:48 EDT -- publication restriction reverified

- Scoped git add failed creating `.git/index.lock` with Permission denied; staged diff remains empty. Commit/push cannot complete inside the declared read-only Git boundary, and no alternate tool/checkout is used to bypass it.
- Verified X-Bow/contract/report work is preserved in the working tree and explicit delivery patch/manifest. Owner/lead can publish the reviewed paths from an environment with writable Git metadata, excluding icebow/data and using the requested Codex trailer. No permission question is needed to preserve the already authorized work.

## 2026-10-03 22:12 EDT -- final source/label handoff after both-order census

- What: complete causal troop/tower hits, defensive context labels and flight/pull/impact timing before fitting the six-target joint IL weighting and claiming full behaviour acceptance. This continues the earlier source/label blocker; no acceptance rule was weakened.
- Why (MEASURED): all14,661 unique replays/10,045 Rockets audited. Historical cast-prior counts are494 Rocket->Tornado and21 Tornado->Rocket;489 first-order cases have exact observed flight. The3,738 non-tower candidates include2,283 own-half aims, but neither half nor non-tower geometry proves defensive intent. Nominal troop-body cost median5.0 is not actual elixir value hit. Sparse body damage/disappearance cannot separate Rocket from simultaneous damage or prove pulled-group landing time. Policy ghost logs retain no required flight/pull/tower-state timeline; eleven full behaviour metrics remain null.
- Options: validate corrected public source semantics and reviewed contextual labels, then instrument matched baseline replays; or owner explicitly approves a different, validated estimator/label contract. Recommendation: source validation and reviewed examples first. Additional paid capture or replacing a required metric is an owner decision. No such work was launched, no model action rule added, no checkpoint deployed.
- Evidence: `L70/gen_v31/NATIVE_ROCKET_TORNADO_REPORT.md`, `native_rocket_tornado_2140/`, `combo_order_comparison_2140.json`, `runs/combo_verification_2140.json`, `runs/behaviour_coverage_2140.json`, and `research/sandbox_tools/PUBLIC_OBJECT_RECORDING.md`.
- Ability calibration share/delay tolerance and public readiness/lifetime decisions remain as recorded. R1t's old execution blocker is historical: the lead's external14:55 launch completed training21:17 and both acceptance sets21:32. A future multiprocessing launch from this sandbox remains unvalidated; no IPC bypass is authorized or attempted.
- Publication rechecked22:11: scoped add still cannot create `.git/index.lock`; staged diff empty. No autopilot commit or push exists. Review the explicit delivery patch/manifest from a Git-write-enabled environment, never stage icebow/data, and use `Co-Authored-By: Codex gpt-6-astra (autopilot)`.

## 2026-10-03 22:3x -- OWNER ANSWERED (relayed by the lead): see TICKET.md 'OWNER DECISIONS 2026-10-03 22:3x' items 1-7.

## 2026-10-04 21:31 EDT -- Q0 source telemetry gap; measurement continues
- What/why: Q0 requests trophy progression and pre-emptive Log rates. Existing live_play frame events save entities/elixir but omit projectiles; live/nav event schemas do not save numeric trophies. Verified selected source prefixes in L71/live_comparison/report.json:38/303 old and2/9 R1e ended logs have frames, zero frames have a projectile field. These metrics remain null, not zero. Win/loss, card counts, ability presses and X-Bow coordinates are available.
- Options: (A) continue available observational metrics and defer new logging to the next owner-approved live restart; (B) owner authorizes a logging-only change/new live launcher, with public projectile fields and an explicitly measured trophy-reading source; (C) separately analyze saved videos as a sparse sample, which cannot recover a complete historical trophy or barrel denominator.
- Recommendation: A now; prepare B for the next owner-requested live change. No active live source/process/override changed. Q1/Q2 CPU work remains unblocked. Historical missing data cannot be reconstructed by treating wins as fixed trophy gains.
- Q1 design note remains: with ratio0.5, probabilities[0.6,0.4] retain both cards, so near-zero confident-row overrides are not guaranteed by construction. Measure the requested settings and report/reject failing candidates; do not silently add a new cutoff or relax the agreement/adoption rules.

## 2026-10-04 -- AUTHORIZED: R1e live anti-leak ablation
- Owner explicitly requested: turn off the hardcoded anti-leak rule and redeploy the R1e model live to observe performance. This authorizes the live stop/restart and setting change; no approval remains pending for this experiment.
- Decision: opt-in --no-anti-leak disables only the forced-spend override. Keep R1e u0155, tau0.35, argmax cards/cells, public counter, look-ahead, abilities and existing recording settings. Default standalone behaviour remains unchanged; the persistent supervisor opts in.
- Evidence and deployment boundary: scratchpad/gauntlet/L71/leak_ablation/deployment.json and GATES.md. This is an owner-requested live observational test, not a simulator acceptance result or a proven improvement. Separate its matches from earlier R1e matches when reporting. Sampling and spell aim remain separate experiments.
