"""The tree settling model against SPICE at full depth.

The slot model charges the path from the DAC to the far end of the selected leaf line with its Elmore delay
times ln(dV / eps) (flow/cosim.tree_path, tree_slot_time); tests/test_cosim.py checks a two-level tree, while
the best trees have three to eight levels. Here the whole path of each design's best tree at both droop
anchors (studies/droop_anchors.py, 4 K switching models, operational budget) is written as an RC network: the
DAC resistance and root capacitance, each line as a ladder of n_seg segments of wire resistance and of wire
plus sibling off capacitance, and the on-resistance of the selected switch between lines. ngspice gives the
time at which the far end of the leaf line stays within eps of a 1.2 V step; the model's line term should be
at least as long (conservative) and not much longer.

Run:  python studies/tree_spice.py      (about a minute; writes results/tree_spice.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import tree as T  # noqa: E402
from flow import cosim as C  # noqa: E402

WORK = ROOT / "build" / "tree_spice" / "tree_spice"
N_SEG = 60


def netlist(n, cell, tree):
    r_on = cell["tau_node"] / tree.c_node
    L = ["* tree path", "VS s 0 PWL(0 0 1p 1.2)", f"RS s a0 {tree.r_src:.6g}", f"CR a0 0 {tree.c_root:.6g}"]
    node, k = "a0", 0
    for lvl, (f, side, leaf) in enumerate(C.tree_levels(n, tree)):
        if lvl:
            nxt = f"a{k + 1}"
            L.append(f"RSW{lvl} {node} {nxt} {r_on / tree.w_tree:.6g}")
            node, k = nxt, k + 1
        length = f * side
        c_sw = f * (cell["c_line_cell"] if leaf else tree.w_tree * cell["c_line_cell"])
        r_seg = tree.r_wire * length / N_SEG
        c_seg = (tree.c_wire * length + c_sw) / N_SEG
        for i in range(N_SEG):
            nxt = f"a{k + 1}"
            L += [f"R{lvl}_{i} {node} {nxt} {r_seg:.6g}", f"C{lvl}_{i} {nxt} 0 {c_seg:.6g}"]
            node, k = nxt, k + 1
    return L, node


def main():
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    an = json.loads((OUT / "droop_anchors.json").read_text(encoding="utf-8"))
    sysj = json.loads((ROOT / "results" / "system.json").read_text(encoding="utf-8"))
    spec = an["spec_operational"]
    eps = 0.1 * spec
    designs = T.designs(res)
    cases = [(r["design"], r["anchor"], r["config"], r["tree_n"]["2e-09"]) for r in an["rows"]]
    cases += [(r["design"], r["anchor"], r["config"], min(r["tree"]["2e-09"]["n"], sysj["n_per_reticle"]))
              for r in sysj["rows"] if r["anchor"].startswith("Darnas")]
    out = {"eps": eps, "n_seg": N_SEG, "rows": []}
    WORK.mkdir(parents=True, exist_ok=True)
    for i, (d, anchor, cfg, n) in enumerate(cases):
        cell = designs[d]["cell"]
        fan = None if cfg.startswith("Fone") else float(cfg[1:].split("_")[0])
        tree = C.TreeConfig(fanout=fan, w_tree=float(cfg.split("_w")[1]))
        tau, _, _ = C.tree_path(n, cell, tree)
        t_model = tau * np.log(tree.dv_line / eps)
        L, far = netlist(n, cell, tree)
        L += [f".save v({far})", f".tran {t_model / 4000:.3e} {2.5 * t_model:.3e}", ".end", ""]
        w = C.spice.run_ngspice("\n".join(L), WORK, f"tree{i}")
        t, v = w["time"], w[f"v({far})"]
        late = np.nonzero(np.abs(v - 1.2) > eps)[0]
        t_spice = float(t[late[-1]]) if late.size else 0.0
        row = {"design": d, "anchor": anchor, "config": cfg, "n": n, "levels": len(C.tree_levels(n, tree)),
               "t_model": float(t_model), "t_spice": t_spice, "ratio": t_spice / t_model}
        out["rows"].append(row)
        print(f"{d[:40]:40s} {anchor[:22]:22s} {cfg:10s} N {n:.2g} levels {row['levels']}: model {t_model * 1e9:.4g} ns, "
              f"SPICE {t_spice * 1e9:.4g} ns, ratio {row['ratio']:.3f}", flush=True)
    (OUT / "tree_spice.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["## Settling of the full tree path: Elmore model against SPICE", "",
         f"eps = {eps * 1e6:.0f} µV, 1.2 V step, {N_SEG} RC segments per line.", "",
         "| design | droop | best tree | electrodes | lines on the path | model (ns) | SPICE (ns) | SPICE / model |",
         "|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        L.append(f"| {r['design']} | {r['anchor']} | {r['config']} | {r['n']:.2g} | {r['levels']} | {r['t_model'] * 1e9:.4g} | "
                 f"{r['t_spice'] * 1e9:.4g} | {r['ratio']:.3f} |")
    (OUT / "tree_spice.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
