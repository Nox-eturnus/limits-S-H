"""System figures away from the reference operating point, and the quantities that depend on them.

A. The cold-stage load, DACs and slot time of 10^6 electrodes (the rows of studies/system.py: best tree, addressing
   energy, DACs of 157 uW) at 46.5 mV/s, 3.1 mV/s and 5.5 uV/s on 1 pF, first with the operational budget at 10 dec/V
   and 99.9 % (reproduces results/system.json and the droop anchors), then at 33.69 dec/V and 99.99 %.
B. The static array at the lowest droop recomputed at the slope of each row of the pulse-driver table
   (studies/node_size.py, static_load, unchanged; 1 pF and 70 fF; 99.9 % and 99.99 %), and the coldest stage of each
   driver load of studies/pulse_drivers_one_array.py together with it.
C. The slot time at the highest droop: hold time over electrodes per DAC, from part A.
D. The lowest droop held within the untracked budget for equal signs, neither tracked nor centred: hold time and the
   electrodes per DAC of the best tree, at 10 dec/V and 99.9 % and at 33.69 dec/V, 100 and 15 MHz.
E. Reading a droop rate through the qubits at the lowest droop: the accuracy needed on the droop of one hold period
   (the rate error that costs a tenth of the budget, results/rate_error_and_devices.json part A) against the 1/f drift
   of the device over that period.
F. Sampled converter noise: the limits of the joint allocation (kT/C included), at which no droop budget remains, and
   the noise that keeps half and 90 % of the hold time of a noiseless converter, at 100 and 15 MHz.
G. Area lost to isolated wells (8.4 um band) for compact groups of cells at pitches of 22, 11 and 9 um.

Run:  python studies/system_operating_points.py     (about 15 min; writes results/system_operating_points.{json,md})
"""
import json
import math
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import node_size as NS  # noqa: E402
import system as SY  # noqa: E402
import system_budget as SB  # noqa: E402
import tree as T  # noqa: E402
from flow import cosim as C  # noqa: E402

N_ARRAY = 1e6
N_BAR = N_ARRAY * 2 / 3.5
ANCH = {"46.5 mV/s": 46.5e-3, "3.1 mV/s": 3.1e-3, "5.5 uV/s": 5.5e-6}
STAGES = (("20 mK", 19e-6), ("140 mK", 200e-6), ("1.2 K", 40e-3), ("4.2 K", 1.5))
KTC = 7.6e-6

res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
DES = T.designs(res)
BUD = common.budgets()
REF22 = json.loads((ROOT / "results" / "rate_error_and_devices.json").read_text(encoding="utf-8"))
OP = {s: REF22["A"][f"100|{s}|0.001"]["centred"]["b0"] for s in ("3.87", "10", "16.6", "33.69")}
OP4 = {s: REF22["A"][f"100|{s}|0.0001"]["centred"]["b0"] for s in ("3.87", "10", "16.6", "33.69")}
N_RET = T.RETICLE / C.TreeConfig().pitch ** 2


def row(r, spec, rate):
    """One row of Supplementary Table S25, as studies/system.py computes it."""
    bd = C.hold_budget(spec, r["residual"], 0.1)
    b = SB.best_tree(r, spec, rate, 2e-9)
    if not b["n"] > 0:
        return None
    cfg = C.TreeConfig(fanout=None if b["config"].startswith("Fone") else float(b["config"][1:].split("_")[0]),
                       w_tree=float(b["config"].split("_w")[1]))
    e_addr = SY.addressing_energy(b["n"], cfg)
    hold = bd / rate
    p_ref, p_addr = b["p_per_electrode"], e_addr / hold
    n_cap = min(b["n"], N_RET)
    return {"n": b["n"], "hold_s": hold, "slot_s": hold / b["n"], "p_refresh_W": p_ref, "p_addressing_W": p_addr,
            "cold_load_W": N_ARRAY * (p_ref + p_addr), "dacs": math.ceil(N_ARRAY / n_cap)}


def part_a():
    out = {}
    for lab, spec in (("10|0.001", BUD["s10_t0.001"]["operational"]), ("33.69|0.0001", BUD["s33.69_t0.0001"]["operational"])):
        for an, rate in ANCH.items():
            for name, r in DES.items():
                if name == "TG, ESD on the node":
                    continue
                out[f"{lab}|{an}|{name}"] = row(r, spec, rate)
    return out


def coldest(p, static):
    for name, cap in STAGES:
        if p + static <= cap:
            return name
    return "above 4.2 K"


