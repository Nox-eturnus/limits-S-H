"""Effective dimension of the pedestals of the combined worst case.

The surrogate of studies/combined_case_fine_move.py is fitted to 20 channels at 61 held voltages, so its covariance
has rank 19. This prints how much of the variance the leading components carry and how strongly adjacent held
voltages correlate.

Run:  python studies/combined_case_rank.py
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import cell_margins as CM  # noqa: E402

KEY = "bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 20 K), mismatch x 2, tree of one reticle"
x, v, *_ = CM.prepare(json.loads((ROOT / "results" / "mc_cell_combined_fine_pedestals.json").read_text(encoding="utf-8"))[KEY])
s = np.linalg.svd((x - x.mean(0)) / np.sqrt(len(x) - 1), compute_uv=False)
print(f"{len(x)} channels, {len(v)} held voltages, rank {int((s > s.max() * 1e-9).sum())}")
print("cumulative variance of the leading components:", np.round(np.cumsum(s ** 2) / (s ** 2).sum(), 4)[:5])
c = np.diag(np.corrcoef(x, rowvar=False), 1)
print(f"correlation of adjacent held voltages: smallest {c.min():.4f}, median {np.median(c):.4f}")
