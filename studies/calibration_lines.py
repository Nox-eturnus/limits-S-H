"""Calibration lines and the verdict rule.

The per-channel calibration is a least-squares line through the seven standard held voltages
(studies/cell_margins.py, residual_operator). The same closed-form margins (studies/array_yield.py, corrected for the
tail optimism of studies/tail_corrected.py) are computed for that line and for two-point calibrations: a line through
the two end points of the window, and through the pair of standard voltages that gives the design the largest margin
in the 4 K band. Intervals: 300 bootstrap resamples of the channels.

Verdicts: resolved only when the 90 % interval, widened at its lower end (1.4 % for the transmission gates, 5.3 %
otherwise) and corrected for tau, lies wholly outside 0.9 to 1.1; "pass" above, "fail" below, "unresolved" otherwise.
The NMOS switch is also evaluated on a fixed window of 0.3 to 0.7 V in every condition.

Run:  python studies/calibration_lines.py     (about 2 min; writes results/calibration_lines.{json,md})
"""
import itertools
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
import tail_corrected as Y8  # noqa: E402

W, N99, REF = common.WORST, "s33.69_t0.001", common.REF
B = CM.RA.budgets()
FIG6, S6_BANDS = Y8.FIG6, Y8.S6_BANDS
NMOS = Y8.NMOS
N_BOOT = 300
LO, HI = 0.9, 1.1


def two_point(v, std, i, j):
    """Residual operator of the line through standard voltages i and j (indices into v)."""
    A = np.eye(len(v))
    A[:, i] -= (v[j] - v) / (v[j] - v[i])
    A[:, j] -= (v - v[i]) / (v[j] - v[i])
    return A


def margin_ci(x, v, std, A, nominal, t, key, rng, kind="full", boot=True):
    m, s = Y.moments(x, v, std, A, nominal, kind)
    point = Y.margin_closed(m * (1 + t), s * (1 + t), B[key])
    if not boot:
        return point, None
    bs = []
    for _ in range(N_BOOT):
        xb = x[rng.integers(0, len(x), len(x))]
        mb, sb = Y.moments(xb, v, std, A, nominal, kind)
        bs.append(Y.margin_closed(mb * (1 + t), sb * (1 + t), B[key]))
    return point, [float(np.quantile(bs, 0.05)), float(np.quantile(bs, 0.95))]


def verdict(design, point, ci):
    if ci is None:
        return "pass" if point > HI else "fail" if point < LO else "unresolved"
    lo = ci[0] / (1 + Y.widening(design))
    return "pass" if lo > HI else "fail" if ci[1] < LO else "unresolved"


