"""Steep-subthreshold bands, calibrated on measured 77 K data.

The bands of studies/cryogenic.py shift |V_T| and scale the mobility of the room-temperature models and
run at 27 C, so their subthreshold swing stays near its room-temperature value (80-95 mV/decade). At low
temperature the swing falls, which sharpens the turn-off of a switch and can change how its channel
charge divides between the line and the hold node.

An effective-temperature band adds this: the model files get tnom = T_eff and the deck runs at
.temp = T_eff, so the BSIM4 temperature-scaling terms vanish (no extrapolation of the qualified
temperature equations) while the thermal voltage kT/q, and with it the subthreshold swing, follows
T_eff. The model also recomputes its surface and built-in potentials at T_eff, which moves the
threshold; that shift is measured here (constant-current threshold, 0.1 uA x W/L at |V_DS| = 10 mV)
and removed from dV_T, so the switch devices keep the threshold of their band.

Calibration on data: Beall et al. measured SkyWater LVT nMOS at 77 K (|V_DS| = 10 mV, 1 nA
resolution); clone their data into build/external/beall2026 (see studies/beall_check.py). Their swing
between 3 and 30 nA (about 50 mV/decade) is reproduced by the 77 K band at T_eff of about 120 K, not
77 K: the measured devices are less steep than kT/q alone predicts, as expected from band tails and
interface states. Three bands follow:
  "4 K, steep (T_eff 120 K)"   the 4 K band with the swing measured at 77 K
  "4 K, steep (T_eff 30 K)"    15-20 mV/decade, within the range measured on bulk CMOS at 4.2 K
  "4 K, steep (T_eff 20 K)"    about 10-13 mV/decade, near the steepest long-channel bulk devices at 4.2 K
                               (about 11 mV/decade; 28 nm devices about 28 mV/decade; Beckers et al. 2018)

Run:  python studies/subthreshold.py      (about 3 min; writes results/subthreshold.{json,md})
"""
import csv
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flow import spice  # noqa: E402
from flow.pdk import fet18_lib_line  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
EXT = ROOT / "build" / "external" / "beall2026" / "cryo_data"
WORK = ROOT / "build" / "subthreshold" / "subthreshold"
BAND_77K = (0.10, 2.5, 1.0, 0.80, 3.0)          # band "77 K Beall fit" of studies/cryogenic.py
BAND_4K = (0.15, 2.0, 1.0, 0.15, 2.0)           # band "4 K proxy" of studies/cryogenic.py
T_SCAN = (200.0, 150.0, 120.0, 100.0, 77.0, 50.0, 30.0)
T_EFF = (120.0, 30.0, 20.0)
DATA = {"nMOS L 0.15 W 1.6": ("nmos_FET_len_0p15_wid_1p6", 1.6, 0.15),
        "nMOS L 1 W 1.6": ("nmos_FET_len_1_wid_1p6", 1.6, 1.0)}
SWITCH = {"nfet_01v8": (1.0, 0.15), "pfet_01v8": (2.0, 0.15), "nfet_g5v0d10v5": (0.84, 0.5),
          "pfet_g5v0d10v5": (1.68, 0.5)}
WINDOW_DATA = (3e-9, 30e-9)
WINDOW_DEEP = (1e-11, 1e-9)


def deck(lib, temp, dev, w, l):
    sgn = -1 if dev.startswith("pfet") else 1
    vmax = 3.3 if "g5v0" in dev else 1.8
    return f"""* id-vg, |V_DS| = 10 mV, quasi-static ramp (1.8 V/s: no displacement current)
{lib}
.temp {temp}
VG g 0 PWL(0 0 1 {sgn * vmax})
VD d 0 {sgn * 0.01}
XM d g 0 0 sky130_fd_pr__{dev} w={w} l={l}
.option gmin=1e-18 abstol=1e-17 reltol=1e-6
.tran 1m 1 0 1m
.save i(vd)
.end
"""


def sim(band, t_eff, dev, w, l, devices):
    temp = 27.0 if t_eff is None else round(t_eff - 273.15, 2)
    cryo = tuple(band) if t_eff is None else tuple(band) + (temp,)
    lib = fet18_lib_line("tt", devices, False, cryo)
    name = f"{dev}_w{w:g}_l{l:g}_{'_'.join(f'{x:g}' for x in cryo)}"
    wv = spice.run_ngspice(deck(lib, temp, dev, w, l), WORK, name)
    return wv["time"] * (3.3 if "g5v0" in dev else 1.8), np.abs(wv["i(vd)"])


def swing(vg, i, window):
    """Subthreshold swing (mV/decade) between the gate voltages where the current crosses the window."""
    lo, hi = window
    x = np.log10(np.maximum.accumulate(np.maximum(i, 1e-30)))
    if x[-1] < np.log10(hi) or x[0] > np.log10(lo):
        return float("nan")
    return float((np.interp(np.log10(hi), x, vg) - np.interp(np.log10(lo), x, vg)) / np.log10(hi / lo) * 1e3)


def vt(vg, i, w, l):
    x = np.log10(np.maximum.accumulate(np.maximum(i, 1e-30)))
    return float(np.interp(np.log10(1e-7 * w / l), x, vg))


