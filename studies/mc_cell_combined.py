"""One combined worst case: the steepest band, twice the mismatch and the tree source of a full reticle together.

The sensitivity variants of the 4 K band are otherwise applied one at a time. Here the steepest subthreshold band
(T_eff = 20 K), twice the mismatch and the tree source of a full reticle act together, for the six designs of Figure 6,
20 channels each, one cell per channel (as studies/mc_cell.py).

Run:  python studies/mc_cell_combined.py combined      (about 85 min on 28 threads; needs ngspice and the PDK)
      python studies/mc_cell_combined.py collect       (writes results/mc_cell_combined_pedestals.json)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import mc_cell as M  # noqa: E402

M.LOG = OUT / "mc_cell_combined_channels.jsonl"
M.PEDS = OUT / "mc_cell_combined_pedestals.json"
M.WORK = ROOT / "build" / "mc_cell_combined"
M.THREADS = 28

COMBINED = "4 K, steep (T_eff 20 K), mismatch x 2, tree of one reticle"
DESIGNS = ("NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive", "TG + dummies", "TG, no ESD",
           "T-switch + OTA buffer", "TG, ESD on the node")       # all six designs of Figure 6

_conditions = M.conditions


def conditions():
    c = _conditions()
    steep = c["4 K, steep (T_eff 20 K)"]
    band = tuple(steep["cryo"])
    c[COMBINED] = dict(cryo=band[:2] + (2.0,) + band[3:], mm=2.0, temp=steep["temp"], tree="reticle")
    return c


M.conditions = conditions


def sets():
    return {"combined": [(d, COMBINED, 20, False) for d in DESIGNS]}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "combined":
        M.sets = sets
        M.simulate(["combined"])
    M.collect()
