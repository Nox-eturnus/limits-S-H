"""Tail-corrected values of every margin that the article and its Supplementary Information quote.

From results/tail_corrected.json and, for the uncorrected values, results/cell_margins.json.
Run:  python studies/quoted_numbers.py      (seconds; writes results/quoted_numbers.md)
"""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tail_corrected as Y8  # noqa: E402

W, N99, REF = Y8.W, Y8.N99, Y8.REF
D = json.loads((OUT / "tail_corrected.json").read_text(encoding="utf-8"))["designs"]
r6 = json.loads((Y8.ROOT / "results" / "cell_margins.json").read_text(encoding="utf-8"))["designs"]
FIG6 = Y8.FIG6
CRYO = ("77 K proxy", "4 K proxy", "4 K high", "77 K Beall fit", "4 K, Beall pMOS", "4 K, steep (T_eff 120 K)",
        "4 K, steep (T_eff 30 K)", "4 K, steep (T_eff 20 K)", "4 K, clock edge 600 ps", "4 K, clock edge 67 ps")
TREES = ("4 K, tree source", "4 K, tree, ESD-dominated droop", "4 K, tree, one reticle", "4 K, tree, ESD diodes on 1 pF",
         "4 K, buffered leaf line")
L = []


def m(name, key=W, kind="full"):
    r = D.get(name)
    k = f"{key}|{kind}|mixed"
    return None if r is None or k not in r["margin"] else r["margin"][k]


def v(name, key=W, kind="full"):
    return D[name]["verdict"].get(f"{key}|{kind}|mixed")


def lo_of(items):
    items = [(n, x) for n, x in items if x is not None]
    n, x = min(items, key=lambda t: t[1])
    return f"{x:.3g} ({n})"


# room temperature, Table S3
pd = [n for n in D if n.startswith("D ") and n.endswith("|300 K")]
L.append("## Room temperature (Table S3 cells)")
L.append(f"- 99.9 %, 10 dec/V per channel lowest: {lo_of([(n, m(n, REF)) for n in pd])}")
L.append(f"- 99.9 %, 33.69 per channel lowest: {lo_of([(n, m(n, N99)) for n in pd])}")
L.append(f"- 99.9 %, 10 dec/V shared lowest: {lo_of([(n, m(n, REF, 'shared')) for n in pd])}; verdicts "
         + ", ".join(f"{n.split('|')[0]} {v(n, REF, 'shared')}" for n in pd))
L.append("- strictest shared: " + ", ".join(f"{n.split('|')[0]} {m(n, kind='shared'):.3g} {v(n, kind='shared')}" for n in pd))
for span, f in (("move50mV", 1.27), ("move20mV", 1.60)):
    L.append(f"- {span} strictest, lowest as stored: {lo_of([(n, m(n, kind=span)) for n in pd])}; divided by {f}: "
             f"{min(m(n, kind=span) for n in pd) / f:.3g}")

# Figure 6 designs, all bands and trees
L.append("\n## Figure 6 designs, cryogenic bands and trees")
allc = [n for n in D if n.split("|")[0] in FIG6 and "mismatch" not in n]
cryo_trees = [n for n in allc if n.split("|")[1] in CRYO + TREES]
for key, lab in ((REF, "99.9 %, 10 dec/V"), (N99, "99.9 %, 33.69")):
    for kind in ("full", "shared"):
        L.append(f"- {lab} {kind}, all conditions incl. 300 K: lowest {lo_of([(n, m(n, key, kind)) for n in allc])}")
    nv = [(n, v(n, N99, "shared")) for n in allc if v(n, N99, "shared") != "pass"]
    if key == N99:
        L.append(f"- 99.9 %, 33.69 shared not pass: {nv}")
