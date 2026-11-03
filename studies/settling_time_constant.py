"""Shortest node time constant of each switch architecture, and mismatch of the switches sized for settling.

The nominal margins of the switches of 5 to 40 um (studies/settling_and_partition.py) are interpolated in log-log
between the widths to the node time constant at which the margin is one, extrapolated from the two narrowest or two
widest widths where none is crossed, and the largest over the bands is reported; the same with a per-channel quadratic
calibration. The largest ratio of time constant to margin is given for comparison. The channels of
studies/mc_cell_settling_mismatch.py give closed-form margins with mismatch beside those of the nominal cell.

Run:  python studies/settling_time_constant.py     (writes results/settling_time_constant.{json,md})
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
import settling_and_partition as A10  # noqa: E402
import calibration_nonlinear as C11  # noqa: E402

W, N99 = common.WORST, "s33.69_t0.001"
ARCHS = ("TG", "TG + dummies", "bootstrapped", "NMOS")
LINE_OP = CM.residual_operator


def quad_op(v, cal):
    return C11.poly_operator(v, cal, 2)[0]


def margins(op):
    """Nominal margins of the switches sized for settling, as settling_and_partition.wide but with the residual operator op."""
    import mc_cell_settling as M10
    import mc_cell_variants as M9
    CM.residual_operator = op
    K = A10.keys()
    r9 = A10.nominal_runs(ROOT / "results" / "mc_cell_variants_channels.jsonl", lambda r: r["design"].startswith("TG sized for settling"))
    r10 = A10.nominal_runs(ROOT / "results" / "mc_cell_settling_channels.jsonl", lambda r: " sized for settling" in r["design"])
    tau = {k: r["tau_node"] for k, r in json.loads((ROOT / "results" / "settling_and_partition.json").read_text())["wide"]["rows"].items()}
    out = {}
    for arch in ARCHS:
        for w in M10.WIDE:
            name, src = (M9.wide_name(w), r9) if arch == "TG" else (M10.wide_name(arch, w), r10)
            for c in ("300 K", "4 K proxy"):
                d = src.get((name, c))
                row = A10.fine_metrics(d, K) if d else None
                if row is not None:
                    row["tau_node"] = tau[f"{arch}|{w:g}|{c}"]
                    out[f"{arch}|{w:g}|{c}"] = row
    CM.residual_operator = LINE_OP
    return out


def crossing(t, m):
    """tau at which the margin is one, log-log interpolation over the widths (t ascending)."""
    o = np.argsort(t)
    lt, lm = np.log(np.asarray(t)[o]), np.log(np.asarray(m)[o])
    for i in range(len(lt) - 1):
        if (lm[i] - 0) * (lm[i + 1] - 0) <= 0:
            return float(np.exp(lt[i] + (0 - lm[i]) * (lt[i + 1] - lt[i]) / (lm[i + 1] - lm[i])))
    i = 0 if lm[0] > 0 else len(lt) - 2            # all pass: extrapolate below; all fail: above
    return float(np.exp(lt[i] + (0 - lm[i]) * (lt[i + 1] - lt[i]) / (lm[i + 1] - lm[i])))


def tau_min(rows):
    res = {}
    for arch in ARCHS:
        r = {}
        for kn, key, metric in (("move50_99.9_33.69", "99.9 %, 33.69", "move50"),
                                ("open_99.99_33.69", "99.99 %, 33.69", "open_loop")):
            per_band = []
            for c in ("300 K", "4 K proxy"):
                rs = [x for k, x in rows.items() if k.startswith(arch + "|") and k.endswith("|" + c)]
                per_band.append(crossing([x["tau_node"] for x in rs], [x[key][metric] for x in rs]))
            ratio = max(x["tau_node"] / x[key][metric] for k, x in rows.items() if k.startswith(arch + "|"))
            r[kn] = {"interpolated": max(per_band), "ratio_bound": ratio}
        res[arch] = r
    return res


def mismatch():
    """Closed-form worst-of-10^6 margins (studies/array_yield.py; exact for these Gaussian linear functionals of the
    pedestals), with tau = 9.8 %, for levels set open-loop and moves of 20 and 50 mV on the 20 mV grid, with the 20
    channels and for the nominal cell alone (mismatch set to zero)."""
    import array_yield as Y
    import tail_corrected as Y8
    recs = json.loads((OUT / "mc_cell_settling_mismatch_pedestals.json").read_text(encoding="utf-8"))
    B = CM.RA.budgets()
    t = Y8.TAU_MAX
    out = {}
    for name, rec in recs.items():
        x, v, std, nominal, _ = CM.prepare(rec)
        A = CM.residual_operator(v, std)
        mu, C = x.mean(0), np.cov(x, rowvar=False)
        funcs = {"open": A[std]}
        for span in (0.02, 0.05):
            rows = [A[k] - A[j] for j in range(len(v)) for k in range(j + 1, len(v)) if v[k] - v[j] <= span + 1e-9]
            funcs[f"move{span * 1e3:g}"] = np.array(rows)
        r = {}
        for fk, D in funcs.items():
            m = D @ mu
            s = np.sqrt(np.clip(np.einsum("ij,jk,ik->i", D, C, D), 0, None))
            for key, kn in ((N99, "99.9"), (W, "99.99")):
                r[f"{kn}|{fk}"] = Y.margin_closed(m * (1 + t), s * (1 + t), B[key])
                r[f"{kn}|{fk}|nominal"] = Y.margin_closed((D @ nominal) * (1 + t), np.full(len(m), 1e-12), B[key])
        r["mismatch_sd_max_uV"] = float(np.sqrt(np.diag(A @ C @ A.T))[std].max() * 1e6)
        out[name] = r
        print(name, {k: round(x, 3) for k, x in r.items()}, flush=True)
    return out


def main():
    lin, quad = margins(LINE_OP), margins(quad_op)
    out = {"tau_line": tau_min(lin), "tau_quad": tau_min(quad), "mismatch": mismatch(),
           "rows_quad": {k: {kk: r[kk] for kk in ("tau_node", "99.9 %, 33.69", "99.99 %, 33.69")} for k, r in quad.items()}}
    (OUT / "settling_time_constant.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["## Shortest node time constant and mismatch of switches sized for settling", "",
         "| architecture | 50 mV moves, 99.9 %, 33.69: ratio bound / interpolated / interpolated, quadratic | "
         "open-loop, 99.99 %, 33.69: same |", "|---|---|---|"]
    for a in ARCHS:
        tl, tq = out["tau_line"][a], out["tau_quad"][a]
        L.append(f"| {a} | " + " | ".join(f"{tl[k]['ratio_bound'] * 1e9:.3g} / {tl[k]['interpolated'] * 1e9:.3g} / "
                                          f"{tq[k]['interpolated'] * 1e9:.3g} ns" for k in tl) + " |")
    L += ["", "Quadratic calibration, nominal margins (50 mV move at 99.9 %, 33.69 / open-loop at 99.99 %, 33.69):", "",
          "| key | tau (ns) | 50 mV move | open-loop |", "|---|---|---|---|"]
    for k, r in out["rows_quad"].items():
        L.append(f"| {k} | {r['tau_node'] * 1e9:.3g} | {r['99.9 %, 33.69']['move50']:.3g} | {r['99.99 %, 33.69']['open_loop']:.3g} |")
    L += ["", "Switches of 20 um, 20 channels (mismatch x 2 of the real switch), closed form, tau 9.8 %: with mismatch / nominal", "",
          "| design | 99.9 %, 33.69: open-loop | 20 mV move | 50 mV move | 99.99 %, 33.69: open-loop | 50 mV move | mismatch sd max (uV) |",
          "|---|---|---|---|---|---|---|"]
    for n, r in out["mismatch"].items():
        c = lambda k: f"{r[k]:.3g} / {r[k + '|nominal']:.3g}"
        L.append(f"| {n} | {c('99.9|open')} | {c('99.9|move20')} | {c('99.9|move50')} | {c('99.99|open')} | "
                 f"{c('99.99|move50')} | {r['mismatch_sd_max_uV']:.3g} |")
    (OUT / "settling_time_constant.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
