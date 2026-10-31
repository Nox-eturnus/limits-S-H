"""The operational budget under error correction when frame tracking misses part of the droop.

The conditional phase of a barrier offset is counted as for M_QEC = 2 repeated gates in the worst case
(studies/operational_budget.py). The single-qubit part is different: if a fraction f of the offset stays
untracked, each of the four barriers next to a data qubit leaves a Z rotation on that qubit, and these four
rotations are the same operator, so in the worst case (equal signs) their angles add within a round before
the X-stabiliser measurement projects them. Per gate, the error is therefore
    phase = sqrt(M_QEC) P_cond phase + 2 f (1 - P_cond) phase,  1 - F(phase) <= target.
f = 0 gives the operational budget; f = 1 the operational budget without frame tracking (the equal-sign
budget b_eq of the worst-channel margins). studies/partial_tracking.py gives the same for M = 4 without
the error-correction accounting.

Run:  python studies/partial_tracking_qec.py      (about 2 min; writes results/partial_tracking_qec.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
from flow import budget as B  # noqa: E402
from repeated_gates import _PROJ_COND  # noqa: E402

SLOPES = (3.87, 10.0, 33.69)
TARGETS = (1e-3, 1e-4)
FRACTIONS = (0.0, 0.03, 0.1, 0.3, 1.0)
IDLES = (0.0, 1e-6)
N_LOCAL = 4                    # barriers next to one data qubit


def infid(lay, dv, f):
    """Error per gate: the conditional part as for M_QEC coherent repetitions (amplitude x sqrt(M), the
    infidelity of M gates shared over M), plus the untracked local part added over N_LOCAL barriers."""
    ph = lay.phase_errors(B.static(lay, dv))
    cond = _PROJ_COND @ ph
    return B.phase_infidelity(np.sqrt(common.M_QEC) * cond + np.sqrt(N_LOCAL) * f * (ph - cond))


def budget(lay, target, f):
    best = np.inf
    for sign in (+1, -1):
        g = lambda x: infid(lay, sign * x, f) - target  # noqa: E731
        xs = np.geomspace(1e-9, 0.2, 200)
        vals = np.array([g(x) for x in xs])
        i = np.nonzero(vals >= 0)[0]
        if i.size == 0:
            continue
        i = i[0]
        best = min(best, xs[0] if i == 0 else brentq(g, xs[i - 1], xs[i], xtol=xs[i - 1] * 1e-6))
    return float(best) * common.HOOK


def main():
    rows = []
    for s in SLOPES:
        for idle in IDLES:
            lay = B.layer(s_dec_per_v=s, t_idle=idle)
            for tgt in TARGETS:
                rows.append({"s": s, "t_idle": idle, "target": tgt,
                             "budget": {f"{f:g}": budget(lay, tgt, f) for f in FRACTIONS}})
    (OUT / "partial_tracking_qec.json").write_text(json.dumps({"hook": common.HOOK, "rows": rows}, indent=1), encoding="utf-8")
    L = ["## Operational budget with a fraction f of the offset untracked (error-correction accounting)", "",
         "| s (dec/V) | idle per layer | target | " + " | ".join(f"f = {f:g}" for f in FRACTIONS) + " |",
         "|---|---|---|" + "---|" * len(FRACTIONS)]
    for r in rows:
        L.append(f"| {r['s']:g} | {r['t_idle'] * 1e6:g} µs | {r['target']:g} | " +
                 " | ".join(f"{v * 1e3:.3g} mV" for v in r["budget"].values()) + " |")
    (OUT / "partial_tracking_qec.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
