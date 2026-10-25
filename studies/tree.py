"""Electrodes per DAC with the upper levels of a multiplexer tree modelled.

The path from the DAC to an electrode runs through the upper levels of the tree (flow/cosim.py
TreeConfig: series switch on-resistance, sibling off-capacitance, metal-2 wire at each level), for a
single upper level and for upper levels of a given fan-out. The refresh energy includes the control
wires of the selected switches, and the area of N electrodes is compared with one reticle-sized die.
The final line alone (no upper levels) is kept as an upper bound.

Inputs: results/cryogenic.json (4 K proxy switching, tt). Run:  python studies/tree.py
Writes results/tree.{json,md} (about 10 min, mostly the curves against droop rate).
"""
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flow import cosim as C  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
REF = "s10_t0.001"
ANCHORS = {"ESD-dominated, 3.1 mV/s": 3.1e-3, "Darnas et al., 5.5 µV/s": 5.5e-6}
FANOUTS = (None, 1000, 100, 32, 10, 4)          # None: one upper level
W_TREE = (1.0, 10.0, 100.0)
RETICLE = 26e-3 * 33e-3                         # m^2, one full reticle field
FIG5_DESIGNS = ("bootstrapped (transistor level), 0.3 V underdrive", "T-switch + OTA buffer", "TG, no ESD",
                "TG, ESD on the node")


def designs(res):
    rows = [r for r in res["switching"] if r and "error" not in r and r["band"] == "4 K proxy" and r["corner"] == "tt"]
    return {r["design"]: r for r in rows if r["design"] != "bootstrapped, 0.3 V underdrive"}   # ideal drive


def leaf_only(cell):
    """The final line alone, without the levels above it (an upper bound)."""
    return C.LineConfig(c_line_fixed=10e-12 + 1000 * cell["c_line_cell"], r_wire_per=5.5, c_wire_per=2.2e-15)


def evaluate(r, spec, rate, tree):
    s = spec
    bd = C.hold_budget(s, r["residual"], 0.1)
    hold = bd / rate
    n = C.n_max_tree(hold, r["cell"], s, bd, tree)
    e = C.tree_refresh_energy(n, r["cell"], tree) if n > 0 else float("nan")
    return {"n": n, "hold_s": hold, "levels": len(C.tree_levels(n, tree)) if n > 0 else 0,
            "e_refresh": e, "p_per_electrode": e / hold if n > 0 else float("nan"),
            "area_m2": n * tree.pitch ** 2}


def main():
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    spec = res["spec"][REF]
    out = {"anchors": ANCHORS, "reticle_m2": RETICLE, "rows": []}
    base = C.TreeConfig()
    out["n_per_reticle"] = RETICLE / base.pitch ** 2
    for name, r in designs(res).items():
        bd = C.hold_budget(spec, r["residual"], 0.1)
        for an, rate in ANCHORS.items():
            row = {"design": name, "anchor": an, "rate": rate,
                   "n_leaf_only": C.n_max(bd / rate, r["cell"], spec, bd, leaf_only(r["cell"])),
                   "n_flat_met2": C.n_max(bd / rate, r["cell"], spec, bd, C.LineConfig(r_wire_per=5.5, c_wire_per=2.2e-15)),
                   "tree": {}}
            for f in FANOUTS:
                for w in W_TREE:
                    row["tree"][f"F{f or 'one'}_w{w:g}"] = evaluate(r, spec, rate, replace(base, fanout=f, w_tree=w))
            best = max(row["tree"].items(), key=lambda kv: kv[1]["n"])
            row["best"] = {"config": best[0], **best[1]}
            # largest droop rate at which the best tree still refreshes one full reticle of electrodes
            rates = np.geomspace(1e-9, 1e-1, 81)
            n_best = [max(C.n_max_tree(bd / q, r["cell"], spec, bd, replace(base, fanout=f, w_tree=w))
                          for f in FANOUTS for w in W_TREE) for q in rates]
            fits = [q for q, n in zip(rates, n_best) if n >= out["n_per_reticle"]]
            row["rate_for_reticle"] = max(fits) if fits else 0.0
            out["rows"].append(row)
            print(f"{name:55s} {an:26s} leaf-only {row['n_leaf_only']:.2g}  one level "
                  f"{row['tree']['Fone_w10']['n']:.2g}  best {best[0]} {best[1]['n']:.2g}", flush=True)
    # curves for Fig. 5a: best tree against droop rate (stored, so make_figures.py stays fast)
    rates = np.geomspace(1e-8, 1e1, 60)
    out["fig5_rates"] = rates.tolist()
    out["fig5_curves"] = {}
    for name, r in designs(res).items():
        if name not in FIG5_DESIGNS:
            continue
        bd = C.hold_budget(spec, r["residual"], 0.1)
        out["fig5_curves"][name] = [max(C.n_max_tree(bd / q, r["cell"], spec, bd, replace(base, fanout=f, w_tree=w))
                                        for f in FANOUTS for w in W_TREE) for q in rates]
    (OUT / "tree.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def table(out):
    L = ["## Electrodes per DAC with the upper tree levels (4 K proxy, tt, s = 10 dec/V, 99.9 %)", "",
         "Leaf lines of 1000 cells. Upper levels: series switch = cell switch × w, "
         "siblings load each line with w × C_off, met2 wire past each child region at the region's side "
         "length. 'One level' = one upper line carrying all leaf lines. Best = largest N over fan-outs "
         f"{[f or 'one' for f in FANOUTS]} and w {list(W_TREE)}. One reticle (26 × 33 mm²) holds "
         f"{out['n_per_reticle']:.2g} electrodes at the 22 µm pitch.", ""]
    L += ["| design | droop | flat met2 | tree, leaf line only | tree, one level (w 10) | best tree (config) "
          "| levels | refresh energy (pJ) | power per electrode | area at best N (cm²) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        b = r["best"]
        L.append(f"| {r['design']} | {r['anchor']} | {r['n_flat_met2']:.2g} | {r['n_leaf_only']:.2g} | "
                 f"{r['tree']['Fone_w10']['n']:.2g} | {b['n']:.2g} ({b['config']}) | {b['levels']} | "
                 f"{b['e_refresh'] * 1e12:.3g} | {b['p_per_electrode']:.2g} W | {b['area_m2'] * 1e4:.3g} |")
    L += ["", "Largest droop rate at which the best tree still refreshes a full reticle of electrodes "
          f"({out['n_per_reticle']:.2g}):", ""]
    seen = set()
    for r in out["rows"]:
        if r["design"] not in seen:
            seen.add(r["design"])
            L.append(f"- {r['design']}: {r['rate_for_reticle'] * 1e6:.3g} µV/s")
    L.append("")
    return L


if __name__ == "__main__":
    o = main()
    (OUT / "tree.md").write_text("\n".join(table(o)), encoding="utf-8")
