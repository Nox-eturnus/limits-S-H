"""Pulse distortion by a voltage-dependent node capacitance, under the calibration an experiment uses.

studies/design_space.py calibrates the CZ amplitude of each electrode from its small-signal coupling k,
measured with a 50 mV step at the held voltage (flow/cosim.insitu_calibration). A voltage-dependent node
capacitance then leaves the difference between the small-signal and the large-signal coupling over the
pulse, plus the change of pulse shape. Four calibrations are compared with the charge-balance model of
studies/pulse_distortion.py (which reproduces the co-simulation to within 20 %):

  k, per electrode    drive = v0 / k_b (the in-situ calibration of the co-simulation)
  k, shared           drive = v0 / k_ref, one coupling measured at 0.9 V for every electrode
  qubit-level         the drive amplitude of each electrode is set on the qubit (conditional phase) and the
                      single-qubit phases are recalibrated, as in device practice: min over a of the gate
                      infidelity with optimal Z angles, minus that of the nominal gate
  predistortion       the drive is computed from the charge balance with an estimate of C_o(V) whose
                      change from its value at the held voltage is 10 % too large, so that the node follows
                      the nominal pulse up to the model error

For each calibration and for s = 3.87, 10 and 33.69 dec/V the script gives the largest area of each ESD
diode of the pair and the largest slope dC/dV of an electrode capacitance at which the worst held voltage
keeps 99.9 % and 99.99 %. Held voltages are 0.3 to 1.2 V where the node stays inside the range where C_o(V)
was measured (bias + pulse <= 1.6 V), i.e. 0.3 to 0.9 V at 3.87 dec/V.

Run:  python studies/qubit_calibration.py     (about 15 min; writes results/qubit_calibration.{json,md})
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import pulse_distortion as PD  # noqa: E402
from flow import budget as B  # noqa: E402

SLOPES = (3.87, 10.0, 33.69)
MODES = ("k_per_electrode", "k_shared", "qubit_level", "predistortion")
TARGETS = (1e-3, 1e-4)
V_REF = 0.9
EST_ERR = 0.10
V_MAX = 1.6
_LAY = {}


def lay_for(s):
    if s not in _LAY:
        _LAY[s] = B.layer(s_dec_per_v=s)
    return _LAY[s]


def biases(lay):
    return [vb for vb in PD.V_FIT if vb + lay.v0.max() <= V_MAX + 1e-9]


def drive_k(lay, cp, q_o, c_o, vb, k):
    vd = np.zeros_like(lay.v0)
    vd[:lay.n_gate] = lay.v0[:lay.n_gate] / k
    return vd


def node_dv(lay, cp, q_o, c_o, vb, vd):
    v = PD.node_voltage(cp, q_o, c_o, vb, vd)
    dv = v - vb - lay.v0
    dv[lay.n_gate:] = 0.0
    return dv


def k_small(cp, q_o, c_o, vb):
    return (PD.node_voltage(cp, q_o, c_o, vb, np.array([PD.STEP]))[0] - vb) / PD.STEP


def infidelity(lay, c_node, c_o_of_v, vb, mode, c_est_of_v=None):
    cp = PD.F_PULSE * c_node
    q_o, c_o = PD.charge_fn(c_o_of_v)
    if mode == "k_per_electrode":
        return lay.excess_infidelity(node_dv(lay, cp, q_o, c_o, vb, drive_k(lay, cp, q_o, c_o, vb, k_small(cp, q_o, c_o, vb))))
    if mode == "k_shared":
        return lay.excess_infidelity(node_dv(lay, cp, q_o, c_o, vb, drive_k(lay, cp, q_o, c_o, vb, k_small(cp, q_o, c_o, V_REF))))
    if mode == "qubit_level":
        base = drive_k(lay, cp, q_o, c_o, vb, k_small(cp, q_o, c_o, vb))
        f0 = 1.0 - lay.f_nominal

        def err(a):
            return lay.infidelity(node_dv(lay, cp, q_o, c_o, vb, a * base), recalibrate_z=True)
        r = minimize_scalar(err, bounds=(0.8, 1.25), method="bounded", options={"xatol": 1e-7})
        return max(float(r.fun) - f0, 0.0)
    if mode == "predistortion":
        q_e, _ = PD.charge_fn(c_est_of_v(vb))
        target = vb + lay.v0
        vd = target - vb + (q_e(target) - q_e(vb)) / cp
        vd[lay.n_gate:] = 0.0
        return lay.excess_infidelity(node_dv(lay, cp, q_o, c_o, vb, vd))
    raise ValueError(mode)


def esd_job(args):
    s, c_node, k0, k100, mode = args
    lay = lay_for(s)
    c0 = PD.c_other_from_k(c_node, k0)
    c100 = PD.c_other_from_k(c_node, k100)

    def worst(area):
        c_o = lambda v: c0(v) + area / 100.0 * (c100(v) - c0(v))  # noqa: E731
        c_e = lambda vb: (lambda v: c_o(v) + EST_ERR * area / 100.0 * (c100(v) - c0(v) - c100(vb) + c0(vb)))  # noqa: E731
        return max(infidelity(lay, c_node, c_o, vb, mode, c_e) for vb in biases(lay))
    row = {"s": s, "c_node": c_node, "mode": mode, "worst_100um2": worst(100.0)}
    for tgt in TARGETS:
        if worst(1e5) < tgt:
            row[f"area_{tgt:g}"] = float("inf")
            continue
        row[f"area_{tgt:g}"] = float(brentq(lambda a: np.log(max(worst(a), 1e-30) / tgt), 1e-3, 1e5, xtol=1e-3, rtol=1e-3))
    print(f"ESD s {s:g} C {c_node * 1e15:g} fF {mode}: 100 um2 -> {row['worst_100um2']:.2e}, "
          f"areas {row['area_0.001']:.3g} / {row['area_0.0001']:.3g} um2", flush=True)
    return row


def electrode_job(args):
    s, c_node, mode = args
    lay = lay_for(s)
    base = (1 - PD.F_PULSE) * c_node
    vb = 0.9 if 0.9 in biases(lay) else max(biases(lay))

    def f_of(slope):
        c_o = lambda v: base + slope * (np.asarray(v, float) - 0.9)  # noqa: E731
        c_e = lambda vb: (lambda v: c_o(v) + EST_ERR * slope * (np.asarray(v, float) - vb))  # noqa: E731
        return infidelity(lay, c_node, c_o, vb, mode, c_e)
    row = {"s": s, "c_node": c_node, "mode": mode, "bias": vb}
    for tgt in TARGETS:
        hi = 1e-11
        if f_of(hi) < tgt:
            row[f"slope_{tgt:g}"] = float("inf")
            continue
        row[f"slope_{tgt:g}"] = float(brentq(lambda x: np.log(max(f_of(x), 1e-30) / tgt), 1e-18, hi, xtol=1e-19, rtol=1e-3))
    print(f"electrode s {s:g} C {c_node * 1e15:g} fF {mode}: {row['slope_0.001'] * 1e15:.3g} / {row['slope_0.0001'] * 1e15:.3g} fF/V",
          flush=True)
    return row


def main():
    tab = json.loads((ROOT / "results" / "design_space.json").read_text(encoding="utf-8"))["pulse_table"]
    by = {(p["c_node"], p["esd_area"]): p for p in tab if "f_pulse" in p}
    cnodes = sorted({c for c, _ in by})
    jobs_e = [(s, c, by[(c, 0.0)]["k"], by[(c, 100.0)]["k"], m) for s in SLOPES for c in cnodes for m in MODES]
    jobs_l = [(s, c, m) for s in SLOPES for c in (2e-13, 1e-12, 3e-12) for m in MODES]
    with ProcessPoolExecutor(12) as ex:
        esd = list(ex.map(esd_job, jobs_e))
        el = list(ex.map(electrode_job, jobs_l))
    out = {"modes": MODES, "est_err": EST_ERR, "biases": {f"{s:g}": biases(lay_for(s)) for s in SLOPES},
           "esd": esd, "electrode": el}
    (OUT / "qubit_calibration.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    return out


def table(out):
    L = ["## Pulse distortion under four calibrations (charge-balance model, TG cell couplings)", "",
         f"Predistortion uses a C_o(V) whose voltage-dependent part is {out['est_err'] * 100:.0f} % too large. Biases: "
         + "; ".join(f"{s} dec/V: {b}" for s, b in out["biases"].items()), "",
         "### Largest area of each ESD diode (µm²) for 99.9 % / 99.99 %, and infidelity of a 100 µm² pair", "",
         "| s (dec/V) | C_node | " + " | ".join(MODES) + " |", "|---|---|" + "---|" * len(MODES)]
    rows = {(r["s"], r["c_node"], r["mode"]): r for r in out["esd"]}
    for s in SLOPES:
        for c in sorted({r["c_node"] for r in out["esd"]}):
            cells = []
            for m in MODES:
                r = rows[(s, c, m)]
                cells.append(f"{r['area_0.001']:.3g} / {r['area_0.0001']:.3g} ({r['worst_100um2']:.1e})")
            L.append(f"| {s:g} | {c * 1e15:g} fF | " + " | ".join(cells) + " |")
    L += ["", "### Largest slope of an electrode capacitance (fF/V) for 99.9 % / 99.99 %", "",
          "| s (dec/V) | C_node | " + " | ".join(MODES) + " |", "|---|---|" + "---|" * len(MODES)]
    rows = {(r["s"], r["c_node"], r["mode"]): r for r in out["electrode"]}
    for s in SLOPES:
        for c in (2e-13, 1e-12, 3e-12):
            L.append(f"| {s:g} | {c * 1e15:g} fF | " + " | ".join(
                f"{rows[(s, c, m)]['slope_0.001'] * 1e15:.3g} / {rows[(s, c, m)]['slope_0.0001'] * 1e15:.3g}" for m in MODES) + " |")
    (OUT / "qubit_calibration.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    table(main())
