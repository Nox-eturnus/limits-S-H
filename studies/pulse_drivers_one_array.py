"""Pulse-driver bounds for one array: 10^6 electrodes, which hold 5.7 x 10^5 barriers.

At 3.5 gates per qubit, 10^6 electrodes hold 2/3.5 x 10^6 barriers (studies/separate_hold_array.py and
studies/pulse_driver_node_size.py use 10^6 barriers). Energies per pulse are unchanged; powers and stages are
recomputed. Separate hold array: C_p = 1 pF, C_o = 3 or 4.5 pF, bound C_o v0^2 / k. Cells under their electrodes:
bound C_node (1 - k) v0^2 / k for 1 pF and 70 fF nodes, k = 0.5 and 0.9, with the static array at the lowest droop
(1.4 uW on 1 pF, 7.7 uW on 70 fF). Cooling powers of a dilution refrigerator: 1.5 W at 4.2 K, 40 mW at 1.2 K,
200 uW at 140 mK, 19 uW at 20 mK. The last part estimates the resistance of a fan-in line that widens away from
the edge of the qubit region, as a fraction of the 37.5 kohm of a line of constant 50 nm width.

Run:  python studies/pulse_drivers_one_array.py     (seconds; writes results/pulse_drivers_one_array.json)
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "results"
SLOPES = (3.87, 10, 16.6, 33.69)
STAGES = (("20 mK", 19e-6), ("140 mK", 200e-6), ("1.2 K", 40e-3), ("4.2 K", 1.5))
N_EL = 1e6
N_BAR = N_EL * 2 / 3.5


def coldest(p, static):
    for name, cap in STAGES:
        if p + static <= cap:
            return name
    return "above 4.2 K"


out = {"n_barriers": N_BAR, "separate": [], "under": []}
for s in SLOPES:
    v0 = 2.6 / s
    for co in (3e-12, 4.5e-12):
        k = 1e-12 / (1e-12 + co)
        e = co * v0 ** 2 / k
        p = e * N_BAR / 10e-6
        out["separate"].append({"s": s, "C_o_pF": co * 1e12, "k": k, "swing_V": v0 / k, "P_mW_10us": p * 1e3,
                                "stage": coldest(p, 1.4e-6)})
    for c, static in ((1e-12, 1.4e-6), (70e-15, 7.7e-6)):
        row = {"s": s, "C_fF": c * 1e15}
        for k in (0.5, 0.9):
            e = c * (1 - k) * v0 ** 2 / k
            for rt in (1e-6, 10e-6):
                p = e * N_BAR / rt
                row[f"k{k}_{rt * 1e6:g}us"] = (round(e * 1e15, 4), round(p * 1e3, 5), coldest(p, static))
        out["under"].append(row)
out["dac_per_barrier_W"] = 157e-6 * N_BAR
for r in out["separate"]:
    print({a: (round(b, 3) if isinstance(b, float) else b) for a, b in r.items()})
for r in sorted(out["under"], key=lambda r: (r["C_fF"] < 1000, r["s"])):
    print(r)
print("barriers", N_BAR, "DAC per barrier (W)", out["dac_per_barrier_W"])
(OUT / "pulse_drivers_one_array.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

# ---- fan-in line that widens away from the edge of the qubit region (order of magnitude)
# Width 50 nm at the edge (half-side r0 of the region for 4, 6 and 10 layers), growing in proportion to the distance
# from the centre over the next 15 mm; inside the region a mean run of r0 / 3 at 50 nm. Sheet resistance 0.125 ohm/sq.
import math
taper = []
for layers, side in ((4, 12.5e-3), (6, 8.3e-3), (10, 5.0e-3)):
    r0 = side / 2
    outside = 0.125 * (r0 / 50e-9) * math.log((r0 + 15e-3) / r0)
    inside = 0.125 * (r0 / 3) / 50e-9
    taper.append({"layers": layers, "R_outside_kohm": outside / 1e3, "R_inside_kohm": inside / 1e3,
                  "ratio_to_37.5k": (outside + inside) / 37.5e3})
    print(taper[-1])
out["fan_in_taper"] = taper
(OUT / "pulse_drivers_one_array.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
