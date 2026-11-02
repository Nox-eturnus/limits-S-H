"""Uncertainty of the tail optimism tau of the Gaussian surrogate (studies/tail_optimism.py).

tau compares the largest deviation among the n = 20 channels simulated with every mismatch coefficient scaled by s
with the median of the largest of n deviations that the surrogate predicts. If the simulated tail is the surrogate tail
scaled by (1 + tau), the observed ratio is (1 + tau) R, with R the largest of n surrogate deviations over its median, so
the 90 % interval of (1 + tau) is [ratio / q95(R), ratio / q05(R)]. The upper end for each design is then applied to
every margin of results/tail_corrected.json to list the verdicts it changes.

Run:  python studies/tail_optimism_interval.py     (writes results/tail_optimism_interval.{json,md})
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
import tail_optimism as A8  # noqa: E402

DEEP = ("2.5", "3")
N_SETS = 20_000


def interval(recs, design, base_cond, scaled_prefix):
    base = recs[f"{design}|{base_cond}"]
    vb = np.round(np.asarray(base["v"]), 3)
    std = CM.standard_mask(vb, vb)
    v = vb[std]
    trk1 = np.abs(np.asarray(base["track"])[:, std]) < A7.TOL
    win1 = trk1.all(0) & np.asarray(base["ok_nominal"])[std]
    x1 = np.asarray(base["peds"])[:, std][:, win1]
    mu, cov = x1.mean(0), np.cov(x1, rowvar=False)
    rng = np.random.default_rng(10)
    out = {}
    for s in DEEP:
        r = recs.get(f"{design}|{scaled_prefix}, mismatch x {s}")
        if r is None:
            continue
        vv = np.round(np.asarray(r["v"]), 3)
        sel = np.isin(vv, v)
        p, t = np.asarray(r["peds"])[:, sel], np.abs(np.asarray(r["track"])[:, sel]) < A7.TOL
        n = len(p)
        common_w = win1 & t.all(0)
        obs = float(np.abs(A7.line_resid(p[:, common_w], v[common_w])).max())
        idx = [list(np.where(win1)[0]).index(i) for i in np.where(common_w)[0]]
        z = rng.multivariate_normal(np.zeros(len(mu)), cov, N_SETS * n)
        syn = (mu + float(s) * z)[:, idx]
        mx = np.abs(A7.line_resid(syn, v[common_w])).max(1).reshape(N_SETS, n).max(1)
        med = float(np.median(mx))
        q05, q95 = np.quantile(mx / med, [0.05, 0.95])
        ratio = obs / med
        out[s] = {"n": n, "ratio": ratio, "tau_point": ratio - 1, "tau_lo": ratio / q95 - 1, "tau_hi": ratio / q05 - 1,
                  "R_q05": float(q05), "R_q95": float(q95)}
    k = max(out, key=lambda s: out[s]["ratio"])
    return {"scales": out, "decisive_scale": k, **{f: out[k][f] for f in ("tau_point", "tau_lo", "tau_hi")}}


def main():
    recs = A8.peds()
    cases = {"TG|300 K": (A7.TG, "300 K", "300 K"), "TG|4 K high": (A7.TG, "4 K high", "4 K high"),
             "TG|4 K proxy": (A7.TG, "4 K proxy", "4 K"), "bootstrapped|4 K proxy": (A7.BOOT, "4 K proxy", "4 K"),
             "NMOS|4 K proxy": ("NMOS, 0.3 V underdrive", "4 K proxy", "4 K")}
    out, L = {}, ["# 90 % interval of the tail optimism tau", "",
                  "| design, band | tau (point estimate) | 90 % interval | spread of the largest of 20 (q05 to q95 of max/median) |",
                  "|---|---|---|---|"]
    for lab, args in cases.items():
        try:
            r = interval(recs, *args)
        except KeyError as e:
            out[lab] = {"error": repr(e)}
            L.append(f"| {lab} | – | missing record {e} | – |")
            continue
        out[lab] = r
        sc = r["scales"][r["decisive_scale"]]
        L.append(f"| {lab} | {r['tau_point'] * 100:.1f} % | {r['tau_lo'] * 100:.1f} to {r['tau_hi'] * 100:.1f} % | "
                 f"{sc['R_q05']:.2f} to {sc['R_q95']:.2f} |")
    hi = max(r["tau_hi"] for r in out.values() if "tau_hi" in r)
    out["tau_hi_max"] = hi
    L += ["", f"Largest upper end: {hi * 100:.1f} %."]
    # verdicts of Table S6 with tau at the largest upper end instead of the measured value
    y8 = json.loads((ROOT / "results" / "tail_corrected.json").read_text(encoding="utf-8"))
    up = {"TG": max(out[k]["tau_hi"] for k in out if k.startswith("TG|")), "bootstrapped": out["bootstrapped|4 K proxy"]["tau_hi"],
          "NMOS": out["NMOS|4 K proxy"]["tau_hi"], "other": hi}
    out["tau_upper_by_design"] = up
    out["verdicts"] = verdicts(y8, up)
    L += ["", "Upper ends applied: " + ", ".join(f"{k} {v * 100:.1f} %" for k, v in up.items()) + ".", "",
          "Verdicts (every margin of results/tail_corrected.json, Table S6 and the variants) that change when each margin is "
          "divided by 1 + the upper end for its design instead of 1 + its measured tau:", ""] + (
        [f"- {c}" for c in out["verdicts"]["changed"]] or ["- none"]) + ["", f"{out['verdicts']['n']} verdicts checked."]
    (OUT / "tail_optimism_interval.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT / "tail_optimism_interval.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


def upper(d, up):
    if d.startswith("TG") and "dummies" not in d and "+" not in d:
        return up["TG"]
    if d.startswith("bootstrapped"):
        return up["bootstrapped"]
    if d.startswith("NMOS"):
        return up["NMOS"]
    return up["other"]


def verdicts(y8, up):
    import array_yield as Y
    import tail_corrected as Y8
    changed, n = [], 0
    for key, r in y8["designs"].items():
        d, c = key.split("|", 1)
        f = (1 + r["tau"]) / (1 + upper(d, up))              # margins and intervals are already divided by 1 + tau
        w = Y.widening(d)
        for kk in r["margin"]:
            if not kk.endswith("|mixed") or "interp" in kk or "win" in kk or kk not in r.get("ci90", {}):
                continue
            lo, hi = r["ci90"][kk]
            old, new = label(lo, hi, w), label(lo * f, hi * f, w)
            n += 1
            if old != new:
                changed.append(f"{d}, {c}, {kk}: {old} -> {new} (margin {r['margin'][kk]:.3g} -> {r['margin'][kk] * f:.3g})")
    return {"n": n, "changed": changed}


def label(lo, hi, w):
    lo = lo / (1 + w)
    return "pass" if lo > 1.1 else "fail" if hi < 0.9 else "unresolved"


if __name__ == "__main__":
    main()
