"""Crop the ladder-nav templates from raw 900x1600 captures (2026-10-02, MuMu, CR 160402012). Re-run after a UI change."""
import json
from pathlib import Path
import cv2
H = Path(__file__).resolve().parent
RAW = H.parent / "raw"
# name: (source, box x0 y0 x1 y1, search region, threshold)
SPEC = {
    "play_again": ("res_8.png", (195, 1408, 425, 1500), (100, 1300, 520, 1600), 0.85),
    "results_ok": ("res_8.png", (478, 1408, 705, 1500), (380, 1300, 800, 1600), 0.85),
    "winner":     ("res_8.png", (330, 152, 570, 196), (150, 60, 750, 1000), 0.80),   # y of the match = who won
    "battle":     ("main4.png", (345, 1180, 575, 1258), (250, 1100, 650, 1400), 0.85),
    "daily_bonus": ("main4.png", (335, 1268, 600, 1318), (250, 1200, 650, 1400), 0.85),
    "red_x":      ("promo_pass_x.png", (782, 197, 833, 248), (560, 60, 900, 600), 0.85),
    "modes_hdr":  ("trophy_btn.png", (240, 330, 660, 400), (150, 250, 750, 500), 0.85),
    "logo":       ("queue1.png", (180, 60, 710, 260), (100, 0, 800, 360), 0.80),
}
man = {}
for n, (src, b, reg, thr) in SPEC.items():
    img = cv2.imread(str(RAW / src))
    cv2.imwrite(str(H / f"{n}.png"), img[b[1]:b[3], b[0]:b[2]])
    man[n] = {"file": f"{n}.png", "source": src, "box": b, "region": reg, "threshold": thr}
(H / "manifest.json").write_text(json.dumps({"frame": [900, 1600], "templates": man}, indent=1))
print("built", len(man))
