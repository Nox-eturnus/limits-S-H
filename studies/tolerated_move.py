"""Largest move from a tuned level that a switch tolerates.

A level tuned on the qubits and then moved open-loop by Delta carries the change of its deviation from the
per-channel calibration line over the move. Delta_max is the largest move whose worst-of-10^6 margin is one, at the
strictest point (99.99 %, 33.69 dec/V, untracked budget) and at 99.9 % and the same slope.

A. The designs of Figure 6, the steep bands, 1.5 or 2 times the mismatch, and GF180 (closed form of
   studies/array_yield.py with the tail correction of studies/tail_corrected.py). Below the spacing of the standard
   held voltages, the change over a move Delta is the chord slope between adjacent standard voltages times Delta times
   c(Delta): the largest ratio of local to chord slope at 1 mV (3.22 for 0.2 V spacing, 1.62 for 0.1 V;
   studies/calibration_accuracy.py), the overstatement of interpolated moves measured on the fine windows at 20 and
   50 mV (1.66 and 1.29; studies/system_operation.py) and the largest between-point factor (1.16) at the spacing,
   log-log in between. Where Delta_max exceeds the spacing, chords between standard voltages at most Delta apart are
   used with the between-point factor. A 90 % interval from 200 bootstrap resamples of the Monte Carlo channels.
B. Switches of 5 to 40 um sized for settling (nominal, 20 mV grid, studies/calibration_accuracy.py part B data): the
   change of the deviation from a cubic spline through it, for every move on a 0.5 mV grid. By exact scaling, a switch
   of width W on C_node is the switch of width W x 1 pF / C_node on 1 pF.

Run:  python studies/tolerated_move.py      (about 15 min; writes results/tolerated_move.{json,md})
"""
import json
import sys
import zlib
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import cell_margins as CM  # noqa: E402
import array_yield as Y  # noqa: E402
import tail_corrected as Y8  # noqa: E402
import calibration_accuracy as A12  # noqa: E402

W, N99 = common.WORST, "s33.69_t0.001"
B = CM.RA.budgets()
KEYS = {"99.99": W, "99.9": N99}
RATIO = {0.1: 1.617, 0.2: 3.222}          # results/calibration_accuracy.md, 1 mV moves
BETWEEN = 1.156                            # largest between-point factor (calibration_accuracy, window line)
N_BOOT = 200


def records():
    sky = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    sky.update(json.loads((ROOT / "results" / "mc_cell_extra_pedestals.json").read_text(encoding="utf-8")))
    gf = json.loads((ROOT / "results" / "gf180_pedestals.json").read_text(encoding="utf-8"))
    names = json.loads((ROOT / "results" / "calibration_nonlinear.json").read_text(encoding="utf-8"))["rows"]
    out = {n: sky.get(n) or gf.get(n) for n in names}
    for d in Y8.FIG6:
        for c in A12.STEEP_MM:
            if f"{d}|{c}" in sky:
                out[f"{d}|{c}"] = sky[f"{d}|{c}"]
    return {k: v for k, v in out.items() if v}


def c_move(delta, spacing):
    """Factor by which the change over a move delta (V) exceeds the chord-slope estimate: the local-to-chord slope
    ratio at 1 mV, the overstatement of interpolated moves measured on the fine windows at 20 and 50 mV (1.66, 1.29)
    and the between-point factor at the spacing; log-log in between."""
    pts = ((1e-3, RATIO[spacing]), (0.02, 1.66), (0.05, 1.29), (spacing, BETWEEN))
    xs, ys = np.log([p[0] for p in pts]), np.log([p[1] for p in pts])
    return float(np.exp(np.interp(np.log(delta), xs, ys)))


