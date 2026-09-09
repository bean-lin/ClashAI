# Owner notes 2026-09-09 — two directives on perception and training

**Recorded:** 2026-09-09, fork `bean-lin/ClashAI`. **Status:** owner directives, not yet implemented.
**Reviewed:** 2026-09-09 against HANDOFF.md through §5cs.99 and GAUNTLET_LOG.md through L67h (fork
`main` = upstream `f9a86e5`). Nothing here changes the running pipeline by being written down. Each
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
original pipeline did start with the owner's own games (record → label → BC; README, "The original
pipeline"). What exists of them on disk is 4 sessions / 276 plays (§5cs.58), against 66,579 pro
play rows in corpus_v5 icebow alone (§5cs.77) **(a)**. The owner has since ruled (2026-09-08,
L67f / §5cs.98 G) that their own clicks are not a quality standard and are never used as placement
labels; their sessions serve only as real detector input for label-free instruments. If that ruling
stands, this difference is already settled. If the owner wants their matches in the corpus anyway,
they enter the same way live matches do in S4: recorded with the replay tag, re-driven in the
engine, then labelled (§5cs.56 prerequisite).

**Decision asked.** Confirm (1) the pro corpus stays the primary sample source, i.e. the 2026-09-08
ruling on the owner's own clicks stands, and (2) S4 stays last and stays measurement-only until the
live placement defect (§5cs.98) is closed. No code change follows from this note unless either
ruling changes.
