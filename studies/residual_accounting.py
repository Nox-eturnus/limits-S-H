"""Which budget the static residual is judged against: common and mismatch parts, and moves from a tuned level.

Untracked budget. The residual pedestal after an electronic two-point calibration is, by definition, not
known to the controller, so it cannot be frame-tracked. It is judged against the untracked budget
(studies/partial_tracking_qec.py, f = 1, no idle time: the conditional phase as for M = 2 repeated gates and
the single-qubit Stark phases of the four barriers around a data qubit added in amplitude, the worst case of
equal signs). Idle time is assumed refocused by an echo; without an echo an untracked offset fails the
budget at any idle time of a microsecond.

Common and mismatch parts. Equal signs apply only to the part of the residual that every channel shares. The
residual r_i(V) of channel i is split into the residual of the mean pedestal, r_mu(V), common to all
channels, and the mismatch part d_i(V) = r_i(V) - r_mu(V), whose sign is random from channel to channel.
With independent signs the surface code behaves as for Pauli errors (studies/surface_code.py), so d is
judged against the single-gate untracked budget b_ind, and r_mu against the equal-sign budget b_eq. Within
one channel the two parts are one offset and add linearly; the common part, in addition, interferes with the
common part of the partner barrier. The error measure is therefore
    u_i = max_V sqrt(((r_mu + d_i) / b_ind)^2 + r_mu^2 (1 / b_eq^2 - 1 / b_ind^2)),  margin = 1 / u(worst channel),
which is |r| / b_ind for a pure mismatch deviation and |r_mu| / b_eq for a pure common one, and never smaller
than |r| / b_ind. The bounds e/b_eq (all equal signs) and e/b_ind (all independent) are kept for reference.

Moves. If each barrier's static level is found by qubit-level tuning through its own hold cell, the pedestal
at that level is absorbed into the DAC code. What the electronic calibration still has to predict is a move
of the level by Delta from the tuned point, set open-loop from the two-point line. Its error is
r_i(V0 + Delta) - r_i(V0): the line's offset cancels and only the change of the residual over the move
remains. It is evaluated for moves up to 50, 100 and 200 mV (pairs of held voltages at most Delta apart;
below the grid step the residual is interpolated linearly), with the same split.

The worst of 10^6 channels and the 90 % bootstrap interval are computed as in studies/tail_surrogate.py
(importance sampling, 10^6 samples for the point estimate, 300 bootstrap replicates of 10^5). This script
applies the accounting to the multi-voltage pedestals of studies/tail_surrogate.py, studies/extra_bands.py
and studies/tree_source_1pf.py; studies/cell_margins.py applies its functions to one cell per channel, which
is what the article reports.

Run:  python studies/residual_accounting.py         (about 1 h on 12 processes)
      python studies/residual_accounting.py merge   (only records not yet analysed)
Writes results/residual_accounting.{json,md}.
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

N_ARRAY = 1e6
Q_WORST = 0.5 ** (1 / N_ARRAY)
S_IS = 1.8
N_POINT = 1_000_000
N_BOOT = 300
N_BOOT_SAMPLE = 100_000
CHUNK = 250_000
SPANS = (0.05, 0.1, 0.2)
KEYS = (common.WORST, "s33.69_t0.001", common.REF)


def budgets():
    """Tracked operational (old), untracked equal-sign b_eq (f = 1) and untracked single-gate b_ind, in V."""
    bud = common.budgets()
    pt = json.loads((ROOT / "results" / "partial_tracking_qec.json").read_text(encoding="utf-8"))["rows"]
    out = {}
    for k, (s, t) in common.POINTS.items():
        row = next(r for r in pt if r["s"] == s and r["target"] == t and r["t_idle"] == 0.0)
        out[k] = {"tracked_op": bud[k]["operational"], "b_eq": row["budget"]["1"], "b_ind": bud[k]["per_gate"]}
    return out


def _proj(v):
    X = np.column_stack([np.ones_like(v), v])
    return np.eye(len(v)) - X @ np.linalg.pinv(X)          # residual operator: r = (I - P) p


def _pairs(v, span):
    """Index arrays (j, k) and scales of the moves between held voltages at most span apart; below the grid
    step, the adjacent pairs scaled by span / step (the residual interpolated linearly)."""
    out = [(j, k, 1.0) for j in range(len(v)) for k in range(j + 1, len(v)) if v[k] - v[j] <= span + 1e-9]
    if not out:
        out = [(j, j + 1, span / (v[j + 1] - v[j])) for j in range(len(v) - 1)]
    j, k, sc = map(np.array, zip(*out))
    return j, k, sc


def _mixed(c, d, b):
    """Error measure of a deviation with common part c (shared sign) and mismatch part d (random sign)."""
    return np.sqrt(((c + d) / b["b_ind"]) ** 2 + c ** 2 * (1 / b["b_eq"] ** 2 - 1 / b["b_ind"] ** 2))


def measures(p, v, mu, nominal, B):
    """Normalised error of each sample row of pedestals p, for every measure; margin = 1 / quantile."""
    R = _proj(v)
    r = p @ R.T
    r_mu = R @ mu
    d = r - r_mu
    out = {}
    e_tot = np.abs(r).max(1)
    line = np.polyval(np.polyfit(v, nominal, 1), v)
    sh = p - line                                     # shared calibration: deviation from the nominal line
    sh_c, sh_d = mu - line, p - mu
    for k in KEYS:
        b = B[k]
        out[f"{k}|full|tracked_eq"] = e_tot / b["tracked_op"]            # frame-tracked operational budget, for comparison
        out[f"{k}|full|bound_eq"] = e_tot / b["b_eq"]
        out[f"{k}|full|bound_ind"] = e_tot / b["b_ind"]
        out[f"{k}|full|mixed"] = _mixed(r_mu, d, b).max(1)
        out[f"{k}|shared|mixed"] = _mixed(sh_c, sh_d, b).max(1)
        for span in SPANS:
            j, i, sc = _pairs(v, span)
            c = sc * (r_mu[i] - r_mu[j])
            dd = sc * (d[:, i] - d[:, j])
            out[f"{k}|move{span * 1e3:g}mV|mixed"] = _mixed(c, dd, b).max(1)
    return out


def is_samples(x, n, rng):
    mu, cov = x.mean(0), np.cov(x, rowvar=False)
    kdim = len(mu)
    L = np.linalg.cholesky(cov + np.diag(np.full(kdim, 1e-24)))
    for i in range(0, n, CHUNK):
        m = min(CHUNK, n - i)
        u = rng.standard_normal((m, kdim)) * S_IS
        w = S_IS ** kdim * np.exp(-0.5 * (u * u).sum(1) * (1 - 1 / S_IS ** 2))
        yield mu + u @ L.T, w


def worst(x, v, nominal, B, n, rng, exceed=False):
    mu = x.mean(0)
    acc, ws = {}, []
    for p, w in is_samples(x, n, rng):
        for k, a in measures(p, v, mu, nominal, B).items():
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


def analyse_one(args):
    name, rec, B = args
    v = np.asarray(rec["v"])
    ok = np.asarray(rec["ok"], bool)
    x = np.asarray(rec["peds"])[:, ok]
    v, nominal = v[ok], np.asarray(rec["nominal"])[ok]
    rng = np.random.default_rng(common.name_seed(name) + 5)
    point, exc = worst(x, v, nominal, B, N_POINT, rng, exceed=True)
    boots = {k: [] for k in point}
    for _ in range(N_BOOT):
        xb = x[rng.integers(0, len(x), len(x))]
        w, _ = worst(xb, v, nominal, B, N_BOOT_SAMPLE, rng)
        for k in boots:
            boots[k].append(w[k])
    # share of the mismatch part at the worst voltage of the mean channel, for the text
    R = _proj(v)
    r_mu = R @ x.mean(0)
    d_sd = (x @ R.T - r_mu).std(0, ddof=1)
    out = {"n": len(x), "v": v.tolist(), "margin": {k: 1 / q for k, q in point.items()},
           "ci90": {k: [1 / float(np.quantile(b, 0.95)), 1 / float(np.quantile(b, 0.05))] for k, b in boots.items()},
           "exceed_per_1e6": exc, "common_residual_max": float(np.abs(r_mu).max()),
           "mismatch_residual_sd_max": float(d_sd.max())}
    print(f"{name[:70]:70s} strictest: tracked {out['margin'][f'{common.WORST}|full|tracked_eq']:.2f} "
          f"mixed {out['margin'][f'{common.WORST}|full|mixed']:.2f} move100 {out['margin'][f'{common.WORST}|move100mV|mixed']:.2f}",
          flush=True)
    return name, out


def classify(lo, hi):
    return "pass" if lo > 1 else "fail" if hi < 1 else "indeterminate"


def main(merge=False):
    """merge: analyse only the records not yet in residual_accounting.json and add them to it."""
    B = budgets()
    recs = {}
    for f in (ROOT / "results" / "tail_surrogate_pedestals.json", ROOT / "results" / "extra_bands_pedestals.json",
              OUT / "tree_source_1pf_pedestals.json"):
        if not f.exists():
            continue
        for n, r in json.loads(f.read_text(encoding="utf-8")).items():
            if len(r["peds"]) >= 10:
                recs[n] = r
    old = json.loads((OUT / "residual_accounting.json").read_text(encoding="utf-8"))["designs"] if merge else {}
    jobs = [(n, r, B) for n, r in recs.items() if n not in old]
    with ProcessPoolExecutor(max(1, min(12, len(jobs)))) as ex:
        res = {**old, **dict(ex.map(analyse_one, jobs))}
    out = {"budgets": B, "spans": SPANS, "n_boot": N_BOOT, "designs": res}
    (OUT / "residual_accounting.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def table(out):
    B = out["budgets"]
    L = ["## Static residual against the untracked budget, common and mismatch parts separated", "",
         "Budgets (µV): " + "; ".join(f"{k}: tracked operational {b['tracked_op'] * 1e6:.0f}, untracked equal-sign "
                                      f"{b['b_eq'] * 1e6:.0f}, untracked single-gate {b['b_ind'] * 1e6:.0f}" for k, b in B.items()), "",
         "Margin of the worst of 10^6 channels [90 % interval], class. 'full': the level set open-loop from the two-point line "
         "anywhere in the window; 'move Δ': the level tuned on the qubit and then moved open-loop by up to Δ.", ""]
    for key in KEYS:
        L += [f"### {key}", "", "| design | band | n | tracked, equal sign | full, mixed | bounds eq / ind | "
              "exceed / 10^6 | shared, mixed | move 50 mV | move 100 mV | move 200 mV |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, r in out["designs"].items():
            d, band = name.split("|")

            def cell(m):
                k = f"{key}|{m}"
                lo, hi = r["ci90"][k]
                return f"{r['margin'][k]:.2f} [{lo:.2f}, {hi:.2f}] {classify(lo, hi)[0]}"
            L.append(f"| {d} | {band} | {r['n']} | {cell('full|tracked_eq')} | {cell('full|mixed')} | "
                     f"{r['margin'][f'{key}|full|bound_eq']:.2f} / {r['margin'][f'{key}|full|bound_ind']:.2f} | "
                     f"{r['exceed_per_1e6'][f'{key}|full|mixed']:.3g} | {cell('shared|mixed')} | {cell('move50mV|mixed')} | "
                     f"{cell('move100mV|mixed')} | {cell('move200mV|mixed')} |")
        L.append("")
    (OUT / "residual_accounting.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    table(main(merge="merge" in sys.argv))
