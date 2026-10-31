"""Worst-channel margins from the one-cell-per-channel Monte Carlo (studies/mc_cell.py).

The accounting is that of studies/residual_accounting.py (untracked budget; the deviation of a channel from its
calibration line split into the deviation of the mean channel, common to all channels, and the part that
mismatch adds; the worst of 10^6 channels from a Gaussian surrogate with a 90 % bootstrap interval), with:

1. Each row of pedestals is one cell, so the surrogate carries the correlation of a cell's pedestal across
   held voltages.
2. The surrogate is sampled in the space of the principal components of the Monte Carlo channels
   (rank min(n - 1, number of held voltages)), which is the same Gaussian and also covers the fine grid,
   where there are more held voltages than channels.
3. The calibration line is fitted on the standard seven held voltages that every channel tracks; the
   deviation is evaluated there ("full") and, on the fine grid (20 mV steps), at every simulated voltage. The
   error of a level tuned on the qubits and moved by up to Delta is the change of the deviation between
   simulated held voltages at most Delta apart. Where only the standard grid exists, the change below the grid
   step is interpolated linearly and flagged.

studies/tail_corrected.py divides these margins by the measured tail optimism of the surrogate.
Run:  python studies/cell_margins.py [merge]     (about 3 h on 12 processes; resumes if interrupted)
Writes results/cell_margins.{json,md}.
"""
import json
import os
import sys
import zlib

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import residual_accounting as RA  # noqa: E402

N_ARRAY = 1e6
Q_WORST = 0.5 ** (1 / N_ARRAY)
S_IS = 1.8
N_POINT = 1_000_000
N_BOOT = 300
N_BOOT_SAMPLE = 100_000
CHUNK = 250_000
SPANS = (0.02, 0.05, 0.1, 0.2)
KEYS = (common.WORST, "s33.69_t0.001", common.REF)
STD_TOL = 1e-6


def standard_mask(v, design_v):
    """The standard seven held voltages (0.3-1.5 V in 0.2 V steps, or 0.3-0.9 V in 0.1 V steps)."""
    lo, hi = min(design_v), max(design_v)
    step = 0.1 if hi <= 0.95 else 0.2
    return np.array([abs((x - 0.3) / step - round((x - 0.3) / step)) < 1e-6 for x in v])


def residual_operator(v, cal):
    """r = p - line, with the line fitted by least squares on the voltages in cal: r = A p."""
    X = np.column_stack([np.ones(cal.sum()), v[cal]])
    coef = np.linalg.pinv(X)                                # (2, n_cal)
    full = np.column_stack([np.ones(len(v)), v])
    A = np.eye(len(v))
    A[:, cal] -= full @ coef
    return A


def move_pairs(v, std, span, fine):
    """(j, k, scale): pairs of held voltages at most span apart. On a fine grid, simulated pairs only; else
    pairs on the standard grid, and below its step the adjacent pairs scaled by span / step (interpolated)."""
    idx = np.arange(len(v)) if fine else np.where(std)[0]
    out = [(j, k, 1.0) for a, j in enumerate(idx) for k in idx[a + 1:] if v[k] - v[j] <= span + 1e-9]
    interp = False
    if not out:
        out = [(idx[a], idx[a + 1], span / (v[idx[a + 1]] - v[idx[a]])) for a in range(len(idx) - 1)]
        interp = True
    j, k, sc = map(np.array, zip(*out))
    return j, k, sc, interp


