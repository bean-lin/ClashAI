"""Scorer validation (L69 reward_plan.md section 7): does the 12-s rollout Scorer rank moves like FULL-MATCH outcomes?

    research/ext/Royale/.venv/Scripts/python.exe scratchpad/gauntlet/L69/scorer_val/validate.py \
        --out scratchpad/gauntlet/L69/scorer_val/run1 --opps gen,s1 --seeds 0:10 --per-match 5 --K 8 \
        [--T 0.5] [--horizon 12] [--topk 4] [--cells 3] [--workers 1] [--threads 2] [--forms-mode base]
    ... validate.py --smoke --out DIR          (gen, seed 0, 2 decisions, K 2)
    ... validate.py --summarise DIR            (re-aggregate DIR/decisions.jsonl)

CPU only. Decisions = N = len(opps) x len(seeds) x per-match.

SAMPLING. Each (opp, seed) is one plain-arm match of pipeline.search_s0 (our gen_v1_s0 icebow at the live rule tau 0.35
vs the frozen gen_v1_s0 on a seeded census deck, or vs S1 on icebow; search_s0.setup_job). Our ELIGIBLE decisions
(>= 1 affordable card) are numbered 0, 1, ...; the evaluated ones are ``--per-match`` indices drawn without
replacement from range(``--max-eligible``) with rng [seed, crc32(opp), 69] (a match that ends first yields fewer).
The match itself always continues with the PLAIN decision, so the evaluation never changes the trajectory.

AT EACH DECISION, candidates = WAIT + search_s0.shortlist (top --topk cards x top --cells cells), as search_s0 does.
  (a) the 12-s horizon score of every candidate: search_s0.Runner.rollout_scores under --rollout-self idle AND policy
      (one rollout pass each), each pass scored by Scorer v1 AND v2 on the SAME fork end states -> 4 scorers
      (v1_idle, v2_idle, v1_policy, v2_policy).
  (b) the outcome of playing the match to the END from each candidate, K times: a fork (search_s0.fork_into) applies the
      candidate, then BOTH sides play on with e1_eval's ``sample`` policy at temperature --T (default 0.5, the RL
      behaviour policy: gate ~ Bernoulli(sigmoid((z - logit(tau)) / T)), card and cell ~ softmax(logits / T); ours tau
      0.35, opponent tau 0.27; the REAL opponent model, not the self-model). Continuation k uses the same behaviour
      seeds for every candidate (common random numbers), so candidate differences are not seed noise.
      Per candidate: win rate (win 1, draw 0.5, loss 0) and mean final crown-tower HP difference (ours - theirs).
PER DECISION, per scorer x outcome (win, hp): Spearman rho over the candidates (average ranks; undefined -> skipped and
counted when either side is constant), top-1 hit (the scorer's argmax -- first max, i.e. WAIT on ties, search_s0's
rule -- is among the candidates with the best outcome), its chance rate (|best set| / n), and the regret (best outcome
- outcome of the scorer's pick). Outcome reliability: split-half Spearman of the outcome itself (even vs odd k) --
the ceiling any scorer can reach at this K. Aggregates: means with percentile-bootstrap 95% CIs over decisions.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[4]
for _p in (REPO, REPO / "icebow" / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from pipeline import search_s0 as S          # noqa: E402
from pipeline import e1_eval as E            # noqa: E402

SCORER_KEYS = ("v1_idle", "v2_idle", "v1_policy", "v2_policy")
OUTCOMES = ("win", "hp")
WIN_VALUE = {"win": 1.0, "draw": 0.5, "loss": 0.0}


# ------------------------------------------------------------------------------------------------------
# statistics (pure numpy; tested on synthetic input)
# ------------------------------------------------------------------------------------------------------
def avg_ranks(x) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(len(x), dtype=np.float64)
    for v in np.unique(x):                       # ties -> their average rank
        idx = x == v
        r[idx] = r[idx].mean()
    return r


def spearman(a, b):
    """Spearman rho with average ranks; None if either side is constant (or < 2 items)."""
    if len(a) < 2:
        return None
    ra, rb = avg_ranks(a), avg_ranks(b)
    if ra.std() == 0 or rb.std() == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


def top1(score, outcome) -> tuple[bool, float, float]:
    """(hit, chance, regret): the scorer's argmax (first max) in the best-outcome set; |best| / n; best - picked."""
    o = np.asarray(outcome, dtype=np.float64)
    pick = int(np.argmax(np.asarray(score, dtype=np.float64)))
    best = o.max()
    return bool(o[pick] == best), float((o == best).sum() / len(o)), float(best - o[pick])


