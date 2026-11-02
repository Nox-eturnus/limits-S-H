"""Pulse drivers for 10^6 barriers, per slope and round time, against the stages of a dilution refrigerator.

Per pulse (one CZ per barrier per surface-code round, k = C_pulse / C_node, 1 pF nodes): the resistive lower bound
C_node (1 - k) v0^2 / k, which a driver that charges through a resistance or by charge sharing cannot beat; cells with
the energy per pulse of the switched-capacitor cells of Pauka et al. (18 nW per MHz at 100 mV, i.e. 18 fJ per pulse),
scaled with the square of the pulse-line swing (k = 0.5); and the coldest stage that carries each together with the
static array at the lowest droop.

Run:  python studies/pulse_driver_stages.py     (writes results/pulse_driver_stages.{json,md})
"""
import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parents[1] / "results"
N_BAR = 1e6
C_NODE = 1e-12
E_PAUKA, V_PAUKA = 18e-15, 0.1          # J per pulse at 100 mV (18 nW/MHz)
STAGES = {"20 mK": 19e-6, "140 mK": 200e-6, "1.2 K": 40e-3, "4.2 K": 1.5}
STATIC = 1.4e-6
SLOPES = (3.87, 10.0, 16.6, 33.69)
ROUNDS = (1e-6, 10e-6)


def v0(s):
    return np.log10(20e6 / 50e3) / s             # barrier pulse taking J from 50 kHz to 20 MHz


def coldest(p):
    for name, q in STAGES.items():
        if p + STATIC <= q:
            return name
    return "above 4.2 K"


def main():
    out, L = {}, ["# Pulse drivers for 10^6 barriers", "",
                  "| s (dec/V) | v0 (V) | swing k=0.5 (V) | bound k=0.5 / k=0.9 (fJ) | Pauka-like (fJ) | "
                  "1 us rounds: bound 0.5 / 0.9 / Pauka-like (mW), coldest stage | 10 us rounds: same |", "|---|---|---|---|---|---|---|"]
    for s in SLOPES:
        a = v0(s)
        e = {"bound 0.5": C_NODE * 0.5 * a ** 2 / 0.5, "bound 0.9": C_NODE * 0.1 * a ** 2 / 0.9,
             "Pauka-like": E_PAUKA * (a / 0.5 / V_PAUKA) ** 2}
        row = {"v0": a, "swing": a / 0.5, "energy_J": e, "rounds": {}}
        cells = []
        for t in ROUNDS:
            p = {k: N_BAR * x / t for k, x in e.items()}
            st = {k: coldest(x) for k, x in p.items()}
            row["rounds"][f"{t * 1e6:g} us"] = {"power_W": p, "stage": st}
            cells.append(" / ".join(f"{p[k] * 1e3:.3g} ({st[k]})" for k in e))
        out[f"{s:g}"] = row
        L.append(f"| {s:g} | {a:.3g} | {a / 0.5:.3g} | {e['bound 0.5'] * 1e15:.3g} / {e['bound 0.9'] * 1e15:.3g} | "
                 f"{e['Pauka-like'] * 1e15:.3g} | " + " | ".join(cells) + " |")
    (OUT / "pulse_driver_stages.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT / "pulse_driver_stages.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
