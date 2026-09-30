# Reward-shaping plan for icebow RL (2026-09-30, DRAFT for owner approval)

Owner's rule: "We can bring shaped rewards back but we can't blindly introduce terms anymore; we need to carefully
plan out and implement the reward system to prevent collapses."

## 0. What history says (the failures we must not repeat)

| # | What broke | Evidence | Lesson |
|---|---|---|---|
| 1 | A **free-standing** penalty (`threat_miss_idle`) charged every step | bar at 0-2 for 91% of steps; hold-to-6 scored 8.5x worse than spend-immediately (HANDOFF §4.1) | Never add terms that are not potential differences; test scripted behaviours BEFORE training |
| 2 | Play gate collapsed with no gate prior | engA 36 -> 0.12 plays/match, gate max 0.23 < tau (§5cs.46) | Keep the gate prior; watch an UNCONDITIONAL play rate |
| 3 | Placement collapse under PPO | row 13 from 41% to 84.5% of plays, 28/432 cells (§4.3) | Per-card cell-entropy alarms, not just a global one |
| 4 | Graded placement reward narrowed cells | Knight 1 distinct cell; watchdog "cell head collapsed"; no control run (archive :12611) | Every shaping arm needs a matched no-shaping control |
| 5 | KL leash froze learning | pro agreement 15.44 -> 16.33 -> 15.64 (§5cs.44-51) | The leash stops collapse AND learning; its tightness is its own experiment |
| 6 | Conditional-metric blindness | top-1 16.73 while playing 0.12 times per match (:1921) | Every conditional metric needs an unconditional companion |
| 7 | Friend's elixir potential as loud as winning | 0.80 vs terminal 0.80 per episode (RoyaleLearn rewards.py:446); his run then played Hog 95%, Cannon 0.6%, Log 1.0% (hog26-9 notes) | Budget each term's magnitude; spells and buildings need fair pricing or none |

## 1. The key structural fact about OUR learner

`pipeline/rl_royale.py` gives every decision in a match the SAME advantage: the match's win/loss, minus a
leave-one-out group baseline (`loo_advantage`, :460-475). There is no per-step return and no critic.

Potential-based shaping adds `F_t = gamma * Phi(s_{t+1}) - Phi(s_t)` per step with `Phi(terminal) = 0`. Summed over a
match this **telescopes to a constant** (`-Phi(s_0)`, identical for every match of the same start). So **added to our
current per-match advantage, shaping changes nothing at all.** Shaping only helps through per-decision credit: the
return from each decision onward. Hence two separate changes, in order.

## 2. The plan: one change per experiment, each gated

**R0 (running now): league1c.** league1b plus the learner always on icebow (opponent decks unchanged). No reward change.
It tells us whether concentrating the signal on one deck matters. It is the baseline for everything below.

**R1: per-decision credit, win/loss only.** Replace the per-match advantage with per-decision returns-to-go plus a value
baseline (GAE; the model already has a value head, currently trained only as an auxiliary crown-difference predictor).
Reward still win/loss only. This is what makes shaping possible, and it is a change on its own, so it gets its own
run and its own verdict against R0. Risk: a poor critic makes noisy advantages. The value head's outcome accuracy is
0.70 at init. Mitigation: fit the critic for N updates with the policy frozen before any policy step.

**R2: potential-based shaping, two terms only.** On top of R1:
- `Phi_tower = w_t * (sum own tower HP fraction - sum foe tower HP fraction) / 3`
- `Phi_crown = w_c * (own crowns - foe crowns) / 3`
- `F = gamma * Phi(s') - Phi(s)`, `Phi(terminal) = 0`, gamma the same gamma the returns use (checked by a test).

**No elixir potential in R2.** It is the term that dominated the friend's run, the kind of term behind our own §4.1
collapse, and it misprices spells (a spell never becomes a board unit, so casting one always "loses" elixir
potential). It gets its own step R3 only if R2 is clean, with spell pricing fixed and a hard magnitude cap.

## 3. Pre-flight checks before ANY shaped training run (cheap, CPU, minutes)

1. **Telescoping test:** on recorded matches, the per-match sum of F equals `-Phi(s_0)` to float precision.
2. **Magnitude budget:** on 100 matches of the IL policy, mean |sum of per-step F| per match is at most 0.5 x the
   terminal magnitude (the friend's term was 1.0x). If it is over, reduce w before training.
3. **Scripted-behaviour audit** (the check that caught §4.1): compute per-decision advantages under R1+R2 for scripted
   policies: IL policy, never-play, spend-immediately, hold-to-9, spam-one-card, never-buildings, never-spells.
   No degenerate policy may have a HIGHER mean advantage than the IL policy. If one does, stop and redesign.

## 4. Collapse alarms during training (automatic stop rules)

The existing guards stay: entropy floor per head, plays/min band, KL stop, screen exploit guards, pro-agreement
tripwire. New ones:

| Alarm | Stops when | Catches |
|---|---|---|
| per-card play rate per opportunity | any card < 25% of its IL-baseline rate for 3 consecutive updates | Cannon/Log-style suppression (friend), 4-costs never played (§4.1) |
| unconditional play rate | plays/match < 50% of init, or gate p90 == max to 3 decimals | gate collapse (engA) |
| elixir at play and leak share | mean elixir-at-play leaves [0.6x, 1.5x] of init, or 10-elixir share > 2x init | bar emptying / hoarding |
| per-card cell entropy | any card's cell entropy < 50% of init | placement collapse (§4.3, arm G) |
| shaping dominance | per-update mean |F| > 0.5 x terminal magnitude | a term louder than winning |
| spell and building share | share of plays that are spells or buildings < 50% of init | friend's building and spell decline |

Each alarm logs its reading every update, so a stop comes with the curve that caused it.

## 5. Evaluation (unchanged instrument, closed loop)

Each candidate is scored as league1 was (the pinned 299 train-split screen vs init) **plus** the S0 harness's plain arm:
candidate vs frozen gen_v1 and vs S1 on the same 24 seeds, paired. That is a closed-loop head-to-head the ghost
screen cannot provide. A matched no-shaping control is always the previous step's run (R0 for R1, R1 for R2).

## 6. Cost and order

- R0 league1c: one overnight GPU run (now).
- R1: code change (worker + verifier, about 1 day), critic warm-up, then one overnight run.
- R2: potential functions + the 3 pre-flight checks (CPU, hours), then one overnight run.
- R3 (elixir potential): only if R2 is clean.

Nothing here is implemented until the owner approves the plan.
