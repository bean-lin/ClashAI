DONE_WITH_CONCERNS

This is a source-and-evidence delivery, not a deployed reader upgrade. The two host collectors have exited normally. The running pilot and its reader were not changed.

## Sandbox bridge findings (item 1)

Source: `research/ext/cr-native-sandbox/android_probe/native/jni_bridge.cpp`, especially lines 91-98, 1150-1175, 1380-1530, 1582-1677 and 2033-2138. These are **other-build** findings (150535029), not live offset authority.

The sandbox's manager `+0x20` leads to context; context `+0x90` to battle. Battle `+0xa8 -> hp_state`, hp_state `+8 -> registry`, registry `+0x40 -> collection`, collection `+8 -> data`, `+0x14 -> count`. It enumerates object pointers from the same registry for units, projectiles and effects. The global object ID at `+8` separates series: 3M areas, 4M projectiles/other nonunits, 5M troops/towers. It additionally checks vtables: projectile `0x1969b38`, area `0x19691f8`; these RVAs are wrong for the live build.

Common fields: side `+0x78`, x/y `+0x7c/+0x80`, secondary x/y `+0x84/+0x88`, card ID `+0xac`. Projectile pointer candidates are source `+0x100`, target `+0x108`, attached owner `+0x118`; target coordinate candidates `+0x120/+0x124`. Areas use data `+0x48`, level `+0xfc`, `+0x100` labelled elapsed, override `+0x114`. The sandbox estimates remaining life from override or data `+0x170/+0x174/+0x178`, radius from `+0x17c`, and explicitly does not implement its tournament-cap branch. **Live capture disproves that elapsed interpretation and does not validate those data offsets.**

Buffs are per-character: entity `+0x18 -> component array`; kind `+0x30` bit 3 and component count `+0x24 >=4` gate component slot 3 (`array+0x18`). Manager vtable is `0x196ec68`; manager `+0x18 -> instance pointer array`, count `+0x24`, capped at 64. Instance owner `+0`, remaining/total `+8/+0xc`, data `+0x18`, level `+0x28`, instigator side `+0x40`, shield HP `+0x54`. Data supplies name/ID, damage reduction, speed multipliers, invisibility and other flags. Manager-vtable or owner mismatch is flagged. Buff exports were already marked unverified upstream and are **not** claimed as live-validated or added here.

## Live evidence (items 2-3)

`identity.json` independently confirms build 160402012, PID 2013 and ELF64 machine 62 at `0x74b3c0206000`. Capture metadata preserves mapping snapshots. No native game functions were called.

Root chain: `*[base+0x1aeef98] -> *[root+0x18] -> *[context+0x90] = battle`. The downstream registry chain is unchanged from the sandbox. In observed matches `*[player_state+8] == battle`, so its collection is also directly at `battle+0x40`. Troop vtable `0x19f6c28`; king tower `0x19f7838`; projectile `0x19f7370`; area `0x19f6a28`. `0x19f7038` also appears among 3M/4M objects, including objects with cleared fields: it is **not** accepted as a projectile/area vtable.

| Field | Live offset | Evidence/status |
|---|---|---|
| vtable pointer / generation ID | `0x00` / `0x08` | Map-relative class and per-battle object identity |
| side / x / y / native card ID | `0x78` / `0x7c` / `0x80` / `0xac` | Cast-correlated for Rocket, Log, Tornado |
| projectile target x/y | `0x120` / `0x124` | Rocket endpoint exactly matches native cast target |
| projectile source/target/attached owner pointers | `0x100` / `0x108` / `0x118` | Exported raw pointer candidates; semantics not independently validated here |
| area data / level | `0x48` / `0xfc` | Data names recovered; level exported as raw |
| area remaining time | `0x100` | Countdown: 101/101 adjacent coherent pairs match -50 ms/tick |
| area override candidate | `0x114` | Exported as `life_override_ms_raw`; no derived lifetime formula |
| evolved form | card ID at `0xac` belongs to 13M table | Names plus cast cycles, independently counted bodies |

Rocket example: `live_play_20261003_124543.jsonl`, play 689, confirmed 717; `capture_a` batches 105/106, ticks 752/772, address `0x74b519d47a00`, generation 4000023, side 1. Positions `(11640,16346)` and `(13078,9506)` move toward constant target `(13500,7500)`, exactly the logged target transformed from our frame. The capture contains 28 matched Log bodies. Log's endpoint is its roll endpoint, not necessarily its cast/start point; keep those concepts separate.

Tornado example: `live_play_20261003_125856.jsonl`, play 778, confirmed 806; `capture_b` batches 323/324, ticks 818/825, address `0x74b4780ffad0`, generation 3000005, side 1. Both positions equal `(4500,17500)`, the native cast point. Data name `Tornado`; remaining 400 -> 50 ms. Other corroborating countdowns include BarbarianRage, IceWizardHero_FreezeAeo, Freeze and Rage. Data `+0x170` is -256 for the recorded Tornado, further demonstrating that the old lifetime formula is unsuitable.

