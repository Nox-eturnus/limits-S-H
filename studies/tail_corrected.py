"""Worst-channel margins and array-failure probabilities corrected for the tail optimism of the surrogate.

Tail correction. Scaled-sigma sampling (studies/tail_optimism.py) finds the largest deviation of the worst channels
up to tau above the surrogate at 4.6 to 5.5 sigma. Every margin of studies/cell_margins.py is divided by 1 + tau and
every closed-form probability (studies/array_yield.py) is computed with the deviation scaled by 1 + tau. tau is the
value measured for that design in that condition where one was measured (TG: 300 K, 4 K, 4 K high; bootstrapped and
NMOS switches: 4 K) and the largest measured value elsewhere, including every design without a scaled-sigma run.
Verdicts: pass when the corrected 90 % interval, widened at its lower end as in studies/array_yield.py, lies above
one; fail when it lies below one; near one otherwise.

Probability floor. Probabilities below 10^-6 are reported as "< 10^-6": the tail was checked directly only to
5.5 sigma, and below this level the model error (mismatch x 2, curvature x 1.3 columns) carries the information.

Covariance check. The closed form uses only the variance of the deviation at each of the seven standard held
voltages (union bound), estimated from 20 channels (100 for three designs). A Ledoit-Wolf shrinkage of the
covariance of the deviations (seven voltages) towards their mean variance is used as a check of that estimate.

Curvature scale. The scale c* at which the corrected margin falls to one (the mean deviation scaled by c, the
mismatch part unchanged), against the spread of the curvature across bands.

These are the margins of Fig. 6a. Run:  python studies/tail_corrected.py      (about a minute)
Writes results/tail_corrected.{json,md}.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import cell_margins as CM  # noqa: E402
import array_yield as Y  # noqa: E402

W, N99, REF = common.WORST, "s33.69_t0.001", common.REF
NMOS, BOOT = "NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive"
TSWO, TGD, TG, TGE = "T-switch + OTA buffer", "TG + dummies", "TG, no ESD", "TG, ESD on the node"
FIG6 = (NMOS, BOOT, TSWO, TGD, TG, TGE)
S6_BANDS = ("300 K", "77 K proxy", "4 K proxy", "4 K high", "77 K Beall fit", "4 K, Beall pMOS", "4 K, steep (T_eff 120 K)",
            "4 K, tree, ESD-dominated droop", "4 K, tree, one reticle")
FLOOR = 1e-6
A8 = json.loads((OUT / "tail_optimism.json").read_text(encoding="utf-8"))
TAU_MAX = A8["tau_by_design"]["not measured"]
TAU = {(TG, "300 K"): A8["TG|300 K"]["tau"], (TG, "4 K proxy"): A8["TG|4 K proxy"]["tau"],
       (TG, "4 K high"): A8["TG|4 K high"]["tau"], (BOOT, "4 K proxy"): A8["bootstrapped|4 K proxy"]["tau"],
       (NMOS, "4 K proxy"): A8["NMOS|4 K proxy"]["tau"]}


def tau(design, cond):
    return TAU.get((design, cond), TAU_MAX)


def verdict(design, lo, hi, t):
    w = Y.widening(design)
    lo, hi = lo / (1 + t), hi / (1 + t)
    return "pass" if lo / (1 + w) > 1 else "fail" if hi < 1 else "near one"


def pfmt(p):
    return "< 10^-6" if p < FLOOR else f"{p:.0e}".replace("e-0", " × 10^-").replace("e-", " × 10^-") if p < 0.01 else f"{p:.2f}"


def g3(x):
    return "–" if x is None else f"{x:.3g}"


def ledoit_wolf(x):
    """Ledoit-Wolf shrinkage of the sample covariance towards mu I (Ledoit and Wolf 2004)."""
    n, p = x.shape
    xc = x - x.mean(0)
    S = xc.T @ xc / n
    mu = np.trace(S) / p
    d2 = np.sum((S - mu * np.eye(p)) ** 2)
    b2 = sum(np.sum((np.outer(r, r) - S) ** 2) for r in xc) / n ** 2
    delta = min(b2, d2) / d2 if d2 > 0 else 1.0
    return delta * mu * np.eye(p) + (1 - delta) * S * n / (n - 1), delta


def moments_lw(x, v, std, A, nominal, kind):
    """Mean and standard deviation of the deviation at the standard held voltages, with the covariance of the
    deviations of the channels (seven voltages) shrunk by Ledoit-Wolf towards their mean variance."""
    if kind == "full":
        d = (x @ A.T)[:, std]
    else:
        line = np.polyval(np.polyfit(v[std], nominal[std], 1), v)
        d = (x - line)[:, std]
    C, delta = ledoit_wolf(d)
    return d.mean(0), np.sqrt(np.clip(np.diag(C), 0, None)), delta


def main():
    r6 = json.loads((ROOT / "results" / "cell_margins.json").read_text(encoding="utf-8"))["designs"]
    recs = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    B = CM.RA.budgets()
    rng = np.random.default_rng(8)
    out = {"tau": {f"{d}|{c}": t for (d, c), t in TAU.items()}, "tau_max": TAU_MAX, "designs": {}}

    for name, r in r6.items():
        d, c = name.split("|")
        t = tau(d, c)
        row = {"tau": t, "n": r["n"], "margin": {}, "ci90": {}, "verdict": {}}
        for k, m in r["margin"].items():
            if not k.endswith("|mixed"):
                continue
            row["margin"][k] = m / (1 + t)
            lo, hi = r["ci90"][k]
            row["ci90"][k] = [lo / (1 + t), hi / (1 + t)]
            row["verdict"][k] = verdict(d, lo, hi, t)
        # closed-form probabilities with the deviation scaled by 1 + tau, and the model-error variants
        x, v, std, nominal, _ = CM.prepare(recs[name])
        A = CM.residual_operator(v, std)
        for kind in ("full", "shared"):
            m, s = Y.moments(x, v, std, A, nominal, kind)
            m, s = m * (1 + t), s * (1 + t)
            b = B[W]
            row[f"p|{kind}"] = {vn: Y.p_array(Y.p_channel(m * fm, s * fs, b)[0]) for vn, (fs, fm) in Y.VARIANTS.items()}
            row[f"exp_count|{kind}"] = 1e6 * Y.p_channel(m, s, b)[0]
            if kind == "full":
                boots = []
                for _ in range(300):
                    xb = x[rng.integers(0, len(x), len(x))]
                    mb, sb = Y.moments(xb, v, std, A, nominal, kind)
                    boots.append(Y.p_array(Y.p_channel(mb * (1 + t), sb * (1 + t), b)[0]))
                row["p_boot95"] = float(np.quantile(boots, 0.95))
                # curvature scale at which the corrected margin is one
                lo_c, hi_c = 0.5, 20.0
                for _ in range(60):
                    cc = np.sqrt(lo_c * hi_c)
                    if Y.margin_closed(m * cc, s, b) > 1:
                        lo_c = cc
                    else:
                        hi_c = cc
                row["curvature_scale_to_one"] = float(np.sqrt(lo_c * hi_c))
                row["curvature_max_uV"] = float(np.abs(m / (1 + t)).max() * 1e6)
                # Ledoit-Wolf covariance check
                ml, sl, delta = moments_lw(x, v, std, A, nominal, kind)
                row["lw"] = {"delta": float(delta), "margin": Y.margin_closed(ml * (1 + t), sl * (1 + t), b),
                             "margin_sample": Y.margin_closed(m, s, b), "n_voltages_fit": int(len(v)),
                             "n_voltages_closed_form": int(std.sum())}
        out["designs"][name] = row
    (OUT / "tail_corrected.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    tables(out)


def tables(out):
    D = out["designs"]

    def get(d, c, key=W, kind="full"):
        r = D.get(f"{d}|{c}")
        k = f"{key}|{kind}|mixed"
        return None if r is None or k not in r["margin"] else (r["margin"][k], r["ci90"][k], r["verdict"][k])

    L = ["# Tail-corrected margins and floored probabilities", "",
         "tau: " + ", ".join(f"{k} {v * 100:.1f} %" for k, v in out["tau"].items()) + f"; elsewhere {out['tau_max'] * 100:.1f} %.", ""]

    # ---- verdicts that are not a pass
    L += ["## Verdicts other than pass (all conditions, strictest point, levels set open-loop)", "",
          "| design | condition | calibration | corrected margin [90 %] | verdict |", "|---|---|---|---|---|"]
    for name, r in sorted(D.items()):
        for kind in ("full", "shared"):
            k = f"{W}|{kind}|mixed"
            if k in r["verdict"] and r["verdict"][k] != "pass" and (kind == "full" or "mismatch x" not in name):
                if kind == "shared" and r["verdict"][k] == "fail":
                    continue
                lo, hi = r["ci90"][k]
                L.append(f"| {name.split('|')[0]} | {name.split('|')[1]} | {kind} | {r['margin'][k]:.3g} [{lo:.3g}, {hi:.3g}] | {r['verdict'][k]} |")
    L.append("")

    # ---- Table S3 (the nine cells of studies/cells.py, 300 K)
    PD = (("NMOS switch", "D NSW"), ("TG", "D TG"), ("TG with dummies", "D TGD"), ("Bootstrapped NMOS", "D BOOT"),
          ("Charge-locked TG", "D CLK"), ("Thick-oxide T-switch", "D TSW"), ("TG, high-threshold PMOS", "D TGH"),
          ("T-switch, buffered, thick oxide", "D TSWB"), ("T-switch, buffered, thin oxide", "D NTB"))
    T3 = ["| Cell | Margin, per-channel calibration | Margin, shared calibration | P(any of 10^6 channels over budget), per channel / shared |",
          "|---|---|---|---|"]
    for lab, d in PD:
        f, s = get(d, "300 K"), get(d, "300 K", kind="shared")
        r = D[f"{d}|300 K"]
        T3.append(f"| {lab} | {f[0]:.3g} [{f[1][0]:.3g}, {f[1][1]:.3g}]{'' if f[2] == 'pass' else ', ' + f[2]} | "
                  f"{s[0]:.3g} [{s[1][0]:.3g}, {s[1][1]:.3g}]{'' if s[2] == 'pass' else ', ' + s[2]} | "
                  f"{pfmt(r['p|full']['model'])} / {pfmt(r['p|shared']['model'])} |")
    L += ["## Table S3 (margin columns)", ""] + T3 + [""]

    # ---- Table S6
    T6 = ["| Cell | " + " | ".join(S6_BANDS) + " |", "|---|" + "---|" * len(S6_BANDS)]
    for d in FIG6:
        cells = []
        for c in S6_BANDS:
            f, s = get(d, c), get(d, c, kind="shared")
            cells.append("–" if f is None else f"{f[0]:.3g} / {s[0]:.3g}" + ("" if f[2] == "pass" else f" ({f[2]})"))
        T6.append(f"| {d} | " + " | ".join(cells) + " |")
    L += ["## Table S6", ""] + T6 + [""]

    # ---- Table S7 widths
    WID = ((NMOS, "0.42", NMOS), (NMOS, "1", NMOS + ", W 1"), (NMOS, "3", NMOS + ", W 3"), (BOOT, "0.42", BOOT),
           (BOOT, "1", "bootstrapped (transistor level), W 1"), (TSWO, "0.42", TSWO + ", W 0.42"), (TSWO, "0.84", TSWO),
           (TGD, "0.84", TGD + ", W 0.84"), (TGD, "1", TGD), (TG, "0.42", TG + ", W 0.42"),
           (TG + ", 0.3 V underdrive", "0.42", TG + ", W 0.42, 0.3 V underdrive"), (TG, "1", TG), (TG, "3", TG + ", W 3"))
    T7 = ["| Cell | $W_n$ (µm) | 50 Ω | Tree |", "|---|---|---|---|"]
    for lab, w, d in WID:
        cells = []
        for c in ("4 K proxy", "4 K, tree, ESD-dominated droop"):
            f, s = get(d, c), get(d, c, kind="shared")
            cells.append("–" if f is None else f"{f[0]:.3g} / {s[0]:.3g}" + ("" if f[2] == "pass" else f" ({f[2]})"))
        T7.append(f"| {lab} | {w} | " + " | ".join(cells) + " |")
    L += ["## Table S7", ""] + T7 + [""]

    # ---- Table S8 variants
    V8 = (("4 K", "4 K proxy"), ("Steep, $T_{\\mathrm{eff}}$ = 120 K", "4 K, steep (T_eff 120 K)"),
          ("Steep, $T_{\\mathrm{eff}}$ = 30 K", "4 K, steep (T_eff 30 K)"), ("Steep, $T_{\\mathrm{eff}}$ = 20 K", "4 K, steep (T_eff 20 K)"),
          ("Clock edges 600 ps", "4 K, clock edge 600 ps"), ("Clock edges 67 ps", "4 K, clock edge 67 ps"),
          ("Tree source, fan-out 10 at 5 × 10^5", "4 K, tree source"), ("Tree source, best tree at 3.1 mV/s", "4 K, tree, ESD-dominated droop"),
          ("Tree source, best tree on one reticle", "4 K, tree, one reticle"),
          ("Tree source, best tree with protection diodes on 1 pF", "4 K, tree, ESD diodes on 1 pF"),
          ("Buffered final line", "4 K, buffered leaf line"), ("Mismatch × 1.5", "4 K, mismatch x 1.5"), ("Mismatch × 2", "4 K, mismatch x 2"))
    T8 = ["| Variant | NMOS, 0.3 V underdrive: 99.99% | 99.9% | Bootstrapped NMOS: 99.99% | 99.9% | TG with dummies: 99.99% | 99.9% |",
          "|---|---|---|---|---|---|---|"]
    for lab, c in V8:
        cells = []
        for d in (NMOS, BOOT, TGD):
            f, f9 = get(d, c), get(d, c, N99)
            r = D.get(f"{d}|{c}")
            if f is None:
                cells += ["–", "–"]
                continue
            ec = r["exp_count|full"]
            cells += [f"{f[0]:.3g} ({'0' if ec < 0.05 else f'{ec:.2g}'})" + ("" if f[2] == "pass" else f", {f[2]}"), f"{f9[0]:.3g}"]
        T8.append(f"| {lab} | " + " | ".join(cells) + " |")
    L += ["## Table S8", ""] + T8 + [""]

    # ---- Table S9 probabilities
    T9 = ["| Cell | Per channel: model | 95th bootstrap percentile | Mismatch × 2 | Curvature × 1.3 | Both | Shared, 4 K band |",
          "|---|---|---|---|---|---|---|"]
    for d in FIG6:
        rows = [D[f"{d}|{c}"] for c in S6_BANDS if f"{d}|{c}" in D]
        mx = lambda f: max(f(r) for r in rows)  # noqa: E731
        T9.append(f"| {d} | {pfmt(mx(lambda r: r['p|full']['model']))} | {pfmt(mx(lambda r: r['p_boot95']))} | "
                  f"{pfmt(mx(lambda r: r['p|full']['mismatch x 2']))} | {pfmt(mx(lambda r: r['p|full']['curvature x 1.3']))} | "
                  f"{pfmt(mx(lambda r: r['p|full']['mismatch x 2, curvature x 1.3']))} | {pfmt(D[f'{d}|4 K proxy']['p|shared']['model'])} |")
    L += ["## Table S9", ""] + T9 + [""]

    # ---- covariance check and curvature scale
    L += ["## Ledoit-Wolf check and dimensionality (4 K band, strictest point, per channel)", "",
          "| design | channels | voltages in the fit | voltages in the closed form | shrinkage | corrected margin, sample / Ledoit-Wolf |",
          "|---|---|---|---|---|---|"]
    for d in FIG6:
        r = D[f"{d}|4 K proxy"]
        lw = r["lw"]
        L.append(f"| {d} | {r['n']} | {lw['n_voltages_fit']} | {lw['n_voltages_closed_form']} | {lw['delta']:.2f} | "
                 f"{lw['margin_sample']:.3g} / {lw['margin']:.3g} |")
    L += ["", "## Curvature scale at which the corrected per-channel margin falls to one (strictest point)", "",
          "| design | lowest over Figure 6 conditions (condition) | 4 K band | curvature of the mean channel over the bands (µV) |",
          "|---|---|---|---|"]
    for d in FIG6:
        rows = {c: D[f"{d}|{c}"] for c in S6_BANDS if f"{d}|{c}" in D}
        cmin = min(rows.items(), key=lambda t: t[1]["curvature_scale_to_one"])
        curv = [r["curvature_max_uV"] for c, r in rows.items() if "tree" not in c]
        L.append(f"| {d} | {cmin[1]['curvature_scale_to_one']:.2f} ({cmin[0]}) | {rows['4 K proxy']['curvature_scale_to_one']:.2f} | "
                 f"{min(curv):.1f} to {max(curv):.1f} |")
    L.append("")

    # ---- summary numbers
    L += ["## Summary numbers for the text", ""]
    for d in FIG6:
        rs = [(c, get(d, c)) for c in S6_BANDS if get(d, c)]
        rc = [(c, x) for c, x in rs if c not in ("300 K",) and "tree" not in c]
        rt = [(c, x) for c, x in rs if "tree" in c]
        sh = [(c, get(d, c, kind="shared")) for c in S6_BANDS if get(d, c)]
        L.append(f"- {d}: per-channel {min(x[0] for _, x in rs):.3g} to {max(x[0] for _, x in rs):.3g} "
                 f"(cryo 50 ohm {min(x[0] for _, x in rc):.3g}-{max(x[0] for _, x in rc):.3g}, trees "
                 f"{min(x[0] for _, x in rt):.3g}-{max(x[0] for _, x in rt):.3g}); shared {min(x[0] for _, x in sh):.3g}-{max(x[0] for _, x in sh):.3g}; "
                 f"verdicts {sorted(set(x[2] for _, x in rs))}; 4 K {get(d, '4 K proxy')[0]:.3g} {get(d, '4 K proxy')[2]}")
    for key, lab in ((N99, "99.9 %, 33.69"), (REF, "99.9 %, 10 dec/V")):
        for kind in ("full", "shared"):
            allm = [(n, r["margin"][f"{key}|{kind}|mixed"]) for n, r in D.items()
                    if f"{key}|{kind}|mixed" in r["margin"] and "mismatch" not in n and n.split("|")[0] in FIG6]
            mn = min(allm, key=lambda t: t[1])
            L.append(f"- {lab}, {kind}, Figure 6 designs, all conditions: lowest {mn[1]:.3g} ({mn[0]})")
    for span in ("move20mV", "move50mV"):
        xs = [(n, r["margin"][f"{W}|{span}|mixed"]) for n, r in D.items() if f"{W}|{span}|mixed" in r["margin"]
              and n.split("|")[0] in FIG6 and "mismatch" not in n and n.split("|")[1] != "300 K"]
        mn = min(xs, key=lambda t: t[1])
        L.append(f"- {span} (as stored; fine grid in the 4 K band), cryo and trees: lowest {mn[1]:.3g} ({mn[0]})")
    for c in ("4 K, mismatch x 1.5", "4 K, mismatch x 2"):
        L.append(f"- {c}: " + ", ".join(f"{d} {get(d, c)[0]:.3g} / shared {get(d, c, kind='shared')[0]:.3g}"
                                        for d in (NMOS, BOOT, TGD) if get(d, c)))
    pd_rt = [(n, r["margin"][f"{W}|full|mixed"], r["verdict"][f"{W}|full|mixed"]) for n, r in D.items() if n.startswith("D ")]
    L.append("- Table S3 per channel: " + ", ".join(f"{n.split('|')[0]} {m:.3g} {v}" for n, m, v in sorted(pd_rt)))
    L.append("- Table S3 99.9 %/10 dec/V per channel lowest: " + f"{min(r['margin'][f'{REF}|full|mixed'] for n, r in D.items() if n.startswith('D ')):.3g}"
             + "; 99.9 %/33.69 lowest: " + f"{min(r['margin'][f'{N99}|full|mixed'] for n, r in D.items() if n.startswith('D ')):.3g}")
    (OUT / "tail_corrected.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
