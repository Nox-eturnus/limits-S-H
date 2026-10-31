"""Pedestal Monte Carlo with one physical cell per channel.

The SKY130 mismatch is drawn per transistor instance (studies/instance_check.py), and the pedestal testbench
of flow/holdstage.py places one switch instance per held voltage, so the held voltages of one Monte Carlo
seed of a multi-voltage deck are independently mismatched cells. A deck with a single cell and a fixed seed,
by contrast, reproduces one cell at every held voltage. Here every channel is one cell: for each seed, one
single-cell deck per held voltage with that seed. Only the switching transient is simulated (pedestal and
tracking error); leakage does not depend on this.

Conditions reuse the bands of studies/cryogenic.py, the variants of studies/extra_bands.py (steep bands,
clock edges, tree sources, mismatch scaling) and the tree at the protection-diode droop of a 1 pF node
(studies/droop_anchors.py). Designs: the six of the temperature study, the nine cells of studies/cells.py as
designed, and sizing variants at equal and minimum widths.

Run:  python studies/mc_cell.py <set> [<set> ...]   (resumable; see sets(); about 10-12 h on 30 threads for all)
      python studies/mc_cell.py                     (collect only)
Appends to results/mc_cell_channels.jsonl; collect writes results/mc_cell_pedestals.json.
"""
import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import cryogenic as R  # noqa: E402
import extra_bands as E3  # noqa: E402
from flow import holdstage as H  # noqa: E402
from flow import spice  # noqa: E402

LOG = OUT / "mc_cell_channels.jsonl"
PEDS = OUT / "mc_cell_pedestals.json"   # written by collect()
WORK = ROOT / "build" / "mc_cell"
THREADS = 30
_lock = threading.Lock()
BAND_4K = R.BANDS["4 K proxy"]

# ---------------------------------------------------------------------------------------------- designs
FIG6 = [d for d in R.DESIGNS if d != "bootstrapped, 0.3 V underdrive"]
SIZING = {   # every architecture at its smallest proper width, and width sweeps of the NMOS switch and TG
    "NMOS, 0.3 V underdrive, W 1": dict(arch="NSW", wn=1.0, esd_area=0.0, v_underdrive=0.3),
    "NMOS, 0.3 V underdrive, W 3": dict(arch="NSW", wn=3.0, esd_area=0.0, v_underdrive=0.3),
    "bootstrapped (transistor level), W 1": dict(arch="BOOTT", wn=1.0, esd_area=0.0, v_underdrive=0.3),
    "TG, no ESD, W 0.42": dict(arch="TG", wn=0.42, esd_area=0.0),
    "TG, no ESD, W 3": dict(arch="TG", wn=3.0, esd_area=0.0),
    "TG + dummies, W 0.84": dict(arch="TGD", wn=0.84, esd_area=0.0),   # smallest width with half-size dummies
    "TG, no ESD, W 0.42, 0.3 V underdrive": dict(arch="TG", wn=0.42, esd_area=0.0, v_underdrive=0.3),
    "T-switch + OTA buffer, W 0.42": dict(arch="TSWO", wn=0.42, esd_area=0.0, i_buf=1e-9),
}
NINE_CELLS = {f"D {a}": dict(arch=a) for a in H.ARCHS_D}     # the nine cells of studies/cells.py as designed (wn 1, ESD 100)
DESIGNS = {**R.DESIGNS, **SIZING, **NINE_CELLS}
TREE_PROXY = {   # sizing variants take the tree source of the design they resize (the source barely depends on W)
    **{k: "NMOS, 0.3 V underdrive" for k in SIZING if k.startswith("NMOS")},
    **{k: "TG, no ESD" for k in SIZING if k.startswith("TG")},
    "bootstrapped (transistor level), W 1": "bootstrapped (transistor level), 0.3 V underdrive",
    "T-switch + OTA buffer, W 0.42": "T-switch + OTA buffer",
}


# ------------------------------------------------------------------------------------------- conditions
def conditions():
    c = {"300 K": {}}
    for b, v in R.BANDS.items():
        if v is not None:
            c[b] = dict(cryo=v)
    for name, v in E3.variants().items():
        c[name] = dict(v)
    c["4 K, tree, ESD diodes on 1 pF"] = dict(cryo=BAND_4K, tree="esd1pf")
    c["4 K, buffered leaf line"] = dict(cryo=BAND_4K, tree="buffered")
    for s in SSS_SCALES:                                                     # scaled-sigma sampling
        c.setdefault(f"4 K, mismatch x {s:g}", dict(cryo=BAND_4K[:2] + (s,), mm=s))
    return c


SSS_SCALES = (1.5, 2.0, 2.5, 3.0, 5.3)


