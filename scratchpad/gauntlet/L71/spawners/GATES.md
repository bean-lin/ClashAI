# Spawner correction acceptance

- [x] S1: Exact catalog body identity covers Witch, Furnace, Night Witch and the audited huts/Tombstone, including ordinary child forms and conservative unknowns.
  CHECK: icebow/.venv/Scripts/python.exe -m pytest scratchpad/gauntlet/L71/spawners/test_body_identity.py -q
  EXPECT: passed
  Evidence: prototype_checks.json records the exact command, cwd, exit, matched output and SHA-256; 13 tests plus the three-card repeated-wave SIM probe pass. This is prototype evidence, not live deployment.
- [ ] S2: Every changed training token is backed by a reproduced original public row; expert labels and replay splits remain unchanged.
  MANUAL: Inspect reconstruction receipt and independently compare original/corrected arrays and hashes.
- [ ] S3: Opt-in contract is shared by dataset, SIM and live, with legacy parity and actual checkpoint loading verified.
  MANUAL: Inspect integration tests after the active Q3 snapshot finishes.
- [ ] S4: Trained correction passes held-out and same-code gameplay acceptance and is verified in the authorized live deployment.
  MANUAL: Inspect training/control, full evaluation receipts and deployed startup/confirmed-play logs.
