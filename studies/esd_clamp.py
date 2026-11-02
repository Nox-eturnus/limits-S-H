"""A gate-coupled clamp as a replacement for ESD diodes on the hold node.

Clamp: an NMOS shunt (nfet_01v8, L 0.15 um, W 1 or 5 um) from the hold node to ground, its gate coupled to the node by
C_G = 2 fF and returned to ground through R_G = 1 GOhm, against an ESD pair of 100 um^2 each, in the room-temperature
models and in the 4 K switching band: leakage at held voltages of 0.3 to 1.5 V; node capacitance and its slope dC/dV
between 0.3 and 0.6 V; the offset left by the largest gate pulse and after a 1.2 V refresh step while the gate
recovers; turn-on without supply for a 3 V edge in 0.5 ns.

Run:  python studies/esd_clamp.py     (writes results/esd_clamp.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
from flow import holdstage as H  # noqa: E402
from flow import spice  # noqa: E402
import cryogenic as R  # noqa: E402

WORK = ROOT / "build" / "esd_clamp" / "clamp"
CG, RG = 2e-15, 1e9
VS = (0.3, 0.6, 0.9, 1.2, 1.5)


def cfg(cryo):
    return H.HoldConfig(arch="TG", esd_area=0.0, cryo=cryo, workdir=str(WORK))


def element(kind, w):
    if kind == "esd":
        return ["XESD hold vdd 0 ESD a=100 p=40", "RDUM g 0 1"]
    return [f"XCL hold g 0 0 NSWG wn={w:g} l=0.15", f"CG hold g {CG:g}", f"RG g 0 {RG:g}"]


def run(name, c, body, tstop, tstep="0.1n"):
    deck = "\n".join([H._header(c, abstol=1e-16), f"VDD vdd 0 {c.vdd}"] + body +
                     [".save i(vh) v(g) v(hold)", f".tran {tstep} {tstop:.4e}", ".end", ""])
    return spice.run_ngspice(deck, str(WORK / name.replace(' ', '_')), "d")


def main():
    spice.SPICEINIT = spice.SPICEINIT.replace("num_threads=4", "num_threads=1")
    spice.RETRY_RELAXED = True
    out = {}
    L = ["## Gate-coupled clamp against an ESD pair of 100 um^2 each", ""]
    for band, cryo in (("300 K", None), ("4 K band", R.BANDS["4 K proxy"])):
        c = cfg(cryo)
        for kind, w in (("esd", 0), ("clamp", 1.0), ("clamp", 5.0)):
            tag = f"{kind} {w:g} {band}"
            row = {"leak": {}, "cap": {}}
            for v in VS:
                body = element(kind, w) + [f"VH hold 0 PWL(0 {v} 10n {v} 20n {v + 0.01} 1 {v + 0.01})"]
                wv = run(f"{tag} v{v}", c, body, 20e-9)
                t, i = wv["time"], -wv["i(vh)"]
                row["leak"][v] = float(np.mean(i[(t > 9e-9) & (t <= 10e-9)]))
                row["cap"][v] = float((np.mean(i[(t > 18e-9) & (t <= 20e-9)]) - row["leak"][v]) * 10e-9 / 0.01)
            row["dCdV_03_06"] = (row["cap"][0.6] - row["cap"][0.3]) / 0.3
            if kind == "clamp":
                pulse = (f"VH hold 0 PWL(" + " ".join(f"{(1e-6 + 50e-9 * k / 200):.6e} {0.6 + 0.335 * (1 - np.cos(2 * np.pi * k / 200)):.6f}"
                                                       for k in range(201)) + " 2e-6 0.6)")
                wv = run(f"{tag} pulse", c, element(kind, w) + ["VH0 a 0 0", pulse.replace("VH hold 0", "VH hold 0")], 2e-6, "0.2n")
                t, i = wv["time"], -wv["i(vh)"]
                m = (t >= 0.9e-6) & (t <= 1.9e-6)
                q = np.trapezoid(i[m] - row["leak"][0.6], t[m])
                row["pulse_offset_uV"] = float(q / 1e-12 * 1e6)
                row["pulse_gate_peak"] = float(np.max(wv["v(g)"]))
                step = "VH hold 0 PWL(0 0.3 1e-6 0.3 1.001e-6 1.5 1 1.5)"
                wv = run(f"{tag} step", c, element(kind, w) + [step], 100e-6, "10n")
                t, i = wv["time"], -wv["i(vh)"]
                m = t >= 1.05e-6
                q = np.trapezoid(i[m] - row["leak"][1.5], t[m])
                row["step_offset_uV"] = float(q / 1e-12 * 1e6)
                edge = "VH hold 0 PWL(0 0 1e-9 0 1.5e-9 3 1 3)"
                wv = run(f"{tag} edge", c, element(kind, w) + [edge], 20e-9, "10p")
                row["edge_gate_peak"] = float(np.max(wv["v(g)"]))
                row["edge_current_peak_mA"] = float(np.max(-wv["i(vh)"]) * 1e3)
            out[tag] = row
            print(tag, json.dumps({k: v for k, v in row.items() if k not in ("leak", "cap")}), flush=True)
    for tag, r in out.items():
        L.append(f"- {tag}: leakage {', '.join(f'{v:g} V {r['leak'][v] * 1e15:.3g} fA' for v in VS)}; "
                 f"C {r['cap'][0.6] * 1e15:.3g} fF at 0.6 V, dC/dV {r['dCdV_03_06'] * 1e15:.3g} fF/V"
                 + (f"; pulse offset {r['pulse_offset_uV']:.3g} uV (gate peak {r['pulse_gate_peak'] * 1e3:.3g} mV); "
                    f"after refresh step {r['step_offset_uV']:.3g} uV; 3 V edge: gate {r['edge_gate_peak']:.2f} V, "
                    f"{r['edge_current_peak_mA']:.3g} mA" if "pulse_offset_uV" in r else ""))
    (OUT / "esd_clamp.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT / "esd_clamp.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