def _tree_esd1pf(design):
    a = json.loads((ROOT / "results" / "droop_anchors.json").read_text(encoding="utf-8"))
    row = next(r for r in a["rows"] if r["design"] == design and r["anchor"].startswith("ESD-dominated"))
    f, w = row["config"][1:].split("_w")
    return float(f), float(w), float(row["tree_n"]["2e-09"])


R_BUFFER = 1e3     # a unity-gain buffer at the top of each leaf line, output resistance 1 kOhm


def source(design, tree):
    base = TREE_PROXY.get(design, design)
    if tree == "fixed":
        return E3.tree_source(base)
    if tree in ("esd", "reticle"):
        return E3.tree_source(base, *E3.best_tree(base, tree))
    if tree == "esd1pf":
        return E3.tree_source(base, *_tree_esd1pf(base))
    if tree == "buffered":
        _, c_leaf = E3.tree_source(base, *E3.best_tree(base, "esd"))
        r_leaf = _leaf_wire_r(base)
        return R_BUFFER + r_leaf, c_leaf
    raise ValueError(tree)


def _leaf_wire_r(design):
    """Wire resistance of one 1000-electrode leaf line (metal 2 at the cell pitch), as in flow/cosim.py."""
    from flow import cosim as C
    tree = C.TreeConfig()
    levels = C.tree_levels(1000, tree)
    f, side, _ = levels[-1]
    return tree.r_wire * f * side


def make_cfg(design, cond, seed, v):
    kw = dict(DESIGNS[design])
    cd = conditions()[cond]
    extra = {}
    for k in ("temp", "t_edge"):
        if k in cd:
            extra[k] = cd[k]
    if cd.get("tree"):
        extra["r_src"], extra["c_src"] = source(design, cd["tree"])
    cryo = cd.get("cryo")
    if cryo is not None and "mm" in cd:
        cryo = tuple(cryo[:2]) + (cd["mm"],) + tuple(cryo[3:])
    base = R.E.base_cfg(cryo=cryo, mismatch=seed > 0, seed=max(seed, 1), **kw, **extra)
    wd = WORK / hashlib.md5(repr((design, cond, seed)).encode()).hexdigest()[:12]
    return replace(base, v_hold=(float(v),), workdir=str(wd))


def grid(design, fine=False):
    """Held voltages: the standard seven, plus (fine) 20 mV steps in two windows."""
    base = R.E.base_cfg(**DESIGNS[design])
    v = [round(x, 3) for x in base.v_hold]
    if fine:
        lo = (0.3, 0.6) if base.arch in ("NSW", "NTB") else (0.3, 0.7)
        for a in lo:
            v += [round(a + 0.02 * k, 3) for k in range(1, 10)]
    return sorted(set(v))


def measure(cfg):
    """Pedestal and tracking error of the single cell of cfg (switching transient only)."""
    tl = H.timeline(cfg)
    name = f"v{cfg.v_hold[0]:g}"
    w = spice.run_ngspice(H.transient_deck(cfg), cfg.workdir, name)
    (Path(cfg.workdir) / f"{name}.raw").unlink(missing_ok=True)   # ~3 MB per deck; 30k decks fill the disk
    t, x = w["time"], w["v(hold0)"]
    v_pre = H._settled(t, x, tl["t_open"] - 0.1e-9)
    v_post = H._settled(t, x, tl["t_ped"])
    return v_post - v_pre, v_pre - cfg.v_hold[0]


def run_one(design, cond, seed, v):
    try:
        ped, trk = measure(make_cfg(design, cond, seed, v))
        rec = {"design": design, "cond": cond, "seed": seed, "v": v, "ped": ped, "track": trk}
    except Exception as e:
        rec = {"design": design, "cond": cond, "seed": seed, "v": v, "error": str(e).splitlines()[0][:200]}
    with _lock, LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


def load_log():
    out = {}
    if LOG.exists():
        for line in LOG.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            out[(r["design"], r["cond"], r["seed"], r["v"])] = r
    return out


# ------------------------------------------------------------------------------------------------- sets
STEEP = ("4 K, steep (T_eff 120 K)", "4 K, steep (T_eff 30 K)", "4 K, steep (T_eff 20 K)")
BANDS6 = ("300 K", "77 K proxy", "4 K proxy", "4 K high", "77 K Beall fit", "4 K, Beall pMOS")
TREES = ("4 K, tree, ESD-dominated droop", "4 K, tree, one reticle")
DECISIVE = ("NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive", "TG + dummies")
# the designs closest to a margin of one in the 4 K band after the 20-channel run (TG 1.11, TG with ESD 1.25),
# and the bootstrapped switch
HUNDRED = ("TG, no ESD", "TG, ESD on the node", "bootstrapped (transistor level), 0.3 V underdrive")


