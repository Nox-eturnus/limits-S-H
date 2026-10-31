"""Qubit-side bounds on the static budget, and the joint error allocation.

  Stark shift on both qubits   The untracked single-gate budget recomputed with equal and with opposite
                               Stark shifts (1e8 Hz/V) on both qubits; the frame-tracked budget removes all
                               single-qubit phases and should not depend on them.
  Non-exponential J(V)         log10 J made quadratic in V, with the local slope at the peak of the pulse
                               equal to s and the slope at the idle point either half of it (J steepens
                               towards the peak) or twice it (J saturates), against the pure exponential.
  Coherent error               rotation angle and diamond-norm error of the residual coherent error at each
                               budget, against the Pauli-twirled error of the same average infidelity.
  1/f budget                   for recalibration every 100 s, 1 h and 1 day.
  Joint allocation             at the strictest point (33.69 dec/V, 99.99 %) and at 10 dec/V, 99.9 %: the
                               operational static budget V_b is shared, in infidelity, between device 1/f
                               noise, random static offsets that change at every refresh (kT/C, sampled DAC
                               noise) and the deterministic offsets (worst-channel pedestal residual,
                               settling, droop), which add linearly as voltages. For the frame-tracked
                               conditional-phase error 1 - F = T (V / V_b)^2, so the deterministic offsets may
                               reach V_det = V_b sqrt(1 - I_dev / T - (s_kTC^2 + s_DAC^2) / V_b^2). The
                               pedestal margin is (V_det - eps) / e_ped, with eps = 0.1 V_b the settling
                               allowance. studies/allocation.py redoes the allocation with the untracked
                               budgets and the margins of studies/cell_margins.py.

Run:  python studies/qubit_bounds.py      (about 10 min; writes results/qubit_bounds.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import operational_budget as common  # noqa: E402
from flow import budget as B  # noqa: E402

ALPHA = B.STARK_BARTEE
KB = 1.380649e-23
_LOCAL = np.array([[1, 1, 1, 1], [0, 1, 0, 1], [0, 0, 1, 1]], float).T
_PROJ_COND = np.eye(4) - _LOCAL @ np.linalg.pinv(_LOCAL)
SLOPES = (3.87, 10.0, 33.69)
TARGETS = (1e-3, 1e-4)


def tracked_budget(lay, target):
    """Frame-tracked static budget, one gate (studies/repeated_gates.py, M = 1)."""
    best = np.inf
    for sign in (+1, -1):
        f = lambda x: B.phase_infidelity(_PROJ_COND @ lay.phase_errors(B.static(lay, sign * x))) - target  # noqa: E731
        xs = np.geomspace(1e-7, 0.2, 200)
        vals = np.array([f(x) for x in xs])
        i = np.nonzero(vals >= 0)[0]
        if i.size:
            i = i[0]
            best = min(best, xs[0] if i == 0 else brentq(f, xs[i - 1], xs[i], xtol=xs[i - 1] * 1e-6))
    return float(best)


def untracked_budget(lay, target):
    return float(min(B.max_static(lay, target, +1), B.max_static(lay, target, -1)))


class QuadraticExchange:
    """log10 J = log10 J_idle + a V + b V^2, with slope a at idle and s_peak at the peak of the pulse."""

    def __init__(self, s_peak, ratio_idle, j_idle, j_peak):
        self.j_idle = j_idle
        a = ratio_idle * s_peak
        decades = np.log10(j_peak / j_idle)
        v_p = 2 * decades / (s_peak + a)
        self.a, self.b, self.s = a, (s_peak - a) / (2 * v_p), s_peak

    def j_of_v(self, v):
        v = np.asarray(v, dtype=float)
        return self.j_idle * 10.0 ** (self.a * v + self.b * v * v)

    def v_of_j(self, j):
        L = np.log10(np.asarray(j, dtype=float) / self.j_idle)
        if abs(self.b) < 1e-15:
            return L / self.a
        return (-self.a + np.sqrt(self.a ** 2 + 4 * self.b * L)) / (2 * self.b)


def quadratic_layer(s, ratio):
    lay = B.layer(s_dec_per_v=s)
    j_peak = lay.cfg.j_idle + lay.amp                  # the calibrated peak exchange of the exponential gate
    lay.ex = QuadraticExchange(s, ratio, lay.cfg.j_idle, j_peak)
    lay._calibrate()
    return lay


def main():
    bud = common.budgets()
    out = {"stark": [], "jv": [], "angles": [], "one_over_f": [], "allocation": {}}
    # Stark shift on both qubits
    for s in SLOPES:
        for case, (q1, q2) in {"one qubit": (0.0, ALPHA), "equal": (ALPHA, ALPHA), "opposite": (-ALPHA, ALPHA)}.items():
            lay = B.layer(s_dec_per_v=s, stark_q1=q1, stark_q2=q2)
            for t in TARGETS:
                out["stark"].append({"s": s, "case": case, "target": t, "untracked": untracked_budget(lay, t),
                                     "tracked": tracked_budget(lay, t)})
        print("stark", s, flush=True)
    # non-exponential J(V), s = 10 dec/V at the peak
    for ratio in (1.0, 0.5, 2.0):
        lay = quadratic_layer(10.0, ratio) if ratio != 1.0 else B.layer(s_dec_per_v=10.0)
        for t in TARGETS:
            out["jv"].append({"s_peak": 10.0, "idle_slope_ratio": ratio, "target": t,
                              "untracked": untracked_budget(lay, t), "tracked": tracked_budget(lay, t)})
        print("jv", ratio, flush=True)
    # residual coherent error at each operational budget
    for key, b in bud.items():
        r = common.POINTS[key][1]
        theta = float(np.arcsin(np.sqrt(r / 0.8)))       # frame-tracked: exp(-i theta ZZ), 1 - F = 0.8 sin^2 theta
        out["angles"].append({"point": key, "target": r, "zz_angle_rad": theta, "conditional_phase_rad": 4 * theta,
                              "diamond_coherent": 2 * np.sin(theta), "diamond_twirled": 2 * 1.25 * r})
    # 1/f budget against the recalibration interval
    for s in SLOPES:
        lay = B.layer(s_dec_per_v=s)
        for t in TARGETS:
            row = {"s": s, "target": t}
            for lab, f_lo in (("100 s", 1e-2), ("1 h", 1 / 3600), ("1 day", 1 / 86400)):
                row[lab] = B.max_one_over_f(lay, t, f_lo)
            out["one_over_f"].append(row)
    # joint allocation
    tail = json.loads((OUT / "tail_surrogate.json").read_text(encoding="utf-8"))["designs"]
    ktc = float(np.sqrt(KB * 4.2 / 1e-12))
    for key, (s, t) in (("s33.69_t0.0001", (33.69, 1e-4)), ("s10_t0.001", (10.0, 1e-3))):
        vb = bud[key]["operational"]
        a_b = next(r["100 s"] for r in out["one_over_f"] if r["s"] == s and r["target"] == t)
        rows = []
        for dev_a in (0.0, 9e-6, 49e-6):
            for s_dac in (0.0, 20e-6, 50e-6, 188e-6):
                share = (dev_a / a_b) ** 2 + (ktc ** 2 + s_dac ** 2) / vb ** 2
                v_det = vb * np.sqrt(1 - share) if share < 1 else 0.0
                row = {"device_1f_1Hz": dev_a, "dac_rms": s_dac, "infidelity_share_used": share, "v_det": v_det}
                for d, label in (("NMOS, 0.3 V underdrive|4 K proxy", "NMOS"),
                                 ("bootstrapped (transistor level), 0.3 V underdrive|4 K proxy (100 channels)", "bootstrapped"),
                                 ("TG + dummies|4 K proxy (100 channels)", "TG + dummies")):
                    e = tail[d]["per_channel"]
                    row[label] = {"pedestal_margin_alone": vb / e,
                                  "pedestal_margin_joint": max(v_det - 0.1 * vb, 0.0) / e,
                                  "droop_left": max(v_det - 0.1 * vb - e, 0.0)}
                rows.append(row)
        # largest DAC noise for which the bootstrapped switch keeps a joint margin of one, quiet device
        e = tail["bootstrapped (transistor level), 0.3 V underdrive|4 K proxy (100 channels)"]["per_channel"]
        need = (e + 0.1 * vb) / vb
        dac_max = vb * np.sqrt(max(1 - need ** 2 - (9e-6 / a_b) ** 2 - ktc ** 2 / vb ** 2, 0.0))
        out["allocation"][key] = {"v_b": vb, "one_over_f_budget": a_b, "ktc_rms_4K_1pF": ktc, "rows": rows,
                                  "dac_rms_max_bootstrapped": float(dac_max)}
    (OUT / "qubit_bounds.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def table(out):
    L = ["## Untracked and tracked single-gate static budget with the Stark shift on one or both qubits (mV)", "",
         "| s (dec/V) | target | one qubit: untracked / tracked | equal on both | opposite on both |", "|---|---|---|---|---|"]
    for s in SLOPES:
        for t in TARGETS:
            r = {x["case"]: x for x in out["stark"] if x["s"] == s and x["target"] == t}
            L.append(f"| {s:g} | {t:g} | " + " | ".join(f"{r[c]['untracked'] * 1e3:.3g} / {r[c]['tracked'] * 1e3:.3g}"
                                                         for c in ("one qubit", "equal", "opposite")) + " |")
    L += ["", "## Non-exponential J(V), slope 10 dec/V at the peak (mV)", "",
          "| idle slope / peak slope | target | untracked | tracked |", "|---|---|---|---|"]
    for r in out["jv"]:
        L.append(f"| {r['idle_slope_ratio']:g} | {r['target']:g} | {r['untracked'] * 1e3:.3g} | {r['tracked'] * 1e3:.3g} |")
    L += ["", "## Residual coherent error at the operational budgets", "",
          "| point | target | ZZ angle (mrad) | conditional phase (mrad) | diamond norm, coherent | diamond norm, twirled |",
          "|---|---|---|---|---|---|"]
    for r in out["angles"]:
        L.append(f"| {r['point']} | {r['target']:g} | {r['zz_angle_rad'] * 1e3:.1f} | {r['conditional_phase_rad'] * 1e3:.1f} | "
                 f"{r['diamond_coherent']:.3g} | {r['diamond_twirled']:.3g} |")
    L += ["", "## 1/f budget at 1 Hz (µV/√Hz) against the recalibration interval", "",
          "| s (dec/V) | target | 100 s | 1 h | 1 day |", "|---|---|---|---|---|"]
    for r in out["one_over_f"]:
        L.append(f"| {r['s']:g} | {r['target']:g} | {r['100 s'] * 1e6:.0f} | {r['1 h'] * 1e6:.0f} | {r['1 day'] * 1e6:.0f} |")
    for key, a in out["allocation"].items():
        L += ["", f"## Joint allocation at {key}: V_b = {a['v_b'] * 1e6:.0f} µV, 1/f budget {a['one_over_f_budget'] * 1e6:.0f} µV/√Hz, "
              f"kT/C at 4.2 K on 1 pF {a['ktc_rms_4K_1pF'] * 1e6:.1f} µV", "",
              "| device 1/f at 1 Hz (µV/√Hz) | DAC noise sampled (µV rms) | share of target used | V_det (µV) "
              "| NMOS: margin alone / joint | bootstrapped | TG + dummies |", "|---|---|---|---|---|---|---|"]
        for r in a["rows"]:
            L.append(f"| {r['device_1f_1Hz'] * 1e6:g} | {r['dac_rms'] * 1e6:g} | {r['infidelity_share_used']:.2f} | {r['v_det'] * 1e6:.0f} | "
                     + " | ".join(f"{r[d]['pedestal_margin_alone']:.2f} / {r[d]['pedestal_margin_joint']:.2f}"
                                  for d in ("NMOS", "bootstrapped", "TG + dummies")) + " |")
        L.append(f"\nLargest sampled DAC noise for a joint margin of one (bootstrapped, 9 µV/√Hz device): "
                 f"{a['dac_rms_max_bootstrapped'] * 1e6:.0f} µV rms")
    (OUT / "qubit_bounds.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    table(main())
