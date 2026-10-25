"""Channel mismatch judged on the worst channel of an array.

Mismatch does not change from one refresh to the next. For a given channel it is a fixed offset, so
the static budget applies to that channel, and an array of N channels is limited by its worst one.
Deterministic errors on one electrode add as voltages, so with a shared calibration the worst channel
carries |residual| + z(N) sigma, where z(N) is the median of the largest of N two-sided Gaussian
deviates. With a per-channel calibration, each Monte Carlo channel gets its own two-point (linear)
calibration, and the spread of its remaining nonlinearity is extrapolated to N channels. The RMS
margin (budget / sigma) is kept in the output for comparison.

Inputs: the Monte Carlo decks of studies/cells.py (300 K, 20 seeds, re-read from build/cells without
re-simulating, so cells.py must have run on this machine) and the per-seed pedestals of
studies/cryogenic.py (4 K proxy, 12 seeds, mismatch x 1, 1.5, 2).
Run:  python studies/mismatch.py      (about 1 min; writes results/mismatch.{json,md})
"""
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flow import holdstage as H  # noqa: E402
from flow import spice  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
WORST, REF = "s33.69_t0.0001", "s10_t0.001"
N_ARRAY = (1e3, 1e4, 1e6, 1.8e6)               # 1.8e6: one reticle at the 22 um pitch
N_MC_D = 20
THICK, NMOS_ONLY = ("TSW", "TSWB"), ("NSW", "NTB")
ARCH_NAMES = {"NSW": "NMOS switch", "TG": "TG", "TGD": "TG with dummies", "BOOT": "bootstrapped NMOS",
              "CLK": "charge-locked TG", "TSW": "thick-oxide T-switch", "TGH": "TG, high-threshold PMOS",
              "TSWB": "T-switch, buffered, thick oxide", "NTB": "T-switch, buffered, thin oxide"}


def z_max(n):
    """Median of max |x_i| over n standard Gaussian deviates: (2 Phi(z) - 1)^n = 1/2."""
    return float(optimize.brentq(lambda z: n * np.log(2 * stats.norm.cdf(z) - 1) - np.log(0.5), 0.5, 10))


def sigma_upper(sig, n, conf=0.95):
    """One-sided upper confidence bound on sigma from n samples (chi-square)."""
    return sig * np.sqrt((n - 1) / stats.chi2.ppf(1 - conf, n - 1))


def per_channel_residuals(peds, v, ok):
    """Each channel (row) calibrated on its own straight line over the passed voltages: max |dev|."""
    x = np.asarray(v)[ok]
    out = []
    for p in peds:
        y = np.asarray(p)[ok]
        c = np.polyfit(x, y, 1)
        out.append(float(np.max(np.abs(y - np.polyval(c, x)))))
    return np.array(out)


def judge(peds, v, ok, resid_nom, spec):
    """Margins for one design: shared calibration (worst channel of N) and per-channel calibration."""
    peds = np.asarray(peds)[:, ok]
    n = len(peds)
    sig = float(peds.std(axis=0, ddof=1).max())
    sig_hi = float(sigma_upper(sig, n))
    pc = per_channel_residuals(peds, np.asarray(v)[ok], np.ones(peds.shape[1], bool))
    r = {"n_mc": n, "sigma": sig, "sigma_upper95": sig_hi, "residual_nominal": resid_nom,
         "per_channel_residual_max": float(pc.max()), "per_channel_residual_mean": float(pc.mean()),
         "per_channel_residual_sd": float(pc.std(ddof=1)), "spec": spec, "margins": {}}
    for key, s in spec.items():
        m = {"rms_1sigma": s / sig}
        for N in N_ARRAY:
            z = z_max(N)
            m[f"shared_N{N:.0e}"] = s / (abs(resid_nom) + z * sig)
            m[f"shared_N{N:.0e}_sigma_upper"] = s / (abs(resid_nom) + z * sig_hi)
            # per-channel calibration: the nonlinearity spread across channels, extrapolated to N
            m[f"per_channel_N{N:.0e}"] = s / (pc.mean() + z * pc.std(ddof=1))
        m["per_channel_mc_max"] = s / pc.max()
        r["margins"][key] = m
    return r


