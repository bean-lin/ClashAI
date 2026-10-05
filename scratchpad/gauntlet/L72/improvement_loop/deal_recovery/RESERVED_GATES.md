# Gates: reserved native deal recovery

OWNS: scratchpad/gauntlet/L72/improvement_loop/deal_recovery/reserved_*.json, scratchpad/gauntlet/L72/improvement_loop/deal_recovery/run_reserved.py, scratchpad/gauntlet/L72/improvement_loop/deal_recovery/verify_reserved.py, scratchpad/gauntlet/L72/improvement_loop/deal_recovery/RESERVED_*.md

Scope: Reconstruct the complete fixed 65 reserved fallback cases with unchanged source commands and criteria, preserving all failed attempts.

- [x] R1: Frozen jobs include every non-training fallback exactly once with unchanged original identity and input hashes.
  CHECK: icebow/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/deal_recovery/verify_reserved.py --jobs-only
  EXPECT: RESERVED_DEAL_JOBS_VERIFIED
  EVIDENCE: l72-deal-recovery-reserved-jobs.json/out; exit0 and token; all65 cases (12development/53confirmation), original splits/forms/commands/seed/level; training proof and plan hashes bound.

- [ ] R2: All selected captures and repeats finish with source/runtime provenance and explicit success or exclusion.
  CHECK: icebow/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/deal_recovery/verify_reserved.py
  EXPECT: RESERVED_DEAL_RECOVERY_INDEPENDENT_PASS
  EVIDENCE: pending

- [ ] R3: Report distinguishes new verified reconstruction yield from model acceptance and preserves N2 gaps.
  EVIDENCE: pending
