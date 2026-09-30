"""friend_nav offline: every L69 capture classifies to its screen, plans are the allowlisted input at the expected
point, the Battle / Quickplay buttons are unreachable, stop rules, cross-invite, and an end-to-end run on a scripted
fake device (fake clock; dry-run sends nothing). No emulator is touched."""
import ast
import random
import sys
import time as _time
import types
from pathlib import Path

import cv2
import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import friend_nav as fn  # noqa: E402

RAW = HERE.parents[1] / "L69" / "nav" / "raw"
# Measured from the captures HERE, independently of friend_nav.FORBIDDEN: editing the module's table (a bypass)
# must not make these tests pass.
BATTLE = (305, 1168, 605, 1335)          # yellow Battle button, after_ok_131638
QUICKPLAY = (69, 1284, 393, 1369)        # friends_list_130251
EXPECT = {                               # capture -> (screen, planned target, tap point)
    "results_131619": ("results", "results_ok", (450, 1451)),
    "after_ok_131638": ("main", "main_to_social", None),
    "test_now_125953": ("main", "main_to_social", None),
    "friends_list_130251": ("social", "social_scroll", None),          # friend's row cut off at the list bottom
    "friends_list_130915": ("social", "friend_row", (292, 1129)),
    "friend_entry_130350": ("popup", "popup_friendly_battle", (193, 1312)),
    "battle_type_130729": ("battle_type", "battle_type_1v1", (450, 442)),
    "invite_sent_130520": ("pending", None, None),
    "cancel_invite_130818": ("pending", None, None),
    "invite_incoming_131227": ("incoming", "invite_accept", (575, 739)),
}
CLF = fn.Classifier()


def img(name):
    return cv2.imread(str(RAW / f"{name}.png"))


def inside(pt, r):
    return r[0] <= pt[0] <= r[2] and r[1] <= pt[1] <= r[3]


def touched_points(cmd):
    """Every screen point an input command touches (a swipe: 21 samples along its path)."""
    v = [int(t) for t in cmd.split()[2:]]
    if cmd.startswith("input tap"):
        return [tuple(v)]
    x0, y0, x1, y1 = v[:4]
    return [(x0 + (x1 - x0) * i / 20, y0 + (y1 - y0) * i / 20) for i in range(21)]


def check_safe(target, pt):
    """The invariant: no input in the Battle rectangle, none in Quickplay except the verified popup button."""
    for p in touched_points(fn.command_for(target, pt)):
        assert not inside(p, BATTLE), (target, p)
        assert target == "popup_friendly_battle" or not inside(p, QUICKPLAY), (target, p)


def plan_after_wait(scr):
    return fn.Nav(0.0, random.Random(0)).plan(scr, 25.0)       # past the 5-20 s invite wait


def test_every_capture_is_covered():
    assert sorted(p.stem for p in RAW.glob("*.png")) == sorted(EXPECT)


@pytest.mark.parametrize("name", sorted(EXPECT))
def test_capture_classifies_and_plans_allowlisted_input(name):
    screen, target, pt = EXPECT[name]
    scr = CLF.classify(img(name))
    assert scr["screen"] == screen, scr
    p = plan_after_wait(scr)
    if target is None:
        assert p[0] == "wait", p
        return
    assert p[:2] == ("act", target), p
    if pt is None:
        assert p[2] is None
    else:
        assert abs(p[2][0] - pt[0]) <= 3 and abs(p[2][1] - pt[1]) <= 3, p
    check_safe(target, p[2])


def test_results_capture_verifies_the_friend():
    assert CLF.classify(img("results_131619"))["friend"] is True


def test_results_foreign_opponent_stops():
    im = img("results_131619")
    im[428:480, 305:590] = im[455, 290]                         # blank the opponent name with the banner colour
    scr = CLF.classify(im)
    assert scr["screen"] == "results" and scr["friend"] is False
    nav = fn.Nav(0.0, random.Random(0))
    plans = [nav.plan(scr, 1.0 + i) for i in range(3)]
    assert [p[0] for p in plans] == ["wait", "wait", "stop"], plans    # never taps OK for a non-friend


