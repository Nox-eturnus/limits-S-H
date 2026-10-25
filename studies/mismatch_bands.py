"""Worst-channel mismatch margins in every temperature band, and a test of the Gaussian tail.

Runs the pedestal Monte Carlo of studies/cryogenic.py (mismatch x 1) for the six designs of the
temperature study in all six bands, with 20 channels each, and judges them as studies/mismatch.py
does: shared calibration |r| + z_N sigma, and per-channel two-point calibration (mean + z_N sd of
the remaining nonlinearity). The margin of the nominal cell is kept for comparison.

The 4 K band is extended to 100 channels for the two cells whose margins sit near one (transistor-
level bootstrapped switch, TG with dummies), to test the Gaussian tail that the z_N extrapolation
assumes (Shapiro-Wilk, excess kurtosis, largest deviation against its expectation).

Decks share the work directories of studies/cryogenic.py, so cached decks are reused. New .raw files
are deleted after measurement to save disk; every channel is appended to
results/mismatch_bands_channels.jsonl, so an interrupted run resumes without re-simulating.
Run:  python studies/mismatch_bands.py           (about 2.5 h on 28 threads)
      python studies/mismatch_bands.py analyse   (seconds, from the stored channels)
Writes results/mismatch_bands.{json,md}.
"""
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
sys.path.insert(0, str(ROOT / "studies"))
import cryogenic as R  # noqa: E402
import mismatch as W  # noqa: E402
from flow import holdstage as H  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
LOG = OUT / "mismatch_bands_channels.jsonl"
FIG6 = [d for d in R.DESIGNS if d != "bootstrapped, 0.3 V underdrive"]     # the six designs of the temperature study
N_BAND = 20
TAIL = {"bootstrapped (transistor level), 0.3 V underdrive": 100, "TG + dummies": 100}
THREADS = 28
_lock = threading.Lock()


def run_one(name, band, seed):
    kw = R.DESIGNS[name]
    c = R.BANDS[band] or (0.0, 1.0)
    cryo = (c[0], c[1], 1.0) + (tuple(c[3:5]) if len(c) > 4 else ())
    cfg = R.E.base_cfg(workdir=R._wd("mm", name, band, 1.0), cryo=cryo, mismatch=True, seed=seed, **kw)
    wd = Path(cfg.workdir)
    before = set(wd.glob("*.raw")) if wd.exists() else set()
    try:
        m = H.measure(cfg)
        rec = {"design": name, "band": band, "seed": seed, "pedestal": m["pedestal"].tolist(),
               "ok": (np.abs(m["track_error"]) < R.TRACK_TOL).tolist()}
    except Exception as e:
        rec = {"design": name, "band": band, "seed": seed, "error": str(e).splitlines()[0][:200]}
    for f in set(wd.glob(f"*_mm{seed}_*.raw")) - before:    # keep cached decks, drop this seed's new ones
        f.unlink(missing_ok=True)
    with _lock, LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


def load_log():
    if not LOG.exists():
        return {}
    out = {}
    for line in LOG.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        out[(r["design"], r["band"], r["seed"])] = r
    return out


