"""Scaled-sigma check of the NMOS switch on multi-voltage decks (one Monte Carlo seed per row).

20 Monte Carlo rows of the NMOS cell in the 4 K band with every mismatch coefficient scaled by s = 2.5, 3
and 5.3 (the mm element of the cryo tuple, flow/pdk.py), scaled-sigma sampling after Sun and Li (IEEE TCAD
2015). The worst of 20 rows at scale s lies about 1.87 s standard deviations of the unscaled mismatch into
the tail, i.e. about 4.6 and 5.5 sigma, which brackets the worst of 10^6 channels (about 4.8 sigma); s = 5.3
(about 9.6 sigma) is the worst of 10^6 channels with twice the mismatch. Together with the runs at s = 1,
1.5 and 2 of studies/extra_bands.py it gives the window that every row tracks and the largest per-row
residual, both against the tail depth, compared with the Gaussian surrogate fitted at s = 1.

These decks place one switch instance per held voltage (see studies/tail_surrogate.py); the same check with
one cell per channel is studies/scaled_sigma_nmos.py.
Run:  python studies/high_sigma.py           (simulation, resumable; appends to results/high_sigma_channels.jsonl)
      python studies/high_sigma.py report    (analysis only; writes results/high_sigma.{json,md})
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import extra_bands as E  # noqa: E402

DESIGN = "NMOS, 0.3 V underdrive"
SCALES_NEW = (2.5, 3.0, 5.3)
N_MC = 20
THREADS = 21
LOG = OUT / "high_sigma_channels.jsonl"


def variants():
    v = {f"4 K, mismatch x {s:g}": dict(cryo=E.BAND_4K[:2] + (s,), mm=s) for s in SCALES_NEW}
    return v


def simulate():
    E.variants = variants                         # cfg_for() and run_one() read the variant table and the log
    E.LOG = LOG
    E.C.spice.REUSE = E.C.spice.STRICT = E.C.spice.RETRY_RELAXED = True
    E.C.spice.TIMEOUT = 14400
    done = E.load_log()
    jobs = [(DESIGN, v, s) for v in variants() for s in range(0, N_MC + 1)]
    jobs = [j for j in jobs if j not in done]
    print(f"{len(jobs)} decks to run, {len(done)} logged", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(THREADS) as ex:
        for i, _ in enumerate(ex.map(lambda j: E.run_one(*j), jobs)):
            print(f"  {i + 1}/{len(jobs)} ({time.time() - t0:.0f} s)", flush=True)


def per_channel(peds, v, mask):
    """Largest deviation of each channel from its own straight line over the voltages in mask."""
    x, y = np.asarray(v)[mask], np.asarray(peds)[:, mask]
    X = np.column_stack([np.ones_like(x), x])
    P = X @ np.linalg.pinv(X)
    return np.abs(y - y @ P.T).max(axis=1)


def load(path):
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["design"] == DESIGN:
            out.setdefault(r["variant"], {})[r["seed"]] = r
    return out


def report():
    runs = {**load(ROOT / "results" / "extra_bands_channels.jsonl"), **load(LOG)}
    base = json.loads((ROOT / "results" / "tail_surrogate_pedestals.json").read_text(encoding="utf-8"))[f"{DESIGN}|4 K proxy"]
    names = {1.0: None, 1.5: "4 K, mismatch x 1.5", 2.0: "4 K, mismatch x 2",
             2.5: "4 K, mismatch x 2.5", 3.0: "4 K, mismatch x 3", 5.3: "4 K, mismatch x 5.3"}
    bud = common.budgets()
    b_worst, b_99 = bud[common.WORST]["operational"], bud["s33.69_t0.001"]["operational"]
    v = np.array(base["v"])
    q20 = stats.norm.ppf(0.5 ** (1 / N_MC))                  # median depth of the worst of 20 (about 1.87)
    q6 = stats.norm.ppf(0.5 ** (1 / 1e6))                    # worst of 10^6 (about 4.9)
    # Gaussian surrogate at s = 1 (20 channels, as in the paper), scaled by s: what it predicts for the worst of 20
    ped1 = np.array(base["peds"])
    window1 = np.array(base["ok"])
    mu, cov = ped1[:, window1].mean(0), np.cov(ped1[:, window1].T)
    rng = np.random.default_rng(5)
    out = {"design": DESIGN, "v": v.tolist(), "budget_129": b_worst, "budget_404": b_99,
           "depth_worst20": q20, "depth_worst1e6": q6, "scales": {}}
    for s, name in names.items():
        if name is None:
            rows = [{"pedestal": p, "ok": [True] * len(v)} for p in base["peds"]]
            ok_all = window1
        else:
            rr = runs.get(name, {})
            nom = rr.get(0)
            rows = [rr[k] for k in range(1, N_MC + 1) if k in rr and "error" not in rr[k]]
            if not rows or nom is None:
                continue
            ok_all = np.array(nom["ok"]) & np.all([r["ok"] for r in rows], axis=0)
        peds = np.array([r["pedestal"] for r in rows])
        ok_each = np.array([r["ok"] for r in rows])
        top = [float(v[np.where(np.cumprod(o))[0].max()]) for o in ok_each]      # highest voltage of each channel's window
        win = v[ok_all]
        err = per_channel(peds, v, ok_all)
        # same window as at s = 1 (0.3-0.8 V), wherever every channel tracks it
        common_mask = window1 & ok_all
        err_c = per_channel(peds, v, common_mask)
        # surrogate prediction for the worst of 20 at scale s over the same window
        z = rng.multivariate_normal(np.zeros(len(mu)), cov, size=200000)
        idx = np.where(window1)[0]
        sel = [list(idx).index(i) for i in np.where(common_mask)[0]]
        synth = (mu + s * z)[:, sel]
        X = np.column_stack([np.ones(len(sel)), v[common_mask]])
        P = X @ np.linalg.pinv(X)
        e_syn = np.abs(synth - synth @ P.T).max(axis=1)
        pred20 = float(np.quantile(e_syn, 0.5 ** (1 / N_MC)))
        out["scales"][f"{s:g}"] = {
            "n": len(rows), "depth_sigma": s * q20, "window_all": [float(win.min()), float(win.max())],
            "top_tracked_min": min(top), "channels_losing_0.8V": int(sum(t < 0.8 - 1e-9 for t in top)),
            "channels_losing_0.7V": int(sum(t < 0.7 - 1e-9 for t in top)),
            "max_residual_own_window": float(err.max()), "max_residual_common_window": float(err_c.max()),
            "surrogate_pred_worst20": pred20, "common_window": v[common_mask].tolist()}
        print(f"s = {s:g}: depth {s * q20:.2f} sigma, window {win.min():.1f}-{win.max():.1f} V, "
              f"max residual {err.max() * 1e6:.1f} uV (window {v[common_mask].min():.1f}-{v[common_mask].max():.1f}: "
              f"{err_c.max() * 1e6:.1f} uV, surrogate {pred20 * 1e6:.1f} uV)", flush=True)
    (OUT / "high_sigma.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = [f"## Scaled-sigma check of {DESIGN}, 4 K band", "",
         f"20 channels per mismatch scale s; the worst of 20 lies about {q20:.2f} s sigma into the tail "
         f"(worst of 10^6: {q6:.2f} sigma). Budgets: {b_worst * 1e6:.0f} µV (99.99 %, 33.69 dec/V), "
         f"{b_99 * 1e6:.0f} µV (99.9 %, 33.69 dec/V).", "",
         "| scale s | depth of worst channel (sigma) | window on every channel | channels losing 0.8 V / 0.7 V "
         "| largest residual, own window | largest residual, 0.3-0.8 V window where tracked | surrogate (s = 1, scaled) prediction | margin at 129 µV |",
         "|---|---|---|---|---|---|---|---|"]
    for s, r in out["scales"].items():
        L.append(f"| {s} | {r['depth_sigma']:.2f} | {r['window_all'][0]:.1f}-{r['window_all'][1]:.1f} V | "
                 f"{r['channels_losing_0.8V']} / {r['channels_losing_0.7V']} of {r['n']} | {r['max_residual_own_window'] * 1e6:.1f} µV | "
                 f"{r['max_residual_common_window'] * 1e6:.1f} µV ({r['common_window'][0]:.1f}-{r['common_window'][-1]:.1f} V) | "
                 f"{r['surrogate_pred_worst20'] * 1e6:.1f} µV | {b_worst / r['max_residual_own_window']:.2f} |")
    (OUT / "high_sigma.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if "report" not in sys.argv:
        simulate()
    report()
