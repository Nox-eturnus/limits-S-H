"""Electrodes per DAC with the operational budget and a finite DAC settling time, and the DAC power.

The operational budget is the frame-tracked budget over M = 4 repeated CZ gates
(studies/repeated_gates.py), at which a processor under error correction would run. The electrode
count is computed with it and, for comparison, with the untracked single-gate budget.

The DAC must settle the 1.2 V line swing to eps (about 0.1 mV), which a cryogenic DAC may not do in
nanoseconds. The count is therefore given for DAC settling times of 2 ns to 1 us (the t_0 of Eq. (4)),
and the DAC power is shared over the electrodes it serves, using the 157 uW of the cryo-CMOS
integrator DAC of Enthoven et al. (IEEE TCAS-I 2026) as a reference.

Inputs: results/cryogenic.json, results/repeated_gates.json. Run:  python studies/system_budget.py
Writes results/system_budget.{json,md} (about 15 min, mostly the curves of Fig. 5a).
"""
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import tree as T  # noqa: E402
from flow import cosim as C  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
M_QEC = 4                                    # CZ gates per data qubit per surface-code round
T_DAC = (2e-9, 10e-9, 100e-9, 1e-6)          # DAC settling per slot (the t_0 of Eq. (4))
P_DAC = 157e-6                               # W, Enthoven et al. 2026, 4.2 K
RATES = np.geomspace(1e-8, 1e1, 60)


def operational_spec(res):
    """Frame-tracked budget for M = 4 repeated gates at s = 10 dec/V and 99.9 %, scaled onto the
    budget of results/cryogenic.json so that both budgets come from the same qubit layer."""
    rg = json.loads((ROOT / "results" / "repeated_gates.json").read_text(encoding="utf-8"))
    row = next(r for r in rg["rows"] if r["s"] == 10.0 and r["target"] == 1e-3)
    untracked = res["spec"][T.REF]
    return untracked, untracked * row["frame"][str(M_QEC)] / row["v1_exact"]


def best_tree(r, spec, rate, t_dac):
    base = replace(C.TreeConfig(), t_overhead=t_dac)
    best = None
    for f in T.FANOUTS:
        for w in T.W_TREE:
            e = T.evaluate(r, spec, rate, replace(base, fanout=f, w_tree=w))
            if best is None or e["n"] > best["n"]:
                best = {"config": f"F{f or 'one'}_w{w:g}", **e}
    return best


def main():
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    spec_untracked, spec_op = operational_spec(res)
    out = {"spec_untracked": spec_untracked, "spec_operational": spec_op, "m_qec": M_QEC, "t_dac": T_DAC,
           "p_dac": P_DAC, "rows": [], "n_per_reticle": T.RETICLE / C.TreeConfig().pitch ** 2}
    print(f"budget at s = 10, 99.9 %: untracked M = 1 {spec_untracked * 1e3:.3f} mV, "
          f"tracked M = {M_QEC} {spec_op * 1e3:.3f} mV", flush=True)
    for name, r in T.designs(res).items():
        for an, rate in T.ANCHORS.items():
            row = {"design": name, "anchor": an, "rate": rate, "budget": {}}
            for label, spec in (("untracked", spec_untracked), ("operational", spec_op)):
                bd = C.hold_budget(spec, r["residual"], 0.1)
                row["budget"][label] = {
                    "hold_s": bd / rate,
                    "flat_met2": C.n_max(bd / rate, r["cell"], spec, bd, C.LineConfig(r_wire_per=5.5, c_wire_per=2.2e-15)),
                    "tree": {f"{t:g}": best_tree(r, spec, rate, t) for t in T_DAC}}
                for t, b in row["budget"][label]["tree"].items():
                    b["p_dac_per_electrode"] = P_DAC / b["n"] if b["n"] > 0 else float("nan")
            out["rows"].append(row)
            u, o = row["budget"]["untracked"]["tree"], row["budget"]["operational"]["tree"]
            print(f"{name[:40]:40s} {an[:14]:14s} N untracked {u['2e-09']['n']:.2g}, operational "
                  + ", ".join(f"{t}: {o[t]['n']:.2g}" for t in o), flush=True)
    # curves of Fig. 5a with the operational budget and the 2 ns DAC, and the reticle droop rate
    out["fig5_rates"] = RATES.tolist()
    out["fig5_curves"], out["fig5_flat"], out["rate_for_reticle"] = {}, {}, {}
    for name, r in T.designs(res).items():
        bd = C.hold_budget(spec_op, r["residual"], 0.1)
        if name in T.FIG5_DESIGNS:
            out["fig5_curves"][name] = [best_tree(r, spec_op, q, 2e-9)["n"] for q in RATES]
            out["fig5_flat"][name] = [C.n_max(bd / q, r["cell"], spec_op, bd,
                                              C.LineConfig(r_wire_per=5.5, c_wire_per=2.2e-15)) for q in RATES]
        grid = np.geomspace(1e-7, 1e-2, 41)
        fits = [q for q in grid if best_tree(r, spec_op, q, 2e-9)["n"] >= out["n_per_reticle"]]
        out["rate_for_reticle"][name] = max(fits) if fits else 0.0
    (OUT / "system_budget.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    return out


def table(out):
    L = ["## Electrodes per DAC with the operational budget and a finite DAC settling time", "",
         f"s = 10 dec/V, 99.9 %, 4 K switching models. Untracked single-gate budget {out['spec_untracked'] * 1e3:.3f} mV "
         f"(per gate); operational budget {out['spec_operational'] * 1e3:.3f} mV = frame-tracked, M = {out['m_qec']} "
         "repeated gates per QEC round. Best tree over fan-outs and switch widths. DAC power share: "
         f"{out['p_dac'] * 1e6:.0f} µW (Enthoven et al. 2026) / N.", "",
         "| design | droop | N, untracked, 2 ns | N, operational, 2 ns | 10 ns | 100 ns | 1 µs | flat met2, operational "
         "| refresh power / electrode (operational, 2 ns) | DAC power / electrode |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        u, o = r["budget"]["untracked"]["tree"], r["budget"]["operational"]["tree"]
        L.append(f"| {r['design']} | {r['anchor']} | {u['2e-09']['n']:.2g} | {o['2e-09']['n']:.2g} | {o['1e-08']['n']:.2g} | "
                 f"{o['1e-07']['n']:.2g} | {o['1e-06']['n']:.2g} | {r['budget']['operational']['flat_met2']:.2g} | "
                 f"{o['2e-09']['p_per_electrode']:.2g} W | {o['2e-09']['p_dac_per_electrode']:.2g} W |")
    L += ["", "Largest droop rate at which the best tree refreshes a full reticle "
          f"({out['n_per_reticle']:.2g} electrodes), operational budget, 2 ns DAC:", ""]
    L += [f"- {d}: {q * 1e6:.3g} µV/s" for d, q in out["rate_for_reticle"].items()]
    (OUT / "system_budget.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    table(main())
