"""Node capacitance, static array and pulse drivers.

The static array at the lowest measured droop (Darnas et al.: 5.5 uV/s on about 1 pF, about 5.5 aA of leakage
through a MOS transistor) for hold nodes of 1 pF, 200 fF and 70 fF, with the tree model of studies/system.py (best
tree, operational budget at 10 dec/V and 99.9 %, 4 K switching models): the same leakage droops a smaller node faster,
the same switch settles it faster (tau_node scales with C), the pedestal residual grows as 1/C, and the cell pitch
shrinks (22, 11 and 9 um). The resistive bound of the pulse drivers (studies/pulse_driver_stages.py) scales with C;
the coldest stage is taken with the static load of the same node.

Run:  python studies/node_size.py      (about 5 min; writes results/node_size.{json,md})
"""
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import system as SYS  # noqa: E402
import pulse_driver_stages as PD  # noqa: E402
import tree as T  # noqa: E402
from flow import cosim as C  # noqa: E402

I_LEAK = 5.5e-6 * 1e-12                    # A: Darnas et al., 5.5 uV/s on about 1 pF
NODES = {1e-12: 22e-6, 0.2e-12: 11e-6, 0.07e-12: 9e-6}
DESIGNS = ("NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive", "TG + dummies")
N_ARRAY = 1e6


def static_load(r, spec, c, pitch):
    cell = dict(r["cell"])
    cell["tau_node"] = r["cell"]["tau_node"] * c / 1e-12
    rr = dict(r, cell=cell, residual=r["residual"] * 1e-12 / c)
    rate = I_LEAK / c
    best = None
    for f in T.FANOUTS:
        for w in T.W_TREE:
            tree = replace(C.TreeConfig(), fanout=f, w_tree=w, c_node=c, pitch=pitch)
            e = T.evaluate(rr, spec, rate, tree)
            if best is None or e["n"] > best[0]["n"]:
                best = (e, tree)
    e, tree = best
    e_addr = SYS.addressing_energy(e["n"], tree)
    p = e["p_per_electrode"] + e_addr / e["hold_s"]
    return {"rate_V_per_s": rate, "n_per_dac": e["n"], "n_per_reticle": T.RETICLE / pitch ** 2,
            "hold_s": e["hold_s"], "p_per_electrode_W": p, "cold_load_W": N_ARRAY * p}


def main():
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    spec = common.budgets()[common.REF]["operational"]
    des = T.designs(res)
    out = {"static": {}, "pulse": {}}
    L = ["# Node size, static array and pulse drivers", "",
         "## Static array at the lowest measured droop (5.5 aA of leakage), 10^6 electrodes", "",
         "| node | pitch (um) | design | droop (uV/s) | electrodes per DAC | per reticle | cold load (uW) |", "|---|---|---|---|---|---|---|"]
    for c, pitch in NODES.items():
        loads = []
        for d in DESIGNS:
            s = static_load(des[d], spec, c, pitch)
            out["static"][f"{c * 1e15:g} fF|{d}"] = s
            loads.append(s["cold_load_W"])
            L.append(f"| {c * 1e15:g} fF | {pitch * 1e6:g} | {d} | {s['rate_V_per_s'] * 1e6:.3g} | {s['n_per_dac']:.2g} | "
                     f"{s['n_per_reticle']:.2g} | {s['cold_load_W'] * 1e6:.3g} |")
        out["static"][f"{c * 1e15:g} fF|max"] = max(loads)
    L += ["", "## Pulse drivers at the resistive bound, 10^6 barriers, with the static load of the same node", "",
          "| node | s (dec/V) | energy k=0.5 / 0.9 (fJ) | 1 us rounds (mW): k=0.5 / 0.9, stage | 10 us rounds (mW): k=0.5 / 0.9, stage |",
          "|---|---|---|---|---|"]
    for c in NODES:
        st = out["static"][f"{c * 1e15:g} fF|max"]
        for s in PD.SLOPES:
            a = PD.v0(s)
            e = {"0.5": c * 0.5 * a ** 2 / 0.5, "0.9": c * 0.1 * a ** 2 / 0.9}
            row = {"energy_J": e}
            cells = []
            for t in PD.ROUNDS:
                p = {k: N_ARRAY * x / t for k, x in e.items()}
                stage = {k: next((n for n, q in PD.STAGES.items() if x + st <= q), "above 4.2 K") for k, x in p.items()}
                row[f"{t * 1e6:g} us"] = {"power_W": p, "stage": stage}
                cells.append(f"{p['0.5'] * 1e3:.3g} / {p['0.9'] * 1e3:.3g}, {stage['0.5']} / {stage['0.9']}")
            out["pulse"][f"{c * 1e15:g} fF|{s:g}"] = row
            L.append(f"| {c * 1e15:g} fF | {s:g} | {e['0.5'] * 1e15:.3g} / {e['0.9'] * 1e15:.3g} | " + " | ".join(cells) + " |")
    (OUT / "node_size.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    (OUT / "node_size.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
