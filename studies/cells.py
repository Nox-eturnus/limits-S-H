"""Single-cell characterisation of the nine S/H architectures on SKY130 against the error budget.

For every architecture: a nominal point, one-at-a-time sweeps (switch width, node capacitance, clock
edge, corner, temperature, ESD size), and Monte Carlo mismatch. Each measured error is then judged
against the qubit-side budget (flow/budget.py at the reference point of studies/error_budget.py,
exchange and Stark shift):

    residual pedestal   pedestal left after a per-channel linear calibration in the held voltage
                        (max |residual| over 0.3-1.5 V)          -> static budget
    shared calibration  channel-to-channel pedestal spread (MC sigma), if one calibration table
                        serves many electrodes                   -> scatter budget
    kT/C                sqrt(kT/C) at 4 K, refreshed every cycle -> scatter budget
    droop               worst leakage / C (DAC line low or high) -> hold time = static budget / droop
    refresh transient   the node waveform when the switch re-closes, fed to the CZ as if the gate
                        started at that instant (refresh scheduled during a gate: worst case)
    crosstalk           feedthrough of a 1.2 V DAC-line swing (refreshing a neighbour) as a step at
                        mid-gate that lasts to the end of the gate

All transistor models are SKY130 at room temperature (tt, and the PDK's leak corner for droop);
studies/cryogenic.py adds the cryogenic bands. The worst-channel mismatch analysis is in
studies/mismatch.py, which re-reads the Monte Carlo decks this script leaves in build/cells.
Run:  python studies/cells.py   (about 15-20 min; writes results/cells.json)
"""
import json
import sys
import time
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flow import budget as B  # noqa: E402
from flow import holdstage as H  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
SLOPES = (3.87, 10.0, 33.69)
TARGETS = (1e-3, 1e-4)
DV_LINE_SWING = 1.2              # V: DAC line moves between neighbours' values (0.3-1.5 V range)
N_MC = 20

SWEEPS = {
    "wn": (0.42, 1.0, 3.0, 10.0),
    "c_node": (70e-15, 200e-15, 1e-12, 3e-12, 15e-12),
    "t_edge": (50e-12, 200e-12, 1e-9, 5e-9),
    "corner": ("tt", "ff", "ss", "fs", "sf", "leak"),
    "temp": (17.0, 27.0, 37.0),
    "esd_area": (0.0, 10.0, 100.0, 1000.0),
    # droop mitigations (second pass)
    "v_underdrive": (0.0, 0.15, 0.3),
    "l": (0.15, 0.35, 1.0),
    "v_os": (0.0, 1e-3, 10e-3),
}
THICK = ("TSW", "TSWB")                # fixed L = 0.5 um thick-oxide devices
NMOS_ONLY = ("NSW", "NTB")             # pass only up to ~VDD - V_T
COMBINED_GRID = ({"esd_area": 0.0, "v_underdrive": 0.0}, {"esd_area": 0.0, "v_underdrive": 0.3})


def _layers():
    return {s: B.layer(s_dec_per_v=s) for s in SLOPES}


def _spec(layers):
    """Error budget recomputed here so the comparison uses exactly the same model."""
    out = {}
    for s, lay in layers.items():
        for tgt in TARGETS:
            out[(s, tgt)] = {
                "static": min(B.max_static(lay, tgt, +1), B.max_static(lay, tgt, -1)),
                "rms": B.max_static_rms(lay, tgt),
            }
    return out


def _wave_on_grid(lay, tr, xr, t0):
    """Error waveform starting at t0 into the gate; before t0 zero, after the trace its last value."""
    x = lay.t - t0
    dv = np.interp(x, tr, xr, left=0.0, right=float(xr[-1]))
    return np.where(x >= 0, dv, 0.0)


def judge(cfg, m, summ, layers, spec):
    """Per slope and target: margins (spec / measured; > 1 passes) and infidelities."""
    res = {}
    k = int(np.argmax(np.abs(m["refresh_glitch"])))
    tr, xr = m["refresh_waves"][k]
    ft_step = summ["feedthrough_max"] * DV_LINE_SWING
    for s, lay in layers.items():
        refresh_inf = lay.excess_infidelity(_wave_on_grid(lay, tr, xr, 0.0))
        xtalk_inf = lay.excess_infidelity(np.where(lay.t >= lay.cfg.t_gate / 2, ft_step, 0.0))
        for tgt in TARGETS:
            sp = spec[(s, tgt)]
            res[f"s{s:g}_t{tgt:g}"] = {
                "residual_margin": sp["static"] / max(summ["pedestal_linear_residual"], 1e-12),
                "ktc4k_margin": sp["rms"] / summ["ktc_rms_4k"],
                "hold_time_s": sp["static"] / max(summ["droop_max"], 1e-30),
                "refresh_infidelity": refresh_inf,
                "refresh_pass": refresh_inf <= tgt,
                "crosstalk_infidelity": xtalk_inf,
                "crosstalk_pass": xtalk_inf <= tgt,
            }
    return res


