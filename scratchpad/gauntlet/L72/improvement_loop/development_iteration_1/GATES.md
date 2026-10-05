# Isolated development iteration gates

OWNS: scratchpad/gauntlet/L72/improvement_loop/development_iteration_1/

- [x] D1: Deterministic replay-separated training/development indices are bound to original expert labels and exclude old validation and reserved confirmation.
  CHECK: icebow/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_1/prepare.py
  EXPECT: DEVELOPMENT_1_DATA_PREPARED
- [x] D2: Independent source-index/count/hash recount rejects leakage and verifies the saved split.
  CHECK: icebow/.venv/Scripts/python.exe scratchpad/gauntlet/L72/improvement_loop/development_iteration_1/verify.py
  EXPECT: DEVELOPMENT_1_SPLIT_VERIFIED
- [ ] D3: The isolated trainer and pre-run metric manifest satisfy the fixed recipe and never evaluate old validation or confirmation.
  MANUAL: Implement and verify data-access boundaries, zero-residual migration, identical sampling, original losses and a checkpoint-free smoke before full optimization.
- [ ] D4: Both full serial arms finish the registered finite updates and all paired development results are independently recounted and reported.
  MANUAL: Preserve failures and full receipts; send model reports once; no acceptance/deployment from development-only evidence.

D1/D2 successful receipts: l72-development1-data-prepared and
l72-development1-data-independent. One positive/eight corruptions pass.
213995 training rows/1573 replays,54723 development rows/405 replays;38317 old
validation pool rows excluded, zero overlap with239939 reserved groups.
No optimization or trainer activation; D3/D4 remain open.
