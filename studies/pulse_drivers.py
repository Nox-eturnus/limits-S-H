"""Order of magnitude of the pulse path that the static multiplexing does not cover.

In the charge-locked cell every barrier receives its CZ pulse through its own pulse capacitor
C_pulse = k C_node (k = 0.5 on a 1 pF node) from a fast driver, which the refresh tree does not multiplex. A
lower bound on the energy of one pulse is the energy dissipated in charging and discharging the series
capacitance that the driver sees, C_s = C_pulse (C_node - C_pulse) / C_node, through a resistive driver to the
pulse-line swing v_line = v0 / k, where v0 is the barrier pulse (J from 50 kHz to 20 MHz: 2.6 decades,
v0 = 2.6 / s):
    E >= C_s v_line^2.
In a surface code each barrier runs one CZ per round, so the power per barrier is E / t_round. The driver's own
bias, the waveform generation and the lines that bring the pulse to the driver are not included, so the
numbers are lower bounds for the load at the stage where the drivers sit. One driver per barrier: about 10^6
drivers for 10^6 barriers.

Run:  python studies/pulse_drivers.py     (seconds; writes results/pulse_drivers.{json,md})
"""
import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parents[1] / "results"
C_NODE = 1e-12
K = 0.5
DECADES = np.log10(20e6 / 50e3)
SLOPES = (3.87, 10.0, 33.69)
ROUNDS = (1e-6, 10e-6)
N_BARRIERS = 1e6


def main():
    c_p = K * C_NODE
    c_s = c_p * (C_NODE - c_p) / C_NODE
    rows = []
    for s in SLOPES:
        v0 = DECADES / s
        v_line = v0 / K
        e = c_s * v_line ** 2
        for t in ROUNDS:
            rows.append({"s": s, "v0": v0, "v_line": v_line, "energy_J": e, "t_round": t,
                         "power_per_barrier_W": e / t, "power_1e6_W": e / t * N_BARRIERS})
    (OUT / "pulse_drivers.json").write_text(json.dumps({"c_series_F": c_s, "rows": rows}, indent=1), encoding="utf-8")
    L = ["## Lower bound on the pulse power", "", f"C_s = {c_s * 1e15:.0f} fF; one CZ per barrier per round.", "",
         "| s (dec/V) | barrier pulse v0 (V) | pulse-line swing (V) | energy per pulse | round | per barrier | 10^6 barriers |",
         "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['s']:g} | {r['v0']:.3f} | {r['v_line']:.2f} | {r['energy_J'] * 1e15:.0f} fJ | {r['t_round'] * 1e6:g} µs | "
                 f"{r['power_per_barrier_W'] * 1e9:.3g} nW | {r['power_1e6_W'] * 1e3:.3g} mW |")
    (OUT / "pulse_drivers.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