def sets():
    """name: list of (design, condition, n_channels, fine grid)."""
    s = {
        # Figure 6 and Table S6: six designs, six bands + the calibrated steep band + two tree sources;
        # the 4 K band on the fine grid
        "fig6": [(d, c, 20, c == "4 K proxy") for d in FIG6 for c in BANDS6 + (STEEP[0],) + TREES],
        # Table S7: the decisive designs in the further variants
        "s7": [(d, c, 20, False) for d in DECISIVE for c in STEEP[1:] + ("4 K, clock edge 600 ps",
               "4 K, clock edge 67 ps", "4 K, tree source", "4 K, mismatch x 1.5", "4 K, mismatch x 2")]
              + [("bootstrapped (transistor level), 0.3 V underdrive", "4 K, tree, ESD diodes on 1 pF", 20, False)],
        # the nine cells of studies/cells.py at room temperature
        "s3": [(d, "300 K", 20, False) for d in NINE_CELLS],
        # equal sizing, 4 K band and the tree of 3.1 mV/s
        "sizing": [(d, c, 20, False) for d in SIZING for c in ("4 K proxy", TREES[0])],
        # 100 channels for the designs whose verdict lies near one (selected after the 20-channel run)
        # (fine grid, as the 20 channels of "fig6" in the same band, so that collect() keeps all 100)
        "hundred": [(d, "4 K proxy", 100, True) for d in HUNDRED],
        # buffered leaf line for the bootstrapped switch
        "buffer": [("bootstrapped (transistor level), 0.3 V underdrive", "4 K, buffered leaf line", 20, False)],
        # scaled-sigma sampling of the NMOS switch (studies/high_sigma.py, one cell per channel)
        "sss": [("NMOS, 0.3 V underdrive", f"4 K, mismatch x {s:g}", 20, False) for s in SSS_SCALES],
    }
    return s


def jobs_for(names):
    out = []
    for n in names:
        for d, c, nch, fine in sets()[n]:
            for seed in range(0, nch + 1):                   # seed 0 = nominal cell
                for v in grid(d, fine):
                    out.append((d, c, seed, v))
    return list(dict.fromkeys(out))


def simulate(names):
    spice.SPICEINIT = spice.SPICEINIT.replace("num_threads=4", "num_threads=1")   # one small deck per thread
    spice.REUSE = spice.STRICT = spice.RETRY_RELAXED = True
    spice.TIMEOUT = 14400
    done = load_log()
    jobs = [j for j in jobs_for(names) if j not in done or "error" in done[j]]
    print(f"{len(jobs)} single-cell decks to run ({len(done)} logged)", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(THREADS) as ex:
        for i, _ in enumerate(ex.map(lambda j: run_one(*j), jobs)):
            if (i + 1) % 200 == 0 or i + 1 == len(jobs):
                el = time.time() - t0
                print(f"  {i + 1}/{len(jobs)} ({el:.0f} s, ~{el / (i + 1) * (len(jobs) - i - 1) / 60:.0f} min left)",
                      flush=True)


def collect():
    """Pedestals per design and condition: rows = channels (seeds), columns = held voltages."""
    log = load_log()
    keys = {}
    for (d, c, s, v), r in log.items():
        keys.setdefault((d, c), {}).setdefault(s, {})[v] = r
    out = {}
    for (d, c), by_seed in keys.items():
        if 0 not in by_seed:
            continue
        vs = sorted(by_seed[0])
        seeds = [s for s in sorted(by_seed) if s > 0 and all(v in by_seed[s] and "error" not in by_seed[s][v] for v in vs)]
        if len(seeds) < 10 or any("error" in by_seed[0][v] for v in vs):
            continue
        ped = np.array([[by_seed[s][v]["ped"] for v in vs] for s in seeds])
        trk = np.array([[by_seed[s][v]["track"] for v in vs] for s in seeds])
        nom = by_seed[0]
        out[f"{d}|{c}"] = {"v": vs, "peds": ped.tolist(), "track": trk.tolist(), "seeds": seeds,
                           "nominal": [nom[v]["ped"] for v in vs],
                           "ok_nominal": [abs(nom[v]["track"]) < R.TRACK_TOL for v in vs],
                           "ok_all": (np.abs(trk) < R.TRACK_TOL).all(0).tolist()}
    PEDS.write_text(json.dumps(out), encoding="utf-8")
    print(f"{len(out)} design-condition pairs written", flush=True)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "collect"]
    if args:
        simulate(args)
    collect()
