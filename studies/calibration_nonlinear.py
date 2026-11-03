"""Nonlinear per-channel calibration, calibration-point error and a common window.

Closed-form worst-of-10^6 margins (studies/array_yield.py, corrected for the tail optimism of studies/tail_corrected.py,
300 bootstrap resamples, verdicts of studies/calibration_lines.py) for
  line       the least-squares line through the seven standard held voltages,
  quadratic  a least-squares quadratic through the same seven voltages (no extra measurement),
  shared     the line, plus a correction of the mean-channel deviation measured once on K = 10 reference channels;
             the correction misses the mean by the error of a 10-channel mean, taken at its 95th percentile,
             1.645 s / sqrt(10), with the same sign at every held voltage,
for the six designs of Figure 6 in seven bands and two tree sources, and for the GF180 designs (tau = 9.8 %).

Calibration-point error: each of the seven points is measured with a white error sigma_m equal to a tenth of the
equal-sign untracked budget of the target. The fitted curve then misses the pedestal at a held voltage by a random
error of variance sigma_m^2 h_jj (h = hat matrix of the fit), independent from channel to channel and fixed for each
channel, which adds to the variance of the mismatch part. Every calibration is evaluated without and with it.

Common window: each design calibrated by a line over every 0.4 V window of its standard held voltages (the window of
a group of electrodes in an isolated well); the margin is the smallest over the windows.

Run:  python studies/calibration_nonlinear.py     (about 5 min; writes results/calibration_nonlinear.{json,md})
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
import tail_corrected as Y8  # noqa: E402
import calibration_lines as C9  # noqa: E402

W, N99, REF = common.WORST, "s33.69_t0.001", common.REF
KEYS = (W, N99, REF)
B = CM.RA.budgets()
FIG6, BANDS = Y8.FIG6, Y8.S6_BANDS
K_REF = 10
Z95 = 1.645
WINDOW = 0.4
N_BOOT = 300


def poly_operator(v, cal, deg):
    """Residual operator r = A p of a least-squares polynomial of degree deg fitted at the voltages in cal, and the
    hat matrix H (prediction at every v from the points in cal)."""
    X = np.vander(v[cal], deg + 1)
    H = np.zeros((len(v), len(v)))
    H[:, cal] = np.vander(v, deg + 1) @ np.linalg.pinv(X)
    return np.eye(len(v)) - H, H


def moments(x, v, std, A, H, kind, sig_m):
    mu = x.mean(0)
    Cx = np.cov(x, rowvar=False)
    m = (A @ mu)[std]
    var = np.clip(np.diag(A @ Cx @ A.T), 0, None)[std]
    if kind == "shared":       # mean-channel deviation corrected from K reference channels
        m = Z95 * np.sqrt(var / K_REF)
    var = var + sig_m ** 2 * np.diag(H)[std]
    return m, np.sqrt(var)


def margin(x, v, std, A, H, kind, key, t, noise, rng, boot):
    sig_m = B[key]["b_eq"] / 10 if noise else 0.0
    m, s = moments(x, v, std, A, H, kind, sig_m)
    point = Y.margin_closed(m * (1 + t), s * (1 + t), B[key])
    ci = None
    if boot:
        bs = []
        for _ in range(N_BOOT):
            xb = x[rng.integers(0, len(x), len(x))]
            mb, sb = moments(xb, v, std, A, H, kind, sig_m)
            bs.append(Y.margin_closed(mb * (1 + t), sb * (1 + t), B[key]))
        ci = [float(np.quantile(bs, 0.05)), float(np.quantile(bs, 0.95))]
    return point, ci


def analyse(d, rec, t, rng):
    x, v, std, nominal, _ = CM.prepare(rec)
    A1, H1 = poly_operator(v, std, 1)
    A2, H2 = poly_operator(v, std, 2)
    ops = {"line": (A1, H1, "full"), "quadratic": (A2, H2, "full"), "shared": (A1, H1, "shared")}
    row = {}
    for on, (A, H, kind) in ops.items():
        for noise in (False, True):
            r = {}
            for key in KEYS:
                p, ci = margin(x, v, std, A, H, kind, key, t, noise, rng, boot=(key == W))
                r[key] = {"margin": p, "ci90": ci, "verdict": C9.verdict(d, p, ci)}
            row[f"{on}{', noise' if noise else ''}"] = r
    # lines over 0.4 V windows of the standard voltages
    idx = np.where(std)[0]
    vs = v[idx]
    wins = []
    for a in range(len(idx)):
        b = [i for i, vv in zip(idx, vs) if vs[a] - 1e-9 <= vv <= vs[a] + WINDOW + 1e-9]
        if v[b[-1]] - v[b[0]] < WINDOW - 1e-9:
            continue
        keep = np.zeros(len(v), bool)
        keep[b] = True
        x2, v2, s2 = x[:, keep], v[keep], np.ones(keep.sum(), bool)
        A, H = poly_operator(v2, s2, 1)
        p, _ = margin(x2, v2, s2, A, H, "full", W, t, False, rng, boot=False)
        wins.append((p, float(v2[0]), float(v2[-1])))
    if wins:
        row["window"] = {"margin": min(wins)[0], "worst": [min(wins)[1], min(wins)[2]],
                         "all": [[a, b, c] for a, b, c in wins]}
    return row


def main():
    rng = np.random.default_rng(11)
    sky = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    gf = json.loads((ROOT / "results" / "gf180_pedestals.json").read_text(encoding="utf-8"))
    out = {"rows": {}}
    for d in FIG6:
        for c in BANDS:
            name = f"{d}|{c}"
            if name in sky:
                out["rows"][name] = analyse(d, sky[name], Y8.tau(d, c), rng)
                r = out["rows"][name]
                print(f"{name[:62]:62s} line {r['line'][W]['margin']:6.3g} quad {r['quadratic'][W]['margin']:6.3g} "
                      f"shared {r['shared'][W]['margin']:6.3g} quad+noise {r['quadratic, noise'][W]['margin']:6.3g} "
                      f"window {r.get('window', {}).get('margin', float('nan')):6.3g}", flush=True)
    for name, rec in gf.items():
        d = name.split("|")[0].replace("GF180 ", "").split(", 0.3-1.5 V")[0].split(", W 0.42")[0]
        out["rows"][name] = analyse(d, rec, Y8.TAU_MAX, rng)
        r = out["rows"][name]
        print(f"{name[:62]:62s} line {r['line'][W]['margin']:6.3g} quad {r['quadratic'][W]['margin']:6.3g} "
              f"shared {r['shared'][W]['margin']:6.3g} quad+noise {r['quadratic, noise'][W]['margin']:6.3g}", flush=True)
    (OUT / "calibration_nonlinear.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    report(out)


def report(out):
    cols = ("line", "line, noise", "quadratic", "quadratic, noise", "shared", "shared, noise")
    L = ["## Nonlinear calibration, calibration-point error and a common window", "",
         "Closed-form worst-of-10^6 margins at the strictest point (99.99 %, 33.69 dec/V, untracked), levels set open-loop,",
         "corrected for tau; [90 % bootstrap interval] and verdict (resolved outside 0.9 to 1.1).", "",
         "| Design | Condition | " + " | ".join(cols) + " | 0.4 V window, line (worst window) |",
         "|---|---|" + "---|" * (len(cols) + 1)]
    for name, row in out["rows"].items():
        d, c = name.split("|")
        cells = []
        for on in cols:
            r = row[on][W]
            cells.append(f"{r['margin']:.3g} [{r['ci90'][0]:.3g}, {r['ci90'][1]:.3g}] {r['verdict']}")
        w = row.get("window")
        cells.append(f"{w['margin']:.3g} ({w['worst'][0]:g}-{w['worst'][1]:g} V)" if w else "–")
        L.append(f"| {d} | {c} | " + " | ".join(cells) + " |")
    L += ["", "Smallest margin over the Figure 6 bands and trees (SKY130), per design and calibration:", "",
          "| Design | " + " | ".join(cols) + " | window | 99.9 %, 33.69: line / quadratic, noise | 99.9 %, 10: line / quadratic, noise |",
          "|---|" + "---|" * (len(cols) + 3)]
    summ = {}
    for d in FIG6:
        rows = [r for n, r in out["rows"].items() if n.startswith(d + "|")]
        mins = {on: min(r[on][W]["margin"] for r in rows) for on in cols}
        mins["window"] = min(r["window"]["margin"] for r in rows if "window" in r)
        for key in (N99, REF):
            for on in ("line", "quadratic, noise"):
                mins[f"{key}|{on}"] = min(r[on][key]["margin"] for r in rows)
        summ[d] = mins
        L.append(f"| {d} | " + " | ".join(f"{mins[on]:.3g}" for on in cols) + f" | {mins['window']:.3g} | "
                 f"{mins[f'{N99}|line']:.3g} / {mins[f'{N99}|quadratic, noise']:.3g} | "
                 f"{mins[f'{REF}|line']:.3g} / {mins[f'{REF}|quadratic, noise']:.3g} |")
    out["summary"] = summ
    (OUT / "calibration_nonlinear.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT / "calibration_nonlinear.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
