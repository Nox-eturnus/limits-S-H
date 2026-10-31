"""Scaled-sigma check of the TG and the bootstrapped switch, and sensitivity to the device capacitances.

  Scaled sigma      as studies/scaled_sigma_nmos.py for the NMOS switch: the window that every channel tracks and
                    the largest deviation of a channel from its own line, against the Gaussian surrogate fitted
                    at s = 1 and scaled by s (runs of studies/mc_cell_extra.py, set "sss").
  Capacitances      margins with the overlap or junction capacitances scaled by 0.7 and 1.3 (closed-form margin
                    of studies/array_yield.py, which reproduces the sampled surrogate to 1 %), with the curvature
                    of the mean pedestal (runs of studies/mc_cell_extra.py, set "cap").

Run:  python studies/scaled_sigma_capacitance.py     (about a minute; writes results/scaled_sigma_capacitance.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import cell_margins as CM  # noqa: E402
import array_yield as Y  # noqa: E402

TG, BOOT = "TG, no ESD", "bootstrapped (transistor level), 0.3 V underdrive"
TOL = 0.1e-3


def peds():
    r6 = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    r7 = json.loads((OUT / "mc_cell_extra_pedestals.json").read_text(encoding="utf-8"))
    return {**r6, **r7}


def line_resid(x, v):
    X = np.column_stack([np.ones_like(v), v])
    return x - x @ (X @ np.linalg.pinv(X)).T


def sss(recs, design, scales):
    base = recs[f"{design}|4 K proxy"]
    vb = np.round(np.asarray(base["v"]), 3)
    std = CM.standard_mask(vb, vb)
    v = vb[std]
    trk1 = np.abs(np.asarray(base["track"])[:, std]) < TOL
    win1 = trk1.all(0) & np.asarray(base["ok_nominal"])[std]
    x1 = np.asarray(base["peds"])[:, std][:, win1]
    mu, cov = x1.mean(0), np.cov(x1, rowvar=False)
    rng = np.random.default_rng(9)
    z = rng.multivariate_normal(np.zeros(len(mu)), cov, 200_000)
    q20 = stats.norm.ppf(0.5 ** (1 / 20))
    out = {}
    for s in (1.0,) + scales:
        r = base if s == 1.0 else recs.get(f"{design}|4 K, mismatch x {s:g}")
        if r is None:
            continue
        vv = np.round(np.asarray(r["v"]), 3)
        sel = np.isin(vv, v)
        p, t = np.asarray(r["peds"])[:, sel], np.abs(np.asarray(r["track"])[:, sel]) < TOL
        if s == 1.0 and len(p) > 20:            # the 100-channel run: compare the first 20 channels, as at s > 1
            p, t = p[:20], t[:20]
        win = t.all(0)
        common_w = win1 & win
        e = np.abs(line_resid(p[:, common_w], v[common_w])).max(1)
        idx = [list(np.where(win1)[0]).index(i) for i in np.where(common_w)[0]]
        syn = (mu + s * z)[:, idx]
        pred = float(np.quantile(np.abs(line_resid(syn, v[common_w])).max(1), 0.5 ** (1 / len(p))))
        lost = [float(v[j]) for j in range(len(v)) if win1[j] and not win[j]]
        out[f"{s:g}"] = {"n": len(p), "depth_sigma": s * q20, "window_all": [float(v[win].min()), float(v[win].max())],
                         "voltages_lost": lost, "max_residual": float(e.max()), "surrogate_pred": pred}
    return out


def capsens(recs, B):
    designs = ("NMOS, 0.3 V underdrive", BOOT, "TG + dummies", TG)
    out = {}
    for d in designs:
        rows = {}
        for cond in ("4 K proxy", "4 K, overlap capacitances x 0.7", "4 K, overlap capacitances x 1.3",
                     "4 K, junction capacitances x 0.7", "4 K, junction capacitances x 1.3"):
            r = recs.get(f"{d}|{cond}")
            if r is None:
                continue
            x, v, std, nominal, _ = CM.prepare(r)
            if cond == "4 K proxy" and len(x) > 20:
                x = x[:20]
            A = CM.residual_operator(v, std)
            row = {"n": len(x), "window": [float(v.min()), float(v.max())],
                   "curvature_max": float(np.abs((A @ x.mean(0))[std]).max())}
            for key in (common.WORST, "s33.69_t0.001"):
                for kind in ("full", "shared"):
                    m, s = Y.moments(x, v, std, A, nominal, kind)
                    row[f"{key}|{kind}"] = {"margin": Y.margin_closed(m, s, B[key]),
                                            "p_array": Y.p_array(Y.p_channel(m, s, B[key])[0])}
            rows[cond] = row
        out[d] = rows
    return out


def main():
    recs = peds()
    B = CM.RA.budgets()
    out = {"sss": {"TG": sss(recs, TG, (1.5, 2.0, 2.5, 3.0)), "bootstrapped": sss(recs, BOOT, (1.5, 2.0, 2.5, 3.0))},
           "capsens": capsens(recs, B)}
    (OUT / "scaled_sigma_capacitance.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    W = common.WORST
    L = ["## Scaled-sigma check (4 K band, 20 channels per scale)", "",
         "| design | s | depth (sigma) | window on every channel | voltages lost | largest residual (µV) | surrogate (µV) |",
         "|---|---|---|---|---|---|---|"]
    for lab, rr in out["sss"].items():
        for s, r in rr.items():
            L.append(f"| {lab} | {s} | {r['depth_sigma']:.1f} | {r['window_all'][0]:.1f}-{r['window_all'][1]:.1f} V | "
                     f"{', '.join(f'{x:.1f}' for x in r['voltages_lost']) or '–'} | {r['max_residual'] * 1e6:.1f} | {r['surrogate_pred'] * 1e6:.1f} |")
    L += ["", "## Capacitance sensitivity (4 K band, 20 channels; closed-form margins at the strictest point)", "",
          "| design | condition | window | curvature of the mean channel (µV) | per channel | P(array) | shared | 99.9 %, per channel |",
          "|---|---|---|---|---|---|---|---|"]
    for d, rows in out["capsens"].items():
        for c, r in rows.items():
            L.append(f"| {d} | {c} | {r['window'][0]:.1f}-{r['window'][1]:.1f} | {r['curvature_max'] * 1e6:.1f} | "
                     f"{r[f'{W}|full']['margin']:.2f} | {r[f'{W}|full']['p_array']:.1e} | {r[f'{W}|shared']['margin']:.2f} | "
                     f"{r['s33.69_t0.001|full']['margin']:.2f} |")
    (OUT / "scaled_sigma_capacitance.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("written results_analyse7.md")


if __name__ == "__main__":
    main()
