"""Accuracy that the calibration needs, margins between calibration points, switches sized for settling and
the joint allocation for daily retuning.

A. For the six designs of Figure 6 in every SKY130 condition of studies/calibration_nonlinear.py, the two steepest
   bands and 1.5 or 2 times the mismatch, and the GF180 designs: the closed-form worst-of-10^6 margin
   (studies/array_yield.py, tail optimism of studies/tail_corrected.py) of a per-channel line, a per-channel quadratic
   and a line over every 0.4 V window, at the standard held voltages only and at every simulated voltage (the fine grid
   of the 4 K band lies between the standard voltages), and the white error sigma of each calibration point at which
   the margin on every simulated voltage falls to one. The fit error at a voltage j has variance sigma^2 (H H^T)_jj,
   with H the hat matrix of the fit.
B. Switches of 5 to 40 um sized for settling (nominal, 20 mV grid, within the calibrated range): margins for levels
   set open-loop (line, quadratic, 0.4 V window, on every grid voltage), for moves of 50 mV (line, quadratic) at 99.9 %
   and 99.99 %, and for moves of 1 mV from the largest slope of a cubic spline through the deviation; the shortest node
   time constant by log-log interpolation (studies/settling_time_constant.py).
C. Moves of 1 mV in GF180 and for the SKY130 designs of Figure 6: the slope of the deviation between adjacent
   standard voltages, closed form, multiplied by the largest ratio of spline slope to chord slope found in B.
D. The joint allocation (studies/allocation.py, studies/system_operation.py) with the 1/f budget for retuning once a
   day instead of every 100 s.
E. Pair-to-pair spread (studies/pair_spread_nonlinear.py) without calibration-point error, line and quadratic.

Run:  python studies/calibration_accuracy.py      (about 5 min; argument b reruns B and C only)
      writes results/calibration_accuracy.{json,md}
"""
import json
import sys
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
import calibration_nonlinear as C11  # noqa: E402
import settling_and_partition as A10  # noqa: E402
import settling_time_constant as T11  # noqa: E402
import pair_spread as Q  # noqa: E402

W, N99, REF = common.WORST, "s33.69_t0.001", common.REF
B = CM.RA.budgets()
WIN = 0.4
STEEP_MM = ("4 K, steep (T_eff 30 K)", "4 K, steep (T_eff 20 K)", "4 K, mismatch x 1.5", "4 K, mismatch x 2")


# ---------------------------------------------------------------- A
def ops(v, std, kind):
    """[(A, H, keep)] for a calibration kind: residual and hat operators on the voltages in keep."""
    if kind in ("line", "quadratic"):
        A, H = C11.poly_operator(v, std, 1 if kind == "line" else 2)
        return [(A, H, np.ones(len(v), bool))]
    out = []
    vs = v[std]
    for a in vs:
        keep = (v >= a - 1e-9) & (v <= a + WIN + 1e-9)
        if v[keep & std].max() - v[keep & std].min() < WIN - 1e-9:
            continue
        A, H = C11.poly_operator(v[keep], std[keep], 1)
        out.append((A, H, keep))
    return out


def margin_at(x, A, H, keep, evalm, key, t, sig):
    xs = x[:, keep]
    mu, C = xs.mean(0), np.cov(xs, rowvar=False)
    m = (A @ mu)[evalm]
    var = np.clip(np.diag(A @ C @ A.T), 0, None) + sig ** 2 * np.diag(H @ H.T)
    return Y.margin_closed(m * (1 + t), np.sqrt(var[evalm]) * (1 + t), B[key])


def calib_row(rec, t):
    x, v, std, nominal, _ = CM.prepare(rec)
    row = {"fine": bool((~std).any())}
    for kind in ("line", "quadratic", "window"):
        r = {}
        for key in (W, N99, REF):
            per = []
            for A, H, keep in ops(v, std, kind):
                vk, sk = v[keep], std[keep]
                m_std = margin_at(x, A, H, keep, sk, key, t, 0.0)
                m_all = margin_at(x, A, H, keep, np.ones(len(vk), bool), key, t, 0.0)
                if m_all <= 1 or key != W:
                    s_req = 0.0
                else:
                    lo, hi = 0.0, 2 * B[key]["b_eq"]
                    for _ in range(25):
                        mid = 0.5 * (lo + hi)
                        if margin_at(x, A, H, keep, np.ones(len(vk), bool), key, t, mid) > 1:
                            lo = mid
                        else:
                            hi = mid
                    s_req = lo
                per.append((m_all, m_std, s_req))
            m_all, m_std, s_req = min(per)          # the worst window (or the single fit)
            r[key] = {"margin_std": m_std, "margin_all": m_all, "sigma_req": s_req,
                      "sigma_req_over_beq": s_req / B[key]["b_eq"], "sigma_req_min": min(p[2] for p in per)}
        row[kind] = r
    return row


