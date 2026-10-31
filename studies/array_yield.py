"""Probability that an array of 10^6 channels has any channel above the budget, in closed form.

The surrogate of studies/cell_margins.py is a Gaussian with the mean and covariance of the Monte Carlo channels. The
deviation of a channel from its calibration line is linear in its pedestals, so at every held voltage j it is
Gaussian, r_j = r_mu_j + d_j with d_j ~ N(0, s_j^2), and the error measure u_j exceeds one exactly when
|r_mu_j + d_j| > t_j = b_ind sqrt(1 - r_mu_j^2 (b_eq^-2 - b_ind^-2)). The probability that a channel exceeds the budget
at some held voltage is bounded by the sum over voltages (union bound, an upper bound) and by the largest term
(a lower bound); both are computed in closed form, without sampling, so they resolve probabilities far below the
1/10^6 that the importance sampler of cell_margins.py reports as zero. The probability that an array fails is
1 - (1 - p)^N with N = 10^6.

Also computed:
  * a check of the closed form: the budget scale at which P(array) = 1/2 reproduces the median worst channel of
    cell_margins.py (the margin);
  * a 95th percentile of P(array) over 300 bootstrap resamples of the Monte Carlo channels;
  * model-error variants: the mismatch spread scaled by 1.5 and 2, the common (curvature) part scaled by 1.3, and
    both together;
  * the near-one rule applied to every verdict: the error interval's upper end widened by 1.4 % for the
    transmission gates and by 5.3 % for every other design (the largest widening measured in
    studies/cell_coverage.py), and a verdict whose widened interval reaches one is near one.

Run:  python studies/array_yield.py     (about 40 s; writes results/array_yield.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.special import log_ndtr

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import cell_margins as CM  # noqa: E402

N = 1e6
N_BOOT = 300
KEYS = (common.WORST, "s33.69_t0.001", common.REF)
VARIANTS = {"model": (1.0, 1.0), "mismatch x 1.5": (1.5, 1.0), "mismatch x 2": (2.0, 1.0),
            "curvature x 1.3": (1.0, 1.3), "mismatch x 2, curvature x 1.3": (2.0, 1.3)}


def widening(design):
    return 0.014 if design.startswith("TG") and "dummies" not in design and "+" not in design else 0.053


def log_p_exceed(m, s, t):
    """log P(|m + d| > t) for d ~ N(0, s^2), elementwise; t <= 0 means certain failure."""
    s = np.maximum(s, 1e-30)
    with np.errstate(divide="ignore"):
        a = log_ndtr((m - t) / s)
        b = log_ndtr((-t - m) / s)
    lp = np.logaddexp(a, b)
    return np.where(t <= 0, 0.0, lp)


def p_channel(m, s, b, scale=1.0):
    """Union-bound and max-term probability that one channel exceeds the budget at some held voltage."""
    be, bi = b["b_eq"] * scale, b["b_ind"] * scale
    arg = 1 - m ** 2 * (be ** -2 - bi ** -2)
    t = bi * np.sqrt(np.clip(arg, 0, None))
    t = np.where(arg <= 0, 0.0, t)
    lp = log_p_exceed(m, s, t)
    return float(min(1.0, np.exp(lp).sum())), float(np.exp(lp.max()))


def p_array(p):
    return float(-np.expm1(N * np.log1p(-min(p, 1 - 1e-16)))) if p < 1 else 1.0


def moments(x, v, std, A, nominal, kind):
    """Mean m and standard deviation s of the deviation at the standard held voltages."""
    mu = x.mean(0)
    C = np.cov(x, rowvar=False)
    if kind == "full":
        m = (A @ mu)[std]
        s = np.sqrt(np.clip(np.diag(A @ C @ A.T), 0, None))[std]
    else:                                                    # shared calibration: the line of the nominal cell
        line = np.polyval(np.polyfit(v[std], nominal[std], 1), v)
        m = (mu - line)[std]
        s = np.sqrt(np.clip(np.diag(C), 0, None))[std]
    return m, s


def margin_closed(m, s, b):
    """Budget scale c at which P(array) = 1/2 (union bound): the closed-form margin is 1/c."""
    lo, hi = 1e-4, 1e4
    for _ in range(80):
        c = np.sqrt(lo * hi)
        if p_array(p_channel(m, s, b, c)[0]) > 0.5:
            lo = c
        else:
            hi = c
    return 1 / np.sqrt(lo * hi)


def analyse(name, rec, B, rng):
    x, v, std, nominal, _ = CM.prepare(rec)
    A = CM.residual_operator(v, std)
    out = {"n": len(x)}
    for kind in ("full", "shared"):
        m, s = moments(x, v, std, A, nominal, kind)
        for key in KEYS:
            b = B[key]
            row = {}
            for vn, (fs, fm) in VARIANTS.items():
                pu, pl = p_channel(m * fm, s * fs, b)
                row[vn] = {"p_channel_union": pu, "p_channel_max": pl, "p_array": p_array(pu), "p_array_lower": p_array(pl)}
            row["margin_closed"] = margin_closed(m, s, b)
            boots = []
            for _ in range(N_BOOT if key == common.WORST else 0):
                xb = x[rng.integers(0, len(x), len(x))]
                mb, sb = moments(xb, v, std, A, nominal, kind)
                boots.append(p_array(p_channel(mb, sb, b)[0]))
            if boots:
                row["p_array_boot95"] = float(np.quantile(boots, 0.95))
            out[f"{key}|{kind}"] = row
    return out


def near_one(r6):
    out = []
    for name, r in r6["designs"].items():
        d, cond = name.split("|")
        w = widening(d)
        for key in KEYS:
            for kind in ("full", "shared"):
                k = f"{key}|{kind}|mixed"
                if k not in r["margin"]:
                    continue
                lo, hi = r["ci90"][k]
                cls = CM.classify(lo, hi)
                cls_w = "pass" if lo / (1 + w) > 1 else "fail" if hi < 1 else "near one"
                if cls != cls_w:
                    out.append({"design": d, "cond": cond, "key": key, "kind": kind, "margin": r["margin"][k],
                                "ci90": [lo, hi], "widening": w, "class": cls, "class_widened": cls_w})
    return out


def main():
    B = CM.RA.budgets()
    recs = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    r6 = json.loads((ROOT / "results" / "cell_margins.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(7)
    res = {}
    for name, rec in recs.items():
        res[name] = analyse(name, rec, B, rng)
        res[name]["margin_residual6"] = r6["designs"][name]["margin"][f"{common.WORST}|full|mixed"] if name in r6["designs"] else None
    out = {"N": N, "variants": VARIANTS, "designs": res, "near_one": near_one(r6)}
    (OUT / "array_yield.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    report(out)


def fmt(p):
    return "0" if p == 0 else f"{p:.1e}" if p < 0.01 else f"{p:.2f}"


def report(out):
    W = common.WORST
    L = ["## Probability that an array of 10^6 channels has a channel above the budget", "",
         "Strictest point (99.99 %, 33.69 dec/V, untracked), levels set open-loop. P(array) from the union bound "
         "(an upper bound); 'boot 95 %' is its 95th percentile over 300 bootstrap resamples of the channels. "
         "'closed margin' is the margin at which P(array) = 1/2, against the median worst channel of residual6.py.", "",
         "| design | condition | n | margin (residual6) | closed margin | P(array), per-channel line | boot 95 % | "
         "mismatch x 1.5 | mismatch x 2 | curvature x 1.3 | mismatch x 2, curvature x 1.3 | P(array), shared line |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in sorted(out["designs"].items()):
        d, cond = name.split("|")
        f, s = r[f"{W}|full"], r[f"{W}|shared"]
        mr = r["margin_residual6"]
        L.append(f"| {d} | {cond} | {r['n']} | {mr:.2f} | {f['margin_closed']:.2f} | {fmt(f['model']['p_array'])} | "
                 f"{fmt(f.get('p_array_boot95', float('nan')))} | {fmt(f['mismatch x 1.5']['p_array'])} | "
                 f"{fmt(f['mismatch x 2']['p_array'])} | {fmt(f['curvature x 1.3']['p_array'])} | "
                 f"{fmt(f['mismatch x 2, curvature x 1.3']['p_array'])} | {fmt(s['model']['p_array'])} |"
                 if mr is not None else f"| {d} | {cond} | {r['n']} | – | {f['margin_closed']:.2f} | {fmt(f['model']['p_array'])} | | | | | | |")
    L += ["", "### Verdicts that change under the near-one rule (widened interval reaches one)", "",
          "| design | condition | point | calibration | margin [90 %] | widening | class | with widening |", "|---|---|---|---|---|---|---|---|"]
    for c in out["near_one"]:
        L.append(f"| {c['design']} | {c['cond']} | {c['key']} | {c['kind']} | {c['margin']:.2f} [{c['ci90'][0]:.2f}, "
                 f"{c['ci90'][1]:.2f}] | {c['widening'] * 100:.1f} % | {c['class']} | {c['class_widened']} |")
    (OUT / "array_yield.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
