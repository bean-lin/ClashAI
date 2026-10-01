"""R2 pre-flight 2 (reward_plan.md §3.2): how loud is each shaping term next to the terminal reward (|z| = 1)?

    research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L69/rshape/magnitude_budget.py \
        --out scratchpad/gauntlet/L69/rshape/budget_100 --matches 100 [--workers 2] [--threads 2] [--smoke]

N IL matches (common.py: gen_v1_s0 plain live condition vs frozen gen_v1 on census decks). Per term (tower, crown,
both at weight 1) and gamma (1, 0.999), per match: |sum_t F_t| (the plan's metric), mean |F_t|, sum |F_t| (total
variation of Phi), mean and max |Phi(s_t)| over decisions (|Phi(s_t)| IS the shaping part of decision t's
return-to-go, reward_shaping docstring); pooled over all decisions: p50/p95/max |Phi(s_t)|.

NOTE on the plan's metric: sum_t gamma^t F_t = -Phi(s_0) exactly, and Phi(s_0) = 0 at a symmetric start, so
|sum F| per match is ~0 at gamma 1 whatever the weights (at gamma < 1 the undiscounted sum is
-(1 - gamma) * sum_{t>=1} Phi(s_t), small). It cannot bound anything. The binding budget used for the proposal is
the per-decision one: p99 over decisions of |Phi(s_t)| (the shaping part of a return-to-go) <= 0.5 x terminal
(p99, not p95: the crown term is 0 on most decisions and jumps by 1/3, so a p95 can miss it entirely).
PROPOSAL RULE: w_tower = w_crown = w (the plan's two formulas share the 1/3-per-tower scale), w = the largest value
<= 1 with p99 |w * (phi_tower + phi_crown)| <= 0.5 ON IL MATCHES. Also reported: the HARD bound. Before the
terminal, |phi_tower| < 1 and |phi_crown| <= 2/3 (3 crowns ends the match), so |Phi| < w * 5/3 on every state any
policy can reach; w = 0.5 / (5/3) = 0.3 keeps the budget everywhere (losing trajectories reach |Phi| ~ 1.65 at
w = 1, measured on never-play). Writes <out>/budget.json.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C                                   # noqa: E402
from pipeline import reward_shaping as RS            # noqa: E402

BUDGET = 0.5
TERMS = {"tower": (1.0, 0.0), "crown": (0.0, 1.0), "both": (1.0, 1.0)}
GAMMAS = (1.0, 0.999)


def reduce(rec: dict) -> dict:
    states, L = rec["_states"], rec["learner_side"]
    out = {"seed": rec["seed"], "outcome": rec["outcome"], "decisions": rec["decisions"],
           "crowns_derivation_mismatch": rec["crowns_derivation_mismatch"], "phi": {}}
    for name, w in TERMS.items():
        ph = np.array([RS.phi(s, L, *w) for s in states])
        out["phi"][name] = ph                         # pooled later (not written per match)
        for g in GAMMAS:
            F = np.array(RS.shaping_terms(states, L, g, w)["F"])
            out[f"{name}|g{g}"] = {"abs_sum_F": float(abs(F.sum())), "mean_abs_F": float(np.abs(F).mean()),
                                   "sum_abs_F": float(np.abs(F).sum())}
        out[f"{name}|phi"] = {"mean_abs_phi": float(np.abs(ph).mean()), "max_abs_phi": float(np.abs(ph).max())}
    return out


def main() -> int:
    a = C.cli(__doc__).parse_args()
    rows = C.play_all(a, ["il"], reduce)
    per_term = {}
    for name in TERMS:
        pooled = np.abs(np.concatenate([r["phi"][name] for r in rows]))
        d = {"pooled_abs_phi": {"p50": float(np.percentile(pooled, 50)), "p95": float(np.percentile(pooled, 95)),
                                "p99": float(np.percentile(pooled, 99)),
                                "max": float(pooled.max())},
             **{k: C.mean(r[f"{name}|phi"][k] for r in rows) for k in ("mean_abs_phi", "max_abs_phi")}}
        for g in GAMMAS:
            d[f"gamma_{g}"] = {k: C.mean(r[f"{name}|g{g}"][k] for r in rows)
                               for k in ("abs_sum_F", "mean_abs_F", "sum_abs_F")}
        per_term[name] = d
    p99 = per_term["both"]["pooled_abs_phi"]["p99"]
    w = min(1.0, BUDGET / p99) if p99 > 0 else 1.0
    s = w                                             # every magnitude above is linear in a common weight
    proposal = {"w_tower": round(w, 4), "w_crown": round(w, 4), "rule": "w_t = w_c, p99 |Phi(s_t)| <= 0.5, w <= 1",
                "at_proposal": {"p99_abs_phi": p99 * s, "max_abs_phi": per_term["both"]["pooled_abs_phi"]["max"] * s,
                                "mean_abs_phi": per_term["both"]["mean_abs_phi"] * s,
                                "mean_abs_sum_F_g0.999": per_term["both"]["gamma_0.999"]["abs_sum_F"] * s,
                                "mean_abs_sum_F_g1": per_term["both"]["gamma_1.0"]["abs_sum_F"] * s,
                                "mean_sum_abs_F_g0.999": per_term["both"]["gamma_0.999"]["sum_abs_F"] * s,
                                "mean_abs_F_g0.999": per_term["both"]["gamma_0.999"]["mean_abs_F"] * s},
                "plan_metric_pass": per_term["both"]["gamma_0.999"]["abs_sum_F"] * s <= BUDGET,
                "per_decision_budget_pass": p99 * s <= BUDGET + 1e-12,
                "hard_bound": {"w_tower": BUDGET / (5 / 3), "w_crown": BUDGET / (5 / 3),
                               "rule": "|Phi| < w * (1 + 2/3) on every pre-terminal state <= 0.5"}}
    for r in rows:
        r.pop("phi")
    C.write(a.out, "budget.json", {
        "matches": len(rows), "terminal_magnitude": 1.0, "budget": BUDGET,
        "wins": sum(r["outcome"] == "win" for r in rows), "losses": sum(r["outcome"] == "loss" for r in rows),
        "decisions_mean": C.mean(r["decisions"] for r in rows),
        "crowns_derivation_mismatch_total": sum(r["crowns_derivation_mismatch"] for r in rows),
        "unweighted": per_term, "proposal": proposal, "per_match": rows})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
