"""Co-simulation and design-space exploration of S/H gate drivers.

Four parts, all written to results/design_space.json (design_space_report.py turns it into tables
and figures):

1. **Co-simulation** (flow/cosim.py). Real SPICE waveforms of a multiplexed DAC line (4 cells, cell 0
   pulsed through C_pulse, cell 1 refreshed at mid-gate) are fed through the CZ model after in-situ
   calibration. Checks the combination rule of the error terms: deterministic offsets add in the
   adiabatic phases, not as infidelities.
2. **Pulse-coupling table.** The capacitive CZ pulse on a node whose junction capacitance depends on
   voltage (the ESD diodes) is distorted; this cannot be seen without the real waveform. Infidelity
   of the dynamic part of the real waveform, per (C_node, ESD area), at s = 10 dec/V.
3. **Design grid.** Every architecture over W, C_node, ESD area, underdrive (TSWO: buffer current):
   the single-cell error terms plus cell parameters (settling, line loading, clock energy, buffer
   power) and an area estimate. Gives hold time, infidelity at a given refresh period, power per
   electrode.
4. **Scaling.** Electrodes per DAC line at 99.9 % (and 99.99 %), against C_node, switch type and
   exchange slope, for a flat line and for a tree demultiplexer, with and without idle-time Stark
   drift.

Run:  python studies/design_space.py            (about 30-40 min on 24 threads)
      python studies/design_space.py quick      (a few points, about 3 min)
      python studies/design_space.py metrics    (re-derive the metrics from the stored SPICE results)
"""
import json
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flow import budget as B  # noqa: E402
from flow import cosim as C  # noqa: E402
from flow import holdstage as H  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
WORK = Path("build/design_space")
THREADS = 24
SLOPES = (3.87, 10.0, 33.69)
TARGETS = (1e-3, 1e-4)
REF = (10.0, 1e-3)                       # reference point of the error budget
NMOS_ONLY = ("NSW", "NTB")
GRID_ARCHS = ("NSW", "TG", "TGD", "BOOT", "TSW", "TGH", "TSWB", "NTB", "TSWO", "BOOTT")   # CLK = TG + C_pulse
GRID = dict(wn=(0.42, 1.0, 3.0), c_node=(70e-15, 200e-15, 1e-12, 3e-12, 15e-12), esd_area=(0.0, 10.0, 100.0))
UNDERDRIVE = (0.0, 0.3)
I_BUF = (1e-9, 10e-9)                    # TSWO: buffer current instead of underdrive
N_REF_LINE = 1000                        # electrodes on the line for the per-refresh line energy
V_LINE_AVG = 0.4                         # mean |line swing| for uniform targets over 0.3-1.5 V
T_REFRESH_PARETO = 1e-3                  # refresh period of the fidelity-against-area front
IDLE = 1e-6                              # idle per layer for the no-frequency-tracking variant

COSIM_DESIGNS = {
    "TG, ESD on the node": dict(arch="TG", esd_area=100.0),
    "TG, no ESD": dict(arch="TG", esd_area=0.0),
    "TG + dummies, no ESD": dict(arch="TGD", esd_area=0.0),
    "NMOS, 0.3 V underdrive, no ESD": dict(arch="NSW", esd_area=0.0, v_underdrive=0.3),
    "bootstrapped, 0.3 V underdrive, no ESD": dict(arch="BOOT", esd_area=0.0, v_underdrive=0.3),
    "T-switch + OTA buffer, ESD": dict(arch="TSWO", esd_area=100.0),
    "T-switch + OTA buffer, no ESD": dict(arch="TSWO", esd_area=0.0),
    "bootstrapped (transistor level), 0.3 V underdrive, no ESD": dict(arch="BOOTT", esd_area=0.0, v_underdrive=0.3),
}
COSIM_SLOPE_DESIGNS = ("TG, ESD on the node", "T-switch + OTA buffer, no ESD")


def v_targets(arch, slope=10.0):
    """Held voltages: the pulse rides on top, so V + peak pulse must stay below VDD (1.8 V)."""
    if arch in NMOS_ONLY:
        return (0.3, 0.45, 0.6, 0.75, 0.9)
    return (0.3, 0.6, 0.9, 1.2, 1.5) if slope >= 10 else (0.3, 0.5, 0.7, 0.9, 1.1)