def simulate():
    R.C.spice.REUSE = R.C.spice.STRICT = R.C.spice.RETRY_RELAXED = True
    R.C.spice.TIMEOUT = 3600
    done = load_log()
    jobs = [(d, b, s) for d in FIG6 for b in R.BANDS for s in range(1, N_BAND + 1)]
    jobs += [(d, "4 K proxy", s) for d, n in TAIL.items() for s in range(N_BAND + 1, n + 1)]
    jobs = [j for j in jobs if j not in done]
    print(f"{len(jobs)} decks to run, {len(done)} already logged", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(THREADS) as ex:
        for i, _ in enumerate(ex.map(lambda j: run_one(*j), jobs)):
            if (i + 1) % 20 == 0 or i + 1 == len(jobs):
                print(f"  {i + 1}/{len(jobs)} ({time.time() - t0:.0f} s)", flush=True)


def analyse():
    """Margins per design and band at the strictest point, plus a tail check on the long runs."""
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    spec = {k: res["spec"][k] for k in (W.WORST, W.REF)}
    sw = {(r["design"], r["band"]): r for r in res["switching"]
          if r and "error" not in r and r["corner"] == "tt"}
    log = load_log()
    out = {"z": {f"{N:.0e}": W.z_max(N) for N in W.N_ARRAY}, "bands": {}, "tail": {}}
    for d in FIG6:
        for b in R.BANDS:
            rows = [log[(d, b, s)] for s in range(1, N_BAND + 1) if (d, b, s) in log and "error" not in log[(d, b, s)]]
            nominal = sw.get((d, b))
            if len(rows) < 5 or not nominal:
                continue
            peds = np.array([r["pedestal"] for r in rows])
            ok = np.all([r["ok"] for r in rows], axis=0) & (np.abs(nominal["track_error"]) < R.TRACK_TOL)
            if ok.sum() < 3:
                continue
            resid = nominal["residual"] if np.isfinite(nominal["residual"]) else 0.0
            r = W.judge(peds, nominal["v_hold"], ok, resid, spec)
            r["nominal_margin"] = {k: spec[k] / max(resid, 1e-12) for k in spec}
            r["n_failed_seeds"] = N_BAND - len(rows)
            out["bands"][f"{d}|{b}"] = r
    for d, n in TAIL.items():
        rows = [log[(d, "4 K proxy", s)] for s in range(1, n + 1)
                if (d, "4 K proxy", s) in log and "error" not in log[(d, "4 K proxy", s)]]
        if len(rows) < 30:
            continue
        nominal = sw[(d, "4 K proxy")]
        peds = np.array([r["pedestal"] for r in rows])
        ok = np.all([r["ok"] for r in rows], axis=0) & (np.abs(nominal["track_error"]) < R.TRACK_TOL)
        r = W.judge(peds, nominal["v_hold"], ok, nominal["residual"], spec)
        x = peds[:, ok]
        k = int(np.argmax(x.std(axis=0, ddof=1)))                  # the held voltage that sets sigma
        dev = (x[:, k] - x[:, k].mean()) / x[:, k].std(ddof=1)
        pc = W.per_channel_residuals(x, np.asarray(nominal["v_hold"])[ok], np.ones(x.shape[1], bool))
        from scipy import stats
        r["tail"] = {"n": len(rows), "shapiro_p_pedestal": float(stats.shapiro(dev).pvalue),
                     "max_abs_z_pedestal": float(np.abs(dev).max()),
                     "expected_max_abs_z": W.z_max(len(rows)),
                     "kurtosis_excess_pedestal": float(stats.kurtosis(dev)),
                     "shapiro_p_per_channel": float(stats.shapiro(pc).pvalue),
                     "per_channel_max_over_mean_plus_zsd": float((pc.max() - pc.mean()) / pc.std(ddof=1)),
                     "expected_z_for_n": W.z_max(len(rows))}
        out["tail"][d] = r
    (OUT / "mismatch_bands.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def table(out):
    L = ["## Worst-channel margins in every band (s = 33.69 dec/V, 99.99 %, worst of 10^6 channels)", "",
         f"{N_BAND} Monte Carlo channels per design and band, mismatch × 1. Nominal: spec / nominal residual. "
         "Shared: spec / (|r| + z σ). Per-channel: spec / (mean + z sd) of the per-channel two-point residual.", "",
         "| design | band | n | nominal | shared cal. | shared, σ 95 % upper | per-channel cal. |", "|---|---|---|---|---|---|---|"]
    for k, r in out["bands"].items():
        d, b = k.split("|")
        m = r["margins"][W.WORST]
        L.append(f"| {d} | {b} | {r['n_mc']} | {r['nominal_margin'][W.WORST]:.3g} | {m['shared_N1e+06']:.3g} | "
                 f"{m['shared_N1e+06_sigma_upper']:.3g} | {m['per_channel_N1e+06']:.3g} |")
    L += ["", "## Tail check, 4 K band", "",
          "| design | n | σ (µV) | shared, worst of 10^6 | per-channel, worst of 10^6 | Shapiro p (pedestal) | max |z| seen / expected "
          "| excess kurtosis | Shapiro p (per-channel residual) |", "|---|---|---|---|---|---|---|---|---|"]
    for d, r in out["tail"].items():
        t, m = r["tail"], r["margins"][W.WORST]
        L.append(f"| {d} | {t['n']} | {r['sigma'] * 1e6:.3g} | {m['shared_N1e+06']:.3g} | {m['per_channel_N1e+06']:.3g} | "
                 f"{t['shapiro_p_pedestal']:.2g} | {t['max_abs_z_pedestal']:.2f} / {t['expected_max_abs_z']:.2f} | "
                 f"{t['kurtosis_excess_pedestal']:.2f} | {t['shapiro_p_per_channel']:.2g} |")
    (OUT / "mismatch_bands.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if "analyse" not in sys.argv:
        simulate()
    table(analyse())
