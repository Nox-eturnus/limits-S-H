"""Every worst-channel margin that the article quotes, before the tail correction, from results/cell_margins.json.

The nine cells of studies/cells.py at 300 K are listed under "D <arch>|300 K"; also the sizing variants,
the moves from a tuned level on the fine grid and the buffered leaf line. studies/quoted_numbers.py gives
the numbers with the tail correction of studies/tail_corrected.py.

Run:  python studies/quoted_margins.py     (seconds; writes results/quoted_margins.md)
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "results"
W, N, R = "s33.69_t0.0001", "s33.69_t0.001", "s10_t0.001"
NMOS, BOOT = "NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive"
TSWO, TGD, TG, TGE = "T-switch + OTA buffer", "TG + dummies", "TG, no ESD", "TG, ESD on the node"
FIG6 = (NMOS, BOOT, TSWO, TGD, TG, TGE)
NINE_CELLS = ("NSW", "TG", "TGD", "BOOT", "CLK", "TSW", "TGH", "TSWB", "NTB")
S6_BANDS = ("300 K", "77 K proxy", "4 K proxy", "4 K high", "77 K Beall fit", "4 K, Beall pMOS", "4 K, steep (T_eff 120 K)",
            "4 K, tree, ESD-dominated droop", "4 K, tree, one reticle")
S7_BANDS = ("4 K proxy", "4 K, steep (T_eff 120 K)", "4 K, steep (T_eff 30 K)", "4 K, steep (T_eff 20 K)", "4 K, clock edge 600 ps",
      "4 K, clock edge 67 ps", "4 K, tree source", "4 K, tree, ESD-dominated droop", "4 K, tree, one reticle",
      "4 K, tree, ESD diodes on 1 pF", "4 K, buffered leaf line", "4 K, mismatch x 1.5", "4 K, mismatch x 2")
CRYO50 = ("77 K proxy", "4 K proxy", "4 K high", "77 K Beall fit", "4 K, Beall pMOS", "4 K, steep (T_eff 120 K)",
          "4 K, steep (T_eff 30 K)", "4 K, steep (T_eff 20 K)", "4 K, clock edge 600 ps", "4 K, clock edge 67 ps")
TREES = ("4 K, tree source", "4 K, tree, ESD-dominated droop", "4 K, tree, one reticle", "4 K, tree, ESD diodes on 1 pF",
         "4 K, buffered leaf line")
MOVES = ("move20mV", "move50mV", "move100mV", "move200mV")


def main():
    ra = json.loads((OUT / "cell_margins.json").read_text(encoding="utf-8"))
    D = ra["designs"]

    def g(d, b, key=W, kind="full"):
        r = D.get(f"{d}|{b}")
        k = f"{key}|{kind}|mixed"
        if r is None or k not in r["margin"]:
            return None
        lo, hi = r["ci90"][k]
        return {"m": r["margin"][k], "lo": lo, "hi": hi, "cls": "pass" if lo > 1 else "fail" if hi < 1 else "indet",
                "ex": r["exceed_per_1e6"].get(k), "n": r["n"], "win": r["window"]}

    def fm(x):
        return "–" if x is None else f"{x['m']:.2f} [{x['lo']:.2f}, {x['hi']:.2f}] {x['cls']}"

    def ex(x):
        v = None if x is None else x["ex"]
        return "–" if v is None else "0" if v < 0.05 else f"{v:.2g}"

    def rng(xs):
        xs = [x for x in xs if x is not None]
        return "–" if not xs else f"{min(x['m'] for x in xs):.2f}-{max(x['m'] for x in xs):.2f}"

    L = ["## Margins quoted in the article (one cell per channel, before the tail correction)", "",
         f"Budgets: " + ", ".join(f"{k}: b_eq {b['b_eq'] * 1e6:.0f} µV, b_ind {b['b_ind'] * 1e6:.0f} µV" for k, b in ra["budgets"].items()), ""]

    L += ["### Equal sizing (strictest per-channel | shared | exceed | 99.9 % 33.69 | 10 dec/V | move 20 / 50 mV)", ""]
    for name in sorted(n for n in D if ", W " in n.split("|")[0] or n.split("|")[0] in FIG6):
        d, b = name.split("|")
        if b not in ("4 K proxy", "4 K, tree, ESD-dominated droop"):
            continue
        a = g(d, b)
        L.append(f"- {d} | {b} (n {a['n']}, window {a['win']}): {fm(a)} | shared {fm(g(d, b, kind='shared'))} | exceed {ex(a)} | "
                 f"{fm(g(d, b, N))} | {fm(g(d, b, R))} | {fm(g(d, b, kind='move20mV'))} / {fm(g(d, b, kind='move50mV'))}")

    L += ["", "### Nine cells, 300 K (Table S3): per-channel | shared | exceed | 99.9 % 33.69 | 10 dec/V | shared 10 dec/V | move 50 mV", ""]
    for a_ in NINE_CELLS:
        d = f"D {a_}"
        a = g(d, "300 K")
        if a is None:
            L.append(f"- {d}: –")
            continue
        L.append(f"- {d}: {fm(a)} | shared {fm(g(d, '300 K', kind='shared'))} | exceed {ex(a)} | {g(d, '300 K', N)['m']:.2f} | "
                 f"{g(d, '300 K', R)['m']:.2f} | {g(d, '300 K', R, 'shared')['m']:.2f} | {fm(g(d, '300 K', kind='move50mV'))}")

    L += ["", "### Table S6 (per-channel / shared at the strictest point; class)", "",
          "| design | " + " | ".join(S6_BANDS) + " |", "|---|" + "---|" * len(S6_BANDS)]
    for d in FIG6:
        cells = []
        for b in S6_BANDS:
            x, s = g(d, b), g(d, b, kind="shared")
            cells.append("–" if x is None else f"{x['m']:.2f} / {s['m']:.2f} {x['cls']}")
        L.append(f"| {d} | " + " | ".join(cells) + " |")

    L += ["", "### Table S7 (strictest (exceed) | 99.9 % 33.69)", "",
          "| variant | " + " | ".join(f"{d} strictest | {d} 99.9 %" for d in (NMOS, BOOT, TGD)) + " |", "|---|" + "---|---|" * 3]
    for b in S7_BANDS:
        cells = []
        for d in (NMOS, BOOT, TGD):
            x = g(d, b)
            cells += ["–", "–"] if x is None else [f"{x['m']:.2f} {x['cls']} ({ex(x)})", f"{g(d, b, N)['m']:.3g}"]
        L.append(f"| {b} | " + " | ".join(cells) + " |")

    L += ["", "### Moves from a tuned level, strictest point (fine grid where simulated)", "",
          "| design | condition | " + " | ".join(MOVES) + " | full |", "|---|---|" + "---|" * (len(MOVES) + 1)]
    for name, r in sorted(D.items()):
        if "mismatch" in name:
            continue
        d, b = name.split("|")
        L.append(f"| {d} | {b}{' (fine)' if r.get('fine') else ''} | " + " | ".join(
            "–" if g(d, b, kind=k) is None else f"{g(d, b, kind=k)['m']:.2f} {g(d, b, kind=k)['cls']}" for k in MOVES)
                 + f" | {g(d, b)['m']:.2f} |")

    L += ["", "### Summary statistics", ""]
    for d in FIG6:
        xs = [g(d, b) for b in set(S6_BANDS + S7_BANDS + CRYO50) if g(d, b) and "mismatch" not in b]
        xc = [g(d, b) for b in CRYO50 if g(d, b)]
        xt = [g(d, b) for b in TREES if g(d, b)]
        L.append(f"- {d}: all {rng(xs)} classes {sorted(set(x['cls'] for x in xs))}; cryo 50 ohm {rng(xc)}; trees {rng(xt)}; "
                 f"exceed max {max((x['ex'] or 0) for x in xs):.3g}; lowest lower bound {min(x['lo'] for x in xs):.3f}; "
                 f"99.9 % 33.69 {rng([g(d, b, N) for b in S6_BANDS + S7_BANDS])}; 10 dec/V {rng([g(d, b, R) for b in S6_BANDS + S7_BANDS])}")
    for key in (N, R):
        allm = [(n, r["margin"][f"{key}|full|mixed"], r["ci90"][f"{key}|full|mixed"]) for n, r in D.items() if "mismatch" not in n]
        worst = min(allm, key=lambda t: t[1])
        nonpass = [n for n, m, ci in allm if ci[0] <= 1]
        L.append(f"- {key}: min per-channel {worst[1]:.2f} ({worst[0]}); not passing: {nonpass}")
    for d in (NMOS, BOOT, TGD):
        L.append(f"- {d} x1.5 / x2 mismatch: strictest {fm(g(d, '4 K, mismatch x 1.5'))} / {fm(g(d, '4 K, mismatch x 2'))}; "
                 f"99.9 % {fm(g(d, '4 K, mismatch x 2', N))}")
    for d in FIG6:
        for k in MOVES[:2]:
            xs = [g(d, b, kind=k) for b in CRYO50 + TREES]
            L.append(f"- {k} {d}: cryo + trees {rng(xs)}")
    sh = [(n, r["margin"][f"{W}|shared|mixed"]) for n, r in D.items() if "mismatch" not in n]
    L.append("- shared calibration, strictest, passing (> 1): " + ", ".join(f"{n} {m:.2f}" for n, m in sorted(sh) if m > 1))
    corr = [r["corr_adjacent_mean"] for r in D.values()]
    L.append(f"- adjacent-voltage pedestal correlation of the channels: {min(corr):.2f} to {max(corr):.2f}")
    (OUT / "quoted_margins.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
