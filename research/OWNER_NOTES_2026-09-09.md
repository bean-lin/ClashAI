# Owner notes 2026-09-09 — two directives on perception and training

**Recorded:** 2026-09-09, fork `bean-lin/ClashAI`. **Status:** owner directives, not yet implemented.
**Reviewed:** 2026-09-09 against HANDOFF.md through §5cs.99 and GAUNTLET_LOG.md through L67h (fork
`main` = upstream `f9a86e5`). **Note 3 added and Note 2 corrected:** 2026-09-10. "Owner" below is the
fork owner; the upstream owner is named as such wherever a ruling of theirs is cited. Nothing here changes the running pipeline by being written down. Each
note is given in the owner's words, then placed against what the repo measured, with the decision it
asks for. Tags follow the ledger: **(a)** measured in this repo, **(b)** untested or proposed,
**(c)** contradicted by a measurement.

## Note 1 — Perception: stop pixel processing, talk to the server

> Use of pixel processing to identify entities on the map, this is slow and takes a big chunk of
> resources. Solution: reverse engineer the game's API and directly react with the server.

**What the repo does today (a).** Live play reads the screen: the YOLO11s detector (230 classes,
imgsz 960, presence recall 0.855 / precision 0.886) plus template matching for the hand, an HSV read
of the elixir bar and a digit CNN for tower HP (README, "What the bot reads from the screen"). Two
live paths exist. The default `play.py` loop still feeds the old CNN directly; the contract path
(`clashrl/student_live.py` → `pipeline/obs_contract.from_live`) is wired but OFF unless
`play.student_ckpt` is set (§5cs.97). Training does not go through pixels: Square One S0 re-drives
pro replays through the real engine in an Android emulator and records exact state, so the detector
is on the live path only. (S2's plan to use the detector as a labeller for pro video was measured
and recommended dropped, §5cs.79 / §5cs.86.)

**The premise against the ledger.**
- *"Slow"* — **(c) on latency.** Detector 45–80 ms per decision, student 28.7–37.6 ms, against an
  `act_period` of 1.5 s (§5cs.97: "latency is not a constraint"); detector-only 29.5 ms median /
  35 ms p90 on an idle box (§5be.2), in a 10 Hz thread. When the old loop was served at 0.76 s the
  cost sat in the trainer residual (0.3 s), tower-HP OCR (p90 348 ms) and template matching
  (56–86 ms), not in the detector (§5bl).
