"""Coupling of gate pulses into neighbouring hold nodes, and through a shared well.

Pulse line to neighbour. A pulse line drives its barrier through C_pulse with the swing V_d(t) = v0(t) / k.
If it couples to a neighbouring hold node (or to the electrode line behind it) through C_c, the neighbour
sees dv(t) = (C_c / C_node) v0(t) / k, a copy of the pulse. Two cases:
  - the neighbour runs its own CZ at the same time (parallel gates of a surface-code layer): dv is an
    amplitude error of the fraction x = C_c / (k C_node); the limit is the largest x at which the excess
    infidelity stays at the target with the calibration held fixed;
  - the neighbour is idle: its exchange rises from J_idle to J_idle 10^(s dv) during the pulse and the
    extra conditional phase 2 pi int (J - J_idle) dt adds an error 0.4 (1 - cos(delta / 2)).
The single-qubit Stark phase of a coupled pulse is deterministic and is left to frame tracking.

Shared well. A group of NMOS cells shares one isolated p-well. Each pulsed hold node couples to the well
through the junction of its switch, and the well couples back to every node of the group. Worst case: half
the cells of a group pulsed at once and the well floating (no supply impedance at all) for the 50 ns gate.

Run:  python studies/coupling.py     (seconds; writes results/coupling.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
from flow import budget as B  # noqa: E402

SLOPES = (3.87, 10.0, 33.69)
TARGETS = (1e-3, 1e-4)
K = 0.5
C_NODE = 1e-12
C_FANIN_PER_UM = (0.05e-15, 0.1e-15)      # F/um, adjacent minimum-pitch lines in a mid metal layer (order of magnitude)


def active_limit(lay, tgt):
    f = lambda x: np.log(max(max(lay.excess_infidelity(x * lay.v0), lay.excess_infidelity(-x * lay.v0)), 1e-30) / tgt)  # noqa: E731
    return brentq(f, 1e-6, 0.5, xtol=1e-9)


def idle_error(lay, x):
    dv = x * lay.v0[:lay.n_gate]
    dj = lay.cfg.j_idle * (10 ** (lay.cfg.s_dec_per_v * dv) - 1)
    delta = 2 * np.pi * np.sum(dj * lay.dts[:lay.n_gate])
    return 0.4 * (1 - np.cos(delta / 2))


def idle_limit(lay, tgt):
    f = lambda x: np.log(max(idle_error(lay, x), 1e-30) / tgt)  # noqa: E731
    hi = 1.0
    if f(hi) < 0:
        return float("inf")
    return brentq(f, 1e-6, hi, xtol=1e-9)


def main():
    out = {"k": K, "c_node": C_NODE, "rows": []}
    for s in SLOPES:
        lay = B.layer(s_dec_per_v=s)
        for tgt in TARGETS:
            xa, xi = active_limit(lay, tgt), idle_limit(lay, tgt)
            row = {"s": s, "target": tgt, "v_drive_peak": float(lay.v0.max() / K),
                   "x_active": xa, "cc_active_fF": xa * K * C_NODE * 1e15,
                   "x_idle": xi, "cc_idle_fF": xi * K * C_NODE * 1e15}
            row["fanin_length_um_active"] = [row["cc_active_fF"] * 1e-15 / c for c in C_FANIN_PER_UM]
            out["rows"].append(row)
            print(f"s {s:g} target {tgt:g}: active x {xa:.3g} -> C_c {row['cc_active_fF']:.3g} fF; idle x {xi:.3g} -> "
                  f"{row['cc_idle_fF']:.3g} fF", flush=True)
    # shared well, from the NMOS cell's own junction capacitance (off capacitance on the line side, the
    # same junction on the hold side), 4 K band
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    cell = next(r["cell"] for r in res["switching"] if r and "error" not in r and r["design"] == "NMOS, 0.3 V underdrive"
                and r["band"] == "4 K proxy" and r["corner"] == "tt")
    c_j = cell["c_line_cell"]
    # p-well to deep n-well: ~0.1 fF/um^2 bottom capacitance (order of magnitude) under a 5 x 5 um^2 well area per cell
    c_well_per_cell = 25 * 0.1e-15
    for s in SLOPES:
        lay = B.layer(s_dec_per_v=s)
        dv_well = 0.5 * lay.v0.max() * c_j / (c_j + c_well_per_cell)     # half the cells pulsed, floating well
        dv_node = dv_well * c_j / C_NODE
        out.setdefault("well", []).append({"s": s, "c_j_fF": c_j * 1e15, "c_well_per_cell_fF": c_well_per_cell * 1e15,
                                           "dv_well_mV": dv_well * 1e3, "dv_node_uV": dv_node * 1e6})
        print(f"well s {s:g}: C_j {c_j * 1e15:.3g} fF, well bump {dv_well * 1e3:.3g} mV, node {dv_node * 1e6:.3g} uV", flush=True)
    (OUT / "coupling.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    L = ["## Largest coupling from a pulse line to a neighbouring 1 pF hold node (k = 0.5)", "",
         "| s (dec/V) | target | drive peak (V) | neighbour gating: C_c (fF) | neighbour idle: C_c (fF) | parallel fan-in length at 0.05 / 0.1 fF/µm (µm) |",
         "|---|---|---|---|---|---|"]
    for r in out["rows"]:
        L.append(f"| {r['s']:g} | {r['target']:g} | {r['v_drive_peak']:.3g} | {r['cc_active_fF']:.3g} | {r['cc_idle_fF']:.3g} | "
                 f"{r['fanin_length_um_active'][0]:.3g} / {r['fanin_length_um_active'][1]:.3g} |")
    L += ["", "## Shared p-well, half the cells of a group pulsed, well floating during the gate", "",
          "| s (dec/V) | junction C (fF) | well C per cell (fF) | well bump (mV) | bump on a held node (µV) |", "|---|---|---|---|---|"]
    for r in out["well"]:
        L.append(f"| {r['s']:g} | {r['c_j_fF']:.3g} | {r['c_well_per_cell_fF']:.3g} | {r['dv_well_mV']:.3g} | {r['dv_node_uV']:.3g} |")
    (OUT / "coupling.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
