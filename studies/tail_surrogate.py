"""Worst-of-10^6 margins from a Gaussian surrogate of multi-voltage Monte Carlo decks, with intervals.

Each design's pedestal vector over the held voltages is modelled as multivariate Gaussian, with the mean and
covariance of its Monte Carlo rows. From that model 10^7 synthetic channels are drawn, each calibrated as
in the article:

  per-channel   its own straight line over the held voltages; error = max |deviation|
  shared        the straight line of the nominal cell; error = max |pedestal - line|

so the max-over-voltage and the calibration are applied to every sample rather than assumed Gaussian. The
worst of N channels is the quantile at 0.5^(1/N) of the error distribution (median of the maximum). A
90 % interval comes from a bootstrap over the Monte Carlo rows (resample, refit, redraw; 1000 replicates,
each by importance sampling; its coverage is measured in studies/interval_coverage.py). The expected number
of channels in 10^6 that exceed each budget is also reported. The surrogate is checked on the two designs
with 100 SPICE rows (4 K band): two-sample KS test of the per-channel residuals, 90th and 99th percentiles,
and the 20-row surrogate against the 100-row one.

The rows come from testbenches with one switch instance per held voltage, and the SKY130 mismatch is drawn
per instance (studies/instance_check.py), so a row holds seven independently mismatched cells and its
nonlinearity overstates that of one cell. The margins of the article come from studies/cell_margins.py,
which uses the same surrogate on one cell per channel (studies/mc_cell.py).

Run:  python studies/tail_surrogate.py collect   re-reads the Monte Carlo decks of studies/cells.py (300 K, 9 cells)
                                                 and collects results/tail_surrogate_pedestals.json
      python studies/tail_surrogate.py           analysis (about 5 min on 32 threads)
      python studies/tail_surrogate.py extra     the same for results/extra_bands_pedestals.json
Writes results/tail_surrogate{,_extra}.{json,md}.
"""
import json
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import operational_budget as common  # noqa: E402

PEDS = OUT / "tail_surrogate_pedestals.json"
N_ARRAY = 1e6
N_SAMPLE = 10_000_000
N_BOOT = 1000                           # bootstrap replicates
N_SAMPLE_BOOT = 200_000                 # importance-sampled
S_IS = 1.8
CHUNK = 1_000_000
Q_WORST = 0.5 ** (1 / N_ARRAY)          # median of the max of N channels


