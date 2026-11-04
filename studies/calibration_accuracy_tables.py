"""Table rows from results/calibration_accuracy.json: margins of the switches sized for settling, their shortest
node time constant and the calibration-point accuracy for a margin of one.

Run:  python studies/calibration_accuracy_tables.py     (writes results/calibration_accuracy_tables.md)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "studies"))
import operational_budget as common  # noqa: E402

W = common.WORST
A = json.loads((OUT / "calibration_accuracy.json").read_text(encoding="utf-8"))
NICE = {"TG": "TG", "TG + dummies": "TG with dummies", "bootstrapped": "Bootstrapped NMOS", "NMOS": "NMOS, 0.3 V underdrive"}


def f(x):
    if x >= 100:
        return f"{float(f'{x:.3g}'):.0f}"
    return f"{x:.2g}" if x < 10 else f"{x:.2g}".replace("e+01", "0")


def g(x):
    return f"{x:.2g}" if x < 10 else f"{x:.0f}"


L = ["## Switches sized for settling (nominal, 20 mV grid, calibrated range; open-loop on every grid voltage; 1 mV from the spline slope)", ""]
rows = A["B"]["rows"]
for arch in ("TG", "TG + dummies", "bootstrapped", "NMOS"):
    for w in (5, 10, 20, 40):
        r3, r4 = rows[f"{arch}|{w}|300 K"], rows[f"{arch}|{w}|4 K proxy"]
        L.append(f"| {NICE[arch]} | {w} | {r3['tau_node'] * 1e9:.2g} | {g(r3['99.99']['open_line'])} / {g(r4['99.99']['open_line'])} | "
                 f"{g(r3['99.9']['move50_line'])} / {g(r4['99.9']['move50_line'])} | "
                 f"{g(r3['99.99']['move1_spline'])} / {g(r4['99.99']['move1_spline'])} |")
L += ["", "## Shortest node time constant (ns): '<' where every width passes", "",
      "| Cell | 50 mV re-bias, 99.9% | 50 mV re-bias, 99.99% | open-loop, line | open-loop, quadratic | open-loop, line over 0.4 V |",
      "|---|---|---|---|---|---|"]
for arch in ("TG", "TG + dummies", "bootstrapped", "NMOS"):
    cells = []
    for key, met in (("99.9", "move50_line"), ("99.99", "move50_line"), ("99.99", "open_line"),
                     ("99.99", "open_quadratic"), ("99.99", "open_window")):
        rs = [r for k, r in rows.items() if k.startswith(arch + "|")]
        allpass = all(r[key][met] > 1 for r in rs)
        tmin = min(r["tau_node"] for r in rs)
        t = A["B"]["tau_min"][arch][f"{key}|{met}"]
        cells.append(f"below {tmin * 1e9:.2g}" if allpass else f"{t * 1e9:.2g}")
    L.append(f"| {NICE[arch]} | " + " | ".join(cells) + " |")
L += ["", "## Point accuracy for a margin of one (uV): line / quadratic / 0.4 V window, smallest over the conditions", ""]
nine = ("300 K", "77 K proxy", "4 K proxy", "4 K high", "77 K Beall fit", "4 K, Beall pMOS", "4 K, steep (T_eff 120 K)",
        "4 K, tree, ESD-dominated droop", "4 K, tree, one reticle")
for name, r in A["A"].items():
    pass
designs = sorted({n.split("|")[0] for n in A["A"]})
for d in designs:
    rs = {n: r for n, r in A["A"].items() if n.split("|")[0] == d and (n.startswith("GF180") or n.split("|")[1] in nine)}
    cells = []
    for k in ("line", "quadratic", "window"):
        vals = [r[k][W]["sigma_req"] for r in rs.values()]
        cells.append("–" if min(vals) == 0 else f"{min(vals) * 1e6:.0f}")
    L.append(f"| {d} | " + " / ".join(cells) + " |")
L += ["", "## Steep bands and mismatch, smallest quadratic / window margin (all voltages)", ""]
for n, r in A["A"].items():
    if any(c in n for c in ("T_eff 30", "T_eff 20", "mismatch")):
        L.append(f"- {n}: line {r['line'][W]['margin_all']:.3g}, quadratic {r['quadratic'][W]['margin_all']:.3g}, "
                 f"window {r['window'][W]['margin_all']:.3g}")
fac = {k: max(r[k][W]["margin_std"] / r[k][W]["margin_all"] for r in A["A"].values()) for k in ("line", "quadratic", "window")}
L += ["", f"Largest margin at standard voltages / on every simulated voltage: {fac}", ""]
(OUT / "calibration_accuracy_tables.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
