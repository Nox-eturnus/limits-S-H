"""Spread of the coherent logical error over single sign patterns.

The part of a pedestal deviation that mismatch adds has a sign that is random from channel to channel but fixed on
a given chip, so a chip realises one sign pattern; studies/mixed_sign.py gives the mean over patterns. Here, for a
purely random deviation (theta_b = sigma_b, sigma_b = +-1 per barrier), the ratio of the coherent to the Pauli
logical error at the same angles is computed, to leading order, for N_DRAW independent patterns per distance, with
its percentiles and the angle factor Q^(1 / 2t) that would restore the Pauli value.

Run:  python studies/sign_patterns.py     (a few minutes; writes results/sign_patterns.json)
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import mixed_sign as MS  # noqa: E402

CASES = ((3, 2), (3, 4), (5, 1), (5, 3), (7, 1))
N_DRAW = 2000

rows = []
rng = np.random.default_rng(15)
for d, rounds in CASES:
    group, barriers, nb, t = MS.fault_sets(d, rounds)
    q = []
    for _ in range(N_DRAW):
        coh, pau = MS.logical(group, barriers, rng.choice((-1.0, 1.0), nb))
        q.append(coh / pau)
    q = np.array(q)
    pc = {p: float(np.percentile(q, p)) for p in (5, 50, 95, 99)}
    row = {"d": d, "rounds": rounds, "t": t, "mean": float(q.mean()), "pct": pc, "max": float(q.max()),
           "angle_factor_95": pc[95] ** (1 / (2 * t)), "angle_factor_99": pc[99] ** (1 / (2 * t))}
    rows.append(row)
    print(d, rounds, {k: round(v, 3) for k, v in row.items() if isinstance(v, float)}, {k: round(v, 3) for k, v in pc.items()},
          flush=True)
(OUT / "sign_patterns.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