def boot_ci(x, n_boot: int = 2000, seed: int = 0) -> list:
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0:
        return [None, None]
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, len(x), size=(n_boot, len(x)))].mean(axis=1)
    return [round(float(np.percentile(means, 2.5)), 4), round(float(np.percentile(means, 97.5)), 4)]


def per_decision(rec: dict) -> dict:
    """rec: {"scores": {scorer: [per candidate]}, "outcome_k": {"win": [[per k] per cand], "hp": ...}} -> metrics."""
    out = {}
    for o in OUTCOMES:
        ok = np.asarray(rec["outcome_k"][o], dtype=np.float64)            # [n_cands, K]
        mean = ok.mean(axis=1)
        for s in SCORER_KEYS:
            if s not in rec["scores"]:
                continue
            sc = rec["scores"][s]
            hit, chance, regret = top1(sc, mean)
            out[f"{s}|{o}"] = {"rho": spearman(sc, mean), "top1": hit, "chance": chance, "regret": regret}
        out[f"split_half|{o}"] = spearman(ok[:, 0::2].mean(axis=1), ok[:, 1::2].mean(axis=1)) \
            if ok.shape[1] >= 2 else None
    return out


def aggregate(recs: list[dict], n_boot: int = 2000) -> dict:
    recs = [r for r in recs if not r.get("skipped")]
    mets = [per_decision(r) for r in recs]
    agg = {"n_decisions": len(recs)}
    for o in OUTCOMES:
        for s in SCORER_KEYS:
            k = f"{s}|{o}"
            ms = [m[k] for m in mets if k in m]
            if not ms:
                continue
            rho = [m["rho"] for m in ms if m["rho"] is not None]
            t1 = [float(m["top1"]) for m in ms]
            ch = [m["chance"] for m in ms]
            agg[k] = {"n": len(ms), "rho_n": len(rho), "rho_undefined": len(ms) - len(rho),
                      "rho_mean": round(float(np.mean(rho)), 4) if rho else None, "rho_ci95": boot_ci(rho, n_boot),
                      "top1": round(float(np.mean(t1)), 4), "top1_ci95": boot_ci(t1, n_boot),
                      "top1_chance": round(float(np.mean(ch)), 4),
                      "top1_minus_chance_ci95": boot_ci(np.subtract(t1, ch), n_boot),
                      "regret_mean": round(float(np.mean([m["regret"] for m in ms])), 4),
                      "regret_ci95": boot_ci([m["regret"] for m in ms], n_boot)}
        sh = [m[f"split_half|{o}"] for m in mets if m.get(f"split_half|{o}") is not None]
        agg[f"split_half|{o}"] = {"n": len(sh), "rho_mean": round(float(np.mean(sh)), 4) if sh else None,
                                  "rho_ci95": boot_ci(sh, n_boot)}
    return agg