def measures(p, v, std, A, mu, nominal, B, fine):
    r = p @ A.T
    r_mu = A @ mu
    d = r - r_mu
    out = {}
    line = np.polyval(np.polyfit(v[std], nominal[std], 1), v)
    sh_c, sh_d = mu - line, p - mu
    for k in KEYS:
        b = B[k]
        e = RA._mixed(r_mu, d, b)
        out[f"{k}|full|mixed"] = e[:, std].max(1)
        out[f"{k}|full|bound_ind"] = np.abs(r[:, std]).max(1) / b["b_ind"]
        out[f"{k}|full|bound_eq"] = np.abs(r[:, std]).max(1) / b["b_eq"]
        if fine:
            out[f"{k}|fullfine|mixed"] = e.max(1)
        out[f"{k}|shared|mixed"] = RA._mixed(sh_c[std], sh_d[:, std], b).max(1)
        for span in SPANS:
            j, i, sc, _ = move_pairs(v, std, span, fine)
            out[f"{k}|move{span * 1e3:g}mV|mixed"] = RA._mixed(sc * (r_mu[i] - r_mu[j]), sc[None] * (d[:, i] - d[:, j]), b).max(1)
            if fine:      # within the fine windows, the same move from the standard voltages alone, interpolated
                j, i, sc, _ = move_pairs(v, std, span, False)      # as on the standard grid
                win = fine_windows(v, std)
                keep = np.array([win[a] >= 0 and win[a] == win[c] for a, c in zip(j, i)])
                j, i, sc = j[keep], i[keep], sc[keep]
                out[f"{k}|move{span * 1e3:g}mVinterp|mixed"] = RA._mixed(sc * (r_mu[i] - r_mu[j]),
                                                                         sc[None] * (d[:, i] - d[:, j]), b).max(1)
                jf, i_f, scf, _ = move_pairs(v, std, span, True)
                keep = np.array([win[a] >= 0 and win[a] == win[c] for a, c in zip(jf, i_f)])
                jf, i_f, scf = jf[keep], i_f[keep], scf[keep]
                out[f"{k}|move{span * 1e3:g}mVwin|mixed"] = RA._mixed(scf * (r_mu[i_f] - r_mu[jf]),
                                                                      scf[None] * (d[:, i_f] - d[:, jf]), b).max(1)
    return out


def fine_windows(v, std):
    """Index of the fine-grid window that holds each held voltage (-1 outside both windows)."""
    f = np.sort(v[~std])
    groups = np.split(f, np.where(np.diff(f) > 0.03)[0] + 1)
    out = np.full(len(v), -1)
    for g_i, g in enumerate(groups):
        out[(v >= g.min() - 0.021) & (v <= g.max() + 0.021)] = g_i
    return out


def latent(x):
    """Mean and factor F of the Gaussian with the sample covariance of x: samples are mu + z F, z ~ N(0, I_k)."""
    mu = x.mean(0)
    _, s, vt = np.linalg.svd((x - mu) / np.sqrt(len(x) - 1), full_matrices=False)
    k = int((s > s.max() * 1e-9).sum())
    return mu, s[:k, None] * vt[:k]


def is_samples(x, n, rng):
    mu, F = latent(x)
    k = F.shape[0]
    for i in range(0, n, CHUNK):
        m = min(CHUNK, n - i)
        u = rng.standard_normal((m, k)) * S_IS
        w = S_IS ** k * np.exp(-0.5 * (u * u).sum(1) * (1 - 1 / S_IS ** 2))
        yield mu + u @ F, w


def worst(x, v, std, A, nominal, B, n, rng, fine, exceed=False):
    mu = x.mean(0)
    acc, ws = {}, []
    for p, w in is_samples(x, n, rng):
        for k, a in measures(p, v, std, A, mu, nominal, B, fine).items():
            acc.setdefault(k, []).append(a)
        ws.append(w)
    w = np.concatenate(ws)
    out, exc = {}, {}
    for k, parts in acc.items():
        y = np.concatenate(parts)
        o = np.argsort(y)[::-1]
        out[k] = float(np.interp(1 - Q_WORST, np.cumsum(w[o]) / len(y), y[o]))
        if exceed:
            exc[k] = float((w * (y > 1)).sum() / len(y) * 1e6)
    return out, exc


def prepare(rec):
    v = np.asarray(rec["v"])
    ok = np.asarray(rec["ok_all"], bool) & np.asarray(rec["ok_nominal"], bool)
    std_all = standard_mask(v, v)
    # the window: the standard voltages every channel tracks, and every fine voltage between them
    top = v[std_all & ok].max() if (std_all & ok).any() else v.min()
    keep = ok & (v <= top + 1e-9)
    x = np.asarray(rec["peds"])[:, keep]
    v, nominal, std = v[keep], np.asarray(rec["nominal"])[keep], std_all[keep]
    return x, v, std, nominal, bool((~std).any())


