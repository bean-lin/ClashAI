#!/bin/bash
# Disk cleanup, 2026-09-29. Claude's deletion was blocked by the permission classifier, so the OWNER runs this.
# Run from Git Bash:  bash scratchpad/cleanup_20260929.sh
# Every path below is literal and was checked (untracked by git, not read by current code, results recorded in
# HANDOFF). It never touches league1b, league1_u0200 or anything tonight's runs read, so it is safe to run now.
set -u
cd /c/Users/benpe/ClashBot || exit 1

echo "== TIER 1: stale RL outputs (~0.95 GB)"
# smoke / verify runs of the RL code (test output), and the three pre-league RL runs (superseded; results in HANDOFF)
rm -rf icebow/data/bench/rl_royale/T11smoke_gen icebow/data/bench/rl_royale/T11smoke_s1 \
       icebow/data/bench/rl_royale/T11verify_gen icebow/data/bench/rl_royale/T12bsmoke \
       icebow/data/bench/rl_royale/T12bsmoke_a2 icebow/data/bench/rl_royale/T12bsmoke_gen \
       icebow/data/bench/rl_royale/T12bsmoke_s1 icebow/data/bench/rl_royale/T12bverify \
       icebow/data/bench/rl_royale/smoke_20260924 icebow/data/bench/rl_royale/rl30_20260924 \
       icebow/data/bench/rl_royale/rl30b_20260924 icebow/data/bench/rl_royale/rl30c_lr3e5_20260924

echo "== TIER 1: league1 intermediate checkpoints (~1.0 GB; keeps u0000 u0200 u0250 u0270 u0310 u0350, latest, snaps)"
for f in icebow/data/bench/rl_royale/league1/league1_u0*.pt; do
  case "$(basename "$f")" in
    league1_u0000.pt|league1_u0200.pt|league1_u0250.pt|league1_u0270.pt|league1_u0310.pt|league1_u0350.pt) ;;
    *) rm -f -- "$f" ;;
  esac
done

echo "== TIER 1: caches (regenerate automatically)"
find pipeline icebow/src icebow/tools icebow/tests hogeq/src -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
rm -rf .pytest_cache

echo "== TIER 1: duplicate crawl corpora (~1.85 GB)"
# every replay in these is also in corpus_v6 with identical byte size (0 mismatches over 5,814 files, 2026-09-29);
# their only extra files (per-crawl aggregate.json / summary.jsonl) are preserved in ext/_crawl_summaries/
rm -rf scratchpad/gauntlet/ext/corpus_v4 scratchpad/gauntlet/ext/corpus_v5 \
       scratchpad/gauntlet/ext/corpus_v5_new scratchpad/gauntlet/ext/corpus_v6_new

echo "done"
