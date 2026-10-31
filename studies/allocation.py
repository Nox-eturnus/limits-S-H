"""Joint error allocation with the untracked budgets and the one-cell-per-channel margins.

The pedestal residual is judged against the untracked budget, its common part with equal signs and its
mismatch part with independent signs (studies/residual_accounting.py); its margin alone is m = 1 / u, from
results/cell_margins.json. Offsets that change at every refresh (kT/C, sampled DAC noise) have independent
signs and are judged against the untracked single-gate budget b_ind. Device noise uses its 1/f budget a_b
(results/qubit_bounds.json). The share of the target left for deterministic offsets is 1 - share, and the
pedestal, which adds as a voltage to the settling allowance (0.1 of the budget) and the droop, keeps
    m_joint = m * (sqrt(1 - share) - 0.1).

Run:  python studies/allocation.py     (seconds; writes results/allocation.{json,md})
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
KB = 1.380649e-23
DESIGNS = {"NMOS": "NMOS, 0.3 V underdrive|4 K proxy",
           "bootstrapped": "bootstrapped (transistor level), 0.3 V underdrive|4 K proxy",
           "TG + dummies": "TG + dummies|4 K proxy"}
POINTS = {"s33.69_t0.0001": (33.69, 1e-4), "s10_t0.001": (10.0, 1e-3)}


def main():
    ra = json.loads((OUT / "cell_margins.json").read_text(encoding="utf-8"))
    qb = json.loads((ROOT / "results" / "qubit_bounds.json").read_text(encoding="utf-8"))
    ktc = float(np.sqrt(KB * 4.2 / 1e-12))
    out = {"ktc": ktc, "points": {}}
    for key, (s, t) in POINTS.items():
        b_ind = ra["budgets"][key]["b_ind"]
        a_b = next(r["100 s"] for r in qb["one_over_f"] if r["s"] == s and r["target"] == t)
        rows = []
        for dev in (0.0, 9e-6, 49e-6):
            for dac in (0.0, 50e-6, 120e-6, 188e-6):
                share = (dev / a_b) ** 2 + (ktc ** 2 + dac ** 2) / b_ind ** 2
                f = max(np.sqrt(max(1 - share, 0.0)) - 0.1, 0.0)
                row = {"device": dev, "dac": dac, "share": share}
                for lab, d in DESIGNS.items():
                    m = ra["designs"][d]["margin"][f"{key}|full|mixed"]
                    row[lab] = {"alone": m, "joint": m * f}
                rows.append(row)
        # largest sampled DAC noise for a joint margin of one, quiet device (9 uV/rtHz)
        dac_max = {}
        for lab, d in DESIGNS.items():
            m = ra["designs"][d]["margin"][f"{key}|full|mixed"]
            need = 1 / m + 0.1
            x = 1 - need ** 2 - (9e-6 / a_b) ** 2 - ktc ** 2 / b_ind ** 2
            dac_max[lab] = float(b_ind * np.sqrt(x)) if x > 0 else 0.0
        out["points"][key] = {"b_ind": b_ind, "one_over_f_budget": a_b, "rows": rows, "dac_max_quiet": dac_max}
    (OUT / "allocation.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["## Joint allocation, one cell per channel (pedestal margin alone / joint, worst of 10^6, 4 K band)", ""]
    for key, p in out["points"].items():
        L += [f"### {key}: b_ind {p['b_ind'] * 1e6:.0f} µV, 1/f budget {p['one_over_f_budget'] * 1e6:.0f} µV/√Hz", "",
              "| device at 1 Hz | sampled DAC rms | share of target | " + " | ".join(DESIGNS) + " |", "|---|---|---|" + "---|" * len(DESIGNS)]
        for r in p["rows"]:
            L.append(f"| {r['device'] * 1e6:g} µV/√Hz | {r['dac'] * 1e6:g} µV | {r['share']:.3g} | "
                     + " | ".join(f"{r[k]['alone']:.2f} / {r[k]['joint']:.2f}" for k in DESIGNS) + " |")
        L += ["", "Largest sampled DAC noise for a joint margin of one (9 µV/√Hz device): "
              + ", ".join(f"{k} {v * 1e6:.0f} µV" for k, v in p["dac_max_quiet"].items()), ""]
    (OUT / "allocation.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