for span in ("move20mV", "move50mV"):
    fine = [n for n in cryo_trees if r6[n]["fine"]]
    interp = [n for n in cryo_trees if not r6[n]["fine"]]
    # interpolation bias measured in the fine windows (uncorrected margins: the factor is a ratio, unchanged by tau)
    over = [r6[n]["margin"][f"{W}|{span}interp|mixed"] / r6[n]["margin"][f"{W}|{span}win|mixed"] for n in fine
            if f"{W}|{span}interp|mixed" in r6[n]["margin"]]
    f = max(over)
    L.append(f"- {span}: bias {min(over):.2f} to {f:.2f}; fine grid lowest {lo_of([(n, m(n, kind=span)) for n in fine])}; "
             f"interpolated lowest corrected {lo_of([(n, m(n, kind=span) / f) for n in interp])}")
for d in FIG6:
    cs = [n for n in allc if n.startswith(d + "|")]
    L.append(f"- {d}: per channel {min(m(n) for n in cs):.3g} to {max(m(n) for n in cs):.3g}; "
             f"cryo 50 ohm {min(m(n) for n in cs if n.split('|')[1] in CRYO):.3g} to {max(m(n) for n in cs if n.split('|')[1] in CRYO):.3g}; "
             f"trees {min(m(n) for n in cs if n.split('|')[1] in TREES):.3g} to {max(m(n) for n in cs if n.split('|')[1] in TREES):.3g}; "
             f"shared {min(m(n, kind='shared') for n in cs):.3g} to {max(m(n, kind='shared') for n in cs):.3g}; "
             f"shared cryo 50 ohm {min(m(n, kind='shared') for n in cs if n.split('|')[1] in CRYO):.3g} to "
             f"{max(m(n, kind='shared') for n in cs if n.split('|')[1] in CRYO):.3g}; verdicts "
             + ", ".join(f"{n.split('|')[1]}: {v(n)}" for n in cs if v(n) != "pass"))
for d in ("TG, no ESD", "TG, ESD on the node"):
    nonpmos = [n for n in allc if n.startswith(d + "|") and "Beall" not in n]
    L.append(f"- {d} outside the measured-PMOS bands: {min(m(n) for n in nonpmos):.3g} to {max(m(n) for n in nonpmos):.3g}")
    pm = [n for n in allc if n.startswith(d + "|") and "Beall" in n]
    L.append(f"- {d} in the measured-PMOS bands: {min(m(n) for n in pm):.3g} to {max(m(n) for n in pm):.3g}")
tg = "TG, no ESD|4 K high"
L.append(f"- TG 4 K high: {m(tg):.3g} [{D[tg]['ci90'][f'{W}|full|mixed'][0]:.3g}, {D[tg]['ci90'][f'{W}|full|mixed'][1]:.3g}] {v(tg)}")
L.append(f"- TG 4 K: {m('TG, no ESD|4 K proxy'):.3g} {D['TG, no ESD|4 K proxy']['ci90'][f'{W}|full|mixed']}")
L.append(f"- TG 300 K: {m('TG, no ESD|300 K'):.3g} {D['TG, no ESD|300 K']['ci90'][f'{W}|full|mixed']}")
for c in ("4 K proxy", "4 K high", "4 K, tree, ESD-dominated droop", "4 K, tree, one reticle", "300 K"):
    n = f"TG, no ESD|{c}"
    L.append(f"- P(array) TG {c}: {D[n]['p|full']['model']:.3g}")
L.append("- P(array) per channel largest over the other designs: " + ", ".join(
    f"{d} {max(D[n]['p|full']['model'] for n in allc if n.startswith(d + '|')):.2g}" for d in FIG6 if d != "TG, no ESD"))
L.append("- P(array) model error, largest over conditions: " + "; ".join(
    f"{d}: mism2 {max(D[n]['p|full']['mismatch x 2'] for n in allc if n.startswith(d + '|')):.2g}, curv1.3 "
    f"{max(D[n]['p|full']['curvature x 1.3'] for n in allc if n.startswith(d + '|')):.2g}" for d in FIG6))
(OUT / "quoted_numbers.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
