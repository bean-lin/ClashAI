# Development split ready, training not launched

The preregistered whole-replay hash assignment yields213995 training rows from
1573 replay groups and54723 development rows from405 groups. All268718 original
ordinary expert rows are accounted for. Training has67106 PLAY/146889 WAIT;
development has17192 PLAY/37531 WAIT. No reweighting or labels changed.

All38317 old validation pool rows are excluded. Membership is disjoint from all
239939 reserved raw replay groups. Both observer sides stay together; the parent
R1e model's earlier exposure to these historical examples remains disclosed.
The independent verifier reconstructs indices/counts from the original sources
without importing the producer, trainer or model. One positive and eight leakage/
missing/duplicate/order corruption controls pass. Data, context, corrected-label
binding, initial checkpoint, recipe and reservation hashes are frozen.

D1/D2 complete; D3/D4 open. Next implement the isolated ordinary_v5 versus
ordinary_v6 driver, freeze subgroup metric definitions, verify zero-residual
migration and identical batch/mirror draws, and run a checkpoint-free smoke.
The old trainer cannot be reused unchanged because it predicts on historical
validation. Then perform the registered serial1000-update arms, independently
recount development results, and send the owner's model reports with the verdict
NOT ACCEPTED pending final evidence. This split does not authorize deployment.

No optimizer updates, candidate checkpoints, policy predictions, GPU job launch
or Discord report occurred during preparation. The live owner farming run was
left operating with its selected checkpoint.
