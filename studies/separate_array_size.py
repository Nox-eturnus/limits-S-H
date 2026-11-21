"""The size of a separate hold array and the length of its connections.

One 26 x 33 mm^2 reticle holds 1.8 x 10^6 cells of 1 pF at a 22 um pitch, so 10^6 cells cover 484 mm^2, not a full
reticle. The fan-in estimate of studies/system_operation.py (cells uniform over the whole reticle, Manhattan
distance to a central qubit region, mean 14.7 mm, largest 29.5 mm) is repeated for 10^6 cells packed at that pitch
in a square ring around the qubit region, whose side the edge fan-in sets (12.5, 8.3 and 5.0 mm for 4, 6 and 10
routing layers), with the same distance measure. Everything that follows from the length is recomputed with the
formulas of the earlier studies:

  - connection capacitance 0.2 to 0.3 fF/um and the separate-array driver bound C_o v0^2 / k with C_p = 1 pF,
    k = C_p / (C_p + C_o), v0 = 2.6 / s, 5.7 x 10^5 barriers, one CZ per barrier per 10 us round, the coldest stage
    after Krinner et al. with the static array at the lowest droop (studies/pulse_drivers_one_array.py);
  - resistance at 50 nm and 0.125 ohm per square, distributed time constant R C_o / 2, and the widening-line
    estimate (studies/separate_hold_array.py, studies/pulse_drivers_one_array.py);
  - coupling of adjacent connections, 0.05 to 0.1 fF/um unshielded and 1 to 5 % of it shielded
    (studies/system_operation.py), and the crosstalk tolerance eps (C_p + C_o) of a neighbour that runs its own CZ
    (studies/connection_crosstalk.py).

Run:  python studies/separate_array_size.py     (seconds; writes results/separate_array_size.{json,md})
"""
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
PITCH, N_CELLS = 22e-6, 1e6
REGION = {4: 12.5e-3, 6: 8.3e-3, 10: 5.0e-3}       # side of the qubit region for 10^6 lines through its edge
SLOPES = (3.87, 10, 16.6, 33.69)
STAGES = (("20 mK", 19e-6), ("140 mK", 200e-6), ("1.2 K", 40e-3), ("4.2 K", 1.5))
N_BAR = 1e6 * 2 / 3.5
CP, F_PER_M = 1e-12, (0.2e-15 / 1e-6, 0.3e-15 / 1e-6)
EPS = json.loads((ROOT / "results" / "zeeman_equal_sign.json").read_text(encoding="utf-8"))["C"]


def coldest(p, static=1.4e-6):
    for name, cap in STAGES:
        if p + static <= cap:
            return name
    return "above 4.2 K"


def ring(side_in, area, n=400_000, seed=1):
    side_out = math.sqrt(side_in ** 2 + area)
    rng = np.random.default_rng(seed)
    pts = rng.uniform(-side_out / 2, side_out / 2, (int(n * side_out ** 2 / area * 1.05), 2))
    pts = pts[(np.abs(pts) > side_in / 2).any(1)][:n]
    d = np.abs(pts).sum(1)
    return side_out, float(d.mean()), float(d.max())


