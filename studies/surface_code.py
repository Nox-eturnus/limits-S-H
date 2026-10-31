"""Does a static barrier offset accumulate coherently under error correction? State-vector simulation, d = 3.

A data qubit takes part in four CZ gates per surface-code round, but each of those gates uses a different
barrier, driven by its own channel with its own offset, and a given barrier enters one CZ per round. After
frame tracking the error of one gate is a ZZ rotation exp(-i theta Z_a Z_d) on that pair, with added
infidelity 0.8 sin^2(theta). This script tests directly whether such errors build up coherently.

Model: distance-3 rotated surface code (9 data qubits) with CZ-based syndrome extraction. One ancilla is
reused for the eight stabilisers of a round (X checks with Hadamards on the data, Z checks without), so
every (stabiliser, data qubit) pair is its own CZ with its own barrier and its own static offset, applied as
exp(-i theta_k Z_a Z_d) at that CZ in every round. The ancilla is measured and reset after each check
(outcomes sampled by the Born rule, trajectories vectorised). After R rounds a perfect final syndrome is
taken and corrected with a minimum-weight lookup decoder; the logical fidelity is computed exactly over all
256 syndrome sectors, so coherent residues count.

Compared at equal per-gate infidelity:
  coherent, same sign   theta_k = +theta for every pair (the worst case for constructive build-up)
  coherent, random sign theta_k = +-theta, fixed per pair over all rounds (independent channels)
  Pauli-twirled         Z_a Z_d applied with probability sin^2(theta) at every CZ
If the coherent errors were amplified over the four gates of a data qubit (M = 4), the physical error rate
would be up to 16 / 4 = 4 times the twirled one and the logical error rate up to 16 times.

Needs NumPy only.
Run:  python studies/surface_code.py           (about 1 h; writes results/surface_code.{json,md})
      python studies/surface_code.py refine    (more rounds at small angles; results/surface_code_refine.json)
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parents[1] / "results"
ND, NQ = 9, 10                     # data qubits 0..8 (3 x 3, row-major), ancilla 9
ANC = 9
X_STABS = [(0, 1, 3, 4), (4, 5, 7, 8), (1, 2), (6, 7)]
Z_STABS = [(1, 2, 4, 5), (3, 4, 6, 7), (0, 3), (5, 8)]
Z_LOGICAL, X_LOGICAL = (0, 1, 2), (0, 3, 6)
DIM = 1 << NQ
IDX = np.arange(DIM)
BITS = (IDX[:, None] >> np.arange(NQ)) & 1          # bit q of basis index (qubit q)
ZSIGN = 1 - 2 * BITS                                 # +1 / -1 eigenvalue of Z_q


def mask(qs):
    return sum(1 << q for q in qs)


def apply_h(psi, q):
    """Hadamard on qubit q for a batch of states (rows)."""
    m = 1 << q
    lo = (IDX & m) == 0
    a, b = psi[:, IDX[lo]], psi[:, IDX[lo] | m]
    out = np.empty_like(psi)
    out[:, IDX[lo]] = (a + b) / np.sqrt(2)
    out[:, IDX[lo] | m] = (a - b) / np.sqrt(2)
    return out


def cz_phase(a, d):
    return np.where(BITS[:, a] & BITS[:, d], -1.0, 1.0)


def zz_phase(a, d, theta):
    return np.exp(-1j * theta * ZSIGN[:, a] * ZSIGN[:, d])


def measure_reset(psi, rng):
    """Measure the ancilla in Z, collapse, reset it to |0>."""
    one = BITS[:, ANC] == 1
    p1 = np.sum(np.abs(psi[:, one]) ** 2, axis=1)
    out = rng.random(len(psi)) < p1
    psi = psi.copy()
    psi[np.ix_(out, ~one)] = 0
    psi[np.ix_(~out, one)] = 0
    psi /= np.linalg.norm(psi, axis=1, keepdims=True)
    flip = IDX ^ (1 << ANC)                              # reset: X on the ancilla where it read 1
    psi[out] = psi[out][:, flip]
    return psi


def check(psi, stab, kind, thetas, mode, p, rng):
    """One stabiliser measurement through CZ gates, with the static error of each CZ."""
    psi = apply_h(psi, ANC)
    for d in stab:
        if kind == "X":
            psi = apply_h(psi, d)
        psi = psi * cz_phase(ANC, d)
        th = thetas[(kind, stab, d)]
        if mode == "pauli":
            hit = rng.random(len(psi)) < p
            psi[hit] = psi[hit] * (ZSIGN[:, ANC] * ZSIGN[:, d])
        else:
            psi = psi * zz_phase(ANC, d, th)
        if kind == "X":
            psi = apply_h(psi, d)
    psi = apply_h(psi, ANC)
    return measure_reset(psi, rng)


def stab_op(psi, stab, kind):
    """S psi for a batch, S an X or Z string on data qubits (ancilla in |0>)."""
    if kind == "Z":
        return psi * np.prod(ZSIGN[:, list(stab)], axis=1)
    return psi[:, IDX ^ mask(stab)]


def project_code(psi):
    for kind, stabs in (("X", X_STABS), ("Z", Z_STABS)):
        for s in stabs:
            psi = (psi + stab_op(psi, s, kind)) / 2
    return psi / np.linalg.norm(psi, axis=1, keepdims=True)


def logical_states():
    zero = np.zeros((1, DIM), complex)
    zero[0, 0] = 1
    plus = zero.copy()
    for q in range(ND):
        plus = apply_h(plus, q)
    return {"0": project_code(zero)[0], "+": project_code(plus)[0]}


def syndrome(err, stabs):
    """Syndrome of a Pauli-error support (set of qubits) against stabilisers of the other type."""
    return tuple(len(set(err) & set(s)) % 2 for s in stabs)


def lookup(stabs):
    """Minimum-weight correction (support) for every syndrome of the given stabilisers."""
    table = {}
    for w in range(ND + 1):
        for sup in itertools.combinations(range(ND), w):
            table.setdefault(syndrome(sup, stabs), sup)
    return table


ZCORR, XCORR = lookup(X_STABS), lookup(Z_STABS)      # Z errors flip X checks; X errors flip Z checks


def decoded_basis(psi_l):
    """Columns C_s^dagger |psi_L> for all 256 syndrome sectors s (Z correction for the X syndrome,
    X correction for the Z syndrome): the fidelity after perfect syndrome measurement and lookup
    correction is sum_s |<C_s^dagger psi_L | psi>|^2."""
    cols = []
    for zc in ZCORR.values():
        for xc in XCORR.values():
            v = psi_l[None, :]
            v = v[:, IDX ^ mask(xc)] if xc else v                       # X correction (self-inverse)
            v = v * np.prod(ZSIGN[:, list(zc)], axis=1) if zc else v    # Z correction
            cols.append(v[0])
    return np.array(cols).T


def run(theta, mode, rounds, n_traj, state, seed):
    rng = np.random.default_rng(seed)
    pairs = [(k, s, d) for k, stabs in (("X", X_STABS), ("Z", Z_STABS)) for s in stabs for d in s]
    sign = rng.choice([-1.0, 1.0], len(pairs)) if mode == "random" else np.ones(len(pairs))
    thetas = {pr: theta * sg for pr, sg in zip(pairs, sign)}
    p = np.sin(theta) ** 2
    psi_l = LOGICAL[state]
    psi = np.repeat(psi_l[None, :], n_traj, axis=0)
    basis = decoded_basis(psi_l)
    out = {}
    for r in range(1, max(rounds) + 1):
        for kind, stabs in (("X", X_STABS), ("Z", Z_STABS)):
            for s in stabs:
                psi = check(psi, s, kind, thetas, mode, p, rng)
        if r in rounds:
            raw = np.abs(psi @ psi_l.conj()) ** 2                          # before decoding
            dec = np.sum(np.abs(psi @ basis.conj()) ** 2, axis=1)            # after perfect decoding
            out[r] = {"raw_infid": float(1 - raw.mean()), "raw_se": float(raw.std() / np.sqrt(n_traj)),
                      "logical_infid": float(1 - dec.mean()), "logical_se": float(dec.std() / np.sqrt(n_traj))}
    return out


LOGICAL = logical_states()


def main():
    rounds = (1, 2, 4)
    r_gate = (5e-3, 1e-2, 2e-2, 4e-2)                 # added CZ infidelity 0.8 sin^2(theta), exaggerated
    n_traj = 4000
    res = {"rounds": rounds, "n_traj": n_traj, "rows": []}
    for rg in r_gate:
        theta = float(np.arcsin(np.sqrt(rg / 0.8)))
        for state in ("0", "+"):
            row = {"r_gate": rg, "theta": theta, "p_pauli": float(np.sin(theta) ** 2), "state": state}
            for mode in ("same", "random", "pauli"):
                row[mode] = run(theta, mode, rounds, n_traj, state,
                                 seed=int(rg * 1e6) + 7 * "0+".index(state) + 13 * ("same", "random", "pauli").index(mode))
            res["rows"].append(row)
            r4 = {m: row[m][4] for m in ("same", "random", "pauli")}
            print(f"r = {rg:g}, |{state}_L>: 4 rounds raw " + ", ".join(f"{m} {v['raw_infid']:.4g}" for m, v in r4.items())
                  + "; logical " + ", ".join(f"{m} {v['logical_infid']:.3g}+-{v['logical_se']:.1g}" for m, v in r4.items()),
                  flush=True)
    (OUT / "surface_code.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    L = ["## Static ZZ errors in a distance-3 surface code: coherent against Pauli-twirled", "",
         f"{n_traj} trajectories per entry; CZ-based syndrome extraction, 24 CZ gates per round, each its own barrier. "
         "Raw: 1 - |<psi_L|psi>|^2 before decoding. Logical: after perfect final syndrome and lookup decoding. "
         "Ratio = coherent (same sign) / Pauli-twirled.", "",
         "| r per gate | state | rounds | raw: same / random / Pauli | ratio raw | logical: same / random / Pauli | ratio logical |",
         "|---|---|---|---|---|---|---|"]
    for row in res["rows"]:
        for r in rounds:
            a, b, c = (row[m][str(r)] if isinstance(next(iter(row[m])), str) else row[m][r] for m in ("same", "random", "pauli"))
            L.append(f"| {row['r_gate']:g} | {row['state']} | {r} | {a['raw_infid']:.4g} / {b['raw_infid']:.4g} / {c['raw_infid']:.4g} | "
                     f"{a['raw_infid'] / c['raw_infid']:.3f} | {a['logical_infid']:.3g} / {b['logical_infid']:.3g} / "
                     f"{c['logical_infid']:.3g} (±{c['logical_se']:.1g}) | {a['logical_infid'] / max(c['logical_infid'], 1e-12):.2f} |")
    (OUT / "surface_code.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__" and "refine" not in sys.argv:
    main()


def refine():
    """Small-error limit of the coherent / twirled ratio: more trajectories at the two smallest error
    rates, two rounds, and four independent sign patterns for the random-sign case."""
    n_traj, rounds = 8000, (1, 2)
    res = {"n_traj": n_traj, "rows": []}
    for rg in (2.5e-3, 5e-3):
        theta = float(np.arcsin(np.sqrt(rg / 0.8)))
        for state in ("0", "+"):
            row = {"r_gate": rg, "state": state,
                   "same": run(theta, "same", rounds, n_traj, state, seed=101),
                   "pauli": run(theta, "pauli", rounds, n_traj, state, seed=102),
                   "random": [run(theta, "random", rounds, n_traj, state, seed=200 + k) for k in range(4)]}
            res["rows"].append(row)
            a, c = row["same"][2], row["pauli"][2]
            rnd = np.mean([x[2]["logical_infid"] for x in row["random"]])
            print(f"refine r = {rg:g} |{state}_L>: logical same {a['logical_infid']:.3g}+-{a['logical_se']:.1g}, "
                  f"pauli {c['logical_infid']:.3g}+-{c['logical_se']:.1g}, random (4 patterns) {rnd:.3g}", flush=True)
    (OUT / "surface_code_refine.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__" and "refine" in sys.argv:
    refine()