def dmax_mc(x, v, std, t, b):
    """Delta_max (V) for one set of channels, and the margin of a 1 mV move."""
    A = CM.residual_operator(v, std)
    mu, C = x.mean(0), np.cov(x, rowvar=False)
    idx = np.where(std)[0]
    spacing = round(float(v[idx[1]] - v[idx[0]]), 2)
    D = np.array([(A[idx[i + 1]] - A[idx[i]]) / (v[idx[i + 1]] - v[idx[i]]) * 1e-3 for i in range(len(idx) - 1)])
    sd = lambda M: np.sqrt(np.clip(np.einsum("ij,jk,ik->i", M, C, M), 0, None))  # noqa: E731
    mc = Y.margin_closed(D @ mu * (1 + t), sd(D) * (1 + t), b)       # margin of the chord-slope change over 1 mV
    m1 = mc / c_move(1e-3, spacing)
    if spacing * 1e3 * c_move(spacing, spacing) > mc:                 # Delta_max below the spacing
        lo, hi = 1e-4, spacing
        for _ in range(60):
            mid = np.sqrt(lo * hi)
            lo, hi = (mid, hi) if mid * 1e3 * c_move(mid, spacing) <= mc else (lo, mid)
        return float(lo), m1
    vs = v[idx]
    spans = np.arange(spacing, vs[-1] - vs[0] + 1e-9, spacing)

    def ok(span):        # the margin falls as the span grows (the set of pairs only grows)
        P = np.array([A[idx[k]] - A[idx[j]] for j in range(len(idx)) for k in range(j + 1, len(idx))
                      if vs[k] - vs[j] <= span + 1e-9])
        return Y.margin_closed(P @ mu * BETWEEN * (1 + t), sd(P) * BETWEEN * (1 + t), b) >= 1

    lo, hi = 0, len(spans) - 1             # largest passing index by bisection; spans[0] passes by construction
    if ok(spans[hi]):
        return float(spans[hi]), m1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if ok(spans[mid]) else (lo, mid)
    return float(spans[lo]), m1


def part_a():
    out = {}
    for name, rec in records().items():
        x, v, std, nominal, _ = CM.prepare(rec)
        d = name.split("|")[0]
        t = Y8.TAU_MAX if name.startswith("GF180") else Y8.tau(d, name.split("|")[1])
        idx = np.where(std)[0]
        window = float(v[idx[-1]] - v[idx[0]])
        rng = np.random.default_rng(common.name_seed(name) + 13)
        row = {"window_V": window}
        for kn, key in KEYS.items():
            point, m1 = dmax_mc(x, v, std, t, B[key])
            boots = [dmax_mc(x[rng.integers(0, len(x), len(x))], v, std, t, B[key])[0] for _ in range(N_BOOT)]
            row[kn] = {"dmax_V": point, "ci90_V": [float(np.percentile(boots, 5)), float(np.percentile(boots, 95))],
                       "margin_1mV": m1, "whole_window": point >= window - 1e-9}
        out[name] = row
        print(f"{name[:62]:62s} " + "  ".join(f"{kn}: {row[kn]['dmax_V'] * 1e3:.3g} mV "
                                              f"[{row[kn]['ci90_V'][0] * 1e3:.3g}, {row[kn]['ci90_V'][1] * 1e3:.3g}]"
                                              for kn in KEYS), flush=True)
    return out


def dmax_nominal(v, r, b):
    cs = CubicSpline(v, r)
    h = 0.0005
    vv = np.arange(v[0], v[-1] + 1e-12, h)
    rv = cs(vv)
    slope = float(np.max(np.abs(cs(vv, 1))))
    if slope * h > b:
        return b / slope
    best = 0.0
    for n in range(1, len(vv)):
        if np.max(np.abs(rv[n:] - rv[:-n])) <= b:
            best = n * h
        else:
            break
    return best


