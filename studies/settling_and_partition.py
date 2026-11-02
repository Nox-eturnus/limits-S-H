"""Analysis of studies/mc_cell_settling.py.

Switches sized for settling (5 to 40 um on 1 pF, scaled equivalent, nominal, 20 mV grid) for the TG
(studies/mc_cell_variants.py), the TG with dummies, the bootstrapped switch and the NMOS switch: node time constant,
margins for levels set open-loop, for moves of 50 and 20 mV and for a move of 1 mV (from the steepest change of the
deviation between neighbouring 20 mV points), against the untracked budget for equal signs, and the shortest node time
constant at which each architecture keeps a margin of one (largest ratio of time constant to margin over widths and
bands). Charge partition (50/50 and 0/100 instead of 40/60) and the non-quasi-static charge model in the 4 K band:
closed-form margins of the four deciding designs and of their nominal cells on the 20 mV grid. Interpolation bias of
move margins in a second band. The usable held window at 3.87 decades per volt (0.3 to 1.1 V below the 1.8 V supply
with the 0.67 V pulse): margins with the line fitted over that window.

Run:  python studies/settling_and_partition.py     (writes results/settling_and_partition.{json,md})
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
L = []
MOVES = (0.05, 0.02)


def nominal_runs(path, pred):
    recs = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["seed"] == 0 and "ped" in r and pred(r):
            recs.setdefault((r["design"], r["cond"]), {})[r["v"]] = (r["ped"], r["track"])
    return recs


def fine_metrics(d, keys):
    """Open-loop, move and drift-scale margins of a nominal cell on a 20 mV grid (as studies/variants.py wide)."""
    import mc_cell as M
    v = np.array(sorted(x for x, (p, t) in d.items() if abs(t) < M.R.TRACK_TOL))
    if len(v) < 10:
        return None
    stop = next((i for i in range(1, len(v)) if v[i] - v[i - 1] > 0.021), len(v))
    v = v[:stop]
    p = np.array([d[x][0] for x in v])
    std = np.array([abs((x - 0.3) / 0.2 - round((x - 0.3) / 0.2)) < 1e-6 for x in v])
    A = CM.residual_operator(v, std)
    r = A @ p
    slope = float(np.max(np.abs(np.diff(r)) / np.diff(v)))        # V of deviation per V of move
    row = {"window": [float(v.min()), float(v.max())], "curvature_uV": float(np.abs(r[std]).max() * 1e6),
           "dev_slope_uV_per_mV": slope * 1e3}
    for kn, b in keys.items():
        mv = {}
        for span in MOVES:
            dmax = max(abs(r[k] - r[j]) for j in range(len(v)) for k in range(j + 1, len(v)) if v[k] - v[j] <= span + 1e-9)
            mv[span] = b["b_eq"] / dmax
        row[kn] = {"open_loop": b["b_eq"] / np.abs(r[std]).max(), "move50": mv[0.05], "move20": mv[0.02],
                   "move1": b["b_eq"] / (slope * 1e-3)}
    return row


def keys():
    import pair_spread as Q
    return {"99.99 %, 33.69": B[W], "99.9 %, 33.69": B[N99], "99.9 %, 10": B[REF],
            "99.99 %, 16.6": Q.budgets(16.6, 1e-4, 1.0)}


def tau_node(design_kw, v0):
    import mc_cell as M
    from flow import cosim as C
    cfg = M.R.E.base_cfg(**design_kw)
    return C.cell_params(cfg, v0=v0)["tau_node"]


def wide():
    import mc_cell_settling as M10
    import mc_cell_variants as M9
    K = keys()
    r9 = nominal_runs(ROOT / "results" / "mc_cell_variants_channels.jsonl", lambda r: r["design"].startswith("TG sized for settling"))
    r10 = nominal_runs(OUT / "mc_cell_settling_channels.jsonl", lambda r: " sized for settling" in r["design"])
    out = {}
    L.extend(["## Switches sized for settling, 1 pF, nominal cell, 20 mV grid", "",
              "Margins against the untracked budget for equal signs: open-loop / 50 mV move / 20 mV move / 1 mV move.", "",
              "| architecture | W (um) | band | tau_node (ns) | window | curvature (uV) | " + " | ".join(K) + " |",
              "|---|---|---|---|---|---|" + "---|" * len(K)])
    for arch in ("TG", "TG + dummies", "bootstrapped", "NMOS"):
        for w in M10.WIDE:
            if arch == "TG":
                name, kw, src = M9.wide_name(w), M9.M.DESIGNS[M9.wide_name(w)], r9
            else:
                name, kw, src = M10.wide_name(arch, w), M10.M.DESIGNS[M10.wide_name(arch, w)], r10
            try:
                tau = tau_node(kw, 0.6 if arch == "NMOS" else 0.9)
            except Exception:
                tau = float("nan")
            for c in ("300 K", "4 K proxy"):
                d = src.get((name, c))
                row = fine_metrics(d, K) if d else None
                if row is None:
                    continue
                row["tau_node"] = tau
                out[f"{arch}|{w:g}|{c}"] = row
                L.append(f"| {arch} | {w:g} | {c} | {tau * 1e9:.3g} | {row['window'][0]:g}-{row['window'][1]:g} V | "
                         f"{row['curvature_uV']:.3g} | " + " | ".join(
                             f"{row[k]['open_loop']:.3g} / {row[k]['move50']:.3g} / {row[k]['move20']:.3g} / {row[k]['move1']:.3g}"
                             for k in K) + " |")
    # shortest node time constant for a margin of one (margin proportional to tau_node), worst over widths and bands
    tmin = {}
    L.extend(["", "Shortest node time constant for a margin of one (largest tau_node / margin over widths and bands):", "",
              "| architecture | 50 mV moves, 99.9 %, 33.69 | open-loop, 99.99 %, 33.69 | open-loop, 99.9 %, 10 | 1 mV moves, 99.99 %, 33.69 |",
              "|---|---|---|---|---|"])
    for arch in ("TG", "TG + dummies", "bootstrapped", "NMOS"):
        rows = [r for k, r in out.items() if k.startswith(arch + "|") and np.isfinite(r["tau_node"])]
        if not rows:
            continue
        t = {"move50_99.9_33.69": max(r["tau_node"] / r["99.9 %, 33.69"]["move50"] for r in rows),
             "open_99.99_33.69": max(r["tau_node"] / r["99.99 %, 33.69"]["open_loop"] for r in rows),
             "open_99.9_10": max(r["tau_node"] / r["99.9 %, 10"]["open_loop"] for r in rows),
             "move1_99.99_33.69": max(r["tau_node"] / r["99.99 %, 33.69"]["move1"] for r in rows)}
        tmin[arch] = t
        L.append(f"| {arch} | " + " | ".join(f"{x * 1e9:.3g} ns" for x in t.values()) + " |")
    L.append("")
    return {"rows": out, "tau_min": tmin}


def closed(rec, t, key=W, kind="full", seeds=None):
    if seeds is not None:
        keep = [i for i, s in enumerate(rec["seeds"]) if s in seeds]
        rec = dict(rec, peds=[rec["peds"][i] for i in keep], track=[rec["track"][i] for i in keep],
                   seeds=[rec["seeds"][i] for i in keep])
    x, v, std, nominal, _ = CM.prepare(rec)
    A = CM.residual_operator(v, std)
    m, s = Y.moments(x, v, std, A, nominal, kind)
    return Y.margin_closed(m * (1 + t), s * (1 + t), B[key]), float(np.abs((A @ x.mean(0))[std]).max())


def partition():
    r10 = json.loads((OUT / "mc_cell_settling_pedestals.json").read_text(encoding="utf-8"))
    r6 = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    conds = ("4 K, xpart 0.5", "4 K, xpart 1", "4 K, NQS")
    out = {"mc": {}, "nominal": {}}
    L.extend(["## Charge partition and non-quasi-static charge, 4 K band, strictest point", "",
              "Closed-form margins per channel / shared, levels set open-loop (20 channels, tau of the design); "
              "curvature of the mean channel in brackets (uV).", "",
              "| design | 40/60, quasi-static (reference) | 50/50 | 0/100 | 40/60, NQS |", "|---|---|---|---|---|"])
    for d in (Y8.NMOS, Y8.BOOT, Y8.TGD, Y8.TG):
        t = Y8.tau(d, "4 K proxy")
        ref = r6[f"{d}|4 K proxy"]
        row = {"ref": closed(ref, t, seeds=set(range(1, 21))), "ref_shared": closed(ref, t, kind="shared", seeds=set(range(1, 21)))}
        for c in conds:
            rec = r10.get(f"{d}|{c}")
            if rec:
                row[c] = closed(rec, t)
                row[c + "_shared"] = closed(rec, t, kind="shared")
        out["mc"][d] = row
        cell = lambda k: (f"{row[k][0]:.3g} / {row[k + '_shared'][0]:.3g} ({row[k][1] * 1e6:.3g})" if k in row else "–")  # noqa: E731
        L.append(f"| {d} | {cell('ref')} | " + " | ".join(cell(c) for c in conds) + " |")
    # nominal cells on the 20 mV grid
    K = keys()
    nom = nominal_runs(OUT / "mc_cell_settling_channels.jsonl", lambda r: r["cond"] in ("4 K proxy",) + conds)
    L.extend(["", "Nominal cell on the 20 mV grid: curvature (uV) and margins at 99.99 % / 99.9 %, 33.69 dec/V: "
              "open-loop and 50 mV moves.", "",
              "| design | condition | curvature | open-loop 99.99 % | 50 mV move 99.9 % | 50 mV move 99.99 % |", "|---|---|---|---|---|---|"])
    import mc_cell_settling as M10
    for d in (Y8.NMOS, Y8.BOOT, Y8.TGD, Y8.TG, M10.wide_name("TG", 5.0), M10.wide_name("TG", 40.0)):
        for c in ("4 K proxy",) + conds:
            dd = nom.get((d, c))
            row = fine_metrics(dd, K) if dd else None
            if row is None:
                continue
            out["nominal"][f"{d}|{c}"] = row
            L.append(f"| {d} | {c} | {row['curvature_uV']:.3g} | {row['99.99 %, 33.69']['open_loop']:.3g} | "
                     f"{row['99.9 %, 33.69']['move50']:.3g} | {row['99.99 %, 33.69']['move50']:.3g} |")
    L.append("")
    return out


def band():
    recs = json.loads((OUT / "mc_cell_settling_pedestals.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(10)
    out = {}
    L.extend(["## Interpolation bias of move margins, 4 K high band (20 channels, fine windows)", "",
              "| design | 20 mV: interpolated / fine | 50 mV: interpolated / fine |", "|---|---|---|"])
    for name, rec in recs.items():
        d, c = name.split("|", 1)
        if c != "4 K high":
            continue
        x, v, std, nominal, fine = CM.prepare(rec)
        if not fine:
            continue
        A = CM.residual_operator(v, std)
        q, _ = CM.worst(x, v, std, A, nominal, B, 200_000, rng, fine)
        row = {}
        for span in (20, 50):
            a, b = q.get(f"{W}|move{span}mVinterp|mixed"), q.get(f"{W}|move{span}mVwin|mixed")
            if a and b:
                row[span] = b / a                      # margins are 1/q: interpolated margin / fine margin
        out[d] = row
        L.append(f"| {d} | " + " | ".join(f"{row[s]:.2f}" if s in row else "–" for s in (20, 50)) + " |")
    if out:
        out["max"] = {s: max(r[s] for r in out.values() if s in r) for s in (20, 50)}
        L.append(f"\nLargest overstatement: 20 mV {out['max'][20]:.2f}, 50 mV {out['max'][50]:.2f} "
                 "(4 K band: 1.60 and 1.27).")
    L.append("")
    return out


def window():
    import pair_spread as Q
    recs = json.loads((ROOT / "results" / "mc_cell_pedestals.json").read_text(encoding="utf-8"))
    b = {"99.99 %": Q.budgets(3.87, 1e-4, 1.0), "99.9 %": Q.budgets(3.87, 1e-3, 1.0)}
    out = {}
    L.extend(["## Usable window at 3.87 dec/V: line fitted over 0.3 to 1.1 V (usable with the 0.67 V pulse) vs 0.3 to 1.5 V, 4 K band",
              "", "| design | 99.99 %: 0.3-1.5 / 0.3-1.1 V | 99.9 %: 0.3-1.5 / 0.3-1.1 V |", "|---|---|---|"])
    for d in Y8.FIG6:
        rec = recs[f"{d}|4 K proxy"]
        x, v, std, nominal, _ = CM.prepare(rec)
        sel = std.copy()
        x, v, nominal = x[:, sel], v[sel], nominal[sel]
        std = np.ones(len(v), bool)
        t = Y8.tau(d, "4 K proxy")
        row = {}
        for lab, top in (("full", 9.9), ("1.1", 1.1 + 1e-9)):
            k = v <= top
            A = CM.residual_operator(v[k], std[k])
            m, s = Y.moments(x[:, k], v[k], std[k], A, nominal[k], "full")
            row[lab] = {tg: Y.margin_closed(m * (1 + t), s * (1 + t), bb) for tg, bb in b.items()}
        out[d] = row
        L.append(f"| {d} | {row['full']['99.99 %']:.3g} / {row['1.1']['99.99 %']:.3g} | "
                 f"{row['full']['99.9 %']:.3g} / {row['1.1']['99.9 %']:.3g} |")
    L.append("")
    return out


def main():
    out = {}
    for name, f in (("wide", wide), ("partition", partition), ("band", band), ("window", window)):
        try:
            out[name] = f()
        except FileNotFoundError as e:
            L.append(f"## {name}: input missing ({e.filename})\n")
    (OUT / "settling_and_partition.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    (OUT / "settling_and_partition.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
