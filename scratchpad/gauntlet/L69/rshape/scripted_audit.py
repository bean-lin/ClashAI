"""R2 pre-flight 3 (reward_plan.md §3.3): per-decision shaped returns of scripted policies. No degenerate policy may
have a higher mean than the IL policy.

    research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L69/rshape/scripted_audit.py \
        --out scratchpad/gauntlet/L69/rshape/audit_M --matches M --w-tower W --w-crown W [--gamma 0.999] \
        [--lams 1.0,0.95] [--policies il,never,...] [--workers 2] [--threads 2] [--smoke]

Every policy (common.POLICIES) plays the same seeds (same opponent deck, side, deal). Per decision t of a match with
T decisions and outcome z (+1 / -1 / 0): r_t = F_t + [t == T-1] z, G_t = sum_k (gamma lam)^(k-t) r_k: the lambda-return
with NO critic (V = 0); lam 1 = the plain return-to-go the plan specifies. Split G_t = terminal part
z (gamma lam)^(T-1-t) + shaping part (at lam 1 exactly -Phi(s_t), reward_shaping docstring). "Advantage" = G_t minus
ONE baseline, the decision-pooled mean G over every policy's decisions (a constant, so the ranking is the ranking of
mean G). Rankings reported for G (R1+R2), the terminal part alone (R1) and the shaping part alone; flags = any
degenerate policy whose decision-pooled mean G beats il's, per lam. Also paired per seed vs il (per-match mean G).
Writes <out>/audit.json; exit 2 when a flag fires at the first lam (default 1, the plan's rule).

CAVEAT (read before trusting the verdict): the shaping part of G_t is -Phi(s_t) -- it is HIGHER when we are behind.
A policy that sits behind all match gets a shaping bonus on every decision without any action having earned it; in
expectation it is a state-only baseline (no policy-gradient bias), but it moves this audit's MEAN. Read the
terminal-only and shaping-only rankings next to the combined one. lam < 1 (V = 0) is the action-dependent view: its
shaping part is ~ the potential GAINED over the next ~1/(1 - gamma lam) decisions (lam 0.95: ~20 decisions = 10 s),
i.e. what a short-horizon GAE would credit the shaping for; there the terminal part reaches only the last decisions.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C                                   # noqa: E402
from pipeline import reward_shaping as RS            # noqa: E402


def main() -> int:
    ap = C.cli(__doc__)
    ap.add_argument("--w-tower", type=float, required=True, help="from magnitude_budget.py's proposal")
    ap.add_argument("--w-crown", type=float, required=True)
    ap.add_argument("--gamma", type=float, default=0.999, help="per decision")
    ap.add_argument("--lams", default="1.0,0.95", help="lambda-returns with V = 0; the first is the verdict's")
    ap.add_argument("--policies", default=",".join(C.POLICIES))
    a = ap.parse_args()
    pols = [p for p in a.policies.split(",") if p]
    if "il" not in pols or any(p not in C.POLICIES for p in pols):
        raise SystemExit(f"--policies must include il and be drawn from {C.POLICIES}")
    g, w, lams = a.gamma, (a.w_tower, a.w_crown), [float(x) for x in a.lams.split(",") if x]

    def reduce(rec: dict) -> dict:
        sh = RS.shaping_terms(rec["_states"], rec["learner_side"], g, w)
        T = len(sh["F"])
        r = list(sh["F"])
        r[-1] += rec["z"]
        keep = ("policy", "seed", "outcome", "z", "crowns_for", "crowns_against", "decisions", "plays_attempted",
                "plays_accepted", "crowns_derivation_mismatch", "wall_s")
        out = {**{k: rec[k] for k in keep}, "F": np.array(sh["F"]), "lam": {}}
        for lam in lams:
            G = np.array(RS.returns_to_go(r, g * lam))
            term = rec["z"] * (g * lam) ** np.arange(T - 1, -1, -1, dtype=np.float64)
            out["lam"][lam] = {"G": G, "term": term, "shape": G - term}
        return out

    rows = C.play_all(a, pols, reduce)
    per = {}
    for p in pols:
        rs = [r for r in rows if r["policy"] == p]
        if not rs:
            continue
        per[p] = {"matches": len(rs), "decisions": int(sum(r["decisions"] for r in rs)),
                  "win": sum(r["outcome"] == "win" for r in rs), "loss": sum(r["outcome"] == "loss" for r in rs),
                  "draw": sum(r["outcome"] == "draw" for r in rs), "z_mean": C.mean(r["z"] for r in rs),
                  "F_mean": float(np.concatenate([r["F"] for r in rs]).mean()),
                  "plays_accepted_mean": C.mean(r["plays_accepted"] for r in rs),
                  "plays_attempted_mean": C.mean(r["plays_attempted"] for r in rs),
                  "crowns_diff_mean": C.mean(r["crowns_for"] - r["crowns_against"] for r in rs)}
    il = {r["seed"]: r for r in rows if r["policy"] == "il"}
    by_lam = {}
    for lam in lams:
        base = float(np.concatenate([r["lam"][lam]["G"] for r in rows]).mean())
        st = {}
        for p in per:
            rs = [r for r in rows if r["policy"] == p]
            G, term, shape = (np.concatenate([r["lam"][lam][k] for r in rs]) for k in ("G", "term", "shape"))
            d = np.array([r["lam"][lam]["G"].mean() - il[r["seed"]]["lam"][lam]["G"].mean() for r in rs
                          if r["seed"] in il])
            sd = float(d.std(ddof=1)) if d.size > 1 else 0.0
            st[p] = {"adv_mean": float(G.mean() - base), "adv_std": float(G.std()), "G_mean": float(G.mean()),
                     "terminal_part_mean": float(term.mean()), "shaping_part_mean": float(shape.mean()),
                     "G_mean_per_match": C.mean(r["lam"][lam]["G"].mean() for r in rs),
                     "paired_vs_il": {"n": int(d.size), "mean": float(d.mean()) if d.size else math.nan,
                                      "t": float(d.mean() / (sd / math.sqrt(d.size))) if sd > 0 else None}}

        def rank(key):
            return sorted(st, key=lambda p: -st[p][key])

        by_lam[str(lam)] = {"baseline_G": base, "rank_G_R1R2": rank("G_mean"),
                            "rank_terminal_R1": rank("terminal_part_mean"), "rank_shaping_only": rank("shaping_part_mean"),
                            "flags_degenerate_above_il": [p for p in st if p != "il" and st[p]["G_mean"] > st["il"]["G_mean"]],
                            "per_policy": st}
    flags = by_lam[str(lams[0])]["flags_degenerate_above_il"]
    C.write(a.out, "audit.json", {
        "gamma": g, "weights": {"w_tower": w[0], "w_crown": w[1]}, "verdict_lam": lams[0],
        "verdict": "STOP: redesign" if flags else "pass", "flags_degenerate_above_il": flags,
        "per_policy": per, "by_lam": by_lam,
        "per_match": [{k: v for k, v in r.items() if k != "lam" and not isinstance(v, np.ndarray)} for r in rows]})
    return 2 if flags else 0


if __name__ == "__main__":
    raise SystemExit(main())
