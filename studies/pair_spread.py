"""Pair-to-pair variation of the qubit budget combined with the electronic worst channel.

The local exchange slope and the Stark coefficient of each pair are log-normal around their nominal values, with
sigma_ln of 0.1 or 0.2 for the slope and 0.2 or 0.5 for the Stark coefficient (assumed spreads), independent of the
channel that drives the pair. On a 9 x 9 grid out to 6 sigma the untracked budgets (single gate, worse sign; equal
signs, four barriers, studies/partial_tracking_qec.py with f = 1) are recomputed with flow/budget.py and interpolated
onto a 97 x 97 grid; the closed-form channel failure probability of studies/array_yield.py is averaged over the pairs
and the array fails with 1 - (1 - p)^N. The margin is the budget scale at which that probability is 1/2.

Run:  python studies/pair_spread.py     (about 40 min; writes results/pair_spread.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
from flow import budget as B  # noqa: E402
import partial_tracking_qec as PT  # noqa: E402
import cell_margins as CM  # noqa: E402
import array_yield as Y  # noqa: E402
import tail_corrected as Y8  # noqa: E402

POINTS = {"33.69 dec/V, 99.99%": (33.69, 1e-4), "16.6 dec/V, 99.99%": (16.6, 1e-4),
          "33.69 dec/V, 99.9%": (33.69, 1e-3), "10 dec/V, 99.9%": (10.0, 1e-3)}
SPREADS = {"none": (0.0, 0.0), "slope 0.1, Stark 0.2": (0.1, 0.2), "slope 0.1, Stark 0.5": (0.1, 0.5),
           "slope 0.2, Stark 0.5": (0.2, 0.5)}
ZC = np.linspace(-6, 6, 9)          # coarse grid of the budgets, in units of the largest spreads
ZF = np.linspace(-6, 6, 97)         # fine integration grid
SMAX = (0.2, 0.5)


def budgets(s, target, alpha_scale):
    lay = B.layer(s_dec_per_v=s, stark_q2=B.STARK_BARTEE * alpha_scale)
    b_ind = min(B.max_static(lay, target, +1), B.max_static(lay, target, -1))
    return {"b_ind": b_ind, "b_eq": PT.budget(lay, target, 1.0)}


def rule(table, sig_s, sig_a):
    """Budgets and weights on the fine grid: log budgets interpolated from the coarse table (ln f_s, ln f_a)."""
    from scipy.interpolate import RegularGridInterpolator
    if sig_s == 0 and sig_a == 0:
        return [(table["nominal"], 1.0)]
    gs, ga = SMAX[0] * ZC, SMAX[1] * ZC
    fi = {k: RegularGridInterpolator((gs, ga), np.log(table[k]), method="cubic") for k in ("b_ind", "b_eq")}
    zs, za = np.meshgrid(ZF, ZF, indexing="ij")
    w = np.exp(-0.5 * (zs ** 2 + za ** 2))
    w /= w.sum()
    pts = np.column_stack([(sig_s * zs).ravel(), (sig_a * za).ravel()])
    bi, be = np.exp(fi["b_ind"](pts)), np.exp(fi["b_eq"](pts))
    keep = w.ravel() > 1e-14
    return [({"b_ind": a, "b_eq": b}, x) for a, b, x in zip(bi[keep], be[keep], w.ravel()[keep])]


def table_for(s0, t):
    tab = {"b_ind": np.zeros((len(ZC), len(ZC))), "b_eq": np.zeros((len(ZC), len(ZC)))}
    for i, zs in enumerate(ZC):
        for j, za in enumerate(ZC):
            b = budgets(s0 * np.exp(SMAX[0] * zs), t, np.exp(SMAX[1] * za))
            tab["b_ind"][i, j], tab["b_eq"][i, j] = b["b_ind"], b["b_eq"]
    tab["nominal"] = budgets(s0, t, 1.0)
    return tab


def margin_joint(m, s, bl):
    """bl: [(budget dict, weight)]; budget scale at which the array of 10^6 fails with probability 1/2."""
    bi = np.array([b["b_ind"] for b, _ in bl])[:, None]
    be = np.array([b["b_eq"] for b, _ in bl])[:, None]
    wt = np.array([x for _, x in bl])

    def p_arr(c):
        b_e, b_i = be * c, bi * c
        arg = 1 - m[None] ** 2 * (b_e ** -2 - b_i ** -2)
        tt = np.where(arg <= 0, 0.0, b_i * np.sqrt(np.clip(arg, 0, None)))
        lp = Y.log_p_exceed(m[None], s[None], tt)
        pc = np.minimum(1.0, np.exp(lp).sum(1))
        return Y.p_array(min(1.0, float((wt * pc).sum())))
    lo, hi = 1e-3, 1e3
    for _ in range(60):
        c = np.sqrt(lo * hi)
        lo, hi = (c, hi) if p_arr(c) > 0.5 else (lo, c)
    return 1 / np.sqrt(lo * hi), p_arr(1.0)


def main():
    recs = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    out = {"spreads": SPREADS, "rows": {}}
    for pn, (s0, t) in POINTS.items():
        tab = table_for(s0, t)
        print(pn, "budgets done", flush=True)
        for sn, (ss, sa) in SPREADS.items():
            bl = rule(tab, ss, sa)
            for d in Y8.FIG6:
                x, v, std, nominal, _ = CM.prepare(recs[f"{d}|4 K proxy"])
                A = CM.residual_operator(v, std)
                tau = Y8.tau(d, "4 K proxy")
                for kind in ("full", "shared"):
                    m, sd = Y.moments(x, v, std, A, nominal, kind)
                    mg, p1 = margin_joint(m * (1 + tau), sd * (1 + tau), bl)
                    out["rows"].setdefault(f"{d}|{kind}", {}).setdefault(pn, {})[sn] = {"margin": mg, "p_array": p1}
        out.setdefault("tables", {})[pn] = {k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in tab.items()}
    (OUT / "pair_spread.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["## Margins with pair-to-pair variation of slope and Stark coefficient (4 K band, open-loop)",
         "", "Closed-form margin on the array of 10^6 (P = 1/2), corrected for tau; P(array fails) at the nominal budget "
         "scale in brackets. Spreads are sigma_ln of the local slope and of the Stark coefficient.", "",
         "| Design | Calibration | Point | " + " | ".join(SPREADS) + " |", "|---|---|---|" + "---|" * len(SPREADS)]
    for dk, by_p in out["rows"].items():
        d, kind = dk.split("|")
        for pn, by_s in by_p.items():
            cells = [f"{by_s[sn]['margin']:.3g} ({by_s[sn]['p_array']:.1e})" for sn in SPREADS]
            L.append(f"| {d} | {kind} | {pn} | " + " | ".join(cells) + " |")
    (OUT / "pair_spread.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
