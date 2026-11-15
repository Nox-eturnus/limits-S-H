"""The bootstrapped switch in the combined worst case on a 20 mV grid of held voltages.

The same 20 channels (same seeds) and the same condition as studies/mc_cell_combined.py (steepest band, twice the
mismatch, tree source of a full reticle), simulated every 20 mV from 0.3 to 1.5 V, so that the largest move from a
tuned level can be read from the local slope of the deviation rather than from chords between the standard voltages.

Run:  python studies/mc_cell_combined_fine.py run       (about 2 h on 28 threads; needs ngspice and the PDK; seeds its
                                                         log with the standard-voltage records of the combined case)
      python studies/mc_cell_combined_fine.py collect   (writes results/mc_cell_combined_fine_pedestals.json)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import mc_cell_combined as mc14  # noqa: E402

M = mc14.M
BOOT = "bootstrapped (transistor level), 0.3 V underdrive"
M.LOG = OUT / "mc_cell_combined_fine_channels.jsonl"
M.PEDS = OUT / "mc_cell_combined_fine_pedestals.json"
M.WORK = ROOT / "build" / "mc_cell_combined_fine"


def grid(design, fine=False):
    return [round(0.3 + 0.02 * k, 3) for k in range(61)]


def seed_log():
    if M.LOG.exists():
        return
    old = (ROOT / "results" / "mc_cell_combined_channels.jsonl").read_text(encoding="utf-8").splitlines()
    keep = [l for l in old if json.loads(l)["design"] == BOOT and "error" not in json.loads(l)]
    M.LOG.write_text("\n".join(keep) + "\n", encoding="utf-8")


if __name__ == "__main__":
    M.grid = grid
    M.sets = lambda: {"fine": [(BOOT, mc14.COMBINED, 20, True)]}
    if sys.argv[1:] and sys.argv[1] == "run":
        seed_log()
        M.simulate(["fine"])
    M.collect()
