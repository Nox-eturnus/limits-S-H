"""A droop rate known with an error, the Si-MOS device at its own Zeeman difference, and the converter at 15 MHz.

A. Centring offsets each sample by half of the expected droop, so with an actual rate (1 + x) times the calibrated one
   the node runs from -b to b (1 + 2x) over a hold period, and the untracked part grows from 0 to 2x b. The accounting
   of studies/partial_tracking_qec.py (conditional phase as for M = 2, the untracked single-qubit phase of the four
   barriers around a data qubit added in amplitude) is applied to the total and the untracked offset at 41 points of the
   hold period, both signs; without centring the node runs from 0 to b (1 + x) with x b untracked. Outputs: the centred
   budget at x = 0, 0.03, 0.1, the rate error that costs a tenth of the budget, and the same without centring, at
   100 and 15 MHz (gate rule of studies/zeeman_device_scale.py part A), no idle time, and at 100 MHz with 1 us of idle
   time per layer. The budgets at x = 0 reproduce results/tracking_and_routing.json and results/partial_tracking_qec.json.
B. The margins at the slopes of measured devices (studies/system_operation.py, measured devices; tail correction and
   daily device share as studies/calibration_accuracy.py) for the device of Nickl et al. at 15 MHz (333 ns gate), with
   the 1/f budget for daily retuning from flow.budget.max_one_over_f, first at 100 MHz against the stored values.
C. The converter at 15 MHz: DAC step (twice the untracked single-gate budget) and the largest sampled white DAC noise
   of the joint allocation (quiet device), on a tuned level and for levels set open-loop.
D. Where the white-noise error of transitions between |01> and |10> lies: its share without the Stark shift at
   10 dec/V, and the band that holds 80 % of the transition part of the kernel, at 100 and 15 MHz.

Run:  python studies/rate_error_and_devices.py     (about 20 min; writes results/rate_error_and_devices.{json,md})
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
import partial_tracking_qec as PT  # noqa: E402
import cell_margins as CM  # noqa: E402
import array_yield as Y  # noqa: E402
import tail_corrected as Y8  # noqa: E402
from flow import budget as B  # noqa: E402
from repeated_gates import _PROJ_COND  # noqa: E402

SLOPES = (3.87, 10.0, 16.6, 33.69)
TARGETS = (1e-3, 1e-4)
U = np.linspace(0.0, 1.0, 41)
KTC = float(np.sqrt(1.380649e-23 * 4.2 / 1e-12))


def gate(dez, s, t_idle=0.0):
    tg = 50e-9 * 100e6 / dez
    return B.layer(s_dec_per_v=s, d_ez=dez, t_gate=tg, dt=max(5e-12, tg / 1e4), t_idle=t_idle)


# ------------------------------------------------------------------------------------------------------------- A
def phase_table(lay):
    xs = np.linspace(-8e-3, 8e-3, 3201)
    ph = np.array([lay.phase_errors(B.static(lay, x)) for x in xs])
    return lambda v: np.array([np.interp(v, xs, ph[:, k]) for k in range(4)])


def infid2(phf, v_tot, v_unt):
    pt, pu = phf(v_tot), phf(v_unt)
    return B.phase_infidelity(np.sqrt(common.M_QEC) * (_PROJ_COND @ pt) + 2.0 * (pu - _PROJ_COND @ pu))


def worst(phf, b, eps, centred):
    w = 0.0
    for sg in (+1, -1):
        for u in U:
            tot = b * (-1 + 2 * (1 + eps) * u) if centred else b * (1 + eps) * u
            unt = (2 if centred else 1) * eps * b * u
            w = max(w, infid2(phf, sg * tot, sg * unt))
    return w


def largest(fun, target, hi=8e-3):
    xs = np.geomspace(1e-6, hi, 120)
    vals = np.array([fun(x) - target for x in xs])
    i = np.nonzero(vals >= 0)[0][0]
    return brentq(lambda x: fun(x) - target, xs[i - 1], xs[i], xtol=xs[i - 1] * 1e-7)


def rate_case(lay, t):
    phf = phase_table(lay)
    out = {}
    for centred, lab in ((True, "centred"), (False, "plain")):
        b = lambda e: largest(lambda x: worst(phf, x, e, centred), t)  # noqa: E731
        b0 = b(0.0)
        out[lab] = {"b0": b0, "b003": b(0.03), "b01": b(0.1),
                    "eps10": brentq(lambda e: b(e) - 0.9 * b0, 1e-4, 1.0, xtol=1e-5)}
    return out


def part_a():
    s21 = json.loads((ROOT / "results" / "tracking_and_routing.json").read_text(encoding="utf-8"))["A"]
    part = json.loads((ROOT / "results" / "partial_tracking_qec.json").read_text(encoding="utf-8"))["rows"]
    out = {}
    for dez in (100e6, 15e6):
        for s in SLOPES:
            lay = gate(dez, s)
            for t in TARGETS:
                k = f"{dez / 1e6:g}|{s:g}|{t:g}"
                r = rate_case(lay, t)
                r["check_f0"] = [PT.budget(lay, t, 0.0), s21[k]["budget"]["0"]]
                out[k] = r
                print(f"A {k}: b0 {r['centred']['b0'] * 1e3:.4g} mV (stored {s21[k]['budget']['0'] * 1e3:.4g}); centred "
                      f"eps10 {r['centred']['eps10']:.4f}, b(0.03) {r['centred']['b003'] * 1e3:.3g}, b(0.1) "
                      f"{r['centred']['b01'] * 1e3:.3g} mV; plain eps10 {r['plain']['eps10']:.4f}, b(0.1) "
                      f"{r['plain']['b01'] * 1e3:.3g} mV", flush=True)
    for s in (10.0, 33.69):
        lay = gate(100e6, s, t_idle=1e-6)
        for t in TARGETS:
            k = f"idle|{s:g}|{t:g}"
            ref = next(r for r in part if r["s"] == s and r["t_idle"] == 1e-6 and r["target"] == t)["budget"]["0"]
            r = rate_case(lay, t)
            r["check_f0"] = [PT.budget(lay, t, 0.0), ref]
            out[k] = r
            print(f"A {k}: b0 {r['centred']['b0'] * 1e6:.4g} uV (stored {ref * 1e6:.4g}); centred eps10 "
                  f"{r['centred']['eps10']:.4f}, b(0.03) {r['centred']['b003'] * 1e3:.3g}, b(0.1) "
                  f"{r['centred']['b01'] * 1e3:.3g} mV", flush=True)
    return out


# ------------------------------------------------------------------------------------------------------------- B, C
NAMES = {"NMOS": ("NMOS, 0.3 V underdrive|4 K proxy", Y8.NMOS),
         "bootstrapped": ("bootstrapped (transistor level), 0.3 V underdrive|4 K proxy", Y8.BOOT),
         "TG + dummies": ("TG + dummies|4 K proxy", Y8.TGD), "TG": ("TG, no ESD|4 K proxy", Y8.TG),
         "T-switch + OTA": ("T-switch + OTA buffer|4 K proxy", Y8.TSWO)}


def moments():
    recs = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    mom = {}
    for lab, (name, _) in NAMES.items():
        x, v, std, nominal, _ = CM.prepare(recs[name])
        A = CM.residual_operator(v, std)
        mom[lab] = {k: Y.moments(x, v, std, A, nominal, k) for k in ("full", "shared")}
    return mom


def b_ind(lay, t):
    return min(B.max_static(lay, t, +1), B.max_static(lay, t, -1))


def part_bc():
    mom = moments()
    out_b, out_c = {}, {}
    for dez in (100e6, 15e6):
        lay = gate(dez, 33.69)
        for t in TARGETS:
            b = {"b_ind": b_ind(lay, t), "b_eq": PT.budget(lay, t, 1.0)}
            a_day = B.max_one_over_f(lay, t, 1 / 86400)
            share = {n: (n * 1e-6 / a_day) ** 2 + KTC ** 2 / b["b_ind"] ** 2 for n in (9, 49)}
            row = {"b_ind": b["b_ind"], "b_eq": b["b_eq"], "one_over_f_day": a_day, "share": share, "designs": {}}
            for lab, (_, d) in NAMES.items():
                tau = Y8.tau(d, "4 K proxy")
                full = Y.margin_closed(*mom[lab]["full"], b) / (1 + tau)
                row["designs"][lab] = {"full": full, "shared": Y.margin_closed(*mom[lab]["shared"], b) / (1 + tau),
                                       "joint_49": full * max(np.sqrt(max(1 - share[49], 0.0)) - 0.1, 0.0)}
            out_b[f"{dez / 1e6:g}|{t:g}"] = row
            print(f"B {dez / 1e6:g} MHz {t:g}: b_ind {b['b_ind'] * 1e6:.1f} b_eq {b['b_eq'] * 1e6:.1f} uV, 1/f "
                  f"{a_day * 1e6:.1f} uV/rtHz, share {share[9]:.3f} / {share[49]:.2f}; " + "; ".join(
                      f"{k} {v['full']:.3g}/{v['shared']:.3g}/{v['joint_49']:.3g}" for k, v in row["designs"].items()),
                  flush=True)
            if t == 1e-4:
                c = {"step_V": 2 * b["b_ind"], "bits": float(np.log2(1.2 / (2 * b["b_ind"]))),
                     "noise_tuned_V": b["b_ind"] * np.sqrt(max(1 - share[9] - 0.01, 0.0)), "noise_open_V": {}}
                for lab in ("NMOS", "bootstrapped", "TG + dummies"):
                    m = row["designs"][lab]["full"]
                    x = 1 - share[9] - (0.1 + 1 / m) ** 2
                    c["noise_open_V"][lab] = b["b_ind"] * np.sqrt(x) if x > 0 else 0.0
                out_c[f"{dez / 1e6:g}|33.69|0.0001"] = c
        lay10 = gate(dez, 10.0)
        bi = b_ind(lay10, 1e-3)
        out_c[f"{dez / 1e6:g}|10|0.001"] = {"step_V": 2 * bi, "bits": float(np.log2(1.2 / (2 * bi)))}
        print(f"C {dez / 1e6:g} MHz: " + json.dumps(
            {k: v for k, v in out_c.items() if k.startswith(f"{dez / 1e6:g}|")}, default=float), flush=True)
    return out_b, out_c


# ------------------------------------------------------------------------------------------------------------- D
def transition_part(lay, f):
    gx = lay.transverse_sensitivity()
    ph = np.exp(-1j * 2 * np.pi * np.outer(f, lay.t)) * lay.dts
    return 0.2 * (np.abs(ph @ gx) ** 2 + np.abs(ph.conj() @ gx) ** 2)


def part_d():
    out = {}
    for dez in (100e6, 15e6):
        tg = 50e-9 * 100e6 / dez
        lay = B.layer(s_dec_per_v=10.0, d_ez=dez, t_gate=tg, dt=max(5e-12, tg / 1e4), stark_q2=0.0)
        ph, tr = lay.white_noise_infidelity(1.0, split=True)
        f = np.geomspace(1e5, 2e9, 1500)
        k = transition_part(lay, f)
        cum = np.concatenate([[0], np.cumsum(0.5 * (k[1:] + k[:-1]) * np.diff(f))])
        cum /= cum[-1]
        lo, hi = float(np.interp(0.1, cum, f)), float(np.interp(0.9, cum, f))
        out[f"{dez / 1e6:g}"] = {"transition_share": tr / (ph + tr), "band80_Hz": [lo, hi], "peak_Hz": float(f[np.argmax(k)])}
        print(f"D {dez / 1e6:g} MHz: transitions {100 * tr / (ph + tr):.0f}% of white-noise error; 80% of the transition "
              f"kernel between {lo / 1e6:.3g} and {hi / 1e6:.3g} MHz, peak {f[np.argmax(k)] / 1e6:.3g} MHz", flush=True)
    return out


def report(res):
    a, b, c, d = res["A"], res["B"], res["C"], res["D"]
    L = ["# A centred droop with a rate error, the Si-MOS device at 15 MHz, the converter at 15 MHz", "",
         "## A. Operational budget (mV) for a droop whose rate is in error by eps", "",
         "| case | s (dec/V) | target | b(0) | centred b(0.03) | centred b(0.1) | centred eps_10 | plain b(0.1) | plain eps_10 |",
         "|---|---|---|---|---|---|---|---|---|"]
    for k, v in a.items():
        case, s, t = k.split("|")
        cen, pl = v["centred"], v["plain"]
        L.append(f"| {case + ' MHz' if case != 'idle' else '100 MHz, 1 us idle'} | {s} | {t} | {cen['b0'] * 1e3:.3g} | "
                 f"{cen['b003'] * 1e3:.3g} | {cen['b01'] * 1e3:.3g} | {cen['eps10']:.3f} | {pl['b01'] * 1e3:.3g} | "
                 f"{pl['eps10']:.3f} |")
    L += ["", "## B. Supplementary Table S22, device of Nickl et al. (33.69 dec/V), 4 K band, closed form with the tail "
          "correction: per channel / shared / joint with 49 uV/rtHz", "",
          "| Zeeman | target | b_eq / b_ind (uV) | 1/f budget, daily (uV/rtHz) | share 9 / 49 | " + " | ".join(NAMES) + " |",
          "|---|---|---|---|---|" + "---|" * len(NAMES)]
    for k, v in b.items():
        z, t = k.split("|")
        L.append(f"| {z} MHz | {t} | {v['b_eq'] * 1e6:.1f} / {v['b_ind'] * 1e6:.1f} | {v['one_over_f_day'] * 1e6:.1f} | "
                 f"{v['share'][9]:.3f} / {v['share'][49]:.2f} | " + " | ".join(
                     f"{x['full']:.3g} / {x['shared']:.3g} / {x['joint_49']:.3g}" for x in v["designs"].values()) + " |")
    L += ["", "## C. Converter", ""]
    for k, v in c.items():
        L.append(f"- {k}: step < {v['step_V'] * 1e3:.3g} mV ({v['bits']:.1f} bits over 1.2 V)" + (
            f"; sampled noise, tuned level {v['noise_tuned_V'] * 1e6:.0f} uV rms; open-loop " + ", ".join(
                f"{n} {x * 1e6:.0f} uV" for n, x in v["noise_open_V"].items()) if "noise_tuned_V" in v else ""))
    L += ["", "## D. White-noise transitions, 10 dec/V, no Stark shift", ""]
    for k, v in d.items():
        L.append(f"- {k} MHz: {100 * v['transition_share']:.0f}% of the white-noise error; 80% of the transition kernel "
                 f"between {v['band80_Hz'][0] / 1e6:.3g} and {v['band80_Hz'][1] / 1e6:.3g} MHz, peak {v['peak_Hz'] / 1e6:.3g} MHz")
    (OUT / "rate_error_and_devices.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    res = {"D": part_d()}
    res["B"], res["C"] = part_bc()
    res["A"] = part_a()
    (OUT / "rate_error_and_devices.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    report(res)


if __name__ == "__main__":
    main()