def part_b():
    import mc_cell_settling as M10
    import mc_cell_variants as M9
    import mc_cell as M
    import settling_time_constant as T11
    r9 = A12.A10.nominal_runs(ROOT / "results" / "mc_cell_variants_channels.jsonl", lambda r: r["design"].startswith("TG sized for settling"))
    r10 = A12.A10.nominal_runs(ROOT / "results" / "mc_cell_settling_channels.jsonl", lambda r: " sized for settling" in r["design"])
    taus = {k: r["tau_node"] for k, r in json.loads((ROOT / "results" / "settling_and_partition.json").read_text())["wide"]["rows"].items()}
    out = {}
    for arch in T11.ARCHS:
        for w in M10.WIDE:
            name, src = (M9.wide_name(w), r9) if arch == "TG" else (M10.wide_name(arch, w), r10)
            for c in ("300 K", "4 K proxy"):
                d = src.get((name, c))
                if not d:
                    continue
                v = np.array(sorted(x for x, (p, tr) in d.items() if abs(tr) < M.R.TRACK_TOL))
                stop = next((i for i in range(1, len(v)) if v[i] - v[i - 1] > 0.021), len(v))
                v = v[:stop]
                p = np.array([d[x][0] for x in v])
                std = np.array([abs((x - 0.3) / 0.2 - round((x - 0.3) / 0.2)) < 1e-6 for x in v])
                inside = v <= v[std].max() + 1e-9
                v, p, std = v[inside], p[inside], std[inside]
                r = A12.C11.poly_operator(v, std, 1)[0] @ p
                row = {"tau_node": taus[f"{arch}|{w:g}|{c}"], "window_V": float(v[-1] - v[0])}
                for kn, key in KEYS.items():
                    row[kn] = dmax_nominal(v, r, B[key]["b_eq"])
                out[f"{arch}|{w:g}|{c}"] = row
                print(f"{arch:14s} {w:4g} um {c:10s} tau {row['tau_node'] * 1e9:.3g} ns  dmax 99.99 "
                      f"{row['99.99'] * 1e3:.3g} mV, 99.9 {row['99.9'] * 1e3:.3g} mV", flush=True)
    return out


def report(out):
    L = ["# Largest tolerated move from a tuned level", "",
         "## A. Designs of Figure 6 and GF180 (worst of 10^6, per-channel line, tail-corrected; 90 % bootstrap interval)", "",
         "| condition | window (V) | 99.99 %, 33.69 dec/V: Delta_max (mV) [90 %] | margin at 1 mV | 99.9 %: Delta_max (mV) [90 %] |",
         "|---|---|---|---|---|"]
    for n, r in out["A"].items():
        a, b = r["99.99"], r["99.9"]
        f = lambda z: (f"{z['dmax_V'] * 1e3:.3g}" + (" (whole window)" if z["whole_window"] else "")  # noqa: E731
                       + f" [{z['ci90_V'][0] * 1e3:.3g}, {z['ci90_V'][1] * 1e3:.3g}]")
        L.append(f"| {n} | {r['window_V']:.2g} | {f(a)} | {a['margin_1mV']:.3g} | {f(b)} |")
    L += ["", "Smallest Delta_max over the SKY130 conditions (Figure 6 bands, trees, steep, mismatch) and over GF180, per design:", ""]
    designs = sorted({n.split("|")[0] for n in out["A"]})
    for d in designs:
        rs = [(n, r) for n, r in out["A"].items() if n.split("|")[0] == d]
        for kn in ("99.99", "99.9"):
            n, r = min(rs, key=lambda z: z[1][kn]["dmax_V"])
            L.append(f"- {d} {kn}: {r[kn]['dmax_V'] * 1e3:.3g} mV [{r[kn]['ci90_V'][0] * 1e3:.3g}, "
                     f"{r[kn]['ci90_V'][1] * 1e3:.3g}] ({n.split('|')[1]})")
    L += ["", "## B. Switches sized for settling (nominal, 20 mV grid, spline)", "",
          "| key | tau (ns) | Delta_max 99.99 % (mV) | Delta_max 99.9 % (mV) |", "|---|---|---|---|"]
    for k, r in out["B"].items():
        L.append(f"| {k} | {r['tau_node'] * 1e9:.3g} | {r['99.99'] * 1e3:.3g} | {r['99.9'] * 1e3:.3g} |")
    (OUT / "tolerated_move.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


def main():
    out = {"B": part_b(), "A": part_a()}
    (OUT / "tolerated_move.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    report(out)


if __name__ == "__main__":
    main()
