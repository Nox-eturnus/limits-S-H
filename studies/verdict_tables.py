"""Supplementary tables of worst-channel margins with the verdict rule of studies/calibration_lines.py (resolved only
outside 0.9 to 1.1, otherwise "unresolved"), from results/tail_corrected.json. Margins are unchanged.

Run (after studies/calibration_lines.py):  python studies/verdict_tables.py     (writes results/verdict_tables.md)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import tail_corrected as Y8  # noqa: E402


def main():
    out = json.loads((ROOT / "results" / "tail_corrected.json").read_text(encoding="utf-8"))
    s2 = json.loads((OUT / "calibration_lines.json").read_text(encoding="utf-8"))["s2"]
    for name, r in out["designs"].items():
        for k in r["verdict"]:
            r["verdict"][k] = s2[name][k]
    Y8.OUT = ROOT / "build" / "verdict_tables"          # tables() writes tail_corrected.md there
    Y8.OUT.mkdir(parents=True, exist_ok=True)
    Y8.tables(out)
    src = Y8.OUT / "tail_corrected.md"
    (OUT / "verdict_tables.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    src.unlink()
    print((OUT / "verdict_tables.md").read_text(encoding="utf-8")[:6000])


if __name__ == "__main__":
    main()
