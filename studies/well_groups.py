"""How many electrodes can share an isolated well, and what the well costs in area.

The NMOS switch holds a window of W = 0.4 V on every channel (0.2 V with twice the mismatch,
studies/scaled_sigma_nmos.py) above the potential V_w of its isolated p-well, so the electrodes of one well must
be tuned to static levels within W of each other. Measured spreads of gate operating voltages (random, within a
device):
  - Neyens et al., Nature 629, 80 (2024), Intel Si/SiGe, 300 mm: random gate V_T variation 59 mV; random variation
    of the single-electron voltage 61 and 63 mV; per-gate cross-wafer standard deviation 63 to 89 mV for the
    plunger and barrier gates (all causes, including systematic cross-wafer variation).
  - Loenders et al., arXiv:2605.12143 (2026), imec SiMOS 7 x 7 array: threshold-voltage standard deviation below
    63 mV at the optimal 17 nm oxide.
For tuned levels drawn from a Gaussian of standard deviation sigma, a group of n electrodes fits one well if the
range of its n levels is at most W (V_w is set from the group's own levels). The script gives the largest n for
which this holds with probability 0.99 and 0.999, for sigma = 60 and 90 mV and W = 0.3, 0.4 and 0.5 V.

Area: in SKY130 an isolated p-well is a deep n-well (dnwell.3: 6.3 um spacing between deep n-wells) enclosed by an
n-well ring that reaches 1.03 um inside it (nwell.6) and 0.4 um outside (nwell.5), so neighbouring wells lose a
band of about 1.03 + 6.3 + 1.03 = 8.4 um of transistor area between them. For a square group of n cells at the
22 um pitch this is ((L + 8.4 um)^2 - L^2) / L^2 of the group's transistor area, L = sqrt(n) 22 um. The hold
capacitors (metal-insulator-metal, on the upper metals) can lie over the band.

Run:  python studies/well_groups.py     (seconds; writes results/well_groups.{json,md})
"""
import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parents[1] / "results"
SIGMAS = (0.060, 0.090)
WINDOWS = (0.2, 0.3, 0.4, 0.5)
PROBS = (0.99, 0.999)
PITCH = 22e-6
BAND = 1.03e-6 + 6.3e-6 + 1.03e-6
N_TRIAL = 200_000


def p_fit(n, w_over_sigma, rng):
    x = rng.standard_normal((N_TRIAL, n))
    return float(np.mean(x.max(1) - x.min(1) <= w_over_sigma))


def largest_n(w_over_sigma, p, rng):
    best = 1
    for n in (2, 3, 4, 6, 8, 9, 12, 16, 25, 36, 49, 64, 100, 144, 256, 400, 1000):
        if p_fit(n, w_over_sigma, rng) >= p:
            best = n
        else:
            break
    return best


def overhead(n):
    side = np.sqrt(n) * PITCH
    return float(((side + BAND) ** 2 - side ** 2) / side ** 2)


def main():
    rng = np.random.default_rng(6)
    rows = []
    for s in SIGMAS:
        for w in WINDOWS:
            for p in PROBS:
                n = largest_n(w / s, p, rng)
                rows.append({"sigma": s, "window": w, "p": p, "n_max": n, "area_overhead": overhead(n),
                             "p_fit_n4": p_fit(4, w / s, rng), "p_fit_n16": p_fit(16, w / s, rng)})
    out = {"band_um": BAND * 1e6, "pitch_um": PITCH * 1e6, "rows": rows,
           "overhead_by_n": {n: overhead(n) for n in (1, 4, 9, 16, 64, 256)}}
    (OUT / "well_groups.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["## Electrodes per isolated well", "",
         f"Band lost between wells: {BAND * 1e6:.1f} µm; cell pitch {PITCH * 1e6:.0f} µm.", "",
         "| sigma (mV) | window (V) | probability all fit | largest group n | transistor-area overhead | P(fit), n = 4 | P(fit), n = 16 |",
         "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['sigma'] * 1e3:.0f} | {r['window']:.1f} | {r['p']} | {r['n_max']} | {r['area_overhead']:.0%} | "
                 f"{r['p_fit_n4']:.4f} | {r['p_fit_n16']:.4f} |")
    L += ["", "Overhead by group size: " + ", ".join(f"n = {n}: {v:.0%}" for n, v in out["overhead_by_n"].items())]
    (OUT / "well_groups.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
