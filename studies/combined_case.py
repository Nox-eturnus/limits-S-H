"""Analyses of the combined worst case and of the quantities quoted with it.

A. Margins of the combined worst case (line, quadratic, line over 0.4 V, shared line), next to each factor alone.
B. The factor by which the deviation of the mean channel from its calibration curve may grow before the margin at the
   strictest point falls to one, smallest over the Figure 6 conditions, and the spread of that deviation.
C. A relative spread of the switch width and of the overlap capacitance between channels, added to the surrogate
   through the sensitivity of the nominal pedestal to each.
D. Shared-error budgets divided by 1 + S, with S the summed cross-coupling of the other gates to the tunnel barrier.
E. The pulse-driver bound C_o v0^2 / k with the connection to the qubits on each node (dense array), and the limits
   of the study rescaled to a 70 fF node.
Run:  python studies/combined_case.py          (about 2 min; writes results/combined_case.{json,md})
      python studies/combined_case.py move     (writes results/combined_case_move.json)
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import calibration_accuracy as A12  # noqa: E402  (puts the earlier studies on the path)
import pulse_driver_stages as PD  # noqa: E402

Y, Y8, MARG, B, W = A12.Y, A12.Y8, A12.CM, A12.B, A12.W
N99, REF = A12.N99, A12.REF
COMBINED = "4 K, steep (T_eff 20 K), mismatch x 2, tree of one reticle"
SINGLE = ("4 K proxy", "4 K, steep (T_eff 20 K)", "4 K, mismatch x 2", "4 K, tree, one reticle")
DECIDING = ("NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive", "TG + dummies", "TG, no ESD")
KB = 1.380649e-23


def load_sky():
    sky = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    sky.update(json.loads((ROOT / "results" / "mc_cell_extra_pedestals.json").read_text(encoding="utf-8")))
    return sky


# ---------------------------------------------------------------- A
def part_a(sky):
    new = json.loads((OUT / "mc_cell_combined_pedestals.json").read_text(encoding="utf-8"))
    out = {}
    for d in Y8.FIG6:
        row = {}
        for c in SINGLE + (COMBINED,):
            rec = new.get(f"{d}|{c}") or sky.get(f"{d}|{c}")
            if rec is None:
                continue
            t = Y8.TAU_MAX if c == COMBINED else Y8.tau(d, c)
            r = A12.calib_row(rec, t)
            x, v, std, nominal, _ = MARG.prepare(rec)
            m, s = Y.moments(x, v, std, MARG.residual_operator(v, std), nominal, "shared")
            row[c] = {"window_V": [float(v.min()), float(v.max())],
                      "shared": float(Y.margin_closed(m * (1 + t), s * (1 + t), B[W])),
                      "shared_99.9": float(Y.margin_closed(m * (1 + t), s * (1 + t), B[N99])),
                      **{k: {"99.99": r[k][W]["margin_std"], "99.9": r[k][N99]["margin_std"]}
                         for k in ("line", "quadratic", "window")}}
        out[d] = row
    return out


# ---------------------------------------------------------------- B
def scale_to_one(x, A, keep, t, key=W):
    xs = x[:, keep]
    mu, C = xs.mean(0), np.cov(xs, rowvar=False)
    m = A @ mu
    s = np.sqrt(np.clip(np.diag(A @ C @ A.T), 0, None))

    def marg(c):
        return Y.margin_closed(c * m * (1 + t), s * (1 + t), B[key])

    if marg(1e3) > 1:
        return 1e3, float(np.abs(m).max())
    lo, hi = 1e-3, 1e3
    for _ in range(40):
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if marg(mid) > 1 else (lo, mid)
    return float(np.sqrt(lo * hi)), float(np.abs(m).max())


def part_b(sky):
    gf = json.loads((ROOT / "results" / "gf180_pedestals.json").read_text(encoding="utf-8"))
    out = {}
    names = [(d, c, sky[f"{d}|{c}"], Y8.tau(d, c)) for d in Y8.FIG6 for c in Y8.S6_BANDS if f"{d}|{c}" in sky]
    names += [(n.split("|")[0], n.split("|")[1], r, Y8.TAU_MAX) for n, r in gf.items()]
    for d, c, rec, t in names:
        x, v, std, _, _ = MARG.prepare(rec)
        row = out.setdefault(d, {})
        for kind in ("line", "quadratic", "window"):
            per = [scale_to_one(x, A, keep, t) for A, H, keep in A12.ops(v, std, kind)]
            cmin, dev = min(per)
            row.setdefault(kind, {})[c] = {"scale": cmin, "mean_dev_uV": max(p[1] for p in per) * 1e6}
    summ = {}
    for d, row in out.items():
        summ[d] = {}
        for kind, by_c in row.items():
            worst = min(by_c.items(), key=lambda t: t[1]["scale"])
            devs = [r["mean_dev_uV"] for c, r in by_c.items() if "tree" not in c]
            summ[d][kind] = {"scale_min": worst[1]["scale"], "at": worst[0], "dev_min_uV": min(devs),
                             "dev_max_uV": max(devs), "dev_ratio": max(devs) / max(min(devs), 1e-12)}
    return {"by_condition": out, "summary": summ}


# ---------------------------------------------------------------- C
WIDTH_PAIR = {   # design: (other-width design, ln(W_other / W_design))
    "NMOS, 0.3 V underdrive": ("NMOS, 0.3 V underdrive, W 1", np.log(1 / 0.42)),
    "bootstrapped (transistor level), 0.3 V underdrive": ("bootstrapped (transistor level), W 1", np.log(1 / 0.42)),
    "TG + dummies": ("TG + dummies, W 0.84", np.log(0.84 / 1.0)),
    "TG, no ESD": ("TG, no ESD, W 0.42", np.log(0.42 / 1.0)),
}


def part_c(sky):
    out = {}
    for d in DECIDING:
        rec = sky[f"{d}|4 K proxy"]
        t = Y8.tau(d, "4 K proxy")
        x, v, std, nominal, _ = MARG.prepare(rec)
        x, v, nominal = x[:, std], v[std], nominal[std]
        st = np.ones(len(v), bool)

        def grad(a, b, dln):
            va, vb = np.asarray(a["v"]), np.asarray(b["v"])
            ga = np.array([np.asarray(a["nominal"])[np.argmin(np.abs(va - u))] for u in v])
            gb = np.array([np.asarray(b["nominal"])[np.argmin(np.abs(vb - u))] for u in v])
            return (gb - ga) / dln

        other, dln = WIDTH_PAIR[d]
        g_w = grad(rec, sky[f"{other}|4 K proxy"], dln)
        g_ov = grad(sky[f"{d}|4 K, overlap capacitances x 0.7"], sky[f"{d}|4 K, overlap capacitances x 1.3"],
                    np.log(1.3 / 0.7))
        A = MARG.residual_operator(v, st)
        mu, C = x.mean(0), np.cov(x, rowvar=False)
        line = np.polyval(np.polyfit(v, nominal, 1), v)
        row = {"dped_dlnW_uV": (g_w * 1e6).round(1).tolist(), "dped_dlnCov_uV": (g_ov * 1e6).round(1).tolist()}
        for eps in (0.0, 0.02, 0.05):
            C2 = C + eps ** 2 * (np.outer(g_w, g_w) + np.outer(g_ov, g_ov))
            m_l, s_l = A @ mu, np.sqrt(np.clip(np.diag(A @ C2 @ A.T), 0, None))
            m_s, s_s = mu - line, np.sqrt(np.clip(np.diag(C2), 0, None))
            row[f"{eps:g}"] = {"line": float(Y.margin_closed(m_l * (1 + t), s_l * (1 + t), B[W])),
                               "shared": float(Y.margin_closed(m_s * (1 + t), s_s * (1 + t), B[W])),
                               "shared_99.9_10": float(Y.margin_closed(m_s * (1 + t), s_s * (1 + t), B[REF]))}
        out[d] = row
    return out


# ---------------------------------------------------------------- D
def part_d():
    out = {}
    for key, name in ((N99, "99.9%, 33.69"), (W, "99.99%, 33.69"), (REF, "99.9%, 10")):
        b = B[key]
        out[name] = {f"S={s:g}": {"b_eq_uV": b["b_eq"] / (1 + s) * 1e6, "b_ind_uV": b["b_ind"] / (1 + s) * 1e6}
                     for s in (-0.5, 0.0, 0.5, 1.0)}
    return out


# ---------------------------------------------------------------- E
def part_e():
    mv = json.loads((ROOT / "results" / "tolerated_move.json").read_text(encoding="utf-8"))["B"]
    out = {"dense": {}, "node70": {}}
    # dense array: every hold node carries the fan-in connection (3 to 4.5 pF to ground) besides the pulse capacitor;
    # E = C_other v0^2 / k per pulse, at least C_other v0^2
    for s in PD.SLOPES:
        a = PD.v0(s)
        row = {}
        for co in (3e-12, 4.5e-12):
            for k in (0.5, 0.9, 1.0):
                e = co * a ** 2 / k
                row[f"C_o {co * 1e12:g} pF, k {k:g}"] = {
                    "energy_fJ": e * 1e15,
                    **{f"{t * 1e6:g} us": {"power_mW": PD.N_BAR * e / t * 1e3, "stage": PD.coldest(PD.N_BAR * e / t)}
                       for t in PD.ROUNDS}}
        out["dense"][f"{s:g}"] = row
    # 70 fF node: every limit derived for 1 pF, rescaled
    c, r = 70e-15, 0.07
    lim = {"select-line coupling (aF): 99.99% 33.69 / 99.9% 33.69 / 99.9% 10": [0.06e3 * r, 0.19e3 * r, 0.65e3 * r],
           "pulse-line coupling to a neighbour running a CZ (fF), 99.99%: 3.87 / 10 / 33.69": [0.57 * r, 0.96 * r, 1.2 * r],
           "allowance for electrode, connection and switch (fF): k 0.5 / k 0.9": [c * 0.5 * 1e15, c * 0.1 * 1e15],
           "kT/C noise (uV): 4.2 K / 1.2 K / 0.14 K": [float(np.sqrt(KB * T / c) * 1e6) for T in (4.2, 1.2, 0.14)],
           "droop at 5.5 aA (uV/s)": 5.5e-18 / c * 1e6}

    def interp(arch, band, key):
        w = np.array([5.0, 10.0, 20.0, 40.0])
        y = np.array([mv[f"{arch}|{x:g}|{band}"][key] for x in w])
        return float(np.exp(np.interp(np.log(1 / 0.07), np.log(w), np.log(y))))

    def interp_w(arch, band, key, weq):
        w = np.array([5.0, 10.0, 20.0, 40.0])
        y = np.array([mv[f"{arch}|{x:g}|{band}"][key] for x in w])
        return float(np.exp(np.interp(np.log(weq), np.log(w), np.log(y))))

    lim["equivalent width on 1 pF (um): 1 um switch / 0.42 um switch"] = [1 / 0.07, 0.42 / 0.07]
    lim["largest move, 1 um TG (mV, nominal), 99.99% 33.69: 300 K / 4 K"] = [
        interp("TG", b, "99.99") * 1e3 for b in ("300 K", "4 K proxy")]
    lim["largest move, 1 um TG with dummies (mV): 300 K / 4 K"] = [
        interp("TG + dummies", b, "99.99") * 1e3 for b in ("300 K", "4 K proxy")]
    lim["largest move, 0.42 um NMOS (mV): 300 K / 4 K"] = [
        interp_w("NMOS", b, "99.99", 0.42 / 0.07) * 1e3 for b in ("300 K", "4 K proxy")]
    lim["largest move, 0.42 um bootstrapped (mV): 300 K / 4 K"] = [
        interp_w("bootstrapped", b, "99.99", 0.42 / 0.07) * 1e3 for b in ("300 K", "4 K proxy")]
    out["node70"] = lim
    return out


def main():
    sky = load_sky()
    out = {"A": part_a(sky), "B": part_b(sky), "C": part_c(sky), "D": part_d(), "E": part_e()}
    (OUT / "combined_case.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["# Combined worst case and related quantities", "", "## A. Combined worst case (strictest point; 99.9% at 33.69 dec/V in brackets)", "",
         "| design | condition | window (V) | line | quadratic | line over 0.4 V | shared line |", "|---|---|---|---|---|---|---|"]
    for d, row in out["A"].items():
        for c, r in row.items():
            L.append(f"| {d} | {c} | {r['window_V'][0]:g} to {r['window_V'][1]:g} | " + " | ".join(
                f"{r[k]['99.99']:.3g} ({r[k]['99.9']:.3g})" for k in ("line", "quadratic", "window"))
                + f" | {r['shared']:.3g} ({r['shared_99.9']:.3g}) |")
    L += ["", "## B. Factor by which the deviation of the mean channel may grow before the margin is one (smallest over conditions)", "",
          "| design | line (at) | quadratic (at) | line over 0.4 V (at) | mean deviation from a line over conditions (uV) |", "|---|---|---|---|---|"]
    for d, s in out["B"]["summary"].items():
        L.append(f"| {d} | " + " | ".join(f"{s[k]['scale_min']:.3g} ({s[k]['at']})" for k in ("line", "quadratic", "window"))
                 + f" | {s['line']['dev_min_uV']:.3g} to {s['line']['dev_max_uV']:.3g} (x{s['line']['dev_ratio']:.2g}) |")
    L += ["", "## C. Width and overlap spread between channels, 4 K band, strictest point: line per channel / shared line (shared at 99.9%, 10 dec/V)", "",
          "| design | no spread | 2% | 5% |", "|---|---|---|---|"]
    for d, r in out["C"].items():
        L.append(f"| {d} | " + " | ".join(
            f"{r[e]['line']:.3g} / {r[e]['shared']:.3g} ({r[e]['shared_99.9_10']:.3g})" for e in ("0", "0.02", "0.05")) + " |")
    L += ["", "## D. Shared-error budgets with summed cross-coupling S (uV): equal signs / independent signs", "",
          "| point | S = -0.5 | 0 | 0.5 | 1 |", "|---|---|---|---|---|"]
    for n, r in out["D"].items():
        L.append(f"| {n} | " + " | ".join(f"{v['b_eq_uV']:.0f} / {v['b_ind_uV']:.0f}" for v in r.values()) + " |")
    L += ["", "## E. Dense array: pulse-driver bound with the fan-in capacitance on the node (10^6 barriers)", "",
          "| s | case | energy (fJ) | 1 us rounds (mW, stage) | 10 us rounds (mW, stage) |", "|---|---|---|---|---|"]
    for s, row in out["E"]["dense"].items():
        for n, r in row.items():
            L.append(f"| {s} | {n} | {r['energy_fJ']:.3g} | {r['1 us']['power_mW']:.3g} ({r['1 us']['stage']}) | "
                     f"{r['10 us']['power_mW']:.3g} ({r['10 us']['stage']}) |")
    L += ["", "## E. Limits rescaled to a 70 fF node", ""]
    for k, v in out["E"]["node70"].items():
        L.append(f"- {k}: " + (", ".join(f"{x:.3g}" for x in v) if isinstance(v, list) else f"{v:.3g}"))
    (OUT / "combined_case.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))




# ---------------------------------------------------------------- F (run separately: python studies/combined_case.py move)
def part_f():
    """Largest move from a tuned level in the combined worst case (studies/tolerated_move.py, same closed form)."""
    sys.path.insert(0, str(ROOT / "studies"))
    import tolerated_move as M13
    new = json.loads((OUT / "mc_cell_combined_pedestals.json").read_text(encoding="utf-8"))
    out = {}
    for name, rec in new.items():
        x, v, std, nominal, _ = MARG.prepare(rec)
        idx = np.where(std)[0]
        row = {"window_V": float(v[idx[-1]] - v[idx[0]])}
        for kn, key in M13.KEYS.items():
            point, m1 = M13.dmax_mc(x, v, std, Y8.TAU_MAX, B[key])
            row[kn] = {"dmax_V": point, "margin_1mV": m1}
        out[name] = row
        print(name[:50], {k: (round(r["dmax_V"] * 1e3, 1), round(r["margin_1mV"], 1)) for k, r in row.items() if k != "window_V"},
              row["window_V"])
    (OUT / "combined_case_move.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "move":
        part_f()
    else:
        main()
