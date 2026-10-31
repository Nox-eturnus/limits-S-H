"""Measured droop rates converted to a 1 pF hold node, and every system quantity at the converted anchor.

A droop rate is a leakage current divided by the capacitance on which it was measured, so it transfers to
the 1 pF hold node of this work only through the leakage current:
  van Staveren et al. 2025   3.1 mV/s typical (60 uV/s to 18 mV/s) on a 15 pF hold capacitor, set by the
                             ESD diodes: 46.5 fA (0.9 fA to 270 fA), i.e. 46.5 mV/s (0.9 mV/s to 0.27 V/s)
                             on 1 pF.
  Darnas et al. 2026         5.5 uV/s on a 70 fF sample capacitor plus about 1 pF of pad, bond and
                             interconnect: about 5.9 aA, i.e. 5.9 uV/s on 1 pF, within the accuracy of the
                             parasitic estimate; it is kept at 5.5 uV/s.
  Jadot et al. 2023          0.44 uV/s for an active router; its node capacitance is not converted.
This script computes, at 46.5 mV/s, the line models of studies/cryogenic_report.py, studies/tree.py and
studies/system_budget.py, the system rows of studies/system.py (counts, wire length, power per stage, DACs)
and the source impedance of each design's best tree. 3.1 mV/s is kept as a reference row: it is the droop
of a 1 pF node whose leakage is 15 times lower, for example with diodes sized for the node.

Run:  python studies/droop_anchors.py      (about 2 min; writes results/droop_anchors.{json,md})
"""
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
for p in (ROOT, ROOT / "studies"):
    sys.path.insert(0, str(p))
import operational_budget as common  # noqa: E402
import cryogenic_report as FR  # noqa: E402  (studies/cryogenic_report.py: LINES, tree_lines, droop_budget)
import system as SY  # noqa: E402
import system_budget as SB  # noqa: E402
import tree as T  # noqa: E402
from flow import cosim as C  # noqa: E402

C_REF = {"van Staveren et al. 2025": 15e-12, "Darnas et al. 2026": 70e-15 + 1e-12}
C_NODE = 1e-12
ESD_1PF = 3.1e-3 * C_REF["van Staveren et al. 2025"] / C_NODE          # 46.5 mV/s
ANCHORS = {"ESD-dominated on 1 pF, 46.5 mV/s": ESD_1PF, "reference, 3.1 mV/s": 3.1e-3}
BAND = {"van Staveren et al., low": 60e-6 * 15, "van Staveren et al., typical": ESD_1PF,
        "van Staveren et al., high": 18e-3 * 15, "Darnas et al.": 5.5e-6, "Jadot et al. (not converted)": 0.44e-6}


def tree_source(cell, fanout, w_tree, n):
    """Series resistance DAC -> far end of a leaf line, and the leaf-line capacitance (studies/extra_bands.py)."""
    tree = C.TreeConfig(fanout=fanout, w_tree=w_tree)
    r_on = cell["tau_node"] / tree.c_node
    r, c_leaf = tree.r_src, 0.0
    for k, (f, side, leaf) in enumerate(C.tree_levels(n, tree)):
        if k:
            r += r_on / tree.w_tree
        r += tree.r_wire * f * side
        if leaf:
            c_leaf = tree.c_wire * f * side + f * cell["c_line_cell"]
    return float(r), float(c_leaf)