def part_a():
    sky = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    sky.update(json.loads((ROOT / "results" / "mc_cell_extra_pedestals.json").read_text(encoding="utf-8")))
    gf = json.loads((ROOT / "results" / "gf180_pedestals.json").read_text(encoding="utf-8"))
    names = json.loads((ROOT / "results" / "calibration_nonlinear.json").read_text(encoding="utf-8"))["rows"]
    out = {}
    for name in names:
        rec = sky.get(name) or gf.get(name)
        d, c = name.split("|")
        t = Y8.TAU_MAX if name.startswith("GF180") else Y8.tau(d, c)
        out[name] = calib_row(rec, t)
    for d in Y8.FIG6:
        for c in STEEP_MM:
            name = f"{d}|{c}"
            if name in sky:
                out[name] = calib_row(sky[name], Y8.tau(d, c))
    for name, r in out.items():
        print(f"{name[:60]:60s} " + " ".join(
            f"{k} {r[k][W]['margin_all']:.3g}/{r[k][W]['margin_std']:.3g} s {r[k][W]['sigma_req'] * 1e6:.1f}uV"
            for k in ("line", "quadratic", "window")), flush=True)
    return out


# ---------------------------------------------------------------- B
def spline_slope(v, r):
    cs = CubicSpline(v, r)
    vv = np.linspace(v[0], v[-1], int(round((v[-1] - v[0]) / 0.0005)) + 1)
    return float(np.max(np.abs(cs(vv, 1))))


def chord_ratio(v, r, spacing):
    """Largest spline slope over the largest chord slope between grid points the given spacing apart."""
    step = int(round(spacing / 0.02))
    ch = max(abs(r[i + step] - r[i]) / (v[i + step] - v[i]) for i in range(len(v) - step))
    return spline_slope(v, r) / ch


def wide_rows():
    import mc_cell_settling as M10
    import mc_cell_variants as M9
    import mc_cell as M
    r9 = A10.nominal_runs(ROOT / "results" / "mc_cell_variants_channels.jsonl", lambda r: r["design"].startswith("TG sized for settling"))
    r10 = A10.nominal_runs(ROOT / "results" / "mc_cell_settling_channels.jsonl", lambda r: " sized for settling" in r["design"])
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
                inside = v <= v[std].max() + 1e-9          # the calibrated range only (no extrapolation)
                v, p, std = v[inside], p[inside], std[inside]
                row = {"tau_node": taus[f"{arch}|{w:g}|{c}"], "window_V": [float(v[0]), float(v[-1])]}
                res = {}
                for kind in ("line", "quadratic", "window"):
                    worst_all, worst_std = 0.0, 0.0
                    for A, H, keep in ops(v, std, kind):
                        r = A @ p[keep]
                        worst_all = max(worst_all, float(np.abs(r).max()))
                        worst_std = max(worst_std, float(np.abs(r[std[keep]]).max()))
                    res[kind] = (worst_all, worst_std)
                rl = C11.poly_operator(v, std, 1)[0] @ p
                rq = C11.poly_operator(v, std, 2)[0] @ p
                mv = {}
                for lab, r in (("line", rl), ("quadratic", rq)):
                    mv[lab] = max(abs(r[k] - r[j]) for j in range(len(v)) for k in range(j + 1, len(v))
                                  if v[k] - v[j] <= 0.05 + 1e-9)
                chord1 = float(np.max(np.abs(np.diff(rl)) / np.diff(v)))
                spl1 = spline_slope(v, rl)
                row["between_point_factor"] = {k: res[k][0] / res[k][1] for k in res}
                row["slope_ratio_spline_chord20"] = spl1 / chord1
                row["slope_ratio_spline_chord100"] = chord_ratio(v, rl, 0.1)
                row["slope_ratio_spline_chord200"] = chord_ratio(v, rl, 0.2)
                for key, kn in ((W, "99.99"), (N99, "99.9")):
                    b = B[key]["b_eq"]
                    row[kn] = {"open_line": b / res["line"][0], "open_quadratic": b / res["quadratic"][0],
                               "open_window": b / res["window"][0], "move50_line": b / mv["line"],
                               "move50_quadratic": b / mv["quadratic"], "move1_chord": b / (chord1 * 1e-3),
                               "move1_spline": b / (spl1 * 1e-3)}
                out[f"{arch}|{w:g}|{c}"] = row
    return out


