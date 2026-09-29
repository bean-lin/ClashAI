"""Hero ability button for live_play.py (MuMu): sensor + actuator + receipt, policy as a pluggable rule.

The generalist has no ability action (neither S1 nor GenModel was trained with one), so -- like play.py (L67ag) --
the press is decided OUTSIDE the model: ``should_press`` is the one hook an RL ability head would replace.
Availability is read from the button's own pixels with play.py's measured classifier
(icebow/src/clashrl/hero_ability.ability_button_state: blue disc = ready, grey = unaffordable, neither = absent),
because the memory reader's verified contract has NO ability availability / cooldown fields.

Calibration: the button centre (0.909, 0.765) of the game frame was MEASURED on Google Play Games (run17, Hough
circle; config.yaml hero.button). MuMu shows the same 9:16 game full-screen, so it maps to (818, 1224) on 900x1600 --
PROVISIONAL until a hero match: while a hero is decked, the first 'ready' and first 'grey' button crops of each
match are saved to ability_crops/ so the position and thresholds can be checked, and every classification is logged.
Screenshots are `adb exec-out screencap` (raw RGBA) on a background thread, only while the deck holds a hero.
"""
from __future__ import annotations

import subprocess
import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "icebow" / "src"))
from clashrl.hero_ability import ability_button_state  # noqa: E402

BUTTON = (0.909, 0.765)            # frame fractions, GPG-measured (config.yaml hero.button)
STATE_RADIUS, BLUE_MIN, GREY_MIN = 0.045, 0.30, 0.35
HERO_FORM = 2                      # reader deck_form_flags: 0 base / 1 evo / 2 hero


def parse_raw_screencap(data: bytes) -> np.ndarray | None:
    """`screencap` raw output -> BGR image. Header = w, h, format (+ colour space on newer Android): its length is
    whatever precedes the w*h*4 RGBA pixels."""
    if len(data) < 12:
        return None
    w, h = int.from_bytes(data[0:4], "little"), int.from_bytes(data[4:8], "little")
    head = len(data) - w * h * 4
    if w <= 0 or h <= 0 or head not in (12, 16):
        return None
    rgba = np.frombuffer(data, np.uint8, offset=head).reshape(h, w, 4)
    return cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGR)


def hero_ids(me: dict) -> set[int]:
    """Card ids my deck holds in HERO form (empty = no hero decked)."""
    return {int(c) for c, f in zip(me.get("deck_card_ids") or [], me.get("deck_form_flags") or []) if int(f) == HERO_FORM}


def should_press(f: dict, side: int, hero_card_ids: set[int], reach_tiles: float = 5.5) -> tuple[bool, str]:
    """PLACEHOLDER policy (the RL ability head's slot): press when an enemy troop is within ``reach_tiles`` of my hero
    (reader positions, 1000 units per tile); if the hero entity cannot be found, when an enemy troop is on my half.
    Deliberately generic -- no per-hero stats -- so it only guarantees the button is USED, not used well."""
    hero = next((e for e in f["entities"] if e["side"] == side and int(e["card_id"]) in hero_card_ids), None)
    foes = [e for e in f["entities"] if e["side"] != side and int(e["card_id"]) >= 0]
    if hero is not None:
        d = min((((e["x"] - hero["x"]) ** 2 + (e["y"] - hero["y"]) ** 2) ** 0.5 / 1000 for e in foes), default=99.0)
        return d <= reach_tiles, f"nearest_enemy_to_hero={d:.1f}t"
    mine_half = [e for e in foes if (e["y"] > 16000) == (side == 1)]
    return bool(mine_half), f"hero_unseen enemies_on_my_half={len(mine_half)}"


class HeroButton:
    def __init__(self, adb: list[str], w: int, h: int, crops_dir: Path, period_s: float = 0.5):
        self.adb, self.w, self.h, self.period = adb, w, h, period_s
        self.point = (round(BUTTON[0] * w), round(BUTTON[1] * h))
        self.crops = crops_dir
        self.want = False                       # set by the controller: a hero is decked this match
        self.state, self.blue, self.grey, self.ts = "absent", 0.0, 0.0, 0.0
        self.saved: set[str] = set()
        self._stop = False
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self) -> None:
        while not self._stop:
            if not self.want:
                time.sleep(0.2)
                continue
            t0 = time.time()
            try:
                raw = subprocess.run(self.adb + ["exec-out", "screencap"], capture_output=True, timeout=5).stdout
                img = parse_raw_screencap(raw)
            except Exception:                   # noqa: BLE001 -- a missed grab is a missed reading, not a crash
                img = None
            if img is not None:
                st, b, g = ability_button_state(img, BUTTON, STATE_RADIUS, BLUE_MIN, GREY_MIN)
                self.state, self.blue, self.grey, self.ts = st, b, g, time.time()
                if st in ("ready", "grey") and st not in self.saved:     # calibration evidence, once per state
                    self.crops.mkdir(parents=True, exist_ok=True)
                    x, y, r = self.point[0], self.point[1], int(0.08 * self.w)
                    cv2.imwrite(str(self.crops / f"{time.strftime('%Y%m%d_%H%M%S')}_{st}.png"),
                                img[max(0, y - r):y + r, max(0, x - r):x + r])
                    self.saved.add(st)
            time.sleep(max(0.0, self.period - (time.time() - t0)))

    def fresh_state(self, max_age_s: float = 1.0) -> str:
        return self.state if time.time() - self.ts <= max_age_s else "stale"

    def tap(self) -> None:
        subprocess.run(self.adb + ["shell", f"input tap {self.point[0]} {self.point[1]}"], capture_output=True,
                       timeout=5)

    def new_match(self) -> None:
        self.saved.clear()

    def stop(self) -> None:
        self._stop = True


if __name__ == "__main__":          # self-check: raw parse + placeholder policy (no device needed)
    img = np.zeros((1600, 900, 4), np.uint8)
    img[..., 2] = 255                                   # pure blue in RGBA
    for head in (12, 16):
        raw = (900).to_bytes(4, "little") + (1600).to_bytes(4, "little") + bytes(head - 8) + img.tobytes()
        bgr = parse_raw_screencap(raw)
        assert bgr.shape == (1600, 900, 3) and bgr[0, 0].tolist() == [255, 0, 0]
    assert ability_button_state(parse_raw_screencap(raw), BUTTON, STATE_RADIUS, BLUE_MIN, GREY_MIN)[0] == "ready"
    me = {"deck_card_ids": [26000000, 26000014], "deck_form_flags": [0, 2]}
    assert hero_ids(me) == {26000014}
    ent = lambda s, x, y, c: {"side": s, "x": x, "y": y, "card_id": c}  # noqa: E731
    f = {"entities": [ent(1, 9000, 24000, 26000014), ent(0, 9000, 20000, 26000000), ent(0, 9000, 3000, -1)]}
    assert should_press(f, 1, {26000014})[0] is True                  # enemy 4 tiles from my hero
    f["entities"][1]["y"] = 10000
    assert should_press(f, 1, {26000014})[0] is False                 # enemy 14 tiles away
    assert should_press({"entities": [ent(0, 9000, 20000, 1)]}, 1, {26000014})[0] is True   # hero unseen, foe on my half
    print("hero_button self-check OK; MuMu button point", (round(BUTTON[0] * 900), round(BUTTON[1] * 1600)))
