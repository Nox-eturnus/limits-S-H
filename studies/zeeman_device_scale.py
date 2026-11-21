"""The strictest point at the Zeeman difference of the device that sets its slope.

The device of Nickl et al. (arXiv:2512.10174), which gives the 33.69 dec/V slope, runs at 0.5 T near 14 GHz with
g-factors spread over 2.17e-3, so its qubit frequencies spread over about 15 MHz. Every budget of the paper uses
100 MHz and a 50 ns gate (Xue et al.). Here the 100 MHz results are recomputed with the budgets of a 15 MHz device,
using the rule of studies/zeeman_equal_sign.py (peak exchange a fifth of the Zeeman difference, gate lengthened in
proportion: 333 ns at 15 MHz).

A. Single-gate (b_ind), equal-sign (b_eq) and frame-tracked M = 2 budgets at 100, 25, 15 and 10 MHz, four slopes,
   both targets (flow.budget, studies/partial_tracking_qec.py).
B. Every Monte Carlo condition of studies/tolerated_move.py: closed-form per-channel line margin at 99.99 % and 99.9 %
   (33.69 dec/V) and the tolerated move at 99.99 % (point estimate), with the 100 MHz budgets of each margin scaled
   by the ratios of A, as studies/zeeman_equal_sign.py part D does for 25 MHz.
C. The combined worst case (steepest band, twice the mismatch, tree of a full reticle): tolerated move of the
   bootstrapped switch (studies/combined_case_fine_move.py, seed 15, as studies/combined_case_zeeman.py) and the
   margins with a line, a quadratic and a line over 0.4 V at both targets (studies/combined_case.py part A).
D. Open-loop criterion over the Figure 6 conditions and GF180MCU: tolerated growth of the mean deviation
   (studies/combined_case.py part B), smallest open-loop margins and the point accuracy for a margin of one
   (studies/calibration_accuracy.py).

Run:  python studies/zeeman_device_scale.py     (about 40 min; writes results/zeeman_device_scale.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
from flow import budget as FB  # noqa: E402
import partial_tracking_qec as PT  # noqa: E402
import operational_budget as common  # noqa: E402

ZEEMAN = (100e6, 25e6, 15e6, 10e6)
SLOPES = (3.87, 10.0, 16.6, 33.69)
TARGETS = (1e-3, 1e-4)
W, N99 = common.WORST, "s33.69_t0.001"
NINE = ("300 K", "77 K proxy", "4 K proxy", "4 K high", "77 K Beall fit", "4 K, Beall pMOS", "4 K, steep (T_eff 120 K)",
        "4 K, tree, ESD-dominated droop", "4 K, tree, one reticle")


def part_a():
    out = {}
    for dez in ZEEMAN:
        tg = 50e-9 * 100e6 / dez
        for s in SLOPES:
            lay = FB.layer(s_dec_per_v=s, d_ez=dez, t_gate=tg, dt=max(5e-12, tg / 1e4))
            for t in TARGETS:
                r = {"b_ind": min(FB.max_static(lay, t, +1), FB.max_static(lay, t, -1)),
                     "b_eq": PT.budget(lay, t, 1.0), "tracked_M2": PT.budget(lay, t, 0.0)}
                out[f"{dez / 1e6:g}|{s:g}|{t:g}"] = r
                print(f"A {dez / 1e6:g} MHz s={s:g} t={t:g}: b_ind {r['b_ind'] * 1e6:.1f}  b_eq {r['b_eq'] * 1e6:.1f}  "
                      f"tracked {r['tracked_M2'] * 1e6:.1f} uV", flush=True)
    return out


def ratios(a, dez, t):
    lo, hi = a[f"{dez / 1e6:g}|33.69|{t:g}"], a[f"100|33.69|{t:g}"]
    return lo["b_eq"] / hi["b_eq"], lo["b_ind"] / hi["b_ind"]


def scaled(b, r):
    return dict(b, b_eq=b["b_eq"] * r[0], b_ind=b["b_ind"] * r[1])


def part_b(a):
    import tolerated_move as M13
    import cell_margins as CM
    import array_yield as Y
    import tail_corrected as Y8
    r4, r3 = ratios(a, 15e6, 1e-4), ratios(a, 15e6, 1e-3)
    out = {}
    for name, rec in M13.records().items():
        x, v, std, nominal, _ = CM.prepare(rec)
        d = name.split("|")[0]
        tau = Y8.TAU_MAX if name.startswith("GF180") else Y8.tau(d, name.split("|")[1])
        A = CM.residual_operator(v, std)
        m, sd = Y.moments(x, v, std, A, nominal, "full")
        row = {}
        for lab, key, r in (("99.99", W, r4), ("99.9", N99, r3)):
            row[lab] = [Y.margin_closed(m * (1 + tau), sd * (1 + tau), b) for b in (M13.B[key], scaled(M13.B[key], r))]
        row["dmax_V"] = [M13.dmax_mc(x, v, std, tau, b)[0] for b in (M13.B[W], scaled(M13.B[W], r4))]
        out[name] = row
        print(f"B {name[:60]:60s} line {row['99.99'][0]:.3g}->{row['99.99'][1]:.3g} (99.9: {row['99.9'][0]:.3g}->"
              f"{row['99.9'][1]:.3g})  dmax {row['dmax_V'][0] * 1e3:.4g}->{row['dmax_V'][1] * 1e3:.4g} mV", flush=True)
    return out


def set_budgets(B, base, r4, r3):
    for key, r in ((W, r4), (N99, r3)):
        B[key].clear()
        B[key].update(scaled(base[key], r))


def part_c(a):
    import combined_case_fine_move as M15
    import cell_margins as CM
    import combined_case as ana14
    rec = json.loads((ROOT / "results" / "mc_cell_combined_fine_pedestals.json").read_text(encoding="utf-8"))[M15.KEY]
    x, v, std, _, _ = CM.prepare(rec)
    r4, r3 = ratios(a, 15e6, 1e-4), ratios(a, 15e6, 1e-3)
    out = {"dmax_V": {}}
    for lab, b in (("100 MHz", M15.B[W]), ("15 MHz", scaled(M15.B[W], r4))):
        rng = np.random.default_rng(15)
        out["dmax_V"][lab] = M15.dmax(M15.curve(x, v, std, b, M15.N_POINT, rng, 75))
        print(f"C combined case {lab}: dmax {out['dmax_V'][lab] * 1e3:.1f} mV", flush=True)
    B = ana14.B
    base = {k: dict(B[k]) for k in (W, N99)}
    sky = ana14.load_sky()
    for lab, rr in (("100 MHz", ((1, 1), (1, 1))), ("15 MHz", (r4, r3))):
        set_budgets(B, base, *rr)
        pa = ana14.part_a(sky)
        out[lab] = {d: row.get(ana14.COMBINED) for d, row in pa.items()}
        for d, r in out[lab].items():
            if r:
                print(f"C {lab} combined {d[:45]:45s} " + "  ".join(
                    f"{k} {r[k]['99.99']:.3g}/{r[k]['99.9']:.3g}" for k in ("line", "quadratic", "window")), flush=True)
    set_budgets(B, base, (1, 1), (1, 1))
    return out


def part_d(a):
    import combined_case as ana14
    import tail_corrected as Y8
    B, A12 = ana14.B, ana14.A12
    base = {k: dict(B[k]) for k in (W, N99)}
    r4, r3 = ratios(a, 15e6, 1e-4), ratios(a, 15e6, 1e-3)
    sky = ana14.load_sky()
    gf = json.loads((ROOT / "results" / "gf180_pedestals.json").read_text(encoding="utf-8"))
    out = {}
    for lab, rr in (("100 MHz", ((1, 1), (1, 1))), ("15 MHz", (r4, r3))):
        set_budgets(B, base, *rr)
        growth = ana14.part_b(sky)["summary"]
        res = {}
        for d in list(Y8.FIG6) + sorted({n.split("|")[0] for n in gf}):
            recs = ([(c, gf[f"{d}|{c}"], Y8.TAU_MAX) for c in ("300 K", "4 K proxy", "4 K high") if f"{d}|{c}" in gf]
                    if d.startswith("GF180") else
                    [(c, sky[f"{d}|{c}"], Y8.tau(d, c)) for c in NINE if f"{d}|{c}" in sky])
            if not recs:
                continue
            rows = [A12.calib_row(rec, t) for _, rec, t in recs]
            res[d] = {k: {"margin_min": min(r[k][W]["margin_std"] for r in rows),
                          "margin_min_99.9": min(r[k][N99]["margin_std"] for r in rows),
                          "sigma_req_min_uV": min(r[k][W]["sigma_req"] for r in rows) * 1e6,
                          "growth_min": growth.get(d, {}).get(k, {}).get("scale_min")}
                      for k in ("line", "quadratic", "window")}
            print(f"D {lab} {d[:50]:50s} " + "  ".join(
                f"{k}: m {res[d][k]['margin_min']:.3g} g {res[d][k]['growth_min'] or 0:.3g} "
                f"s {res[d][k]['sigma_req_min_uV']:.0f}" for k in ("line", "quadratic", "window")), flush=True)
        out[lab] = res
    set_budgets(B, base, (1, 1), (1, 1))
    return out


def report(res):
    a, b, c, d = res["A"], res["B"], res["C"], res["D"]
    L = ["# The strictest point with the budgets of a 15 MHz device", "",
         "## A. Budgets (µV): single gate / equal signs / frame-tracked M = 2; gate 50 ns x 100 MHz / Zeeman difference", "",
         "| Zeeman | target | " + " | ".join(f"{s:g} dec/V" for s in SLOPES) + " |", "|---|---|" + "---|" * len(SLOPES)]
    for dez in ZEEMAN:
        for t in TARGETS:
            L.append(f"| {dez / 1e6:g} MHz | {t:g} | " + " | ".join(
                "{b_ind:.1f} / {b_eq:.1f} / {tr:.1f}".format(b_ind=a[f'{dez / 1e6:g}|{s:g}|{t:g}']['b_ind'] * 1e6,
                                                          b_eq=a[f'{dez / 1e6:g}|{s:g}|{t:g}']['b_eq'] * 1e6,
                                                          tr=a[f'{dez / 1e6:g}|{s:g}|{t:g}']['tracked_M2'] * 1e6)
                for s in SLOPES) + " |")
    L += ["", "Change from 100 MHz (single gate / equal signs):", ""]
    for dez in ZEEMAN[1:]:
        for s in SLOPES:
            for t in TARGETS:
                p, q = a[f"100|{s:g}|{t:g}"], a[f"{dez / 1e6:g}|{s:g}|{t:g}"]
                L.append(f"- {dez / 1e6:g} MHz, {s:g} dec/V, {t:g}: x{q['b_ind'] / p['b_ind']:.3f} / x{q['b_eq'] / p['b_eq']:.3f}")
    L += ["", "## B. Every condition: per-channel line margin 99.99 % and 99.9 % (33.69 dec/V), tolerated move (mV); 100 / 15 MHz", "",
          "| condition | 99.99 % | 99.9 % | tolerated move |", "|---|---|---|---|"]
    for n, r in b.items():
        L.append(f"| {n} | {r['99.99'][0]:.3g} / {r['99.99'][1]:.3g} | {r['99.9'][0]:.3g} / {r['99.9'][1]:.3g} | "
                 f"{r['dmax_V'][0] * 1e3:.4g} / {r['dmax_V'][1] * 1e3:.4g} |")
    for k in (0, 1):
        f4 = [r["99.99"][1] / r["99.99"][0] for r in b.values()]
        f3 = [r["99.9"][1] / r["99.9"][0] for r in b.values()]
    sky = [r["dmax_V"][1] for n, r in b.items() if not n.startswith("GF180")]
    gfv = [r["dmax_V"][1] for n, r in b.items() if n.startswith("GF180")]
    L += ["", f"Margin factors at 15 MHz: 99.99 % x{min(f4):.3f} to x{max(f4):.3f}; 99.9 % x{min(f3):.3f} to x{max(f3):.3f}.",
          f"Smallest tolerated move at 15 MHz: SKY130 {min(sky) * 1e3:.1f} mV, GF180 {min(gfv) * 1e3:.1f} mV.",
          f"Smallest per-channel line margin at 99.9 %, 15 MHz: {min(r['99.9'][1] for r in b.values()):.3g}.", "",
          "## C. Combined worst case", "",
          "Tolerated move (bootstrapped switch): " + ", ".join(f"{k} {v * 1e3:.1f} mV" for k, v in c["dmax_V"].items()), "",
          "| design | 100 MHz: line / quadratic / 0.4 V at 99.99 % (99.9 %) | 15 MHz: same |", "|---|---|---|"]
    for dn in c["100 MHz"]:
        r0, r1 = c["100 MHz"][dn], c["15 MHz"][dn]
        if not r0:
            continue
        fmt = lambda r: " / ".join(f"{r[k]['99.99']:.3g} ({r[k]['99.9']:.3g})" for k in ("line", "quadratic", "window"))  # noqa: E731
        L.append(f"| {dn} | {fmt(r0)} | {fmt(r1)} |")
    L += ["", "## D. Open-loop criterion: smallest margin / tolerated growth / point accuracy (µV) for line, quadratic, 0.4 V", "",
          "| design | 100 MHz | 15 MHz |", "|---|---|---|"]
    for dn in d["100 MHz"]:
        fmt = lambda r: "; ".join(f"{k}: {r[k]['margin_min']:.3g} / {r[k]['growth_min'] or 0:.3g} / {r[k]['sigma_req_min_uV']:.0f}"  # noqa: E731
                                  for k in ("line", "quadratic", "window"))
        L.append(f"| {dn} | {fmt(d['100 MHz'][dn])} | {fmt(d['15 MHz'][dn])} |")
    (OUT / "zeeman_device_scale.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    res = {"A": part_a()}
    res["D"] = part_d(res["A"])
    res["C"] = part_c(res["A"])
    res["B"] = part_b(res["A"])
    (OUT / "zeeman_device_scale.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    report(res)
    print("written", flush=True)


if __name__ == "__main__":
    main()
