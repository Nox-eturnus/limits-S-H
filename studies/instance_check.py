"""Is the SKY130 Monte Carlo mismatch drawn per switch instance or per deck?

The pedestal testbench (flow/holdstage.py, transient_deck) places one switch instance per held voltage. If the
mismatch is drawn per instance, the seven held voltages of one seed are seven independently mismatched cells,
not one channel. Two checks, in the 4 K band:
  A  seven copies of the TG at the same held voltage (0.6 V) in one deck: if the pedestals differ by about the
     Monte Carlo spread, the draw is per instance;
  B  a deck with a single cell, at each held voltage separately, with the same seed: if the pedestal of that
     cell is correlated across held voltages over seeds, a single-instance deck with a fixed seed reproduces
     one physical cell.
Both hold (copies in one deck differ by 5-7 uV; single-cell decks are correlated 0.85-0.998), which is why
studies/mc_cell.py simulates one single-cell deck per held voltage.

Run:  python studies/instance_check.py      (about 5 min; writes results/instance_check.json)
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import cryogenic as R  # noqa: E402
from flow import holdstage as H  # noqa: E402
from flow import spice  # noqa: E402

BAND = R.BANDS["4 K proxy"]
DESIGN = "TG, no ESD"
V = (0.3, 0.5, 0.7, 0.9, 1.1)
SEEDS = range(1, 13)


def cfg(seed, v_hold, tag):
    base = R.E.base_cfg(cryo=BAND, mismatch=True, seed=seed, **R.DESIGNS[DESIGN])
    return replace(base, v_hold=v_hold, workdir=str(ROOT / "build" / "instance_check" / tag))


def check_a(seed):
    m = H.measure(cfg(seed, (0.6,) * 7, "same_v"))
    return m["pedestal"].tolist()


def check_b(seed, v):
    m = H.measure(cfg(seed, (v,), f"single_{v:g}"))
    return float(m["pedestal"][0])


def main():
    spice.REUSE = True
    with ThreadPoolExecutor(24) as ex:
        a = list(ex.map(check_a, (1, 2, 3)))
        b = {v: list(ex.map(lambda s: check_b(s, v), SEEDS)) for v in V}
    x = np.array([b[v] for v in V]).T                   # (seed, voltage)
    c = np.corrcoef(x, rowvar=False)
    out = {"design": DESIGN, "band": "4 K proxy",
           "A_same_voltage_pedestals_uV": [[p * 1e6 for p in row] for row in a],
           "A_spread_within_deck_uV": [float(np.std(row) * 1e6) for row in a],
           "B_voltages": V, "B_pedestals_uV": (x * 1e6).tolist(),
           "B_corr_adjacent": [float(c[i, i + 1]) for i in range(len(V) - 1)],
           "B_corr_mean_offdiag": float(c[np.triu_indices(len(V), 1)].mean()),
           "B_sd_uV": (x.std(0, ddof=1) * 1e6).tolist()}
    (OUT / "instance_check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("B_pedestals_uV",)}, indent=1))


if __name__ == "__main__":
    main()
