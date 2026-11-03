"""Pair-to-pair spread (studies/pair_spread.py) with the calibrations of studies/calibration_nonlinear.py.

The budget tables of results/pair_spread.json (log-normal spread of the local slope and of the Stark coefficient) are
combined with the deviation of a per-channel line and of a per-channel quadratic, each with the calibration-point
error (a tenth of the nominal equal-sign budget per point), 4 K band, levels set open-loop.

Run:  python studies/pair_spread_nonlinear.py     (writes results/pair_spread_nonlinear.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import cell_margins as CM  # noqa: E402
import tail_corrected as Y8  # noqa: E402
import pair_spread as Q  # noqa: E402
import calibration_nonlinear as C11  # noqa: E402

POINTS = ("33.69 dec/V, 99.99%", "33.69 dec/V, 99.9%")


def main():
    recs = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    tabs = json.loads((ROOT / "results" / "pair_spread.json").read_text(encoding="utf-8"))["tables"]
    out = {}
    L = ["## Pair-to-pair spread with line / quadratic calibration and calibration noise (4 K band)", "",
         "| Design | Point | Calibration | " + " | ".join(Q.SPREADS) + " |", "|---|---|---|" + "---|" * len(Q.SPREADS)]
    for pn in POINTS:
        tab = {k: (np.array(v) if k != "nominal" else v) for k, v in tabs[pn].items()}
        sig_m = tab["nominal"]["b_eq"] / 10
        for d in Y8.FIG6:
            x, v, std, nominal, _ = CM.prepare(recs[f"{d}|4 K proxy"])
            tau = Y8.tau(d, "4 K proxy")
            for cal, deg in (("line, noise", 1), ("quadratic, noise", 2)):
                A, H = C11.poly_operator(v, std, deg)
                m, sd = C11.moments(x, v, std, A, H, "full", sig_m)
                row = {}
                for sn, (ss, sa) in Q.SPREADS.items():
                    row[sn] = Q.margin_joint(m * (1 + tau), sd * (1 + tau), Q.rule(tab, ss, sa))[0]
                out[f"{d}|{pn}|{cal}"] = row
                L.append(f"| {d} | {pn} | {cal} | " + " | ".join(f"{row[s]:.3g}" for s in Q.SPREADS) + " |")
    (OUT / "pair_spread_nonlinear.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT / "pair_spread_nonlinear.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
