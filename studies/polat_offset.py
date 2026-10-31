"""Agreement with the simulated CZ infidelity of Polat et al. without the fitted duration offset.

studies/benchmark_polat.py reproduces their Figure 2 with an effective pulse 0.05 ns shorter than the plotted
gate time, an offset fitted to their data. This script repeats the comparison at offsets of 0, 0.025, 0.045,
0.05 and 0.055 ns, so the agreement at zero offset can be quoted next to the fitted one, and splits it into the
points away from the fidelity minima (where the offset hardly matters) and the points near them.

Run:  python studies/polat_offset.py     (a few minutes; writes results/polat_offset.json)
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import benchmark_polat as P  # noqa: E402

OFFSETS_NS = (0.0, 0.025, 0.045, 0.05, 0.055)


def run(offset_ns):
    P.FIG2_DURATION_OFFSET_S = offset_ns * 1e-9
    rows = P.b1_v2_fig2()
    dev = np.array([abs(r["ours"] / r["polat"] - 1) for r in rows])
    # minima: points whose reference infidelity is below a tenth of the geometric mean of its two neighbours
    f = np.array([r["polat"] for r in rows])
    notch = np.zeros(len(f), bool)
    notch[1:-1] = f[1:-1] < 0.1 * np.sqrt(f[:-2] * f[2:])
    near = notch | np.roll(notch, 1) | np.roll(notch, -1)
    return offset_ns, {"points": len(rows), "median_rel_dev": float(np.median(dev)), "max_rel_dev": float(dev.max()),
                       "median_away_from_minima": float(np.median(dev[~near])), "max_away_from_minima": float(dev[~near].max()),
                       "max_near_minima": float(dev[near].max()) if near.any() else None, "n_near_minima": int(near.sum())}


def main():
    with ProcessPoolExecutor(len(OFFSETS_NS)) as ex:
        res = dict(ex.map(run, OFFSETS_NS))
    out = {f"{k:g} ns": v for k, v in res.items()}
    (OUT / "polat_offset.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k, v in out.items():
        print(k, {a: (round(b * 100, 3) if isinstance(b, float) else b) for a, b in v.items()})


if __name__ == "__main__":
    main()