def test_unknown_screen_stops_after_timeout_and_never_acts():
    scr = CLF.classify(np.zeros((1600, 900, 3), np.uint8))
    assert scr["screen"] == "unknown"
    nav = fn.Nav(0.0, random.Random(0))
    plans = [(t, nav.plan(scr, t)) for t in np.arange(1.0, 30.0, 0.5)]
    assert all(p[0] == "wait" for t, p in plans if t - 1.0 <= 20)
    stop_t = next(t for t, p in plans if p[0] == "stop")
    assert 21.0 <= stop_t <= 21.6


def test_transition_timeout_stops_even_on_a_known_screen():
    nav = fn.Nav(0.0, random.Random(0))
    assert nav.plan(CLF.classify(img("invite_sent_130520")), 181.0)[0] == "stop"


def test_popup_for_someone_else_is_not_acted_on():
    im = img("friend_entry_130350")
    im[1006:1038, 110:280] = 255                                # header name blanked
    assert CLF.classify(im)["screen"] == "popup_other"


def test_popup_button_drawn_over_quickplay_without_popup_body_is_rejected():
    """The dangerous misread: a Friendly-Battle button + friend header over the bare Social list, where the tap
    would land on Quickplay. The popup's white body is missing on both sides -> never 'popup'."""
    src, im = img("friend_entry_130350"), img("friends_list_130251")
    im[1272:1352, 95:292] = src[1272:1352, 95:292]
    im[1006:1038, 118:270] = src[1006:1038, 118:270]
    scr = CLF.classify(im)
    assert scr["screen"] != "popup", scr
    nav = fn.Nav(0.0, random.Random(0))
    for t in np.arange(25.0, 50.0, 0.5):
        p = nav.plan(scr, t)
        if p[0] == "act":
            check_safe(p[1], p[2])


def test_main_screen_never_yields_battle_or_quickplay_input():
    for name in ("after_ok_131638", "test_now_125953"):
        scr = CLF.classify(img(name))
        nav = fn.Nav(0.0, random.Random(1))
        for t in np.arange(0.0, 60.0, 0.5):
            p = nav.plan(scr, t)
            assert p[0] == "act" and p[1] == "main_to_social", p
            check_safe(p[1], p[2])


def test_friend_row_low_on_screen_scrolls_instead_of_tapping():
    p = plan_after_wait({"screen": "social", "row": (300, 1200), "scores": {}})   # row at the Battle button's height
    assert p[:2] == ("act", "social_scroll")


def test_friend_row_missing_stops_after_three_scrolls():
    nav = fn.Nav(0.0, random.Random(0))
    scr = {"screen": "social", "row": None, "scores": {}}
    for i in range(3):
        p = nav.plan(scr, 25.0 + i)
        assert p[:2] == ("act", "social_scroll")
        nav.acted("social_scroll", 25.0 + i)
    assert nav.plan(scr, 30.0)[0] == "stop"


def test_waits_for_the_friends_invite_before_sending():
    nav = fn.Nav(0.0, random.Random(0))
    wait = nav.wait_until
    assert 5 <= wait <= 20
    scr = CLF.classify(img("friends_list_130915"))
    assert nav.plan(scr, wait - 0.1)[0] == "wait"
    assert nav.plan(scr, wait + 0.1)[:2] == ("act", "friend_row")


def test_cross_invite_cancels_ours_then_accepts_theirs():
    im = img("invite_incoming_131227")
    im[80:225, 25:875] = img("invite_sent_130520")[80:225, 25:875]     # our pending banner over their invite
    scr = CLF.classify(im)
    assert scr["screen"] == "cross", scr
    nav = fn.Nav(0.0, random.Random(0))
    p = nav.plan(scr, 30.0)
    assert p[:2] == ("act", "invite_cancel_ours") and abs(p[2][0] - 750) <= 3 and abs(p[2][1] - 149) <= 3
    check_safe(*p[1:])
    nav.acted("invite_cancel_ours", 30.0)
    assert nav.wait_until >= 35.0                                     # fresh random delay after a cross
    p = nav.plan(CLF.classify(img("invite_incoming_131227")), 31.5)   # ours gone, theirs still up
    assert p[:2] == ("act", "invite_accept")
    check_safe(*p[1:])
    nav.acted("invite_accept", 31.5)
    black = CLF.classify(np.zeros((1600, 900, 3), np.uint8))           # loading screen
    assert nav.plan(black, 32.0)[0] == "wait"
    assert nav.plan(black, 35.1)[0] == "handoff"


