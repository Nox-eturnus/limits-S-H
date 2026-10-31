"""Coherent excess of equal-sign static ZZ errors for a parallel syndrome schedule.

studies/surface_code_distance.py measures the checks one after another through one reused ancilla. Here every
stabiliser has its own ancilla and all checks of a round run in four CZ layers, in the usual orders of the rotated
code (X checks NW, NE, SW, SE; Z checks NW, SW, NE, SE; boundary checks use their two positions). A fault after the CZ
of check c with data qubit q in layer l of round r flips check c in round r, the checks of the other type that contain
q and meet it in a later layer of the same round, every such check in later rounds, and the final syndrome. As in the
sequential case no fault spreads from an ancilla (Z_a commutes with the remaining CZ gates), so the leading-order
ratio is Q = sum_g n_g^2 / sum_g n_g over groups of failing fault sets with the same record and logical coset.

Echo pulses on the data qubits between rounds conjugate later ZZ errors into ZZ errors of the opposite sign. A sign
pattern only changes the relative signs of the amplitudes that are added within a group, so |sum of signed
amplitudes|^2 <= (sum of amplitudes)^2 and Q with echoes never exceeds Q for equal signs without them; the script
checks this with one echo per round (the sign of every fault alternates with the round).

Run:  python studies/surface_code_parallel.py      (a few minutes; writes results/surface_code_parallel.{json,md})
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

ROUNDS = {3: (1, 2, 4), 5: (1, 3), 7: (1, 2)}
ORDER = {"X": ("NW", "NE", "SW", "SE"), "Z": ("NW", "SW", "NE", "SE")}


def positions(d, check, kind):
    """Position (NW, NE, SW, SE) of each data qubit of a check, relative to its plaquette."""
    rc = [divmod(q, d) for q in check]
    if len(check) == 4:
        r0, c0 = min(r for r, _ in rc), min(c for _, c in rc)
    else:
        (ra, ca), (rb, cb) = rc
        if ra == rb:            # horizontal pair: top edge (plaquette above) or bottom edge (plaquette below)
            r0, c0 = (ra - 1, min(ca, cb)) if ra == 0 else (ra, min(ca, cb))
        else:                   # vertical pair: left edge (plaquette to the left) or right edge
            r0, c0 = (min(ra, rb), ca - 1) if ca == 0 else (min(ra, rb), ca)
    out = {}
    for q, (r, c) in zip(check, rc):
        out[q] = ("N" if r == r0 else "S") + ("W" if c == c0 else "E")
    return {q: ORDER[kind].index(p) for q, p in out.items()}


def ratio(d, rounds, basis, echo=False):
    xs, zs, zl, xl = SCD.code(d)
    n, t = d * d, (d + 1) // 2
    src, det, logical = (xs, zs, zl) if basis == "Z" else (zs, xs, xl)
    sk, dk = ("X", "Z") if basis == "Z" else ("Z", "X")
    lay_src = [positions(d, c, sk) for c in src]
    lay_det = [positions(d, c, dk) for c in det]
    rng = np.random.default_rng(d * 1000 + rounds)
    h_own = rng.integers(0, 2 ** 63, (rounds, len(src)), dtype=np.int64)
    h_det = rng.integers(0, 2 ** 63, (rounds, len(det)), dtype=np.int64)
    h_fin = rng.integers(0, 2 ** 63, len(det), dtype=np.int64)
    h_log = np.int64(rng.integers(0, 2 ** 63))
    loc, sgn = {}, {}
    for qb in range(n):
        hs, ss = [], []
        for r in range(rounds):
            for ci, c in enumerate(src):
                if qb not in c:
                    continue
                ell = lay_src[ci][qb]
                h = h_own[r, ci]
                for di, dc in enumerate(det):
                    if qb not in dc:
                        continue
                    for r2 in range(r, rounds):
                        if r2 > r or lay_det[di][qb] > ell:
                            h ^= h_det[r2, di]
                    h ^= h_fin[di]
                if qb in logical:
                    h ^= h_log
                hs.append(h)
                ss.append(-1 if (echo and r % 2) else 1)
        loc[qb], sgn[qb] = np.array(hs, dtype=np.int64), np.array(ss)
    table = SCD.lookup(n, det, t)
    groups, n_sets = {}, 0
    for pat in itertools.combinations(range(n), t):
        s = tuple(len(set(pat) & set(c)) % 2 for c in det)
        resid = set(pat) ^ set(table[s])
        if len(resid & set(logical)) % 2 == 0:
            continue
        acc, sg = np.zeros(1, dtype=np.int64), np.ones(1)
        for qb in pat:
            acc = (acc[:, None] ^ loc[qb][None, :]).ravel()
            sg = (sg[:, None] * sgn[qb][None, :]).ravel()
        order = np.argsort(acc)
        acc, sg = acc[order], sg[order]
        u, idx = np.unique(acc, return_index=True)
        sums = np.add.reduceat(sg, idx)
        cnts = np.diff(np.append(idx, len(acc)))
        for key, a, c in zip(u.tolist(), sums.tolist(), cnts.tolist()):
            g = groups.setdefault(key, [0.0, 0])
            g[0] += a
            g[1] += c
        n_sets += len(acc)
    amp = np.array([g[0] for g in groups.values()])
    q = float((amp ** 2).sum() / n_sets)
    return {"d": d, "rounds": rounds, "basis": basis, "echo": echo, "t": t, "failing_sets": n_sets, "ratio": q,
            "equivalent_physical_factor": q ** (1 / t)}


def main():
    rows = []
    for d, rr in ROUNDS.items():
        for rounds in rr:
            for echo in (False, True):
                r = ratio(d, rounds, "Z", echo)
                rows.append(r)
                print(f"d {d} R {rounds} echo {echo}: Q {r['ratio']:.3f}, factor {r['equivalent_physical_factor']:.3f} "
                      f"({r['failing_sets']} sets)", flush=True)
    seq = json.loads((ROOT / "results" / "surface_code_distance.json").read_text(encoding="utf-8"))
    (OUT / "surface_code_parallel.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    L = ["## Coherent excess, parallel schedule (one ancilla per check, four CZ layers), |0_L>, leading order", "",
         "| d | rounds | sequential Q | parallel Q, equal signs | parallel Q, one echo per round | factor Q^(1/t), parallel |",
         "|---|---|---|---|---|---|"]
    for d, rr in ROUNDS.items():
        for rounds in rr:
            a = [r for r in rows if r["d"] == d and r["rounds"] == rounds and not r["echo"]][0]
            b = [r for r in rows if r["d"] == d and r["rounds"] == rounds and r["echo"]][0]
            s = [r for r in seq if r["d"] == d and r["rounds"] == rounds and r["basis"] == "Z"]
            L.append(f"| {d} | {rounds} | {s[0]['ratio']:.2f} | {a['ratio']:.2f} | {b['ratio']:.2f} | "
                     f"{a['equivalent_physical_factor']:.2f} |" if s else
                     f"| {d} | {rounds} | – | {a['ratio']:.2f} | {b['ratio']:.2f} | {a['equivalent_physical_factor']:.2f} |")
    (OUT / "surface_code_parallel.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
