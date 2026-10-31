"""How the coherent excess of static ZZ errors depends on the code distance, to leading order in the angle.

studies/surface_code.py simulates the distance-3 code with full state vectors at per-gate infidelities of
0.0025 to 0.02. This script computes the logical error rate of the same circuit to leading order in the
rotation angle, which is exact in the small-angle limit of interest, for distances 3, 5 and 7.

Circuit (as surface_code.py): rotated surface code, one reused ancilla, X checks then Z checks in every
round, each check a CZ per data qubit with Hadamards on the data for X checks, and after each CZ the static
error exp(-i theta Z_a Z_d) of its barrier. Ancilla measured and reset after every check; after R rounds a
perfect syndrome is taken and corrected by a minimum-weight lookup decoder.

Leading order. A fault Z_a Z_d inside an X check leaves X_d on the data and flips the outcome of its own
check; X_d then flips every later Z check that contains d. A fault inside a Z check leaves Z_d, flips its
own check and every X check of later rounds that contains d. No fault produces a hook error or a phase:
every term of the expansion is an X (or Z) string times (-i sin theta)^(number of faults). For the
logical state |0_L> only X strings matter, and the lowest-order failures are sets of t = (d + 1) / 2
faults on distinct data qubits whose X string the decoder maps onto X_L. Two fault sets interfere when
they leave the same measurement record and the same final X string up to X stabilisers (same final
syndrome and same logical parity). With all offsets of equal sign, the amplitudes in such a group add,
so to leading order

    P_coherent / P_Pauli = sum_g n_g^2 / sum_g n_g,

with n_g the number of failing fault sets in group g; with independent signs the ratio averages to one.
The record and the coset are linear in the faults, so each fault gets a 64-bit XOR hash and a fault set
the XOR of its faults' hashes (collision probability about 2^-64 per pair).

An equivalent physical factor follows from P_logical ~ p^t: the coherent case behaves as Pauli errors of
rate Q^(1/t) p, which the operational budget for M repeated gates covers when M >= Q^(1/t).

Run:  python studies/surface_code_distance.py      (about 5 min; writes results/surface_code_distance.{json,md})
"""
import itertools
import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parents[1] / "results"
ROUNDS = {3: (1, 2, 3, 4, 6), 5: (1, 2, 3, 5), 7: (1, 2, 3)}


def code(d):
    """Stabilisers (tuples of data qubits, row-major d x d) and logical supports, as in surface_code.py
    for d = 3."""
    q = lambda r, c: r * d + c  # noqa: E731
    xs, zs = [], []
    for r in range(d - 1):
        for c in range(d - 1):
            (xs if (r + c) % 2 == 0 else zs).append((q(r, c), q(r, c + 1), q(r + 1, c), q(r + 1, c + 1)))
    for c in range(d - 1):
        if c % 2 == 1:
            xs.append((q(0, c), q(0, c + 1)))               # top edge
        if c % 2 == 0:
            xs.append((q(d - 1, c), q(d - 1, c + 1)))       # bottom edge
    for r in range(d - 1):
        if r % 2 == 0:
            zs.append((q(r, 0), q(r + 1, 0)))               # left edge
        if r % 2 == 1:
            zs.append((q(r, d - 1), q(r + 1, d - 1)))       # right edge
    z_logical = tuple(q(0, c) for c in range(d))            # top row
    x_logical = tuple(q(r, 0) for r in range(d))            # left column
    return xs, zs, z_logical, x_logical


def lookup(n, checks, wmax):
    """First minimum-weight support for every syndrome reachable with weight <= wmax (the order of
    surface_code.lookup)."""
    table = {}
    for w in range(wmax + 1):
        for sup in itertools.combinations(range(n), w):
            s = tuple(len(set(sup) & set(c)) % 2 for c in checks)
            table.setdefault(s, sup)
    return table


def ratio(d, rounds, basis):
    """Leading-order coherent / Pauli logical-error ratio for |0_L> (basis 'Z': X errors from X checks)
    or |+_L> (basis 'X': Z errors from Z checks)."""
    xs, zs, zl, xl = code(d)
    n, t = d * d, (d + 1) // 2
    src, det, logical = (xs, zs, zl) if basis == "Z" else (zs, xs, xl)
    # record bits: own-check flips (round, source check) and detecting-check parities (round, check)
    rng = np.random.default_rng(d * 100 + rounds)
    h_own = rng.integers(0, 2 ** 63, (rounds, len(src)), dtype=np.int64)
    h_det = rng.integers(0, 2 ** 63, (rounds, len(det)), dtype=np.int64)
    h_fin = rng.integers(0, 2 ** 63, len(det), dtype=np.int64)       # final perfect syndrome
    h_log = np.int64(rng.integers(0, 2 ** 63))
    # in a round X checks come first: an X-check fault of round r is seen by the Z checks of rounds >= r,
    # a Z-check fault of round r by the X checks of rounds > r
    first = 0 if basis == "Z" else 1
    loc = {}                                              # data qubit -> hashes of its fault locations
    for qb in range(n):
        hs = []
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
        loc[qb] = np.array(hs, dtype=np.int64)
    table = lookup(n, det, t)
    groups, n_sets = {}, 0
    for pat in itertools.combinations(range(n), t):
        s = tuple(len(set(pat) & set(c)) % 2 for c in det)
        corr = table[s]
        resid = set(pat) ^ set(corr)
        if len(resid & set(logical)) % 2 == 0:            # decoded to a stabiliser: success
            continue
        acc = np.zeros(1, dtype=np.int64)
        for qb in pat:
            acc = (acc[:, None] ^ loc[qb][None, :]).ravel()
        u, c = np.unique(acc, return_counts=True)
        for key, cnt in zip(u.tolist(), c.tolist()):
            groups[key] = groups.get(key, 0) + cnt
        n_sets += len(acc)
    counts = np.array(list(groups.values()), dtype=float)
    q = float((counts ** 2).sum() / counts.sum())
    return {"d": d, "rounds": rounds, "basis": basis, "t": t, "failing_sets": n_sets,
            "groups": len(counts), "ratio": q, "equivalent_physical_factor": q ** (1 / t)}


def main():
    rows = []
    for d, rr in ROUNDS.items():
        for rounds in rr:
            for basis in ("Z", "X"):
                r = ratio(d, rounds, basis)
                rows.append(r)
                print(f"d = {d}, R = {rounds}, |{'0' if basis == 'Z' else '+'}_L>: ratio {r['ratio']:.3f}, "
                      f"physical factor {r['equivalent_physical_factor']:.3f} ({r['failing_sets']} sets)", flush=True)
    (OUT / "surface_code_distance.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    L = ["## Coherent / Pauli logical error to leading order in theta, equal signs", "",
         "Ratio Q = sum n_g^2 / sum n_g over interfering groups of failing fault sets; equivalent physical factor "
         "Q^(1/t), t = (d + 1) / 2: the operational budget for M repeated gates covers it when M >= Q^(1/t).", "",
         "| d | rounds | state | t | failing fault sets | ratio Q | equivalent physical factor |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['d']} | {r['rounds']} | {'0' if r['basis'] == 'Z' else '+'} | {r['t']} | {r['failing_sets']} | "
                 f"{r['ratio']:.3f} | {r['equivalent_physical_factor']:.3f} |")
    (OUT / "surface_code_distance.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
