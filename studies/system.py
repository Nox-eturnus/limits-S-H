"""Electrode counts, power per cryostat stage, calibration time and addressing overheads.

  Counts       electrodes per DAC with the operational budget (studies/operational_budget.py), the area cap
               of one reticle, and the physical length of a flat line (a serpentine through the cell array:
               n cells at pitch p need a wire n p long inside a square of side sqrt(n) p).
  Power        per temperature stage for 10^6 electrodes. The ESD-free hold node is an internal node bonded
               to the gate electrodes, so the hold array and the tree below the DAC sit at the qubit
               temperature; the DACs sit at 4 K. Their dissipation is compared with the cooling power of a
               dilution refrigerator per stage (Krinner et al. 2019, Table 1: 1.5 W at 4.2 K, 40 mW at
               1.2 K, 200 uW at 140 mK, 19 uW at 20 mK).
  Calibration  time for 10^6 channels: two pedestal points, two droop readings and one pulse amplitude per
               channel, for measurement times from 3 us (RF reflectometry, Thomas et al. 2025) to 100 ms
               (qubit-based), and parallel readout of 1 to 10^4 channels.
  Overheads    left out of the refresh energy: the address lines of each tree level (log2 F lines along
               the line, half of them toggling per refresh) and the decoder gates; and the largest coupling
               capacitance from a toggling select or clock line to a hold node.

Inputs: results/cryogenic.json, results/repeated_gates.json. studies/droop_anchors.py recomputes these
quantities at the droop of protection diodes converted to a 1 pF node.
Run:  python studies/system.py      (about 15 min; writes results/system.{json,md})
"""
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import system_budget as SB  # noqa: E402
import tree as T  # noqa: E402
from flow import cosim as C  # noqa: E402

COOLING = {"4.2 K": 1.5, "1.2 K (still)": 40e-3, "140 mK (cold plate)": 200e-6, "20 mK (mixing chamber)": 19e-6}
N_ARRAY = 1e6
T_MEAS = (3e-6, 1e-3, 0.1)
PARALLEL = (1, 100, 1e4)
MEAS_PER_CHANNEL = 5
C_DEC_GATE = 2e-15                 # F, input capacitance of one decoder gate (order of magnitude)
V_SEL = 2.1


def met2():
    return C.LineConfig(r_wire_per=5.5, c_wire_per=2.2e-15)


def addressing_energy(n, tree):
    """Address lines along each upper-level line (log2 F wires, half toggling) plus F decoder gates per level."""
    e = 0.0
    for f, side, leaf in C.tree_levels(n, tree):
        bits = np.ceil(np.log2(max(f, 2)))
        e += 0.5 * bits * tree.c_wire * f * side * V_SEL ** 2 + f * C_DEC_GATE * V_SEL ** 2
    return e


