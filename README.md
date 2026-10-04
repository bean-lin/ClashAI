# ClashAI

> A bot that plays **Clash Royale** ranked ladder, live, with the **X-Bow control ("icebow") deck**.
> It learns from professional replays, is improved by reinforcement learning in a simulator, and is
> deployed on an Android emulator using **public information only**: what a human could see.

This is a hobby / research project about getting an agent to *actually play* a real-time game it
cannot peek inside. Nothing here is affiliated with or endorsed by Supercell.

> [!TIP]
> **New here?** [icebow/Instructions.txt](icebow/Instructions.txt) is a plain-English, from-scratch
> walkthrough of the pipeline below. [HANDOFF.md](HANDOFF.md) is the project journal (current state,
> measured results, traps) and is the most up-to-date document in the repo.

> [!NOTE]
> **Status (2026-10-04).** Live play works end to end on the trophy ladder, unattended, including
> between-match navigation and daily-chest collection. The best policy measured in the simulator is the
> reinforcement-learning checkpoint `rseries_r1_u0155`; the newest imitation models (`gen_v3.1a/b`) are
> trained on a richer, public-only observation and are **not yet measured as better**. Details and
> numbers are in [Results so far](#results-so-far).

---

## How it works

```
 pro replays (RoyaleAPI + HuggingFace)       14,818 recordings, 14,661 unique replays, 4,283 decks
        |
        v
 real-engine re-drive  -- each replay's commands are replayed tick by tick in the real game engine
 (research/sandbox_tools)   (Android emulator, deterministic), recording the board every few ticks
        |                   with PUBLIC observations: units, projectiles + time-to-impact, area effects
        v
 imitation learning  -- pipeline/dataset_gen.py (feature version 4) -> pipeline/train_gen.py
 ("gen" generalist)     = the gen_v3.1 models: copy where and when the pros play
        |
        v
 reinforcement learning -- pipeline/rl_royale.py: PPO in RoyaleSim, a fast simulator, with a league of
 (the "R-series")          opponent decks and a KL leash back to the imitation model
        |
        v
 simulator acceptance -- paired screens against recorded opponents and reactive opponents
        |                (run_screen.py, search_s0.py): nothing is deployed on a gut feeling
        v
 live deployment -- MuMu emulator: memory reader v2 -> GenPilot -> two ordinary Android taps
```

### The public-information-only rule

The bot may use only what a player sees on screen. The **opponent's hand, next card and elixir are never
fed to a model.** Live, the opponent's elixir is *estimated* by a counter over public events
(`pipeline/opp_elixir_count.py`: start value, the regeneration schedule, minus the cost of every play it
sees). The version-4 observation (`pipeline/public_observation.py`) adds only public things: the
opponent's recently seen plays and the distinct cards observed so far (never the hand or readiness),
projectiles in flight with their target and time-to-impact, spell area effects with remaining time, and
the bot's own ability state derived from its own confirmed presses.

The same builder feeds training, the simulator and live play, so the model sees the same kind of input
in all three places. One caveat, stated in HANDOFF: earlier checkpoints (`gen_v1` to `gen_v3`, the
R-series) were trained on dataset rows that still carried the recorded opponent elixir; they are labelled
*privileged-input* in the audit, and their live path already uses the public counter. Version 4 replaces
those scalars with the counter in training too.

### Why the real engine matters

An early version used a hand-written simulator and a pixel CNN; reinforcement learning from win/loss on
that stack never improved on its imitation starting point and is retired. The current pipeline instead
re-drives every pro replay inside the **real game engine**, so the states the model imitates are faithful
(the engine is deterministic: the same replay twice gives byte-identical states). Spells, evolutions,
heroes and abilities are driven too. The engine runs on a headless Android emulator and is expensive, so
reinforcement learning and acceptance tests run in **RoyaleSim**, a fast third-party reimplementation of
the game, with the real-engine data as the source of truth for what a pro would do.

---

## The models

All models share one network family (`pipeline/model_gen.py`, "GenModel"): entity tokens and spatial
patch tokens with coordinates feed a transformer; heads choose *play or wait* (gate), *which card*
(a pointer over the four hand cards), *which cell* (a full-resolution per-cell head conditioned on the
chosen card's identity), plus a "wait for card X" action and a value head. Card identity inputs mean one
network can play any deck.

| Model | What it is |
| :---- | :--------- |
| `S1` | The earlier icebow-only imitation model (deck-slot inputs). Kept as a fixed opponent in tests. |
| `gen_v1` | First generalist imitation model: indistinguishable from S1 on S1's own validation rows (cell 0.2071 vs 0.2097, card 0.6457 vs 0.6546). The base every later model is compared against. |
| `gen_v2`, `gen_v3` | Wait-label fix; evolution/hero form tags and opponent recent plays. Measured: **no gain** over `gen_v1`. |
| `league1c_u0075`, `rseries_r0p` | Earlier RL checkpoints. R0' did not reproduce the league1c gain on the newer engine. |
| **`rseries_r1_u0155`** | PPO from `gen_v1` with GAE advantages, per-tick discount and a critic warm-up (155 updates). The best policy measured in the simulator so far. |
| `rseries_r1u`, `r2`, `r1t` | One-change variants of R1 (undiscounted return; tower/crown shaping; terminal-gap discount from `gen_v3`). None demonstrated an improvement over R1. |
| `gen_v3.1a` | Imitation on the full version-4 public observation (3,517,863 rows from the complete re-drive), no loss re-weighting. Not deployed. |
| `gen_v3.1b` | `gen_v3.1a` plus six-target context weighting (Rocket on tower, Rocket on troops, Rocket-Tornado combos, offensive and defensive X-Bow). Switched live on 2026-10-04. |

## Results so far

All numbers are copied from [HANDOFF.md](HANDOFF.md), where the full context lives. Two instruments are
used, and they are never mixed:

* **Ghost screen**: the policy plays RoyaleSim matches against *recorded* opponent commands on 299 pinned
  held-out replays. Reported as a paired difference in win value, in percentage points (pp), with a 95%
  clustered bootstrap interval.
* **Reactive play**: the policy plays a reactive frozen opponent (`gen_v1`, or `S1`), 24 seeds; reported
  as wins out of 24.

| Comparison | Ghost screen (paired pp) | Reactive wins / 24 (vs `gen_v1`, vs `S1`) |
| :--------- | :----------------------- | :---------------------------------------- |
| `gen_v1` (evolution re-baseline) | reference | 12, 20 |
| `gen_v3` vs `gen_v1` | -2.3 [-6.4, +1.7] | 13, 20 |
| `rseries_r1_u0155` vs `gen_v1` | +3.0 [-0.3, +6.4] | 14, 24 |
| `rseries_r1` u0080 / u0155 vs R0' | +5.0 [+1.7, +8.7] / +4.7 [+1.3, +8.4] | -- |
| `gen_v3.1a` vs live `u0155` | -3.3 [-7.0, +0.3] (10 better / 20 worse) | 11 (u0155: 14), 15 (u0155: 24) |
| `gen_v3.1b` vs live `u0155` | -2.8 [-6.4, +0.7] | 15 (u0155: 14), 16 (u0155: 24) |
| `gen_v3.1b` vs `gen_v3.1a` | +0.5 [-3.0, +3.8] | -- |

How to read this: R1 beat its predecessor R0' with intervals that exclude zero, but against the plain
imitation base its interval touches zero. The `gen_v3.1` models are statistically level with each other
and slightly behind `u0155` on both instruments (the intervals include zero for 3.1b, just include it for
3.1a). On validation agreement with the pros, `gen_v3.1b` scores cell .2039 / card .6497, against
`gen_v3` .1973 / .6444 (rows not identical).

### Known weaknesses (measured)

* **Rocket use is far below the pros'.** Live audit of `league1c_u0075` (201 matches): Rocket was 1.0% of
  plays (72/7,024) against 5.8% in the reference pro icebow replays, and 0 conversions in 14 windows where
  an enemy princess tower was at or below a Rocket's 497 damage. `gen_v3.1b`: Rocket 93 of its plays
  (1.00%) in 299 ghost games. A diagnosis (`scratchpad/gauntlet/L71/rocket_diag/`) found the model puts
  P = .24 on the Rocket at pro Rocket moments (AUC .84), but the argmax picks it only 22% of the time, and
  the argmax cell for a tower Rocket hits a tower 28.5% of the time.
* **X-Bow placement collapses to a few cells.** Pros use about 24 cells for offensive X-Bows; the model's
  distribution is spread but argmax puts 93-94% of choices on two lane cells (pros 74%). Sampling more
  widely lowered pro agreement and was not adopted.
* **Late responses to Goblin Barrel.** The latency look-ahead (`pipeline/extrapolate.py`, 26 ticks) used to
  advance units only, not projectiles or effects, so the model saw a barrel about 1.3 s too "young" and
  answered late. The fix (R8: advance projectiles and effect timers by the same look-ahead, inference
  only) is **being implemented**; it will be judged by a paired simulator A/B before it goes live.
* **Pre-emptive Log** (Log on a Barrel before it lands): `gen_v3.1a` 64/272 (23.5%), `gen_v3.1b`
  126/274 (46%), pros 39.1%. One seed; the mechanism is untested.

---

## Repo layout

| Path | What lives there |
| :--- | :--------------- |
| [`pipeline/`](pipeline/) | The deck-agnostic pipeline: observation contract (`obs_contract.py`), dataset builder (`dataset_gen.py`), model (`model_gen.py`), trainer (`train_gen.py`), live decision logic (`live_gen.py`), RL (`rl_royale.py`, `royale_env.py`), acceptance (`search_s0.py`, `e1_eval.py`), public-observation modules, per-deck yaml in `decks/`, tests in `tests/`. |
| [`icebow/`](icebow/) | The X-Bow deck: original screen reader, YOLO detector, original trainer, config, templates. Has its own venv and `run.py`. |
| [`hogeq/`](hogeq/) | The Hog / Earthquake deck, a second copy of the same tooling (secondary; most current work is icebow). |
| [`research/`](research/) | Measurement ledgers and decision records. `research/sandbox_tools/` re-drives replays in the real engine (`replay_drive.py`, `replay_batch.py`, `run_public.py`). |
| [`tools/`](tools/) | Pro-replay download and dataset helpers ([`tools/README.md`](tools/README.md)). |
| [`scratchpad/gauntlet/`](scratchpad/gauntlet/) | **Dated experiment folders** (`L64`, `L68`, `L70`, `L71`, ...): each holds one research loop's scripts, outputs and notes. Several live entry points are here (see below). They are history as well as tools: the newest folders are the current work. |
| [`trol/`](trol/) | The earliest scripted bot. Kept for reference. |
| `HANDOFF.md`, `HANDOFF_ARCHIVE.md`, `GAUNTLET_LOG.md`, `log.txt` | Project state and journal, older history, one block per research loop, changelog. |

Not in the repo (git-ignored): `icebow/data/` (replays, datasets, checkpoints, detector weights),
`research/ext/` (the real-engine sandbox, RoyaleSim, and upstream memory-reader sources, each with its own
licence), and the emulator itself. You need these to reproduce results; the code alone will not run.

### Live path

| File | Role |
| :--- | :--- |
| `scratchpad/gauntlet/L68/live_reader/live_play.py` | The live bot on the MuMu emulator: reads the game state from memory (read-only, nothing is written to the game), asks `pipeline/live_gen.py`'s `GenPilot` for a decision, and sends two ordinary Android taps (hand slot, board cell). Confirms each play from the next frames. |
| `scratchpad/gauntlet/L68/live_reader/ladder_nav.py` | Between-match navigation for `--ladder`: Play Again, collect the day's chests after the 4th win, close promo popups, collect Trophy Road rewards, and stop on an "another device connected" dialog rather than kicking the account. Taps only from an allowlist; never the Shop tab. |
| `scratchpad/gauntlet/L68/live_reader/hero_button.py` | Hero ability button: sensed from pixels, decided by a hand-written rule outside the model (interim for the Ice Wizard hero). |
| `scratchpad/gauntlet/L68/live_reader/discord_clip.py` | Records a 60-second overlaid clip of one match per half hour and posts it to a webhook. |
| `scratchpad/gauntlet/L70/live/run_live.sh` | Supervisor: restarts the live run after a stop (up to 10 times) and ends when its STOP file exists. |

---

## Running the main pieces

Commands are from the scripts' own docstrings and HANDOFF; run from the repo root. Training and the
engine need a GPU build of PyTorch and the git-ignored data above. Create the deck venv first:

```powershell
cd icebow
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Each deck has its own venv; RoyaleSim runs from its own interpreter (`research/ext/Royale/.venv`).

**Live ladder play** (emulator running, game on the ladder screen; add `--dry-run` for a single match
without navigation):

```powershell
icebow\.venv\Scripts\python.exe scratchpad\gauntlet\L68\live_reader\live_play.py --ladder --matches 400 `
  --ckpt <checkpoint.pt> --tau 0.35 --max-seconds 600 --stop-file <path-to-STOP-file>
# watch the navigation without tapping:  ... live_play.py --ladder --nav-dry-run
```

**Re-drive pro replays in the real engine** (one replay, then the full public re-drive):

```powershell
research/ext/cr-native-sandbox/.venv/Scripts/python.exe research/sandbox_tools/replay_drive.py --tag <TAG> --port 37031 --runs 2
python research/sandbox_tools/run_public.py --ports 37031,37032 --python <venv python>   # job queue over engine slots
```

**Build the dataset, train the imitation model** (feature version 4, as for `gen_v3.1`):

```powershell
research\ext\Royale\.venv\Scripts\python.exe -m pipeline.dataset_gen --feature-version 4 `
  --corpus <re-driven corpus dirs...> --out icebow\data\pipeline\gen_dataset_v31_public.npz --grid lattice
icebow\.venv\Scripts\python.exe -m pipeline.train_gen --data icebow\data\pipeline\gen_dataset_v31_public.npz `
  --seed 0 --epochs 4 --grid lattice --feature-version 4 --amp bf16 --allow-causal-tti-unknowns --out-dir <dir>
```

`gen_v3.1b` adds `--rocket-context-weight 2.0 --rocket-context-artifact <artifact.json>`; `gen_v3.1a` is the
same run without them (`--inputs-only-arm`).

**Reinforcement learning (R-series), in RoyaleSim:**

```powershell
research\ext\Royale\.venv\Scripts\python.exe -m pipeline.rl_royale --config pipeline\rl_royale.yaml --run NAME
#   --smoke (tiny run + checks)   --resume   key=value to override any yaml key
```

**Acceptance screens** (ghost screen for any checkpoint, then paired scoring of two runs; reactive/search
arms with `search_s0`):

```powershell
research\ext\Royale\.venv\Scripts\python.exe scratchpad\gauntlet\L68\generalist\screen_gen\run_screen.py --ckpt <ckpt.pt> --out <run.jsonl>
research\ext\Royale\.venv\Scripts\python.exe scratchpad\gauntlet\L68\generalist\screen_gen\run_screen.py --pair A.jsonl B.jsonl
research\ext\Royale\.venv\Scripts\python.exe -m pipeline.search_s0 --out <dir> --seeds 0:8 --opps gen,s1 --arms plain --gen <ckpt.pt>
```

**Tests** (observation contract, dataset, model, live decision, extrapolation, public features):

```powershell
.\icebow\.venv\Scripts\python.exe -m unittest pipeline.tests.test_obs_contract
```

### The original pipeline (still runs)

Record yourself playing, label each play as `(screen -> card, cell)`, behaviour-clone a small CNN, then
fine-tune with RL. This is what [icebow/Instructions.txt](icebow/Instructions.txt) and
[icebow/README.md](icebow/README.md) document, and its `run.py` commands still work:

```powershell
cd icebow
python run.py record                              # 1. record yourself playing
python run.py hand-templates                      # 2. build card templates
python run.py verify --hand                       #    ...and check recognition
python run.py label --all                         # 3. turn recordings into data
python run.py outcomes --all
python run.py train-bc --init data/policy_sim.pt  # 4. imitate
python run.py play                                # 5. let it play
```

---

## Status and roadmap

**Done:** the real-engine re-drive of the full pro corpus with public observations; the generalist
imitation model family; RL from imitation with a measured gain over R0'; paired, clustered-bootstrap
acceptance instruments; unattended live ladder play with navigation, chest collection, restarts and clips.

**In progress:**
* R8 (projectile/effect look-ahead at inference) to fix late reactions to Goblin Barrel and other projectiles;
  then a paired simulator A/B.
* `gen_v3.1c`: `gen_v3.1b` with a stronger (4x) context weight, aimed at Rocket use and X-Bow placement.
* R1e: RL from `gen_v3.1b` against the evolution/hero deck census, with every hero and champion pressing its
  ability by a per-ability model calibrated to pro press rates and timing (being wired into RoyaleSim).
* Live currently runs `gen_v3.1b` so its behaviour can be watched; `rseries_r1_u0155` remains the best
  checkpoint measured in the simulator.
* Behaviour metrics for decisive moments (Rocket share and finish-offs, pre-emptive Log, X-Bow lane
  choice) are being used as acceptance criteria next to win value.

**Next candidates (not started):** choosing cards by sampling instead of argmax (the Rocket diagnosis
suggests argmax hides the model's Rocket timing), area-aware aiming for spells, and a pro-data model for the
Ice Wizard hero's ability; decision-time search stays parked.

**Negative results worth knowing:** a KL-free RL run degenerated; tower/crown reward shaping drifted the
gate away from the pros; wait-label and evolution-tag changes (`gen_v2`, `gen_v3`) and an undiscounted
return (`R1u`) gave no measurable gain. These are all in HANDOFF with their numbers.

---

## Sponsors

Want to sponsor my work? This is a hobby, open-source project built in the gaps around coursework. I pay
for replay crawling, engine time and the odd cloud run out of pocket, and any sponsorship buys me more of
the experiments that fill [HANDOFF.md](HANDOFF.md). Any contribution is appreciated!

**[github.com/sponsors/vegetableleaf](https://github.com/sponsors/vegetableleaf)**

| Tier | What you get |
| :--- | :----------- |
| **$5 / month** | A Sponsor badge on your profile |
| **$20 / month** | Your name or logo in this README |
| **$50 / month** | Access to non-secret data: training logs, evaluation numbers and gameplay videos |
| **$150 / month** | Access to pre-release builds, on top of all non-secret data |
| **$10 once** | A special mention on my next Instagram post |
| **$200 once** | You get added as a Contributor, with your own personal branch on this project |

No sponsors yet, the table above is waiting for the first name.
