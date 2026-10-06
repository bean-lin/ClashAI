# Discord reporting

Owner instruction, October 5, 2026: use plain wording, cover the relevant work,
explain findings and their interpretation, state verdicts and next steps, and
make sections easy to distinguish. The owner's supplied newsletter brief is a
style reference, not a script to copy or authority to change server settings.

## Writing each update

Write for a reader who has not followed this repository. Use a short dated title,
bold section labels, blank lines, and brief paragraphs or bullets. Explain model
nicknames on first use. Avoid packed slash-separated counts, unexplained gate
codes, receipt dumps, and technical shorthand. Keep detailed provenance locally.

Adapt these sections to the actual news; do not fill an empty template:

- **Work completed:** what changed or was tested, and why. Include relevant data,
  simulator, live-play, diagnosis, tooling, and evaluation work, not only training.
- **What we found:** a few useful numbers with denominators and named comparisons.
  For model results include R1e and the immediate control under comparable inputs
  and runtime. Distinguish training, recorded-action agreement, simulator games,
  and live games. Give uncertainty when measured; do not invent it.
- **What it means:** explain what the result supports, what remains uncertain,
  and whether a proposed cause is measured or still a hypothesis. Separate PLAY
  from WAIT gains when aggregate agreement could mislead. Coordinate agreement,
  physical damage, and winning games are different measurements.
- **Decision:** accepted, rejected, still running, or blocked, with the reason.
  State deployment status explicitly. An engineering check passing is not a
  stronger-model claim. Preserve all existing acceptance criteria and failures.
- **Next:** the next concrete test or action and the question it should answer.
  Identify a proposal as untested and an active job as active.

Be concise without dropping material failures or contradictory findings. Group
related experiments instead of listing every receipt. A short update may merge
sections. Longer posts may use numbered parts, split at paragraph boundaries.
Do not copy the supplied document or retrofit/resend already delivered reports.

## Daily edition

Send one newsletter every day at **9:30 PM America/New_York** (Eastern local
time, including daylight saving changes), through the existing owner's webhook.
This is directly authorized: no recurring draft-approval request is required.
The daily reporting schedule continues after the temporary improvement-worker
cutoff and Claude's return; it does not authorize more training or live play.

Use the latest HANDOFF, dated reviews, verified results, delivery receipts, and
relevant changes since the prior edition's cutoff. The first edition covers the
preceding 24 hours. Include unfinished work and the current live/deployment
status. Include ladder results/trophy changes or one or two clip links only when
verified records actually provide them. Never invent activity or imply missing
data is zero. On a quiet day, send a brief truthful status instead of recycled
news. Previously reported model results can be summarized as part of the day's
roundup, but must not be sent again as new individual model reports.

Save the actual newsletter as `reports/discord/newsletters/YYYY-MM-DD.md`, using
the Eastern date, plus a same-stem `.sources.json` containing the reporting
window, source paths/hashes, and claim-to-source notes. This evidence stays local;
the audience receives readable findings rather than internal paths and hashes.

## Sending and delivery records

For new reports use the companion sender below. It reads the **same existing
webhook configuration** as `scratchpad/gauntlet/L69/discord/post.py`; the old sender
and its historical hashes remain unchanged. Do not create a new webhook, alter
channels, inspect/display its secret, or post through another route.

```powershell
research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L69/discord/send_report.py --id newsletter-YYYY-MM-DD --file reports/discord/newsletters/YYYY-MM-DD.md
```

For new individual reports use a stable unique ID such as `model-MODEL-final`.
Check existing historical receipts too: a new sender ID does not authorize a
duplicate of an old delivered report. Existing frozen jobs with their bound
sender must not be edited while active; apply the writing guide to their report
drafts and preserve their established receipts.

The companion saves exact text, hashes, per-part HTTP status and Discord message
IDs under `reports/discord/deliveries/ID/`. A completed ID is skipped. An incomplete
or ambiguous attempt stops for delivery reconciliation; never delete its record
or blindly resend. Successful earlier parts must not be duplicated. A draft alone
does not mean delivered. Keep records across Claude/Codex handoffs.

Before posting, check the draft against its sources and remove credentials,
webhook URLs, private setup details, other players' identifying names/tags, and
ping syntax. The sender also disables mentions. Do not infer server/channel
configuration from the supplied brief; use the existing destination unchanged.

## Scheduler ownership

The Codex thread heartbeat named **ClashAI daily newsletter** owns the daily send.
Its automation ID is recorded at the top of HANDOFF. Claude should follow this
writing guide for all new reports, and must not install a second daily scheduler
or manually duplicate a completed edition. If scheduler ownership is transferred,
disable the old schedule first and retain the same dated delivery records.
Local scheduled execution requires the machine and Codex app to be running.
