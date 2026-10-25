"""Temperature and corner robustness of the single-cell and co-simulation conclusions.

No validated 4 K SKY130 model exists. Temperature therefore enters in two separate ways, each as a
band, never as a 4 K prediction:

1. **Switching: a cryogenic proxy on the SKY130 FET models** (flow/pdk.py, `cryo=(dV_T, mu)`):
   every FET's |V_T| raised by dV_T and its mobility scaled by mu, in every bin, in the manner of
   the Beall 2026 77 K refit of SKY130 (VTH0 and U0 multipliers). Run at 27 C, so the BSIM4
   temperature equations are not extrapolated. Bands:
       300 K        PDK models
       77 K proxy   dV_T = +0.10 V, mu x 1.7   (Beall 2026, SKY130 LVT at 77 K: VTH0 x 1.29, U0 x 1.7)
       4 K proxy    dV_T = +0.15 V, mu x 2.0   (Incandela 2018, 160 nm bulk at 4 K: V_T +~30 %, mobility ~2x;
                                               Beckers 2018, 28 nm bulk at 4.2 K: dV_T ~0.1 V, up to 0.2 V)
       4 K high     dV_T = +0.20 V, mu x 2.0   (upper edge, Beckers 2018 long-channel pMOS)
       77 K Beall fit, 4 K Beall pMOS          (the measured pMOS shift of Beall 2026, see beall_check.py)
   The 4 K proxy is also run at every process corner. Measured per design: pedestal and its residual
   after a per-channel linear calibration, the voltage range the switch can pass (track error),
   refresh transient and crosstalk fed to the CZ model, settling time constant, off capacitance.
2. **Leakage: a band, not a model.** At 4 K subthreshold and junction leakage collapse by many
   orders of magnitude and what remains (tunnelling, ESD, interface defects) is not in the SKY130
   models. The PDK models are run from 27 C down to -196 C as a trend (qualified to -40 C only), and
   the 4 K droop is taken from measured cryo-CMOS S/H and demultiplexer chips. Hold time and
   electrodes per line are then given as functions of the droop rate, with those anchors marked.
3. **ESD pulse distortion against temperature**: the co-simulation of a TG with a 100 um^2 ESD pair
   at 27, -40 and -196 C (the diode models' own temperature dependence).

Run:  python studies/cryogenic.py          (about 20 min on 24 threads; writes results/cryogenic.json)
      python studies/cryogenic.py quick    (one design, about 2 min)
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import design_space as E  # noqa: E402  (qubit-side helpers: StaticCurve, base_cfg)
from flow import budget as B  # noqa: E402
from flow import cosim as C  # noqa: E402
from flow import holdstage as H  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
WORK = Path("build/cryogenic")
THREADS = 24

BANDS = {"300 K": None, "77 K proxy": (0.10, 1.7), "4 K proxy": (0.15, 2.0), "4 K high": (0.20, 2.0),
         # bands from the Beall 2026 cross-check (studies/beall_check.py): the proxy fitted to the
         # 77 K SKY130 LVT model (nMOS, L 0.15 um) and to the measured 77 K data (pMOS, L 0.35 um), whose
         # threshold rises far more than the bulk literature suggests. (dV_T_n, mu_n, mm, dV_T_p, mu_p)
         "77 K Beall fit": (0.10, 2.5, 1.0, 0.80, 3.0),
         "4 K, Beall pMOS": (0.15, 2.0, 1.0, 0.80, 3.0)}
CORNERS = ("tt", "ff", "ss", "fs", "sf")
CORNER_BAND = "4 K proxy"
TEMPS = (27.0, -40.0, -100.0, -160.0, -196.0)

# the designs of the temperature study (C_node = 1 pF), with the plain TG with ESD as the reference
DESIGNS = {
    "NMOS, 0.3 V underdrive": dict(arch="NSW", wn=0.42, esd_area=0.0, v_underdrive=0.3),
    "bootstrapped, 0.3 V underdrive": dict(arch="BOOT", wn=0.42, esd_area=0.0, v_underdrive=0.3),
    "bootstrapped (transistor level), 0.3 V underdrive": dict(arch="BOOTT", wn=0.42, esd_area=0.0, v_underdrive=0.3),
    "T-switch + OTA buffer": dict(arch="TSWO", wn=0.84, esd_area=0.0, i_buf=1e-9),
    "TG + dummies": dict(arch="TGD", wn=1.0, esd_area=0.0),
    "TG, no ESD": dict(arch="TG", wn=1.0, esd_area=0.0),
    "TG, ESD on the node": dict(arch="TG", wn=1.0, esd_area=100.0),
}

# Measured droop of cryo-CMOS S/H and demultiplexer chips (V/s), the 4 K anchors of the leakage band
ANCHORS = {
    "van Staveren 2025, 4 K demux (ESD-dominated), typical": 3.1e-3,
    "van Staveren 2025, range low": 60e-6,
    "van Staveren 2025, range high": 18e-3,
    "Jadot 2023, 4 K active router, max": 0.44e-6,
    "Darnas 2026, S/H at 0.5 K, 1.5 V": 5.5e-6,
}
SLOPES = (10.0, 33.69)
TARGETS = (1e-3, 1e-4)


TRACK_TOL = 0.1e-3       # V: tracking error below the settling allowance (eps = 137 uV)
MM_SCALES = (1.0, 1.5, 2.0)   # V_T mismatch at 4 K against the PDK's 300 K values: sensitivity, not sourced
N_MC = 12


def track_limit(m, tol=TRACK_TOL):
    """Highest held voltage the switch still passes (|track error| < tol), and whether all do."""
    ok = np.abs(m["track_error"]) < tol
    vh = np.asarray(m["v_hold"])
    return (float(vh[ok].max()) if ok.any() else 0.0), bool(ok.all())


def _wd(*parts):
    """A short, stable work directory per point (independent of the job order, so reruns reuse decks)."""
    import hashlib
    return str(WORK / parts[0] / hashlib.md5(repr(parts[1:]).encode()).hexdigest()[:10])


def switching_point(name, kw, band, corner, layers, spec, idx):
    cfg = E.base_cfg(workdir=_wd("switch", name, band, corner), cryo=BANDS[band], corner=corner, **kw)
    rec = {"design": name, "band": band, "corner": corner}
    try:
        m = H.measure(cfg)
        s = {k: float(v) for k, v in H.summarize(cfg, m).items()}
        # settling at mid-range for the NMOS-only switches: near 0.9 V a raised V_T leaves them barely on
        cell = C.cell_params(cfg, v0=0.6 if kw["arch"] in E.NMOS_ONLY else 0.9)
    except Exception as e:
        rec["error"] = str(e).splitlines()[0][:300] if str(e) else repr(e)
        return rec
    vmax, all_pass = track_limit(m)
    # residual over the voltages the switch actually passes
    ok = np.abs(m["track_error"]) < TRACK_TOL
    if ok.sum() >= 3:
        vh, ped = np.asarray(m["v_hold"])[ok], m["pedestal"][ok]
        resid = float(np.max(np.abs(ped - np.polyval(np.polyfit(vh, ped, 1), vh))))
    else:
        resid = float("nan")
    # refresh transient: worst over the voltages the switch passes (elsewhere it never settles at all)
    k = int(np.argmax(np.where(ok, np.abs(m["refresh_glitch"]), -1.0)))
    tr, xr = m["refresh_waves"][k]
    judge = {}
    for sl in SLOPES:
        lay = layers[sl]
        x = lay.t
        refresh = lay.excess_infidelity(np.where(x >= 0, np.interp(x, tr, xr, left=0.0, right=float(xr[-1])), 0.0))
        xtalk = lay.excess_infidelity(np.where(x >= lay.cfg.t_gate / 2, s["feedthrough_max"] * C.V_LINE_SWING, 0.0))
        for tgt in TARGETS:
            sp = spec[(sl, tgt)]
            judge[f"s{sl:g}_t{tgt:g}"] = {"residual_margin": sp / max(resid, 1e-12) if np.isfinite(resid) else 0.0,
                                         "refresh_infidelity": float(refresh), "crosstalk_infidelity": float(xtalk)}
    rec.update(summary=s, cell=cell, v_pass_max=vmax, passes_full_range=all_pass,
               v_hold=list(map(float, m["v_hold"])), track_error=m["track_error"].tolist(),
               pedestal_mv=(m["pedestal"] * 1e3).round(5).tolist(), residual=resid, judge=judge)
    return rec


def leakage_point(name, kw, temp, idx):
    cfg = E.base_cfg(workdir=_wd("leak", name, temp), temp=temp, **kw)
    rec = {"design": name, "temp_c": temp}
    try:
        m = H.measure(cfg)
        s = H.summarize(cfg, m)
        rec.update(droop_max=float(s["droop_max"]), leakage_max=float(s["leakage_max"]),
                   c_eff=float(s["c_eff"]), leak_abstol=float(s["leak_abstol"]))
    except Exception as e:
        rec["error"] = str(e).splitlines()[0][:300] if str(e) else repr(e)
    return rec


def esd_pulse_point(temp, lay, idx):
    cfg = E.base_cfg(arch="TG", wn=1.0, esd_area=100.0, temp=temp, workdir=str(WORK / "esd" / f"t{idx}"))
    res, cal, _ = C.cosim(cfg, lay, E.v_targets("TG"), mux=C.MuxConfig(t_gap=50e-9))
    return {"temp_c": temp, "k": cal["k"],
            "f_dyn": [float(lay.excess_infidelity(r["dv"] - r["static"])) for r in res],
            "f_dyn_global_k": [float(lay.excess_infidelity(r["dv"] - r["static"] + r["dv_k"])) for r in res]}


def kickback_point(band, i_buf):
    """OTA buffer kickback under a band: after the refresh opens, the hold node of
    the T-switch + OTA settles as the OTA recovers. Long multiplexed deck, no pulse; returns the shift
    from 3 ns after opening to the final level, and the time to come within 10 uV of it."""
    cfg = E.base_cfg(arch="TSWO", wn=0.84, esd_area=0.0, i_buf=i_buf, cryo=BANDS[band],
                     workdir=_wd("kick", band, i_buf))
    cell = C.cell_params(cfg)
    mux = C.MuxConfig(t_gap=20e-6)
    tg = [0.9, 0.3, 1.2, 0.6]
    deck, tl = C.mux_deck(cfg, mux, tg, tg, cell, 0.137e-3, None)
    w = C.spice.run_ngspice(deck, cfg.workdir, cfg.tag() + "_kick")
    t, v = w["time"], w["v(hold0)"]
    t0 = tl["r2_open"][0]
    final = float(np.mean(v[(t > tl["t_cz"] - 1e-6) & (t <= tl["t_cz"])]))
    early = float(np.interp(t0 + 3e-9, t, v))
    after = (t > t0 + 3e-9) & (t <= tl["t_cz"])
    off = np.abs(v[after] - final) > 10e-6
    t_settle = float(t[after][np.nonzero(off)[0][-1]] - t0) if off.any() else 3e-9
    return {"band": band, "i_buf": i_buf, "kickback": final - early, "t_settle": t_settle,
            "final_minus_target": final - 0.9}


def mismatch_point(name, kw, band, mm, seed):
    """Pedestal under V_T mismatch scaled by mm (shared-calibration case): one Monte Carlo deck."""
    c = BANDS[band] or (0.0, 1.0)
    cryo = (c[0], c[1], mm) + (tuple(c[3:5]) if len(c) > 4 else ())
    cfg = E.base_cfg(workdir=_wd("mm", name, band, mm), cryo=cryo, mismatch=True, seed=seed, **kw)
    try:
        m = H.measure(cfg)
    except Exception as e:
        return {"design": name, "mm": mm, "seed": seed, "error": str(e).splitlines()[0][:200]}
    ok = np.abs(m["track_error"]) < TRACK_TOL
    return {"design": name, "band": band, "mm": mm, "seed": seed, "pedestal": m["pedestal"].tolist(),
            "ok": ok.tolist()}


def run_parallel(jobs, label):
    t0 = time.time()
    out = [None] * len(jobs)
    with ThreadPoolExecutor(THREADS) as ex:
        futs = [ex.submit(f, *a) for f, a in jobs]
        for i, fu in enumerate(futs):
            try:
                out[i] = fu.result()
            except Exception as e:
                out[i] = {"error": repr(e)[:300]}
            if (i + 1) % 10 == 0 or i + 1 == len(jobs):
                print(f"  {label}: {i + 1}/{len(jobs)} ({time.time() - t0:.0f} s)", flush=True)
    return out


def main(quick=False):
    t0 = time.time()
    C.spice.REUSE = C.spice.STRICT = C.spice.RETRY_RELAXED = True
    C.spice.TIMEOUT = 3600
    layers = {s: B.layer(s_dec_per_v=s) for s in SLOPES}
    curves = {s: E.StaticCurve(layers[s]) for s in SLOPES}
    spec = {(s, t): curves[s].allowance(t) for s in SLOPES for t in TARGETS}
    print(f"qubit side done ({time.time() - t0:.0f} s)", flush=True)
    designs = dict(list(DESIGNS.items())[:1]) if quick else DESIGNS
    res = {"bands": {k: v for k, v in BANDS.items()}, "anchors": ANCHORS,
           "spec": {f"s{s:g}_t{t:g}": v for (s, t), v in spec.items()}, "designs": designs}

    jobs, i = [], 0
    for name, kw in designs.items():
        for band in BANDS:
            for corner in (CORNERS if band == CORNER_BAND and not quick else ("tt",)):
                jobs.append((switching_point, (name, kw, band, corner, layers, spec, i)))
                i += 1
    res["switching"] = run_parallel(jobs, "switching")

    jobs = [(leakage_point, (name, kw, T, i)) for i, (name, kw, T) in
            enumerate((n, k, T) for n, k in designs.items() for T in TEMPS)]
    res["leakage"] = run_parallel(jobs, "leakage")

    temps = (27.0,) if quick else (27.0, -40.0, -196.0)
    res["esd_pulse"] = run_parallel([(esd_pulse_point, (T, layers[10.0], i)) for i, T in enumerate(temps)], "esd pulse")

    bands_kick = ("300 K",) if quick else ("300 K", "4 K proxy", "77 K Beall fit", "4 K, Beall pMOS")
    res["kickback"] = run_parallel([(kickback_point, (b, ib)) for b in bands_kick for ib in (1e-9, 10e-9)],
                                   "kickback")

    mm_designs = list(designs)[:1] if quick else [d for d in designs if DESIGNS[d]["arch"] in
                                                  ("NSW", "BOOTT", "TSWO", "TGD")]
    jobs = [(mismatch_point, (d, DESIGNS[d], "4 K proxy", mm, seed)) for d in mm_designs
            for mm in ((1.0,) if quick else MM_SCALES) for seed in range(1, (3 if quick else N_MC) + 1)]
    res["mismatch"] = run_parallel(jobs, "mismatch")

    res["relaxed_runs"] = sorted(set(C.spice.RELAXED_RUNS))
    res["runtime_s"] = time.time() - t0
    (OUT / ("cryogenic_quick.json" if quick else "cryogenic.json")).write_text(json.dumps(res, indent=1, default=float))
    print(f"done in {res['runtime_s']:.0f} s")


if __name__ == "__main__":
    main(quick=len(sys.argv) > 1 and sys.argv[1] == "quick")
