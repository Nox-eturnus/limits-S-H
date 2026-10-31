"""Pedestal Monte Carlo in further cryogenic variants (multi-voltage decks, one Monte Carlo seed per row).

20 Monte Carlo channels plus the nominal cell in each variant, for the six designs of the temperature
study in the calibrated steep band and with the two tree sources, and for the three deciding designs
(NMOS, bootstrapped, TG with dummies) otherwise:

  4 K, steep (T_eff 120 K)   4 K band with the subthreshold swing measured at 77 K (studies/subthreshold.py)
  4 K, steep (T_eff 30 K)    4 K band at 15-20 mV/decade, within the range measured on bulk CMOS at 4.2 K
  4 K, steep (T_eff 20 K)    4 K band at about 10-13 mV/decade, near the steepest long-channel bulk devices
  4 K, clock edge 600 ps     4 K band, clock edges three times slower than the 200 ps default
  4 K, clock edge 67 ps      4 K band, clock edges three times faster
  4 K, tree source           4 K band, the cell driven through the path of a tree (series resistance of the
                             DAC, the upper-level switches and all wires, with the leaf-line capacitance at
                             the switch) instead of 50 ohm; fan-out 10, w = 10, 5 x 10^5 electrodes
  4 K, tree, ESD-dominated droop   the same through each design's own best tree at the ESD-dominated
                             droop (studies/system.py), at its electrode count
  4 K, tree, one reticle     the same through each design's best tree at the droop of Darnas et al., at
                             the 1.8 x 10^6 electrodes of one reticle
  4 K, mismatch x 1.5 / x 2  the mismatch sensitivity of studies/cryogenic.py with 20 channels instead of 12
                             (its work directories are reused, so its 12 seeds are not re-simulated)

The testbench places one switch instance per held voltage and the SKY130 mismatch is drawn per instance
(studies/instance_check.py), so one row of these pedestals holds seven independently mismatched cells.
The worst-channel margins of the article use studies/mc_cell.py, which simulates one cell per channel; this
study supplies the nominal cells of Fig. 6b, the variant definitions and the tree sources.

Every result is appended to results/extra_bands_channels.jsonl (resumable); the pedestals are written to
results/extra_bands_pedestals.json.
Run:  python studies/extra_bands.py           (several hours on 28 threads)
      python studies/extra_bands.py collect   (pedestal file only)
"""
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
import mismatch_bands as WB  # noqa: E402
from flow import cosim as C  # noqa: E402
from flow import holdstage as H  # noqa: E402

LOG = OUT / "extra_bands_channels.jsonl"
# the calibrated steep band runs all six designs of Figure 6; the bound and the sensitivity variants run the
# three designs that decide the 99.99 % comparison (runtime: the steep decks are several times slower)
DECISIVE = ("NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive", "TG + dummies")
N_MC = 20
THREADS = 28
_lock = threading.Lock()
BAND_4K = R.BANDS["4 K proxy"]


def best_tree(design, which):
    """Fan-out, switch width and electrode count of the best tree of studies/system.py for a design:
    'esd' at the ESD-dominated droop (its own count), 'reticle' at the droop of Darnas et al., where
    the area of one reticle caps the count."""
    s = json.loads((OUT / "system.json").read_text(encoding="utf-8"))
    anchor = "ESD-dominated" if which == "esd" else "Darnas"
    row = next(r for r in s["rows"] if r["design"] == design and r["anchor"].startswith(anchor))
    best = row["tree"]["2e-09"]
    f, w = best["config"][1:].split("_w")
    n = best["n"] if which == "esd" else min(best["n"], s["n_per_reticle"])
    return float(f), float(w), float(n)


def tree_source(design, fanout=10.0, w_tree=10.0, n=5e5):
    """Series resistance from the DAC to the far end of a leaf line, and the leaf-line capacitance, for a
    tree of the given fan-out and switch width at n electrodes (default: fan-out 10 and w = 10 at
    5 x 10^5 electrodes, the operational count at ESD-dominated droop)."""
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    cell = next(r["cell"] for r in res["switching"] if r and "error" not in r and r["design"] == design
                and r["band"] == "4 K proxy" and r["corner"] == "tt")
    tree = C.TreeConfig(fanout=fanout, w_tree=w_tree)
    r_on = cell["tau_node"] / tree.c_node
    r, c_leaf = tree.r_src, 0.0
    for k, (f, side, leaf) in enumerate(C.tree_levels(n, tree)):
        if k:
            r += r_on / tree.w_tree
        r += tree.r_wire * f * side
        if leaf:
            c_leaf = tree.c_wire * f * side + f * cell["c_line_cell"]
    return float(r), float(c_leaf)


