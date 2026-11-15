"""Largest move from a tuned level for the bootstrapped switch in the combined worst case, on the 20 mV grid.

The deviation of each surrogate channel from its per-channel line (fitted at the seven standard voltages) is
evaluated on a cubic spline through the 61 simulated voltages, every H volts, and the change over every move of at
most Delta is judged with the mixed error measure, on the worst of 10^6 channels from the jointly Gaussian surrogate
(importance sampling as studies/cell_margins.py), with the tail allowance of a design without a scaled-sigma run
(9.8%). A 90% interval at the strictest point from N_BOOT bootstrap resamples of the 20 channels. The chord estimate
of studies/tolerated_move.py is recomputed from the standard voltages of the same data as a check.

Run:  python studies/combined_case_fine_move.py     (about 35 min; writes results/combined_case_fine_move.json)
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
import tolerated_move as M13  # noqa: E402

KEY = "bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 20 K), mismatch x 2, tree of one reticle"
H = 0.004
N_POINT, N_BOOT, N_BOOT_SAMPLE = 1_000_000, 50, 50_000
B = CM.RA.budgets()
TARGETS = {"99.99": common.WORST, "99.9": "s33.69_t0.001"}
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


def main():
    rec = json.loads((OUT / "mc_cell_combined_fine_pedestals.json").read_text(encoding="utf-8"))[KEY]
    x, v, std, nominal, _ = CM.prepare(rec)
    print(f"{len(x)} channels, {len(v)} held voltages {v[0]:.2f} to {v[-1]:.2f} V", flush=True)
    rng = np.random.default_rng(15)
    out = {}
    for kn, key in TARGETS.items():
        b = B[key]
        steps = 75                        # moves up to 300 mV
        q = curve(x, v, std, b, N_POINT, rng, steps)
        point = dmax(q)
        print(kn, f"point {point * 1e3:.1f} mV", flush=True)
        boots = []
        for i in range(N_BOOT if kn == "99.99" else 0):     # interval for the strictest point only
            if i % 10 == 0:
                print(f"  bootstrap {i}/{N_BOOT}", flush=True)
            xb = x[rng.integers(0, len(x), len(x))]
            boots.append(dmax(curve(xb, v, std, b, N_BOOT_SAMPLE, rng, steps)))
        sx, sv, sstd = x[:, std], v[std], std[std]
        chord, _ = M13.dmax_mc(sx, sv, sstd, TAU, b)                  # chord estimate of tolerated_move, same data
        out[kn] = {"dmax_V": point, "ci90_V": [float(np.percentile(boots, 5)), float(np.percentile(boots, 95))] if boots else None,
                   "chord_estimate_V": chord, "margin_1mV": float(H / 1e-3 / q[0]) if q[0] > 0 else None,
                   "curve": q.tolist()}
        ci = out[kn]["ci90_V"]
        print(kn, f"Delta_max {point * 1e3:.1f} mV", f"[{ci[0] * 1e3:.1f}, {ci[1] * 1e3:.1f}]" if ci else "",
              f"chord estimate {chord * 1e3:.1f} mV", flush=True)
    (OUT / "combined_case_fine_move.json").write_text(json.dumps({KEY: {"window_V": float(v[-1] - v[0]), **out}}, indent=1),
                                     encoding="utf-8")


if __name__ == "__main__":
    main()
