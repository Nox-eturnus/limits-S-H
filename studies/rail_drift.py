"""Sensitivity of the pedestal to a drift of the clock and supply rails.

A rail that drifts after tuning shifts the pedestal of every cell clocked from it by the same amount, an error shared
by all channels on that rail, like a drift of the DAC. For the six designs of Figure 6 (nominal cells, 4 K band,
50 ohm source) on 1 pF and on 70 fF, each rail is stepped by +-100 mV with the others fixed:

    VDD     1.8 V: supply and the high level of the thin-oxide clocks (and the off level of the PMOS gates)
    VDDH    3.3 V: thick-oxide clocks and supply (T-switch with OTA, bootstrap network)
    VNEG    -0.3 V underdrive rail (only designs with underdrive; elsewhere the low clock level is ground)

The sensitivity is (P(+100 mV) - P(-100 mV)) / 200 mV at each held voltage (0.3 to 0.7 V for the NMOS switch, its
window on the worst channel; 0.3 to 1.5 V otherwise). Reported: the largest |dP/dV| per design, rail and node.

Run:  python studies/rail_drift.py     (about 15 min on 24 threads; needs ngspice and the PDK; writes
                                        results/rail_drift.{json,md})
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
from flow import holdstage as H  # noqa: E402
import cryogenic as R  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
WORK = ROOT / "build" / "rail_drift"
STEP = 0.1
FIG6 = ["NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive", "T-switch + OTA buffer",
        "TG + dummies", "TG, no ESD", "TG, ESD on the node"]
NODES = {"1 pF": 1e-12, "70 fF": 70e-15}


def rails(d):
    r = ["vdd"]
    if d["arch"] in ("TSWO", "BOOTT", "TSW", "TSWB"):
        r.append("vddh")
    if d.get("v_underdrive", 0.0) > 0:
        r.append("v_underdrive")
    return r


def cfg_for(name, node):
    d = R.DESIGNS[name]
    v = (0.3, 0.4, 0.5, 0.6, 0.7) if d["arch"] == "NSW" else tuple(np.round(np.linspace(0.3, 1.5, 7), 3))
    return replace(H.HoldConfig(), **d, c_node=NODES[node], cryo=R.BANDS["4 K proxy"], v_hold=v,
                   workdir=str(WORK / f"{d['arch']}_{node.replace(' ', '')}"))


def jobs():
    out = []
    for name in FIG6:
        for node in NODES:
            base = cfg_for(name, node)
            for rail in rails(R.DESIGNS[name]):
                for sgn in (+1, -1):
                    # the underdrive rail sits at -v_underdrive: a drift of +step makes it more negative
                    cfg = replace(base, **{rail: getattr(base, rail) + sgn * STEP},
                                  workdir=f"{base.workdir}_{rail}{sgn:+d}")   # the deck name omits the rails
                    out.append((name, node, rail, sgn, cfg))
    return out


def run(job):
    name, node, rail, sgn, cfg = job
    m = H.measure(cfg)
    return name, node, rail, sgn, [float(x) for x in m["pedestal"]], [float(x) for x in m["v_hold"]]


def main():
    res = {}
    with ThreadPoolExecutor(24) as ex:
        for name, node, rail, sgn, ped, vh in ex.map(run, jobs()):
            res.setdefault(name, {}).setdefault(node, {"v_hold": vh})[f"{rail}|{sgn:+d}" if sgn else rail] = ped
            print(f"{name} | {node} | {rail} {sgn:+d}: {np.round(np.array(ped) * 1e6, 1)} uV", flush=True)
    summ = {}
    for name, nodes in res.items():
        for node, r in nodes.items():
            for rail in rails(R.DESIGNS[name]):
                sens = (np.array(r[f"{rail}|+1"]) - np.array(r[f"{rail}|-1"])) / (2 * STEP)
                summ[f"{name}|{node}|{rail}"] = {"max_abs_uV_per_mV": float(np.max(np.abs(sens))) * 1e3,
                                                  "per_voltage_uV_per_mV": [float(x) * 1e3 for x in sens]}
    (OUT / "rail_drift.json").write_text(json.dumps({"step_V": STEP, "raw": res, "summary": summ}, indent=1), encoding="utf-8")
    L = ["# Pedestal sensitivity to the clock and supply rails (4 K band, nominal cells, +-100 mV)", "",
         "Largest |dP/dV_rail| over the held voltages, in uV of pedestal per mV of rail drift.", "",
         "| design | node | rail | max (uV/mV) | per held voltage |", "|---|---|---|---|---|"]
    for k, v in summ.items():
        n, node, rail = k.split("|")
        L.append(f"| {n} | {node} | {rail} | {v['max_abs_uV_per_mV']:.3g} | "
                 + ", ".join(f"{x:.2g}" for x in v["per_voltage_uV_per_mV"]) + " |")
    (OUT / "rail_drift.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