def part_b():
    out = {"static": {}, "stage": {}}
    for c, pitch in ((1e-12, 22e-6), (70e-15, 9e-6)):
        for s in ("3.87", "10", "16.6", "33.69"):
            for tgt, spec in (("0.001", OP[s]), ("0.0001", OP4[s])):
                loads = {}
                for d in NS.DESIGNS:
                    v = NS.static_load(DES[d], spec, c, pitch)["cold_load_W"]
                    loads[d] = v if np.isfinite(v) else None
                out["static"][f"{c * 1e15:g}|{s}|{tgt}"] = loads
    for c in (1e-12, 70e-15):
        for s in ("3.87", "10", "16.6", "33.69"):
            ld = [v for v in out["static"][f"{c * 1e15:g}|{s}|0.001"].values() if v is not None]
            st = max(ld)
            st4 = max(v for v in out["static"][f"{c * 1e15:g}|{s}|0.0001"].values() if v is not None)
            v0 = 2.6 / float(s)
            row_ = {"static_max_W": st, "static_max_9999_W": st4}
            for k in (0.5, 0.9):
                e = c * (1 - k) * v0 ** 2 / k
                for rt in (1e-6, 10e-6):
                    p = e * N_BAR / rt
                    row_[f"k{k}_{rt * 1e6:g}us"] = {"P_W": p, "stage": coldest(p, st), "stage_9999": coldest(p, st4),
                                                    "stage_ref_static": coldest(p, 1.4e-6 if c == 1e-12 else 7.7e-6)}
            out["stage"][f"{c * 1e15:g}|{s}"] = row_
    return out


def part_d():
    out = {}
    cases = {"10|0.001|100": 0.799e-3, "33.69|0.0001|100": REF22["B"]["100|0.0001"]["b_eq"],
             "33.69|0.0001|15": REF22["B"]["15|0.0001"]["b_eq"], "33.69|0.001|15": REF22["B"]["15|0.001"]["b_eq"]}
    rate = 5.5e-6
    for lab, beq in cases.items():
        best = {}
        for name in ("NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive", "TG + dummies"):
            r = DES[name]
            bd = C.hold_budget(beq, r["residual"], 0.1, centred=False)
            hold = bd / rate
            nbest = 0.0
            for f in T.FANOUTS:
                for w in T.W_TREE:
                    n = C.n_max_tree(hold, r["cell"], beq, bd, replace(C.TreeConfig(), fanout=f, w_tree=w))
                    nbest = max(nbest, n)
            best[name] = {"hold_s": hold, "n": nbest, "reticle": nbest >= N_RET}
        out[lab] = {"b_eq": beq, "designs": best}
    return out


def part_e():
    out = {}
    for key, v in REF22["A"].items():
        if "idle" in key:
            continue
        b0, e10 = v["centred"]["b0"], v["centred"]["eps10"]
        bd = 0.9 * b0
        T_h = 2 * bd / 5.5e-6
        need = e10 * 2 * bd
        drift = [A * math.sqrt(math.log(T_h)) for A in (9e-6, 49e-6)]
        out[key] = {"hold_s": T_h, "need_V": need, "drift_V": drift, "ratio": [d / need for d in drift]}
    return out


def part_f():
    out = {}
    for key in ("100|0.0001", "15|0.0001"):
        v = REF22["B"][key]
        b, share = v["b_ind"], v["share"]["9"]
        f0 = math.sqrt(1 - share - (KTC / b) ** 2)
        rows = {}
        for name, m in (("tuned", math.inf), ("NMOS", v["designs"]["NMOS"]["full"]),
                        ("bootstrapped", v["designs"]["bootstrapped"]["full"]),
                        ("TG + dummies", v["designs"]["TG + dummies"]["full"])):
            floor = 0.1 + (0.0 if m == math.inf else 1 / m)
            if f0 <= floor:
                rows[name] = None
                continue
            sig = lambda need: b * math.sqrt(max(1 - share - need ** 2 - (KTC / b) ** 2, 0.0))  # noqa: E731
            rows[name] = {"zero": sig(floor), "half": sig(floor + 0.5 * (f0 - floor)),
                          "ninety": sig(floor + 0.9 * (f0 - floor))}
        out[key] = rows
    return out


def part_g():
    return {f"{p:g}": {f"{n}": (((n ** 0.5) * p + 8.4) / ((n ** 0.5) * p)) ** 2 - 1 for n in (100, 25, 4, 1)}
            for p in (22.0, 11.0, 9.0)}


