"""Error budget: barrier-voltage errors that an adiabatic CZ tolerates, against the exchange slope s.

Every entry is the largest error of one kind that, alone, keeps the error added after calibration
at or below 1e-3 (99.9 %) or 1e-4 (99.99 %). Deterministic errors (static offset, glitch) are
solved with the exact propagator and checked against the adiabatic phase model; noise budgets use
the filter-function kernel, which tests/test_budget.py checks against Monte Carlo.

Reference point: raised-cosine CZ, t_gate = 50 ns, dEz = 100 MHz, J_idle = 50 kHz, Stark shift
1e8 Hz/V on Q2 (Bartee 2025), recalibration every 100 s for 1/f noise. Sensitivity tables vary each
of these.

Run:  python studies/error_budget.py      (about 3 min; writes results/error_budget.{json,md,png})
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flow import budget as B  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
SLOPES = [3.87, 7.25, 10.0, 16.6, 33.69]          # Park 2026 (3), Park 2026 interchanged, Nickl 2025
TARGETS = [1e-3, 1e-4]
TAUS = [1e-9, 10e-9, 100e-9]
F_LO = 1e-2                                       # 1/f noise below 1 / (100 s) is recalibrated
DROOP = {"vanStaveren2025 (50 fA, 15 pF)": 3.1e-3, "vanStaveren2025 best": 60e-6,
         "Darnas2026 (0.5 K)": 5.5e-6}
KB = 1.380649e-23


def both_signs(fun):
    return min(fun(+1), fun(-1))


def channel_specs(lay, target):
    st_num = both_signs(lambda sg: B.max_static(lay, target, sg))
    st_ad = both_signs(lambda sg: B.max_static(lay, target, sg, model="adiabatic"))
    rms = B.max_static_rms(lay, target)
    mid = lay.cfg.t_gate / 2
    gl = {f"{tau * 1e9:g}ns": both_signs(lambda sg: B.max_glitch(lay, target, tau, 0.0, sg))
          for tau in TAUS}
    gl_ad = {f"{tau * 1e9:g}ns": both_signs(lambda sg: B.max_glitch(lay, target, tau, 0.0, sg,
                                                                    model="adiabatic"))
             for tau in TAUS}
    gm = {f"{tau * 1e9:g}ns": both_signs(lambda sg: B.max_glitch(lay, target, tau, mid, sg))
          for tau in TAUS}
    gm_ad = {f"{tau * 1e9:g}ns": both_signs(lambda sg: B.max_glitch(lay, target, tau, mid, sg,
                                                                    model="adiabatic"))
             for tau in TAUS}
    ph, tr = lay.white_noise_infidelity(1.0, split=True)
    return {
        "static_v": st_num, "static_adiabatic_v": st_ad, "static_rms_v": rms,
        "c_min_kTC_4K_f": KB * 4 / rms ** 2, "c_min_kTC_300K_f": KB * 300 / rms ** 2,
        "hold_time_s": {k: st_num / r for k, r in DROOP.items()},
        "droop_v_per_s_for_1ms_refresh": st_num / 1e-3,
        "glitch_v": gl, "glitch_adiabatic_v": gl_ad,
        "glitch_midgate_v": gm, "glitch_midgate_adiabatic_v": gm_ad,
        "white_v_rthz": B.max_white(lay, target),
        "white_transition_fraction": tr / (ph + tr),
        "one_over_f_v_rthz_at_1hz": B.max_one_over_f(lay, target, F_LO),
    }


def stark_only_static(target, alpha, t_gate):
    """Analytic: Z error phi = 2 pi alpha dv t_gate on one qubit, 1 - F = 0.4 (1 - cos phi)."""
    return np.arccos(1 - target / 0.4) / (2 * np.pi * alpha * t_gate)


def main_table():
    rows = []
    for s in SLOPES:
        for label, stark in (("J only", 0.0), ("J + Stark", B.STARK_BARTEE)):
            lay = B.layer(s_dec_per_v=s, stark_q2=stark)
            for target in TARGETS:
                rows.append({"s_dec_per_v": s, "model": label, "target": target,
                             "nominal_infidelity": 1 - lay.f_nominal, **channel_specs(lay, target)})
            print(f"  s = {s:5.2f}  {label:9s}  done", flush=True)
    return rows


def sensitivity_table(s=10.0, target=1e-3):
    base = dict(s_dec_per_v=s)
    cases = [("reference", {}),
             ("dEz = 300 MHz", dict(d_ez=300e6)), ("dEz = 1 GHz", dict(d_ez=1e9)),
             ("t_gate = 25 ns", dict(t_gate=25e-9)), ("t_gate = 100 ns", dict(t_gate=100e-9)),
             ("J_idle = 20 kHz", dict(j_idle=20e3)), ("J_idle = 100 kHz", dict(j_idle=100e3)),
             ("Stark -1e8 Hz/V on Q2", dict(stark_q2=-B.STARK_BARTEE)),
             ("Stark 1e8 Hz/V on Q1", dict(stark_q1=B.STARK_BARTEE, stark_q2=0.0)),
             ("Stark 3e8 Hz/V on Q2", dict(stark_q2=3 * B.STARK_BARTEE)),
             ("no Stark", dict(stark_q2=0.0))]
    rows = []
    for name, kw in cases:
        lay = B.layer(**base, **kw)
        rows.append({"case": name, "nominal_infidelity": 1 - lay.f_nominal,
                     "static_v": both_signs(lambda sg: B.max_static(lay, target, sg)),
                     "glitch_10ns_v": both_signs(lambda sg: B.max_glitch(lay, target, 10e-9, 0.0, sg)),
                     "glitch_10ns_mid_v": both_signs(lambda sg: B.max_glitch(
                         lay, target, 10e-9, lay.cfg.t_gate / 2, sg)),
                     "white_v_rthz": B.max_white(lay, target),
                     "one_over_f_v_rthz_at_1hz": B.max_one_over_f(lay, target, F_LO)})
        print(f"  sensitivity: {name}", flush=True)
    return rows


def idle_table(s=10.0, target=1e-3):
    rows = []
    for t_idle in (0.0, 100e-9, 1e-6, 10e-6):
        row = {"t_idle_s": t_idle}
        for label, stark in (("J only", 0.0), ("J + Stark", B.STARK_BARTEE)):
            for j_idle in (50e3, 100e3):
                lay = B.layer(s_dec_per_v=s, stark_q2=stark, t_idle=t_idle, j_idle=j_idle,
                              dt_idle=min(1e-9, max(t_idle, 1e-9) / 200))
                row[f"{label}, J_idle {j_idle / 1e3:g} kHz"] = both_signs(
                    lambda sg: B.max_static(lay, target, sg))
        rows.append(row)
        print(f"  idle: {t_idle * 1e6:g} us", flush=True)
    return rows


# ---------------------------------------------------------------------------------------- output

def fmt_v(v):
    return f"{v * 1e3:.3g}" if np.isfinite(v) else "> 200"


def write_markdown(res, path):
    L = ["# Error budget (generated by studies/error_budget.py; do not edit)", "",
         f"Reference: t_gate 50 ns, dEz 100 MHz, J_idle 50 kHz, Stark 1e8 Hz/V on Q2, "
         f"1/f recalibrated below {F_LO:g} Hz. Each entry: the largest error of that kind alone "
         "that keeps the infidelity added after calibration at the target. Signed errors: the "
         "worse sign. Glitch 'start': step-and-decay transient that begins as the CZ starts "
         "(refresh of this electrode just before the gate). 'mid': begins at mid-gate (crosstalk "
         "from refreshing another electrode on the same line).", ""]
    for target in TARGETS:
        L += [f"## Target 1 - F = {target:g} ({(1 - target) * 100:g} %)", "",
              "| s (dec/V) | model | static (mV) | RMS scatter (mV) | C_min kT/C 4 K (fF) | "
              "glitch 10 ns, start (mV) | glitch 100 ns, start (mV) | glitch 1 ns, mid (mV) | "
              "glitch 10 ns, mid (mV) | white (nV/√Hz) | 1/f at 1 Hz (µV/√Hz) |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in res["main"]:
            if r["target"] != target:
                continue
            g, m = r["glitch_v"], r["glitch_midgate_v"]
            L.append(f"| {r['s_dec_per_v']:g} | {r['model']} | {fmt_v(r['static_v'])} | "
                     f"{fmt_v(r['static_rms_v'])} | {r['c_min_kTC_4K_f'] * 1e15:.2g} | "
                     f"{fmt_v(g['10ns'])} | {fmt_v(g['100ns'])} | {fmt_v(m['1ns'])} | "
                     f"{fmt_v(m['10ns'])} | "
                     f"{r['white_v_rthz'] * 1e9:.3g} | {r['one_over_f_v_rthz_at_1hz'] * 1e6:.3g} |")
        L.append("")
        L += ["Hold time before the static budget is spent (J + Stark), for measured droop rates:", "",
              "| s (dec/V) | " + " | ".join(DROOP) + " |", "|---|" + "---|" * len(DROOP)]
        for r in res["main"]:
            if r["target"] == target and r["model"] == "J + Stark":
                L.append(f"| {r['s_dec_per_v']:g} | " +
                         " | ".join(f"{t:.3g} s" for t in r["hold_time_s"].values()) + " |")
        L.append("")
    L += ["## Stark shift alone (analytic, one qubit, 1e8 Hz/V)", "",
          "| target | static (mV) |", "|---|---|"]
    for target in TARGETS:
        L.append(f"| {target:g} | {fmt_v(stark_only_static(target, B.STARK_BARTEE, 50e-9))} |")
    L += ["", "## Sensitivity at s = 10 dec/V, target 1e-3", "",
          "| case | nominal 1 - F | static (mV) | glitch 10 ns start (mV) | glitch 10 ns mid (mV) | "
          "white (nV/√Hz) | 1/f at 1 Hz (µV/√Hz) |", "|---|---|---|---|---|---|---|"]
    for r in res["sensitivity"]:
        L.append(f"| {r['case']} | {r['nominal_infidelity']:.1e} | {fmt_v(r['static_v'])} | "
                 f"{fmt_v(r['glitch_10ns_v'])} | {fmt_v(r['glitch_10ns_mid_v'])} | "
                 f"{r['white_v_rthz'] * 1e9:.3g} | "
                 f"{r['one_over_f_v_rthz_at_1hz'] * 1e6:.3g} |")
    keys = [k for k in res["idle"][0] if k != "t_idle_s"]
    L += ["", "## Idle time after the CZ (static budget in mV, s = 10 dec/V, target 1e-3)", "",
          "| t_idle | " + " | ".join(keys) + " |", "|---|" + "---|" * len(keys)]
    for r in res["idle"]:
        L.append(f"| {r['t_idle_s'] * 1e6:g} µs | " + " | ".join(fmt_v(r[k]) for k in keys) + " |")
    L += ["", "## Model agreement", "",
          f"Adiabatic phase model against exact numerics over the main table: static "
          f"{res['agreement']['static_max_rel']:.2%}, glitch (τ ≥ 10 ns) "
          f"{res['agreement']['glitch_max_rel']:.2%}, glitch 1 ns "
          f"{res['agreement']['glitch_1ns_max_rel']:.2%}, mid-gate glitch (τ ≥ 10 ns) "
          f"{res['agreement']['glitch_mid_max_rel']:.2%}, mid-gate 1 ns "
          f"{res['agreement']['glitch_mid_1ns_max_rel']:.2%} (max relative difference of the spec).", ""]
    path.write_text("\n".join(L), encoding="utf-8")


def plot(res, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 2, figsize=(11, 8.5))

    # (a) infidelity against static offset
    a = ax[0, 0]
    dvs = np.geomspace(1e-5, 2e-2, 60)
    for s in (3.87, 10.0, 33.69):
        lay = B.layer(s_dec_per_v=s)
        a.loglog(dvs * 1e3, [lay.excess_infidelity(B.static(lay, d)) for d in dvs], label=f"s = {s:g} dec/V")
    lay = B.layer(s_dec_per_v=10.0, stark_q2=0.0)
    a.loglog(dvs * 1e3, [lay.excess_infidelity(B.static(lay, d)) for d in dvs], "k:", label="s = 10, no Stark")
    for t in TARGETS:
        a.axhline(t, color="grey", lw=0.6)
    a.set(xlabel="residual static barrier offset (mV)", ylabel="1 - F added after calibration",
          ylim=(1e-7, 1), title="(a) static offset (J + Stark)")
    a.legend(fontsize=8)

    # (b) static budget against slope
    b = ax[0, 1]
    for target, ls in zip(TARGETS, ("-", "--")):
        for model, c in (("J only", "C0"), ("J + Stark", "C3")):
            rr = [r for r in res["main"] if r["target"] == target and r["model"] == model]
            b.loglog([r["s_dec_per_v"] for r in rr], [r["static_v"] * 1e3 for r in rr], ls, color=c,
                     marker="o", label=f"{model}, {target:g}")
        b.axhline(stark_only_static(target, B.STARK_BARTEE, 50e-9) * 1e3, color="C2", ls=ls, lw=0.8,
                  label=f"Stark alone, {target:g}")
    b.set(xlabel="exchange slope s (dec/V)", ylabel="max residual offset (mV)",
          title="(b) static budget against slope")
    b.legend(fontsize=7)

    # (c) glitch budget against tau
    c = ax[1, 0]
    taus = np.geomspace(0.3e-9, 1e-6, 16)
    for s in (3.87, 10.0, 33.69):
        lay = B.layer(s_dec_per_v=s)
        ln, = c.loglog(taus * 1e9, [both_signs(lambda sg: B.max_glitch(lay, 1e-3, t, 0.0, sg)) * 1e3
                                    for t in taus], marker=".", label=f"s = {s:g}, at gate start")
        c.loglog(taus * 1e9, [both_signs(lambda sg: B.max_glitch(lay, 1e-3, t, 25e-9, sg)) * 1e3
                              for t in taus], "--", color=ln.get_color(), label=f"s = {s:g}, mid-gate")
    c.set(xlabel="glitch decay time τ (ns)", ylabel="max glitch amplitude (mV)",
          title="(c) step-and-decay glitch, 99.9 %")
    c.legend(fontsize=8)

    # (d) noise kernel
    d = ax[1, 1]
    lay = B.layer(s_dec_per_v=10.0)
    f = np.geomspace(1e3, 2e10, 500)
    k = lay.kernel(f)
    d.loglog(f, k, label="kernel K(f)")
    d.axvline(lay.cfg.d_ez, color="grey", ls=":", lw=0.8)
    d.text(lay.cfg.d_ez * 1.1, k.max() * 0.3, "dEz", fontsize=8)
    d.set(xlabel="frequency (Hz)", ylabel="K(f) (V⁻²)",
          title="(d) noise kernel, s = 10: E[1-F] = ∫ S_V K df")
    d.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(path, dpi=150)


def main():
    t0 = time.time()
    res = {"reference": {"t_gate_s": 50e-9, "d_ez_hz": 100e6, "j_idle_hz": 50e3,
                         "stark_hz_per_v": B.STARK_BARTEE, "f_lo_hz": F_LO}}
    print("main table", flush=True)
    res["main"] = main_table()
    print("sensitivity", flush=True)
    res["sensitivity"] = sensitivity_table()
    print("idle", flush=True)
    res["idle"] = idle_table()
    rel = lambda a, b: abs(a - b) / b if np.isfinite(b) else 0.0  # noqa: E731
    res["agreement"] = {
        "static_max_rel": max(rel(r["static_adiabatic_v"], r["static_v"]) for r in res["main"]),
        "glitch_max_rel": max(rel(r["glitch_adiabatic_v"][k], r["glitch_v"][k])
                              for r in res["main"] for k in ("10ns", "100ns")),
        "glitch_1ns_max_rel": max(rel(r["glitch_adiabatic_v"]["1ns"], r["glitch_v"]["1ns"])
                                  for r in res["main"]),
        "glitch_mid_max_rel": max(rel(r["glitch_midgate_adiabatic_v"][k], r["glitch_midgate_v"][k])
                                  for r in res["main"] for k in ("10ns", "100ns")),
        "glitch_mid_1ns_max_rel": max(rel(r["glitch_midgate_adiabatic_v"]["1ns"],
                                          r["glitch_midgate_v"]["1ns"]) for r in res["main"])}
    res["runtime_s"] = time.time() - t0
    (OUT / "error_budget.json").write_text(json.dumps(res, indent=1))
    write_markdown(res, OUT / "error_budget.md")
    plot(res, OUT / "error_budget.png")
    print(f"done in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
