"""Extract Fig. 2 of Polat et al. 2026 (vector graphics) from the arXiv PDF: simulation, Eq. 8 and Eq. 10.

The figure is stored as vector paths, so the data points are read exactly from the PDF and mapped to
data coordinates with the figure's own tick marks (not digitised by eye).
  x: tick at 10 ns -> 392.72 pt, 23.93 pt per 10 ns
  y: 1 - F = 10**(-(y - 56.16) / 12.824)   (decade ticks at 56.16, 68.98, ..., 184.40 pt)
Points at or below the plot floor (1e-10, y >= 184.3) are clipped by the plot and flagged.

The PDF itself is not distributed with this repository.
Usage: python studies/extract_polat_fig2.py <path to arXiv:2508.02902v1 PDF>
Writes results/polat_fig2_extracted.json.
"""
import json
import sys

import pymupdf

sys.path.insert(0, __file__.rsplit("benchmarks", 1)[0])
from flow import config  # noqa: E402

CURVES = {(0.0, 0.45, 0.74): "simulation", (0.85, 0.33, 0.1): "eq8", (0.93, 0.69, 0.13): "eq10"}


def x_to_ns(x):
    return 10.0 + (x - 392.72) / (23.93 / 10.0)


def y_to_infid(y):
    return 10.0 ** (-(y - 56.16) / 12.824)


def extract(pdf_path, page_no=3):
    page = pymupdf.open(pdf_path)[page_no]
    out = {}
    for d in page.get_drawings():
        col = d.get("color") and tuple(round(c, 2) for c in d["color"])
        if col in CURVES and len(d["items"]) > 50:
            pts = [d["items"][0][1]] + [it[2] for it in d["items"] if it[0] == "l"]
            out[CURVES[col]] = [{"t_gate_ns": x_to_ns(p.x), "infidelity": y_to_infid(p.y),
                                 "clipped": p.y >= 184.3} for p in pts]
    return out


if __name__ == "__main__":
    data = extract(sys.argv[1])
    dest = config.PACKAGE_DIR / "results" / "polat_fig2_extracted.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=1))
    for k, v in data.items():
        print(k, len(v), "points, t =", round(v[0]["t_gate_ns"], 2), "...", round(v[-1]["t_gate_ns"], 2), "ns")