def part_b():
    rows = wide_rows()
    tau = {}
    for arch in T11.ARCHS:
        tau[arch] = {}
        for kn in ("99.99", "99.9"):
            for met in ("open_line", "open_quadratic", "open_window", "move50_line", "move50_quadratic"):
                per = []
                for c in ("300 K", "4 K proxy"):
                    rs = [x for k, x in rows.items() if k.startswith(arch + "|") and k.endswith("|" + c)]
                    per.append(T11.crossing([x["tau_node"] for x in rs], [x[kn][met] for x in rs]))
                tau[arch][f"{kn}|{met}"] = max(per)
    return {"rows": rows, "tau_min": tau}


# ---------------------------------------------------------------- C
def part_c(ratio, which="gf"):
    if which == "gf":
        recs = json.loads((ROOT / "results" / "gf180_pedestals.json").read_text(encoding="utf-8"))
    else:                                                   # SKY130: the Figure-6 conditions of calib11
        sky = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
        names = json.loads((ROOT / "results" / "calibration_nonlinear.json").read_text(encoding="utf-8"))["rows"]
        sky.update(json.loads((ROOT / "results" / "mc_cell_extra_pedestals.json").read_text(encoding="utf-8")))
        recs = {n: sky[n] for n in names if n in sky}
        recs.update({f"{d}|{c}": sky[f"{d}|{c}"] for d in Y8.FIG6 for c in STEEP_MM if f"{d}|{c}" in sky})
    out = {}
    for name, rec in recs.items():
        x, v, std, nominal, _ = CM.prepare(rec)
        A = CM.residual_operator(v, std)
        mu, C = x.mean(0), np.cov(x, rowvar=False)
        idx = np.where(std)[0]
        D = np.array([(A[idx[i + 1]] - A[idx[i]]) / (v[idx[i + 1]] - v[idx[i]]) * 1e-3 for i in range(len(idx) - 1)])
        m = D @ mu
        s = np.sqrt(np.clip(np.einsum("ij,jk,ik->i", D, C, D), 0, None))
        spacing = round(float(v[idx[1]] - v[idx[0]]), 2)
        rr = ratio[spacing]
        t = Y8.TAU_MAX if which == "gf" else Y8.tau(*name.split("|"))
        out[name] = {"spacing": spacing, "ratio": rr,
                     "move1": Y.margin_closed(m * rr * (1 + t), s * rr * (1 + t), B[W])}
    return out


# ---------------------------------------------------------------- D
def part_d():
    qb = json.loads((ROOT / "results" / "qubit_bounds.json").read_text(encoding="utf-8"))["one_over_f"]
    ratios = [r["100 s"] / r["1 day"] for r in qb]
    f2 = max(ratios) ** 2                                      # device share x (a_100s / a_day)^2
    al = json.loads((ROOT / "results" / "allocation.json").read_text(encoding="utf-8"))
    s20 = []
    dmap = {"NMOS": Y8.NMOS, "bootstrapped": Y8.BOOT, "TG + dummies": Y8.TGD}
    for key, pt in al["points"].items():
        for r in pt["rows"]:
            dev = (r["device"] / pt["one_over_f_budget"]) ** 2
            share = r["share"] + dev * (f2 - 1)
            f = max(np.sqrt(max(1 - share, 0.0)) - 0.1, 0.0)
            row = {"point": key, "device": r["device"], "dac": r["dac"], "share": share}
            for k, d in dmap.items():
                t = Y8.tau(d, "4 K proxy")
                row[k] = {"alone": r[k]["alone"] / (1 + t), "joint": r[k]["alone"] * f / (1 + t)}
            s20.append(row)
    pt = al["points"][W]
    r9 = [r for r in pt["rows"] if abs(r["device"] - 9e-6) < 1e-9 and r["dac"] == 0][0]
    share9 = r9["share"] + (9e-6 / pt["one_over_f_budget"]) ** 2 * (f2 - 1)
    lims = {}
    for k, d in dmap.items():
        m = r9[k]["alone"] / (1 + Y8.tau(d, "4 K proxy"))
        lims[k] = float(pt["b_ind"] * np.sqrt(max(1 - share9 - (0.1 + 1 / m) ** 2, 0)))
    s7 = json.loads((ROOT / "results" / "system_operation.json").read_text(encoding="utf-8"))["measured_devices"]
    lab = {"NMOS": Y8.NMOS, "bootstrapped": Y8.BOOT, "T-switch + OTA": Y8.TSWO, "TG + dummies": Y8.TGD, "TG": Y8.TG,
           "TG with ESD": Y8.TGE}
    s21 = []
    for r in s7:
        ktc = r["share_9"] - (9e-6 / r["one_over_f"]) ** 2
        sh = {n: (n * 1e-6 / r["one_over_f"]) ** 2 * f2 + ktc for n in (9, 49)}
        row = {"device": r["device"], "s": r["s"], "target": r["target"], "share_9": sh[9], "share_49": sh[49]}
        for k, d in lab.items():
            t = Y8.tau(d, "4 K proxy")
            full = r["designs"][k]["full"] / (1 + t)
            row[k] = {"full": full, "shared": r["designs"][k]["shared"] / (1 + t),
                      "joint_49": full * max(np.sqrt(max(1 - sh[49], 0.0)) - 0.1, 0.0)}
        s21.append(row)
    return {"f2": f2, "allocation": s20, "dac_limit_V": lims, "operating_points": s21}


