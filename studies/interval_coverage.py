"""Coverage of the 90 % intervals of the worst-channel surrogate (studies/tail_surrogate.py).

Measures how often the 20-channel interval contains the value it estimates, for two interval methods:

  percentile   resample the Monte Carlo channels, refit mean and covariance, recompute the worst of
               10^6 channels; 5th and 95th percentiles of the replicates
  parametric   draw the covariance from its posterior given the channels, Sigma ~ InvWishart(n - 1,
               (n - 1) S), and the mean from N(xbar, Sigma / n), then recompute; 5th and 95th percentiles

on the two designs with 100 SPICE channels in results/tail_surrogate_pedestals.json (4 K band), in two
studies:

  model        the truth is the Gaussian fitted to the 100 channels; 20-channel sets are drawn from it, so
               the true worst-channel error is known exactly (tests the interval under the Gaussian model)
  subsample    20 of the 100 SPICE channels are drawn without replacement; the reference is the
               100-channel estimate (tests the interval on the simulated channels themselves)

The worst of 10^6 channels (the quantile of the per-channel residual at 0.5^(1/10^6)) is computed by
importance sampling (Gaussian proposal widened by S_IS), which agrees with 10^7 plain samples to about
2 % at a fifteenth of the cost. The functions are reused by studies/cell_coverage.py.

Run:  python studies/interval_coverage.py      (about 40 min on 8 processes; writes results/interval_coverage.{json,md})
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy import stats

OUT = Path(__file__).resolve().parents[1] / "results"
PEDS = OUT / "tail_surrogate_pedestals.json"
DESIGNS = ("bootstrapped (transistor level), 0.3 V underdrive|4 K proxy (100 channels)",
           "TG + dummies|4 K proxy (100 channels)")
Q_WORST = 0.5 ** (1 / 1e6)
S_IS = 1.8
N_IS, N_IS_TRUTH = 100_000, 2_000_000
N_SUB, B, K_MODEL, K_SUB = 20, 200, 200, 150
WORKERS = 8


def hat(v):
    X = np.column_stack([np.ones_like(v), v])
    return np.eye(len(v)) - X @ np.linalg.pinv(X)


def worst_is(mu, cov, A, n, rng):
    """Per-channel worst of 10^6 by importance sampling: proposal N(0, S_IS^2 I) in whitened space."""
    k = len(mu)
    L = np.linalg.cholesky(cov + np.diag(np.full(k, 1e-24)))
    u = rng.standard_normal((n, k)) * S_IS
    w = S_IS ** k * np.exp(-0.5 * (u * u).sum(1) * (1 - 1 / S_IS ** 2))
    y = np.abs((mu + u @ L.T) @ A.T).max(1)
    o = np.argsort(y)[::-1]
    return float(np.interp(1 - Q_WORST, np.cumsum(w[o]) / n, y[o]))


def replicates(x, A, method, rng):
    n, k = x.shape
    xbar, S = x.mean(0), np.cov(x, rowvar=False)
    out = np.empty(B)
    for b in range(B):
        if method == "percentile":
            xb = x[rng.integers(0, n, n)]
            mu, cov = xb.mean(0), np.cov(xb, rowvar=False)
        else:
            cov = stats.invwishart.rvs(df=n - 1, scale=(n - 1) * S, random_state=rng)
            mu = rng.multivariate_normal(xbar, cov / n)
        out[b] = worst_is(mu, cov, A, N_IS, rng)
    return out


def one(args):
    """Point estimate and both replicate sets for one 20-channel set."""
    x, A, seed = args
    rng = np.random.default_rng(seed)
    est = worst_is(x.mean(0), np.cov(x, rowvar=False), A, N_IS, rng)
    return est, replicates(x, A, "percentile", rng), replicates(x, A, "parametric", rng)


def study(name, rec):
    ok = np.asarray(rec["ok"], bool)
    v = np.asarray(rec["v"])[ok]
    x100 = np.asarray(rec["peds"])[:, ok]
    A = hat(v)
    rng = np.random.default_rng(7)
    mu100, cov100 = x100.mean(0), np.cov(x100, rowvar=False)
    truth = worst_is(mu100, cov100, A, N_IS_TRUTH, rng)
    sets = {"model": [rng.multivariate_normal(mu100, cov100, N_SUB) for _ in range(K_MODEL)],
            "subsample": [x100[rng.choice(len(x100), N_SUB, replace=False)] for _ in range(K_SUB)]}
    res = {"truth_100": truth}
    for kind, xs in sets.items():
        with ProcessPoolExecutor(WORKERS) as ex:
            rows = list(ex.map(one, [(x, A, 1000 * i + 17) for i, x in enumerate(xs)]))
        res[kind] = [{"est": e, "percentile": p.tolist(), "parametric": q.tolist()} for e, p, q in rows]
        print(f"{name[:40]} {kind}: done", flush=True)
    return res


def coverage(rows, truth, method, lo=5, hi=95):
    """Fraction of intervals containing the truth, and the fractions missing low (interval below the
    truth) and high."""
    q = np.array([np.percentile(r[method], [lo, hi]) for r in rows])
    below, above = (q[:, 1] < truth).mean(), (q[:, 0] > truth).mean()
    return float(1 - below - above), float(below), float(above)


def main():
    recs = json.loads(PEDS.read_text(encoding="utf-8"))
    out = {name: study(name, recs[name]) for name in DESIGNS}
    (OUT / "interval_coverage.json").write_text(json.dumps(out), encoding="utf-8")
    report(out)


def report(out):
    L = ["## Coverage of the nominal 90 % interval of the worst-channel error, 20 channels", "",
         "Interval contains the reference: coverage; 'error interval too low' means the whole interval lies below "
         "the reference error (margin interval too high). Reference: the 100-channel Gaussian (model study) or the "
         "100-channel estimate (subsample study).", "",
         "| design | study | reference (µV) | median 20-ch estimate (µV) | percentile: coverage / too low / too high | "
         "parametric: coverage / too low / too high |", "|---|---|---|---|---|---|"]
    for name, r in out.items():
        for kind in ("model", "subsample"):
            rows, t = r[kind], r["truth_100"]
            cells = []
            for m in ("percentile", "parametric"):
                c, lo, hi = coverage(rows, t, m)
                cells.append(f"{c:.2f} / {lo:.2f} / {hi:.2f}")
            med = np.median([x["est"] for x in rows])
            L.append(f"| {name.split('|')[0]} | {kind} | {t * 1e6:.1f} | {med * 1e6:.1f} | {cells[0]} | {cells[1]} |")
    (OUT / "interval_coverage.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if "report" in sys.argv:
        report(json.loads((OUT / "interval_coverage.json").read_text(encoding="utf-8")))
    else:
        main()