def variants():
    st = json.loads((OUT / "subthreshold.json").read_text(encoding="utf-8"))["bands"]
    v = {}
    for name, band in st.items():
        v[name] = dict(cryo=tuple(band), temp=band[5])
    v["4 K, clock edge 600 ps"] = dict(cryo=BAND_4K, t_edge=600e-12)
    v["4 K, clock edge 67 ps"] = dict(cryo=BAND_4K, t_edge=67e-12)
    v["4 K, tree source"] = dict(cryo=BAND_4K, tree="fixed")
    v["4 K, tree, ESD-dominated droop"] = dict(cryo=BAND_4K, tree="esd")
    v["4 K, tree, one reticle"] = dict(cryo=BAND_4K, tree="reticle")
    v["4 K, mismatch x 1.5"] = dict(cryo=BAND_4K[:2] + (1.5,), mm=1.5)
    v["4 K, mismatch x 2"] = dict(cryo=BAND_4K[:2] + (2.0,), mm=2.0)
    return v


ALL_SIX = ("4 K, steep (T_eff 120 K)", "4 K, tree, ESD-dominated droop", "4 K, tree, one reticle")


def designs_for(vname):
    return WB.FIG6 if vname in ALL_SIX else DECISIVE


def cfg_for(design, vname, seed):
    v = variants()[vname]
    kw = dict(R.DESIGNS[design])
    extra = {}
    if "temp" in v:
        extra["temp"] = v["temp"]
    if "t_edge" in v:
        extra["t_edge"] = v["t_edge"]
    if v.get("tree") == "fixed":
        extra["r_src"], extra["c_src"] = tree_source(design)
    elif v.get("tree"):
        extra["r_src"], extra["c_src"] = tree_source(design, *best_tree(design, v["tree"]))
    mism = seed > 0
    if "mm" in v:            # the work directories of studies/cryogenic.py, so its cached seeds are reused
        wd = R._wd("mm", design, "4 K proxy", v["mm"])
    elif not mism:
        wd = R._wd("r3nom", design, vname)
    else:
        wd = R._wd("r3mc", design, vname)
    return R.E.base_cfg(workdir=wd, cryo=v["cryo"], mismatch=mism, seed=max(seed, 1), **kw, **extra)


def run_one(design, vname, seed):
    cfg = cfg_for(design, vname, seed)
    try:
        m = H.measure(cfg)
        rec = {"design": design, "variant": vname, "seed": seed, "pedestal": m["pedestal"].tolist(),
               "track_error": m["track_error"].tolist(), "v_hold": list(map(float, m["v_hold"])),
               "ok": (np.abs(m["track_error"]) < R.TRACK_TOL).tolist()}
    except Exception as e:
        rec = {"design": design, "variant": vname, "seed": seed, "error": str(e).splitlines()[0][:200]}
    with _lock, LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


def load_log():
    out = {}
    if LOG.exists():
        for line in LOG.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            out[(r["design"], r["variant"], r["seed"])] = r
    return out


def simulate():
    C.spice.REUSE = C.spice.STRICT = C.spice.RETRY_RELAXED = True
    C.spice.TIMEOUT = 14400          # 4 h: the tree-source decks of the NMOS cell are long
    done = load_log()
    jobs = [(d, v, s) for v in variants() for d in designs_for(v) for s in range(0, N_MC + 1)]   # seed 0 = nominal
    jobs = [j for j in jobs if j not in done]
    print(f"{len(jobs)} decks to run, {len(done)} logged", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(THREADS) as ex:
        for i, _ in enumerate(ex.map(lambda j: run_one(*j), jobs)):
            if (i + 1) % 20 == 0 or i + 1 == len(jobs):
                print(f"  {i + 1}/{len(jobs)} ({time.time() - t0:.0f} s)", flush=True)


def collect():
    log = load_log()
    out = {}
    for v in variants():
        for d in designs_for(v):
            nom = log.get((d, v, 0))
            rows = [log[(d, v, s)] for s in range(1, N_MC + 1) if (d, v, s) in log and "error" not in log[(d, v, s)]]
            if not nom or "error" in nom or len(rows) < 10:
                continue
            ok = np.array(nom["ok"]) & np.all([r["ok"] for r in rows], axis=0)
            out[f"{d}|{v}"] = {"v": nom["v_hold"], "peds": [r["pedestal"] for r in rows], "ok": ok.tolist(),
                               "nominal": nom["pedestal"], "n_pass": int(np.sum(nom["ok"]))}
    (OUT / "extra_bands_pedestals.json").write_text(json.dumps(out), encoding="utf-8")
    print(f"{len(out)} design-variant pairs written")


if __name__ == "__main__":
    if "collect" not in sys.argv:
        print({d: (tree_source(d), tree_source(d, *best_tree(d, "esd")), tree_source(d, *best_tree(d, "reticle")))
               for d in WB.FIG6}, flush=True)
        simulate()
    collect()
