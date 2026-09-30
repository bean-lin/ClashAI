"""L68 live test: generalist pilots a TRAINING CAMP match on MuMu from the memory reader. Owner-run.

    icebow/.venv/Scripts/python.exe scratchpad/gauntlet/L68/live_reader/live_play.py --training-camp [--dry-run]

Loop: reader frame (100 ms) -> pipeline.live_gen.GenPilot (opponent hand/next/elixir never used) -> if it plays,
two ordinary Android taps (hand slot, board) -> receipt from the NEXT frames: the tapped hand slot rotated (the
elixir-drop half of upstream card_receipt is dropped: regen hid cheap plays). No game-memory writes. Taps follow upstream's ScreenLayout
(native X kept on screen for side 1; arena shifted one tile from the Cannon read-back). Each confirmed troop's
spawn position is compared with the intended cell -> tap-calibration error in tiles.
Stops: battle over / tick stalled 3 s, 5 unconfirmed taps, --max-seconds. Log: live_play_<ts>.jsonl here.
--matches N --friend NAME: N matches back to back; between them friend_nav.py starts the next friendly 1v1 against
that friend's bot (allowlisted taps only; see its docstring and --nav-dry-run). Default N = 1: no navigation.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
from pipeline.live_gen import GenPilot  # noqa: E402
from hero_button import HeroButton, hero_ids, should_press  # noqa: E402

# adb.exe directly (same device pin as adb.sh): from Python, "bash" resolves to WSL's System32 bash, which cannot
# run the Windows adb -> empty output.
ADB = [r"C:\Program Files\Netease\MuMuPlayer\nx_device\15.0\shell\adb.exe", "-s", "127.0.0.1:16384"]
ENV = dict(os.environ)
RVA, ROOT_CTX = "0x1aeef98", "0x18"
UI_READY_MIN_TICK = 150
CONFIRM_TICKS = 60       # a tap is "unconfirmed" only after 60 GAME ticks (3 s) without registering -- never wall clock


def clock_verdict(tick: int, last_tick: int, idle_s: float) -> str:
    """wait | stall | proceed. 2026-09-30: the reader emits active+coherent frames at game_tick 0 (loading screen /
    countdown); the old guard counted that flat 0 as a stall and exited after 3 s. Tick 0 = the clock has not
    started: keep waiting, never decide. Only while the clock has NEVER run (last_tick < 0); a tick 0 after it ran
    (reader glitch) is an ordinary non-advancing tick and stalls after 3 s like any other."""
    if tick <= 0 and last_tick < 0:
        return "wait"
    return "proceed" if tick > last_tick or idle_s <= 3 else "stall"


def adb(*args: str, timeout: float = 5) -> str:
    return subprocess.run(ADB + list(args), capture_output=True, text=True, timeout=timeout, env=ENV).stdout


EVEN_BUILDINGS = {"Tesla"}   # ponytail: the icebow deck's only 2x2 building; add Cannon etc. for other decks


class Layout:
    """upstream native_core/mumu_live_actions.ScreenLayout.from_size, taking OUR board frame (me at the bottom,
    side 1 rotated 180 deg) instead of a canonical cell."""
    def __init__(self, w: int, h: int):
        vw = min(float(w), h * 9 / 16) if w / h > 0.8 else float(w)
        left = (w - vw) / 2
        self.w, self.h = w, h
        self.ax0, self.ax1 = left + vw * .055, left + vw * .945
        self.ay0, self.ay1 = h * (.105 - .685 / 32), h * (.790 - .685 / 32)
        self.hand_y, self.hand_x = h * .890, [left + vw * f for f in (.31, .50, .69, .88)]

    def board(self, xy: tuple[float, float], side: int, even: bool = False) -> tuple[int, int]:
        fx = 1.0 - xy[0] if side == 1 else xy[0]          # screen keeps native X; our frame rotated it
        fy = xy[1]
        if even:   # a 2x2 building takes its tapped tile's ARENA lower-left corner (RoyaleSim placement.SNAP_EVEN_CORNER);
            # a tap ON the corner snapped 1 tile left 34/35 times (L68 hog-pull audit) -> tap a quarter tile inside,
            fx += 0.25 / 18                                # +x native on both sides
            fy += 0.25 / 32 if side == 1 else -0.25 / 32   # +y native: side 1's screen y runs with native y, side 0's against
        return round(self.ax0 + fx * (self.ax1 - self.ax0)), round(self.ay0 + fy * (self.ay1 - self.ay0))

    def hand(self, pos: int) -> tuple[int, int]:
        return round(self.hand_x[pos]), round(self.hand_y)


def screen_size() -> tuple[int, int]:
    # An adb SERVER restart (e.g. another adb version on the PC) drops the TCP device 127.0.0.1:16384 while MuMu keeps
    # running (2026-09-25 02:3x: `devices` listed only emulator-5554). Reconnect first; fail readably if still gone.
    subprocess.run([ADB[0], "connect", ADB[2]], capture_output=True, text=True, timeout=10, env=ENV)
    if adb("shell", "id -u").strip() != "0":               # MuMu restarts reset adbd to the shell user; the reader
        adb("root")                                        # needs root for /proc/PID/mem. `adb root` restarts adbd,
        time.sleep(2)                                      # which drops the TCP device -> reconnect.
        subprocess.run([ADB[0], "connect", ADB[2]], capture_output=True, text=True, timeout=10, env=ENV)
    sizes = re.findall(r"(\d+)x(\d+)", adb("shell", "wm size"))
    if not sizes:
        raise SystemExit(f"MuMu not reachable at {ADB[2]} (adb connect failed). Is MuMu running? "
                         f"`bash scratchpad/gauntlet/L68/live_reader/adb.sh devices -l` shows what adb sees.")
    w, h = sizes[-1]                                        # an Override size, if any, is listed last
    return int(w), int(h)


def my_frame_xy(e: dict, side: int) -> tuple[float, float]:
    x, y = (18000 - e["x"], 32000 - e["y"]) if side == 1 else (e["x"], e["y"])
    return x / 18000, 1 - y / 32000


class ScreenRec:
    """Device-side `screenrecord` in back-to-back segments (Android caps one run at 180 s; a match with overtime is
    longer). Each segment logs /proc/uptime just before recording starts -- the same clock as the reader's
    sample_monotonic_us -- so overlay_replay.py can align boxes to video. Stopped with SIGINT so the mp4 finalises."""
    SEG_S = 170

    def __init__(self, stamp: str):
        import threading
        self.stamp, self.segments, self.stop_flag = stamp, [], False
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self) -> None:
        i = 0
        while not self.stop_flag:
            remote = f"/sdcard/lp_{self.stamp}_{i}.mp4"
            p = subprocess.Popen(ADB + ["shell", f"cat /proc/uptime; exec screenrecord --time-limit {self.SEG_S} "
                                                 f"--bit-rate 6000000 {remote}"],
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=ENV)
            up = (p.stdout.readline() or "0").split()[0]
            self.segments.append([remote, float(up)])
            p.wait()
            i += 1

    def stop(self) -> list:
        """Finish the segment in progress, pull every segment to OUT_DIR/raw, delete it from the device."""
        self.stop_flag = True
        adb("shell", "pkill -INT screenrecord")
        self.thread.join(timeout=10)
        raw = REPO / "icebow" / "data" / "overlayed_replays" / "raw"
        raw.mkdir(parents=True, exist_ok=True)
        out = []
        for remote, t0 in self.segments:
            local = raw / Path(remote).name
            subprocess.run(ADB + ["pull", remote, str(local)], capture_output=True, timeout=120, env=ENV)
            adb("shell", f"rm -f {remote}")
            if local.is_file():
                out.append([str(local), t0])
        return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--training-camp", action="store_true", help="REQUIRED: you confirm the match is Training Camp")
    ap.add_argument("--ckpt", default=str(REPO / "icebow/data/pipeline/gen_v1_s0/gen_s0.pt"))
    ap.add_argument("--tau", type=float, default=0.5)
    ap.add_argument("--leak", type=float, default=9.5, help="force a play at >= this elixir (anti-leak rule)")
    ap.add_argument("--interval-ms", type=int, default=100)
    ap.add_argument("--max-seconds", type=float, default=400,
                    help="PER-MATCH wall-clock cap (reset each match): overtime ends by 6,000 ticks = 300 s of "
                         "game time, + loading/countdown. Hitting it stops the whole run")
    ap.add_argument("--dry-run", action="store_true", help="decide and log, never tap")
    ap.add_argument("--overlay", choices=("both", "detector", "reader"), default="both",
                    help="replay style: detector = play.py-style YOLO boxes only (cosmetic, e.g. for posts), "
                         "reader = memory-reader markers + taps, both")
    ap.add_argument("--no-record", action="store_true",
                    help="skip the overlaid replay (default: screenrecord + reader boxes -> "
                         "icebow/data/overlayed_replays/live_<stamp>.mp4)")
    ap.add_argument("--device", default="auto", choices=("auto", "cuda", "cpu"),
                    help="where the model runs; auto = cuda when available. 2026-09-26: on CPU with torch's default "
                         "16 threads, other busy jobs pushed decisions from ~40 ms to 0.5-3.4 s")
    ap.add_argument("--extrapolate", type=int, default=26,
                    help="decide on the board this many ticks ahead, where the card lands (~26 live; 0 = off). "
                         "Screen (HANDOFF L68as): +3.4 pp gen / +6.9 pp v6lat vs no extrapolation at delay 26")
    ap.add_argument("--no-opp-counter", action="store_true",
                    help="feed the model opponent elixir = unknown instead of the public-events counter")
    ap.add_argument("--no-ability", action="store_true",
                    help="never press the hero ability button (default: pressed by hero_button.should_press when the "
                         "deck holds a hero and the button reads ready)")
    ap.add_argument("--matches", type=int, default=1,
                    help="play this many matches back to back (default 1 = one match, no navigation). > 1 needs "
                         "--friend: between matches friend_nav.py starts the next FRIENDLY 1v1 against that friend's "
                         "bot; the previous match's overlay renders in the background")
    ap.add_argument("--friend", help="the friend (a bot, never a ladder player) to play when --matches > 1; must be "
                                     "the friend the nav templates were cropped for")
    ap.add_argument("--nav-dry-run", action="store_true",
                    help="play nothing: run ONE between-match navigation that classifies the live screens and logs "
                         "the tap it WOULD make, never tapping (navigate by hand to test it)")
    a = ap.parse_args()
    if not a.training_camp:
        print("refusing: pass --training-camp to confirm the match is Training Camp (bot opponent)")
        return 2
    if a.matches < 1 or ((a.matches > 1 or a.nav_dry_run) and not a.friend):
        print("refusing: --matches > 1 and --nav-dry-run need --friend NAME (the friend's bot; never ladder)")
        return 2
    nav = None
    if a.matches > 1 or a.nav_dry_run:
        from friend_nav import FriendNav
        nav = FriendNav(ADB, a.friend, dry_run=a.nav_dry_run)   # refuses a friend the templates were not cropped for
        if screen_size() != (900, 1600):
            print("refusing: the nav templates are 900x1600; the device screen differs")
            return 2
        if a.nav_dry_run:
            return 0 if nav.run()[0] else 1
    import torch
    torch.set_num_threads(4)                         # never fight every core with the owner's other jobs
    device = ("cuda" if torch.cuda.is_available() else "cpu") if a.device == "auto" else a.device
    pilot = GenPilot(a.ckpt, device=device, gate_tau=a.tau, use_counter=not a.no_opp_counter,
                     extrapolate_ticks=a.extrapolate)
    lay = Layout(*screen_size())
    renders: list = []                                   # background overlay renders of matches 1..N-1
    try:
        for k in range(a.matches):
            if k:
                ok, why = nav.run()                      # results -> Social -> invite/accept -> battle loading
                if not ok:
                    print(f"[nav] run stopped before match {k + 1}: {why}", flush=True)
                    break
                pilot.reset_match()                      # same loaded model, fresh history / opp counter
            why = play_match(a, pilot, lay, device, renders if k + 1 < a.matches else None,
                             start_timeout=60 if k else None)   # after a nav handoff only
            if k + 1 < a.matches and why not in MATCH_OVER:
                print(f"[live] run stopped after match {k + 1}: {why}", flush=True)
                break
    finally:
        for p, name in renders:                          # stopping is safe: let the background renders finish
            if p.wait():
                print(f"[overlay] render failed (exit {p.returncode}); re-render with overlay_replay.py {name}")
    return 0


MATCH_OVER = {"battle_over_hands_visible", "battle_inactive", "tick_stalled"}   # ordinary match ends: nav may go on


def play_match(a, pilot, lay, device, renders: list | None, start_timeout: float | None = None) -> str:
    """One match (the whole pre---matches main loop). renders=None: overlay rendered here before returning, as a
    single match always was; a list: rendered in a background process appended to it. start_timeout: stop if the
    battle clock never runs within this many seconds (after a nav handoff). -> the stop reason."""
    stamp = time.strftime('%Y%m%d_%H%M%S')
    log = open(HERE / f"live_play_{stamp}.jsonl", "w", encoding="utf-8")
    import queue
    import threading
    _wlock = threading.Lock()
    stop: dict = {"why": "reader_stream_ended"}

    def W(**k):                                          # called from the main loop AND the reader thread
        if k.get("event") == "stop":
            stop["why"] = k["why"]
        with _wlock:
            log.write(json.dumps(k, default=str) + "\n")
            log.flush()
    W(event="start", screen=[lay.w, lay.h], tau=a.tau, leak=a.leak, dry_run=a.dry_run, ckpt=a.ckpt,
      extrapolate=a.extrapolate, opp_counter=not a.no_opp_counter, device=device)
    rec = None if a.no_record else ScreenRec(stamp)
    button = None if a.no_ability else HeroButton(ADB, lay.w, lay.h, HERE / "ability_crops", period_s=2.0)
    ab_pending, last_bstate = None, None
    cmd = (f"/data/local/tmp/live_sampler $(pidof com.supercell.clashroyale) {a.interval_ms} {RVA} {ROOT_CTX} "
           f"--unified 0")
    procs: list = []

    def stream():
        """Reader lines; the 2026-09-25 01:55 run lost the stream silently at tick 953, so a closed stream is now
        logged (exit code + stderr) and the reader restarted, at most 3 times."""
        for attempt in range(4):
            p = subprocess.Popen(ADB + ["shell", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                 env=ENV)
            procs.append(p)
            yield from p.stdout
            try:
                rc = p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                rc = None
            W(event="reader_closed", attempt=attempt, rc=rc, stderr=(p.stderr.read() or "")[-500:],
              last_tick=last_tick)
            time.sleep(0.5)
        W(event="stop", why="reader_closed_4x")

    t0, pending, fails, played, confirmed, last_tick, last_adv = time.time(), None, 0, 0, 0, -1, time.time()
    seen_active, both_vis, warmed, waiting_logged = False, 0, False, False
    from collections import deque
    dec_times: deque = deque(maxlen=20)
    warned_at = 0.0
    # 2026-09-25 18:32 friendly match: the reader stream stalled for up to 5.4 s (adb saturated by the hero-button
    # screenshots, ~330-430 ms each every 0.5 s), then the loop worked through the backlog IN ORDER and decided on
    # frames up to ~20 s old -> long "pending" leaks, then dumps. Now a thread pumps the stream into a queue; every
    # frame still feeds the counter / log / confirmations in order, but the model only DECIDES on the newest frame.
    q: queue.Queue = queue.Queue()

    def pump():
        for ln in stream():
            q.put(ln)
        q.put(None)
    threading.Thread(target=pump, daemon=True).start()
    try:
        while True:
            line = q.get()
            if line is None:
                break
            newest = q.empty()                           # decide only on the newest frame available
            now = time.time()
            if now - t0 > a.max_seconds:
                live = last_tick >= 0 and now - last_adv <= 3        # clock still running: a cap, not an end
                print(f"[live] --max-seconds {a.max_seconds:.0f} hit at tick {last_tick} "
                      f"({'battle clock STILL ADVANCING -- capped mid-match' if live else 'clock not advancing'}); "
                      f"stopping the run", flush=True)
                W(event="stop", why="max_seconds", clock_advancing=live, last_tick=last_tick,
                  max_seconds=a.max_seconds); break
            if start_timeout and last_tick < 0 and now - t0 > start_timeout:
                W(event="stop", why="no_battle_start"); break
            try:
                f = json.loads(line)
            except ValueError:
                continue
            if not (f.get("battle_active") and f.get("coherent")):
                if seen_active and now - last_adv > 3:
                    W(event="stop", why="battle_inactive"); break
                continue
            tick = int(f["game_tick"])
            verdict = clock_verdict(tick, last_tick, now - last_adv)
            if verdict == "wait":                        # battle clock still at 0: no decisions, no stall clock
                if not waiting_logged:
                    print("[live] battle clock at tick 0 -- waiting for the match to start", flush=True)
                    W(event="waiting_clock", tick=tick)
                    waiting_logged = True
                continue
            if verdict == "stall":
                W(event="stop", why="tick_stalled", tick=tick); break
            if tick > last_tick:
                last_tick, last_adv = tick, now
            seen_active = True
            # Both hands visible = the results / replay screen (upstream mumu_live_controller never controls then).
            # 2026-09-25: deciding on such a frame raised in my_side_of and killed the run before the overlay render.
            vis = [p["side"] for p in f["players"] if any(i >= 0 for i in p["hand_deck_indices"])]
            if len(vis) != 1:
                both_vis += 1
                if both_vis >= 20:                       # ~2 s of it: the match is over
                    W(event="stop", why="battle_over_hands_visible", tick=tick); break
                continue
            both_vis = 0
            opp_est = pilot.observe(f)                   # public-events opp-elixir counter: EVERY active+coherent frame
            if not warmed:                               # the first CUDA forward took 1.6 s (2026-09-26 22:04) -- pay it
                try:                                     # before the 150-tick input guard, not on the first real play
                    pilot.decide(f)
                except Exception:                        # noqa: BLE001 -- warm-up only; the real decision retries
                    pass
                warmed = True
            if tick < UI_READY_MIN_TICK:
                continue
            side = next(p["side"] for p in f["players"] if any(i >= 0 for i in p["hand_deck_indices"]))
            me = next(p for p in f["players"] if p["side"] == side)
            t_dev = f["sample_monotonic_us"] / 1e6
            if rec:                                          # what the model perceived, for overlay_replay.py
                opp = next(p for p in f["players"] if p["side"] != side)
                # ents: side, x, y, card_id, hp, max_hp, kind, address (address/kind = the opp-elixir counter's play
                # detection). opp_elixir_true_EVAL_ONLY grades that counter offline; it is never fed to the model.
                W(event="frame", t_dev=t_dev, tick=tick, my_side=side, elixir=me["elixir_raw"] / 1e4, backlog=q.qsize(),
                  opp_elixir_true_EVAL_ONLY=opp["elixir_raw"] / 1e4, opp_elixir_est=opp_est,
                  ents=[[e["side"], e["x"], e["y"], e["card_id"], e["hp"], e["max_hp"], e["kind"], e["address"]]
                        for e in f["entities"]])
            hids = hero_ids(me)
            if button:                                   # screenshot only after the hero was played (not in hand)
                button.want = bool(hids) and any(i not in me["hand_deck_indices"] for i, fl in
                                                 enumerate(me.get("deck_form_flags") or []) if int(fl) == 2)
            if button and hids:
                st = button.fresh_state()
                if st != last_bstate:                    # every transition logged: the calibration evidence
                    W(event="button", tick=tick, state=st, blue=round(button.blue, 3), grey=round(button.grey, 3))
                    last_bstate = st
                if ab_pending:
                    spent = ab_pending["elixir_raw"] - me["elixir_raw"]
                    moved = button.ts > ab_pending["t"] + 0.3 and st in ("grey", "absent")
                    if spent > 0 or moved:
                        W(event="ability_confirmed", tick=tick, elixir_drop=spent / 1e4, button_after=st,
                          latency_s=round(now - ab_pending["t"], 3))
                        ab_pending = None
                    elif tick - ab_pending["tick"] > CONFIRM_TICKS:
                        W(event="ability_unconfirmed", tick=tick, button_after=st)
                        ab_pending = None
                elif st == "ready" and not pending and newest:
                    press, why = should_press(f, side, hids)
                    if press:
                        W(event="ability", tick=tick, t_dev=t_dev, why=why, tap=list(button.point),
                          elixir=me["elixir_raw"] / 1e4)
                        if not a.dry_run:
                            button.tap()
                            ab_pending = {"t": now, "tick": tick, "elixir_raw": me["elixir_raw"]}
            if pending:
                old = pending["me"]
                pos = pending["d"]["hand_pos"]
                rotated = me["hand_deck_indices"][pos] != old["hand_deck_indices"][pos]
                dropped = old["elixir_raw"] - me["elixir_raw"]     # logged only: regen during the ~28-tick landing
                if rotated:   # (~1 elixir in 2x, ~1.5 in 3x) outgrows a Skeletons' cost, so "elixir dropped" missed
                    # 16 of 23 real plays and stopped matches (L68 2026-09-29); a slot rotates only when its card is played
                    d = pending["d"]
                    cid = me["deck_card_ids"][d["deck_index"]]
                    new = [e for e in f["entities"] if e["side"] == side and e["card_id"] == cid
                           and e["address"] not in pending["addrs"]]
                    err = None
                    if new:
                        ex, ey = my_frame_xy(new[0], side)
                        err = round(((ex - d["xy"][0]) * 18) ** 2 + ((ey - d["xy"][1]) * 32) ** 2, 4) ** 0.5
                    # stamp the LANDING time (this confirmation frame), as training rows do -- the decision frame's
                    # time made the model's "seconds since my play" ~1.3 s too large (T9 worker finding, 2026-09-25)
                    pilot.record_play(d["card"], d["form"], d["xy"], tick * 0.05)
                    confirmed += 1
                    W(event="confirmed", tick=tick, name=d["name"], intended=d["xy"], elixir_drop=dropped / 1e4,
                      spawn=[my_frame_xy(e, side) for e in new[:1]], err_tiles=err, latency_s=round(now - pending["t"], 3))
                    pending = None
                elif tick - pending["tick"] > CONFIRM_TICKS:
                    fails += 1
                    W(event="unconfirmed", tick=tick, name=pending["d"]["name"], intended=pending["d"]["xy"],
                      p_play=pending["d"]["p_play"], elixir=old["elixir_raw"] / 1e4, fails=fails)
                    pending = None
                    if fails >= 5:
                        W(event="stop", why="5_unconfirmed"); break
                continue
            if not newest:                               # stale frame: newer ones are already queued
                continue
            t_dec = time.time()
            d = pilot.decide(f)
            decide_ms = round((time.time() - t_dec) * 1000)
            dec_times.append(decide_ms)
            # 2026-09-26: every bad live match that evening ran with the CPU loaded (training / screens / low-battery
            # throttle): decisions took 176-347 ms instead of ~40 ms, the loop fell behind, the bot leaked. Say so.
            if len(dec_times) >= 10 and sorted(dec_times)[len(dec_times) // 2] > 100 and now - warned_at > 30:
                msg = (f"CPU-STARVED: median decision {sorted(dec_times)[len(dec_times) // 2]} ms over the last "
                       f"{len(dec_times)} decisions (normal ~40 ms), backlog {q.qsize()} frames -- close heavy jobs "
                       f"(training, screens) and plug in; play quality will be poor until then")
                print(msg, flush=True)
                W(event="cpu_starved", tick=tick, median_decide_ms=sorted(dec_times)[len(dec_times) // 2],
                  backlog=q.qsize())
                warned_at = now
            el = me["elixir_raw"] / 1e4
            forced = not d["play"] and el >= a.leak and d["card"] > 0
            if not (d["play"] or forced):
                continue
            hand, board = lay.hand(d["hand_pos"]), lay.board(d["xy"], side, even=d["name"] in EVEN_BUILDINGS)
            W(event="play", tick=tick, t_dev=t_dev, name=d["name"], p_play=round(d["p_play"], 4), forced=forced, elixir=el,
              hand_pos=d["hand_pos"], xy=[round(v, 4) for v in d["xy"]], tap_hand=hand, tap_board=board)
            played += 1
            if a.dry_run:
                continue
            t_tap = time.time()
            adb("shell", f"input tap {hand[0]} {hand[1]}; sleep 0.05; input tap {board[0]} {board[1]}")
            W(event="tap_timing", tick=tick, decide_ms=decide_ms, tap_ms=round((time.time() - t_tap) * 1000),
              frame_age_backlog=q.qsize())
            pending = {"d": d, "me": me, "t": now, "tick": tick, "addrs": {e["address"] for e in f["entities"]}}
    finally:
        for p in procs:
            p.terminate()
        adb("shell", "pkill -f live_sampler")
        if button:
            button.stop()
        if rec:
            W(event="recording", segments=rec.stop())
        W(event="end", played=played, confirmed=confirmed, fails=fails, seconds=round(time.time() - t0, 1))
        log.close()
        print(json.dumps({"played": played, "confirmed": confirmed, "fails": fails, "log": log.name}))
        if rec and renders is not None:                  # a next match follows: render in a separate low-priority
            try:                                         # process (no GIL/CPU fight with its decisions)
                renders.append((subprocess.Popen(
                    [sys.executable, str(HERE / "overlay_replay.py"), log.name, "--overlay", a.overlay],
                    creationflags=getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)), log.name))
            except Exception as exc:                     # noqa: BLE001 -- never mask the original error
                print(f"[overlay] render failed: {exc!r}; re-render with overlay_replay.py {log.name}")
        elif rec:                                        # in `finally`: a crash above must not lose the replay
            try:
                from overlay_replay import render
                render(Path(log.name), overlay=a.overlay)
            except Exception as exc:                     # noqa: BLE001 -- never mask the original error
                print(f"[overlay] render failed: {exc!r}; re-render with overlay_replay.py {log.name}")
    return stop["why"]


if __name__ == "__main__":
    raise SystemExit(main())