# ---------------------------------------------------------------- E
def part_e():
    recs = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    tabs = json.loads((ROOT / "results" / "pair_spread.json").read_text(encoding="utf-8"))["tables"]
    out = {}
    for pn in ("33.69 dec/V, 99.99%",):
        tab = {k: (np.array(v) if k != "nominal" else v) for k, v in tabs[pn].items()}
        for d in Y8.FIG6:
            x, v, std, nominal, _ = CM.prepare(recs[f"{d}|4 K proxy"])
            tau = Y8.tau(d, "4 K proxy")
            for cal, deg in (("line", 1), ("quadratic", 2)):
                A, H = C11.poly_operator(v, std, deg)
                m, sd = C11.moments(x, v, std, A, H, "full", 0.0)
                out[f"{d}|{pn}|{cal}"] = {sn: Q.margin_joint(m * (1 + tau), sd * (1 + tau), Q.rule(tab, ss, sa))[0]
                                          for sn, (ss, sa) in Q.SPREADS.items()}
    return out


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "b":          # rerun B and C only, keep A, D, E
        out = json.loads((OUT / "calibration_accuracy.json").read_text(encoding="utf-8"))
        out["B"] = part_b()
        rows = out["B"]["rows"].values()
        ratio = {0.1: max(r["slope_ratio_spline_chord100"] for r in rows),
                 0.2: max(r["slope_ratio_spline_chord200"] for r in rows)}
        out["C"] = part_c(ratio)
        out["C_sky"] = part_c(ratio, "sky")
        (OUT / "calibration_accuracy.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
        report(out)
        return
    out = {"A": part_a()}
    out["B"] = part_b()
    rows = out["B"]["rows"].values()
    ratio = {0.1: max(r["slope_ratio_spline_chord100"] for r in rows),
             0.2: max(r["slope_ratio_spline_chord200"] for r in rows)}
    out["C"] = part_c(ratio)
    out["C_sky"] = part_c(ratio, "sky")
    out["D"] = part_d()
    out["E"] = part_e()
    (OUT / "calibration_accuracy.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    report(out)


def report(out):
    L = ["# Calibration accuracy, settling widths and allocation", "", "## A. Calibrations: margin on every simulated voltage / at the standard voltages "
         "only, and the per-point accuracy for a margin of one (strictest point)", "",
         "| condition | line | quadratic | 0.4 V window line | sigma_req line / quadratic / window (uV) |",
         "|---|---|---|---|---|"]
    for n, r in out["A"].items():
        L.append(f"| {n} | " + " | ".join(f"{r[k][W]['margin_all']:.3g} / {r[k][W]['margin_std']:.3g}"
                                         for k in ("line", "quadratic", "window")) + " | "
                 + " / ".join(f"{r[k][W]['sigma_req'] * 1e6:.1f}" for k in ("line", "quadratic", "window")) + " |")
    L += ["", "Smallest over conditions (SKY130 Figure-6 conditions incl. trees, steep bands, mismatch; GF180 separate):", ""]
    for grp, pred in (("SKY130", lambda n: not n.startswith("GF180")), ("GF180", lambda n: n.startswith("GF180"))):
        for k in ("line", "quadratic", "window"):
            rs = [(n, r[k][W]) for n, r in out["A"].items() if pred(n)]
            ma = min(rs, key=lambda z: z[1]["margin_all"])
            fac = max(z[1]["margin_std"] / z[1]["margin_all"] for z in rs)
            ok = [z for z in rs if z[1]["margin_all"] > 1]
            sr = min(ok, key=lambda z: z[1]["sigma_req"]) if ok else None
            L.append(f"- {grp} {k}: smallest margin {ma[1]['margin_all']:.3g} ({ma[0]}); largest std/all factor {fac:.3f}; "
                     + (f"smallest sigma_req among passing {sr[1]['sigma_req'] * 1e6:.1f} uV = "
                        f"{sr[1]['sigma_req_over_beq']:.3f} b_eq ({sr[0]})" if sr else "none passes"))
    L += ["", "## B. Switches sized for settling (nominal, 20 mV grid)", "",
          "| key | tau (ns) | between-point factor line / quad / window | spline/chord 20 mV | 99.99: open line / quad / window | "
          "50 mV line / quad | 1 mV chord / spline | 99.9: 50 mV line / quad |", "|---|---|---|---|---|---|---|---|"]
    for k, r in out["B"]["rows"].items():
        a, b = r["99.99"], r["99.9"]
        f = r["between_point_factor"]
        L.append(f"| {k} | {r['tau_node'] * 1e9:.3g} | {f['line']:.3f} / {f['quadratic']:.3f} / {f['window']:.3f} | "
                 f"{r['slope_ratio_spline_chord20']:.3f} | {a['open_line']:.3g} / {a['open_quadratic']:.3g} / "
                 f"{a['open_window']:.3g} | {a['move50_line']:.3g} / {a['move50_quadratic']:.3g} | "
                 f"{a['move1_chord']:.3g} / {a['move1_spline']:.3g} | {b['move50_line']:.3g} / {b['move50_quadratic']:.3g} |")
    L += ["", "Shortest node time constant (ns), largest over 300 K and the 4 K band:", "",
          "| arch | " + " | ".join(next(iter(out["B"]["tau_min"].values()))) + " |",
          "|---|" + "---|" * len(next(iter(out["B"]["tau_min"].values())))]
    for a, r in out["B"]["tau_min"].items():
        L.append(f"| {a} | " + " | ".join(f"{x * 1e9:.3g}" for x in r.values()) + " |")
    L += ["", "## C. GF180 1 mV moves (strictest point, closed form, slope ratio applied)", ""]
    for n, r in out["C"].items():
        L.append(f"- {n}: {r['move1']:.3g} (spacing {r['spacing']} V, ratio {r['ratio']:.3f})")
    if "C_sky" in out:
        L += ["", "## C2. SKY130 Figure-6 designs, 1 mV moves, same method", ""]
        for n, r in out["C_sky"].items():
            L.append(f"- {n}: {r['move1']:.3g} (spacing {r['spacing']} V, ratio {r['ratio']:.3f})")
    L += ["", f"## D. Joint allocation, 1/f budget for daily retuning (device share x {out['D']['f2']:.3f})", ""]
    for r in out["D"]["allocation"]:
        L.append(f"- {r['point']} dev {r['device'] * 1e6:g} dac {r['dac'] * 1e6:g}: share {r['share']:.3g}; "
                 + "; ".join(f"{k} {r[k]['alone']:.3g} / {r[k]['joint']:.3g}" for k in ("NMOS", "bootstrapped", "TG + dummies")))
    L.append("- DAC limits (strictest, 9 uV/rtHz): " + ", ".join(f"{k} {v * 1e6:.0f} uV" for k, v in out["D"]["dac_limit_V"].items()))
    for r in out["D"]["operating_points"]:
        L.append(f"- {r['device']} s {r['s']} t {r['target']}: share 9/49 {r['share_9']:.3g}/{r['share_49']:.3g}; "
                 + "; ".join(f"{k} {r[k]['full']:.3g}/{r[k]['shared']:.3g}/{r[k]['joint_49']:.3g}" for k in
                             ("NMOS", "bootstrapped", "TG + dummies", "TG", "T-switch + OTA")))
    L += ["", "## E. Pair spread without calibration-point error (strictest point)", ""]
    for k, r in out["E"].items():
        L.append(f"- {k}: " + ", ".join(f"{s} {x:.3g}" for s, x in r.items()))
    (OUT / "calibration_accuracy.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
