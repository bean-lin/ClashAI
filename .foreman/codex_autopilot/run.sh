#!/bin/bash
# Re-invoked by Windows Task Scheduler (task ClashBot_CodexAutopilot, every 3 h until 2026-10-06). One run at a time.
cd /c/Users/benpe/ClashBot
D=.foreman/codex_autopilot
[ "$(date +%Y%m%d)" -gt 20261006 ] && exit 0
if [ -f $D/LOCK ] && [ $(( $(date +%s) - $(stat -c %Y $D/LOCK) )) -lt 12600 ]; then exit 0; fi
date > $D/LOCK
CODEX=/c/Users/benpe/AppData/Local/Programs/OpenAI/Codex/bin/codex
"$CODEX" exec -m gpt-6-astra -c model_reasoning_effort=high --sandbox workspace-write \
  -c sandbox_workspace_write.network_access=true -C /c/Users/benpe/ClashBot - < $D/TICKET.md \
  > $D/runs/run_$(date +%Y%m%d_%H%M).log 2>&1
rm -f $D/LOCK
