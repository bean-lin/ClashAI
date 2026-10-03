# Gates: live reader phase 1

OWNS: scratchpad/gauntlet/L70/reader/* (new files only; re_peek and re_peek.c excluded)

Scope: read-only host probing, labelled evidence, optional C extension and Python decoder.

- [x] G1: Sandbox container and layout findings are documented with build-specific caveats.
  EVIDENCE: Manual source review of jni_bridge.cpp enumeration and export; REPORT.md item 1 records container, vtables, layouts, buffs and disproven elapsed-time interpretation.
- [x] G2: Batched live snapshots contain registry objects and bounded battle/player-state container candidates at no more than 2 Hz.
  CHECK: python -B scratchpad/gauntlet/L70/reader/audit_evidence.py
  EXPECT: EVIDENCE_AUDIT_PASSED
  EVIDENCE: Direct Python check in C:/Users/benpe/ClashBot; exit 0; expectation matched; output SHA256 31228bc8c6e69b288cbe9b1f158fd85403fcabf41dabb20a81f3bb8558583bad; full command/output in validation.json.

- [x] G3: Rocket, Log and Tornado observations correlate with confirmed bot casts and native coordinates.
  CHECK: python -B scratchpad/gauntlet/L70/reader/test_reference.py
  EXPECT: Ran 7 tests
  EVIDENCE: Direct Python check in C:/Users/benpe/ClashBot; exit 0; expectation matched; output SHA256 d79285e542166f20a7817056ac884c8625dab5e3eda34d956b0eeac73ba77c19; full command/output in validation.json.

- [x] G4: Evolution marker separates at least five independently labelled base and evolved bodies per requested card.
  CHECK: python -B scratchpad/gauntlet/L70/reader/audit_evidence.py
  EXPECT: EVIDENCE_AUDIT_PASSED
  EVIDENCE: Direct Python check in C:/Users/benpe/ClashBot; exit 0; expectation matched; output SHA256 31228bc8c6e69b288cbe9b1f158fd85403fcabf41dabb20a81f3bb8558583bad; full command/output in validation.json.

- [x] G5: Optional C extension preserves default source behavior and Python reference decodes recorded bytes with explicit uncertainty.
  CHECK: python -B scratchpad/gauntlet/L70/reader/test_reference.py
  EXPECT: Ran 7 tests
  EVIDENCE: Direct Python check in C:/Users/benpe/ClashBot; exit 0; expectation matched; output SHA256 d79285e542166f20a7817056ac884c8625dab5e3eda34d956b0eeac73ba77c19; full command/output in validation.json.

- [x] G6: Lead compilation and runtime comparison checklist is delivered; build and runtime diff remain unperformed here by instruction.
  EVIDENCE: live_sampler2.c header contains exact gcc -O2 -static -o live_sampler2 live_sampler2.c command and explicit default/new-field verification checklist; compare_default.py delivered. No compilation or runtime equality claim.
- [x] G7: Findings distinguish verified fields, candidates, missing evidence and collection limitations.
  EVIDENCE: FINDINGS.md and REPORT.md record raw-pointer uncertainty, 2826 missing object observations, bounded census, existing-video limitations and unperformed C validation.