def phase_d():
    """Re-read the Monte Carlo decks of studies/cells.py (spice.REUSE); a deck that is not cached raises."""
    res = json.loads((ROOT / "results" / "cells.json").read_text(encoding="utf-8"))
    spec = {k: res["spec"][k]["static"] for k in (WORST, REF)}
    spice.REUSE = True
    real_run = spice._run

    def no_sim(*a, **k):
        raise RuntimeError("Monte Carlo deck not cached")
    spice._run = no_sim
    out = {}
    try:
        for arch, a in res["archs"].items():
            base = H.HoldConfig(arch=arch, workdir=f"build/cells/{arch}")     # as studies/cells.py (run from the repository root)
            if arch in NMOS_ONLY:
                base = replace(base, v_hold=tuple(np.round(np.linspace(0.3, 0.9, 7), 3)))
            peds = []
            for seed in range(1, N_MC_D + 1):
                try:
                    peds.append(H.measure(replace(base, mismatch=True, seed=seed))["pedestal"])
                except Exception as e:
                    print(f"  {arch} seed {seed}: {str(e).splitlines()[0][:80]}", flush=True)
            peds = np.array(peds)
            ok = np.ones(peds.shape[1], bool)
            resid = a["nominal"]["summary"]["pedestal_linear_residual"]
            r = judge(peds, base.v_hold, ok, resid, spec)
            r["sigma_population"] = a["mc"]["pedestal_sigma_max"]
            out[arch] = r
            print(f"{arch}: n = {r['n_mc']}, sigma {r['sigma'] * 1e6:.3g} uV (population {r['sigma_population'] * 1e6:.3g}), "
                  f"worst-channel margin at 1e6: {r['margins'][WORST]['shared_N1e+06']:.3g}", flush=True)
    finally:
        spice._run = real_run
        spice.REUSE = False
    return out


def phase_f():
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    spec = {k: res["spec"][k] for k in (WORST, REF)}
    sw = {r["design"]: r for r in res["switching"]
          if r and "error" not in r and r["band"] == "4 K proxy" and r["corner"] == "tt"}
    mm = [x for x in res["mismatch"] if x and "error" not in x]
    out = {}
    for d in dict.fromkeys(x["design"] for x in mm):
        nominal = sw.get(d)
        resid = nominal["residual"] if nominal and np.isfinite(nominal["residual"]) else 0.0
        v = nominal["v_hold"] if nominal else None
        for f in (1.0, 1.5, 2.0):
            rows = [x for x in mm if x["design"] == d and x["mm"] == f]
            peds = np.array([x["pedestal"] for x in rows])
            ok = np.all([x["ok"] for x in rows], axis=0)
            vv = v if v is not None else np.linspace(0.3, 1.5, peds.shape[1])
            r = judge(peds, vv, ok, resid, spec)
            out[f"{d}|{f:g}"] = r
            print(f"{d} x{f:g}: n = {r['n_mc']}, sigma {r['sigma'] * 1e6:.3g} uV, RMS margin "
                  f"{r['margins'][WORST]['rms_1sigma']:.3g}, worst of 1e6 {r['margins'][WORST]['shared_N1e+06']:.3g}",
                  flush=True)
    return out


def table(d, f):
    zs = ", ".join(f"z({N:.0e}) = {z_max(N):.2f}" for N in N_ARRAY)
    L = ["## Mismatch on the worst channel of an array", "",
         f"Margin = static spec / (|nominal residual| + z(N) σ), s = 33.69 dec/V, 99.99 % (168 µV). {zs}. "
         "'σ, 95 % upper' uses the one-sided chi-square bound on σ. Per-channel: every Monte Carlo channel "
         "calibrated on its own straight line; margin = spec / (mean + z(N) sd) of its remaining nonlinearity.", "",
         "### 300 K (studies/cells.py, 20 channels per held voltage)", "",
         "| cell | σ (µV) | RMS margin (budget / σ) | shared cal., worst of 10^4 | worst of 10^6 | worst of 10^6, σ 95 % upper "
         "| per-channel cal., worst of 10^6 | per-channel, Monte Carlo max |", "|---|---|---|---|---|---|---|---|"]
    for arch, r in d.items():
        m = r["margins"][WORST]
        L.append(f"| {ARCH_NAMES.get(arch, arch)} | {r['sigma'] * 1e6:.3g} | {m['rms_1sigma']:.3g} | "
                 f"{m['shared_N1e+04']:.3g} | {m['shared_N1e+06']:.3g} | {m['shared_N1e+06_sigma_upper']:.3g} | "
                 f"{m['per_channel_N1e+06']:.3g} | {m['per_channel_mc_max']:.3g} |")
    L += ["", "### 4 K proxy (studies/cryogenic.py, 12 channels per held voltage, mismatch scaled)", "",
          "| cell | mismatch × | σ (µV) | RMS margin (budget / σ) | shared cal., worst of 10^4 | worst of 10^6 "
          "| worst of 10^6, σ 95 % upper | per-channel cal., worst of 10^6 |", "|---|---|---|---|---|---|---|---|"]
    for k, r in f.items():
        name, sc = k.split("|")
        m = r["margins"][WORST]
        L.append(f"| {name} | {sc} | {r['sigma'] * 1e6:.3g} | {m['rms_1sigma']:.3g} | {m['shared_N1e+04']:.3g} | "
                 f"{m['shared_N1e+06']:.3g} | {m['shared_N1e+06_sigma_upper']:.3g} | {m['per_channel_N1e+06']:.3g} |")
    L.append("")
    return L


def main():
    d, f = phase_d(), phase_f()
    out = {"z": {f"{N:.0e}": z_max(N) for N in N_ARRAY}, "room_temperature": d, "cryogenic": f}
    (OUT / "mismatch.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT / "mismatch.md").write_text("\n".join(table(d, f)), encoding="utf-8")


if __name__ == "__main__":
    main()