def test_allowlist_is_structural():
    with pytest.raises(fn.NavViolation):
        fn.command_for("battle", (455, 1250))
    with pytest.raises(fn.NavViolation):
        fn.command_for("quickplay", (230, 1325))
    for target, (kind, spec) in fn.TARGETS.items():
        if kind == "swipe":
            check_safe(target, None)
            with pytest.raises(fn.NavViolation):
                fn.command_for(target, (455, 1250))
            continue
        with pytest.raises(fn.NavViolation):
            fn.command_for(target, (455, 1250))                         # the Battle button's centre
        if target != "popup_friendly_battle":
            with pytest.raises(fn.NavViolation):
                fn.command_for(target, (230, 1325))                     # Quickplay's centre
    rng = random.Random(0)                                              # fuzz: whatever command_for accepts is safe
    for _ in range(20000):
        target = rng.choice([t for t, (k, _) in fn.TARGETS.items() if k == "tap"])
        pt = (rng.uniform(0, 900), rng.uniform(0, 1600))
        try:
            check_safe(target, pt)
        except fn.NavViolation:
            pass


def test_only_command_for_builds_input_commands():
    src = (HERE / "friend_nav.py").read_text()
    tree = ast.parse(src)
    fdef = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "command_for")
    lines = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
             and ("input tap" in n.value or "input swipe" in n.value or "keyevent" in n.value)]
    assert len(lines) == 2 and all(fdef.lineno <= ln <= fdef.end_lineno for ln in lines), lines
    shells = [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and n.value == "shell"]
    assert len(shells) == 1                                              # the one adb shell call: `cmd` from command_for


# ---- end to end on a scripted fake device ---------------------------------------------------------------------------
class FakeDevice:
    """Screens advance only when the matching allowlisted input arrives -- like the game."""
    NEXT = {"results_131619": ((450, 1451), "after_ok_131638"),
            "after_ok_131638": ("swipe", "friends_list_130915"),
            "friends_list_130915": ((292, 1129), "friend_entry_130350"),
            "friend_entry_130350": ((193, 1312), "battle_type_130729"),
            "battle_type_130729": ((450, 442), "invite_sent_130520")}

    def __init__(self):
        self.screen, self.pending_polls, self.cmds, self.now = "results_131619", 0, [], 0.0
        self.imgs = {n: img(n) for n in EXPECT}

    def grab(self):
        if self.screen == "invite_sent_130520":
            self.pending_polls += 1
            if self.pending_polls > 6:                                  # friend accepted: loading screen
                return np.zeros((1600, 900, 3), np.uint8)
        return self.imgs[self.screen]

    def run(self, args, **kw):
        cmd = args[-1]
        self.cmds.append(cmd)
        want, nxt = self.NEXT.get(self.screen, (None, None))
        v = cmd.split()
        if want == "swipe" and v[1] == "swipe" or (want and v[1] == "tap" and want != "swipe"
                                                   and max(abs(int(v[2]) - want[0]), abs(int(v[3]) - want[1])) <= 3):
            self.screen = nxt
        return types.SimpleNamespace(stdout=b"", returncode=0)