def base_cfg(**kw):
    arch = kw.get("arch", "TG")
    cfg = H.HoldConfig(**kw)
    if arch in NMOS_ONLY:
        cfg = replace(cfg, v_hold=tuple(np.round(np.linspace(0.3, 0.9, 7), 3)))
    return cfg


# ==================================================================================== qubit side

class StaticCurve:
    """Excess infidelity of a static barrier offset (J + Stark, exact numerics), tabulated."""

    def __init__(self, layer):
        self.layer = layer
        x = np.concatenate([-np.geomspace(20e-3, 1e-7, 120), [0.0], np.geomspace(1e-7, 20e-3, 120)])
        self.x = x
        self.f = np.array([layer.excess_infidelity(B.static(layer, v)) for v in x])

    def __call__(self, dv):
        return np.interp(dv, self.x, self.f)

    def allowance(self, target):
        """Largest |offset| (worse sign) with infidelity <= target."""
        if target <= 0:
            return 0.0
        out = []
        for sgn in (1, -1):
            m = (np.sign(self.x) == sgn)
            xs, fs = np.abs(self.x[m]), self.f[m]
            o = np.argsort(xs)
            xs, fs = xs[o], fs[o]
            k = np.nonzero(fs > target)[0]
            if not k.size:
                out.append(xs[-1])
                continue
            i = k[0]
            out.append(np.interp(target, fs[i - 1:i + 1], xs[i - 1:i + 1]) if i else 0.0)
        return float(min(out))


def qubit_side():
    layers, curves, spec = {}, {}, {}
    for s in SLOPES:
        for idle in (0.0, IDLE):
            lay = B.layer(s_dec_per_v=s, t_idle=idle)
            layers[(s, idle)] = lay
            curves[(s, idle)] = StaticCurve(lay)
            for tgt in TARGETS:
                spec[(s, idle, tgt)] = curves[(s, idle)].allowance(tgt)
    return layers, curves, spec


# ==================================================================================== design metrics

def design_metrics(row, curves, spec, pulse_tab):
    """Hold time, infidelity at a refresh period, power, from one grid row (in place)."""
    s, c = row["summary"], row["cell"]
    resid = s["pedestal_linear_residual"]
    droop = s["droop_max"]
    f_pulse = pulse_tab.get(f"{row['config']['c_node']:.3g}_{row['config']['esd_area']:g}", np.nan)
    e_line = (10e-12 + N_REF_LINE * c["c_line_cell"]) * V_LINE_AVG * 1.8
    e_node = s["c_eff"] * droop * 1e-3 * 1.8            # top-up after 1 ms of droop (negligible)
    row["energy"] = {"e_clk": c["e_clk"], "e_line_share": e_line, "e_refresh": c["e_clk"] + e_line + e_node,
                     "p_static": c["p_static"]}
    m = {}
    for (sl, idle, tgt), S in spec.items():
        key = f"s{sl:g}_t{tgt:g}" + ("_idle" if idle else "")
        curve = curves[(sl, idle)]
        fp = f_pulse if (np.isfinite(f_pulse) and sl == REF[0] and not idle) else 0.0
        allow = curve.allowance(tgt - fp) if tgt > fp else 0.0
        bd = C.hold_budget(allow, resid, eps_frac=0.1 * S / max(allow, 1e-12), centred=True)
        hold = bd / max(droop, 1e-30)
        m[key] = {"allow": allow, "droop_budget": bd, "hold_time": hold,
                  "n_flat": C.n_max(hold, c, S, bd, C.LineConfig()) if c["tau_node"] > 0 else 0.0,
                  "n_tree": C.n_max(hold, c, S, bd, C.LineConfig(c_line_fixed=10e-12 + 1000 * c["c_line_cell"]))
                  if c["tau_node"] > 0 else 0.0}
    row["metrics"] = m
    # infidelity at a 1 ms refresh period (centred droop) at the reference point, pulse included
    curve = curves[(REF[0], 0.0)]
    worst = abs(resid) + 0.5 * droop * T_REFRESH_PARETO
    row["infidelity_1ms"] = float(max(curve(worst), curve(-worst)) + (f_pulse if np.isfinite(f_pulse) else 0.0))
    row["f_pulse"] = float(f_pulse) if np.isfinite(f_pulse) else None
    row["area"] = C.area_um2(H.HoldConfig(**{k: v for k, v in row["config"].items()}))
    return row


