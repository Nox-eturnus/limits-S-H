"""Operational static budget under error correction, shared by the studies that judge offsets against it.

A data qubit takes part in four CZ gates per surface-code round, but those gates use four different
barriers, and a given barrier enters one CZ per round, so their errors are different operators and do not
add coherently (studies/surface_code.py: with independent signs, coherent and Pauli-twirled errors give the
same logical error rate). Errors that act identically on the code space do interfere:
  - in a weight-2 boundary check the two ZZ errors Z_a Z_0 and Z_a Z_3 are the same operator on code
    states (Z_0 Z_3 is the stabiliser), so their angles add as for two repeated gates on one pair (M = 2);
    the one-round raw error rate of the simulation shows it (coherent / Pauli = 1.30-1.40, predicted 1.33);
  - in a weight-4 check, pairs of errors whose data parts differ by the stabiliser (Z_1 Z_2 and Z_3 Z_4)
    interfere at second order, doubling their probability.
With all offsets of the same sign (the worst case) the operational budget is therefore the frame-tracked
budget for M_QEC = 2 repeated gates (results/repeated_gates.json); with independent signs M = 1 applies.
"""
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M_QEC = 2                    # worst case: equivalent errors of a boundary check add as two repeated gates
HOOK = 1.0                   # kept as a hook for other accountings
POINTS = {"s33.69_t0.0001": (33.69, 1e-4), "s33.69_t0.001": (33.69, 1e-3),
          "s10_t0.001": (10.0, 1e-3), "s10_t0.0001": (10.0, 1e-4)}
WORST, REF = "s33.69_t0.0001", "s10_t0.001"


def budgets(m=M_QEC, hook=HOOK):
    """{point: {"per_gate": untracked single-gate budget, "operational": frame-tracked, M gates, times hook}} in V."""
    spec = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))["spec"]
    rg = json.loads((ROOT / "results" / "repeated_gates.json").read_text(encoding="utf-8"))
    out = {}
    for key, (s, t) in POINTS.items():
        row = next(r for r in rg["rows"] if r["s"] == s and r["target"] == t)
        out[key] = {"per_gate": spec[key], "operational": spec[key] * row["frame"][str(m)] / row["v1_exact"] * hook}
    return out


def operational_range():
    """Operational budget at every slope and target of results/repeated_gates.json (V)."""
    rg = json.loads((ROOT / "results" / "repeated_gates.json").read_text(encoding="utf-8"))
    return {(r["s"], r["target"]): r["frame"][str(M_QEC)] * HOOK for r in rg["rows"]}


_SEEDS = json.loads((ROOT / "results" / "sample_seeds.json").read_text(encoding="utf-8"))


def name_seed(name):
    """Random seed of the surrogate sampling of a "design|condition" record: the crc32 of its label. Records whose
    label was shortened after their results were computed keep the seed of that computation
    (results/sample_seeds.json), so that a rerun reproduces the stored results exactly."""
    return _SEEDS.get(name, zlib.crc32(name.encode()))