def main():
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    bud = common.budgets()
    spec_op = bud[common.REF]["operational"]
    spec_pg = res["spec"][common.REF]
    pitch = C.TreeConfig().pitch
    n_ret = T.RETICLE / pitch ** 2
    out = {"anchors": ANCHORS, "band_1pF": BAND, "c_ref": C_REF, "spec_operational": spec_op,
           "spec_per_gate": spec_pg, "n_per_reticle": n_ret, "rows": []}
    for name, r in T.designs(res).items():
        for an, rate in ANCHORS.items():
            row = {"design": name, "anchor": an, "rate": rate}
            # SI Table S4, per-gate rows (studies/cryogenic_report.py line models, one-level tree of studies/tree.py)
            bd, s = FR.droop_budget(res, r)
            lines = {**FR.LINES, **FR.tree_lines(r["cell"])}
            row["s4_lines"] = {k: C.n_max(bd / rate, r["cell"], s, bd, ln) for k, ln in lines.items()}
            row["s4_one_level_w10"] = T.evaluate(r, s, rate, replace(C.TreeConfig(), fanout=None, w_tree=10.0))["n"]
            row["s4_best_per_gate"] = SB.best_tree(r, s, rate, 2e-9)["n"]
            # operational budget: system quantities (studies/system.py)
            bd = C.hold_budget(spec_op, r["residual"], 0.1)
            flat = C.n_max(bd / rate, r["cell"], spec_op, bd, SY.met2())
            tree = {f"{t:g}": SB.best_tree(r, spec_op, rate, t) for t in SB.T_DAC}
            b = tree["2e-09"]
            fan = None if b["config"].startswith("Fone") else float(b["config"][1:].split("_")[0])
            w = float(b["config"].split("_w")[1])
            cfg = C.TreeConfig(fanout=fan, w_tree=w)
            e_addr = SY.addressing_energy(b["n"], cfg) if b["n"] > 0 else float("nan")
            n_cap = min(b["n"], n_ret)
            row.update({"hold_s": bd / rate, "flat": flat, "flat_wire_m": flat * pitch,
                        "flat_square_mm": np.sqrt(flat) * pitch * 1e3,
                        "tree_n": {t: v["n"] for t, v in tree.items()}, "n_capped": n_cap,
                        "levels": b["levels"], "config": b["config"], "e_refresh": b["e_refresh"],
                        "e_addressing": e_addr, "p_refresh": b["p_per_electrode"],
                        "p_addressing": e_addr / (bd / rate), "p_dac": SB.P_DAC / n_cap})
            row["dacs"] = float(np.ceil(SY.N_ARRAY / n_cap))
            row["cold_load_W"] = SY.N_ARRAY * (row["p_refresh"] + row["p_addressing"])
            row["4K_load_W"] = row["dacs"] * SB.P_DAC
            row["tree_source"] = tree_source(r["cell"], fan if fan else 1e9, w, b["n"]) if fan else (float("nan"), float("nan"))
            out["rows"].append(row)
            print(f"{name[:42]:42s} {an[:26]:26s} flat {flat:.2g} tree {b['n']:.2g} ({b['config']}, {b['levels']} levels) "
                  f"cold {row['cold_load_W'] * 1e6:.3g} uW, R_src {row['tree_source'][0] / 1e3:.3g} kOhm", flush=True)
    (OUT / "droop_anchors.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    return out


def table(out):
    L = ["## Droop anchors converted to a 1 pF node", "",
         "van Staveren et al.: 3.1 mV/s on 15 pF = 46.5 fA, i.e. 46.5 mV/s on 1 pF (range 0.9 mV/s to 0.27 V/s). "
         "Darnas et al.: 5.5 µV/s on 70 fF + ~1 pF, unchanged. s = 10 dec/V, 99.9 %, 4 K switching models.", "",
         f"Operational budget {out['spec_operational'] * 1e3:.3f} mV, per-gate {out['spec_per_gate'] * 1e3:.3f} mV; "
         f"one reticle holds {out['n_per_reticle']:.3g} cells.", "",
         "### System rows, operational budget", "",
         "| design | droop | hold (s) | flat N | flat wire (m) / square (mm) | tree N, 2 ns / 100 ns / 1 µs | levels, config "
         "| tree source R / C_leaf | refresh / addressing / DAC per electrode | 10^6 electrodes: cold-stage / DACs at 4 K |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        t = r["tree_n"]
        L.append(f"| {r['design']} | {r['anchor']} | {r['hold_s']:.3g} | {r['flat']:.2g} | {r['flat_wire_m']:.2f} / "
                 f"{r['flat_square_mm']:.1f} | {t['2e-09']:.2g} / {t['1e-07']:.2g} / {t['1e-06']:.2g} | {r['levels']}, "
                 f"{r['config']} | {r['tree_source'][0] / 1e3:.3g} kΩ / {r['tree_source'][1] * 1e12:.3g} pF | "
                 f"{r['p_refresh']:.2g} / {r['p_addressing']:.2g} / {r['p_dac']:.2g} W | "
                 f"{r['cold_load_W'] * 1e6:.3g} µW / {r['dacs']:.0f} × 157 µW = {r['4K_load_W'] * 1e3:.3g} mW |")
    L += ["", "### SI Table S4 rows, per-gate budget", ""]
    keys = list(out["rows"][0]["s4_lines"])
    L += ["| design | droop | " + " | ".join(keys) + " | one level, w 10 | best tree |", "|---|---|" + "---|" * (len(keys) + 2)]
    for r in out["rows"]:
        L.append(f"| {r['design']} | {r['anchor']} | " + " | ".join(f"{r['s4_lines'][k]:.2g}" for k in keys)
                 + f" | {r['s4_one_level_w10']:.2g} | {r['s4_best_per_gate']:.2g} |")
    (OUT / "droop_anchors.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    table(main())
