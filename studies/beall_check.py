"""Check of the two-parameter cryogenic proxy against the Beall 2026 77 K SKY130 models.

Beall et al. (arXiv:2604.21625) measured SkyWater 130 nm low-V_T FETs at 77 K and refit BSIM4 by
scaling VTH0, U0, RDSW, NFACTOR, VSAT, ETA0 and DELTA per bin. Their model cards and data are public
(github.com/UTA-Advanced-Detector-Technologies/Skywater-130nm-77K-Cryogenic-Models); clone them into
build/external/beall2026 before running (used as data only, not modified).

The proxy of flow/pdk.py shifts |V_T| and scales the mobility, nothing else. This script asks whether
those two parameters reproduce what a switch cares about: the channel conductance at small V_DS over
the on-state gate drive, and the threshold. For three measured devices (nMOS L = 0.15 / 1 um,
pMOS L = 0.35 um, W = 1.6 um):

  1. the PDK LVT model at 27 C (300 K reference);
  2. Beall's 77 K model at -196.15 C (their intended use), and their measured 77 K data;
  3. the proxy on the PDK LVT model at 27 C, (dV_T, mu) fitted to Beall's model on a grid;
  4. the proxy at the 77 K band (+0.10 V, x1.7).

Reported: conductance error (RMS of log G over the on-state range) and threshold shift.

Run:  python studies/beall_check.py      (about 2 min; writes results/beall_check.{json,png})
"""
import csv
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flow import config, spice  # noqa: E402
from flow.pdk import fet18_lib_line  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
EXT = ROOT / "build" / "external" / "beall2026"
WORK = ROOT / "build" / "cryogenic" / "beall"
VD = 0.01                                    # V, the measured transfer curves at |V_DS| = 10 mV
DEVICES = {
    "nMOS L 0.15 W 1.6": dict(kind="nfet", w=1.6, l=0.15, data="nmos_FET_len_0p15_wid_1p6"),
    "nMOS L 1 W 1.6": dict(kind="nfet", w=1.6, l=1.0, data="nmos_FET_len_1_wid_1p6"),
    "pMOS L 0.35 W 1.6": dict(kind="pfet", w=1.6, l=0.35, data="pmos_FET_len_0.35_wid_1.6"),
}
BAND_77K = (0.10, 1.7)
GRIDS = {"nfet": (np.round(np.arange(0.0, 0.2501, 0.05), 3), np.round(np.arange(1.0, 4.51, 0.25), 2)),
         # the measured 77 K pMOS threshold rises by ~0.5 V (Beall data): a wider shift range
         "pfet": (np.round(np.arange(0.0, 0.9001, 0.05), 3), np.round(np.arange(0.5, 3.01, 0.25), 2))}


def beall_card(kind):
    """Beall's 77 K card with its one relative include pointed at the installed PDK's lod.spice."""
    src = EXT / "cryo_models" / f"sky130_fd_pr__{kind}_01v8_lvt__tt_77k.corner.spice"
    dst = WORK / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    lod = (config.SKY130_NGSPICE_LIB.parent / "parameters" / "lod.spice").as_posix()
    text = re.sub(r'^\.include\s+"[^"]*lod\.spice"', f'.include "{lod}"', src.read_text(), flags=re.M)
    if not dst.exists() or dst.read_text() != text:
        dst.write_text(text)
    return dst


def deck(kind, w, l, lib_lines, temp):
    sgn = 1 if kind == "nfet" else -1
    return f"""* id-vg
{lib_lines}
.temp {temp}
VG g 0 PWL(0 0 1u {sgn * 1.8})
VD d 0 {sgn * VD}
XM d g 0 0 sky130_fd_pr__{kind}_01v8_lvt w={w} l={l}
.tran 2n 1u
.save i(vd)
.end
"""


def run(kind, w, l, lib_lines, temp, name):
    wv = spice.run_ngspice(deck(kind, w, l, lib_lines, temp), WORK, name)
    vg = wv["time"] / 1e-6 * 1.8
    return vg, np.abs(wv["i(vd)"])


def pdk_lines(cryo=None):
    return fet18_lib_line("tt", "lvt", False, cryo)


def beall_lines(kind):
    nonfet = (config.SKY130_NGSPICE_LIB.parent / "corners" / "tt" / "nonfet.spice").as_posix()
    allsp = (config.SKY130_NGSPICE_LIB.parent / "all.spice").as_posix()
    return (".param mc_mm_switch=0\n.param mc_pr_switch=0\n"
            f'.include "{allsp}"\n.include "{nonfet}"\n.include "{beall_card(kind).as_posix()}"')


def measured(dev):
    f = EXT / "cryo_data" / dev["data"] / ("idvg_Vd0p01.csv" if dev["kind"] == "nfet" else "idvg_Vd-0p01.csv")
    rows = list(csv.reader(open(f)))[1:]
    vg = np.abs(np.array([float(r[1]) for r in rows]))
    i = np.abs(np.array([float(r[2]) for r in rows]))
    o = np.argsort(vg)
    return vg[o], i[o]