def measured(folder):
    rows = list(csv.reader(open(EXT / folder / "idvg_Vd0p01.csv")))[1:]
    vg = np.array([float(r[1]) for r in rows])
    i = np.abs(np.array([float(r[2]) for r in rows]))
    o = np.argsort(vg)
    return vg[o], i[o]


def compensated(band, t_eff, shift):
    """Band tuple with tnom and with dV_T reduced by the threshold shift that T_eff itself causes."""
    b = list(band)
    b[0] -= shift["nfet_01v8"]
    b[3] -= shift["pfet_01v8"]
    return tuple(round(x, 4) for x in b) + (round(t_eff - 273.15, 2),)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    out = {"window_data": WINDOW_DATA, "window_deep": WINDOW_DEEP, "data": {}, "switch": {}, "bands": {}}
    # 1. measured 77 K swing against the 77 K band at 27 C and over T_eff (LVT devices, as measured)
    for name, (folder, w, l) in DATA.items():
        vg, i = measured(folder)
        r = {"measured": swing(vg, i, WINDOW_DATA), "vt_measured": vt(vg, i, w, l), "model": {}}
        with ThreadPoolExecutor(8) as ex:
            curves = list(ex.map(lambda t: (t, sim(BAND_77K, t, "nfet_01v8_lvt", w, l, "lvt")), (None,) + T_SCAN))
        for t, (v, x) in curves:
            r["model"][f"{t or 300:g}"] = {"swing": swing(v, x, WINDOW_DATA), "vt": vt(v, x, w, l)}
        out["data"][name] = r
    # 2. threshold shift caused by T_eff on the switch devices, then the compensated 4 K bands
    jobs = list(SWITCH.items())
    with ThreadPoolExecutor(8) as ex:
        base = dict(zip(SWITCH, ex.map(lambda j: sim(BAND_4K, None, j[0], *j[1], "hold"), jobs)))
    for t in T_EFF:
        with ThreadPoolExecutor(8) as ex:
            raw = dict(zip(SWITCH, ex.map(lambda j: sim(BAND_4K, t, j[0], *j[1], "hold"), jobs)))
        shift = {d: vt(*raw[d], *SWITCH[d]) - vt(*base[d], *SWITCH[d]) for d in SWITCH}
        band = compensated(BAND_4K, t, shift)
        with ThreadPoolExecutor(8) as ex:
            comp = dict(zip(SWITCH, ex.map(lambda j: sim(band[:5], t, j[0], *j[1], "hold"), jobs)))
        out["bands"][f"4 K, steep (T_eff {t:g} K)"] = band
        out["switch"][f"{t:g}"] = {d: {"vt_band_27C": vt(*base[d], *SWITCH[d]), "vt_shift_uncompensated": shift[d],
                                       "vt_compensated": vt(*comp[d], *SWITCH[d]),
                                       "swing_27C": swing(*base[d], WINDOW_DEEP), "swing_T_eff": swing(*comp[d], WINDOW_DEEP)}
                                   for d in SWITCH}
    (OUT / "subthreshold.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["## Steep-subthreshold bands", "",
         f"Swing in mV/decade at |V_DS| = 10 mV. Data window {WINDOW_DATA[0]:g}-{WINDOW_DATA[1]:g} A (resolved by the 77 K data); "
         f"deep window {WINDOW_DEEP[0]:g}-{WINDOW_DEEP[1]:g} A. Threshold: 0.1 µA × W/L.", "",
         "### Measured 77 K (Beall et al., LVT nMOS) against the 77 K band over T_eff", "",
         "| device | measured | " + " | ".join(f"T_eff {t:g} K" for t in (300.0,) + T_SCAN) + " |",
         "|---|---|" + "---|" * (len(T_SCAN) + 1)]
    for n, r in out["data"].items():
        L.append(f"| {n}, swing | {r['measured']:.0f} | " + " | ".join(f"{m['swing']:.0f}" for m in r["model"].values()) + " |")
        L.append(f"| {n}, V_T (V) | {r['vt_measured']:.3f} | " + " | ".join(f"{m['vt']:.3f}" for m in r["model"].values()) + " |")
    L += ["", "### Switch devices in the 4 K band, before and after the effective temperature", "",
          "| T_eff | device | V_T at 27 C (V) | shift from T_eff alone (mV) | V_T compensated (V) | swing 27 C | swing T_eff |",
          "|---|---|---|---|---|---|---|"]
    for t, rows in out["switch"].items():
        for d, r in rows.items():
            L.append(f"| {t} K | {d} | {r['vt_band_27C']:.3f} | {r['vt_shift_uncompensated'] * 1e3:.0f} | {r['vt_compensated']:.3f} | "
                     f"{r['swing_27C']:.0f} | {r['swing_T_eff']:.0f} |")
    L += ["", "Bands (dV_T_n, mu_n, mm, dV_T_p, mu_p, tnom °C): " + "; ".join(f"{k}: {v}" for k, v in out["bands"].items())]
    (OUT / "subthreshold.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