@pytest.mark.parametrize("dry", [False, True])
def test_end_to_end_fake_device(dry, monkeypatch, tmp_path):
    dev = FakeDevice()
    clock = types.SimpleNamespace(time=lambda: dev.now, strftime=_time.strftime,
                                  sleep=lambda s: setattr(dev, "now", dev.now + s))
    monkeypatch.setattr(fn, "time", clock)
    monkeypatch.setattr(fn.subprocess, "run", dev.run)

    class QuickNav(fn.Nav):                                             # shorter clocks: each frame costs a real
        TRANSITION_S = 20.0                                             # full-resolution classification

        def __init__(self, t0, rng=None):
            super().__init__(t0, rng)
            self.wait_until = t0 + 5.0
    monkeypatch.setattr(fn, "Nav", QuickNav)
    nav = fn.FriendNav(["adb"], "JinxTheCat", dry_run=dry, log_dir=tmp_path)
    monkeypatch.setattr(nav, "grab", dev.grab)
    ok, why = nav.run()
    if dry:
        assert dev.cmds == [] and not ok and "transition" in why        # nothing sent; stays on results -> 180 s stop
        return
    assert ok, why
    kinds = [c.split()[1] for c in dev.cmds]
    assert kinds == ["tap", "swipe", "tap", "tap", "tap"], dev.cmds
    for c in dev.cmds:
        for p in touched_points(c):
            assert not inside(p, BATTLE)
    in_qp = [c for c in dev.cmds if any(inside(p, QUICKPLAY) for p in touched_points(c))]
    assert len(in_qp) == 1 and dev.cmds.index(in_qp[0]) == 3              # only the verified popup button


def test_wrong_friend_refused():
    with pytest.raises(SystemExit):
        fn.FriendNav(["adb"], "SomeoneElse")


# ---- live_play.play_match safety (repair 2): fake reader / adb / pilot / guard, no device ---------------------------
import argparse  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import threading  # noqa: E402

import live_play as lp  # noqa: E402


def rframe(tick, stale=False):
    me = {"side": 0, "hand_deck_indices": [0, 1, 2, 3], "elixir_raw": 80000, "deck_card_ids": [26000000] * 8,
          "deck_form_flags": [0] * 8}
    opp = dict(me, side=1, hand_deck_indices=[-1] * 4)
    return json.dumps({"battle_active": True, "coherent": True, "game_tick": tick, "sample_monotonic_us": tick * 50000,
                       "players": [me, opp], "entities": [], "stale": stale}) + "\n"


class FakeSampler:
    """adb shell live_sampler: yields its lines slowly, then stays OPEN (a live sampler) until terminate()."""
    def __init__(self, lines, on_line=None):
        self.lines, self.on_line, self.killed = lines, on_line, threading.Event()
        self.stderr = io.StringIO("")
        self.stdout = self._out()

    def _out(self):
        for i, ln in enumerate(self.lines):
            if self.killed.is_set():
                return
            if self.on_line:
                self.on_line(i)
            yield ln
            _time.sleep(0.03)                           # one frame at a time: the loop sees each as the newest
        self.killed.wait(15)

    def terminate(self):
        self.killed.set()

    def wait(self, timeout=None):
        return 0


class FakeGuard:
    inst = None

    def __init__(self, adb, *a, **k):
        self.menu, self.armed = None, False
        FakeGuard.inst = self

    def feed(self, img):
        pass

    def stop(self):
        pass


class FakePilot:
    def __init__(self):
        self.decided, self.last = [], None

    def observe(self, f):
        return None

    def decide(self, f):
        self.decided.append(f)
        self.last = f
        return {"play": True, "card": 1, "form": 0, "hand_pos": 0, "deck_index": 0, "xy": (0.5, 0.6),
                "name": "Knight", "p_play": 0.9}

    def record_play(self, *a):
        pass


