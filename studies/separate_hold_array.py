"""A separate hold array reached through long connections: pulse-driver bound and fan-in line.

With the hold cells on a separate array, each node carries the 3 to 4.5 pF of its 15 mm connection, which also holds
the level, so the whole capacitor of a 22 um cell, about 1 pF, can serve as pulse capacitor: k = C_p / (C_p + C_o).
Bound C_o v0^2 / k per pulse, 10^6 barriers, one CZ per barrier per round of 10 us (and 1 us), against the cooling
powers of a dilution refrigerator (1.5 W at 4.2 K, 40 mW at 1.2 K, 200 uW at 140 mK, 19 uW at 20 mK) with the static
array at the lowest droop (1.4 uW). The fan-in line is 15 mm long and about 50 nm wide (100 nm metal pitch), at the
0.125 ohm per square of SkyWater metal 2, a lower bound for so narrow a wire; distributed time constant RC / 2.

Run:  python studies/separate_hold_array.py     (seconds; writes results/separate_hold_array.json)
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "results"
SLOPES = (3.87, 10, 16.6, 33.69)
CP = 1e-12
CO = (3e-12, 4.5e-12)
STAGES = (("20 mK", 19e-6), ("140 mK", 200e-6), ("1.2 K", 40e-3), ("4.2 K", 1.5))
STATIC = 1.4e-6
N_BAR = 1e6


def coldest(p):
    for name, cap in STAGES:
        if p + STATIC <= cap:
            return name
    return "above 4.2 K"


rows = []
for s in SLOPES:
    v0 = 2.6 / s
    for co in CO:
        k = CP / (CP + co)
        e = co * v0 ** 2 / k
        r = {"s": s, "C_o_pF": co * 1e12, "k": k, "swing_V": v0 / k, "E_fJ": e * 1e15}
        for rt in (10e-6, 1e-6):
            p = e * N_BAR / rt
            r[f"P_mW_{rt * 1e6:g}us"] = p * 1e3
            r[f"stage_{rt * 1e6:g}us"] = coldest(p)
        rows.append(r)
        print({a: (round(b, 3) if isinstance(b, float) else b) for a, b in r.items()})
rsq, length, width = 0.125, 15e-3, 50e-9
R = rsq * length / width
rc = [{"C_pF": c * 1e12, "R_kohm": R / 1e3, "tau_ns": R * c / 2 * 1e9} for c in CO]
print("fan-in line:", rc)
(OUT / "separate_hold_array.json").write_text(json.dumps({"separate_array": rows, "fan_in_line": rc}, indent=1), encoding="utf-8")