def main():
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    bud = common.budgets()
    spec = bud[common.REF]["operational"]
    pitch = C.TreeConfig().pitch
    n_ret = T.RETICLE / pitch ** 2
    out = {"spec": spec, "n_per_reticle": n_ret, "rows": [], "cooling": COOLING}
    for name, r in T.designs(res).items():
        bd = C.hold_budget(spec, r["residual"], 0.1)
        for an, rate in T.ANCHORS.items():
            flat = C.n_max(bd / rate, r["cell"], spec, bd, met2())
            tree = {f"{t:g}": SB.best_tree(r, spec, rate, t) for t in SB.T_DAC}
            b = tree["2e-09"]
            cfg = C.TreeConfig(fanout=None if b["config"].startswith("Fone") else float(b["config"][1:].split("_")[0]),
                               w_tree=float(b["config"].split("_w")[1]))
            e_addr = addressing_energy(b["n"], cfg) if b["n"] > 0 else float("nan")
            row = {"design": name, "anchor": an, "rate": rate, "hold_s": bd / rate, "flat": flat,
                   "flat_wire_m": flat * pitch, "flat_square_mm": np.sqrt(flat) * pitch * 1e3,
                   "tree": tree, "n_capped": min(b["n"], n_ret), "area_limited": b["n"] > n_ret,
                   "e_refresh": b["e_refresh"], "e_addressing": e_addr, "p_refresh": b["p_per_electrode"],
                   "p_addressing": e_addr / (bd / rate), "p_dac": SB.P_DAC / min(b["n"], n_ret),
                   "levels": b["levels"], "config": b["config"]}
            # 10^6 electrodes: cold-stage load (tree + hold array) and 4 K load (DACs)
            n_dac = np.ceil(N_ARRAY / row["n_capped"])
            row["cold_load_W"] = N_ARRAY * (row["p_refresh"] + row["p_addressing"])
            row["dacs"] = n_dac
            row["4K_load_W"] = n_dac * SB.P_DAC
            out["rows"].append(row)
            print(f"{name[:40]:40s} {an[:24]:24s} flat {flat:.2g} tree {b['n']:.2g} cold {row['cold_load_W'] * 1e6:.3g} uW", flush=True)
    out["rate_for_reticle"] = {}
    for name, r in T.designs(res).items():
        grid = np.geomspace(1e-7, 1e-2, 41)
        fits = [q for q in grid if SB.best_tree(r, spec, q, 2e-9)["n"] >= n_ret]
        out["rate_for_reticle"][name] = max(fits) if fits else 0.0
    out["fig5_rates"] = SB.RATES.tolist()
    out["fig5_curves"], out["fig5_flat"] = {}, {}
    for name, r in T.designs(res).items():
        if name in T.FIG5_DESIGNS:
            bd = C.hold_budget(spec, r["residual"], 0.1)
            out["fig5_curves"][name] = [SB.best_tree(r, spec, q, 2e-9)["n"] for q in SB.RATES]
            out["fig5_flat"][name] = [C.n_max(bd / q, r["cell"], spec, bd, met2()) for q in SB.RATES]
    out["calibration_s"] = {f"{t:g}|{p:g}": MEAS_PER_CHANNEL * N_ARRAY * t / p for t in T_MEAS for p in PARALLEL}
    out["select_coupling_max_fF"] = {k: b["operational"] * 1e-12 / V_SEL * 1e15 for k, b in bud.items()}
    (OUT / "system.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    return out


def table(out):
    L = [f"## System quantities, s = 10 dec/V, 99.9 %, operational budget {out['spec'] * 1e3:.3f} mV, 4 K switching models", "",
         f"One reticle (26 × 33 mm²) holds {out['n_per_reticle']:.3g} cells of 1 pF at 22 µm pitch.", "",
         "| design | droop | flat line N | flat wire (m) / square side (mm) | tree N, 2 ns / 100 ns / 1 µs | capped at reticle | levels, config "
         "| refresh / addressing / DAC power per electrode | 10^6 electrodes: cold-stage load / DACs at 4 K |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        t = r["tree"]
        L.append(f"| {r['design']} | {r['anchor']} | {r['flat']:.2g} | {r['flat_wire_m']:.2f} / {r['flat_square_mm']:.1f} | "
                 f"{t['2e-09']['n']:.2g} / {t['1e-07']['n']:.2g} / {t['1e-06']['n']:.2g} | {r['n_capped']:.2g}{' (area)' if r['area_limited'] else ''} | "
                 f"{r['levels']}, {r['config']} | {r['p_refresh']:.2g} / {r['p_addressing']:.2g} / {r['p_dac']:.2g} W | "
                 f"{r['cold_load_W'] * 1e6:.3g} µW / {r['dacs']:.0f} × 157 µW = {r['4K_load_W'] * 1e3:.3g} mW |")
    L += ["", "Cooling power (Krinner et al. 2019): " + ", ".join(f"{k}: {v:g} W" for k, v in out["cooling"].items()), "",
          "Largest droop rate at which the best tree refreshes a full reticle:", ""]
    L += [f"- {d}: {q * 1e6:.3g} µV/s" for d, q in out["rate_for_reticle"].items()]
    L += ["", "### Calibration time for 10^6 channels, 5 measurements per channel (s)", "",
          "| time per measurement | 1 in parallel | 100 | 10^4 |", "|---|---|---|---|"]
    for t in T_MEAS:
        L.append(f"| {t:g} s | " + " | ".join(f"{out['calibration_s'][f'{t:g}|{p:g}']:.3g}" for p in PARALLEL) + " |")
    L += ["", "### Largest coupling from a toggling select line (2.1 V) to a 1 pF hold node (fF)", ""]
    L += [f"- {k}: {v:.3g} fF" for k, v in out["select_coupling_max_fF"].items()]
    (OUT / "system.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    table(main())
