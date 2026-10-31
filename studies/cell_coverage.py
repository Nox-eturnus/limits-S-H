"""The worst-channel surrogate and its intervals on 100 one-cell channels.

For every design with 100 channels in results/mc_cell_pedestals.json (the 4 K band), over the standard held
voltages of the window (as the margins of studies/cell_margins.py):
  - normality: Shapiro-Wilk on the pedestal at every held voltage (smallest p reported) and on the per-channel
    error (largest deviation from the channel's own line);
  - body of the distribution: two-sample Kolmogorov-Smirnov of the surrogate's per-channel error against the
    100 simulated errors, and their 90th and 99th percentiles;
  - coverage of the 90 % percentile-bootstrap interval of the worst of 10^6 channels, from 20-channel sets
    drawn from the Gaussian fitted to the 100 channels (model study) and from the 100 channels themselves
    (subsample study), with the functions of studies/interval_coverage.py.

Run:  python studies/cell_coverage.py     (about 40 min per design on 8 processes; resumes if interrupted)
Writes results/cell_coverage.{json,md}.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import interval_coverage as CV  # noqa: E402
import cell_margins as CM  # noqa: E402


def body(x, v, rng):
    A = CV.hat(v)
    pc = np.abs(x @ A.T).max(1)
    mu, cov = x.mean(0), np.cov(x, rowvar=False)
    syn = np.abs(rng.multivariate_normal(mu, cov, 200_000) @ A.T).max(1)
    return {"shapiro_p_pedestal_min": float(min(stats.shapiro(x[:, j]).pvalue for j in range(x.shape[1]))),
            "shapiro_p_per_channel": float(stats.shapiro(pc).pvalue),
            "ks_p": float(stats.ks_2samp(syn, pc).pvalue),
            "p90_surrogate": float(np.quantile(syn, 0.9)), "p90_spice": float(np.quantile(pc, 0.9)),
            "p99_surrogate": float(np.quantile(syn, 0.99)), "p99_spice": float(np.quantile(pc, 0.99))}


def main():
    recs = json.loads((OUT / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    ckpt = OUT / "cell_coverage_partial.jsonl"      # finished designs, so an interrupted run resumes
    out = dict(json.loads(l) for l in ckpt.read_text(encoding="utf-8").splitlines()) if ckpt.exists() else {}
    for name, r in recs.items():
        if len(r["peds"]) < 100 or name in out:
            continue
        # the standard held voltages of the window, as for the margins of residual6 (the fine grid serves the moves)
        x, v, std, _, _ = CM.prepare(r)
        x, v = x[:, std], v[std]
        rec = {"v": v.tolist(), "peds": x.tolist(), "ok": [True] * len(v)}
        res = CV.study(name, rec)
        res["body"] = body(x, v, np.random.default_rng(8))
        cov = {}
        for kind in ("model", "subsample"):
            c, lo, hi = CV.coverage(res[kind], res["truth_100"], "percentile")
            est = np.array([q["est"] for q in res[kind]])
            cov[kind] = {"coverage": c, "error_interval_too_low": lo, "error_interval_too_high": hi,
                         "median_bias": float(np.median(est) / res["truth_100"] - 1)}
        res["coverage"] = cov
        out[name] = res
        with ckpt.open("a", encoding="utf-8") as f:
            f.write(json.dumps([name, res]) + "\n")
        print(name, json.dumps(res["body"]), json.dumps(cov), flush=True)
    (OUT / "cell_coverage.json").write_text(json.dumps(out), encoding="utf-8")
    ckpt.unlink(missing_ok=True)
    L = ["## Surrogate and interval checks on 100 one-cell channels", "",
         "| design | Shapiro p (pedestal, min over V) | Shapiro p (per-channel error) | KS p | p90 surrogate / SPICE (µV) | "
         "p99 surrogate / SPICE (µV) | coverage model (too low / too high) | coverage subsample (too low / too high) |",
         "|---|---|---|---|---|---|---|---|"]
    for name, r in out.items():
        b, c = r["body"], r["coverage"]
        L.append(f"| {name} | {b['shapiro_p_pedestal_min']:.2f} | {b['shapiro_p_per_channel']:.2f} | {b['ks_p']:.2f} | "
                 f"{b['p90_surrogate'] * 1e6:.1f} / {b['p90_spice'] * 1e6:.1f} | {b['p99_surrogate'] * 1e6:.1f} / "
                 f"{b['p99_spice'] * 1e6:.1f} | " + " | ".join(
                     f"{c[k]['coverage']:.2f} ({c[k]['error_interval_too_low']:.2f} / {c[k]['error_interval_too_high']:.2f})"
                     for k in ("model", "subsample")) + " |")
    (OUT / "cell_coverage.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
