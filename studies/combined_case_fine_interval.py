"""90% interval of the largest move from a tuned level in the combined worst case, from 300 resamples.

Same data, spline, error measure, tail allowance and importance sampling as studies/combined_case_fine_move.py,
whose interval used 50 bootstrap resamples of the 20 channels. Here the resamples are drawn in workers of N with
their own seeds (1601 to 1606, 50 each) and merged with the point value of that study.

Run:  python studies/combined_case_fine_interval.py SEED N     (about 2 h for N = 50; one worker)
      python studies/combined_case_fine_interval.py merge      (writes results/combined_case_fine_interval.json)
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import cell_margins as CM  # noqa: E402
import residual_accounting as RA  # noqa: E402
import tail_corrected as Y8  # noqa: E402

KEY = "bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 20 K), mismatch x 2, tree of one reticle"
H = 0.004
N_BOOT_SAMPLE = 50_000
STEPS = 75                               # moves up to 300 mV
SEEDS = (1601, 1602, 1603, 1604, 1605, 1606)
B = CM.RA.budgets()
TAU = Y8.TAU_MAX
CM.CHUNK = 50_000


def spline_operator(v, vv):
    return CubicSpline(v, np.eye(len(v)), axis=0)(vv)          # (len(vv), len(v)), linear in the data


def curve(x, v, std, b, n, rng, max_steps):
    """Worst-of-10^6 error measure of the change over moves of at most k * H, for k = 1 .. max_steps."""
    A = CM.residual_operator(v, std)
    vv = np.arange(v[0], v[-1] + 1e-9, H)
    S = spline_operator(v, vv) @ A                            # pedestals -> deviation on the fine grid
    mu = x.mean(0)
    r_mu = S @ mu
    ys, ws = [], []
    for p, w in CM.is_samples(x, n, rng):
        d = p @ S.T - r_mu
        run = np.zeros((len(p), max_steps), dtype=np.float32)
        best = np.zeros(len(p))
        for k in range(1, max_steps + 1):
            e = RA._mixed((r_mu[k:] - r_mu[:-k]) * (1 + TAU), (d[:, k:] - d[:, :-k]) * (1 + TAU), b).max(1)
            best = np.maximum(best, e)
            run[:, k - 1] = best
        ys.append(run)
        ws.append(w)
    y, w = np.concatenate(ys), np.concatenate(ws)
    q = np.empty(max_steps)
    for k in range(max_steps):
        o = np.argsort(y[:, k])[::-1]
        q[k] = np.interp(1 - CM.Q_WORST, np.cumsum(w[o]) / len(y), y[o, k])
    return q


def dmax(q):
    ok = np.where(q <= 1)[0]
    if len(ok) == 0:                       # below one step: the first step scaled (the change is linear there)
        return H / q[0]
    k = ok[-1]
    if k == len(q) - 1:
        return (k + 1) * H
    return (k + 1) * H + H * (1 - q[k]) / (q[k + 1] - q[k])   # linear between steps


def worker(seed, n):
    rec = json.loads((ROOT / "results" / "mc_cell_combined_fine_pedestals.json").read_text(encoding="utf-8"))[KEY]
    x, v, std, nominal, _ = CM.prepare(rec)
    rng = np.random.default_rng(seed)
    b = B[common.WORST]
    boots = []
    for i in range(n):
        xb = x[rng.integers(0, len(x), len(x))]
        boots.append(dmax(curve(xb, v, std, b, N_BOOT_SAMPLE, rng, STEPS)))
        print(seed, i, boots[-1], flush=True)
    (OUT / f"fine_interval_resamples_{seed}.json").write_text(json.dumps(boots), encoding="utf-8")


def merge():
    boots = []
    for seed in SEEDS:
        boots += json.loads((OUT / f"fine_interval_resamples_{seed}.json").read_text(encoding="utf-8"))
    point = json.loads((ROOT / "results" / "combined_case_fine_move.json").read_text(encoding="utf-8"))[KEY]["99.99"]["dmax_V"]
    out = {"n_boot": len(boots), "point_V": point,
           "ci90_V": [float(np.percentile(boots, 5)), float(np.percentile(boots, 95))],
           "median_V": float(np.percentile(boots, 50)), "seeds": list(SEEDS)}
    print(out)
    (OUT / "combined_case_fine_interval.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1] == "merge":
        merge()
    else:
        worker(int(sys.argv[1]), int(sys.argv[2]))
