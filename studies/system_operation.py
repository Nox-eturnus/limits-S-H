"""Operation of the array: measured devices, drift, lines per qubit, power left out, sensor noise.

  measured_devices  switch margins at the operating points of measured devices (Park et al.: 7.25 and 16.6 dec/V;
                    Nickl et al.: 33.69 dec/V) with the gate-referred charge noise of Connors et al. (9 to
                    49 uV/rtHz), alone and in the joint allocation (studies/allocation.py).
  drift             device drift between qubit-level retunings against the untracked budgets.
  lines_fan_in      lines per qubit and the share that static multiplexing removes; the fan-in from the hold array
                    to the qubit array (perimeter limit, wire length, crosstalk against the limits of
                    studies/coupling.py).
  move_correction   move margins outside the fine windows corrected for the overstatement that the fine windows
                    measure (interpolation from the standard voltages).
  excluded_power    power terms left out of the array estimate (clocks, level shifters, bootstrap clock, wells), and
                    the static leakage per cell that keeps the lowest-droop array within the mixing-chamber cooling
                    power.
  sensor_noise      gate-referred noise of a charge-sensor measurement of the pedestal, from a measured readout speed.

Run:  python studies/system_operation.py      (about a minute; writes results/system_operation.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import cell_margins as CM  # noqa: E402
import array_yield as Y  # noqa: E402
from flow import budget as B  # noqa: E402
from partial_tracking_qec import budget as pt_budget  # noqa: E402

KB = 1.380649e-23
E = 1.602176634e-19
KTC = float(np.sqrt(KB * 4.2 / 1e-12))
L = []


# ------------------------------------------------------------------------------------------------- measured devices
def untracked_single(lay, target):
    """Untracked single-gate budget: the largest static offset with 1 - F <= target (worse sign)."""
    best = np.inf
    for sign in (+1, -1):
        g = lambda x: B.phase_infidelity(lay.phase_errors(B.static(lay, sign * x))) - target  # noqa: E731
        xs = np.geomspace(1e-7, 0.05, 200)
        vals = np.array([g(x) for x in xs])
        i = np.nonzero(vals >= 0)[0]
        if i.size:
            i = i[0]
            best = min(best, brentq(g, xs[i - 1], xs[i], xtol=xs[i - 1] * 1e-6))
    return float(best)


def one_over_f_budget(s, target):
    rows = json.loads((ROOT / "results" / "error_budget.json").read_text(encoding="utf-8"))["main"]
    r = [x for x in rows if abs(x["s_dec_per_v"] - s) < 1e-6 and x["target"] == target and "Stark" in x["model"]]
    return r[0]["one_over_f_v_rthz_at_1hz"] if r else None


DEVICES = {"Park et al., conventional gates (Si/SiGe)": 7.25, "Park et al., interchanged gates (Si/SiGe)": 16.6,
           "Nickl et al., foundry SiMOS": 33.69}
D4K = {"NMOS": "NMOS, 0.3 V underdrive|4 K proxy", "bootstrapped": "bootstrapped (transistor level), 0.3 V underdrive|4 K proxy",
       "T-switch + OTA": "T-switch + OTA buffer|4 K proxy", "TG + dummies": "TG + dummies|4 K proxy",
       "TG": "TG, no ESD|4 K proxy", "TG with ESD": "TG, ESD on the node|4 K proxy"}


def measured_devices():
    recs = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    mom = {}
    for lab, name in D4K.items():
        x, v, std, nominal, _ = CM.prepare(recs[name])
        A = CM.residual_operator(v, std)
        mom[lab] = {k: Y.moments(x, v, std, A, nominal, k) for k in ("full", "shared")}
    out = []
    for dev, s in DEVICES.items():
        lay = B.layer(s_dec_per_v=s)
        for tgt in (1e-3, 1e-4):
            b = {"b_ind": untracked_single(lay, tgt), "b_eq": pt_budget(lay, tgt, 1.0)}
            a_b = one_over_f_budget(s, tgt)
            row = {"device": dev, "s": s, "target": tgt, "b_ind": b["b_ind"], "b_eq": b["b_eq"], "one_over_f": a_b,
                   "designs": {}}
            for noise in (9e-6, 49e-6):
                share = (noise / a_b) ** 2 + KTC ** 2 / b["b_ind"] ** 2 if a_b else np.nan
                row[f"share_{noise * 1e6:g}"] = share
            for lab, mm in mom.items():
                full = Y.margin_closed(*mm["full"], b)
                shared = Y.margin_closed(*mm["shared"], b)
                d = {"full": full, "shared": shared}
                for noise in (9e-6, 49e-6):
                    f = max(np.sqrt(max(1 - row[f"share_{noise * 1e6:g}"], 0.0)) - 0.1, 0.0)
                    d[f"joint_{noise * 1e6:g}"] = full * f
                row["designs"][lab] = d
            out.append(row)
    L.extend(["## Margins at the operating points of measured devices (4 K band, worst of 10^6, levels set open-loop)", "",
              "Closed-form margins (studies/array_yield.py) with the budgets of each slope; joint: within the allocation of "
              "Supplementary Section S12 with device noise of 9 or 49 µV/√Hz at 1 Hz and kT/C at 4.2 K.", "",
              "| device | s (dec/V) | target | b_eq / b_ind (µV) | device share 9 / 49 µV/√Hz | "
              + " | ".join(f"{k}: per channel / shared / joint 9 / joint 49" for k in D4K) + " |",
              "|---|---|---|---|---|" + "---|" * len(D4K)])
    for r in out:
        L.append(f"| {r['device']} | {r['s']:g} | {r['target']:g} | {r['b_eq'] * 1e6:.0f} / {r['b_ind'] * 1e6:.0f} | "
                 f"{r['share_9']:.3f} / {r['share_49']:.2f} | "
                 + " | ".join(f"{d['full']:.2f} / {d['shared']:.2f} / {d['joint_9']:.2f} / {d['joint_49']:.2f}"
                              for d in r["designs"].values()) + " |")
    L.append("")
    return out


# ------------------------------------------------------------------------------------------------- drift
def drift():
    """1/f device drift between retunings: sigma(T) = A sqrt(ln(f_hi T)), A at 1 Hz, f_hi = 1 Hz averaging bandwidth."""
    Bu = CM.RA.budgets()
    out = {"intervals_s": [100, 3600, 86400], "rows": []}
    for a in (9e-6, 49e-6):
        sig = {T: a * np.sqrt(np.log(1.0 * T)) for T in out["intervals_s"]}
        row = {"A": a, "drift_rms": sig}
        for key in (common.WORST, common.REF):
            b = Bu[key]
            # retune interval at which the drift reaches half the untracked equal-sign budget
            row[f"T_half_beq_{key}"] = float(np.exp(min((0.5 * b["b_eq"] / a) ** 2, np.log(3.15e7))))   # capped at 1 year
        out["rows"].append(row)
    L.extend(["## Device drift between qubit-level retunings (1/f, measured from 1 Hz down to 1/T)", "",
              "| noise at 1 Hz | drift rms over 100 s / 1 h / 1 day (µV) | retune interval for drift = b_eq/2, strictest point | same, 99.9 % and 10 dec/V |",
              "|---|---|---|---|"])
    for r in out["rows"]:
        d = r["drift_rms"]
        L.append(f"| {r['A'] * 1e6:g} µV/√Hz | {d[100] * 1e6:.0f} / {d[3600] * 1e6:.0f} / {d[86400] * 1e6:.0f} | "
                 f"{r[f'T_half_beq_{common.WORST}']:.3g} s | {r[f'T_half_beq_{common.REF}']:.3g} s |")
    L.append("")
    return out


# ------------------------------------------------------------------------------------------------- lines and fan-in
def lines_fan_in():
    """Lines per qubit in a square lattice with barrier-controlled CZ gates; fan-in from the hold array."""
    out = {}
    # gates per qubit: one plunger; two barriers (four per qubit, each shared by two qubits); 0.5 for screening,
    # reservoir and sensor gates (an assumption: one such gate per two qubits)
    gates = {"plunger": 1.0, "barrier": 2.0, "screening, reservoir, sensor": 0.5}
    scen = {"plungers static (single-qubit gates by a shared drive)": {"barrier"},
            "plungers pulsed individually": {"barrier", "plunger"}}
    tot = sum(gates.values())
    out["gates"] = gates
    out["scenarios"] = {}
    for name, fast in scen.items():
        n_fast = sum(gates[g] for g in fast)
        out["scenarios"][name] = {"lines_without_mux": tot, "lines_with_mux": n_fast, "removed": 1 - n_fast / tot}
    # fan-in perimeter limit: N_max = 4 s L / p for a square qubit region of side s, L routing layers, pitch p
    p_sig = 0.2e-6        # one signal and one shield at a 100 nm metal pitch
    layers = (4, 6, 10)
    out["fanin"] = {}
    for nl in layers:
        n_1mm = 4 * 1e-3 * nl / p_sig
        side_1e6 = 1e6 * p_sig / (4 * nl)
        out["fanin"][nl] = {"n_max_1mm2": n_1mm, "side_for_1e6_m": side_1e6, "qubit_pitch_m": side_1e6 / 1e3}
    # wire length from a 26 x 33 mm2 hold array to a central qubit region: mean and largest
    rng = np.random.default_rng(1)
    pts = rng.uniform([-13e-3, -16.5e-3], [13e-3, 16.5e-3], (200_000, 2))
    dist = np.abs(pts).sum(1)                     # Manhattan routing
    out["wire_mean_m"], out["wire_max_m"] = float(dist.mean()), float(dist.max())
    # crosstalk: adjacent coupling 0.05 to 0.1 fF/um at minimum pitch; a grounded shield leaves an assumed 1 to 5 %
    for lab, frac in (("unshielded", 1.0), ("shielded, 1 %", 0.01), ("shielded, 5 %", 0.05)):
        out[f"coupling_mean_{lab}_fF"] = [c * frac * out["wire_mean_m"] * 1e6 for c in (0.05, 0.1)]
    out["limit_99.99_fF"] = (0.57, 1.2)
    out["limit_idle_fF"] = 136
    # pitch-matched (sparse) array: each hold cell under its own electrode, wire length about one cell pitch
    out["pitch_matched_wire_um"] = 22
    L.extend(["## Lines per qubit and the fan-in", "",
              "Gates per qubit in a square lattice: " + ", ".join(f"{k} {v:g}" for k, v in gates.items()) + ".", "",
              "| scenario | individual lines per qubit without multiplexing | individual fast lines with multiplexing | share removed |",
              "|---|---|---|---|"])
    for n, s in out["scenarios"].items():
        L.append(f"| {n} | {s['lines_without_mux']:g} | {s['lines_with_mux']:g} | {s['removed'] * 100:.0f} % |")
    L.extend(["", "| routing layers | lines through the edge of a 1 mm² region | side of a region for 10^6 lines | qubit pitch for 10^6 qubits |",
          "|---|---|---|---|"])
    for nl, f in out["fanin"].items():
        L.append(f"| {nl} | {f['n_max_1mm2']:.2g} | {f['side_for_1e6_m'] * 1e3:.1f} mm | {f['qubit_pitch_m'] * 1e6:.1f} µm |")
    L.extend(["", f"Wire from the hold array to a central qubit region: mean {out['wire_mean_m'] * 1e3:.1f} mm, largest "
          f"{out['wire_max_m'] * 1e3:.1f} mm. Coupling to an adjacent line over the mean length: unshielded "
          f"{out['coupling_mean_unshielded_fF'][0]:.0f} to {out['coupling_mean_unshielded_fF'][1]:.0f} fF, shielded (1 to 5 % residual) "
          f"{out['coupling_mean_shielded, 1 %_fF'][0]:.1f} to {out['coupling_mean_shielded, 5 %_fF'][1]:.0f} fF, against 0.57 to 1.2 fF "
          "at 99.99 % for a neighbour running its own CZ.", ""])
    return out


# ------------------------------------------------------------------------------------------------- move correction
def move_correction():
    r6 = json.loads((ROOT / "results" / "cell_margins.json").read_text(encoding="utf-8"))["designs"]
    W = common.WORST
    fig6 = ("NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive", "T-switch + OTA buffer",
            "TG + dummies", "TG, no ESD", "TG, ESD on the node")
    out = {}
    for span in (20, 50):
        over = [r["margin"][f"{W}|move{span}mVinterp|mixed"] / r["margin"][f"{W}|move{span}mVwin|mixed"]
                for n, r in r6.items() if r["fine"] and f"{W}|move{span}mVinterp|mixed" in r["margin"]
                and n.split("|")[0] in fig6]
        f = max(over)
        rows = [(n, r["margin"][f"{W}|move{span}mV|mixed"]) for n, r in r6.items() if n.split("|")[0] in fig6]
        interp = [(n, m / f) for n, m in rows if not r6[n]["fine"]]
        fine = [(n, m) for n, m in rows if r6[n]["fine"]]
        lo = min(interp, key=lambda t: t[1])
        out[span] = {"overstatement_max": f, "overstatement_range": [min(over), max(over)],
                     "min_corrected_interp": lo, "min_fine": min(fine, key=lambda t: t[1])}
    L.extend(["## Move margins corrected for the measured interpolation bias (strictest point, Figure 6 designs)", "",
              "| move | overstatement in the fine windows (interpolated / simulated) | lowest corrected margin outside the fine windows | lowest fine-grid margin |",
              "|---|---|---|---|"])
    for span, o in out.items():
        L.append(f"| {span} mV | {o['overstatement_range'][0]:.2f} to {o['overstatement_range'][1]:.2f} | "
                 f"{o['min_corrected_interp'][1]:.1f} ({o['min_corrected_interp'][0]}) | {o['min_fine'][1]:.1f} ({o['min_fine'][0]}) |")
    L.append("")
    return out


# ------------------------------------------------------------------------------------------------- excluded power
def excluded_power():
    """Per-refresh terms left out of the array power, and the static leakage allowance at the mixing chamber."""
    terms = {   # energy per refresh (J), order-of-magnitude, from CV^2 of the stated capacitances
        "clock buffer of the selected path (2 to 5 fF internal per level, 3 to 7 levels, 2.1 V)": (2e-15 * 3 * 2.1 ** 2, 5e-15 * 7 * 2.1 ** 2),
        "level shifters, -0.3 V and 3.3 V drives (10 to 20 fF each, two per refresh, 3.6 V)": (2 * 10e-15 * 3.6 ** 2, 2 * 20e-15 * 3.6 ** 2),
        "bootstrap capacitor recharge (50 fF to 1.8 V, bootstrapped switch only)": (50e-15 * 1.8 ** 2, 50e-15 * 1.8 ** 2),
    }
    tot = (sum(a for a, _ in terms.values()), sum(b for _, b in terms.values()))
    counted = {"46.5 mV/s": (35e-12 + 68e-12, 38e-12 + 75e-12), "5.5 uV/s": (200e-12 + 213e-12, 245e-12 + 366e-12)}
    mc = 19e-6
    low = 1.4e-6
    leak_allow = (mc - low) / 1e6 / 2.1         # per cell, at a 2.1 V supply
    wells = {"groups of 100": 1e4, "groups of 25": 4e4}
    out = {"terms": terms, "total": tot, "counted": counted, "share": {k: (tot[0] / c[1], tot[1] / c[0]) for k, c in counted.items()},
           "leak_allow_per_cell_A": leak_allow, "well_supplies": wells,
           "well_supply_allow_W": {k: (mc - low) / n for k, n in wells.items()}}
    L.extend(["## Power terms left out of the array estimate", "",
              "| term | energy per refresh |", "|---|---|"])
    for k, (a, b) in terms.items():
        L.append(f"| {k} | {a * 1e15:.0f} to {b * 1e15:.0f} fJ |")
    L.extend([f"| total | {tot[0] * 1e12:.2f} to {tot[1] * 1e12:.2f} pJ |", "",
          "Share of the counted refresh and addressing energy: " + ", ".join(
              f"{k}: {s[0] * 100:.2f} to {s[1] * 100:.1f} %" for k, s in out["share"].items()) + ".",
          f"Static leakage allowed per cell for the lowest-droop array (1.4 µW) to stay within 19 µW at the mixing chamber: "
          f"{leak_allow * 1e12:.1f} pA at 2.1 V. Isolated-well supplies for the NMOS switch: "
          + ", ".join(f"{k} ({n:.0e} supplies) {w * 1e9:.1f} nW each" for (k, n), w in zip(wells.items(), out['well_supply_allow_W'].values())) + ".", ""])
    return out


# ------------------------------------------------------------------------------------------------- sensor noise
def sensor_noise():
    """Gate-referred noise of a pedestal measurement through a charge sensor.

    Noiri et al. distinguish two charge states with a signal-to-noise ratio of 6 in 0.8 us. A charge contrast dq at the
    sensor (in units of e) then corresponds to a charge noise density S_q = dq sqrt(t) / SNR (white noise, SNR = signal /
    rms in the integration time t). A barrier offset dV reaches the sensor as a charge dV / V_add, where V_add is the
    barrier voltage that changes the sensed charge by one electron through the cross-capacitance, so the gate-referred
    noise is S_V = S_q V_add. dq (0.1 to 0.3 e) and V_add (0.1 to 1 V) are assumed ranges."""
    t, snr = 0.8e-6, 6.0
    out = {"cases": []}
    for dq in (0.1, 0.3):
        for vadd in (0.1, 1.0):
            sq = dq * np.sqrt(t) / snr
            out["cases"].append({"dq": dq, "V_add": vadd, "S_q": sq, "S_V": sq * vadd})
    sv = [c["S_V"] for c in out["cases"]]
    out["S_V_range"] = [min(sv), max(sv)]
    eps = {"strictest": 11e-6, "99.9 %, 10 dec/V": 80e-6}
    out["t_point"] = {k: [s ** 2 / (2 * e ** 2) for s in out["S_V_range"]] for k, e in eps.items()}
    out["t_total_100par"] = {k: [6e6 * x / 100 for x in v] for k, v in out["t_point"].items()}
    L.extend(["## Gate-referred noise of a pedestal measurement through a charge sensor", "",
              f"S_q from Noiri et al. (SNR 6 in 0.8 µs): {min(c['S_q'] for c in out['cases']):.1e} to "
              f"{max(c['S_q'] for c in out['cases']):.1e} e/√Hz; S_V = {out['S_V_range'][0] * 1e6:.1f} to "
              f"{out['S_V_range'][1] * 1e6:.0f} µV/√Hz.", ""])
    for k in eps:
        a, b = out["t_point"][k]
        ta, tb = out["t_total_100par"][k]
        L.append(f"- {k}: {a:.2g} to {b:.2g} s per point; 10^6 channels, 100 in parallel: {ta / 60:.2g} min to {tb / 3600:.2g} h")
    L.append("")
    return out


def main():
    out = {"measured_devices": measured_devices(), "drift": drift(), "lines_fan_in": lines_fan_in(),
           "move_correction": move_correction(), "excluded_power": excluded_power(), "sensor_noise": sensor_noise()}
    (OUT / "system_operation.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    (OUT / "system_operation.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