def main():
    out = {"A": part_a()}
    print("A done", flush=True)
    out["B"] = part_b()
    print("B done", flush=True)
    out["D"] = part_d()
    print("D done", flush=True)
    out["E"], out["F"], out["G"] = part_e(), part_f(), part_g()
    (OUT / "system_operating_points.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    L = ["# System figures away from the reference operating point", "", "## A. Table S25 at the reference point and the strictest point", "",
         "| point | droop | design | per DAC | DACs | hold (s) | slot (us) | refresh / addressing per electrode | cold load |",
         "|---|---|---|---|---|---|---|---|---|"]
    for k, v in out["A"].items():
        lab, an, name = k.split("|", 2)[0] + "|" + k.split("|")[1], k.split("|")[2], k.split("|", 3)[3]
        if v is None:
            L.append(f"| {lab} | {an} | {name} | no droop budget | | | | | |")
            continue
        L.append(f"| {lab} | {an} | {name} | {v['n']:.3g} | {v['dacs']} | {v['hold_s']:.3g} | {v['slot_s'] * 1e6:.3g} | "
                 f"{v['p_refresh_W'] * 1e12:.3g} / {v['p_addressing_W'] * 1e12:.3g} pW | {v['cold_load_W'] * 1e6:.3g} uW |")
    L += ["", "## B. Table S27: static array at each row's slope (uW, NMOS / bootstrapped / TG with dummies) and stages", ""]
    for k, v in out["B"]["static"].items():
        L.append(f"- {k}: " + ", ".join("none" if x is None else f"{x * 1e6:.3g}" for x in v.values()))
    L += ["", "| node fF / slope | static max (uW) 99.9 / 99.99 % | k=0.5: 1 us / 10 us | k=0.9: 1 us / 10 us | same at 99.99 % | stored-static stages, same order |", "|---|---|---|---|---|---|"]
    for k, v in out["B"]["stage"].items():
        L.append(f"| {k} | {v['static_max_W'] * 1e6:.3g} / {v['static_max_9999_W'] * 1e6:.3g} | {v['k0.5_1us']['stage']} / {v['k0.5_10us']['stage']} | "
                 f"{v['k0.9_1us']['stage']} / {v['k0.9_10us']['stage']} | {v['k0.5_1us']['stage_9999']} / {v['k0.5_10us']['stage_9999']}; "
                 f"{v['k0.9_1us']['stage_9999']} / {v['k0.9_10us']['stage_9999']} | {v['k0.5_1us']['stage_ref_static']} / "
                 f"{v['k0.5_10us']['stage_ref_static']}; {v['k0.9_1us']['stage_ref_static']} / {v['k0.9_10us']['stage_ref_static']} |")
    L += ["", "## D. Lowest droop held within the untracked budget for equal signs, no tracking, no centring", ""]
    for k, v in out["D"].items():
        L.append(f"- {k}: b_eq {v['b_eq'] * 1e6:.1f} uV; " + "; ".join(
            f"{n.split(',')[0].split(' (')[0]} hold {d['hold_s']:.3g} s, per DAC {d['n']:.3g} ({'reticle' if d['reticle'] else 'below a reticle'})"
            for n, d in v["designs"].items()))
    L += ["", "## E. Droop of one hold period at 5.5 uV/s: accuracy needed against the device drift", ""]
    for k, v in out["E"].items():
        L.append(f"- {k}: hold {v['hold_s']:.3g} s, needed {v['need_V'] * 1e6:.1f} uV, drift {v['drift_V'][0] * 1e6:.1f}-{v['drift_V'][1] * 1e6:.1f} uV, ratio {v['ratio'][0]:.2f}-{v['ratio'][1]:.2f}")
    L += ["", "## F. Sampled converter noise (uV rms): no droop budget / half / 90 % of the hold time", ""]
    for k, v in out["F"].items():
        L.append(f"- {k}: " + "; ".join(f"{n} " + ("none" if d is None else f"{d['zero'] * 1e6:.1f} / {d['half'] * 1e6:.1f} / {d['ninety'] * 1e6:.1f}") for n, d in v.items()))
    L += ["", "## G. Area lost to isolated wells (groups of 100 / 25 / 4 / 1)", ""]
    for k, v in out["G"].items():
        L.append(f"- pitch {k} um: " + ", ".join(f"{n}: {x:.0%}" for n, x in v.items()))
    (OUT / "system_operating_points.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
