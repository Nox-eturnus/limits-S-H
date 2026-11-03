"""Pulse drivers per unit node capacitance.

studies/pulse_driver_stages.py for 1 pF nodes, repeated for 200 fF. The resistive bound C_node (1 - k) v0^2 / k scales
with the node capacitance; the Pauka-like cell, which spends 7.2 times the k = 0.5 bound on a 1 pF node, is scaled with
the node as well.

Run:  python studies/pulse_driver_node_size.py     (writes results/pulse_driver_node_size.{json,md})
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import pulse_driver_stages as S  # noqa: E402


def main():
    out, L = {}, ["# Pulse drivers for 10^6 barriers, 1 pF and 200 fF nodes", "",
                  "Energy per pulse per pF of node: bound k=0.5 = (1-k) v0^2 / k per pF.", "",
                  "| node | s (dec/V) | bound k=0.5 / k=0.9 (fJ) | Pauka-like (fJ) | 1 us rounds (mW, stage) | 10 us rounds (mW, stage) |",
                  "|---|---|---|---|---|---|"]
    for c in (1e-12, 0.2e-12):
        for s in S.SLOPES:
            a = S.v0(s)
            b5 = c * 0.5 * a ** 2 / 0.5
            e = {"bound 0.5": b5, "bound 0.9": c * 0.1 * a ** 2 / 0.9,
                 "Pauka-like": S.E_PAUKA * (a / 0.5 / S.V_PAUKA) ** 2 * c / 1e-12}
            row = {}
            cells = []
            for t in S.ROUNDS:
                p = {k: S.N_BAR * x / t for k, x in e.items()}
                st = {k: S.coldest(x) for k, x in p.items()}
                row[f"{t * 1e6:g} us"] = {"power_W": p, "stage": st}
                cells.append(" / ".join(f"{p[k] * 1e3:.3g} ({st[k]})" for k in e))
            out[f"{c * 1e15:g} fF|{s:g}"] = {"energy_J": e, "rounds": row}
            L.append(f"| {c * 1e15:g} fF | {s:g} | {e['bound 0.5'] * 1e15:.3g} / {e['bound 0.9'] * 1e15:.3g} | "
                     f"{e['Pauka-like'] * 1e15:.3g} | " + " | ".join(cells) + " |")
    (OUT / "pulse_driver_node_size.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT / "pulse_driver_node_size.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