# ------------------------------------------------------------------------------------------------------
# the evaluation
# ------------------------------------------------------------------------------------------------------
class ValRunner(S.Runner):
    """search_s0.Runner whose 'search' arm EVALUATES the chosen eligible decisions and always returns the plain one."""
    eval_idx: frozenset = frozenset()
    K, T = 8, 0.5

    def arm_decide(self, m, ds, arm, p, enc, heads, allowed, plain, st, rng, stalled=False):
        i = st["eligible"] - 1
        if i in self.eval_idx:
            t = time.perf_counter()
            rec = self.evaluate(m, ds, p, enc, heads, allowed)
            rec.update({"eligible_idx": i, "plain": {k: plain[k] for k in ("play", "slot", "cell")},
                        "stalled": bool(stalled), "wall_s": round(time.perf_counter() - t, 1)})
            self.records.append(rec)
            print(f"[val] {m.spec['tag']} dec {i} tick {rec['tick']} n {len(rec['acts'])} "
                  f"rollout {rec['rollout_s']}s cont {rec['cont_s']}s", flush=True)
        return plain

    def evaluate(self, m, ds, p, enc, heads, allowed) -> dict:
        L = m.learner.side
        cands = S.shortlist(self.learner, enc, heads, allowed, self.topk, self.cells)
        acts = [S.WAIT] + cands
        root, n0 = m.env.core.state(), len(m.learner.plays)
        if getattr(self, "v2", None) is None:
            self.v2 = S.make_scorer(m.env, "v2")
        scores, t = {}, time.perf_counter()
        for mode in S.ROLLOUT_SELF:
            self.rollout_self = mode
            ws, sc = self.rollout_scores(m, ds, cands, p)                 # self.scorer = v1
            scores[f"v1_{mode}"] = [ws] + sc
            s0 = self.v2.snapshot(root, L)
            scores[f"v2_{mode}"] = [self.v2.score(s0, self.v2.snapshot(f.env.core.state(), L), S.fork_spent(f.learner, n0))
                                    for f in self.last_forks]
        rollout_s, t = time.perf_counter() - t, time.perf_counter()
        ok = self.continue_to_end(m, ds, acts, p, zlib.crc32(f"{m.spec['tag']}:{int(m.env.tick)}".encode()))
        return {"tag": m.spec["tag"], "opp": m.spec["opp"]["id"], "seed": int(m.spec["seed"]), "tick": int(m.env.tick),
                "p": float(p), "acts": [{k: a[k] for k in ("play", "slot", "cell")} for a in acts],
                "scores": scores, "outcome_k": ok, "K": self.K, "T": self.T,
                "rollout_s": round(rollout_s, 1), "cont_s": round(time.perf_counter() - t, 1)}

    def continue_to_end(self, m, ds, acts, p, seed: int) -> dict:
        """Every act x K: fork, apply the act, both sides play on with the sample policy (T) to the match end, all forks
        in lockstep (one forward per (model, side) per round). -> {"win": [[k] per act], "hp": [[k] per act]}."""
        K, L = self.K, m.learner.side
        blob = m.env.core.save_state()
        forks = [S.fork_into(m, e2, blob) for e2 in self._pool(len(acts) * K)]
        lcfg = {**m.learner.cfg, "policy": "sample", "T": self.T}
        ocfg = {**m.opp.cfg, "policy": "sample", "T": self.T}
        for j, f in enumerate(forks):
            a, k = acts[j // K], j % K
            f.learner.cfg, f.opp.cfg = lcfg, ocfg
            f.learner.rng_behave = np.random.default_rng([seed, k, 0])   # common random numbers across acts
            f.opp.rng_behave = np.random.default_rng([seed, k, 1])
            f.learner.apply(p, a)
        first = [f.opp for f in forks] if m.opp in ds else []           # the opponent decides at the root too
        active = list(forks)
        while True:
            due, first = first, []
            if not due:
                for f in list(active):
                    got = f.due()
                    if got:
                        due += got
                    else:
                        active.remove(f)
                if not due:
                    break
                for s in due:
                    s.prepare()
            groups: dict = {}
            for s in due:
                groups.setdefault((id(s.model), s.side), []).append(s)
            todo = {}
            for sides in groups.values():
                model, c = sides[0].model, sides[0].cfg
                if isinstance(model, E.GenPolicy):
                    enc, heads, pp, hand = model.forward_batch([s.gen_row(model) for s in sides], c["device"])
                else:
                    enc, heads, pp, hand = E.model_forward_batch(model, *zip(*[s._obs for s in sides]), device=c["device"])
                pre = [s.pre(hand[r]) for r, s in enumerate(sides)]
                dec = E.sample_decide_batch(model, enc, heads, pp, np.stack([x[1] for x in pre]),
                                            np.array([x[2] for x in pre], dtype=bool), sides, c)
                todo.update({id(s): (pp[r], dec[r]) for r, s in enumerate(sides)})
            for s in due:
                s.apply(*todo[id(s)])
        win, hp = [], []
        for f in forks:
            st = f.env.core.state()
            win.append(WIN_VALUE[f.env.outcome(L)[0]])
            hp.append(S.tower_hp(st, L) - S.tower_hp(st, 1 - L))
        return {"win": np.reshape(win, (len(acts), K)).tolist(), "hp": np.reshape(hp, (len(acts), K)).tolist()}


_W: dict = {}


def _init(args: dict) -> None:
    S._init_worker(args)
    run = S._W["runner"]
    run.__class__ = ValRunner                        # same object, evaluate-and-play-plain arm_decide
    run.records, run.K, run.T = [], int(args["K"]), float(args["T"])
    _W.update(args=args)


def eval_indices(opp: str, seed: int, per_match: int, max_eligible: int) -> frozenset:
    rng = np.random.default_rng([int(seed), zlib.crc32(opp.encode()), 69])
    return frozenset(int(i) for i in rng.choice(max_eligible, size=min(per_match, max_eligible), replace=False))


def _job(job: tuple) -> list[dict]:
    opp, seed = job
    a, run = _W["args"], S._W["runner"]
    got = S.setup_job(run, S._W["census"], opp, seed)
    if got is None:
        return [{"opp": opp, "seed": seed, "skipped": "no loadable deck"}]
    m, name = got
    run.eval_idx, run.records = eval_indices(opp, seed, a["per_match"], a["max_eligible"]), []
    st = {"eligible": 0, "unsearched": 0}            # the only counters Runner.round touches on this arm
    while len(run.records) < len(run.eval_idx):      # the plain match, until every chosen decision is evaluated
        ds = m.due()
        if not ds:
            break
        run.round(m, ds, "search", st, None)
    return [{**r, "opp_deck_name": name} for r in run.records]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path)
    ap.add_argument("--summarise", type=Path, default=None)
    ap.add_argument("--smoke", action="store_true", help="gen, seed 0, 2 decisions, K 2")
    ap.add_argument("--opps", default="gen,s1")
    ap.add_argument("--seeds", default="0:10")
    ap.add_argument("--per-match", type=int, default=5)
    ap.add_argument("--max-eligible", type=int, default=300)
    ap.add_argument("--K", type=int, default=8)
    ap.add_argument("--T", type=float, default=0.5, help="continuation sampling temperature (e1_eval sample policy)")
    ap.add_argument("--horizon", type=float, default=12.0)
    ap.add_argument("--topk", type=int, default=4)
    ap.add_argument("--cells", type=int, default=3)
    ap.add_argument("--gen", default=S.GEN_CKPT)
    ap.add_argument("--s1", default=S.S1_CKPT)
    ap.add_argument("--tail-cap", type=int, default=7200)
    ap.add_argument("--forms-mode", default="base", choices=("base", "deck"))
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--threads", type=int, default=2)
    a = ap.parse_args(argv)
    if a.summarise:
        recs = [json.loads(x) for x in (a.summarise / "decisions.jsonl").read_text(encoding="utf-8").splitlines() if x]
        agg = aggregate(recs)
        (a.summarise / "summary.json").write_text(json.dumps(agg, indent=1), encoding="utf-8")
        print(json.dumps(agg, indent=1))
        return 0
    if a.smoke:
        a.opps, a.seeds, a.per_match, a.K, a.max_eligible = "gen", "0", 2, 2, 40
    if a.out is None:
        ap.error("--out is required")
    if a.out.exists() and any(a.out.iterdir()):
        raise SystemExit(f"REFUSING: {a.out} exists and is not empty")
    a.out.mkdir(parents=True, exist_ok=True)
    opps, seeds = [x for x in a.opps.split(",") if x], S._range(a.seeds)
    args = {"gen": a.gen, "opp_gen": a.gen, "s1": a.s1, "opps": opps, "threads": a.threads, "tail_cap": a.tail_cap,
            "horizon": a.horizon, "interval": 1, "topk": a.topk, "cells": a.cells, "device": "cpu", "search_min_p": 0.0,
            "rollout_self": "idle", "forms_mode": a.forms_mode, "scorer": "v1", "K": a.K, "T": a.T,
            "per_match": a.per_match, "max_eligible": a.max_eligible}
    (a.out / "run.json").write_text(json.dumps({**args, "gen_sha256": S.sha256(REPO / a.gen),
                                                "s1_sha256": S.sha256(REPO / a.s1),
                                                "started": time.strftime("%Y-%m-%d %H:%M:%S")}, indent=1), encoding="utf-8")
    jobs = [(o, s) for o in opps for s in seeds]
    recs, t0 = [], time.perf_counter()
    fh = (a.out / "decisions.jsonl").open("a", encoding="utf-8")

    def emit(rs):
        for r in rs:
            recs.append(r)
            fh.write(json.dumps(r) + "\n")
        fh.flush()

    if a.workers <= 1:
        _init(args)
        for j in jobs:
            emit(_job(j))
    else:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=(args,)) as pool:
            for rs in pool.imap_unordered(_job, jobs):
                emit(rs)
    fh.close()
    agg = aggregate(recs)
    walls = [r["wall_s"] for r in recs if "wall_s" in r]
    agg["wall_total_s"] = round(time.perf_counter() - t0, 1)
    agg["wall_per_decision_s"] = round(float(np.mean(walls)), 1) if walls else None
    (a.out / "summary.json").write_text(json.dumps(agg, indent=1), encoding="utf-8")
    print(json.dumps(agg, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