Evolution is not hidden behind a missing boolean in these observations: the native card ID itself distinguishes forms. Knight/`Knight_EV1` use 26000000/13000000; Tesla/`Tesla_EV1` use 27000006/13000102. Data names come through entity `+0x48`, native string length at data `+0x2c`, inline/indirect chars `+0x30`. For each matched body, confirmed-cast ordinal, independent name, and at least one coherent sample agree: Knight 24 base/6 evolved; Tesla 15 base/5 evolved. Evolved bodies are third casts in the observed two-base/one-evolved cycle. The first mid-match Knight evolution was not counted when its onset was too far from a confirmed cast. The audit retains five examples per class with address, generation, tick and log.

Opponent table-13 forms include `electro_dragon_ev1` and `RageBarbarian_EV1`. `video_evidence_0.png` / `_1.png` were extracted from the **already existing** recorded match `lp_20261003_124226_0.mp4`; no capture command was issued. The right-bridge enemy cluster agrees with the sampled positions; purple rage/freeze effects obscure strict visual evolution identification. Encoder delay is also uncalibrated. Treat this as a limited visual cross-check, not universal form validation.

## Capture bounds and limitations

`probe_host.py` uses root `re_peek` with O_RDONLY and one adb call per batch: stdin is written to `/data/local/tmp/re_<tag>_req`, output to `/data/local/tmp/re_<tag>_out`, then cat. `MSYS_NO_PATHCONV=1` is set. Requests are restricted to readable mappings, at most 1,024 requests / 256 KiB per batch. Game memory is never written. All host outputs are in this directory.

Capture A: 720 one-second batches, 722 adb calls, 58,329,492 estimated transferred text bytes, 86 failed individual memory reads. Capture B: 960 half-second batches, 962 calls, 31,192,646 bytes, no failed reads; expensive container census runs in four-batch bursts every 40 batches. Measured minimum batch-start gaps exceed 1.0000/0.5000 seconds. Approximate traffic was 79/63 KiB/s; maximum batch time 0.418/0.442 s. These totals exclude separate setup/identity/clock checks.

The census scans aligned pointers in `0x600` battle/player-state windows plus registry, up to 160 candidate headers; it tests Supercell pointer/capacity/count vectors and STL triples, bounded to 256 elements. `evidence_audit.json` lists candidate paths/vtables. It is not an exhaustive heap or linked-list proof. The main registry allows up to 2,048 entries. Raw object windows are `0x200` and may extend beyond an individual object's allocation; only the identified class fields are interpreted.

Dependent pointers are planned from prior batches. Offline decoders use **current batch bytes only**, require current registry-prefix membership and class IDs, and expose missing suffixes/objects. There are 1,623 decodable and 1,592 tick-coherent frames, with 2,826 missing object observations. Missing reads, frees, reuse and sub-second lifetimes prevent completeness claims. Clock fits associate eight battle instances with logs, median errors about 0.87-1.41 ticks. A tick bracket is not an engine lock. Mapping snapshots are not refreshed continuously.

## Sampler v2 and verification (item 4)

`live_sampler2.c` is a standalone copy of upstream with optional `--extended` after `--unified N`. The original default readers and JSON formatters are preserved verbatim. With the flag, the reader adds per-entity `evo` 0/1, admits table-13 bodies that v1 filters, and adds projectiles/effects plus validity/error metadata. Native form IDs are retained; no unverified normalization formula maps Tesla 13000102 to its base ID. Other consumers may need explicit form mapping before eventual integration.

The extension reads within v1's tick/root/context/battle bracket. It suppresses nonunit arrays on inactive, incoherent or failed extended reads. `remaining_ms` comes directly from the measured countdown; negative values become null. Unknown nonunit classes are counted, not guessed. No buff extension or game input was added. The inherited `kill(pid,0)` is only an existence/permission check, not a termination signal.

**Not compiled or run here. No v1/v2 runtime diff result exists.** Exact lead build command in WSL, from this directory:

```sh
gcc -O2 -static -o live_sampler2 live_sampler2.c
```

The C header contains the required lead checklist. Independent live JSON streams necessarily differ in reader_pid, timestamps, timings and scheduling. `compare_default.py` reports raw equality separately, then compares coherent same-tick payloads excluding only reader_pid, sequence, sample_monotonic_us and read_us. A normalized comparison is not a byte-identical formatter proof; the lead should additionally compare deterministic identical C frame fixtures.

Reproduction from repository root (Python only, no device reads):

```text
python -B scratchpad/gauntlet/L70/reader/test_reference.py
python -B scratchpad/gauntlet/L70/reader/audit_evidence.py
python -B scratchpad/gauntlet/L70/reader/reference_fields.py --capture scratchpad/gauntlet/L70/reader/capture_a.jsonl --out scratchpad/gauntlet/L70/reader/decoded_fresh.jsonl
```

The Python reference deliberately retains partial decoded research evidence with `extension.valid=false` and missing-read diagnostics; C suppresses nonunits on invalid frames. Compare new field values on identical valid captured bytes. Seven tests cover recorded Rocket and Tornado, evolution names/cycles with at least five independent bodies per class, wrong-build vtable rejection, malformed/missing reads, negative timers and unchanged default source sections. These are source/offline checks, not C compilation or engine runtime evidence.
