"""The operational budget when frame tracking misses part of the droop.

Frame tracking removes the single-qubit phases predicted from the known offset of a channel. If the
droop of a channel is known only to a fraction, for example because its leakage drifts or switches,
a fraction f of the offset stays untracked and keeps its Stark phase. To first order in the offset,
the phases after tracking are the conditional part plus f times the local part:
    phase = P_cond phase + f (1 - P_cond) phase,
with f = 0 the frame-tracked budget and f = 1 the untracked one. The budget is given for M = 4
repeated gates (the operational budget) at 99.9 % and 99.99 %, without idle time and with 1 us of
idle time per gate layer.

Run:  python studies/partial_tracking.py     (about 1 min; writes results/partial_tracking.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
from flow import budget as B  # noqa: E402
from repeated_gates import _PROJ_COND  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
SLOPES = (3.87, 10.0, 33.69)
TARGETS = (1e-3, 1e-4)
FRACTIONS = (0.0, 0.03, 0.1, 0.3, 1.0)
IDLES = (0.0, 1e-6)
M = 4


def seq_infidelity(lay, dv, f):
    ph = lay.phase_errors(B.static(lay, dv))
    ph = _PROJ_COND @ ph + f * (ph - _PROJ_COND @ ph)
    return B.phase_infidelity(M * ph)


def budget(lay, target, f):
    best = np.inf
    for sign in (+1, -1):
        g = lambda x: seq_infidelity(lay, sign * x, f) - M * target  # noqa: E731
        xs = np.geomspace(1e-9, 0.2, 200)
        vals = np.array([g(x) for x in xs])
        i = np.nonzero(vals >= 0)[0]
        if i.size == 0:
            continue
        i = i[0]
        best = min(best, xs[0] if i == 0 else brentq(g, xs[i - 1], xs[i], xtol=xs[i - 1] * 1e-6))
    return float(best)


def main():
    rows = []
    for s in SLOPES:
        for idle in IDLES:
            lay = B.layer(s_dec_per_v=s, t_idle=idle)
            for tgt in TARGETS:
                r = {"s": s, "t_idle": idle, "target": tgt, "budget": {f"{f:g}": budget(lay, tgt, f) for f in FRACTIONS}}
                rows.append(r)
                print(f"s {s:g} idle {idle * 1e6:g} us {tgt:g}: " +
                      ", ".join(f"f {k}: {v * 1e3:.3g} mV" for k, v in r["budget"].items()), flush=True)
    (OUT / "partial_tracking.json").write_text(json.dumps({"M": M, "rows": rows}, indent=1), encoding="utf-8")
    L = [f"## Operational budget (M = {M}) with a fraction f of the offset untracked", "",
         "| s (dec/V) | idle per layer | target | " + " | ".join(f"f = {f:g}" for f in FRACTIONS) + " |",
         "|---|---|---|" + "---|" * len(FRACTIONS)]
    for r in rows:
        L.append(f"| {r['s']:g} | {r['t_idle'] * 1e6:g} µs | {r['target']:g} | " +
                 " | ".join(f"{v * 1e3:.3g} mV" for v in r["budget"].values()) + " |")
    (OUT / "partial_tracking.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
