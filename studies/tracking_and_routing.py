"""Tracking accuracy at a small Zeeman difference, and the track area of a separate array's connections.

A. The operational budget when frame tracking misses a fraction f of the offset (studies/partial_tracking_qec.py,
   unchanged: conditional phase as for M = 2, the untracked single-qubit phase of the four barriers around a data qubit
   added in amplitude), without idle time (idles refocused by an echo), at 100 MHz and 15 MHz with the gate rule of
   studies/zeeman_device_scale.py part A (peak exchange a fifth of the Zeeman difference, gate lengthened in
   proportion: 50 ns at 100 MHz, 333 ns at 15 MHz). Also the fraction f_10 at which the budget falls by a tenth. The
   100 MHz rows reproduce results/partial_tracking_qec.json.
B. Track area of the connections of a separate hold array, from the ring geometry of results/separate_array_size.json:
   10^6 connections of the mean length at a pitch of 200 nm (a line beside a shield) against the area of the square of
   array and qubit region times the number of routing layers.

Run:  python studies/tracking_and_routing.py     (about 10 min; writes results/tracking_and_routing.{json,md})
"""
import json
import sys
from pathlib import Path

from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
from flow import budget as FB  # noqa: E402
import partial_tracking_qec as PT  # noqa: E402

ZEEMAN = (100e6, 15e6)
SLOPES = (3.87, 10.0, 16.6, 33.69)
TARGETS = (1e-3, 1e-4)
FRACTIONS = (0.0, 0.01, 0.03, 0.1, 0.3, 1.0)


def part_a():
    out = {}
    for dez in ZEEMAN:
        tg = 50e-9 * 100e6 / dez
        for s in SLOPES:
            lay = FB.layer(s_dec_per_v=s, d_ez=dez, t_gate=tg, dt=max(5e-12, tg / 1e4))
            for t in TARGETS:
                b = {f"{f:g}": PT.budget(lay, t, f) for f in FRACTIONS}
                b0 = b["0"]
                f10 = brentq(lambda f: PT.budget(lay, t, f) - 0.9 * b0, 1e-4, 1.0, xtol=1e-4)
                out[f"{dez / 1e6:g}|{s:g}|{t:g}"] = {"budget": b, "f10": f10, "t_gate": tg}
                print(f"A {dez / 1e6:g} MHz s={s:g} t={t:g}: " + "  ".join(f"f={k} {v * 1e3:.3g} mV" for k, v in b.items())
                      + f"  f10 {f10:.4f}", flush=True)
    return out


def part_b():
    fan = json.loads((ROOT / "results" / "separate_array_size.json").read_text(encoding="utf-8"))
    p, n, reticle = 200e-9, 1e6, 26 * 33
    out = {}
    for layers, r in fan["ring"].items():
        need = n * r["mean_mm"] * 1e-3 * p * 1e6                # mm^2 of track
        square = r["outer_mm"] ** 2
        out[layers] = {"mean_mm": r["mean_mm"], "need_mm2": need, "square_mm2": square,
                       "ratio_square": need / (square * int(layers)), "ratio_reticle": need / (reticle * int(layers))}
        print(f"B {layers} layers: need {need:.0f} mm^2, x{out[layers]['ratio_square']:.2f} of the square, "
              f"x{out[layers]['ratio_reticle']:.2f} of the reticle", flush=True)
    return out


def report(res):
    L = ["# Tracking accuracy at 15 MHz and track area of a separate array", "",
         "## A. Operational budget (mV) with a fraction f of the offset untracked, no idle time; f_10: budget down by a tenth", "",
         "| Zeeman | s (dec/V) | target | " + " | ".join(f"f = {f:g}" for f in FRACTIONS) + " | f_10 |",
         "|---|---|---|" + "---|" * (len(FRACTIONS) + 1)]
    for k, v in res["A"].items():
        dez, s, t = k.split("|")
        L.append(f"| {dez} MHz | {s} | {t} | " + " | ".join(f"{x * 1e3:.3g}" for x in v["budget"].values())
                 + f" | {v['f10']:.3f} |")
    L += ["", "## B. Track area of 10^6 connections at 200 nm against the routing layers", "",
          "| layers | mean (mm) | track needed (mm^2) | square of array and qubit region (mm^2) | needed / square x layers | needed / reticle x layers |",
          "|---|---|---|---|---|---|"]
    for layers, v in res["B"].items():
        L.append(f"| {layers} | {v['mean_mm']:.1f} | {v['need_mm2']:.0f} | {v['square_mm2']:.0f} | {v['ratio_square']:.2f} | "
                 f"{v['ratio_reticle']:.2f} |")
    (OUT / "tracking_and_routing.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    res = {"B": part_b(), "A": part_a()}
    (OUT / "tracking_and_routing.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    report(res)


if __name__ == "__main__":
    main()
