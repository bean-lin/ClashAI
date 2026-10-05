# Catalog correction gates

- [x] C1: Exact isolated metadata diff, unchanged native code/assets and synthetic form controls pass.
  Evidence: native_catalog_corrected.json, l72-native-catalog-prepared/controls and l72-native-elite-form-probe-v5 receipts, exit 0. Preserve failed v4 schema assertion.
- [x] C2: Outcome-blind newly compatible Icebow selection and original command/form conversion verified.
  Evidence: native_compatibility_corrected.json and reserved_icebow_corrected_prepared.json; 162 groups, 12,957 source commands, 17 scheduled repeats. l72-native-corrected-compatibility and l72-corrected-icebow-prepared exit 0.
- [ ] C3: New native collection and independent usable-yield/repeat reconciliation complete.
  Evidence pending: corrected_icebow_launch.json and corrected_icebow_verifier_launch.json. First four fixed records independently pass; qualification/recount controls pass. Do not duplicate jobs or edit bound sources.

Evidence must record actual commands, exit codes, hashes and limitations. Original
v1/v2 failed probes and old catalog/pilot results remain immutable.
