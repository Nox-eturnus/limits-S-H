"""Tail optimism of the Gaussian surrogate in every design and band where it was measured.

For each design and band the tail optimism tau is the largest ratio of the simulated to the predicted largest
deviation, minus one, at the two scales that bracket the depth of the worst of 10^6 channels (s = 2.5 and 3, 4.6
and 5.5 sigma). Runs: the TG at 300 K and in the 4 K band with the larger threshold shift (studies/mc_cell_tg.py),
the TG and the bootstrapped switch in the 4 K band (studies/scaled_sigma_capacitance.py) and the NMOS switch
(studies/scaled_sigma_nmos.py).

Run:  python studies/tail_optimism.py     (seconds; writes results/tail_optimism.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import cell_margins as CM  # noqa: E402
import scaled_sigma_capacitance as A7  # noqa: E402

TG, BOOT = A7.TG, A7.BOOT
SCALES = (1.5, 2.0, 2.5, 3.0)
DEEP = ("2.5", "3")


def peds():
    r = {}
    for f in (ROOT / "results" / "mc_cell_pedestals.json", ROOT / "results" / "mc_cell_extra_pedestals.json", OUT / "mc_cell_tg_pedestals.json"):
        r.update(json.loads(f.read_text(encoding="utf-8")))
    return r


def sss(recs, design, base_cond, scaled_prefix):
    base = recs[f"{design}|{base_cond}"]
    vb = np.round(np.asarray(base["v"]), 3)
    std = CM.standard_mask(vb, vb)
    v = vb[std]
    trk1 = np.abs(np.asarray(base["track"])[:, std]) < A7.TOL
    win1 = trk1.all(0) & np.asarray(base["ok_nominal"])[std]
    x1 = np.asarray(base["peds"])[:, std][:, win1]
    mu, cov = x1.mean(0), np.cov(x1, rowvar=False)
    rng = np.random.default_rng(9)
    z = rng.multivariate_normal(np.zeros(len(mu)), cov, 200_000)
    q20 = stats.norm.ppf(0.5 ** (1 / 20))
    out = {}
    for s in (1.0,) + SCALES:
        r = base if s == 1.0 else recs.get(f"{design}|{scaled_prefix}, mismatch x {s:g}")
        if r is None:
            continue
        vv = np.round(np.asarray(r["v"]), 3)
        sel = np.isin(vv, v)
        p, t = np.asarray(r["peds"])[:, sel], np.abs(np.asarray(r["track"])[:, sel]) < A7.TOL
        if s == 1.0 and len(p) > 20:
            p, t = p[:20], t[:20]
        win = t.all(0)
        common_w = win1 & win
        e = np.abs(A7.line_resid(p[:, common_w], v[common_w])).max(1)
        idx = [list(np.where(win1)[0]).index(i) for i in np.where(common_w)[0]]
        syn = (mu + s * z)[:, idx]
        pred = float(np.quantile(np.abs(A7.line_resid(syn, v[common_w])).max(1), 0.5 ** (1 / len(p))))
        out[f"{s:g}"] = {"depth_sigma": s * q20, "window_all": [float(v[win].min()), float(v[win].max())],
                         "max_residual": float(e.max()), "surrogate_pred": pred, "ratio": float(e.max()) / pred}
    out["tau"] = max(out[k]["ratio"] for k in DEEP if k in out) - 1
    return out


def nmos_tau():
    """studies/scaled_sigma_nmos.py: the ratio at 4.6 and 5.5 sigma (s = 2.5 and 3)."""
    sc = json.loads((ROOT / "results" / "scaled_sigma_nmos.json").read_text(encoding="utf-8"))["scales"]
    return max(sc[k]["max_residual"] / sc[k]["surrogate_pred"] for k in DEEP) - 1


def main():
    recs = peds()
    a7 = json.loads((ROOT / "results" / "scaled_sigma_capacitance.json").read_text(encoding="utf-8"))["sss"]
    out = {"TG|300 K": sss(recs, TG, "300 K", "300 K"), "TG|4 K high": sss(recs, TG, "4 K high", "4 K high")}
    for lab, rr in (("TG|4 K proxy", a7["TG"]), ("bootstrapped|4 K proxy", a7["bootstrapped"])):
        rr = dict(rr)
        for k, r in rr.items():
            r["ratio"] = r["max_residual"] / r["surrogate_pred"]
        rr["tau"] = max(rr[k]["ratio"] for k in DEEP) - 1
        out[lab] = rr
    try:
        out["NMOS|4 K proxy"] = {"tau": nmos_tau()}
    except Exception as e:                       # sss6.json layout differs: record and fall back to the table value
        out["NMOS|4 K proxy"] = {"tau": None, "error": repr(e)}
    taus = {k: v["tau"] for k, v in out.items() if v.get("tau") is not None}
    out["tau_by_design"] = {"TG": max(v for k, v in taus.items() if k.startswith("TG")),
                            "bootstrapped": taus.get("bootstrapped|4 K proxy"),
                            "NMOS": taus.get("NMOS|4 K proxy"),
                            "not measured": max(taus.values())}
    (OUT / "tail_optimism.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["## Tail optimism of the surrogate (scaled-sigma, 20 channels per scale)", "",
         "| design, band | s | depth (sigma) | window on every channel | largest residual (µV) | surrogate (µV) | ratio |",
         "|---|---|---|---|---|---|---|"]
    for lab, rr in out.items():
        if lab == "tau_by_design" or "tau" not in rr or len(rr) < 3:
            continue
        for s, r in rr.items():
            if s == "tau":
                continue
            L.append(f"| {lab} | {s} | {r['depth_sigma']:.1f} | {r['window_all'][0]:.1f}-{r['window_all'][1]:.1f} V | "
                     f"{r['max_residual'] * 1e6:.1f} | {r['surrogate_pred'] * 1e6:.1f} | {r['ratio']:.3f} |")
    L += ["", "Tail optimism tau at 4.6 to 5.5 sigma: " + ", ".join(f"{k}: {v * 100:.1f} %" for k, v in taus.items()) + ".",
          "By design (largest over bands; designs without a scaled-sigma run take the largest measured value): "
          + ", ".join(f"{k}: {v * 100:.1f} %" for k, v in out["tau_by_design"].items() if v is not None) + "."]
    (OUT / "tail_optimism.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