def main():
    recs = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    y8 = json.loads((ROOT / "results" / "tail_corrected.json").read_text(encoding="utf-8"))["designs"]
    rng = np.random.default_rng(9)
    out = {"pairs": {}, "rows": {}, "s2": {}, "s4": {}}

    # pick the best pair per design in the 4 K band
    for d in FIG6:
        x, v, std, nominal, _ = CM.prepare(recs[f"{d}|4 K proxy"])
        idx = np.where(std)[0]
        best = max(itertools.combinations(idx, 2),
                   key=lambda ij: Y.margin_closed(*[a * (1 + Y8.tau(d, "4 K proxy")) for a in
                                                    Y.moments(x, v, std, two_point(v, std, *ij), nominal, "full")], B[W]))
        out["pairs"][d] = [float(v[best[0]]), float(v[best[1]])]

    for d in FIG6:
        for c in S6_BANDS:
            name = f"{d}|{c}"
            if name not in recs:
                continue
            x, v, std, nominal, _ = CM.prepare(recs[name])
            t = Y8.tau(d, c)
            idx = np.where(std)[0]
            ops = {"least squares, 7 points": CM.residual_operator(v, std),
                   "two points, window ends": two_point(v, std, idx[0], idx[-1])}
            pv = out["pairs"][d]
            pi = [int(np.argmin(np.abs(v - p))) for p in pv]
            if all(abs(v[i] - p) < 1e-6 for i, p in zip(pi, pv)):
                ops[f"two points, best pair {pv[0]:g}/{pv[1]:g} V"] = two_point(v, std, *pi)
            row = {}
            for on, A in ops.items():
                r = {}
                for key in (W, N99, REF):
                    p, ci = margin_ci(x, v, std, A, nominal, t, key, rng, boot=(key == W))
                    r[key] = {"margin": p, "ci90": ci, "verdict": verdict(d, p, ci)}
                row[on] = r
            row["yield8_ls_margin"] = y8[name]["margin"][f"{W}|full|mixed"]
            out["rows"][name] = row
            print(f"{name[:60]:60s} LS {row['least squares, 7 points'][W]['margin']:7.3g} (y8 {row['yield8_ls_margin']:7.3g})"
                  f"  ends {row['two points, window ends'][W]['margin']:7.3g}", flush=True)

    # the verdict rule on every stored margin
    changes = []
    for name, r in y8.items():
        d = name.split("|")[0]
        for k, mval in r["margin"].items():
            ci = r["ci90"].get(k)
            new = verdict(d, mval, ci)
            old = r["verdict"].get(k)
            out["s2"].setdefault(name, {})[k] = new
            if old != new:
                changes.append((name, k, old, new, mval))
    out["s2_changes"] = changes

    # NMOS on the fixed window 0.3 to 0.7 V
    for name, rec in recs.items():
        if not name.startswith(NMOS + "|"):
            continue
        x, v, std, nominal, _ = CM.prepare(rec)
        keep = v <= 0.7 + 1e-9
        if v[keep & std].size < 4 or v.max() < 0.7 - 1e-9:
            continue
        x2, v2, std2, nom2 = x[:, keep], v[keep], std[keep], nominal[keep]
        c = name.split("|")[1]
        A = CM.residual_operator(v2, std2)
        p, ci = margin_ci(x2, v2, std2, A, nom2, Y8.tau(NMOS, c), W, rng)
        ps, cis = margin_ci(x2, v2, std2, A, nom2, Y8.tau(NMOS, c), W, rng, kind="shared")
        out["s4"][c] = {"margin": p, "ci90": ci, "shared": ps, "shared_ci90": cis,
                        "window_as_stored": [float(v.min()), float(v.max())],
                        "yield8_margin": y8.get(name, {}).get("margin", {}).get(f"{W}|full|mixed")}

    (OUT / "calibration_lines.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    report(out)


def report(out):
    L = ["## Calibration lines, verdict rule and fixed NMOS window", "",
         "Margins at the strictest point (99.99 %, 33.69 dec/V, untracked), levels set open-loop, per-channel calibration,",
         "closed form corrected for tau; [90 % bootstrap interval]; verdict with the 0.9-1.1 rule.", "",
         "Best pairs (4 K band): " + ", ".join(f"{d}: {p[0]:g}/{p[1]:g} V" for d, p in out["pairs"].items()), "",
         "| Design | Condition | Least squares, 7 points | Two points, ends | Two points, best pair | yield8 (IS) |",
         "|---|---|---|---|---|---|"]
    for name, row in out["rows"].items():
        d, c = name.split("|")
        cells = []
        for on in ("least squares, 7 points", "two points, window ends"):
            r = row[on][W]
            cells.append(f"{r['margin']:.3g} [{r['ci90'][0]:.3g}, {r['ci90'][1]:.3g}] {r['verdict']}")
        bp = [k for k in row if k.startswith("two points, best")]
        if bp:
            r = row[bp[0]][W]
            cells.append(f"{r['margin']:.3g} [{r['ci90'][0]:.3g}, {r['ci90'][1]:.3g}] {r['verdict']}")
        else:
            cells.append("–")
        L.append(f"| {d} | {c} | " + " | ".join(cells) + f" | {row['yield8_ls_margin']:.3g} |")
    L += ["", "Lowest margins at 99.9 % (33.69 and 10 dec/V), per calibration:"]
    for on in ("least squares, 7 points", "two points, window ends"):
        for key in (N99, REF):
            vals = [(row[on][key]["margin"], n) for n, row in out["rows"].items()]
            L.append(f"- {on}, {key}: {min(vals)[0]:.3g} ({min(vals)[1]})")
    L += ["", f"## Verdict changes under the 0.9-1.1 rule ({len(out['s2_changes'])})", ""]
    for name, k, old, new, mval in out["s2_changes"]:
        if k.endswith("|mixed") and ("full|" in k or "shared|" in k):
            L.append(f"- {name} {k}: {old} -> {new} ({mval:.3g})")
    L += ["", "## NMOS on 0.3 to 0.7 V", "", "| Condition | per channel | shared | as stored (window) |", "|---|---|---|---|"]
    for c, r in out["s4"].items():
        L.append(f"| {c} | {r['margin']:.3g} [{r['ci90'][0]:.3g}, {r['ci90'][1]:.3g}] | {r['shared']:.3g} | "
                 f"{r['yield8_margin'] if r['yield8_margin'] is None else round(r['yield8_margin'], 3)} "
                 f"({r['window_as_stored'][0]:g}-{r['window_as_stored'][1]:g} V) |")
    (OUT / "calibration_lines.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