def grid_point(i, kw):
    cfg = base_cfg(workdir=str(WORK / "grid" / f"p{i}"), **kw)
    rec = {"config": {k: v for k, v in asdict(cfg).items() if k not in ("extra", "v_hold", "workdir")}}
    try:
        m = H.measure(cfg)
        rec["summary"] = {k: float(v) for k, v in H.summarize(cfg, m).items()}
        rec["cell"] = C.cell_params(cfg)
    except Exception as e:
        rec["error"] = str(e).splitlines()[0][:300] if str(e) else repr(e)
    return rec


def grid_jobs(quick=False):
    jobs = []
    archs = ("TG", "TSWO") if quick else GRID_ARCHS
    for arch in archs:
        for wn in ((1.0,) if quick else GRID["wn"]):
            for c in ((1e-12,) if quick else GRID["c_node"]):
                for esd in ((0.0, 100.0) if quick else GRID["esd_area"]):
                    extra = [{"i_buf": ib} for ib in I_BUF] if arch == "TSWO" else \
                        [{"v_underdrive": u} for u in UNDERDRIVE]
                    for x in (extra[:1] if quick else extra):
                        w = wn * 2 if arch in ("TSW", "TSWB", "TSWO") else wn   # thick oxide: wider
                        jobs.append(dict(arch=arch, wn=w, c_node=c, esd_area=esd, **x))
    return jobs


# ==================================================================================== pulse-coupling table

def pulse_point(c_node, esd, lay, curve):
    """Dynamic part of the real waveform (pulse distortion + crosstalk) for a TG cell, s = 10."""
    cfg = base_cfg(arch="TG", c_node=c_node, esd_area=esd,
                   workdir=str(WORK / "pulse" / f"c{c_node * 1e15:g}_esd{esd:g}"))
    res, cal, _ = C.cosim(cfg, lay, v_targets("TG"), mux=C.MuxConfig(t_gap=50e-9))
    f_dyn = [lay.excess_infidelity(r["dv"] - r["static"]) for r in res]
    f_dyn_globalk = [lay.excess_infidelity(r["dv"] - r["static"] + r["dv_k"]) for r in res]
    return {"c_node": c_node, "esd_area": esd, "f_dyn": f_dyn, "f_dyn_global_k": f_dyn_globalk,
            "k": cal["k"], "f_pulse": float(max(f_dyn))}


# ==================================================================================== co-simulation set

def cosim_design(name, kw, slope, lay, curve, mux=C.MuxConfig()):
    tag = list(COSIM_DESIGNS).index(name)
    cfg = base_cfg(workdir=str(WORK / "cosim" / f"s{slope:g}" / f"d{tag}"), **kw)
    t0 = time.time()
    res, cal, cell = C.cosim(cfg, lay, v_targets(kw["arch"], slope), mux=mux)
    m = H.measure(cfg)
    droop = np.abs(m["droop"]).max(axis=0)                       # worst line state, per held voltage
    vh = np.array(cfg.v_hold)
    S = curve.allowance(1e-3)
    rows = []
    for r in res:
        rate = float(np.interp(r["target"], vh, droop))
        static, dyn = r["static"], r["dv"] - r["static"]
        f_s, f_r = curve(static), lay.excess_infidelity(dyn)
        # droop offsets: centred (pre-offset by half the droop over one period), at the end of a
        # period that uses half the remaining static budget, and at the full budget
        # add droop offsets of either sign, half and all of the static budget left by the static part
        # Three combination rules against the real waveform:
        #   independent      infidelities add (valid for independent random errors)
        #   coherent         static offsets add as voltages, the dynamic part adds in infidelity
        #   phase-additive   every deterministic term adds in the adiabatic phases (linearised)
        ph_s, ph_r = lay.phase_errors(B.static(lay, static)), lay.phase_errors(dyn)
        comp = []
        for frac in (0.5, 1.0):
            for sgn in (+1, -1):
                dd = sgn * frac * max(S - abs(static), 0.0)
                ph = ph_s + ph_r + lay.phase_errors(B.static(lay, dd))
                comp.append({"droop_offset": dd, "f_real": float(lay.excess_infidelity(r["dv"] + dd)),
                             "f_coherent": float(curve(static + dd) + f_r),
                             "f_independent": float(f_s + curve(dd) + f_r),
                             "f_phase_additive": B.phase_infidelity(ph)})
        rows.append({"target": r["target"], "static": static, "infidelity": r["infidelity"],
                     "infidelity_global_k": float(lay.excess_infidelity(r["dv"] + r["dv_k"])),
                     "f_static": float(f_s), "f_dynamic": float(f_r), "droop_rate": rate,
                     "k_t": r["k_t"], "composition": comp,
                     "dv_trace": r["dv"][::20].round(7).tolist()})
    return {"name": name, "config": kw, "slope": slope, "cal": cal, "cell": cell, "points": rows,
            "t_slot": res[0]["timeline"]["t_slot"], "runtime_s": time.time() - t0,
            "t_trace": lay.t[::20].tolist()}


