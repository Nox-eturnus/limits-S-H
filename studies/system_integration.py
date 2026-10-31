"""Integration of the array with the qubit chip and the cryostat.

  stage_load        load per temperature stage of the whole static-plus-pulse architecture: tree and hold cells
                    (studies/droop_anchors.py) plus the lower bound on the pulse drivers (studies/pulse_drivers.py),
                    against the cooling power of each stage.
  placement         placement of the hold cells and pulse drivers: lines per qubit (3.5), the qubit pitch that each
                    placement allows (pitch-matched cells, in-plane fan-in through the edge, face-to-face bonding at a
                    bond pitch), and the crosstalk of long pulse lines after qubit-level calibration (fixed schedule)
                    or with electronic compensation of accuracy a (schedule-dependent crosstalk).
  drift_moves       size of the open-loop moves between qubit-level tunings that drift compensation requires, and the
                    move margins that follow from the linear dependence of the move error on the move
                    (results/cell_margins.json).
  leakage_range     electrodes per DAC over the measured leakage range of the protection diodes of van Staveren et al.
  zeeman            untracked static budget against the Zeeman difference, with the gate time lengthened to keep the
                    gate adiabatic.
  calibration_time  differential measurement and parallelism tied to the number of sensors read at once.

Run:  python studies/system_integration.py      (a few minutes; writes results/system_integration.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import droop_anchors as A5  # noqa: E402

from flow import budget as B  # noqa: E402

L = []
STAGES = {"20 mK": 19e-6, "140 mK": 200e-6, "1.2 K": 40e-3, "4.2 K": 1.5}      # Krinner et al. 2019
N_E = 1e6                      # electrodes
GATES_PER_QUBIT = 3.5          # one plunger, two barriers, half a screening, reservoir or sensor gate
CELL_PITCH = {"1 pF": 22e-6, "200 fF": (9e-6, 11e-6), "70 fF": (4e-6, 9e-6)}


# ------------------------------------------------------------------------------------------------- stage load
def stage_load():
    a = json.loads((ROOT / "results" / "droop_anchors.json").read_text(encoding="utf-8"))
    pd = {(3.87, 1e-6): 452e-3, (3.87, 10e-6): 45.2e-3, (10.0, 1e-6): 67.7e-3, (10.0, 10e-6): 6.77e-3,
          (33.69, 1e-6): 5.97e-3, (33.69, 10e-6): 0.597e-3}                       # studies/pulse_drivers.py
    static = {"46.5 mV/s": [r["cold_load_W"] for r in a["rows"] if r["anchor"].startswith("ESD")],
              "3.1 mV/s": [r["cold_load_W"] for r in a["rows"] if r["anchor"].startswith("reference")],
              "5.5 uV/s": [0.94e-6, 1.4e-6]}                                          # SI Table S23
    out = {"pulse_W": {f"{s:g}|{t * 1e6:g}us": p for (s, t), p in pd.items()}, "static_W": {}, "rows": []}
    for k, v in static.items():
        out["static_W"][k] = [min(v), max(v)]
    L.extend(["## Load at the qubit stage: tree and hold cells plus the lower bound on the pulse drivers (10^6 electrodes, "
              "10^6 barriers)", "",
              "| droop | s (dec/V) | round | static array | pulse drivers (lower bound) | total | stages that can carry it |",
              "|---|---|---|---|---|---|---|"])
    for k, (lo, hi) in out["static_W"].items():
        for (s, t), p in pd.items():
            tot = hi + p
            fit = [n for n, c in STAGES.items() if tot <= c]
            out["rows"].append({"droop": k, "s": s, "round_s": t, "static_W": hi, "pulse_W": p, "total_W": tot, "fits": fit})
            L.append(f"| {k} | {s:g} | {t * 1e6:g} µs | {hi * 1e3:.3g} mW | {p * 1e3:.3g} mW | {tot * 1e3:.3g} mW | "
                     f"{', '.join(fit)} |")
    L.append("")
    return out


# ------------------------------------------------------------------------------------------------- placement
def placement():
    out = {}
    n_q = N_E / GATES_PER_QUBIT
    out["qubits"] = n_q
    # (i) pitch-matched: the cells of a qubit's 3.5 electrodes under that qubit
    pm = {}
    for c, p in CELL_PITCH.items():
        lo, hi = (p, p) if np.isscalar(p) else p
        pm[c] = [np.sqrt(GATES_PER_QUBIT) * lo, np.sqrt(GATES_PER_QUBIT) * hi]
    out["pitch_matched_qubit_pitch_m"] = pm
    # (ii) in-plane fan-in through the edge of the qubit region: 4 a L / p lines, one signal and one shield at 100 nm
    p_sig = 0.2e-6
    edge = {}
    for nl in (4, 6, 10):
        side = N_E * p_sig / (4 * nl)
        edge[nl] = {"side_m": side, "qubit_pitch_m": side / np.sqrt(n_q)}
    out["edge"] = edge
    # (iii) face-to-face bonding: one bond per electrode at a bond pitch p_b (assumed range)
    bond = {}
    for pb in (1e-6, 3e-6, 10e-6):
        bond[pb] = {"side_m": np.sqrt(N_E) * pb, "qubit_pitch_m": np.sqrt(GATES_PER_QUBIT) * pb}
    out["bond"] = bond
    # crosstalk of long pulse lines (15 mm mean, studies/system_operation.py) against the limits of studies/coupling.py
    lim = {"99.99 %": (0.573e-15, 1.18e-15), "99.9 %": (1.81e-15, 3.67e-15)}
    coup = {"unshielded": (0.74e-12, 1.5e-12), "shielded (1 to 5 % residual)": (7e-15, 74e-15)}
    acc = {}
    for t, (l_lo, l_hi) in lim.items():
        for c, (c_lo, c_hi) in coup.items():
            acc[f"{t}|{c}"] = [l_lo / c_hi, l_hi / c_lo]
    out["required_compensation_accuracy"] = acc
    L.extend(["## Placement of hold cells and pulse drivers", "",
              f"10^6 electrodes at {GATES_PER_QUBIT} electrodes per qubit = {n_q:.3g} qubits; every electrode needs its "
              "own connection from its hold cell, static or pulsed.", "",
              "| placement | assumption | qubit pitch |", "|---|---|---|"])
    for c, (lo, hi) in pm.items():
        L.append(f"| hold cells under their electrodes | cell pitch for {c} | {lo * 1e6:.1f} to {hi * 1e6:.1f} µm |")
    for nl, e in edge.items():
        L.append(f"| separate hold array, in-plane fan-in through the edge | {nl} routing layers, 200 nm per line | "
                 f"{e['qubit_pitch_m'] * 1e6:.1f} µm (region side {e['side_m'] * 1e3:.1f} mm) |")
    for pb, b in bond.items():
        L.append(f"| separate hold tier, face-to-face bonds | bond pitch {pb * 1e6:g} µm | {b['qubit_pitch_m'] * 1e6:.1f} µm "
                 f"(region side {b['side_m'] * 1e3:.0f} mm) |")
    L.extend(["", "Electronic compensation accuracy that a 15 mm pulse line needs when its crosstalk depends on the schedule "
              "(a neighbour that sometimes pulses and sometimes idles); with a fixed schedule the crosstalk is absorbed by "
              "qubit-level tuning of the CZ amplitude.", "",
              "| target | line | coupling | limit | required accuracy |", "|---|---|---|---|---|"])
    for k, (lo, hi) in acc.items():
        t, c = k.split("|")
        L.append(f"| {t} | {c} | {coup[c][0] * 1e15:.3g} to {coup[c][1] * 1e15:.3g} fF | {lim[t][0] * 1e15:.2g} to "
                 f"{lim[t][1] * 1e15:.2g} fF | {lo * 100:.2g} to {hi * 100:.2g} % |")
    L.append("")
    return out


# ------------------------------------------------------------------------------------------------- drift moves
def drift_moves():
    r = json.loads((ROOT / "results" / "cell_margins.json").read_text(encoding="utf-8"))["designs"]
    s7 = json.loads((ROOT / "results" / "system_operation.json").read_text(encoding="utf-8"))
    drift = {f"{row['A'] * 1e6:g} uV/rtHz": row["drift_rms"] for row in s7["drift"]["rows"]}
    # the move error grows in proportion to the move (Supplementary Section S6), so the margin of a move of delta is
    # the 20 mV margin times 20 mV / delta; lowest 20 mV margins: 6.0 interpolated and corrected, 16 on the fine grid
    m20 = {"interpolated, corrected": 6.0, "fine grid": 16.0}
    moves = (0.2e-3, 1e-3, 5e-3)
    out = {"drift": drift, "m20": m20, "margins": {k: {f"{d * 1e3:g} mV": v * 20e-3 / d for d in moves} for k, v in m20.items()}}
    L.extend(["## Open-loop moves between qubit-level tunings", "",
              "Drift of a level between tunings (1/f, studies/system_operation.py): " + "; ".join(
                  f"{k}: {v['86400'] * 1e6 if '86400' in v else v[86400] * 1e6:.0f} µV per day" for k, v in drift.items()) + ".",
              "A virtual-gate correction moves a barrier by the drift of a neighbour times a normalised cross-coupling below one, "
              "so drift compensation needs moves below about 0.2 mV per day.", "",
              "| lowest 20 mV margin | 0.2 mV | 1 mV | 5 mV |", "|---|---|---|---|"])
    for k, v in out["margins"].items():
        L.append(f"| {k} ({m20[k]:g}) | " + " | ".join(f"{x:.0f}" for x in v.values()) + " |")
    L.append("")
    return out


# ------------------------------------------------------------------------------------------------- leakage range
def leakage_range():
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    bud = A5.common.budgets()
    spec_op = bud[A5.common.REF]["operational"]
    rates = {"low (0.9 mV/s)": 60e-6 * 15, "typical (46.5 mV/s)": 3.1e-3 * 15, "high (0.27 V/s)": 18e-3 * 15}
    out = {}
    for name, r in A5.T.designs(res).items():
        bd = A5.C.hold_budget(spec_op, r["residual"], 0.1)
        row = {}
        for k, rate in rates.items():
            flat = A5.C.n_max(bd / rate, r["cell"], spec_op, bd, A5.SY.met2())
            tree = A5.SB.best_tree(r, spec_op, rate, 2e-9)["n"]
            row[k] = {"flat": float(flat), "tree": float(min(tree, A5.T.RETICLE / A5.C.TreeConfig().pitch ** 2))}
        out[name] = row
        print(name, {k: f"{v['tree']:.2g}" for k, v in row.items()}, flush=True)
    L.extend(["## Electrodes per DAC over the measured leakage range of the protection diodes (1 pF node, 99.9 %, "
              "10 dec/V, 4 K switching models)", "",
              "| design | " + " | ".join(f"{k}: flat / tree" for k in rates) + " |", "|---|" + "---|" * len(rates)])
    for name, row in out.items():
        L.append(f"| {name} | " + " | ".join(f"{v['flat']:.2g} / {v['tree']:.2g}" for v in row.values()) + " |")
    L.append("")
    return out


# ------------------------------------------------------------------------------------------------- Zeeman difference
def zeeman():
    cases = ((1e9, 50e-9), (100e6, 50e-9), (50e6, 100e-9), (25e6, 200e-9))
    out = []
    L.extend(["## Untracked single-gate static budget against the Zeeman difference (Stark 10^8 Hz/V on one qubit)", "",
              "The gate time is lengthened in proportion to 1/ΔE_Z below 100 MHz so that the peak exchange stays at ΔE_Z/5.", "",
              "| ΔE_Z | gate time | nominal 1 - F | " + " | ".join(f"{s:g} dec/V: 99.9 % / 99.99 % (mV)" for s in (3.87, 10, 33.69)) + " |",
              "|---|---|---|---|---|---|"])
    for dez, tg in cases:
        row = {"d_ez": dez, "t_gate": tg, "budgets": {}}
        cells = []
        for s in (3.87, 10.0, 33.69):
            lay = B.layer(s_dec_per_v=s, d_ez=dez, t_gate=tg, dt=max(5e-12, tg / 1e4))
            row["nominal_infidelity"] = 1 - lay.f_nominal
            b = [min(B.max_static(lay, t, +1), B.max_static(lay, t, -1)) for t in (1e-3, 1e-4)]
            row["budgets"][f"{s:g}"] = b
            cells.append(f"{b[0] * 1e3:.3g} / {b[1] * 1e3:.3g}")
        out.append(row)
        L.append(f"| {dez / 1e6:g} MHz | {tg * 1e9:g} ns | {row['nominal_infidelity']:.1e} | " + " | ".join(cells) + " |")
        print(L[-1], flush=True)
    L.append("")
    return out


# ------------------------------------------------------------------------------------------------- calibration time
def calibration_time():
    s7 = json.loads((ROOT / "results" / "system_operation.json").read_text(encoding="utf-8"))["sensor_noise"]
    out = {"t_point_plain": s7["t_point"], "differential_factor": 4.0}
    # A differential point averages two states for half the time each: the variance of the difference is four times
    # that of one plain average of the same total duration.
    par = (1e2, 1e3, 1e4)
    out["t_total"] = {k: {f"{p:g}": [6e6 * 4 * t / p for t in v] for p in par} for k, v in s7["t_point"].items()}
    L.extend(["## Calibration time of 10^6 channels, differential points, against the number of sensors read at once", "",
              "| point accuracy | " + " | ".join(f"{p:g} at once" for p in par) + " |", "|---|" + "---|" * len(par)])

    def h(x):
        return f"{x / 60:.2g} min" if x < 3600 else f"{x / 3600:.2g} h" if x < 2 * 86400 else f"{x / 86400:.2g} d"
    for k, v in out["t_total"].items():
        L.append(f"| {k} | " + " | ".join(f"{h(a)} to {h(b)}" for a, b in v.values()) + " |")
    L.append("")
    return out


def main():
    out = {"stage_load": stage_load(), "placement": placement(), "drift_moves": drift_moves(),
           "calibration_time": calibration_time(), "leakage_range": leakage_range(), "zeeman": zeeman()}
    (OUT / "system_integration.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    (OUT / "system_integration.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
