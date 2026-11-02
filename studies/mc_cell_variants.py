"""Single-cell SPICE runs (as studies/mc_cell.py) for further variants of the 4 K band.

Subcommands (each in its own process, because some rewrite model files):
  body <f>   the body-effect parameters k1 and k2 of every FET scaled by f (0.7 or 1.3), four deciding designs,
             20 channels each.
  tol        numerical tolerance: channels 0 to 10 of the NMOS, bootstrapped and 1 um TG cells with reltol 1e-6,
             reltol 1e-7, or a maximum time step of 5 ps.
  wide       transmission gates sized for settling, 5 to 40 um (PMOS twice as wide), no ESD, on 1 pF, simulated as
             their exact scaled equivalent (a 5 um switch on 1 pF x 5/W from 50 ohm x W/5), nominal cell, every 20 mV
             from 0.3 to 1.5 V, 300 K and 4 K band.
  gfbeta     GF180MCU with the current-factor mismatch of its model file (mis_k, defined per instance but unused in the
             released models) applied through mulu0, four designs, 4 K band, 20 channels, same threshold draws.
  collect    write the pedestal files.

Run:  python studies/mc_cell_variants.py body 0.7 ; ... body 1.3 ; ... tol ; ... wide ; ... gfbeta
"""
import re
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import mc_cell as M  # noqa: E402
from flow import config, pdk  # noqa: E402

M.LOG = OUT / "mc_cell_variants_channels.jsonl"
M.PEDS = OUT / "mc_cell_variants_pedestals.json"
M.WORK = ROOT / "build" / "mc_cell_variants"
M.THREADS = 28

NMOS, BOOT, TGD, TG = ("NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive",
                       "TG + dummies", "TG, no ESD")
DECIDING = (NMOS, BOOT, TGD, TG)
TOL = {"4 K, reltol 1e-6": ("reltol=1e-5", "reltol=1e-6"), "4 K, reltol 1e-7": ("reltol=1e-5", "reltol=1e-7"),
       "4 K, max step 5 ps": None}
WIDE = (5.0, 10.0, 20.0, 40.0)
W_SIM = 5.0
FINE = [round(0.3 + 0.02 * k, 3) for k in range(61)]

_conditions = M.conditions
_tl = threading.local()


def conditions():
    c = _conditions()
    for f in (0.7, 1.3):
        c[f"4 K, body effect x {f:g}"] = dict(cryo=M.BAND_4K)
    for name in TOL:
        c[name] = dict(cryo=M.BAND_4K)
    return c


M.conditions = conditions


def wide_name(w):
    return f"TG sized for settling, W {w:g}"


for _w in WIDE:
    _k = _w / W_SIM
    M.DESIGNS[wide_name(_w)] = dict(arch="TG", wn=W_SIM, esd_area=0.0, c_node=1e-12 / _k, r_src=50.0 * _k)

_grid = M.grid


def grid(design, fine=False):
    return FINE if design.startswith("TG sized for settling") else _grid(design, fine)


M.grid = grid

_measure = M.measure
_run_one = M.run_one


def measure(cfg):
    """As mc_cell.measure, with the tolerance of the condition of this thread applied to the deck."""
    cond = getattr(_tl, "cond", None)
    if cond not in TOL:
        return _measure(cfg)
    H, spice = M.H, M.spice
    tl = H.timeline(cfg)
    name = f"v{cfg.v_hold[0]:g}"
    deck = H.transient_deck(cfg)
    if TOL[cond] is None:
        deck = re.sub(r"(?m)^(\.tran\s+\S+\s+\S+)\s*$", r"\1 0 5e-12", deck)
    else:
        deck = deck.replace(*TOL[cond])
    w = spice.run_ngspice(deck, cfg.workdir, name)
    (Path(cfg.workdir) / f"{name}.raw").unlink(missing_ok=True)
    t, x = w["time"], w["v(hold0)"]
    return H._settled(t, x, tl["t_ped"]) - H._settled(t, x, tl["t_open"] - 0.1e-9), \
        H._settled(t, x, tl["t_open"] - 0.1e-9) - cfg.v_hold[0]


