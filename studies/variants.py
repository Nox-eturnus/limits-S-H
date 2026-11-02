"""Analysis of studies/mc_cell_variants.py.

Body effect: closed-form corrected margins at the strictest point with k1, k2 scaled by 0.7 and 1.3, against the same
20 channels of the 4 K band. Numerical tolerance: the deviation of each channel from its seven-point line at the
tighter settings against the reference decks. Transmission gates sized for settling: node time constant, open-loop
residual and the change of the residual over moves of 20 and 50 mV against the untracked budget for equal signs.
GF180 with current-factor mismatch against threshold mismatch only.

Run:  python studies/variants.py     (writes results/variants.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402
import cell_margins as CM  # noqa: E402
import array_yield as Y  # noqa: E402
import tail_corrected as Y8  # noqa: E402

W, N99, REF = common.WORST, "s33.69_t0.001", common.REF
B = CM.RA.budgets()
TAU_MAX = Y8.TAU_MAX
L = []


def closed(rec, t, key=W, kind="full", seeds=None):
    if seeds is not None:
        keep = [i for i, s in enumerate(rec["seeds"]) if s in seeds]
        rec = dict(rec, peds=[rec["peds"][i] for i in keep], track=[rec["track"][i] for i in keep],
                   seeds=[rec["seeds"][i] for i in keep])
    x, v, std, nominal, _ = CM.prepare(rec)
    A = CM.residual_operator(v, std)
    m, s = Y.moments(x, v, std, A, nominal, kind)
    return Y.margin_closed(m * (1 + t), s * (1 + t), B[key]), float(np.abs((A @ x.mean(0))[std]).max())


def body():
    r9 = json.loads((OUT / "mc_cell_variants_pedestals.json").read_text(encoding="utf-8"))
    r6 = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    out = {}
    L.extend(["## Body effect (k1, k2) scaled, 4 K band, strictest point, per channel / shared (closed form)", "",
              "| Design | reference (same 20 channels) | k x 0.7 | k x 1.3 | curvature of the mean channel (µV): ref / 0.7 / 1.3 |",
              "|---|---|---|---|---|"])
    for d in Y8.FIG6[:2] + (Y8.TGD, Y8.TG):
        ref = r6[f"{d}|4 K proxy"]
        seeds = set(range(1, 21))
        t = Y8.tau(d, "4 K proxy")
        row = {"ref": closed(ref, t, seeds=seeds), "ref_shared": closed(ref, t, kind="shared", seeds=seeds)}
        for f in ("0.7", "1.3"):
            rec = r9.get(f"{d}|4 K, body effect x {f}")
            if rec:
                row[f] = closed(rec, t)
                row[f + "_shared"] = closed(rec, t, kind="shared")
        out[d] = row
        L.append(f"| {d} | {row['ref'][0]:.3g} / {row['ref_shared'][0]:.3g} | " +
                 " | ".join(f"{row[f][0]:.3g} / {row[f + '_shared'][0]:.3g}" if f in row else "–" for f in ("0.7", "1.3")) +
                 f" | {row['ref'][1] * 1e6:.3g} / " + " / ".join(f"{row[f][1] * 1e6:.3g}" if f in row else "–" for f in ("0.7", "1.3")) + " |")
    L.append("")
    return out


def tol():
    ref = {}
    for line in (ROOT / "results" / "mc_cell_channels.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r.get("cond") == "4 K proxy" and r["seed"] <= 10 and "ped" in r:
            ref[(r["design"], r["seed"], r["v"])] = r["ped"]
    new = {}
    for line in (OUT / "mc_cell_variants_channels.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["cond"] in ("4 K, reltol 1e-6", "4 K, reltol 1e-7", "4 K, max step 5 ps") and "ped" in r:
            new[(r["design"], r["cond"], r["seed"], r["v"])] = r["ped"]
    out = {}
    L.extend(["## Numerical tolerance (4 K band, seeds 0 to 10)", "",
              "| Design | Setting | largest change of a pedestal (µV) | largest change of a deviation from the line (µV) | largest deviation, ref / new (µV) |",
              "|---|---|---|---|---|"])
    for d in (Y8.NMOS, Y8.BOOT, Y8.TG):
        vs = sorted({k[2] for k in ref if k[0] == d and k[2] <= (0.8 if d == Y8.NMOS else 1.5) + 1e-9})
        vs = [v for v in vs if abs((v - 0.3) / (0.1 if d == Y8.NMOS else 0.2) - round((v - 0.3) / (0.1 if d == Y8.NMOS else 0.2))) < 1e-6]
        v = np.array(vs)
        A = CM.residual_operator(v, np.ones(len(v), bool))
        for c in ("4 K, reltol 1e-6", "4 K, reltol 1e-7", "4 K, max step 5 ps"):
            dp, dr, mr, mn = [], [], [], []
            for s in range(0, 11):
                try:
                    p0 = np.array([ref[(d, s, x)] for x in vs])
                    p1 = np.array([new[(d, c, s, x)] for x in vs])
                except KeyError:
                    continue
                dp.append(np.abs(p1 - p0).max())
                dr.append(np.abs(A @ p1 - A @ p0).max())
                mr.append(np.abs(A @ p0).max())
                mn.append(np.abs(A @ p1).max())
            if dp:
                out[f"{d}|{c}"] = {"n": len(dp), "d_ped": max(dp), "d_dev": max(dr), "dev_ref": max(mr), "dev_new": max(mn)}
                L.append(f"| {d} | {c} | {max(dp) * 1e6:.3g} | {max(dr) * 1e6:.3g} | {max(mr) * 1e6:.3g} / {max(mn) * 1e6:.3g} |")
    L.append("")
    return out


def wide():
    import mc_cell_variants as M9
    import pair_spread as Q
    from flow import cosim as C
    recs = {}
    for line in (OUT / "mc_cell_variants_channels.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["design"].startswith("TG sized for settling") and "ped" in r:
            recs.setdefault((r["design"], r["cond"]), {})[r["v"]] = (r["ped"], r["track"])
    b166 = Q.budgets(16.6, 1e-4, 1.0)
    keys = {"99.99 %, 33.69": B[W], "99.99 %, 16.6": b166, "99.9 %, 33.69": B[N99], "99.9 %, 10": B[REF]}
    out = {}
    L.extend(["## Transmission gates sized for settling, on 1 pF, nominal cell, 20 mV grid", "",
              "Margins against the untracked budget for equal signs: open-loop / move of 50 mV / move of 20 mV.", "",
              "| W (um) | band | tau_node (ns) | window | " + " | ".join(keys) + " |", "|---|---|---|---|" + "---|" * len(keys)])
    import cell_margins  # noqa: F401
    for w in M9.WIDE:
        name = M9.wide_name(w)
        cfg = M9.M.R.E.base_cfg(**M9.M.DESIGNS[name])
        try:
            tau = C.cell_params(cfg, v0=0.9)["tau_node"]
        except Exception:
            tau = float("nan")
        for c in ("300 K", "4 K proxy"):
            d = recs.get((name, c), {})
            v = np.array(sorted(x for x, (p, t) in d.items() if abs(t) < M9.M.R.TRACK_TOL))
            if len(v) < 10:
                continue
            # contiguous tracked window from 0.3 V
            stop = next((i for i in range(1, len(v)) if v[i] - v[i - 1] > 0.021), len(v))
            v = v[:stop]
            p = np.array([d[x][0] for x in v])
            std = np.array([abs((x - 0.3) / 0.2 - round((x - 0.3) / 0.2)) < 1e-6 for x in v])
            A = CM.residual_operator(v, std)
            r = A @ p
            row = {"tau_node": tau, "window": [float(v.min()), float(v.max())]}
            cells = []
            for kn, b in keys.items():
                ol = b["b_eq"] / np.abs(r[std]).max()
                mv = {}
                for span in (0.05, 0.02):
                    dmax = max(abs(r[k] - r[j]) for j in range(len(v)) for k in range(j + 1, len(v)) if v[k] - v[j] <= span + 1e-9)
                    mv[span] = b["b_eq"] / dmax
                row[kn] = {"open_loop": ol, "move50": mv[0.05], "move20": mv[0.02]}
                cells.append(f"{ol:.3g} / {mv[0.05]:.3g} / {mv[0.02]:.3g}")
            out[f"{w:g}|{c}"] = row
            L.append(f"| {w:g} | {c} | {tau * 1e9:.3g} | {v.min():g}-{v.max():g} V | " + " | ".join(cells) + " |")
    L.append("")
    return out


def gfbeta():
    old = json.loads((ROOT / "results" / "gf180_pedestals.json").read_text(encoding="utf-8"))
    p = OUT / "gf180_current_factor" / "mc_cell_peds.json"
    if not p.exists():
        return {}
    new = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    L.extend(["## GF180 with current-factor mismatch, 4 K band, strictest point (closed form, tau 9.8 %)", "",
              "| Design | threshold only: per channel / shared | with current factor: per channel / shared | spread of the pedestal (µV): old / new |",
              "|---|---|---|---|"])
    for name, rec in new.items():
        d = name.split("|")[0]
        o = old.get(f"{d}|4 K proxy")
        if not o:
            continue
        sp = lambda r: float(np.std(np.array(r["peds"]), axis=0, ddof=1).max())  # noqa: E731
        row = {"old": closed(o, TAU_MAX)[0], "old_shared": closed(o, TAU_MAX, kind="shared")[0],
               "new": closed(rec, TAU_MAX)[0], "new_shared": closed(rec, TAU_MAX, kind="shared")[0],
               "spread_old": sp(o), "spread_new": sp(rec)}
        out[d] = row
        L.append(f"| {d} | {row['old']:.3g} / {row['old_shared']:.3g} | {row['new']:.3g} / {row['new_shared']:.3g} | "
                 f"{row['spread_old'] * 1e6:.3g} / {row['spread_new'] * 1e6:.3g} |")
    L.append("")
    return out


def main():
    out = {"body": body(), "tol": tol(), "wide": wide(), "gfbeta": gfbeta()}
    (OUT / "variants.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT / "variants.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
