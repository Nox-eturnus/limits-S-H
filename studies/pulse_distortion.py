"""ESD diode area that still passes pulse distortion, and the nonlinearity allowed for the electrode itself.

The CZ pulse reaches the hold node through C_pulse, and while the switch is open the node only
shares charge. A voltage-dependent capacitance on the node therefore turns the drive into a distorted
barrier pulse. Quasi-static model (the gate lasts 50 ns, leakage is negligible):

    C_p (V - V_d) + Q_o(V) = C_p V_b + Q_o(V_b),

with Q_o the charge on every other capacitance of the node. The drive is V_d = v0 / k_b, where k_b is
the coupling measured with a 50 mV step at the bias V_b (as flow/cosim.insitu_calibration does), so
the error dv = V - V_b - v0 comes only from the nonlinearity. C_o(V) of the SPICE cells is recovered
from the couplings k(V) that the co-simulation measured (C_o = C_p (1/k - 1)) and interpolated between biases.

1. Validation: the model against the SPICE co-simulation (pulse_table of results/design_space.json, TG, s = 10 dec/V).
2. ESD threshold: the ESD part of C_o scaled with the diode area; the largest area per C_node at
   which the worst bias stays at 1e-3 and 1e-4.
3. Electrode: an extra capacitance with a constant slope dC/dV; the largest slope that passes.

Run:  python studies/pulse_distortion.py   (writes results/pulse_distortion.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flow import budget as B  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
F_PULSE = 0.5
V_T = (0.3, 0.6, 0.9, 1.2, 1.5)
V_FIT = (0.3, 0.6, 0.9, 1.2)     # 1.5 V: the pulse would leave the measured range (extrapolation)
STEP = 0.05
TARGETS = (1e-3, 1e-4)


def charge_fn(c_of_v, v_lo=0.0, v_hi=2.0, n=2001):
    """Q(V) = integral of C(V) dV on a fine grid (C(V) any callable)."""
    v = np.linspace(v_lo, v_hi, n)
    c = c_of_v(v)
    q = np.concatenate([[0.0], np.cumsum(0.5 * (c[1:] + c[:-1]) * np.diff(v))])
    return lambda x: np.interp(x, v, q), lambda x: np.interp(x, v, c)


def node_voltage(cp, q_o, c_o, vb, vd):
    """Solve C_p (V - V_d) + Q_o(V) = C_p V_b + Q_o(V_b) for V (Newton, vectorised)."""
    q0 = cp * vb + q_o(vb)
    v = vb + vd * cp / (cp + c_o(vb))
    for _ in range(30):
        f = cp * (v - vd) + q_o(v) - q0
        v = v - f / (cp + c_o(v))
    return v


def infidelity(lay, c_node, c_o_of_v, vb):
    cp = F_PULSE * c_node
    q_o, c_o = charge_fn(c_o_of_v)
    k_b = (node_voltage(cp, q_o, c_o, vb, np.array([STEP]))[0] - vb) / STEP
    v0 = lay.v0
    vd = np.zeros_like(v0)
    vd[:lay.n_gate] = v0[:lay.n_gate] / k_b
    v = node_voltage(cp, q_o, c_o, vb, vd)
    dv = v - vb - v0
    dv[lay.n_gate:] = 0.0
    return lay.excess_infidelity(dv)


def c_other_from_k(c_node, ks):
    """C_o(V) from the SPICE couplings at the five biases (monotone cubic, held flat beyond)."""
    cp = F_PULSE * c_node
    c = cp * (1.0 / np.asarray(ks) - 1.0)
    f = PchipInterpolator(V_T, c, extrapolate=False)
    return lambda v: f(np.clip(v, V_T[0], V_T[-1]))


def main():
    lay = B.layer(s_dec_per_v=10.0)
    tab = json.loads((ROOT / "results" / "design_space.json").read_text(encoding="utf-8"))["pulse_table"]
    tab = [p for p in tab if "f_pulse" in p]
    out = {"validation": [], "esd": [], "electrode": []}
    # 1. validation against SPICE
    for p in tab:
        c_o = c_other_from_k(p["c_node"], p["k"])
        for i, vb in enumerate(V_T):
            if vb not in V_FIT:
                continue
            fm = infidelity(lay, p["c_node"], c_o, vb)
            out["validation"].append({"c_node": p["c_node"], "esd": p["esd_area"], "v": vb,
                                      "model": fm, "spice": p["f_dyn"][i]})
    # 2. ESD area threshold: ESD part = C_o(esd 100) - C_o(esd 0), scaled with area
    by = {(p["c_node"], p["esd_area"]): p for p in tab}
    for c_node in sorted({p["c_node"] for p in tab}):
        c0 = c_other_from_k(c_node, by[(c_node, 0.0)]["k"])
        c100 = c_other_from_k(c_node, by[(c_node, 100.0)]["k"])

        def worst(area):
            c_o = lambda v: c0(v) + area / 100.0 * (c100(v) - c0(v))  # noqa: E731
            return max(infidelity(lay, c_node, c_o, vb) for vb in V_FIT)
        row = {"c_node": c_node, "worst_at": {a: worst(a) for a in (1.0, 3.0, 10.0, 30.0, 100.0)}}
        for tgt in TARGETS:
            lo, hi = 1e-3, 1e4
            if worst(hi) < tgt:
                row[f"area_{tgt:g}"] = float("inf")
                continue
            row[f"area_{tgt:g}"] = float(brentq(lambda a: np.log(max(worst(a), 1e-30) / tgt), lo, hi, xtol=1e-3))
        # one pulse amplitude shared by all electrodes: the SPICE results at 10 and 100 um^2, log-log
        g10, g100 = max(by[(c_node, 10.0)]["f_dyn_global_k"]), max(by[(c_node, 100.0)]["f_dyn_global_k"])
        p = np.log10(g100 / g10)
        row["global_k_exponent"] = float(p)
        for tgt in TARGETS:
            row[f"area_global_{tgt:g}"] = float(10.0 * (tgt / g10) ** (1.0 / p))
        # slope of the ESD capacitance per um^2 (100 um^2 pair, between 0.3 and 0.6 V)
        row["desd_dv_per_um2_0.3_0.6"] = float((c100(0.6) - c0(0.6) - c100(0.3) + c0(0.3)) / 0.3 / 100.0)
        out["esd"].append(row)
        print(f"C_node {c_node * 1e15:g} fF: area for 1e-3 {row['area_0.001']:.3g} um^2, 1e-4 {row['area_0.0001']:.3g} um^2",
              flush=True)
    # 3. electrode with a constant dC/dV on top of the linear node
    for c_node in (2e-13, 1e-12, 3e-12):
        base = lambda v, c=c_node: np.full_like(np.asarray(v, float), (1 - F_PULSE) * c)  # noqa: E731

        def f_of(slope, c_node=c_node, base=base):
            c_o = lambda v: base(v) + slope * (np.asarray(v, float) - 0.9)  # noqa: E731
            return infidelity(lay, c_node, c_o, 0.9)
        row = {"c_node": c_node, "f_at": {f"{s * 1e15:g} fF/V": f_of(s) for s in (1e-15, 3e-15, 10e-15, 30e-15)}}
        for tgt in TARGETS:
            row[f"slope_{tgt:g}"] = float(brentq(lambda s: np.log(f_of(s) / tgt), 1e-18, 1e-12, xtol=1e-19))
        out["electrode"].append(row)
        print(f"electrode, C_node {c_node * 1e15:g} fF: |dC/dV| for 1e-3 {row['slope_0.001'] * 1e15:.3g} fF/V, "
              f"1e-4 {row['slope_0.0001'] * 1e15:.3g} fF/V", flush=True)
    (OUT / "pulse_distortion.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    L = ["## Pulse distortion from a voltage-dependent node capacitance (TG, s = 10 dec/V, per-electrode k)", "",
         "### Model against the SPICE co-simulation", "", "| C_node | ESD (µm²) | bias (V) | model 1 − F | SPICE 1 − F |",
         "|---|---|---|---|---|"]
    for r in out["validation"]:
        L.append(f"| {r['c_node'] * 1e15:g} fF | {r['esd']:g} | {r['v']:g} | {r['model']:.2e} | {r['spice']:.2e} |")
    L += ["", "### Largest ESD pair area (worst bias 0.3-1.2 V)", "",
          "| C_node | area for 1e-3 | area for 1e-4 | shared k (SPICE, log-log): 1e-3 / 1e-4 | d(C_ESD)/dV per µm², 0.3-0.6 V |",
          "|---|---|---|---|---|"]
    for r in out["esd"]:
        L.append(f"| {r['c_node'] * 1e15:g} fF | {r['area_0.001']:.3g} µm² | {r['area_0.0001']:.3g} µm² | "
                 f"{r['area_global_0.001']:.3g} / {r['area_global_0.0001']:.3g} µm² | "
                 f"{r['desd_dv_per_um2_0.3_0.6'] * 1e18:.3g} aF/V |")
    L += ["", "### Largest slope dC/dV of an added electrode capacitance (bias 0.9 V)", "",
          "| C_node | dC/dV for 1e-3 | dC/dV for 1e-4 |", "|---|---|---|"]
    for r in out["electrode"]:
        L.append(f"| {r['c_node'] * 1e15:g} fF | {r['slope_0.001'] * 1e15:.3g} fF/V | {r['slope_0.0001'] * 1e15:.3g} fF/V |")
    L.append("")
    (OUT / "pulse_distortion.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