def analyse_one(args):
    name, rec, B = args
    x, v, std, nominal, fine = prepare(rec)
    A = residual_operator(v, std)
    rng = np.random.default_rng(common.name_seed(name) + 6)
    point, exc = worst(x, v, std, A, nominal, B, N_POINT, rng, fine, exceed=True)
    boots = {k: [] for k in point}
    for _ in range(N_BOOT):
        xb = x[rng.integers(0, len(x), len(x))]
        w, _ = worst(xb, v, std, A, nominal, B, N_BOOT_SAMPLE, rng, fine)
        for k in boots:
            boots[k].append(w[k])
    r = x @ A.T
    r_mu = A @ x.mean(0)
    cstd = np.corrcoef(x[:, std], rowvar=False)
    out = {"n": len(x), "v": v.tolist(), "fine": fine, "window": [float(v.min()), float(v.max())],
           "margin": {k: 1 / q for k, q in point.items()},
           "ci90": {k: [1 / float(np.quantile(b, 0.95)), 1 / float(np.quantile(b, 0.05))] for k, b in boots.items()},
           "exceed_per_1e6": exc, "common_residual_max": float(np.abs(r_mu[std]).max()),
           "mismatch_residual_sd_max": float((r - r_mu)[:, std].std(0, ddof=1).max()),
           "pedestal_sd_max": float(x[:, std].std(0, ddof=1).max()),
           "corr_adjacent_mean": float(np.mean(np.diag(cstd, 1))),
           "sim_max_residual": float(np.abs(r[:, std]).max())}
    print(f"{name[:72]:72s} n {len(x):3d} corr {out['corr_adjacent_mean']:+.2f} strictest "
          f"{out['margin'][f'{common.WORST}|full|mixed']:.2f} move50 {out['margin'][f'{common.WORST}|move50mV|mixed']:.2f}",
          flush=True)
    return name, out


def classify(lo, hi):
    return "pass" if lo > 1 else "fail" if hi < 1 else "indeterminate"


def main(merge=False):
    B = RA.budgets()
    recs = json.loads((OUT / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    old = json.loads((OUT / "cell_margins.json").read_text(encoding="utf-8"))["designs"] if merge and (OUT / "cell_margins.json").exists() else {}
    # every finished pair is appended to a checkpoint, so an interrupted run resumes where it stopped
    ckpt = OUT / "cell_margins_partial.jsonl"
    done = {}
    if ckpt.exists():
        for line in ckpt.read_text(encoding="utf-8").splitlines():
            n, r = json.loads(line)
            if n in recs and r["n"] == len(recs[n]["peds"]):
                done[n] = r
    old = {**old, **done}
    jobs = [(n, r, B) for n, r in recs.items() if n not in old or old[n]["n"] != len(r["peds"])
            or len(old[n]["v"]) > len(r["v"])]
    res = dict(old)
    with ProcessPoolExecutor(max(1, min(12, len(jobs)))) as ex, ckpt.open("a", encoding="utf-8") as f:
        for n, r in ex.map(analyse_one, jobs):
            res[n] = r
            f.write(json.dumps([n, r]) + "\n")
            f.flush()
    out = {"budgets": B, "spans": SPANS, "n_boot": N_BOOT, "designs": res}
    (OUT / "cell_margins.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    ckpt.unlink()
    return out


def table(out):
    B = out["budgets"]
    L = ["## Worst-channel margins with one cell per channel", "",
         "Budgets (µV): " + "; ".join(f"{k}: untracked equal-sign {b['b_eq'] * 1e6:.0f}, untracked single-gate "
                                      f"{b['b_ind'] * 1e6:.0f}" for k, b in B.items()), "",
         "Margin of the worst of 10^6 channels [90 % interval] and class. 'full': level set open-loop from the line, "
         "standard held voltages; 'full, fine': every simulated voltage (fine grid only); 'move Δ': tuned on the qubits "
         "and moved by up to Δ (fine grid: simulated pairs; otherwise interpolated below the grid step, marked *).", ""]
    for key in KEYS:
        L += [f"### {key}", "", "| design | condition | n | corr | window (V) | full | exceed / 10^6 | shared | full, fine | "
              "move 20 mV | move 50 mV | move 100 mV | move 200 mV |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, r in sorted(out["designs"].items()):
            d, cond = name.split("|")

            def cell(m):
                k = f"{key}|{m}"
                if k not in r["margin"]:
                    return "–"
                lo, hi = r["ci90"][k]
                return f"{r['margin'][k]:.2f} [{lo:.2f}, {hi:.2f}] {classify(lo, hi)[0]}"
            star = "" if r["fine"] else "*"
            L.append(f"| {d} | {cond} | {r['n']} | {r['corr_adjacent_mean']:+.2f} | {r['window'][0]:.2f}-{r['window'][1]:.2f} | "
                     f"{cell('full|mixed')} | {r['exceed_per_1e6'][f'{key}|full|mixed']:.3g} | {cell('shared|mixed')} | "
                     f"{cell('fullfine|mixed')} | {cell('move20mV|mixed')}{star} | {cell('move50mV|mixed')}{star} | "
                     f"{cell('move100mV|mixed')}{star if r['v'][1] - r['v'][0] > 0.15 else ''} | {cell('move200mV|mixed')} |")
        L.append("")
    (OUT / "cell_margins.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    table(main(merge="merge" in sys.argv))
