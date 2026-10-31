"""A measured anchor for the circuit layer: injected charge of a sample-and-hold switch on 15 pF.

van Staveren et al. (IEEE TQE 6, 3101618, 2025) measured the net charge that their sample-and-hold
switch injects onto a 15 pF on-chip hold capacitor at millikelvin temperature: 59 fC and 66 fC at two
bias points (their Fig. 12). Their switch is a minimum-length 1.8 V transmission gate in a 22 nm
FinFET process, sized for an on-resistance of 20-40 ohm, with a pad ESD pair on the output.

The SkyWater models have no bin for devices of hundreds of micrometres, so the cell is simulated as
its exact scaled equivalent: a switch of width W/k on C_hold/k with ESD area 100/k um^2 and source
resistance 50 k ohm has the same node waveform, hence the same pedestal, and the injected charge is
C_hold x pedestal. The comparison simulates the same circuit in the flow: a SkyWater 1.8 V transmission
gate (minimum length, PMOS twice the NMOS width) sized for 20 and 40 ohm at mid-rail with the
room-temperature models, on 15 pF with a 100 um^2 ESD pair, with the room-temperature models and in the
4 K band. It reports the net injected charge C x pedestal at mid-rail (0.7-1.1 V) and over all passed
held voltages, for clock edges of 0.2 and 2 ns (their edge time is not stated). The processes differ,
so this checks the order of magnitude of the injected charge, which is set by the channel charge of a
switch of a given on-resistance (W L C_ox V_ov ~ L^2 / (mu R_on)), not a quantitative validation.

Run:  python studies/anchor_charge.py      (about 10 min; writes results/anchor_charge.{json,md})
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import cryogenic as R  # noqa: E402
from flow import cosim as C  # noqa: E402
from flow import holdstage as H  # noqa: E402

WORK = ROOT / "build" / "anchor_charge" / "anchor"
C_HOLD = 15e-12
MEASURED_FC = (59.0, 66.0)
BAND = R.BANDS["4 K proxy"]
WIDTHS = (50.0, 100.0, 200.0, 400.0)
W_SIM = 5.0                              # simulated NMOS width (um); k = W / W_SIM


def base(wn, t_edge=200e-12, r_src=50.0, cryo=None):
    k = wn / W_SIM
    return H.HoldConfig(arch="TG", wn=W_SIM, c_node=C_HOLD / k, esd_area=100.0 / k, cryo=cryo, t_edge=t_edge,
                        r_src=r_src * k, workdir=str(WORK / f"w{wn:g}"))


def r_on(wn):
    k = wn / W_SIM
    cfg = base(wn, r_src=1.0)
    cell = C.cell_params(cfg, v0=0.9)
    return (cell["tau_node"] / (C_HOLD / k) - 1.0 * k) / k      # on-resistance of the full-width switch


def main():
    C.spice.REUSE = True
    with ThreadPoolExecutor(4) as ex:
        ron = dict(zip(WIDTHS, ex.map(r_on, WIDTHS)))
    lw, lr = np.log(WIDTHS), np.log([ron[w] for w in WIDTHS])
    fit = np.polyfit(lr, lw, 1)
    w_for = {r: float(np.exp(np.polyval(fit, np.log(r)))) for r in (20.0, 40.0)}
    jobs = [(r, w, te, b) for r, w in w_for.items() for te in (200e-12, 2e-9) for b in ("300 K", "4 K proxy")]

    def one(j):
        r, w, te, b = j
        m = H.measure(base(round(w, 1), te, cryo=R.BANDS[b]))
        ok = np.abs(m["track_error"]) < R.TRACK_TOL
        q = m["pedestal"] * C_HOLD * 1e15
        return {"r_on_target": r, "wn": round(w, 1), "t_edge": te, "band": b, "v_hold": list(map(float, m["v_hold"])),
                "q_fC": q.tolist(), "ok": ok.tolist(), "pedestal_mV": (m["pedestal"] * 1e3).tolist()}

    with ThreadPoolExecutor(4) as ex:
        rows = list(ex.map(one, jobs))
    out = {"measured_fC": MEASURED_FC, "r_on_by_width": {f"{w:g}": ron[w] for w in WIDTHS}, "rows": rows}
    (OUT / "anchor_charge.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["## Injected charge: SkyWater TG of the same on-resistance against van Staveren et al. (59 and 66 fC on 15 pF)", "",
         "On-resistance at 0.9 V, room-temperature models: " + ", ".join(f"W_n {w:g} µm: {ron[w]:.0f} Ω" for w in WIDTHS), "",
         "| R_on target | W_n (µm) | band | clock edge | Q at 0.7-1.1 V (fC) | Q over passed voltages (fC) | pedestal on 15 pF, mid-rail (mV) |",
         "|---|---|---|---|---|---|---|"]
    for r in rows:
        v, ok = np.array(r["v_hold"]), np.array(r["ok"])
        q = np.array(r["q_fC"])
        mid = ok & (v >= 0.7) & (v <= 1.1)
        p = np.abs(np.array(r["pedestal_mV"]))[mid]
        L.append(f"| {r['r_on_target']:g} Ω | {r['wn']:g} | {r['band']} | {r['t_edge'] * 1e9:g} ns | "
                 f"{q[mid].min():.0f} to {q[mid].max():.0f} | {q[ok].min():.0f} to {q[ok].max():.0f} | {p.min():.2f}-{p.max():.2f} |")
    (OUT / "anchor_charge.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