def run_one(design, cond, seed, v):
    _tl.cond = cond
    return _run_one(design, cond, seed, v)


M.measure = measure
M.run_one = run_one


def scale_body(f):
    """The 4 K model files in a build directory of their own, with k1 and k2 of every bin scaled by f."""
    config.BUILD_DIR = ROOT / "build" / "mc_cell_variants" / f"pdk_body{f:g}"
    pat = re.compile(r"^(\+\s*)(k1|k2)(\s*=\s*)([-+0-9.eE]+)(.*)$", re.I)
    for mm in (False, True):
        pdk.write_fet18_lib("tt", "hold", mm, M.BAND_4K)
    n = 0
    for p in config.BUILD_DIR.glob("pdk/*/tt/*.spice"):
        mark = p.with_suffix(".bodyscaled")
        if mark.exists():
            continue
        lines = p.read_text().splitlines()
        for i, line in enumerate(lines):
            m = pat.match(line)
            if m:
                lines[i] = f"{m.group(1)}{m.group(2)}{m.group(3)}{float(m.group(4)) * f:.7g}{m.group(5)}"
                n += 1
        p.write_text("\n".join(lines) + "\n")
        mark.write_text("")
    print(f"{n} body-effect parameters scaled by {f:g} in {config.BUILD_DIR}", flush=True)


def gfbeta():
    import gf180 as G
    src = G.patched_models()
    dst_dir = ROOT / "build" / "mc_cell_variants" / "gf180beta"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "sm141064.ngspice"
    if not dst.exists():
        text = src.read_text(encoding="utf-8")
        n_n = text.count("mulu0='gf_mu_n'")
        n_p = text.count("mulu0='gf_mu_p'")
        text = (text.replace("mulu0='gf_mu_n'", "mulu0='gf_mu_n*(1+mis_k*sw_stat_mismatch*gf_mm)'")
                    .replace("mulu0='gf_mu_p'", "mulu0='gf_mu_p*(1+mis_k*sw_stat_mismatch*gf_mm)'"))
        dst.write_text(text, encoding="utf-8")
        print(f"current-factor mismatch applied to {n_n} NMOS and {n_p} PMOS instances", flush=True)
    G.patched_models = lambda: dst
    H, Mg = G.configure()
    Mg.LOG = OUT / "gf180_current_factor_channels.jsonl"
    Mg.PEDS = OUT / "gf180_current_factor" / "mc_cell_peds.json"
    Mg.PEDS.parent.mkdir(exist_ok=True)
    Mg.WORK = ROOT / "build" / "mc_cell_variants" / "gf_decks"
    conds = {"4 K proxy, current-factor mismatch": dict(cryo=(0.15, 2.0))}
    Mg.conditions = lambda: conds
    Mg.DESIGNS["GF180 TG, no ESD, W 0.42"] = dict(Mg.DESIGNS["GF180 TG, no ESD"], wn=0.42)
    Mg.sets = lambda: {"gfbeta": [(d, c, 20, False) for d in Mg.DESIGNS for c in conds]}
    Mg.simulate(["gfbeta"])
    Mg.collect()


def run(name, s):
    M.sets = lambda: s
    M.simulate([name])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "body":
        f = float(a[1])
        scale_body(f)
        run("body", {"body": [(d, f"4 K, body effect x {f:g}", 20, False) for d in DECIDING]})
    elif a and a[0] == "tol":
        run("tol", {"tol": [(d, c, 10, False) for d in (NMOS, BOOT, TG) for c in TOL]})
    elif a and a[0] == "wide":
        run("wide", {"wide": [(wide_name(w), c, 0, False) for w in WIDE for c in ("300 K", "4 K proxy")]})
    elif a and a[0] == "gfbeta":
        gfbeta()
        sys.exit(0)
    M.collect()