def main():
    rng = np.random.default_rng(1)                     # the earlier estimate, as a check
    pts = rng.uniform([-13e-3, -16.5e-3], [13e-3, 16.5e-3], (200_000, 2))
    old = np.abs(pts).sum(1)
    res = {"area_mm2": N_CELLS * PITCH ** 2 * 1e6, "reticle_mm2": 26 * 33,
           "full_reticle": {"mean_mm": float(old.mean()) * 1e3, "max_mm": float(old.max()) * 1e3}, "ring": {}}
    for layers, a in REGION.items():
        side_out, mean, mx = ring(a, N_CELLS * PITCH ** 2)
        res["ring"][layers] = {"region_mm": a * 1e3, "outer_mm": side_out * 1e3, "mean_mm": mean * 1e3, "max_mm": mx * 1e3}
    means = [r["mean_mm"] * 1e-3 for r in res["ring"].values()]
    L = (min(means), max(means))
    co = (F_PER_M[0] * L[0], F_PER_M[1] * L[1])
    res["L_mean_mm"] = [x * 1e3 for x in L]
    res["L_max_mm"] = max(r["max_mm"] for r in res["ring"].values())
    res["C_o_pF"] = [c * 1e12 for c in co]
    res["k"] = [CP / (CP + c) for c in co]
    res["drivers"] = []
    for s in SLOPES:
        v0 = 2.6 / s
        for c in co:
            k = CP / (CP + c)
            p = c * v0 ** 2 / k * N_BAR / 10e-6
            res["drivers"].append({"s": s, "C_o_pF": c * 1e12, "k": k, "swing_V": v0 / k, "P_mW_10us": p * 1e3,
                                   "stage": coldest(p)})
    R = [0.125 * x / 50e-9 for x in L]
    res["R_kohm"] = [r / 1e3 for r in R]
    res["tau_ns"] = [R[0] * co[0] / 2 * 1e9, R[1] * co[1] / 2 * 1e9]
    taper = []
    for layers, a in REGION.items():                   # widening line, as studies/pulse_drivers_one_array.py, over the new length
        r0 = a / 2
        outside = 0.125 * (r0 / 50e-9) * math.log((r0 + L[1]) / r0)
        inside = 0.125 * (r0 / 3) / 50e-9
        taper.append((outside + inside) / R[1])
    res["taper_ratio"] = [min(taper), max(taper)]
    unsh = (0.05e-15 / 1e-6 * L[0], 0.1e-15 / 1e-6 * L[1])
    sh = (0.01 * unsh[0], 0.05 * unsh[1])
    res["coupling_fF"] = {"unshielded": [x * 1e15 for x in unsh], "shielded": [x * 1e15 for x in sh]}
    res["xtalk"] = {}
    for tgt in ("0.0001", "0.001"):
        eps = [EPS[f"{s:g}|{tgt}"]["eps_single"] for s in SLOPES]
        lim = (min(eps) * (CP + co[0]), max(eps) * (CP + co[1]))
        res["xtalk"][tgt] = {"limit_fF": [x * 1e15 for x in lim],
                             "accuracy_shielded": [lim[0] / sh[1], lim[1] / sh[0]],
                             "accuracy_unshielded": [lim[0] / unsh[1], lim[1] / unsh[0]]}
    (OUT / "separate_array_size.json").write_text(json.dumps(res, indent=1), encoding="utf-8")

    T = ["# A separate hold array of 10^6 cells packed at the 22 um pitch", "",
         f"Cells cover {res['area_mm2']:.0f} mm^2 of the {res['reticle_mm2']} mm^2 reticle. Earlier estimate (whole reticle): "
         f"mean {res['full_reticle']['mean_mm']:.1f} mm, largest {res['full_reticle']['max_mm']:.1f} mm.", "",
         "| layers | qubit region (mm) | outer side (mm) | mean (mm) | largest (mm) |", "|---|---|---|---|---|"]
    for layers, r in res["ring"].items():
        T.append(f"| {layers} | {r['region_mm']:.1f} | {r['outer_mm']:.1f} | {r['mean_mm']:.1f} | {r['max_mm']:.1f} |")
    T += ["", f"Connection {res['C_o_pF'][0]:.2f} to {res['C_o_pF'][1]:.2f} pF, k {res['k'][1]:.3f} to {res['k'][0]:.3f}; "
          f"R {res['R_kohm'][0]:.0f} to {res['R_kohm'][1]:.0f} kohm, tau {res['tau_ns'][0]:.0f} to {res['tau_ns'][1]:.0f} ns, "
          f"widening line x{res['taper_ratio'][0]:.2f} to x{res['taper_ratio'][1]:.2f}.", "",
          "| s (dec/V) | swing (V) | bound, 10 us rounds (mW) | coldest stage |", "|---|---|---|---|"]
    for s in SLOPES:
        rr = [r for r in res["drivers"] if r["s"] == s]
        T.append(f"| {s:g} | {rr[0]['swing_V']:.2f} to {rr[1]['swing_V']:.2f} | {rr[0]['P_mW_10us']:.1f} to "
                 f"{rr[1]['P_mW_10us']:.1f} | {rr[0]['stage']} / {rr[1]['stage']} |")
    c = res["coupling_fF"]
    T += ["", f"Coupling of adjacent connections: unshielded {c['unshielded'][0]:.0f} to {c['unshielded'][1]:.0f} fF, "
          f"shielded {c['shielded'][0]:.1f} to {c['shielded'][1]:.0f} fF."]
    for tgt, x in res["xtalk"].items():
        T.append(f"- target {tgt}: limit {x['limit_fF'][0]:.1f} to {x['limit_fF'][1]:.1f} fF; compensation shielded "
                 f"{x['accuracy_shielded'][0]:.1%} to {x['accuracy_shielded'][1]:.0%}, unshielded "
                 f"{x['accuracy_unshielded'][0]:.2%} to {x['accuracy_unshielded'][1]:.2%} (above 100 %: none needed)")
    (OUT / "separate_array_size.md").write_text("\n".join(T) + "\n", encoding="utf-8")
    print("\n".join(T))


if __name__ == "__main__":
    main()
