# Owner notes 2026-09-09 — two directives on perception and training

**Recorded:** 2026-09-09, fork `bean-lin/ClashAI`. **Status:** owner directives, not yet implemented.
Nothing here changes the running pipeline by being written down. Each note is given in the owner's
words, then placed against what the repo measured, with the decision it asks for.

## Note 1 — Perception: stop pixel processing, talk to the server

> Use of pixel processing to identify entities on the map, this is slow and takes a big chunk of
> resources. Solution: reverse engineer the game's API and directly react with the server.

**What the repo does today.** Live play reads the screen through the YOLO detector plus the hand,
elixir and tower readers (`icebow/`, `hogeq/`), all funnelled through `pipeline/obs_contract.py`.
Training does NOT go through pixels: Square One stage 0 re-drives pro replays through the real
engine in an Android emulator and records exact state, so the detector is on the live path only.

**What would change.** A custom client speaking the Supercell protocol replaces the detector at
live time. Perception cost goes to zero and the observation becomes exact.

**Costs to weigh before starting.**
- The client-server traffic is encrypted and the protocol changes with every game release; the
  client has to be re-derived per patch.
- A custom client is a different tier of Terms of Service violation from screen automation
  (README warning). It is the behaviour Supercell bans hardest and pursues against projects.
- The current design's stated premise is that the bot sees only what a person sees. Dropping it
  is a product decision, not a perf fix.

**Decision asked.** Owner to rule whether the human-view premise stays. If it stays, the perf work
is inside the detector path (resolution, frame budget, model size), not a protocol client.

## Note 2 — Training: play first, store samples, abstract, tokenise, track progress

> Use of neural AI learning with real players is a waste of compute. AI will never learn to win
> because you skipped 100 steps ahead and expect results. You have to play yourself first and
> store it as samples, abstract the data then tokenise it in vectors so it may be coherent for your
> AI model to learn efficiently and so that you follow the progress along the way.

**Where this stands against the ledger.** The first pipeline (pixel CNN + RL from win/loss) was
measured over ~60 experiment loops and never beat its imitation init; RL on the real engine failed
twice more (HANDOFF §4, §5cs.44-51). The rebuild already follows the shape of this note:

| Owner's step | Square One stage | State |
| :--- | :--- | :--- |
| Play first, store samples | S0: ~1,850 pro replays re-driven in the engine, every frame recorded | done |
| Abstract the data | S0: one `BoardState` contract shared by engine and detector | done |
| Tokenise into vectors | S1: entity tokens + spatial patch tokens with coordinates, per-cell head | in progress |
| Follow progress along the way | Pre-registered gate per stage; a failed gate stops the next stage | in place |
| Learn against real players | S4 only, after imitation and engine search | not started |

**The one difference.** The samples are professional replays, not the owner's own games. That is the
better teacher unless the owner is above the pro corpus's trophy band. If the owner wants their own
matches in the corpus, they enter the same way live matches do in S4: recorded, re-driven in the
engine, then labelled.

**Decision asked.** Confirm the pro corpus stays the primary sample source and S4 stays last. No
code change follows from this note unless that ruling changes.
