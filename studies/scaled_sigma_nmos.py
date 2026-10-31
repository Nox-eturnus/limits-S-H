"""Scaled-sigma check of the NMOS switch with one cell per channel.

20 channels of the NMOS cell in the 4 K band at mismatch scales s = 1, 1.5, 2, 2.5, 3 and 5.3 (studies/mc_cell.py,
set "sss"); the worst of 20 lies about 1.82 s standard deviations of the unscaled mismatch into the tail (worst of
10^6: 4.83; with twice the mismatch: 9.7). For each scale: the window that every channel tracks, the channels that
lose 0.8 and 0.7 V, and the largest deviation of a channel from its own line over the window that the s = 1
channels track, against the prediction of the Gaussian surrogate fitted at s = 1 and scaled by s.

Run:  python studies/scaled_sigma_nmos.py     (seconds; writes results/scaled_sigma_nmos.{json,md})
"""
import json
from pathlib import Path

import numpy as np
from scipy import stats

OUT = Path(__file__).resolve().parents[1] / "results"
DESIGN = "NMOS, 0.3 V underdrive"
SCALES = (1.0, 1.5, 2.0, 2.5, 3.0, 5.3)
TOL = 0.1e-3


def line_resid(x, v):
    X = np.column_stack([np.ones_like(v), v])
    return x - x @ (X @ np.linalg.pinv(X)).T


def main():
    recs = json.loads((OUT / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    base = recs[f"{DESIGN}|4 K proxy"]
    vb = np.round(np.asarray(base["v"]), 3)
    std = np.isclose((vb - 0.3) / 0.1, np.round((vb - 0.3) / 0.1))
    v = vb[std]
    trk1 = np.abs(np.asarray(base["track"])[:, std]) < TOL
    win1 = trk1.all(0) & np.asarray(base["ok_nominal"])[std]
    x1 = np.asarray(base["peds"])[:, std][:, win1]
    mu, cov = x1.mean(0), np.cov(x1, rowvar=False)
    rng = np.random.default_rng(9)
    z = rng.multivariate_normal(np.zeros(len(mu)), cov, 200_000)
    q20 = stats.norm.ppf(0.5 ** (1 / 20))
    out = {"design": DESIGN, "v": v.tolist(), "window_s1": v[win1].tolist(), "scales": {}}
    for s in SCALES:
        r = base if s == 1.0 else recs.get(f"{DESIGN}|4 K, mismatch x {s:g}")
        if r is None:
            continue
        vv = np.round(np.asarray(r["v"]), 3)
        sel = np.isin(vv, v)
        peds, trk = np.asarray(r["peds"])[:, sel], np.abs(np.asarray(r["track"])[:, sel]) < TOL
        top = [float(v[np.where(np.cumprod(t))[0].max()]) if t[0] else 0.0 for t in trk]
        win = trk.all(0)
        common = win1 & win
        e = np.abs(line_resid(peds[:, common], v[common])).max(1)
        idx = [list(np.where(win1)[0]).index(i) for i in np.where(common)[0]]
        syn = (mu + s * z)[:, idx]
        pred = float(np.quantile(np.abs(line_resid(syn, v[common])).max(1), 0.5 ** (1 / len(peds))))
        out["scales"][f"{s:g}"] = {"n": len(peds), "depth_sigma": s * q20, "window_all": [float(v[win].min()), float(v[win].max())],
                                   "lose_0.8": int(sum(t < 0.8 - 1e-9 for t in top)), "lose_0.7": int(sum(t < 0.7 - 1e-9 for t in top)),
                                   "common_window": v[common].tolist(), "max_residual": float(e.max()), "surrogate_pred": pred}
    (OUT / "scaled_sigma_nmos.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = [f"## Scaled-sigma check of {DESIGN}, 4 K band, one cell per channel", "",
         "| s | depth (sigma) | window on every channel | channels losing 0.8 / 0.7 V | common window | largest residual (µV) | surrogate (µV) |",
         "|---|---|---|---|---|---|---|"]
    for s, r in out["scales"].items():
        L.append(f"| {s} | {r['depth_sigma']:.1f} | {r['window_all'][0]:.1f}-{r['window_all'][1]:.1f} V | {r['lose_0.8']} / {r['lose_0.7']} | "
                 f"{min(r['common_window']):.1f}-{max(r['common_window']):.1f} V | {r['max_residual'] * 1e6:.1f} | {r['surrogate_pred'] * 1e6:.1f} |")
    (OUT / "scaled_sigma_nmos.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