def metrics(vg, i, w, l, ref=None):
    icrit = 1e-7 * w / l
    vt = float(np.interp(icrit, i, vg)) if i.max() > icrit else np.nan
    return {"vt": vt, "g_on": float(np.interp(1.8, vg, i) / VD)}


def log_g_error(vg, i, vg_ref, i_ref, lo=0.9, hi=1.8):
    x = np.linspace(lo, hi, 40)
    a, b = np.interp(x, vg, i), np.interp(x, vg_ref, i_ref)
    ok = (a > 0) & (b > 0)
    return float(np.sqrt(np.mean(np.log(a[ok] / b[ok]) ** 2)))


def main():
    spice.REUSE = True
    out = {}
    for name, dev in DEVICES.items():
        kind, w, l = dev["kind"], dev["w"], dev["l"]
        tag = name.replace(" ", "_").replace(".", "p")
        vg0, i0 = run(kind, w, l, pdk_lines(), 27.0, f"{tag}_pdk300")
        vgn, i_n = run(kind, w, l, pdk_lines(), -196.15, f"{tag}_pdk77naive")
        vgb, ib = run(kind, w, l, beall_lines(kind), -196.15, f"{tag}_beall77")
        vgm, im = measured(dev)
        dg, mg = GRIDS[kind]
        grid = [(dvt, mu) for dvt in dg for mu in mg]

        def proxy(c):
            vg, i = run(kind, w, l, pdk_lines(c), 27.0, f"{tag}_px{c[0]:g}_{c[1]:g}")
            return c, vg, i

        with ThreadPoolExecutor(16) as ex:
            px = list(ex.map(proxy, grid))
        errs = {c: log_g_error(vg, i, vgb, ib) for c, vg, i in px}
        best = min(errs, key=errs.get)
        vgp, ip = next((vg, i) for c, vg, i in px if c == best)
        errs_m = {c: log_g_error(vg, i, vgm, im) for c, vg, i in px}
        best_m = min(errs_m, key=errs_m.get)
        vgk, ik = run(kind, w, l, pdk_lines(BAND_77K), 27.0, f"{tag}_band77")
        m0, mb, mm_ = metrics(vg0, i0, w, l), metrics(vgb, ib, w, l), metrics(vgm, im, w, l)
        out[name] = {
            "pdk_300K": m0, "beall_77K_model": mb, "beall_77K_measured": mm_,
            "pdk_naive_77K": metrics(vgn, i_n, w, l),
            "proxy_best": {"dvt": best[0], "mu": best[1], **metrics(vgp, ip, w, l),
                           "log_g_rms_vs_model": errs[best], "log_g_rms_vs_measured": log_g_error(vgp, ip, vgm, im)},
            "proxy_fit_to_measured": {"dvt": best_m[0], "mu": best_m[1], "log_g_rms_vs_measured": errs_m[best_m],
                                      **metrics(*next((vg, i) for c, vg, i in px if c == best_m), w, l)},
            "proxy_band_77K": {**metrics(vgk, ik, w, l), "log_g_rms_vs_model": log_g_error(vgk, ik, vgb, ib),
                               "log_g_rms_vs_measured": log_g_error(vgk, ik, vgm, im)},
            "model_vs_measured_log_g_rms": log_g_error(vgb, ib, vgm, im),
            "pdk300_vs_model_log_g_rms": log_g_error(vg0, i0, vgb, ib),
            "curves": {k: (np.asarray(v[0])[::10].round(4).tolist(), np.asarray(v[1])[::10].tolist())
                       for k, v in {"pdk300": (vg0, i0), "beall77": (vgb, ib), "measured77": (vgm, im),
                                    "proxy_best": (vgp, ip), "proxy_band77": (vgk, ik)}.items()},
        }
        print(name, {k: v for k, v in out[name].items() if k != "curves"}, flush=True)
    (OUT / "beall_check.json").write_text(json.dumps(out, indent=1, default=float))
    plot(out)


def plot(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, len(out), figsize=(5.5 * len(out), 4.5))
    for a, (name, r) in zip(np.atleast_1d(ax), out.items()):
        c = r["curves"]
        for k, st, lab in (("pdk300", "-", "PDK, 300 K"), ("measured77", "k.", "Beall, measured 77 K"),
                           ("beall77", "--", "Beall model, 77 K"),
                           ("proxy_best", ":", f"proxy fit (+{r['proxy_best']['dvt']:g} V, ×{r['proxy_best']['mu']:g})"),
                           ("proxy_band77", "-.", "proxy, our 77 K band (+0.10 V, ×1.7)")):
            a.semilogy(c[k][0], np.maximum(c[k][1], 1e-13), st, ms=2, label=lab)
        a.set(xlabel="|V_GS| (V)", ylabel=f"|I_D| at |V_DS| = {VD * 1e3:g} mV (A)", title=name, ylim=(1e-12, None))
        a.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "beall_check.png", dpi=150)


if __name__ == "__main__":
    main()
