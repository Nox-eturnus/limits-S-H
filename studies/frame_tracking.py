"""The static budget with and without tracking of the qubit frequencies, and with idle time.

A droop offset is predictable: it grows at a rate that a calibration can measure, so the controller can
update the single-qubit frames (virtual Z) from the known offset. That removes the Stark part of the
error, during the gate and during idle time, and leaves the conditional phase. This script gives the
static budget per gate for five slopes, without idle time and with 1 and 10 us of idle time per gate
layer, untracked and frame-tracked, and for a Stark coefficient three times larger. The Stark
coefficient of 1e8 Hz/V is the shift with the exchange (barrier) gate voltage reported by Bartee et al.

Run:  python studies/frame_tracking.py      (writes results/frame_tracking.{json,md})
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from flow import budget as B  # noqa: E402
from repeated_gates import budget  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
SLOPES = (3.87, 7.25, 10.0, 16.6, 33.69)
TARGETS = (1e-3, 1e-4)
IDLES = (0.0, 1e-6, 10e-6)


def main():
    rows = []
    for s in SLOPES:
        for idle in IDLES:
            lay = B.layer(s_dec_per_v=s, t_idle=idle)
            for tgt in TARGETS:
                r = {"s": s, "t_idle": idle, "target": tgt,
                     "untracked": budget(lay, tgt, 1, "coherent"), "tracked": budget(lay, tgt, 1, "frame")}
                rows.append(r)
                print(f"s {s:g} idle {idle * 1e6:g} us 1-F {tgt:g}: untracked {r['untracked'] * 1e3:.3g} mV, "
                      f"tracked {r['tracked'] * 1e3:.3g} mV", flush=True)
    # sensitivity: Stark coefficient x3 at s = 10
    alpha = []
    for k in (1.0, 3.0):
        lay = B.layer(s_dec_per_v=10.0, stark_q2=k * B.STARK_BARTEE)
        alpha.append({"alpha_factor": k, "untracked": budget(lay, 1e-3, 1, "coherent"),
                      "tracked": budget(lay, 1e-3, 1, "frame")})
    out = {"rows": rows, "alpha_sensitivity_s10_t1e-3": alpha}
    (OUT / "frame_tracking.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["## Static budget per gate, untracked and frame-tracked (one CZ, idle time per layer)", "",
         "| s (dec/V) | target | idle 0: untracked / tracked | idle 1 µs | idle 10 µs |", "|---|---|---|---|---|"]
    for s in SLOPES:
        for tgt in TARGETS:
            cells = []
            for idle in IDLES:
                r = next(x for x in rows if x["s"] == s and x["t_idle"] == idle and x["target"] == tgt)
                cells.append(f"{r['untracked'] * 1e3:.3g} / {r['tracked'] * 1e3:.3g} mV")
            L.append(f"| {s:g} | {tgt:g} | " + " | ".join(cells) + " |")
    L += ["", "Stark coefficient ×1 and ×3 at s = 10, 99.9 %: " +
          "; ".join(f"×{a['alpha_factor']:g}: untracked {a['untracked'] * 1e3:.3g} mV, tracked {a['tracked'] * 1e3:.3g} mV"
                    for a in alpha), ""]
    (OUT / "frame_tracking.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
