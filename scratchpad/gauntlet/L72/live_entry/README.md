# Manual recording entry

From PowerShell in `C:\Users\benpe\ClashBot`:

```powershell
.\icebow\.venv\Scripts\python.exe .\scratchpad\gauntlet\L68\live_reader\live_play.py
```

Keep MuMu and Clash Royale open, run the command, then enter a match manually. The default handles one match, records it and saves raw and overlaid videos under `icebow/data/overlayed_replays`. It does not navigate into another match or publish anything. CPU inference uses four threads so the serialized GPU training chain can continue. `--overlay reader` selects only reader markers; default `both` includes cosmetic detector boxes.

The script loads the checkpoint named by `scratchpad/gauntlet/L70/live/CKPT_OVERRIDE`, prints its full path/source/SHA256, and never selects by modification time. Currently that pointer is R1e31 u0155, the last owner-selected live model. None of the new L71 candidates qualifies yet. The pointer should move only when a successor passes the declared acceptance checks; this manual filming path is not an autonomous R1e fallback deployment.

An explicit `--ckpt "C:\path\to\checkpoint.pt"` wins over the pointer. Missing or malformed selections fail clearly. A changed default selection ends a multi-match run between matches; an explicit selection stays fixed. `--check` loads and reports the chosen model offline without connecting to the emulator.

The current public-input pilot supports checkpoint feature versions4–6, audited PLAY and WAIT, and the public opponent-elixir counter. Defaults remain deterministic card/cell argmax and tau0.35; failed sampling/Rocket-area options stay disabled. Forced anti-leak spending has been removed. `--no-anti-leak` remains a harmless compatibility alias. The screenshot menu guard remains opt-in; tick/countdown, stale-reader, input-timeout and receipt checks still prevent accidental inputs. The owner-approved temporary hero ability behavior remains unchanged.

Periodic recording via `--clip-every` now stays local. Automatic Discord clip/connection-loss notifications were removed from the live entry and supervisor. The historical `live_play_v2.py` command delegates to this canonical entry, so it cannot drift to stale defaults.

Verification covers selected/explicit/invalid checkpoint behavior, reader/decision/audit parity on archived real frames, navigation and tap receipt regressions, and rendering/decoding a short archived video. It is not a new live-match acceptance claim. The owner stopped the prior session after its match; STOP remains set for the supervisor. The single-match command above is a separate manual run and does not use that supervisor STOP file.