def collect():
    """Per-channel pedestals of every design: 300 K nine cells (decks of studies/cells.py, re-read), six designs in
    six bands (results/mismatch_bands_channels.jsonl), and the 100-channel 4 K runs."""
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "studies"))
    from flow import holdstage as H
    from flow import spice
    import mismatch as W
    out = {}
    res = json.loads((ROOT / "results" / "cells.json").read_text(encoding="utf-8"))
    spice.REUSE = True
    real = spice._run

    def no_sim(*a, **k):
        raise RuntimeError("Monte Carlo deck not cached")
    spice._run = no_sim
    try:
        for arch, a in res["archs"].items():
            base = H.HoldConfig(arch=arch, workdir=f"build/cells/{arch}")
            if arch in W.NMOS_ONLY:
                base = replace(base, v_hold=tuple(np.round(np.linspace(0.3, 0.9, 7), 3)))
            peds = []
            for seed in range(1, W.N_MC_D + 1):
                try:
                    peds.append(H.measure(replace(base, mismatch=True, seed=seed))["pedestal"].tolist())
                except Exception as e:
                    print(f"  {arch} seed {seed}: {str(e).splitlines()[0][:80]}", flush=True)
            out[f"{W.ARCH_NAMES[arch]}|300 K (nine cells)"] = {
                "v": list(base.v_hold), "peds": peds, "ok": [True] * len(base.v_hold),
                "nominal": [x * 1e-3 for x in a["nominal"]["pedestal_mv"]]}
    finally:
        spice._run = real
        spice.REUSE = False
    f = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    sw = {(r["design"], r["band"]): r for r in f["switching"] if r and "error" not in r and r["corner"] == "tt"}
    log = {}
    for line in (ROOT / "results" / "mismatch_bands_channels.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if "error" not in r:
            log.setdefault((r["design"], r["band"]), {})[r["seed"]] = r
    for (d, b), rows in log.items():
        nom = sw.get((d, b))
        if not nom:
            continue
        sys.path.insert(0, str(ROOT / "studies"))
        import cryogenic as R
        ok = np.abs(np.array(nom["track_error"], float)) < R.TRACK_TOL
        for tag, seeds in (("", range(1, 21)), (" (100 channels)", range(1, 101))):
            rr = [rows[s] for s in seeds if s in rows]
            if tag and len(rr) < 100:
                continue
            okk = ok & np.all([r["ok"] for r in rr], axis=0)
            out[f"{d}|{b}{tag}"] = {"v": nom["v_hold"], "peds": [r["pedestal"] for r in rr], "ok": okk.tolist(),
                                    "nominal": [x * 1e-3 for x in nom["pedestal_mv"]]}
    PEDS.write_text(json.dumps(out), encoding="utf-8")
    print(f"{len(out)} designs written to {PEDS.name}")


def _fit_matrix(v):
    X = np.column_stack([np.ones_like(v), v])
    return X @ np.linalg.pinv(X)               # hat matrix: fitted = P y


def errors(samples, v, nominal):
    """Per-channel and shared calibration errors for rows of pedestal samples."""
    P = _fit_matrix(v)
    per = np.abs(samples - samples @ P.T).max(axis=1)
    c = np.polyfit(v, nominal, 1)
    shared = np.abs(samples - np.polyval(c, v)).max(axis=1)
    return per, shared


def draw(x, n, rng):
    mu, cov = x.mean(axis=0), np.cov(x, rowvar=False)
    L = np.linalg.cholesky(cov + 1e-30 * np.eye(len(mu)) + np.diag(np.full(len(mu), 1e-24)))
    for i in range(0, n, CHUNK):
        m = min(CHUNK, n - i)
        yield mu + rng.standard_normal((m, len(mu))) @ L.T


def worst(x, v, nominal, n, rng, budgets_v):
    per_all, sh_all = [], []
    for s in draw(x, n, rng):
        p, q = errors(s, v, nominal)
        per_all.append(p)
        sh_all.append(q)
    per, sh = np.concatenate(per_all), np.concatenate(sh_all)
    out = {"per_channel": float(np.quantile(per, Q_WORST)), "shared": float(np.quantile(sh, Q_WORST))}
    out["exceed_per_1e6"] = {k: {"per_channel": float((per > b).mean() * 1e6), "shared": float((sh > b).mean() * 1e6)}
                             for k, b in budgets_v.items()}
    return out, per


def worst_is(x, v, nominal, n, rng):
    """Worst of 10^6 channels, per-channel and shared, by importance sampling: the Gaussian of the
    channels x is sampled with its whitened coordinates widened by S_IS and reweighted. Agrees with
    10^7 plain samples to about 2 % at a fifteenth of the cost (studies/interval_coverage.py)."""
    mu, cov = x.mean(axis=0), np.cov(x, rowvar=False)
    k = len(mu)
    L = np.linalg.cholesky(cov + 1e-30 * np.eye(k) + np.diag(np.full(k, 1e-24)))
    u = rng.standard_normal((n, k)) * S_IS
    w = S_IS ** k * np.exp(-0.5 * (u * u).sum(1) * (1 - 1 / S_IS ** 2))
    per, shared = errors(mu + u @ L.T, v, nominal)
    out = {}
    for key, y in (("per_channel", per), ("shared", shared)):
        o = np.argsort(y)[::-1]
        out[key] = float(np.interp(1 - Q_WORST, np.cumsum(w[o]) / n, y[o]))
    return out


def analyse_one(args):
    name, rec, budgets_v = args
    v = np.asarray(rec["v"])
    ok = np.asarray(rec["ok"], bool)
    x = np.asarray(rec["peds"])[:, ok]
    v, nominal = v[ok], np.asarray(rec["nominal"])[ok]
    rng = np.random.default_rng(common.name_seed(name))
    main, per = worst(x, v, nominal, N_SAMPLE, rng, budgets_v)
    # percentile bootstrap over the channels; its coverage was measured in studies/interval_coverage.py
    boots = {"per_channel": [], "shared": []}
    for _ in range(N_BOOT):
        xb = x[rng.integers(0, len(x), len(x))]
        w = worst_is(xb, v, nominal, N_SAMPLE_BOOT, rng)
        for k in boots:
            boots[k].append(w[k])
    # the Gaussian extrapolation of studies/mismatch_bands.py, for comparison
    pc_mc, _ = errors(x, v, nominal)
    zN = 4.96                                           # z_N for 10^6 channels (studies/mismatch.py)
    sig = x.std(axis=0, ddof=1).max()
    resid = float(np.abs(nominal - np.polyval(np.polyfit(v, nominal, 1), v)).max())
    out = {"n": len(x), "voltages": int(ok.sum()), **main,
           "ci90": {k: [float(np.quantile(b, 0.05)), float(np.quantile(b, 0.95))] for k, b in boots.items()},
           "gaussian_rev2": {"per_channel": float(pc_mc.mean() + zN * pc_mc.std(ddof=1)), "shared": resid + zN * sig},
           "mc_per_channel": pc_mc.tolist()}
    if len(x) >= 100:                                   # validation of the surrogate on 100 SPICE channels
        ks = stats.ks_2samp(per[:200_000], pc_mc)
        out["validation"] = {"ks_p": float(ks.pvalue),
                             "p90_surrogate": float(np.quantile(per, 0.9)), "p90_spice": float(np.quantile(pc_mc, 0.9)),
                             "p99_surrogate": float(np.quantile(per, 0.99)), "p99_spice": float(np.quantile(pc_mc, 0.99))}
    return name, out


def analyse(peds=PEDS, tag=""):
    recs = json.loads(peds.read_text(encoding="utf-8"))
    bud = common.budgets()
    budgets_v = {f"{k}|{kind}": b[kind] for k, b in bud.items() for kind in ("per_gate", "operational")}
    jobs = [(n, r, budgets_v) for n, r in recs.items() if len(r["peds"]) >= 10]
    with ProcessPoolExecutor(min(32, len(jobs))) as ex:
        res = dict(ex.map(analyse_one, jobs))
    out = {"budgets": bud, "q_worst": Q_WORST, "n_sample": N_SAMPLE, "n_boot": N_BOOT, "designs": res}
    (OUT / f"tail_surrogate{tag}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def classify(lo, hi):
    return "pass" if lo > 1 else "fail" if hi < 1 else "indeterminate"


def table(out, tag=""):
    b = out["budgets"]
    L = ["## Worst-of-10^6 margins from a Gaussian-copula surrogate (10^7 synthetic channels), 90 % bootstrap interval", "",
         "Margin = budget / error of the worst of 10^6 channels (median of the maximum). Budgets (µV): "
         + "; ".join(f"{k}: per gate {v['per_gate'] * 1e6:.0f}, operational {v['operational'] * 1e6:.0f}" for k, v in b.items()),
         "", "Class: pass if the whole 90 % interval is above one, fail if below, otherwise indeterminate. "
         "Exceed: expected number of channels in 10^6 above the budget.", ""]
    for key in (common.WORST, "s33.69_t0.001", common.REF):
        bo = b[key]["operational"]
        L += [f"### Operational budget at {key} ({bo * 1e6:.0f} µV)", "",
              "| design | band | n | per-channel margin [90 % CI] | class | rev. 2 Gaussian | exceed / 10^6 | shared margin [90 % CI] | class | exceed / 10^6 |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for name, r in out["designs"].items():
            d, band = name.split("|")
            pc, sh = r["ci90"]["per_channel"], r["ci90"]["shared"]
            m = bo / r["per_channel"]
            ms = bo / r["shared"]
            ex = r["exceed_per_1e6"][f"{key}|operational"]
            L.append(f"| {d} | {band} | {r['n']} | {m:.2f} [{bo / pc[1]:.2f}, {bo / pc[0]:.2f}] | {classify(bo / pc[1], bo / pc[0])} | "
                     f"{bo / r['gaussian_rev2']['per_channel']:.2f} | {ex['per_channel']:.3g} | "
                     f"{ms:.2f} [{bo / sh[1]:.2f}, {bo / sh[0]:.2f}] | {classify(bo / sh[1], bo / sh[0])} | {ex['shared']:.3g} |")
        L.append("")
    L += ["### Validation on 100 SPICE channels (4 K band)", "",
          "| design | KS p (surrogate vs SPICE per-channel residual) | p90 surrogate / SPICE (µV) | p99 surrogate / SPICE (µV) |",
          "|---|---|---|---|"]
    for name, r in out["designs"].items():
        if "validation" in r:
            v = r["validation"]
            L.append(f"| {name} | {v['ks_p']:.2f} | {v['p90_surrogate'] * 1e6:.1f} / {v['p90_spice'] * 1e6:.1f} | "
                     f"{v['p99_surrogate'] * 1e6:.1f} / {v['p99_spice'] * 1e6:.1f} |")
    (OUT / f"tail_surrogate{tag}.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if "collect" in sys.argv:
        collect()
    elif "extra" in sys.argv:                      # the variants of extra_bands.py
        table(analyse(OUT / "extra_bands_pedestals.json", "_extra"), "_extra")
    else:
        table(analyse())
