"""Every worst-channel margin against the per-gate and the operational budget.

A margin is budget / error, so a margin computed at one budget converts to another by the ratio of
the budgets. The per-gate budgets come from results/cryogenic.json (s = 10 and 33.69 dec/V, 99.9 %
and 99.99 %), and the operational budget is the frame-tracked budget over M = 4 repeated gates
(results/repeated_gates.json), taken as a ratio to the single-gate budget of the same run.

Inputs: results/mismatch.json (300 K, nine cells), results/mismatch_bands.json (six designs in six
bands). Run:  python studies/margins.py      (seconds; writes results/margins.{json,md})
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "studies"))
import mismatch as W  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
M_QEC = "4"
POINTS = (("s33.69_t0.0001", 33.69, 1e-4), ("s33.69_t0.001", 33.69, 1e-3), ("s10_t0.001", 10.0, 1e-3))
CAL = (("per_channel_N1e+06", "per-channel"), ("shared_N1e+06", "shared"))


def budgets():
    spec = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))["spec"]
    rg = json.loads((ROOT / "results" / "repeated_gates.json").read_text(encoding="utf-8"))
    out = {}
    for key, s, t in POINTS:
        row = next(r for r in rg["rows"] if r["s"] == s and r["target"] == t)
        out[key] = {"per_gate": spec[key], "operational": spec[key] * row["frame"][M_QEC] / row["v1_exact"]}
    return out


def convert(m_worst, spec_worst, bud):
    """Margins at every point and budget from the margins at the strictest per-gate point."""
    return {f"{key}|{kind}": {lab: m_worst[cal] * b / spec_worst for cal, lab in CAL}
            for key, bb in bud.items() for kind, b in bb.items()}


def main():
    bud = budgets()
    wc = json.loads((ROOT / "results" / "mismatch.json").read_text(encoding="utf-8"))
    out = {"budgets": bud, "300K": {}, "bands": {}}
    for arch, r in wc["room_temperature"].items():
        out["300K"][W.ARCH_NAMES.get(arch, arch)] = convert(r["margins"][W.WORST], r["spec"][W.WORST], bud)
    p = OUT / "mismatch_bands.json"
    if p.exists():
        wb = json.loads(p.read_text(encoding="utf-8"))
        for k, r in wb["bands"].items():
            c = convert(r["margins"][W.WORST], r["spec"][W.WORST], bud)
            c["nominal_per_gate"] = r["nominal_margin"][W.WORST]
            c["nominal_operational"] = r["nominal_margin"][W.WORST] * bud[W.WORST]["operational"] / r["spec"][W.WORST]
            out["bands"][k] = c
        out["tail"] = {d: convert(r["margins"][W.WORST], r["spec"][W.WORST], bud) | {"n": r["tail"]["n"]}
                       for d, r in wb.get("tail", {}).items()}
    (OUT / "margins.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def table(out):
    b = out["budgets"]
    L = ["## Worst-of-10^6 margins, per-gate and operational budget", "",
         "Budgets (mV): " + "; ".join(f"{k}: per-gate {v['per_gate'] * 1e3:.3f}, operational {v['operational'] * 1e3:.3f}"
                                      for k, v in b.items()), ""]
    for title, rows in (("300 K, nine cells (20 channels)", out["300K"]), ("Bands (20 channels)", out["bands"]),
                        ("4 K band, long runs", out.get("tail", {}))):
        L += [f"### {title}", "", "| cell | per-gate 99.99 % s 33.69: per-ch / shared | operational 99.99 % s 33.69 "
              "| operational 99.9 % s 33.69 | operational 99.9 % s 10 |", "|---|---|---|---|---|"]
        for name, c in rows.items():
            f = lambda k: f"{c[k]['per-channel']:.2f} / {c[k]['shared']:.2f}"  # noqa: E731
            L.append(f"| {name} | {f('s33.69_t0.0001|per_gate')} | {f('s33.69_t0.0001|operational')} | "
                     f"{f('s33.69_t0.001|operational')} | {f('s10_t0.001|operational')} |")
        L.append("")
    (OUT / "margins.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    table(main())