def _clean(summ):
    return {k: float(v) for k, v in summ.items()}


def run_point(cfg, layers, spec):
    try:
        m = H.measure(cfg)
    except Exception as e:                      # record and continue (e.g. a size outside the PDK bins)
        print(f"    failed: {cfg.tag()}: {str(e).splitlines()[0]}", flush=True)
        return {"config": {k: v for k, v in asdict(cfg).items() if k not in ("extra", "v_hold", "workdir")},
                "error": str(e)[:500]}
    summ = H.summarize(cfg, m)
    return {"config": {k: v for k, v in asdict(cfg).items() if k not in ("extra", "v_hold", "workdir")},
            "pedestal_mv": (m["pedestal"] * 1e3).round(5).tolist(),
            "summary": _clean(summ),
            "judge": judge(cfg, m, summ, layers, spec)}


def main(archs=H.ARCHS_D, n_mc=N_MC):
    t0 = time.time()
    layers = _layers()
    spec = _spec(layers)
    res = {"spec": {f"s{s:g}_t{t:g}": v for (s, t), v in spec.items()}, "archs": {}}
    for arch in archs:
        base = H.HoldConfig(arch=arch, workdir=f"build/cells/{arch}")
        if arch in NMOS_ONLY:                       # an NMOS alone passes only up to ~VDD - V_T
            base = replace(base, v_hold=tuple(np.round(np.linspace(0.3, 0.9, 7), 3)))
        a = {"nominal": run_point(base, layers, spec), "sweeps": {}, "mc": {}}
        for par, vals in SWEEPS.items():
            if (par == "l" and arch in THICK) or (par == "v_os" and arch not in H.BUFFERED):
                continue
            rows = []
            for v in vals:
                kw = {par: v}
                if arch in THICK and par == "wn":
                    kw = {"wn": v * 2}      # thick oxide: same sweep, wider devices
                rows.append(run_point(replace(base, **kw), layers, spec))
            a["sweeps"][par] = rows
            print(f"  {arch}: sweep {par} done ({time.time() - t0:.0f} s)", flush=True)
        # Best combined droop mitigation for this architecture: no ESD on the hold node (internal
        # node, no pad), with or without 0.3 V underdrive, whichever leaks less
        combos = [run_point(replace(base, **kw), layers, spec) for kw in COMBINED_GRID]
        combos = [c for c in combos if "error" not in c]
        a["combined"] = min(combos, key=lambda c: c["summary"]["droop_max"]) if combos else None
        # Monte Carlo mismatch: each of the 7 instances per deck is an independent channel
        peds, droops = [], []
        for seed in range(1, n_mc + 1):
            try:
                mm = H.measure(replace(base, mismatch=True, seed=seed))
            except Exception as e:
                print(f"    MC seed {seed} failed: {str(e).splitlines()[0]}", flush=True)
                continue
            peds.append(mm["pedestal"])
            droops.append(np.abs(mm["droop"]))
        peds = np.array(peds)                        # (n_mc, n_v)
        a["mc"] = {"pedestal_sigma_mv": (peds.std(axis=0) * 1e3).round(5).tolist(),
                   "pedestal_sigma_max": float(peds.std(axis=0).max()),
                   "droop_max_over_mc": float(np.max(droops)),
                   # channel-to-channel spread of the droop at each held voltage and line state:
                   # what a per-channel droop calibration would have to learn
                   "droop_rel_sigma": float(np.median(np.std(droops, axis=0) / np.mean(droops, axis=0))),
                   "n": int(len(peds))}
        sig = a["mc"]["pedestal_sigma_max"]
        a["mc"]["shared_cal_margin"] = {f"s{s:g}_t{t:g}": spec[(s, t)]["rms"] / sig for s, t in spec}
        res["archs"][arch] = a
        print(f"{arch} done ({time.time() - t0:.0f} s)", flush=True)
    res["runtime_s"] = time.time() - t0
    (OUT / "cells.json").write_text(json.dumps(res, indent=1, default=float))
    print(f"done in {res['runtime_s']:.0f} s")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        main(archs=("TG",), n_mc=2)
    else:
        main()