- *"A big chunk of resources"* — **(b).** No GPU-share or power measurement of the live detector is
  in the ledger. Known: it shares an 8 GB VRAM card while playing; the detector upgrade
  (yolo26s / yolo26-p2) was measured slower and ruled NO-GO by the owner (§5be; §6 "do not
  re-propose").
- *What the screen path does cost* — **(a), and it is information, not time.** On real live frames
  the placement head collapses toward its prior (top-1 cell share 0.25 vs 0.07 on the engine at
  matched unit counts). Ablation names the cause: values the screen cannot supply — unit HP, exact
  and opponent elixir, king HP — while spell tokens, unknown team tags and low confidence each do
  nothing (§5cs.98 D). Supplying those values beats flagging them, measured against pro labels
  (exact cell 18.78 → 20.15, card 52.11 → 63.25, §5cs.98 E). A server feed would supply all of them
  exactly. That is the strongest argument for it, and it is not the one the note makes.

**What would change (b).** A custom client speaking Supercell's protocol replaces the detector and
the readers at live time. Perception cost goes to zero and the observation becomes exact.

**Costs to weigh before starting.**
- *Protocol churn* — **(b, external) for the protocol; (a) for the precedent.** The client–server
  transport is encrypted and version-gated, and every game release changes the client. The repo
  already carries one reverse-engineered artefact with this property: the engine sandbox's ~60
  hardcoded `libg.so` addresses are invalidated by every CR update, roughly monthly, and pin it to
  build 15.535.29 (`research/CR_NATIVE_SANDBOX_ASSESSMENT.md` §2). A live protocol client is
  re-derived on the same cadence, and unlike the sandbox it fails in front of the server, not offline.
- *Terms of Service tier* — **(b, external).** The README warns that screen automation already
  violates Supercell's ToS. The repo also already reverse-engineers the client — offline, never
  contacting Supercell's servers, and flagged as such when it was adopted
  (`CR_NATIVE_SANDBOX_ASSESSMENT.md` §2; bridge RE owner-authorised, §5cs.45). A protocol client is a
  third tier: a non-official client talking to Supercell's live servers on a real account. That is
  the behaviour server-side anti-cheat exists to detect, and modified clients and private servers
  are the category Supercell has pursued legally.
- *The stated premise* — **(a).** README: "The bot never sees the game's internal state. It gets
  what a person gets." Dropping it is a product decision, not a perf fix, and it changes what S4's
  live grading measures.

**Decision asked.** Owner to rule whether the human-view premise stays.
- If it stays: the measured live defect is missing values, not speed, so the work is estimators and
  fills on the live path (§5cs.98 E is the first, already wired) and, if resources matter, a
  GPU-share measurement before any detector change (the model-size route is already ruled out).
- If it goes: a research brief first (protocol survey, account risk, patch cadence) before any
  client code, per the rule that nothing is implemented by being written down.

## Note 2 — Training: play first, store samples, abstract, tokenise, track progress

> Use of neural AI learning with real players is a waste of compute. AI will never learn to win
> because you skipped 100 steps ahead and expect results. You have to play yourself first and
> store it as samples, abstract the data then tokenise it in vectors so it may be coherent for your
> AI model to learn efficiently and so that you follow the progress along the way.

**Where this stands against the ledger (a).** The first pipeline (pixel CNN + RL from win/loss)
was measured over ~60 experiment loops and never beat its imitation init (README); RL on the real
engine then failed twice more, ~1,500 matches across four arms (HANDOFF §4, §5cs.44–51). The
rebuild approved 2026-09-06 already has the shape of this note, and most of it has now run:

| Owner's step | Square One stage | State on 2026-09-09 |
| :--- | :--- | :--- |
| Play first, store samples | S0: pro replays re-driven in the real engine; state recorded at every play and every 20 ticks (1 s), compact frames without spell/effect tokens (§6 parked item); corpus_v6 = 2,241 icebow replays (§5cs.96), hogeq v5 = 765 (§5cs.78) | done |
| Abstract the data | S0: one `BoardState` contract for engine and detector, `pipeline/obs_contract.py` (§5cs.56) | done |
| Tokenise into vectors | S1: entity tokens + spatial patch tokens with coordinates, full-resolution per-cell head (`pipeline/model_v3.py`) | done — 3-seed bands closed on both decks (§5cs.64/65): icebow tile top-1 18.22 ± 0.11 on the S1 instrument, level with the old init on a matched grid; engine 75/25 vs a no-plays control on 100 entries. The n = 500 winrate-vs-old-init half of the gate is not in the ledger (b) |
| Follow progress along the way | Pre-registered gate per stage; a failed gate stops the next stage (README) | in place — S2 measured +1.50 ± 0.13 pp exact cell per corpus doubling (§5cs.78) and a pro-vs-pro agreement ceiling of 27.5% with the student at 21.04 = 76% of it (L67h); S3's engine search teacher failed its gate five ways and is closed (§5cs.94) |
| Learn against real players | S4, last | opened 2026-09-07 for measurement only (§5cs.95): live-shift cost measured, student wired to the live path behind `play.student_ckpt` (§5cs.97), live placement collapse diagnosed (§5cs.98–99). No learning from live matches has run |

**The one difference.** The samples are professional replays, not the owner's own games. The
original pipeline did start with the operator's own games (record → label → BC; README, "The original
pipeline"). What exists of them upstream is 4 sessions / 276 plays (§5cs.58), against 66,579 pro
play rows in corpus_v5 icebow alone (§5cs.77) **(a)**. The *upstream* owner ruled on 2026-09-08
(L67f / §5cs.98 G) that their own clicks are not a quality standard and are never used as placement
labels. That is a ruling about the upstream owner's play; it does not bind this fork. Note 3 changes
the calculus: on a stock account there is no pro corpus for the deck, so own play is the only sample
source until one of Note 3's routes exists. Own matches enter the same way live matches do in S4:
recorded with the replay tag, re-driven in the engine, then labelled (§5cs.56 prerequisite) — or,
while the engine is blocked, labelled from the screen as the original pipeline did (`run.py label`).

**Decision asked.** Confirm (1) the sample source per Note 3 (pro corpus where one exists for the
deck, own play otherwise), and (2) S4 stays last and stays measurement-only until the live placement
defect (§5cs.98) is closed. No code change follows from this note unless either ruling changes.

## Note 3 — Account: a stock account instead of the icebow deck

> instead of ice bow, we will be using a stock account

**Recorded:** 2026-09-10. A fresh (stock) throwaway account: starter cards at starter levels, from
Training Camp and Arena 1 onward. The first-battle deck is Arrows, Knight, Archers, Minions, Giant and
Fireball, with Goblins and Musketeer filling the eight **(b: confirm the last two in-game)**.

**What is deck-agnostic (a).** The pipeline is deck-parameterised by ruling (§6 ruling 1, 2026-09-06):
a deck is one yaml in `pipeline/decks/` (8 card classes, config, crawl and data dirs). The contract
encodes the hand as 8 deck slots plus a "not in my deck" bit and the model's card head is 8 slots
(`obs_contract._slot_onehot`, `model_v3.N_SLOTS`), so any eight cards fit. All eight stock cards are
detector classes (`vocab.DETECTOR_CLASSES`), so `from_live` needs no new class. hogeq is the folder
recipe: clone the deck folder without `data/ runs/ .venv`, set the `config.yaml` deck and `cards.yaml`
levels, rebuild hand templates (`run.py hand-templates`), keep the BoardWarp calibration.

**What breaks.**
- *The pro corpus* — **(a) for the filters, (b) for the count.** Every corpus filter is exact-deck
  (`hf_to_crawl.py`'s card set; the crawler's deck match). Pros do not play the starter deck, so the
  exact-deck corpus for it is close to empty; the HF count is unmeasured and the filter can be run
  over the 52 parts to measure it. Three routes, none free: (i) own play as the sample source
  (Note 2), small by the ledger's standards (276 plays vs 66,579 rows); (ii) a universal card encoder
  so all 252k public replays train one model regardless of deck — the FirstLight mechanism, ranked
  (B) in §5cs.95 C, a new model family; (iii) a ladder deck the account can build early, crawled as
  icebow was — keeps the pipeline as-is, changes the deck.
- *Live grading* — **(a).** The protocol is a 10,000-trophy ladder band (§6 ruling 2) on the upstream
  owner's account. A stock account plays Training Camp against bots, then low arenas against
  low-level players. The band has to be re-ruled for this account, and "learn against real players"
  (Note 2) is partly "against bots" at first.
- *Card levels* — **(b).** The engine re-drives replays at catalog levels and pro replays are level
  15–16; a stock account's cards start at level 1. HP and damage scale per level, so engine states
  and live states disagree on unit strength until the sandbox is set to the account's levels.
  Whether the sandbox exposes per-card levels is unchecked.
- *ToS* — a throwaway account is what the README asks for; this note removes the risk to any main
  account.

**Decision asked.** (1) Which corpus route: own play only, the universal encoder, or a buildable
ladder deck. (2) The live grading band for the stock account. (3) The eight cards, confirmed in-game,
so the deck yaml can be written. No deck folder or yaml is created until (3).
