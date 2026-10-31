"""Markdown summaries of four long studies, written from their stored results with the studies' own table functions.

    results/mismatch.md       studies/mismatch.py
    results/tree.md           studies/tree.py
    results/system_budget.md  studies/system_budget.py
    results/error_budget.md   studies/error_budget.py

Run:  python studies/summaries.py      (seconds)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
sys.path.insert(0, str(ROOT / "studies"))
import error_budget  # noqa: E402
import mismatch  # noqa: E402
import system_budget  # noqa: E402
import tree  # noqa: E402


def load(name):
    return json.loads((RES / name).read_text(encoding="utf-8"))


def main():
    m = load("mismatch.json")
    (RES / "mismatch.md").write_text("\n".join(mismatch.table(m["room_temperature"], m["cryogenic"])), encoding="utf-8")
    (RES / "tree.md").write_text("\n".join(tree.table(load("tree.json"))), encoding="utf-8")
    system_budget.table(load("system_budget.json"))
    error_budget.write_markdown(load("error_budget.json"), RES / "error_budget.md")


if __name__ == "__main__":
    main()
