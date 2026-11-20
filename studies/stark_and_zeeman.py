"""Two gate-model checks: where the exchange error overtakes the Stark shift, and the Zeeman difference.

A. The untracked single-gate static budget at 99.9 % with and without the Stark shift (10^8 Hz/V on one qubit), and
   the Stark-only budget, against the exchange slope: the slope at which the exchange-only budget equals the
   Stark-only one, and the slope above which the Stark shift lowers the budget by less than 15 %.
B. The frame-tracked budget for M = 2 gates (the operational budget, as in studies/repeated_gates.py) for Zeeman
   differences of 100, 50 and 25 MHz, with the gate lengthened in proportion below 100 MHz (as in
   studies/system_integration.py), at 3.87, 10 and 33.69 dec/V and both targets.

Run:  python studies/stark_and_zeeman.py     (about 10 min; writes results/stark_and_zeeman.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
from flow import budget as B  # noqa: E402
import repeated_gates as RG  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"


def untracked(s, stark, target=1e-3):
    lay = B.layer(s_dec_per_v=s, stark_q2=stark)
    return min(B.max_static(lay, target, +1), B.max_static(lay, target, -1))


def stark_only(target=1e-3):
    """Budget from the Stark phase alone: an exchange that does not respond to the barrier (slope -> 0)."""
    lay = B.layer(s_dec_per_v=1e-6)
    return min(B.max_static(lay, target, +1), B.max_static(lay, target, -1))


def part_a():
    b_s = stark_only()
    rows = {}
    for s in (3.87, 5, 6, 7, 7.25, 8, 8.5, 9, 10, 12, 14, 15, 16, 16.6, 18, 20, 25, 33.69):
        rows[s] = {"with": untracked(s, B.STARK_BARTEE), "without": untracked(s, 0.0)}
        print(f"A s={s:6.2f}  with {rows[s]['with']*1e3:.4f}  without {rows[s]['without']*1e3:.4f}  "
              f"ratio {rows[s]['with']/rows[s]['without']:.4f}", flush=True)
    f_eq = lambda s: untracked(s, 0.0) - b_s  # noqa: E731
    s_eq = brentq(f_eq, 5, 14, xtol=1e-3)
    f_15 = lambda s: untracked(s, B.STARK_BARTEE) / untracked(s, 0.0) - 0.85  # noqa: E731
    s_15 = brentq(f_15, 10, 25, xtol=1e-3)
    return {"stark_only_V": b_s, "slope_equal": s_eq, "slope_stark_below_15pct": s_15,
            "rows": {f"{k:g}": v for k, v in rows.items()}}


def part_b():
    out = {}
    for dez, tg in ((100e6, 50e-9), (50e6, 100e-9), (25e6, 200e-9)):
        for s in (3.87, 10.0, 33.69):
            lay = B.layer(s_dec_per_v=s, d_ez=dez, t_gate=tg, dt=max(5e-12, tg / 1e4))
            for t in (1e-3, 1e-4):
                b = RG.budget(lay, t, 2, "frame")
                out[f"{dez/1e6:g} MHz|{s:g}|{t:g}"] = b
                print(f"B {dez/1e6:g} MHz {tg*1e9:g} ns s={s:g} t={t:g}: frame-tracked M=2 {b*1e3:.4f} mV", flush=True)
    return out


def main():
    a = part_a()
    b = part_b()
    (OUT / "stark_and_zeeman.json").write_text(json.dumps({"A": a, "B": b}, indent=1), encoding="utf-8")
    L = ["# Stark crossover and Zeeman difference", "",
         f"A. Stark-only budget at 99.9 %: {a['stark_only_V']*1e3:.3f} mV. Exchange-only budget equals it at "
         f"{a['slope_equal']:.2f} dec/V. The Stark shift lowers the budget by less than 15 % above "
         f"{a['slope_stark_below_15pct']:.2f} dec/V.", "",
         "| s (dec/V) | with Stark (mV) | without (mV) | ratio |", "|---|---|---|---|"]
    for s, r in a["rows"].items():
        L.append(f"| {s} | {r['with']*1e3:.3f} | {r['without']*1e3:.3f} | {r['with']/r['without']:.3f} |")
    L += ["", "B. Frame-tracked budget for M = 2 (mV) against the Zeeman difference, gate lengthened below 100 MHz", "",
          "| case | 3.87: 99.9 / 99.99 | 10 | 33.69 |", "|---|---|---|---|"]
    for dez in ("100", "50", "25"):
        L.append(f"| {dez} MHz | " + " | ".join(
            f"{b[f'{dez} MHz|{s}|0.001']*1e3:.3g} / {b[f'{dez} MHz|{s}|0.0001']*1e3:.3g}" for s in ("3.87", "10", "33.69")) + " |")
    (OUT / "stark_and_zeeman.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
