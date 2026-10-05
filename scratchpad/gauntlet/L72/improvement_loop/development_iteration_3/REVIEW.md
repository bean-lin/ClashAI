# Registered Rocket aim-loss experiment

The20% defensive-sequence curriculum failed its fixed development criteria:
defense action -0.33pp, fewer correct Rocket actions within sequences and small
Witch/Furnace regressions. Preserve that outcome. Iteration1 isolated generic
projectile targeting passes its development continuation criteria but Rocket
aim remains weak. PLAN/METRICS register a separate one-factor cell-loss emphasis
on all original expert Rocket PLAY labels, including troop targets.

No exposure change, inferred tower/low-HP target, second model forward pass,
card/gate/WAIT/value weighting, tactical rule or Rocket-frequency reward. Weight1
must reproduce original loss/gradients; weight3 adds twice the Rocket cell CE
sum divided by the unchanged total PLAY count. The same v6 architecture, R1e
initialization, ordinary draws/mirroring and fixed1000-step recipe are retained.

Preflight completed October5 14:05 in129.91s, exit0/token matched. Weight1 reproduces
original loss and every parameter gradient exactly with the same dropout RNG.
All base/non-cell terms remain unchanged; added cell gradient is zero outside
original expert PLAY Rocket rows and positive within them. Removing Rocket cards
or their PLAY gates removes the added term. Independent original/defense masks
match; standard weights-only in-memory roundtrip preserves tensors. CPU smoke
loss5.9850544929504395 (two expert Rockets) is not full training and saves no
checkpoint; no development predictions occurred during preflight.

A2/A3 ACTIVE: launch.json/chain_started.json record the serial full1000-update
candidate/evaluation/independent recount chain. One held GPU lock spans gaps.
No other control training/inference is duplicated. Read receipts and exact
results before the new-model Discord report; none is due at launch. No live
change or deployment acceptance. Preserve all frozen sources and failures.
