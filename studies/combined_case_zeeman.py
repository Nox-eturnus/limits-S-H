"""The tolerated move of the combined worst case for a device with a Zeeman difference of 25 MHz.

studies/combined_case_fine_move.py gives the largest move from a tuned level for the bootstrapped switch with the
steepest band, twice the mismatch and the tree of a full reticle together, from a cubic spline through 20 channels
simulated every 20 mV. Here the same point estimate is recomputed with the 100 MHz budgets, as a check that it
reproduces, and with the budgets of a 25 MHz device: the 100 MHz budgets scaled by the ratios of
results/zeeman_equal_sign.json (part A, 33.69 dec/V, 99.99 %).

Run (after studies/zeeman_equal_sign.py):  python studies/combined_case_zeeman.py     (about 30 min; writes
                                            results/combined_case_zeeman.json)
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import combined_case_fine_move as M15  # noqa: E402
import cell_margins as CM  # noqa: E402


def main():
    z = json.loads((OUT / "zeeman_equal_sign.json").read_text(encoding="utf-8"))["D"]
    rec = json.loads((ROOT / "results" / "mc_cell_combined_fine_pedestals.json").read_text(encoding="utf-8"))[M15.KEY]
    x, v, std, _, _ = CM.prepare(rec)
    b100 = M15.B[M15.TARGETS["99.99"]]
    b25 = dict(b100, b_eq=b100["b_eq"] * z["ratio_b_eq"], b_ind=b100["b_ind"] * z["ratio_b_ind"])
    out = {"key": M15.KEY, "ratio_b_eq": z["ratio_b_eq"], "ratio_b_ind": z["ratio_b_ind"]}
    for name, b in (("100 MHz", b100), ("25 MHz", b25)):
        rng = np.random.default_rng(15)
        q = M15.curve(x, v, std, b, M15.N_POINT, rng, 75)
        out[name] = {"dmax_V": M15.dmax(q)}
        print(f"{name}: Delta_max {out[name]['dmax_V'] * 1e3:.1f} mV", flush=True)
    (OUT / "combined_case_zeeman.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
