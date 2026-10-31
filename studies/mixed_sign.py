"""Does the combined error measure of the switch margins bound the logical error for mixed offsets?

The margins (studies/residual_accounting.py, studies/cell_margins.py) judge a channel whose deviation from its
calibration line is c + d (c common to all channels, d of random sign) by
    u = sqrt(((c + d) / b_ind)^2 + c^2 (1 / b_eq^2 - 1 / b_ind^2)),
where b_ind is the budget for independent signs and b_eq that for equal signs. In units of the conditional
phase angle (theta_ind = 1 at b_ind) and with b_eq = b_ind / sqrt(2) (two repeated gates; the four-barrier
Stark term of b_eq acts on single qubits and is not part of this code-level test), u^2 = (c + d)^2 + c^2.

Here the leading-order calculation of studies/surface_code_distance.py is repeated with an angle per barrier,
theta_b = c + m sigma_b with sigma_b = +-1 drawn independently for every barrier (the CZ of one check and one
data qubit, the same in every round). For each ratio c / m the expected coherent logical error over 400 draws
of the signs is compared with
  - the Pauli logical error at the angle u_max = sqrt((|c| + m)^2 + c^2) on every barrier, which is what a
    margin of one on the worst channel allows: the measure bounds the logical error if this ratio is at most one;
  - the Pauli logical error with the same angles theta_b (the coherent excess for these mixed angles).

Run:  python studies/mixed_sign.py     (a few minutes; writes results/mixed_sign.{json,md})
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import surface_code_distance as SCD  # noqa: E402

CASES = ((3, 2), (3, 4), (5, 1), (5, 3))
RATIOS = (0.0, 0.25, 0.5, 1.0, 2.0, 4.0, None)       # c / m; None = m = 0 (common part only)
N_DRAW = 400


def fault_sets(d, rounds, basis="Z"):
    """Failing fault sets to leading order: (group key, barrier ids of the t faults) for every set."""
    xs, zs, zl, xl = SCD.code(d)
    n, t = d * d, (d + 1) // 2
    src, det, logical = (xs, zs, zl) if basis == "Z" else (zs, xs, xl)
    rng = np.random.default_rng(d * 100 + rounds)
    h_own = rng.integers(0, 2 ** 63, (rounds, len(src)), dtype=np.int64)
    h_det = rng.integers(0, 2 ** 63, (rounds, len(det)), dtype=np.int64)
    h_fin = rng.integers(0, 2 ** 63, len(det), dtype=np.int64)
    h_log = np.int64(rng.integers(0, 2 ** 63))
    first = 0 if basis == "Z" else 1
    bid = {}
    loc = {}
    for qb in range(n):
        hs, bs = [], []
        for r in range(rounds):
            for ci, c in enumerate(src):
                if qb not in c:
                    continue
                h = h_own[r, ci]
                for r2 in range(r + first, rounds):
                    for di, dc in enumerate(det):
                        if qb in dc:
                            h ^= h_det[r2, di]
                for di, dc in enumerate(det):
                    if qb in dc:
                        h ^= h_fin[di]
                if qb in logical:
                    h ^= h_log
                hs.append(h)
                bs.append(bid.setdefault((ci, qb), len(bid)))
        loc[qb] = (np.array(hs, dtype=np.int64), np.array(bs))
    table = SCD.lookup(n, det, t)
    keys, barriers = [], []
    for pat in itertools.combinations(range(n), t):
        s = tuple(len(set(pat) & set(c)) % 2 for c in det)
        resid = set(pat) ^ set(table[s])
        if len(resid & set(logical)) % 2 == 0:
            continue
        hs = [loc[q][0] for q in pat]
        bs = [loc[q][1] for q in pat]
        for combo in itertools.product(*[range(len(h)) for h in hs]):
            k = np.int64(0)
            for h, i in zip(hs, combo):
                k ^= h[i]
            keys.append(int(k))
            barriers.append([b[i] for b, i in zip(bs, combo)])
    _, group = np.unique(np.array(keys), return_inverse=True)
    return group, np.array(barriers), len(bid), t


def logical(group, barriers, theta):
    amp = np.prod(theta[barriers], axis=1)
    coh = np.bincount(group, weights=amp)
    return float((coh ** 2).sum()), float((amp ** 2).sum())


def main():
    rng = np.random.default_rng(6)
    rows = []
    for d, rounds in CASES:
        group, barriers, nb, t = fault_sets(d, rounds)
        n_sets = len(barriers)
        for rho in RATIOS:
            c, m = (1.0, 0.0) if rho is None else (rho, 1.0)
            u_max = np.sqrt((abs(c) + m) ** 2 + c ** 2)
            coh, pau = [], []
            for _ in range(N_DRAW if m else 1):
                theta = c + m * rng.choice((-1.0, 1.0), nb)
                a, b = logical(group, barriers, theta)
                coh.append(a)
                pau.append(b)
            p_bound = n_sets * u_max ** (2 * t)
            rows.append({"d": d, "rounds": rounds, "t": t, "c_over_m": rho, "fault_sets": n_sets,
                         "coherent_over_bound": float(np.mean(coh) / p_bound),
                         "coherent_over_bound_max_draw": float(np.max(coh) / p_bound),
                         "coherent_over_same_angle_pauli": float(np.mean(coh) / np.mean(pau)),
                         "bound_equivalent_physical_factor": float((np.mean(coh) / p_bound) ** (1 / t))})
            r = rows[-1]
            print(f"d {d} R {rounds} c/m {('inf' if rho is None else rho)!s:5s}: coherent / bound {r['coherent_over_bound']:.3f} "
                  f"(max draw {r['coherent_over_bound_max_draw']:.3f}), coherent / same-angle Pauli "
                  f"{r['coherent_over_same_angle_pauli']:.3f}", flush=True)
    (OUT / "mixed_sign.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    L = ["## Combined error measure against the leading-order logical error, mixed common and random parts", "",
         "theta_b = c + m sigma_b per barrier; bound: Pauli at u_max = sqrt((|c| + m)^2 + c^2) on every barrier. "
         "A ratio coherent / bound at or below one means the measure is conservative.", "",
         "| d | rounds | c / m | coherent / bound (mean over sign draws) | worst draw | coherent / Pauli at the same angles |",
         "|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['d']} | {r['rounds']} | {'∞' if r['c_over_m'] is None else r['c_over_m']} | "
                 f"{r['coherent_over_bound']:.3f} | {r['coherent_over_bound_max_draw']:.3f} | {r['coherent_over_same_angle_pauli']:.3f} |")
    (OUT / "mixed_sign.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
