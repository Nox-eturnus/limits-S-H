"""Budgets for equal signs against the Zeeman difference, and of a held CZ amplitude.

A. Untracked budgets against the Zeeman difference (100, 50, 25 MHz, the gate lengthened in proportion as in
   studies/stark_and_zeeman.py): the single-gate budget b_ind (worse sign) and the budget for equal signs b_eq
   (studies/partial_tracking_qec.py with f = 1: conditional phase as for M = 2, Stark phases of four barriers added),
   at 3.87, 10, 16.6 and 33.69 dec/V and both targets.
B. The same two budgets with the Stark coefficient on both qubits (equal and opposite sign), 100 MHz, 99.9 %.
C. A held CZ amplitude, dv(t) = eps v0(t): eps for one gate (random sign) and for equal signs (the accounting of A),
   and the swing of the pulse line v0 / k with k = 0.5.
D. Margins and tolerated moves at the strictest point (99.99 %, 33.69 dec/V) with the budgets of a 25 MHz device:
   the 100 MHz budgets of every margin scaled by the ratios of part A, applied to every Monte Carlo condition of
   studies/tolerated_move.py (closed form with the tail allowance; Delta_max point estimates).

Run:  python studies/zeeman_equal_sign.py     (about 20 min; writes results/zeeman_equal_sign.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
from flow import budget as B  # noqa: E402
import partial_tracking_qec as PT  # noqa: E402
from repeated_gates import _PROJ_COND  # noqa: E402

ZEEMAN = ((100e6, 50e-9), (50e6, 100e-9), (25e6, 200e-9))
SLOPES = (3.87, 10.0, 16.6, 33.69)
TARGETS = (1e-3, 1e-4)


def b_ind(lay, t):
    return min(B.max_static(lay, t, +1), B.max_static(lay, t, -1))


def part_a():
    out = {}
    for dez, tg in ZEEMAN:
        for s in SLOPES:
            lay = B.layer(s_dec_per_v=s, d_ez=dez, t_gate=tg, dt=max(5e-12, tg / 1e4))
            for t in TARGETS:
                out[f"{dez / 1e6:g}|{s:g}|{t:g}"] = {"b_ind": b_ind(lay, t), "b_eq": PT.budget(lay, t, 1.0)}
                r = out[f"{dez / 1e6:g}|{s:g}|{t:g}"]
                print(f"A {dez / 1e6:g} MHz s={s:g} t={t:g}: b_ind {r['b_ind'] * 1e6:.1f} uV, b_eq {r['b_eq'] * 1e6:.1f} uV",
                      flush=True)
    return out


def part_b():
    out = {}
    a = B.STARK_BARTEE
    for s in (3.87, 10.0, 33.69):
        for name, q1 in (("one", 0.0), ("both_equal", a), ("both_opposite", -a)):
            lay = B.layer(s_dec_per_v=s, stark_q1=q1, stark_q2=a)
            out[f"{s:g}|{name}"] = {"b_ind": b_ind(lay, 1e-3), "b_eq": PT.budget(lay, 1e-3, 1.0)}
    return out


def _solve(f, t):
    xs = np.geomspace(1e-6, 0.5, 300)
    v = np.array([f(x) for x in xs]) - t
    i = np.nonzero(v >= 0)[0][0]
    return brentq(lambda x: f(x) - t, xs[i - 1], xs[i]) if i else xs[0]


def part_c():
    out = {}
    for s in SLOPES:
        lay = B.layer(s_dec_per_v=s)
        v0 = float(np.max(lay.v0))
        for t in TARGETS:
            def single(e, sg):
                return lay.excess_infidelity(sg * e * lay.v0)

            def equal(e, sg):
                ph = lay.phase_errors(sg * e * lay.v0)
                c = _PROJ_COND @ ph
                return B.phase_infidelity(np.sqrt(2) * c + 2.0 * (ph - c))
            es = min(_solve(lambda e: single(e, 1), t), _solve(lambda e: single(e, -1), t))
            ee = min(_solve(lambda e: equal(e, 1), t), _solve(lambda e: equal(e, -1), t))
            out[f"{s:g}|{t:g}"] = {"v0": v0, "eps_single": es, "eps_equal": ee,
                                   "swing_single_V": es * v0 / 0.5, "swing_equal_V": ee * v0 / 0.5}
    return out


def part_d(a):
    import operational_budget as common
    import tolerated_move as M13
    import cell_margins as CM
    import array_yield as Y
    import tail_corrected as Y8
    b100 = M13.B[common.WORST]
    r_eq = a["25|33.69|0.0001"]["b_eq"] / a["100|33.69|0.0001"]["b_eq"]
    r_ind = a["25|33.69|0.0001"]["b_ind"] / a["100|33.69|0.0001"]["b_ind"]
    b25 = dict(b100, b_eq=b100["b_eq"] * r_eq, b_ind=b100["b_ind"] * r_ind)
    out = {"ratio_b_eq": r_eq, "ratio_b_ind": r_ind, "rows": {}}
    for name, rec in M13.records().items():
        x, v, std, nominal, _ = CM.prepare(rec)
        d = name.split("|")[0]
        tau = Y8.TAU_MAX if name.startswith("GF180") else Y8.tau(d, name.split("|")[1])
        A = CM.residual_operator(v, std)
        row = {}
        for kind in ("full", "shared"):
            m, sd = Y.moments(x, v, std, A, nominal, kind)
            row[kind] = [Y.margin_closed(m * (1 + tau), sd * (1 + tau), b) for b in (b100, b25)]
        row["dmax_V"] = [M13.dmax_mc(x, v, std, tau, b)[0] for b in (b100, b25)]
        row["window_V"] = float(v[np.where(std)[0][-1]] - v[np.where(std)[0][0]])
        out["rows"][name] = row
        print(f"D {name[:60]:60s} full {row['full'][0]:.3g}->{row['full'][1]:.3g}  "
              f"dmax {row['dmax_V'][0] * 1e3:.4g}->{row['dmax_V'][1] * 1e3:.4g} mV", flush=True)
    return out


def report(res):
    a, b, c, d = res["A"], res["B"], res["C"], res["D"]
    L = ["# Budgets for equal signs against the Zeeman difference, and of a held amplitude", "",
         "## A. Untracked budgets (µV): single gate / equal signs; gate 50, 100, 200 ns for 100, 50, 25 MHz", "",
         "| Zeeman | target | " + " | ".join(f"{s:g} dec/V" for s in SLOPES) + " |", "|---|---|" + "---|" * len(SLOPES)]
    for dez, _ in ZEEMAN:
        for t in TARGETS:
            L.append(f"| {dez / 1e6:g} MHz | {t:g} | " + " | ".join(
                f"{a[f'{dez / 1e6:g}|{s:g}|{t:g}']['b_ind'] * 1e6:.1f} / {a[f'{dez / 1e6:g}|{s:g}|{t:g}']['b_eq'] * 1e6:.1f}"
                for s in SLOPES) + " |")
    L += ["", "Change from 100 to 25 MHz (single gate / equal signs):", ""]
    for s in SLOPES:
        for t in TARGETS:
            p, q = a[f"100|{s:g}|{t:g}"], a[f"25|{s:g}|{t:g}"]
            L.append(f"- {s:g} dec/V, {t:g}: x{q['b_ind'] / p['b_ind']:.3f} / x{q['b_eq'] / p['b_eq']:.3f}")
    L += ["", "## B. Stark coefficient on both qubits, 100 MHz, 99.9 % (mV): single gate / equal signs", ""]
    for k, r in b.items():
        L.append(f"- {k}: {r['b_ind'] * 1e3:.3f} / {r['b_eq'] * 1e3:.3f}")
    L += ["", "## C. Held CZ amplitude: fractional error eps (%) and swing of the pulse line at k = 0.5 (mV)", "",
          "| s (dec/V) | target | v0 (V) | eps single gate | eps equal signs | swing single | swing equal |",
          "|---|---|---|---|---|---|---|"]
    for k, r in c.items():
        s, t = k.split("|")
        L.append(f"| {s} | {t} | {r['v0']:.3f} | {r['eps_single'] * 100:.3g} | {r['eps_equal'] * 100:.3g} | "
                 f"{r['swing_single_V'] * 1e3:.3g} | {r['swing_equal_V'] * 1e3:.3g} |")
    L += ["", f"## D. Strictest point with the budgets of a 25 MHz device (b_eq x{d['ratio_b_eq']:.3f}, "
          f"b_ind x{d['ratio_b_ind']:.3f})", "",
          "| condition | per-channel line 100 / 25 MHz | shared line 100 / 25 MHz | Delta_max 100 / 25 MHz (mV) |",
          "|---|---|---|---|"]
    for n, r in d["rows"].items():
        L.append(f"| {n} | {r['full'][0]:.3g} / {r['full'][1]:.3g} | {r['shared'][0]:.3g} / {r['shared'][1]:.3g} | "
                 f"{r['dmax_V'][0] * 1e3:.4g} / {r['dmax_V'][1] * 1e3:.4g} |")
    fr = [r[k][1] / r[k][0] for r in d["rows"].values() for k in ("full", "shared")]
    dm = [r["dmax_V"][1] / r["dmax_V"][0] for r in d["rows"].values() if r["dmax_V"][0] < r["window_V"] - 1e-9]
    floor = min(r["dmax_V"][1] for n, r in d["rows"].items() if not n.startswith("GF180"))
    floor_gf = min(r["dmax_V"][1] for n, r in d["rows"].items() if n.startswith("GF180"))
    L += ["", f"Margin ratio 25 / 100 MHz over all conditions: {min(fr):.3f} to {max(fr):.3f}.",
          f"Delta_max ratio where below the whole window: {min(dm):.3f} to {max(dm):.3f}.",
          f"Smallest Delta_max at 25 MHz: SKY130 {floor * 1e3:.4g} mV, GF180 {floor_gf * 1e3:.4g} mV."]
    (OUT / "zeeman_equal_sign.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


def main():
    a = part_a()
    res = {"A": a, "B": part_b(), "C": part_c()}
    res["D"] = part_d(a)
    (OUT / "zeeman_equal_sign.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    report(res)


if __name__ == "__main__":
    main()