def run_match(monkeypatch, tmp_path, lines, dry_run, on_line=None, start_timeout=None):
    samplers, taps, pilot = [], [], FakePilot()

    def popen(args, **kw):
        s = FakeSampler(lines if not samplers else [], on_line)
        samplers.append(s)
        return s

    def adb(*args, **kw):
        if "input tap" in args[-1]:
            taps.append((args[-1], bool(pilot.last and pilot.last["stale"]), FakeGuard.inst.menu))
        return ""
    monkeypatch.setattr(lp.subprocess, "Popen", popen)
    monkeypatch.setattr(lp, "adb", adb)
    monkeypatch.setattr(lp, "MenuGuard", FakeGuard)
    monkeypatch.setattr(lp, "HERE", tmp_path)
    a = argparse.Namespace(tau=0.5, leak=9.5, dry_run=dry_run, ckpt="x", extrapolate=0, no_opp_counter=True,
                           no_record=True, no_ability=True, interval_ms=100, max_seconds=400, overlay="both")
    why = lp.play_match(a, pilot, lp.Layout(900, 1600), "cpu", None, start_timeout=start_timeout)
    return why, samplers, taps, pilot


def test_stale_same_tick_frames_never_decide_or_tap(monkeypatch, tmp_path):
    lines = []
    for t in range(150, 400, 2):
        lines += [rframe(t), rframe(t, stale=True), rframe(t, stale=True)]
    for dry in (True, False):
        why, samplers, taps, pilot = run_match(monkeypatch, tmp_path, lines, dry,
                                               on_line=lambda i: None if i < len(lines) - 1 else
                                               setattr(FakeGuard.inst, "menu", "results"))
        assert pilot.decided and not any(f["stale"] for f in pilot.decided), dry
        assert not any(stale for _, stale, _ in taps)
        assert (len(taps) > 0) == (not dry)
        assert len(samplers) == 1, "the sampler was restarted after the match's own kill"


def test_menu_during_match_stops_before_any_tap(monkeypatch, tmp_path):
    lines = [rframe(t) for t in range(150, 400, 2)]

    def menu_from_start(i):
        FakeGuard.inst.menu = "main"
    why, samplers, taps, pilot = run_match(monkeypatch, tmp_path, lines, False, on_line=menu_from_start)
    assert why == "menu_screen:main" and taps == [] and len(samplers) == 1

    def menu_midway(i):
        if i == 60:
            FakeGuard.inst.menu = "main"
    why, samplers, taps, pilot = run_match(monkeypatch, tmp_path, lines, False, on_line=menu_midway)
    assert why == "menu_screen:main" and taps and all(menu is None for _, _, menu in taps)
    assert why not in lp.MATCH_OVER and "menu_screen:results" in lp.MATCH_OVER


def test_silent_reader_fires_start_and_stall_timeouts(monkeypatch, tmp_path):
    why, *_ = run_match(monkeypatch, tmp_path, [], True, start_timeout=1.5)          # never a line
    assert why == "no_battle_start"
    monkeypatch.setattr(lp, "READER_SILENT_S", 1.5)
    why, samplers, *_ = run_match(monkeypatch, tmp_path, [rframe(t) for t in range(150, 170, 2)], True)
    assert why == "reader_silent" and len(samplers) == 1


def test_menu_guard_arms_only_when_the_clock_runs():
    g = fn.MenuGuard(["no-such-adb"], clf=CLF)
    g.stop()
    g.feed(img("after_ok_131638"))
    assert g.menu is None                               # started from the menu (Training Camp flow): ignored
    g.armed = True
    g.feed(np.zeros((1600, 900, 3), np.uint8))
    assert g.menu is None
    g.feed(img("after_ok_131638"))
    assert g.menu == "main"


def test_recorded_battle_frames_are_not_menus():
    vids = sorted((HERE.parents[3] / "icebow" / "data" / "overlayed_replays" / "raw").glob("lp_*_0.mp4"))
    if not vids:
        pytest.skip("no recorded live matches on this machine")
    cap, n = cv2.VideoCapture(str(vids[-1])), 0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in range(0, int(total * 0.9), max(1, total // 30)):  # the last 10% may be the (legit) results screen
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, im = cap.read()
        if ok:
            n += 1
            assert CLF.classify(im)["screen"] not in fn.MENU_SCREENS, i
    assert n >= 20


def test_matches_zero_refused(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["live_play.py", "--training-camp", "--matches", "0"])
    assert lp.main() == 2 and ">= 1" in capsys.readouterr().out