# ==================================================================================== main

def run_parallel(fun, jobs, threads=THREADS, label=""):
    t0 = time.time()
    out = [None] * len(jobs)
    with ThreadPoolExecutor(threads) as ex:
        futs = {ex.submit(fun, *j if isinstance(j, tuple) else (j,)): i for i, j in enumerate(jobs)}
        for n, f in enumerate(futs):
            i = futs[f]
            try:
                out[i] = f.result()
            except Exception as e:
                out[i] = {"error": f"{e!r}", "trace": traceback.format_exc()[-800:], "job": str(jobs[i])}
            if (n + 1) % 25 == 0 or n + 1 == len(jobs):
                print(f"  {label}: {n + 1}/{len(jobs)} ({time.time() - t0:.0f} s)", flush=True)
    return out


def main(quick=False):
    t0 = time.time()
    C.spice.REUSE = True       # resume: decks already simulated (unchanged netlist, complete raw) are reused
    C.spice.STRICT = True      # an aborted ngspice run is a failure, not a truncated waveform
    C.spice.TIMEOUT = 3600     # 15 pF decks take > 15 min each under 24-way parallel load
    C.spice.RETRY_RELAXED = True   # ... retried once with reltol 1e-4 (listed in results['relaxed_runs'])
    layers, curves, spec = qubit_side()
    lay, curve = layers[(REF[0], 0.0)], curves[(REF[0], 0.0)]
    print(f"qubit side done ({time.time() - t0:.0f} s)", flush=True)
    res = {"spec": {f"s{s:g}_t{t:g}" + ("_idle" if i else ""): v for (s, i, t), v in spec.items()},
           "settings": {"grid": GRID, "underdrive": UNDERDRIVE, "i_buf": I_BUF, "n_ref_line": N_REF_LINE,
                        "t_refresh_pareto": T_REFRESH_PARETO, "idle": IDLE, "line": asdict(C.LineConfig()),
                        "mux": asdict(C.MuxConfig()), "f_pulse": C.F_PULSE}}

    # 1. long-hold check of the droop extrapolation
    lh = []
    for kw, th in ((dict(arch="TSWB", esd_area=100.0), 30e-3), (dict(arch="TSWB", esd_area=0.0), 10.0),
                   (dict(arch="NSW", esd_area=0.0, v_underdrive=0.3), 1.0)):
        cfg = base_cfg(workdir=str(WORK / "longhold"), **kw)
        tr, pr = C.long_hold_check(cfg, th, v=0.6, v_line=0.0)
        lh.append({"config": kw, "t_hold": th, "drift_transient": tr, "drift_leakage": pr})
    res["long_hold"] = lh
    print(f"long-hold checks done ({time.time() - t0:.0f} s)", flush=True)

    # 2. pulse-coupling table (s = 10)
    pts = [(c, e) for c in ((1e-12,) if quick else GRID["c_node"]) for e in ((0.0, 100.0) if quick else GRID["esd_area"])]
    tab = run_parallel(lambda c, e: pulse_point(c, e, lay, curve), pts, label="pulse table")
    res["pulse_table"] = tab
    pulse_tab = {f"{p['c_node']:.3g}_{p['esd_area']:g}": p["f_pulse"] for p in tab if "f_pulse" in p}

    # 3. design grid
    grid = run_parallel(grid_point, list(enumerate(grid_jobs(quick))), label="grid")
    res["grid"] = [design_metrics(r, curves, spec, pulse_tab) if "error" not in r else r for r in grid]

    # 4. co-simulation set
    jobs = [(n, kw, REF[0]) for n, kw in COSIM_DESIGNS.items()]
    if not quick:
        jobs += [(n, COSIM_DESIGNS[n], s) for n in COSIM_SLOPE_DESIGNS for s in SLOPES if s != REF[0]]
    else:
        jobs = jobs[:2]
    res["cosim"] = run_parallel(lambda n, kw, s: cosim_design(n, kw, s, layers[(s, 0.0)], curves[(s, 0.0)]),
                                jobs, label="cosim")

    # 5. slot-time model against the multiplexed SPICE line
    res["slot_check"] = slot_check(lay, quick)
    res["relaxed_runs"] = sorted(set(C.spice.RELAXED_RUNS))
    res["runtime_s"] = time.time() - t0
    (OUT / ("design_space_quick.json" if quick else "design_space.json")).write_text(json.dumps(res, indent=1, default=float))
    print(f"done in {res['runtime_s']:.0f} s")


