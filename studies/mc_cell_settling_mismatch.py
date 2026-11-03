"""Mismatch of switches sized for settling.

The TG and the NMOS switch of 20 um on 1 pF, as their exact scaled equivalent (a 5 um switch on 0.25 pF from 200 ohm,
studies/mc_cell_settling.py), 20 Monte Carlo channels on the 20 mV grid, 300 K and the 4 K band. The scaled equivalent
draws the mismatch of a 5 um device, whose threshold spread is twice that of a 20 um device, on a node four times
smaller, so its pedestal mismatch is twice that of the real switch: the result bounds the effect of mismatch from
above.

Run:  python studies/mc_cell_settling_mismatch.py           (about 10 min of SPICE)
      python studies/mc_cell_settling_mismatch.py collect   (pedestal file from the logged channels only)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import mc_cell_settling as mc10  # noqa: E402

M = mc10.M
M.LOG = OUT / "mc_cell_settling_mismatch_channels.jsonl"
M.OUT = OUT
M.WORK = ROOT / "build" / "mc_cell_settling_mismatch"
mc10.OUT = OUT

def collect():
    """Pedestals of the logged channels (as studies/mc_cell_settling.py), written to this study's own file."""
    import json
    import numpy as np
    keys = {}
    for (d, c, s, v), r in M.load_log().items():
        keys.setdefault((d, c), {}).setdefault(s, {})[v] = r
    out = {}
    for (d, c), by_seed in keys.items():
        vs = sorted(set(by_seed[0]) & set(by_seed[1]))
        seeds = [s for s in sorted(by_seed) if s > 0 and all(v in by_seed[s] and "error" not in by_seed[s][v] for v in vs)]
        trk = np.array([[by_seed[s][v]["track"] for v in vs] for s in seeds])
        nom = by_seed[0]
        out[f"{d}|{c}"] = {"v": vs, "peds": [[by_seed[s][v]["ped"] for v in vs] for s in seeds], "track": trk.tolist(),
                           "seeds": seeds, "nominal": [nom[v]["ped"] for v in vs],
                           "ok_nominal": [abs(nom[v]["track"]) < M.R.TRACK_TOL for v in vs],
                           "ok_all": (np.abs(trk) < M.R.TRACK_TOL).all(0).tolist()}
    (OUT / "mc_cell_settling_mismatch_pedestals.json").write_text(json.dumps(out), encoding="utf-8")
    print(f"{len(out)} design-condition pairs written", flush=True)


if __name__ == "__main__":
    if sys.argv[1:] != ["collect"]:
        mc10.run("widemm", {"widemm": [(mc10.wide_name(a, 20.0), c, 20, False) for a in ("TG", "NMOS")
                                       for c in ("300 K", "4 K proxy")]})
    collect()
