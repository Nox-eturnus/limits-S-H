"""The NMOS switch referenced to an offset well.

The NMOS switch with underdrive holds a window of about 0.3 to 0.8 V on every channel in the 4 K band.
Published devices give their barrier voltages relative to a tuned operating point (virtual gates; for
example barrier pulses of 0.28 to 0.4 V in Park et al. 2026), so the absolute DC level an electrode needs
is set during tuning and differs between devices. The held window can follow it if the switch sits in an
isolated p-well (deep n-well in SkyWater 130 nm) whose potential V_w is shared by a group of cells, with the
gate clock referenced to the same well (low level V_w - 0.3 V, high level V_w + 1.8 V). Every terminal
voltage of the transistor relative to its body is then that of the ground-referenced cell, so the pedestal
at V_w + v should equal the pedestal of the ground-referenced cell at v; the hold capacitor and the source
resistance are linear and only carry the offset. This script checks that in SPICE, nominal and with
mismatch, in the 4 K band.

Run:  python studies/offset_well.py      (about 5 min; writes results/offset_well.{json,md})
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
from flow import holdstage as H  # noqa: E402
from flow import spice  # noqa: E402

DESIGN = "NMOS, 0.3 V underdrive"
OFFSETS = (0.0, 0.5, 1.0)
SEEDS = (0, 1, 2)                         # 0 = nominal


def deck(cfg, vw):
    """The transient deck of holdstage.py with body, gate clock and line raised by vw."""
    tl = H.timeline(cfg)
    te, ud = cfg.t_edge, cfg.v_underdrive
    clk = (tl["t1"], tl["t_open"], tl["t_reclose"], tl["t_reopen"], te)
    lines = [H._header(cfg), f"VDD vdd 0 {cfg.vdd}", f"VW vw 0 {vw}",
             H._clock("en", vw - ud, vw + cfg.vdd, *clk)]
    tl0, tl1 = tl["t_line"], tl["t_line"] + 1e-9
    for i, v in enumerate(cfg.v_hold):
        dv = cfg.dv_line if v + cfg.dv_line <= cfg.vdd else -cfg.dv_line
        a = v + vw
        lines += [f"VIN{i} vin{i} 0 PWL(0 {a} {tl0:.6e} {a} {tl1:.6e} {a + dv} {tl1 + 10e-9:.6e} {a + dv} "
                  f"{tl1 + 11e-9:.6e} {a})",
                  f"RS{i} vin{i} src{i} {cfg.r_src}",
                  f"XSW{i} src{i} hold{i} en vw NSWG wn={cfg.wn} l={cfg.l}",
                  f"CH{i} hold{i} 0 {cfg.c_node:.6e}"]
    saves = " ".join(f"v(hold{i})" for i in range(len(cfg.v_hold)))
    lines += [f".save {saves}", f".tran {min(10e-12, te / 10):.3e} {tl['t_stop']:.6e}", ".end", ""]
    return "\n".join(lines)


def pedestal(cfg, vw):
    tl = H.timeline(cfg)
    w = spice.run_ngspice(deck(cfg, vw), cfg.workdir, cfg.tag() + f"_vw{vw:g}")
    t = w["time"]
    ped, track = [], []
    for i, v in enumerate(cfg.v_hold):
        x = w[f"v(hold{i})"]
        pre = H._settled(t, x, tl["t_open"] - 0.1e-9)
        ped.append(H._settled(t, x, tl["t_ped"]) - pre)
        track.append(pre - (v + vw))
    return np.array(ped), np.array(track)


def main():
    spice.TIMEOUT, spice.RETRY_RELAXED, spice.REUSE = 14400, True, True
    cfgs = {seed: R.E.base_cfg(workdir=str(ROOT / "build" / "offset_well" / "offset_well"), cryo=R.BANDS["4 K proxy"],
                               mismatch=seed > 0, seed=max(seed, 1), **R.DESIGNS[DESIGN]) for seed in SEEDS}
    jobs = [(seed, vw) for seed in SEEDS for vw in OFFSETS]
    with ThreadPoolExecutor(len(jobs)) as ex:
        res = dict(zip(jobs, ex.map(lambda j: pedestal(cfgs[j[0]], j[1]), jobs)))
    rows = []
    for seed in SEEDS:
        base = res[(seed, 0.0)][0]
        for vw in OFFSETS:
            ped, track = res[(seed, vw)]
            rows.append({"seed": seed, "v_w": vw, "v_hold": [v + vw for v in cfgs[seed].v_hold], "pedestal": ped.tolist(),
                         "track_error": track.tolist(), "max_diff_from_v_w0": float(np.abs(ped - base).max())})
            print(f"seed {seed}, V_w = {vw:g} V: max |pedestal - pedestal(V_w = 0)| = "
                  f"{np.abs(ped - base).max() * 1e6:.3f} uV", flush=True)
    (OUT / "offset_well.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    L = ["## NMOS switch with underdrive in an offset well, 4 K band", "",
         "Pedestal at V_w + v against the ground-referenced cell at v (seven held voltages, 0.3 to 0.9 V + V_w).", "",
         "| channel | V_w (V) | held range (V) | pedestal range (µV) | max difference from V_w = 0 (µV) |", "|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {'nominal' if r['seed'] == 0 else 'Monte Carlo ' + str(r['seed'])} | {r['v_w']:g} | "
                 f"{r['v_hold'][0]:.1f} to {r['v_hold'][-1]:.1f} | {min(r['pedestal']) * 1e6:.0f} to {max(r['pedestal']) * 1e6:.0f} | "
                 f"{r['max_diff_from_v_w0'] * 1e6:.3f} |")
    (OUT / "offset_well.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