def slot_check(lay, quick=False):
    """The refresh-slot model (settle the line, then the node) against SPICE: run the multiplexed
    deck with the slot from the model (margin 1) and with a 3x longer slot; the settled levels must
    agree within eps. Large line capacitance stands in for many electrodes."""
    out = []
    for kw in ((dict(arch="TG", esd_area=0.0),) if quick else
               (dict(arch="TG", esd_area=0.0), dict(arch="TSWB", esd_area=0.0), dict(arch="BOOT", esd_area=0.0, v_underdrive=0.3))):
        for c_line in ((100e-12,) if quick else (10e-12, 100e-12, 1e-9)):
            cfg = base_cfg(workdir=str(WORK / "slot" / f"{kw['arch']}_{c_line * 1e12:g}p"), **kw)
            cell = C.cell_params(cfg)
            eps = 0.1 * 1.37e-3
            lv = {}
            for margin in (1.0, 3.0):
                mux = C.MuxConfig(c_line=c_line, margin=margin, t_gap=20e-9)
                tg = [0.9] + C.neighbours(cfg)[1:]
                deck, tl = C.mux_deck(cfg, mux, tg, tg, cell, eps, None)
                name = cfg.tag() + f"_slot{c_line * 1e12:g}p_m{margin:g}"
                try:
                    w = C.spice.run_ngspice(deck, cfg.workdir, name)
                except C.spice.SpiceError:       # "timestep too small": retry once with reltol 1e-4
                    try:
                        w = C.spice.run_ngspice(deck.replace("reltol=1e-5", "reltol=1e-4"), cfg.workdir, name + "_rt")
                    except C.spice.SpiceError as e:
                        lv["error"] = str(e).splitlines()[0][:200]
                        break
                t = w["time"]
                lv[margin] = [float(np.mean(w[f"v(hold{k})"][(t > tl["t_cz"] - 3e-9) & (t <= tl["t_cz"])])) for k in range(4)]
                lv[f"t_slot_{margin:g}"] = tl["t_slot"]
            if "error" in lv:
                out.append({"config": kw, "c_line": c_line, "error": lv["error"]})
                continue
            diff = float(np.max(np.abs(np.array(lv[1.0]) - np.array(lv[3.0]))))
            out.append({"config": kw, "c_line": c_line, "eps": eps, "max_settling_error": diff,
                        "t_slot_model": lv["t_slot_1"], "t_slot_long": lv["t_slot_3"]})
    return out


def recompute_metrics(name="design_space.json"):
    """Re-derive the design metrics (hold time, electrodes per line, power) from the stored SPICE
    measurements, without re-running SPICE (seconds). Use after changing the scaling model."""
    path = OUT / name
    res = json.loads(path.read_text())
    _, curves, spec = qubit_side()
    pulse_tab = {f"{p['c_node']:.3g}_{p['esd_area']:g}": p["f_pulse"] for p in res["pulse_table"] if "f_pulse" in p}
    res["grid"] = [design_metrics(r, curves, spec, pulse_tab) if "error" not in r else r for r in res["grid"]]
    path.write_text(json.dumps(res, indent=1, default=float))
    print(f"metrics recomputed in {path.name}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "metrics":
        recompute_metrics(*(sys.argv[2:3]))
    else:
        main(quick=arg == "quick")
