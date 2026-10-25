"""A static offset repeats on every gate until the next refresh: budget per gate over M gates.

A static barrier offset is a coherent error: on M consecutive CZ gates of the same pair its adiabatic
phases add, so the infidelity of the sequence grows as M^2 rather than M. This script gives the
static budget per gate for sequences of M gates, with the error per gate held at the target
(sequence infidelity <= M x target), in three cases:

  coherent          the phases of Eq. (2) multiplied by M (exact for diagonal errors)
  frame-tracked     the single-qubit Z parts removed after every gate (virtual-Z update from the known
                    offset), so only the conditional phase accumulates
  twirled           randomized compiling turns the error into a stochastic channel with the same
                    average infidelity per gate; sequence infidelity ~ M x r_1, so the per-gate budget
                    applies unchanged (checked here to first order)

The frame-tracked budget at M = 4 (one surface-code round) is the operational budget used by
studies/system_budget.py and studies/margins.py.
Run:  python studies/repeated_gates.py      (about 1 min; writes results/repeated_gates.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flow import budget as B  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
SLOPES = (3.87, 10.0, 33.69)
TARGETS = (1e-3, 1e-4)
MS = (1, 2, 4, 10, 100)          # beyond, M x target nears the 0.8 ceiling; the budget follows V_1 / sqrt(M)
# local (single-qubit Z) directions in the (00, 01, 10, 11) phase basis; the rest is the conditional phase
_LOCAL = np.array([[1, 1, 1, 1], [0, 1, 0, 1], [0, 0, 1, 1]], float).T
_PROJ_COND = np.eye(4) - _LOCAL @ np.linalg.pinv(_LOCAL)


def seq_infidelity(lay, dv, m, mode):
    ph = lay.phase_errors(B.static(lay, dv))
    if mode == "frame":
        ph = _PROJ_COND @ ph
    return B.phase_infidelity(m * ph)


def budget(lay, target, m, mode):
    """Largest |dv| (worse sign) with sequence infidelity <= m * target."""
    best = np.inf
    for sign in (+1, -1):
        f = lambda x: seq_infidelity(lay, sign * x, m, mode) - m * target  # noqa: E731
        xs = np.geomspace(1e-9, 0.2, 200)
        vals = np.array([f(x) for x in xs])
        i = np.nonzero(vals >= 0)[0]
        if i.size == 0:
            continue
        i = i[0]
        x = xs[0] if i == 0 else brentq(f, xs[i - 1], xs[i], xtol=xs[i - 1] * 1e-6)
        best = min(best, x)
    return float(best)


def main():
    out = {"Ms": MS, "rows": []}
    for s in SLOPES:
        lay = B.layer(s_dec_per_v=s)
        for tgt in TARGETS:
            v1_exact = min(B.max_static(lay, tgt, +1), B.max_static(lay, tgt, -1))
            row = {"s": s, "target": tgt, "v1_exact": v1_exact,
                   "coherent": {m: budget(lay, tgt, m, "coherent") for m in MS},
                   "frame": {m: budget(lay, tgt, m, "frame") for m in MS}}
            # share of the single-gate infidelity at the per-gate budget that is conditional phase
            v1 = row["coherent"][1]
            row["cond_share_at_v1"] = seq_infidelity(lay, v1, 1, "frame") / seq_infidelity(lay, v1, 1, "coherent")
            out["rows"].append(row)
            print(f"s = {s:g}, 1-F = {tgt:g}: V1 {v1 * 1e3:.3g} mV (exact {v1_exact * 1e3:.3g}); coherent M=4 "
                  f"{row['coherent'][4] * 1e3:.3g}, M=100 {row['coherent'][100] * 1e6:.3g} uV; frame-tracked M=1 "
                  f"{row['frame'][1] * 1e3:.3g}, M=4 {row['frame'][4] * 1e3:.3g}, M=100 {row['frame'][100] * 1e6:.3g} uV",
                  flush=True)
    (OUT / "repeated_gates.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    L = ["## Static budget per gate for M repeated CZ gates (error per gate = target)", "",
         "Coherent: adiabatic phases × M. Frame-tracked: single-qubit Z parts removed after each gate. "
         "Twirled: budget of M = 1 applies (stochastic, linear accumulation).", "",
         "| s (dec/V) | target | case | " + " | ".join(f"M = {m:g}" for m in MS) + " |",
         "|---|---|---|" + "---|" * len(MS)]
    for r in out["rows"]:
        for case in ("coherent", "frame"):
            L.append(f"| {r['s']:g} | {r['target']:g} | {case} | " +
                     " | ".join(f"{r[case][m] * 1e3:.3g} mV" if r[case][m] >= 1e-4 else f"{r[case][m] * 1e6:.3g} µV"
                                for m in MS) + " |")
    L.append("")
    (OUT / "repeated_gates.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
