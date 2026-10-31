"""The bootstrapped switch driven through its best tree at the protection-diode droop of a 1 pF node.

At 46.5 mV/s (studies/droop_anchors.py) the best tree of each design is smaller than at 3.1 mV/s, and the
series resistance from the DAC to the far end of a leaf line falls from 22-26 kOhm to 12-14 kOhm. The
bootstrapped switch is the only design whose pedestal depends on that source impedance (NMOS, TGs and
T-switch change by < 5 %, studies/extra_bands.py), so its 20 Monte Carlo rows plus the nominal cell are
simulated in the 4 K band through its own best tree at 46.5 mV/s, with the functions of extra_bands.py.
Margins follow from studies/residual_accounting.py on the pedestals written here.

Run:  python studies/tree_source_1pf.py     (resumable; writes results/tree_source_1pf_channels.jsonl and
      results/tree_source_1pf_pedestals.json)
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import extra_bands as E  # noqa: E402

DESIGN = "bootstrapped (transistor level), 0.3 V underdrive"
VARIANT = "4 K, tree, ESD diodes on 1 pF"
LOG = OUT / "tree_source_1pf_channels.jsonl"
N_MC = 20


def best_tree_1pf(design, which):
    a = json.loads((OUT / "droop_anchors.json").read_text(encoding="utf-8"))
    row = next(r for r in a["rows"] if r["design"] == design and r["anchor"].startswith("ESD-dominated"))
    f, w = row["config"][1:].split("_w")
    return float(f), float(w), float(row["tree_n"]["2e-09"])


def main():
    E.variants = lambda: {VARIANT: dict(cryo=E.BAND_4K, tree="esd1pf")}
    E.best_tree = best_tree_1pf
    E.LOG = LOG
    E.C.spice.REUSE = E.C.spice.STRICT = E.C.spice.RETRY_RELAXED = True
    E.C.spice.TIMEOUT = 14400
    print("tree source:", E.tree_source(DESIGN, *best_tree_1pf(DESIGN, "esd1pf")), flush=True)
    done = E.load_log()
    jobs = [(DESIGN, VARIANT, s) for s in range(0, N_MC + 1) if (DESIGN, VARIANT, s) not in done]
    t0 = time.time()
    with ThreadPoolExecutor(21) as ex:
        for i, _ in enumerate(ex.map(lambda j: E.run_one(*j), jobs)):
            print(f"  {i + 1}/{len(jobs)} ({time.time() - t0:.0f} s)", flush=True)
    log = E.load_log()
    nom = log[(DESIGN, VARIANT, 0)]
    rows = [log[(DESIGN, VARIANT, s)] for s in range(1, N_MC + 1) if "error" not in log.get((DESIGN, VARIANT, s), {"error": 1})]
    ok = np.array(nom["ok"]) & np.all([r["ok"] for r in rows], axis=0)
    out = {f"{DESIGN}|{VARIANT}": {"v": nom["v_hold"], "peds": [r["pedestal"] for r in rows], "ok": ok.tolist(),
                                   "nominal": nom["pedestal"], "n_pass": int(np.sum(nom["ok"]))}}
    (OUT / "tree_source_1pf_pedestals.json").write_text(json.dumps(out), encoding="utf-8")


if __name__ == "__main__":
    main()
