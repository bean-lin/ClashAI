# Pinned upstream port, October 5

The owner requested the new RoyaleSim/RoyaleGym changes and their use for all future RL training. We fetched the official repositories and recorded every intervening commit and changed file in inventory.json. The previous checkouts have no tracked local edits. The port takes the entire compatible source pair, rather than guessing which individual commits to cherry-pick:

- RoyaleSim:369fe33dc729b4a38dce831714724135fa7216ca ->015f9b0084afe574915e3f6ce2f0764c6dec6099 (0.1.13;232 commits).
- RoyaleGym:236cfecc6d93c19c53b93e9177b3ef9753d53b43 ->3117816366b00754da1b56c9543412e4706de62a (0.1.15;180 commits).

Sources are local detached Git worktrees at research/ext/Royale-20261005/{RoyaleSim,RoyaleGym}. Build/data/test receipts live with this report. The previous compiled engine reports369fe33,clean and card FNV1b8121b10c3222cd. Its checkout, installed modules and data stay intact for the two already-started frozen experiment chains. New wheels install into the separate versioned runtime directory. No Torch, learner package or unrelated dependency upgrade is part of this change.

## Relevant upstream changes

The core changed across targeting, combat, movement, arena, entity, spell, state and Python bindings. Shipped fixes include homing-only accounting for victims already doomed by shots in flight; cancellation of ranged launches when a target has moved far beyond reach; Hunter pellet collision with a building's square and battle-stream random delay; full sight including the attacker's radius; champion/hero ability timing including Golden Knight's single press per deployment; spawning, death effects, placement/formation ties and evolved-unit mechanics. Upstream also added per-client calibration alternatives. We preserve the shipped defaults: optional replay hypotheses are not all enabled merely because the code exists.

Bindings now retain the originating card through spawn chains, expose 27-field entity rows (charge, tunnel destination and ability duration appended), additional status bits, champion/evolution-cycle catalogue fields, deck/forms/levels and delayed-command outcomes. Older Gym cannot read the extended rows, so Sim and Gym must move together. Originating-card identity is still not body identity; the separate Witch/Night Witch/Furnace resolver remains necessary and must be checked against this engine.

Hand refill can temporarily leave EMPTY_CARD slots. Overtime ends through tower drain after normal play stops, rather than an immediate lowest-HP verdict. Adapter checks must cover empty slots and terminal outcomes, not just import success. The120s overtime and measured elixir schedule are preserved. Public-input boundaries and model feature versions do not automatically expand when upstream exposes more fields.

Gym adds exact engine-plus-observation-memory snapshots and weighted snapshot banks, richer opt-in public observations, per-card levels and better execution/provenance reporting. Its embedded card-table stamp fixes missing provenance in installed wheels. These APIs are available after the port; adopting new learning inputs or a snapshot curriculum would be a separate measured experiment.

## Runtime and evidence boundaries

The simulator wheel is built with --no-default-features, embedding its card table instead of looking up mutable build-machine data. Arena, globals, 15.535 cards and calibration are staged into the wheel. The exact source, wheel and installed-file hashes are recorded. New main RL runs and spawned actors must activate and verify this runtime, and checkpoints must retain its fingerprint; exact resumes across a different/unrecorded engine must be refused (old weights can initialize a newly named run).

The already queued eight IL arms optimize recorded expert data; their34-job chain also contains frozen old-engine comparisons. Those results must keep that engine label. They neither authorize new PPO training nor demonstrate updated-engine gameplay acceptance. Deployment claims need same-code, same-engine comparisons, and any selected candidate must receive updated-engine verification before a simulator-backed deployment claim is made. Never merge scores across engine versions.

Full upstream test results, project adapter checks and adoption status remain OPEN until their actual receipts are recorded.

Independent data check: data_verified.json confirms the previous four runtime data files still match their captured hashes. The card table has exactly eight added movement/obstacle flags; no prior card leaf value changed. Arena/globals have no changes. Overtime120s and all three elixir regeneration rates are identical. Calibration has new hypothesis keys and documentation, plus existing default changes for Golden Knight recharge and overtime tower drain. check_data.py walks list elements as well as object keys so a full card-list replacement cannot hide numeric changes.
