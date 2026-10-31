"""Scaled-sigma runs of the 1 um TG at 300 K and in the 4 K band with the larger threshold shift ("4 K high").

These are the two conditions outside the 4 K band where its surrogate margin lies closest to one. As
studies/mc_cell_extra.py sss: one-cell-per-channel decks (studies/mc_cell.py), 20 channels per mismatch scale
(1.5, 2, 2.5 and 3).

Run:  python studies/mc_cell_tg.py sss
      python studies/mc_cell_tg.py        (collect only)
Appends to results/mc_cell_tg_channels.jsonl; collect writes results/mc_cell_tg_pedestals.json.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import mc_cell as M  # noqa: E402

M.LOG = OUT / "mc_cell_tg_channels.jsonl"
M.PEDS = OUT / "mc_cell_tg_pedestals.json"
M.WORK = ROOT / "build" / "mc_cell_tg"
M.THREADS = 28

TG = "TG, no ESD"
SCALES = (1.5, 2.0, 2.5, 3.0)
BASES = {"300 K": (0.0, 1.0), "4 K high": M.R.BANDS["4 K high"]}

_conditions = M.conditions


def conditions():
    c = _conditions()
    for band, cryo in BASES.items():
        for s in SCALES:
            c[f"{band}, mismatch x {s:g}"] = dict(cryo=tuple(cryo[:2]) + (s,), mm=s)
    return c


M.conditions = conditions


def sets():
    return {"sss": [(TG, f"{band}, mismatch x {s:g}", 20, False) for band in BASES for s in SCALES]}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "sss":
        M.sets = sets
        M.simulate(["sss"])
    M.collect()
