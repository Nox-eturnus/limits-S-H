"""Untracked static budgets against the Stark coefficient.

The untracked budgets rest on a Stark coefficient of 1e8 Hz/V on one qubit (Bartee et al.). Devices differ, so
the single-gate budget and the untracked equal-sign budget (studies/partial_tracking_qec.py, f = 1) are given
here for coefficients of 0, 0.3, 1, 3 and 10 x 1e8 Hz/V, at 3.87, 10 and 33.69 decades per volt and both
targets. The frame-tracked budget does not depend on the coefficient.

Run:  python studies/stark_scan.py     (a few minutes; writes results/stark_scan.{json,md})
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import partial_tracking_qec as PT  # noqa: E402
from flow import budget as B  # noqa: E402

FACTORS = (0.0, 0.3, 1.0, 3.0, 10.0)
SLOPES = (3.87, 10.0, 33.69)
TARGETS = (1e-3, 1e-4)


def one(args):
    s, a = args
    lay = B.layer(s_dec_per_v=s, stark_q2=a * B.STARK_BARTEE)
    out = []
    for t in TARGETS:
        single = min(B.max_static(lay, t, sign=+1), B.max_static(lay, t, sign=-1))
        out.append({"s": s, "factor": a, "target": t, "single_gate": single, "untracked_equal_sign": PT.budget(lay, t, 1.0)})
    return out


def main():
    jobs = [(s, a) for s in SLOPES for a in FACTORS]
    with ProcessPoolExecutor(len(jobs)) as ex:
        rows = [r for part in ex.map(one, jobs) for r in part]
    (OUT / "stark_scan.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    L = ["## Untracked budgets against the Stark coefficient (multiples of 1e8 Hz/V on one qubit)", "",
         "| target | s (dec/V) | " + " | ".join(f"x {a:g}" for a in FACTORS) + " |", "|---|---|" + "---|" * len(FACTORS)]
    for t in TARGETS:
        for s in SLOPES:
            cells = [next(r for r in rows if r["s"] == s and r["factor"] == a and r["target"] == t) for a in FACTORS]
            L.append(f"| {1 - t:.2%} | {s:g} | " + " | ".join(
                f"{c['single_gate'] * 1e3:.3g} / {c['untracked_equal_sign'] * 1e3:.3g}" for c in cells) + " |")
    L += ["", "Cells: single-gate budget / untracked equal-sign budget, in mV."]
    (OUT / "stark_scan.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
