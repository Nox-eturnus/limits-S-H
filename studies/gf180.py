"""The deciding designs in a second open process, GlobalFoundries GF180MCU (180 nm bulk, 3.3 V).

Models: models/ngspice/sm141064.ngspice and design.ngspice of google/globalfoundries-pdk-libs-gf180mcu_fd_pr (commit
9f992d5, 2023-05-31), placed in ~/pdk/gf180mcu_fd_pr_models. They are BSIM4 subcircuits whose threshold mismatch is
drawn per transistor instance (agauss in each subcircuit), as in SKY130, so the one-cell-per-channel Monte Carlo
of studies/mc_cell.py carries over unchanged.

The model file is copied to build/gf180/ with one change in its fets_mm section: each MOSFET instance gets
    delvto = mis_vth * sw_stat_mismatch * gf_mm  (+ gf_dvt_n for NMOS, - gf_dvt_p for PMOS)   and   mulu0 = gf_mu_(n|p)
so that the cryogenic bands of studies/cryogenic.py (|V_T| raised by dV_T, mobility scaled by mu, mismatch scaled by
mm) apply to GF180 exactly as flow/pdk.py applies them to SKY130.

The hold cells (gf180_hold.lib, written below) use the 3.3 V devices, minimum length 0.28 um, the same widths as the
SKY130 designs of the temperature study, a 3.3 V supply and, for the bootstrap network, the 6 V devices (L 0.7 um)
at 5 V. flow/holdstage.py writes the decks; this module points its model library, cell library and supply at GF180.

Run:  python studies/gf180.py run        (Monte Carlo, about 10 min on 28 threads; also full, tgmin)
      python studies/gf180.py analyse    (margins; writes results/gf180.{json,md})
The channels are in results/gf180_channels.jsonl and the pedestals in results/gf180_pedestals.json.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
MODELS = Path.home() / "pdk" / "gf180mcu_fd_pr_models"
BUILD = ROOT / "build" / "gf180"
XD = 0.24          # source/drain diffusion extension (um)

HOLD_LIB = f"""* GF180MCU hold cells (studies/gf180.py); geometry in um, converted to m for the GF180 subcircuits
.param xd={XD}
.subckt NSWG a b en vss wn=1 l=0.28
XMN a en b vss nmos_3p3 w={{wn*1e-6}} l={{l*1e-6}} ad={{wn*xd*1e-12}} as={{wn*xd*1e-12}} pd={{2*(wn+xd)*1e-6}} ps={{2*(wn+xd)*1e-6}}
.ends NSWG
.subckt TGG a b en enb vdd vss wn=1 wp=2 l=0.28
XMN a en b vss nmos_3p3 w={{wn*1e-6}} l={{l*1e-6}} ad={{wn*xd*1e-12}} as={{wn*xd*1e-12}} pd={{2*(wn+xd)*1e-6}} ps={{2*(wn+xd)*1e-6}}
XMP a enb b vdd pmos_3p3 w={{wp*1e-6}} l={{l*1e-6}} ad={{wp*xd*1e-12}} as={{wp*xd*1e-12}} pd={{2*(wp+xd)*1e-6}} ps={{2*(wp+xd)*1e-6}}
.ends TGG
.subckt TGD a b en enb vdd vss wn=1 wp=2 l=0.28
XMN a en b vss nmos_3p3 w={{wn*1e-6}} l={{l*1e-6}} ad={{wn*xd*1e-12}} as={{wn*xd*1e-12}} pd={{2*(wn+xd)*1e-6}} ps={{2*(wn+xd)*1e-6}}
XMP a enb b vdd pmos_3p3 w={{wp*1e-6}} l={{l*1e-6}} ad={{wp*xd*1e-12}} as={{wp*xd*1e-12}} pd={{2*(wp+xd)*1e-6}} ps={{2*(wp+xd)*1e-6}}
XDN b enb b vss nmos_3p3 w={{max(wn/2,0.22)*1e-6}} l={{l*1e-6}} ad={{max(wn/2,0.22)*xd*1e-12}} as={{max(wn/2,0.22)*xd*1e-12}} pd={{2*(max(wn/2,0.22)+xd)*1e-6}} ps={{2*(max(wn/2,0.22)+xd)*1e-6}}
XDP b en b vdd pmos_3p3 w={{max(wp/2,0.22)*1e-6}} l={{l*1e-6}} ad={{max(wp/2,0.22)*xd*1e-12}} as={{max(wp/2,0.22)*xd*1e-12}} pd={{2*(max(wp/2,0.22)+xd)*1e-6}} ps={{2*(max(wp/2,0.22)+xd)*1e-6}}
.ends TGD
.subckt BOOTT a b enh enhb vdd vneg vss wn=1 l=0.28 cb=50f wt=0.42 lt=0.7
XMS a g b vss nmos_3p3 w={{wn*1e-6}} l={{l*1e-6}} ad={{wn*xd*1e-12}} as={{wn*xd*1e-12}} pd={{2*(wn+xd)*1e-6}} ps={{2*(wn+xd)*1e-6}}
CB t bb {{cb}}
XMB1 bb enhb vss vss nmos_6p0 w={{wt*1e-6}} l={{lt*1e-6}} ad={{wt*xd*1e-12}} as={{wt*xd*1e-12}} pd={{2*(wt+xd)*1e-6}} ps={{2*(wt+xd)*1e-6}}
XMT1 t enh vdd t pmos_6p0 w={{wt*1e-6}} l={{lt*1e-6}} ad={{wt*xd*1e-12}} as={{wt*xd*1e-12}} pd={{2*(wt+xd)*1e-6}} ps={{2*(wt+xd)*1e-6}}
XMG1 g enhb vneg vneg nmos_6p0 w={{wt*1e-6}} l={{lt*1e-6}} ad={{wt*xd*1e-12}} as={{wt*xd*1e-12}} pd={{2*(wt+xd)*1e-6}} ps={{2*(wt+xd)*1e-6}}
XMB2 bb g a vss nmos_6p0 w={{2*wt*1e-6}} l={{lt*1e-6}} ad={{2*wt*xd*1e-12}} as={{2*wt*xd*1e-12}} pd={{2*(2*wt+xd)*1e-6}} ps={{2*(2*wt+xd)*1e-6}}
XMT2 g x t t pmos_6p0 w={{2*wt*1e-6}} l={{lt*1e-6}} ad={{2*wt*xd*1e-12}} as={{2*wt*xd*1e-12}} pd={{2*(2*wt+xd)*1e-6}} ps={{2*(2*wt+xd)*1e-6}}
XMX1 x enh bb vss nmos_6p0 w={{wt*1e-6}} l={{lt*1e-6}} ad={{wt*xd*1e-12}} as={{wt*xd*1e-12}} pd={{2*(wt+xd)*1e-6}} ps={{2*(wt+xd)*1e-6}}
XMX2 x enh t t pmos_6p0 w={{wt*1e-6}} l={{lt*1e-6}} ad={{wt*xd*1e-12}} as={{wt*xd*1e-12}} pd={{2*(wt+xd)*1e-6}} ps={{2*(wt+xd)*1e-6}}
.ends BOOTT
"""


def patched_models():
    """Copy sm141064.ngspice with the cryogenic and mismatch-scaling hooks in every MOSFET instance of fets_mm."""
    BUILD.mkdir(parents=True, exist_ok=True)
    dst = BUILD / "sm141064.ngspice"
    if dst.exists():
        return dst
    lines = (MODELS / "sm141064.ngspice").read_text(encoding="utf-8", errors="replace").splitlines()
    sub, n = None, 0
    for i, ln in enumerate(lines):
        m = re.match(r"^\.subckt\s+(\S+)", ln, re.I)
        if m:
            sub = m.group(1).lower()
        if "delvto='mis_vth*sw_stat_mismatch'" in ln and sub:
            if sub.startswith("nmos"):
                rep = "delvto='mis_vth*sw_stat_mismatch*gf_mm+gf_dvt_n' mulu0='gf_mu_n'"
            elif sub.startswith("pmos"):
                rep = "delvto='mis_vth*sw_stat_mismatch*gf_mm-gf_dvt_p' mulu0='gf_mu_p'"
            else:
                continue
            lines[i] = ln.replace("delvto='mis_vth*sw_stat_mismatch'", rep)
            n += 1
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"patched {n} MOSFET instances in {dst}", flush=True)
    return dst


def lib_line(corner="tt", devices="hold", mismatch=False, cryo=None):
    c = tuple(cryo) if cryo is not None else (0.0, 1.0)
    dvt, mu = c[0], c[1]
    mm = c[2] if len(c) > 2 else 1.0
    dvt_p, mu_p = (c[3], c[4]) if len(c) > 4 else (dvt, mu)
    sec = {"tt": "typical", "ff": "ff", "ss": "ss", "fs": "fs", "sf": "sf"}[corner]
    return (f".param sw_stat_global=0 sw_stat_mismatch={1 if mismatch else 0} mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0\n"
            f".param gf_mm={mm:g} gf_dvt_n={dvt:g} gf_mu_n={mu:g} gf_dvt_p={dvt_p:g} gf_mu_p={mu_p:g}\n"
            f'.lib "{patched_models().as_posix()}" {sec}')


def configure():
    """Point flow/holdstage.py and studies/mc_cell.py at GF180."""
    from flow import holdstage as H
    import mc_cell as M
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "gf180_hold.lib").write_text(HOLD_LIB, encoding="utf-8")
    (BUILD / "empty.lib").write_text("* no cells\n", encoding="utf-8")
    H.HOLD_LIB = BUILD / "gf180_hold.lib"
    H.CELLS = BUILD / "empty.lib"
    H.fet18_lib_line = lib_line
    gf = dict(l=0.28, vdd=3.3, vddh=5.0)
    M.DESIGNS = {
        "GF180 NMOS, 0.3 V underdrive": dict(arch="NSW", wn=0.42, esd_area=0.0, v_underdrive=0.3, **gf),
        "GF180 bootstrapped (transistor level), 0.3 V underdrive": dict(arch="BOOTT", wn=0.42, esd_area=0.0, v_underdrive=0.3, **gf),
        "GF180 TG + dummies": dict(arch="TGD", wn=1.0, esd_area=0.0, **gf),
        "GF180 TG, no ESD": dict(arch="TG", wn=1.0, esd_area=0.0, **gf),
    }
    M.LOG = OUT / "gf180_channels.jsonl"
    M.PEDS = OUT / "gf180_pedestals.json"
    M.WORK = BUILD / "decks"
    M.THREADS = 28
    conds = {"300 K": {}, "4 K proxy": dict(cryo=(0.15, 2.0)), "4 K high": dict(cryo=(0.20, 2.0))}
    M.conditions = lambda: conds
    M.sets = lambda: {"gf180": [(d, c, 20, False) for d in M.DESIGNS for c in conds]}
    return H, M


def run(full=False, tgmin=False):
    """full: the NMOS switch over the whole 0.3 to 1.5 V range, which its 3.3 V gate drive passes in GF180.
    tgmin: the TG at 0.42 um (PMOS 0.84 um), the width at which the SKY130 TG passes."""
    _, M = configure()
    if tgmin:
        M.DESIGNS["GF180 TG, no ESD, W 0.42"] = dict(M.DESIGNS["GF180 TG, no ESD"], wn=0.42)
        conds = M.conditions()
        M.sets = lambda: {"tgmin": [("GF180 TG, no ESD, W 0.42", c, 20, False) for c in conds]}
        M.simulate(["tgmin"])
    elif full:
        M.R.E.NMOS_ONLY = tuple(a for a in M.R.E.NMOS_ONLY if a != "NSW")
        M.DESIGNS["GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V"] = dict(M.DESIGNS["GF180 NMOS, 0.3 V underdrive"])
        conds = M.conditions()
        M.sets = lambda: {"full": [("GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V", c, 20, False) for c in conds]}
        M.simulate(["full"])
    else:
        M.simulate(["gf180"])
    M.collect()


def analyse():
    sys.path.insert(0, str(ROOT / "studies"))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import operational_budget as common
    import cell_margins as CM
    import array_yield as Y
    recs = json.loads((OUT / "gf180_pedestals.json").read_text(encoding="utf-8"))
    B = CM.RA.budgets()
    old = json.loads((OUT / "gf180.json").read_text(encoding="utf-8")) if (OUT / "gf180.json").exists() else {}
    out = {}
    for name, rec in sorted(recs.items()):
        if name in old and old[name]["n"] == len(rec["peds"]):      # analysed before with the same channels
            out[name] = old[name]
            continue
        _, r = CM.analyse_one((name, rec, B))
        x, v, std, nominal, _ = CM.prepare(rec)
        A = CM.residual_operator(v, std)
        m, s = Y.moments(x, v, std, A, nominal, "full")
        r["p_array"] = Y.p_array(Y.p_channel(m, s, B[common.WORST])[0])
        r["pedestal_nominal_range"] = [float(np.min(rec["nominal"])), float(np.max(rec["nominal"]))]
        out[name] = r
    (OUT / "gf180.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    W = common.WORST
    L = ["## GF180MCU (180 nm bulk, 3.3 V devices): worst-channel margins, 20 channels", "",
         "| design | condition | window (V) | common residual (µV) | mismatch residual sd (µV) | per channel, 99.99 % [90 %] | shared, 99.99 % [90 %] | P(array) | per channel, 99.9 %, 10 dec/V | move 50 mV |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in out.items():
        d, c = name.split("|")
        f = lambda k: f"{r['margin'][k]:.2f} [{r['ci90'][k][0]:.2f}, {r['ci90'][k][1]:.2f}]"  # noqa: E731
        L.append(f"| {d} | {c} | {r['window'][0]:.2f}-{r['window'][1]:.2f} | {r['common_residual_max'] * 1e6:.1f} | "
                 f"{r['mismatch_residual_sd_max'] * 1e6:.2f} | {f(f'{W}|full|mixed')} | {f(f'{W}|shared|mixed')} | "
                 f"{r['p_array']:.1e} | {r['margin'][f'{common.REF}|full|mixed']:.1f} | {r['margin'][f'{W}|move50mV|mixed']:.1f} |")
    (OUT / "gf180.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("written results_gf180.md")


if __name__ == "__main__":
    {"run": run, "full": lambda: run(True), "tgmin": lambda: run(tgmin=True), "analyse": analyse}[sys.argv[1]]()
