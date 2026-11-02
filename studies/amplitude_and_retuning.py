"""System estimates that need no circuit simulation.

Locally held pulse amplitude: the largest fractional error of the CZ pulse amplitude at the target, untracked and
frame-tracked for two gates, and as a voltage on a held amplitude of the pulse-line swing; the energy bound
C_node (1 - k) v0^2 / k per pulse. Device noise at 1 K for a noise power or amplitude linear in temperature. Pulse-driver
power for 10^6 barriers (the C V^2 bound, switched-capacitor cells, one cryo-CMOS DAC per barrier). Qubit-time cost of
retuning every pair on the qubits. Calibration time with the seven-point line.

Run:  python studies/amplitude_and_retuning.py     (writes results/amplitude_and_retuning.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
from flow import budget as B  # noqa: E402
from repeated_gates import _PROJ_COND  # noqa: E402

SLOPES = (3.87, 10.0, 16.6, 33.69)
TARGETS = (1e-3, 1e-4)
C_NODE = 1e-12
N_BAR = 1e6
ROUNDS = (1e-6, 1e-5)
STAGES = {"20 mK": 19e-6, "140 mK": 200e-6, "1.2 K": 40e-3, "4.2 K": 1.5}
L = []


def solve(f, target, lo=1e-6, hi=0.5):
    from scipy.optimize import brentq
    xs = np.geomspace(lo, hi, 120)
    vals = [f(x) - target for x in xs]
    i = next(k for k, v in enumerate(vals) if v >= 0)
    return brentq(lambda x: f(x) - target, xs[i - 1], xs[i]) if i else xs[0]


def r2():
    out = {"amplitude": {}, "energy": {}}
    L.extend(["## Locally held pulse amplitude", "",
              "| s (dec/V) | target | v0 peak (V) | eps untracked | eps tracked, M = 2 | held amplitude, untracked / tracked (mV, k = 0.5) |",
              "|---|---|---|---|---|---|"])
    for s in SLOPES:
        lay = B.layer(s_dec_per_v=s)
        v0 = float(np.max(lay.v0))
        for t in TARGETS:
            def unt(e, sign):
                return lay.excess_infidelity(sign * e * lay.v0)

            def trk(e, sign):
                ph = lay.phase_errors(sign * e * lay.v0)
                return B.phase_infidelity(np.sqrt(2) * (_PROJ_COND @ ph))
            eu = min(solve(lambda e: unt(e, +1), t), solve(lambda e: unt(e, -1), t))
            et = min(solve(lambda e: trk(e, +1), t), solve(lambda e: trk(e, -1), t))
            out["amplitude"][f"{s}|{t}"] = {"v0": v0, "eps_untracked": eu, "eps_tracked_M2": et,
                                            "dA_untracked_V": eu * v0 / 0.5, "dA_tracked_V": et * v0 / 0.5}
            L.append(f"| {s:g} | {t:g} | {v0:.3f} | {eu * 100:.3g} % | {et * 100:.3g} % | "
                     f"{eu * v0 / 0.5 * 1e3:.3g} / {et * v0 / 0.5 * 1e3:.3g} |")
    L.extend(["", "Energy bound per pulse C_node (1 - k) v0^2 / k on 1 pF and power for 10^6 barriers (1 / 10 us rounds):", "",
              "| s | k = 0.5 | k = 0.8 | k = 0.9 |", "|---|---|---|---|"])
    for s in (3.87, 10.0, 33.69):
        v0 = 2.6 / s
        row = {}
        for k in (0.5, 0.8, 0.9):
            e = C_NODE * (1 - k) * v0 ** 2 / k
            row[f"{k:g}"] = {"E_J": e, "P_W": [e * N_BAR / r for r in ROUNDS]}
        out["energy"][f"{s:g}"] = row
        L.append(f"| {s:g} | " + " | ".join(f"{r['E_J'] * 1e15:.3g} fJ, {r['P_W'][0] * 1e3:.3g} / {r['P_W'][1] * 1e3:.3g} mW"
                                            for r in row.values()) + " |")
    L.append("")
    return out


def r5():
    s1 = {(99.9, 3.87): 438, (99.9, 7.25): 359, (99.9, 10): 304, (99.9, 16.6): 214, (99.9, 33.69): 116,
          (99.99, 3.87): 139, (99.99, 7.25): 114, (99.99, 10): 96, (99.99, 16.6): 68, (99.99, 33.69): 37}
    lo, hi = 9.0, 49.0
    f_pow, f_amp = np.sqrt(1.0 / 0.1), 1.0 / 0.1
    out = {"budget_uV": {f"{k[0]}|{k[1]}": v for k, v in s1.items()},
           "noise_1K_power_linear": [lo * f_pow, hi * f_pow], "noise_1K_amplitude_linear": [lo * f_amp, hi * f_amp]}
    L.extend(["## Device noise at 1 K against the 1/f budget (µV/√Hz at 1 Hz)", "",
              f"9 to 49 µV/√Hz at 0.1 K become {lo * f_pow:.0f} to {hi * f_pow:.0f} at 1 K for a noise power linear in T, "
              f"{lo * f_amp:.0f} to {hi * f_amp:.0f} for an amplitude linear in T.", "",
              "| target | slope | budget | quiet / noisy device at 1 K (power-linear) |", "|---|---|---|---|"])
    for (t, s), b in s1.items():
        q, n = lo * f_pow, hi * f_pow
        L.append(f"| {t} % | {s:g} | {b} | {'ok' if q < b else 'exceeds'} / {'ok' if n < b else 'exceeds'} |")
    L.append("")
    return out


def r7():
    out = {}
    L.extend(["## Pulse-driver power for 10^6 barriers", ""])
    for s in (3.87, 10.0, 33.69):
        v0 = 2.6 / s
        bound = {f"{k:g}": [C_NODE * (1 - k) * v0 ** 2 / k * N_BAR / r for r in ROUNDS] for k in (0.5, 0.9)}
        out[f"{s:g}"] = {"cv2_bound_W": bound}
        L.append(f"- s = {s:g}: C V^2 bound k = 0.5: {bound['0.5'][0] * 1e3:.3g} / {bound['0.5'][1] * 1e3:.3g} mW, "
                 f"k = 0.9: {bound['0.9'][0] * 1e3:.3g} / {bound['0.9'][1] * 1e3:.3g} mW (1 / 10 us rounds)")
    out["pauka_switched_capacitor_W"] = 18e-9 * N_BAR
    out["dac_per_barrier_W"] = 157e-6 * N_BAR
    L.extend([f"- switched-capacitor cells (Pauka et al., 18 nW per cell, 100 mV pulses): {18e-9 * N_BAR * 1e3:.3g} mW",
              f"- one cryo-CMOS DAC per barrier (157 uW, Enthoven et al.): {157e-6 * N_BAR:.3g} W",
              "- stages: " + ", ".join(f"{k} {v * 1e3:g} mW" for k, v in STAGES.items()), ""])
    return out


def s6():
    """Retuning on the qubits: three parameters per pair (static level or CZ amplitude, two single-qubit phases), each
    from n_set settings x n_shot shots of t_shot."""
    n_pairs = N_BAR * 2 / 3.5 / (2 / 3.5) * (2 / 3.5)      # barriers among 10^6 electrodes (2 of 3.5 per qubit)
    n_pairs = 1e6 * 2 / 3.5
    cases = {"lean": (3, 10, 100, 5e-6), "careful": (3, 20, 300, 10e-6)}
    out = {"n_pairs": n_pairs, "cases": {}}
    L.extend(["## Retuning every pair on the qubits", "", f"{n_pairs:.3g} pairs (barriers of 10^6 electrodes)", "",
              "| case | per pair | 100 / 1e4 pairs at once | fraction of time, retuned daily / hourly / every 100 s |",
              "|---|---|---|---|"])
    for k, (npar, nset, nshot, tshot) in cases.items():
        tp = npar * nset * nshot * tshot
        tot = [n_pairs * tp / p for p in (1e2, 1e4)]
        fr = {c: [x / c for x in tot] for c in (86400.0, 3600.0, 100.0)}
        out["cases"][k] = {"t_pair": tp, "t_total": tot, "fraction": {f"{c:g}": v for c, v in fr.items()}}
        L.append(f"| {k} | {tp * 1e3:.3g} ms | {tot[0]:.3g} / {tot[1]:.3g} s | " +
                 " / ".join(f"{min(v[1], 9.99):.2g}-{min(v[0], 9.99):.2g}" for v in fr.values()) + " |")
    L.append("")
    return out


def r3_time():
    s7 = json.loads((ROOT / "results" / "system_operation.json").read_text(encoding="utf-8"))["sensor_noise"]
    out = {}
    L.extend(["## Calibration time with ten measurements per channel (seven pedestal points, two droop, one pulse)", ""])
    for k, v in s7["t_point"].items():
        out[k] = {f"{p:g}": [1e7 * 4 * t / p for t in v] for p in (1e2, 1e3, 1e4)}

        def h(x):
            return f"{x:.2g} s" if x < 60 else f"{x / 60:.2g} min" if x < 3600 else f"{x / 3600:.2g} h" if x < 2 * 86400 else f"{x / 86400:.2g} d"
        L.append(f"- {k}: " + "; ".join(f"{p} at once {h(a)} to {h(b)}" for p, (a, b) in out[k].items()))
    L.append("")
    return out


def main():
    out = {"r2": r2(), "r5": r5(), "stage_load": r7(), "s6": s6(), "r3_time": r3_time()}
    (OUT / "amplitude_and_retuning.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT / "amplitude_and_retuning.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
