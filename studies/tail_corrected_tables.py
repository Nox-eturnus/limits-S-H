"""Supplementary tables with the tail correction of studies/tail_corrected.py.

  Table S10  capacitance sensitivity (results/scaled_sigma_capacitance.json)
  Table S19  joint allocation (results/allocation.json), with the sampled-DAC-noise limits
  Table S20  measured operating points (results/system_operation.json)
  Table S26  GF180MCU (results/gf180.json); no scaled-sigma run exists in this process, so the largest measured
             tail optimism applies.

Run:  python studies/tail_corrected_tables.py      (seconds; writes results/tail_corrected_tables.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "studies"))
import tail_corrected as Y8  # noqa: E402
import array_yield as Y7  # noqa: E402

W, N99, REF = Y8.W, Y8.N99, Y8.REF
LAB = {"NMOS": Y8.NMOS, "bootstrapped": Y8.BOOT, "T-switch + OTA": Y8.TSWO, "TG + dummies": Y8.TGD, "TG": Y8.TG,
       "TG with ESD": Y8.TGE}


def main():
    out, L = {}, ["# Supplementary tables with the tail correction", ""]

    # ---- Table S10
    a7 = json.loads((ROOT / "results" / "scaled_sigma_capacitance.json").read_text(encoding="utf-8"))["capsens"]
    conds = ("4 K proxy", "4 K, overlap capacitances x 0.7", "4 K, overlap capacitances x 1.3",
             "4 K, junction capacitances x 0.7", "4 K, junction capacitances x 1.3")
    L += ["## Table S10", "", "| Cell | Reference | Overlap × 0.7 | Overlap × 1.3 | Junction × 0.7 | Junction × 1.3 |",
          "|---|---|---|---|---|---|"]
    out["table_S10"] = {}
    for d, rows in a7.items():
        cells = []
        for c in conds:
            r = rows[c]
            t = Y8.tau(d, c)
            f, s = r[f"{W}|full"]["margin"] / (1 + t), r[f"{W}|shared"]["margin"] / (1 + t)
            out["table_S10"][f"{d}|{c}"] = [f, s]
            cells.append(f"{f:.3g} / {s:.3g}")
        L.append(f"| {d} | " + " | ".join(cells) + " |")
    L.append("")

    # ---- Table S19
    al = json.loads((ROOT / "results" / "allocation.json").read_text(encoding="utf-8"))
    L += ["## Table S19", "", "| point | device | DAC | share | NMOS alone / joint | bootstrapped | TG + dummies |", "|---|---|---|---|---|---|---|"]
    out["table_S19"] = []
    dmap = {"NMOS": Y8.NMOS, "bootstrapped": Y8.BOOT, "TG + dummies": Y8.TGD}
    for key, pt in al["points"].items():
        for r in pt["rows"]:
            cells = []
            for k, d in dmap.items():
                t = Y8.tau(d, "4 K proxy")
                cells.append(f"{r[k]['alone'] / (1 + t):.3g} / {r[k]['joint'] / (1 + t):.3g}")
            L.append(f"| {key} | {r['device'] * 1e6:g} | {r['dac'] * 1e6:g} | {r['share']:.3g} | " + " | ".join(cells) + " |")
    # sampled DAC noise at which the joint margin falls to one, strictest point, 9 uV/rtHz device
    pt = al["points"][W]
    b = pt["b_ind"]
    r9 = [r for r in pt["rows"] if abs(r["device"] - 9e-6) < 1e-9 and r["dac"] == 0][0]
    lims = {}
    for k, d in dmap.items():
        m = r9[k]["alone"] / (1 + Y8.tau(d, "4 K proxy"))
        lims[k] = float(b * np.sqrt(max(1 - r9["share"] - (0.1 + 1 / m) ** 2, 0)))
    out["table_S19_dac_limit_V"] = lims
    L += ["", "Sampled DAC noise at which the joint margin falls to one (strictest point, 9 µV/√Hz device): "
          + ", ".join(f"{k} {v * 1e6:.0f} µV rms" for k, v in lims.items()), ""]

    # ---- Table S20
    s7 = json.loads((ROOT / "results" / "system_operation.json").read_text(encoding="utf-8"))["measured_devices"]
    L += ["## Table S20", "", "| device | s | target | " + " | ".join(LAB) + " |", "|---|---|---|" + "---|" * len(LAB)]
    out["table_S20"] = []
    for r in s7:
        cells = []
        for k, d in LAB.items():
            t = Y8.tau(d, "4 K proxy")
            x = r["designs"][k]
            cells.append(f"{x['full'] / (1 + t):.3g} / {x['shared'] / (1 + t):.3g} / {x['joint_49'] / (1 + t):.3g}")
            out["table_S20"].append({"device": r["device"], "target": r["target"], "design": k, "full": x["full"] / (1 + t),
                               "shared": x["shared"] / (1 + t), "joint_49": x["joint_49"] / (1 + t)})
        L.append(f"| {r['device']} | {r['s']:g} | {r['target']:g} | " + " | ".join(cells) + " |")
    for tgt in (1e-3, 1e-4):
        for kind in ("full", "shared", "joint_49"):
            rows = [x for x in out["table_S20"] if x["target"] == tgt and not (tgt == 1e-4 and "Nickl" in x["device"])]
            mn = min(rows, key=lambda x: x[kind])
            L.append(f"- target {tgt:g} (strictest point excluded at 99.99 %), {kind}: lowest {mn[kind]:.3g} ({mn['design']}, {mn['device']})")
    L.append("")

    # ---- Table S26
    g = json.loads((ROOT / "results" / "gf180.json").read_text(encoding="utf-8"))
    rows = (("NMOS, 0.3 V underdrive, 0.3 to 0.9 V", "GF180 NMOS, 0.3 V underdrive", Y8.NMOS),
            ("NMOS, 0.3 V underdrive, 0.3 to 1.5 V", "GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V", None),
            ("Bootstrapped NMOS, transistor level", "GF180 bootstrapped (transistor level), 0.3 V underdrive", Y8.BOOT),
            ("TG with dummies", "GF180 TG + dummies", Y8.TGD), ("TG, 1 µm", "GF180 TG, no ESD", Y8.TG),
            ("TG, 0.42 µm", "GF180 TG, no ESD, W 0.42", Y8.TG + ", W 0.42"))
    y8 = json.loads((OUT / "tail_corrected.json").read_text(encoding="utf-8"))["designs"]
    t = Y8.TAU_MAX
    L += ["## Table S26", "", "| Cell | SKY130, 4 K | GF180, 300 K | GF180, 4 K | GF180, 4 K, high shift | GF180, 99.9%, 10 dec/V, per channel | GF180, 50 mV moves |",
          "|---|---|---|---|---|---|---|"]
    out["table_S26"] = {}
    for lab, gname, skyname in rows:
        sky = "–"
        if skyname and f"{skyname}|4 K proxy" in y8:
            r = y8[f"{skyname}|4 K proxy"]
            sky = f"{r['margin'][f'{W}|full|mixed']:.3g} / {r['margin'][f'{W}|shared|mixed']:.3g}"
        cells, ref, mv, verd = [], [], [], []
        for band in ("300 K", "4 K proxy", "4 K high"):
            r = g[f"{gname}|{band}"]
            f, s = r["margin"][f"{W}|full|mixed"] / (1 + t), r["margin"][f"{W}|shared|mixed"] / (1 + t)
            lo, hi = r["ci90"][f"{W}|full|mixed"]
            verd.append(Y8.verdict(skyname or Y8.NMOS, lo, hi, t))
            cells.append(f"{f:.3g} / {s:.3g}")
            ref.append(r["margin"][f"{REF}|full|mixed"] / (1 + t))
            mv.append(r["margin"][f"{W}|move50mV|mixed"] / (1 + t))
        out["table_S26"][lab] = {"cells": cells, "ref_min": min(ref), "move50_min": min(mv), "verdicts": verd}
        L.append(f"| {lab} | {sky} | " + " | ".join(cells) + f" | {min(ref):.3g} | {min(mv):.3g} |  ({', '.join(verd)})")
    L.append("")
    (OUT / "tail_corrected_tables.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT / "tail_corrected_tables.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
