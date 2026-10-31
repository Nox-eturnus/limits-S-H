"""Figures of the paper, built from the stored results.

    python figures/make_figures.py              # all figures, from stored results (about 1 min)
    python figures/make_figures.py --recompute  # also recompute the cached error-budget curves (a few min)
    python figures/make_figures.py fig2 fig5    # selected figures

Writes figures/figN_<name>.{pdf,png}; fig7 and figS2 are Supplementary Figures S1 and S2. Every figure
is drawn at its printed size, the full text width (6.5 in), with 9-10 pt text. Inputs: the JSON files
in results/, and figures/cache/error_budget_curves.json (cached because panels of Fig. 2 re-evaluate
the CZ model on dense grids).

Colour follows the entity, in a fixed palette order; every series also has its own marker or line
style, so identity is never colour alone. Exchange slope, an ordered quantity, uses one blue ramp
light to dark.
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flow import budget as B  # noqa: E402
from flow import cosim as C  # noqa: E402

import matplotlib  # noqa: E402
import matplotlib.ticker  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parent
CACHE = Path(__file__).resolve().parent / "cache" / "error_budget_curves.json"
W = 6.5                                  # printed width of every figure (in): the text width of the article
REF = "s10_t0.001"
WORST = "s33.69_t0.0001"

# reference palette, fixed slot order (dataviz references/palette.md)
SLOT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SLOPE_RAMP = {3.87: "#86b6ef", 10.0: "#2a78d6", 33.69: "#104281"}     # blue 250 / 450 / 650
INK, INK2, GRID = "#1f1f1e", "#5f5e58", "#d9d8d2"

# one identity per switch family, used in every figure
ARCH = {
    "NSW": ("NMOS", SLOT[0], "o"),
    "TG": ("TG", SLOT[1], "s"),
    "TGD": ("TG + dummies", SLOT[2], "^"),
    "BOOT": ("bootstrapped (ideal drive)", SLOT[3], "v"),
    "BOOTT": ("bootstrapped NMOS", SLOT[3], "D"),
    "CLK": ("charge-locked TG", SLOT[4], "P"),
    "TSW": ("thick T-switch", SLOT[5], "X"),
    "TSWB": ("T-switch, ideal buffer", SLOT[6], "*"),
    "TSWO": ("T-switch + OTA", SLOT[6], "h"),
}
# design names of the stored results -> family key
DESIGN = {
    "NMOS, 0.3 V underdrive": "NSW", "bootstrapped, 0.3 V underdrive": "BOOT",
    "bootstrapped (transistor level), 0.3 V underdrive": "BOOTT", "T-switch + OTA buffer": "TSWO",
    "TG + dummies": "TGD", "TG, no ESD": "TG", "TG, ESD on the node": "TG",
}
BAND_NAME = {"300 K": "300 K", "77 K proxy": "77 K", "4 K proxy": "4 K", "4 K high": "4 K, high shift",
             "77 K Beall fit": "77 K, fitted", "4 K, Beall pMOS": "4 K, measured PMOS shift",
             "4 K, steep (T_eff 120 K)": "4 K, steep", "4 K, steep (T_eff 30 K)": "4 K, steeper (30 K)",
             "4 K, steep (T_eff 20 K)": "4 K, steepest (20 K)",
             "4 K, tree, ESD-dominated droop": "4 K, tree source (5 × 10$^5$)", "4 K, tree, one reticle": "4 K, tree source (one reticle)"}

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "mathtext.fontset": "stix",
    "font.size": 9.5, "axes.titlesize": 10, "axes.labelsize": 9.5, "legend.fontsize": 8,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "axes.linewidth": 0.7, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "lines.linewidth": 1.6, "lines.markersize": 5, "legend.frameon": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300,
    "axes.titlelocation": "left", "axes.titleweight": "bold",
})


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print(f"  {name}")


def limit(ax, y, text, ls="-", where=0.02):
    ax.axhline(y, color=INK2, lw=0.8, ls=ls)
    ax.text(where, y, text, transform=ax.get_yaxis_transform(), fontsize=8, color=INK2, va="bottom")


def two_by_two(height, bottom_span=True, hspace=0.42, wspace=0.32):
    """(fig, a, b, c): panels a and b in the first row, c across the second row (or in its left half)."""
    fig = plt.figure(figsize=(W, height))
    gs = fig.add_gridspec(2, 2, hspace=hspace, wspace=wspace)
    a, b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    c = fig.add_subplot(gs[1, :] if bottom_span else gs[1, 0])
    return fig, a, b, c


# ============================================================================ Fig. 1: architecture

def schematic(ax):
    """Fig. 1a: one multiplexed DAC line with two charge-locked cells, drawn with schemdraw."""
    import io

    import matplotlib.image as mpimg
    import schemdraw
    import schemdraw.elements as elm
    schemdraw.use("matplotlib")
    schemdraw.config(fontsize=10, font="serif", lw=1.0, color=INK)
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=1.6)
        dac = elm.SourceV().up()
        elm.Label().at((dac.center[0] - 0.75, dac.center[1])).label("DAC", loc="left")
        elm.Ground().at(dac.start)
        elm.Resistor().right().at(dac.end).label("$R_{src}$", ofst=0.1)
        line_start = d.here
        taps = []
        for k in range(2):
            elm.Line().right().length(2.0 if k == 0 else 1.8)
            if k == 1:
                elm.Resistor().right().label("wire $R$, $C$", ofst=0.1)
            taps.append(elm.Dot())
        elm.Line().right().length(1.0)
        d.add(elm.Label().at((d.here[0] + 0.1, d.here[1])).label("... $K$ cells", loc="right"))
        d.add(elm.Label().at((line_start[0] + 1.0, line_start[1] + 0.45)).label("shared line", color=INK2))
        for k, tap in enumerate(taps):
            sw = elm.Switch().down().at(tap.center)
            elm.Label().at((sw.center[0] + 0.55, sw.center[1] + 0.1)).label(f"$\\phi_{k + 1}$", loc="right")
            node = elm.Dot().at(sw.end)
            cn = elm.Capacitor().down().at(node.center)
            elm.Label().at((cn.center[0] - 0.55, cn.center[1] - 0.45)).label("$C_{node}$", loc="left")
            elm.Ground().at(cn.end)
            elm.Line().right().at(node.center).length(1.1)
            pn = elm.Dot()
            elm.Line().right().length(0.55)
            elm.Arrow().right().length(0.35).label(f"$B_{k + 1}$", loc="right", ofst=0.05)
            cp = elm.Capacitor().down().at(pn.center).length(1.15).label("$C_{pulse}$", loc="bottom", ofst=0.08)
            ps = elm.SourceSquare().down().at(cp.end).length(1.1)
            elm.Ground().at(ps.end)
            if k == 0:  # pad ESD diodes on the hold node: ruled out
                elm.Line().left().at(node.center).length(1.5).color(SLOT[7])
                dd = elm.Diode().down().reverse().length(1.15).color(SLOT[7])
                elm.Ground().at(dd.end).color(SLOT[7])
                cx, cy = dd.center
                elm.Line().at((cx - 0.45, cy - 0.45)).to((cx + 0.45, cy + 0.45)).color(SLOT[7]).linewidth(1.5)
                elm.Line().at((cx - 0.45, cy + 0.45)).to((cx + 0.45, cy - 0.45)).color(SLOT[7]).linewidth(1.5)
                elm.Label().at((cx - 0.8, cy)).label("pad\nESD", loc="left", color=SLOT[7])
            elm.Label().at(((node.center[0] + pn.center[0]) / 2, node.center[1] + 0.3)).label(
                "hold", halign="center", color=INK2)
        elm.Label().at((ps.center[0] + 0.75, ps.center[1])).label("CZ\npulse", loc="right", color=INK2)
    img = mpimg.imread(io.BytesIO(d.get_imagedata("png")), format="png")
    ax.imshow(img)
    ax.axis("off")


def fig1():
    fig = plt.figure(figsize=(W, 6.6))
    a = fig.add_axes([0.0, 0.47, 1.0, 0.50])
    schematic(a)
    a.set_title("(a)", loc="left", pad=2)

    # (b) timing of one electrode: refresh, pedestal, droop, pulse, neighbour glitch (illustrative)
    b = fig.add_axes([0.08, 0.05, 0.90, 0.36])
    t = np.linspace(0, 10, 2000)
    v = np.zeros_like(t)
    seg = t >= 1.0
    v[seg] = 1.0 - 0.18                                                     # target minus pedestal
    v[seg] -= 0.03 * (t[seg] - 1.0)                                         # droop
    gate = (t > 5.0) & (t < 7.0)
    v[gate] += 1.6 * 0.5 * (1 - np.cos(2 * np.pi * (t[gate] - 5.0) / 2.0))  # capacitive CZ pulse
    v += 0.25 * np.exp(-(t - 6.0) / 0.1) * (t >= 6.0)                        # mid-gate neighbour refresh
    v[t >= 9.0] = 1.0 - 0.18                                                  # next refresh
    b.plot(t, v, color=SLOT[0], lw=1.8)
    b.axhline(1.0, color=INK2, lw=0.8, ls="--")
    b.text(1.3, 1.05, "DAC target", fontsize=9, color=INK2)
    kw = dict(fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.7, color=INK2))
    b.annotate("pedestal\n(charge injection,\nfeedthrough)", (1.12, 0.84), (1.5, 0.12), **kw)
    b.annotate("droop (leakage)", (3.6, 0.74), (2.9, 1.45), **kw)
    b.annotate("CZ pulse via $C_{pulse}$", (5.45, 1.6), (2.3, 2.45), **kw)
    b.annotate("glitch from the refresh\nof a neighbouring electrode", (6.05, 2.62), (7.1, 2.25), **kw)
    b.axvspan(0.2, 1.0, color=GRID, lw=0)
    b.axvspan(9.0, 9.8, color=GRID, lw=0)
    b.text(0.6, 2.75, "refresh", fontsize=9, color=INK2, ha="center")
    b.text(9.4, 2.75, "refresh", fontsize=9, color=INK2, ha="center")
    b.text(5.0, 2.75, "hold", fontsize=9, color=INK2, ha="center")
    b.set(xlabel="time (not to scale)", ylabel="barrier voltage (a.u.)", xticks=[], yticks=[], ylim=(0, 3.0),
          xlim=(0, 10))
    b.grid(False)
    b.set_title("(b)", loc="left")
    save(fig, "fig1_architecture")


# ============================================================================ Fig. 2: error budget

def budget_curves(recompute=False):
    if CACHE.exists() and not recompute:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    print("  computing the error-budget curves (cached afterwards)")
    out = {"dv": list(np.geomspace(1e-5, 2e-2, 50)), "static": {}, "tau": list(np.geomspace(0.3e-9, 1e-6, 14)),
           "glitch_start": {}, "glitch_mid": {}}
    for s in (3.87, 10.0, 33.69):
        lay = B.layer(s_dec_per_v=s)
        out["static"][str(s)] = [lay.excess_infidelity(B.static(lay, d)) for d in out["dv"]]
        for key, t0 in (("glitch_start", 0.0), ("glitch_mid", 25e-9)):
            out[key][str(s)] = [min(B.max_glitch(lay, 1e-3, tau, t0, +1), B.max_glitch(lay, 1e-3, tau, t0, -1))
                                for tau in out["tau"]]
    lay = B.layer(s_dec_per_v=10.0, stark_q2=0.0)
    out["static"]["10, no Stark"] = [lay.excess_infidelity(B.static(lay, d)) for d in out["dv"]]
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(out), encoding="utf-8")
    return out


def fig2(recompute=False):
    cur = budget_curves(recompute)
    spec = load("results/error_budget.json")
    fig, a, b, c = two_by_two(6.4)
    dv = np.array(cur["dv"]) * 1e3
    for s, col in SLOPE_RAMP.items():
        a.loglog(dv, cur["static"][str(s)], color=col, label=f"$s$ = {s:g} dec/V")
    a.loglog(dv, cur["static"]["10, no Stark"], color=SLOPE_RAMP[10.0], ls=":", label="$s$ = 10, no Stark")
    limit(a, 1e-3, "99.9%")
    limit(a, 1e-4, "99.99%", ls="--")
    a.set(xlabel="residual static offset (mV)", ylabel="added infidelity $1-F$", ylim=(1e-7, 1), title="(a)")
    a.legend(loc="lower right")

    for target, ls, mk in ((1e-3, "-", "o"), (1e-4, "--", "s")):
        for model, col in (("J only", INK2), ("J + Stark", SLOT[0])):
            rr = [r for r in spec["main"] if r["target"] == target and r["model"] == model]
            lab = f"{'exchange only' if model == 'J only' else 'with Stark'}, {(1 - target) * 100:g}%"
            b.loglog([r["s_dec_per_v"] for r in rr], [r["static_v"] * 1e3 for r in rr], ls, color=col, marker=mk,
                     label=lab)
    b.set(xlabel="exchange slope $s$ (dec/V)", ylabel="largest residual offset (mV)", title="(b)")
    b.set_xticks([4, 10, 30], ["4", "10", "30"])
    b.set_yticks([0.2, 0.5, 1, 2, 5], ["0.2", "0.5", "1", "2", "5"])
    b.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    b.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    b.set_ylim(0.07, 7)
    b.legend(loc="lower left")

    tau = np.array(cur["tau"]) * 1e9
    for s, col in SLOPE_RAMP.items():
        c.loglog(tau, np.array(cur["glitch_start"][str(s)]) * 1e3, color=col, label=f"$s$ = {s:g}, start of gate")
        c.loglog(tau, np.array(cur["glitch_mid"][str(s)]) * 1e3, color=col, ls="--", label=f"$s$ = {s:g}, mid-gate")
    c.set(xlabel="glitch decay time $\\tau$ (ns)", ylabel="largest glitch amplitude (mV)", title="(c)")
    c.legend(loc="upper right", ncol=2)
    save(fig, "fig2_error_budget")


# ============================================================================ Fig. 3: switch architectures

def fig3():
    res = load("results/cells.json")
    keys = ["NSW", "TG", "TGD", "BOOT", "CLK", "TSW", "TSWB"]
    fig, a, b, c = two_by_two(6.6)
    for k in keys:
        n, col, mk = ARCH[k]
        p = res["archs"][k]["nominal"]["pedestal_mv"]
        v = np.linspace(0.3, 0.9 if k == "NSW" else 1.5, len(p))
        a.plot(v, p, color=col, marker=mk, label=n)
    a.axhline(0, color=INK2, lw=0.6)
    a.set(xlabel="held voltage (V)", ylabel="pedestal (mV)", title="(a)")

    for k in keys:
        n, col, mk = ARCH[k]
        rows = [r for r in res["archs"][k]["sweeps"]["c_node"] if "error" not in r]
        b.loglog([r["summary"]["c_eff"] * 1e12 for r in rows],
                 [max(r["summary"]["pedestal_linear_residual"], 1e-9) * 1e6 for r in rows], color=col, marker=mk)
    limit(b, res["spec"]["s33.69_t0.001"]["static"] * 1e6, "budget, 99.9%", where=0.55)
    limit(b, res["spec"]["s33.69_t0.0001"]["static"] * 1e6, "budget, 99.99%", ls="--", where=0.55)
    b.set(xlabel="node capacitance (pF)", ylabel="pedestal after calibration (µV)", title="(b)")

    for k in keys:
        n, col, mk = ARCH[k]
        rows = [r for r in res["archs"][k]["sweeps"]["esd_area"] if "error" not in r]
        c.loglog([max(r["config"]["esd_area"], 1) for r in rows], [r["summary"]["droop_max"] for r in rows],
                 color=col, marker=mk)
    c.set_xticks([1, 10, 100, 1000], ["none", "10", "100", "1000"])
    c.set(xlabel="area of each ESD diode (µm²)", ylabel="worst-case droop (V/s)", title="(c)")
    h, lab = a.get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.91), columnspacing=1.2)
    fig.subplots_adjust(top=0.87)
    save(fig, "fig3_switch_architectures")


# ============================================================================ Fig. 4: co-simulation, Pareto

def _design_space_report():
    spec = importlib.util.spec_from_file_location("design_space_report", ROOT / "studies" / "design_space_report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fig4():
    res = load("results/design_space.json")
    R = _design_space_report()
    grid = R.ok(res["grid"])
    ota = [r["energy"]["p_static"] for r in grid if r["config"]["arch"] == "TSWO" and abs(r["config"]["i_buf"] - 1e-9) < 1e-12]
    R.BUF_POWER["value"] = float(np.median(ota)) if ota else 0.0
    fig, a, b, c = two_by_two(6.6)

    show = {"TG, ESD on the node": ("TG, pad ESD", SLOT[1], "--"), "TG, no ESD": ("TG, no ESD", SLOT[1], "-"),
            "bootstrapped (transistor level), 0.3 V underdrive, no ESD": ("bootstrapped NMOS", SLOT[3], "-"),
            "T-switch + OTA buffer, no ESD": ("T-switch + OTA", SLOT[6], "-")}
    for d in res["cosim"]:
        if "error" in d or d["slope"] != 10 or d["name"] not in show:
            continue
        n, col, ls = show[d["name"]]
        p = d["points"][0]
        a.plot(np.array(d["t_trace"]) * 1e9, (np.array(p["dv_trace"]) - p["static"]) * 1e3, color=col, ls=ls,
               lw=1.4, label=n)
    a.set(xlabel="time during the CZ gate (ns)", ylabel="barrier error (mV)", title="(a)", ylim=(-0.08, 1.75))
    a.legend(loc="upper right")

    for k, mk, col, lab in (("independent", "x", INK2, "add infidelities"), ("coherent", "+", SLOT[1], "add voltages"),
                            ("phase_additive", "o", SLOT[0], "add phases")):
        xs, ys = [], []
        for d in res["cosim"]:
            if "error" in d:
                continue
            for p in d["points"]:
                for cc in p["composition"]:
                    if f"f_{k}" in cc:
                        xs.append(cc["f_real"])
                        ys.append(cc[f"f_{k}"])
        b.loglog(xs, ys, mk, color=col, ms=4, mfc="none" if mk == "o" else None, mew=0.8, label=lab)
    lim = [1e-6, 1e-2]
    b.plot(lim, lim, color=INK, lw=0.7)
    b.set(xlim=lim, ylim=lim, xlabel="exact infidelity", ylabel="infidelity from the rule", title="(b)")
    b.legend(loc="lower right")

    for arch in ("NSW", "TG", "TGD", "BOOTT", "TSW", "TSWO"):
        n, col, mk = ARCH[arch]
        rows = [r for r in grid if r["config"]["arch"] == arch and np.isfinite(R.power(r)) and R.power(r) > 0]
        c.scatter([r["area"]["total"] for r in rows], [R.power(r) for r in rows], s=14, color=col, marker=mk,
                  alpha=0.55, lw=0, label=n)
    pts = [r for r in grid if np.isfinite(R.power(r)) and R.power(r) > 0]
    front = R.pareto(pts, lambda r: r["area"]["total"], R.power, True)
    c.step([r["area"]["total"] for r in front], [R.power(r) for r in front], color=INK, where="post", lw=1.4,
           label="Pareto front")
    c.set(xscale="log", yscale="log", xlabel="area per electrode (µm²)", ylabel="power per electrode (W)",
          title="(c)")
    c.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), markerscale=1.6, handletextpad=0.3)
    save(fig, "fig4_cosim_pareto")


# ============================================================================ Fig. 5: electrodes per DAC

MET2_FLAT = C.LineConfig(r_wire_per=5.5, c_wire_per=2.2e-15)


def met2_tree(cell):
    return C.LineConfig(c_line_fixed=10e-12 + 1000 * cell["c_line_cell"], r_wire_per=5.5, c_wire_per=2.2e-15)


def fig5():
    res = load("results/cryogenic.json")
    e = load("results/design_space.json")
    ts = load("results/tree.json")       # tree with its upper levels
    sb = load("results/system.json")             # operational budget (studies/operational_budget.py)
    rates = np.geomspace(1e-8, 1e1, 60)
    fig = plt.figure(figsize=(W, 8.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.25, 1], hspace=0.62)
    a, b = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    an = load("results/droop_anchors.json")            # measured droop converted to a 1 pF node
    lo, hi = min(an["band_1pF"].values()), max(an["band_1pF"].values())
    a.axvspan(lo, hi, color=GRID, alpha=0.6, lw=0)
    a.text(np.sqrt(lo * hi), 2.5e9, "measured droop, on 1 pF", ha="center", fontsize=8.5, color=INK2)
    for x in (an["band_1pF"]["van Staveren et al., typical"], an["band_1pF"]["Darnas et al."]):
        a.axvline(x, color=INK2, lw=0.7, ls=(0, (2, 2)))
    for d, esd in (("bootstrapped (transistor level), 0.3 V underdrive", False), ("T-switch + OTA buffer", False),
                   ("TG, no ESD", False), ("TG, ESD on the node", True)):
        n, col, mk = ARCH[DESIGN[d]]
        if esd:
            n += ", pad ESD"
        flat = np.interp(np.log(rates), np.log(sb["fig5_rates"]), sb["fig5_flat"][d])
        tree = np.interp(np.log(rates), np.log(sb["fig5_rates"]), sb["fig5_curves"][d])
        a.loglog(rates, np.maximum(flat, 0.5), color=col, ls="--" if esd else "-", label=f"{n}, flat line")
        cap = sb["n_per_reticle"]                  # beyond one reticle the count is a settling limit only
        a.loglog(rates, np.where(tree <= cap, np.maximum(tree, 0.5), np.nan), color=col,
                 ls=(0, (1, 1, 4, 1)) if esd else ":", marker=mk, markevery=8, ms=4.5, label=f"{n}, tree")
        a.loglog(rates, np.where(tree >= cap, tree, np.nan), color=col, lw=0.8, alpha=0.35,
                 ls=(0, (1, 1, 4, 1)) if esd else ":")
    for txt, v, ls in (("Darnas et al., drift only", 1e7, "-."), ("van Staveren et al., per DAC", 1e4, (0, (1, 2))),
                       ("one reticle of 1 pF cells", ts["n_per_reticle"], (0, (5, 2)))):
        a.axhline(v, color=INK, lw=0.8, ls=ls)
        a.text(1.3e-8, v * 1.6, txt, fontsize=8.5, color=INK2)
    a.set(xlabel="droop rate (V/s)", ylabel="electrodes per DAC", ylim=(1, 1e10), title="(a)")
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, columnspacing=1.5)

    grid = [r for r in e["grid"] if "error" not in r and "metrics" in r]
    for arch in ("NSW", "TG", "TGD", "BOOTT", "TSW", "TSWO"):
        n, col, mk = ARCH[arch]
        rows = [r for r in grid if r["config"]["arch"] == arch and r["metrics"][REF]["n_tree"] > 0]
        fom = [r["summary"]["leakage_max"] * r["cell"]["tau_node"] / r["summary"]["c_eff"] for r in rows]
        b.loglog(fom, [r["metrics"][REF]["n_tree"] for r in rows], mk, color=col, ms=4, alpha=0.6, mew=0, label=n)
    f = np.geomspace(1e-13, 1e-5, 20)
    bd = 2 * (e["spec"][REF] * 0.9)
    b.loglog(f, bd / (f * np.log(bd / (0.1 * e["spec"][REF]) + 1)), color=INK, ls="--", lw=1.0,
             label="settling limit, Eq. (5)")
    b.set(xlabel="switch figure of merit $I_{leak} \\cdot R_{on}$ (V)", ylabel="electrodes, final line only",
          title="(b)")
    b.legend(loc="lower left", ncol=2, columnspacing=1.0, handletextpad=0.3, markerscale=1.3)
    save(fig, "fig5_electrodes_per_dac")


# ============================================================================ Fig. 6: temperature bands

def fig6():
    res = load("results/cryogenic.json")
    sw = [r for r in res["switching"] if r and "error" not in r]
    designs = [d for d in res["designs"] if d != "bootstrapped, 0.3 V underdrive"]   # ideal drive: Figs. 3-4 only
    bands = list(res["bands"])
    band_style = dict(zip(bands, ["o", "s", "^", "v", "D", "P"]))
    band_col = dict(zip(bands, ["#86b6ef", "#5598e7", "#2a78d6", "#104281", SLOT[1], SLOT[7]]))
    labels = {d: ARCH[DESIGN[d]][0] + (", pad ESD" if "ESD on the node" in d else "") for d in designs}

    def get(d, b, c="tt"):
        return next((r for r in sw if r["design"] == d and r["band"] == b and r["corner"] == c), None)

    fig = plt.figure(figsize=(W, 7.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1], width_ratios=[1.35, 1], hspace=0.55, wspace=0.12)
    a = fig.add_subplot(gs[0, :])
    b, c = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
    ra = load("results/cell_margins.json")               # worst of 10^6 channels, one cell per channel
    tail = load("results/tail_corrected.json")["designs"]     # the same margins corrected for the tail optimism
    b_eq = ra["budgets"][WORST]["b_eq"]                 # untracked, equal signs: the nominal cell's residual is common
    trees = ["4 K, tree, ESD-dominated droop", "4 K, tree, one reticle"]
    bands6 = bands + ["4 K, steep (T_eff 120 K)"] + trees
    style6 = {**band_style, "4 K, steep (T_eff 120 K)": "X", trees[0]: "*", trees[1]: "h"}
    col6 = {**band_col, "4 K, steep (T_eff 120 K)": SLOT[5], trees[0]: SLOT[6], trees[1]: SLOT[4]}
    y = np.arange(len(designs))[::-1]
    for d, yy in zip(designs, y):                     # nominal cell over the bands, for comparison
        nom = [b_eq / max(get(d, bnd)["residual"], 1e-12) for bnd in bands if get(d, bnd)]
        a.plot([min(nom), max(nom)], [yy - 0.45, yy - 0.45], color=INK2, lw=1.6, alpha=0.6,
               label="nominal cell, over the bands" if yy == y[0] else None)
        sh = [tail[f"{d}|{bnd}"]["margin"][f"{WORST}|shared|mixed"] for bnd in bands + ["4 K, steep (T_eff 120 K)"] + trees
              if f"{d}|{bnd}" in tail]                # one calibration line shared by all channels
        a.plot([min(sh), max(sh)], [yy + 0.45, yy + 0.45], color=SLOT[3], lw=1.6, alpha=0.8,
               label="shared calibration, over the bands" if yy == y[0] else None)
    for j, bnd in enumerate(bands6):
        xs, lo, hi = [], [], []
        for d in designs:
            r = tail.get(f"{d}|{bnd}")
            if r is None:
                xs.append(np.nan); lo.append(0); hi.append(0)
                continue
            key = f"{WORST}|full|mixed"
            m, ci = r["margin"][key], r["ci90"][key]
            xs.append(m); lo.append(m - ci[0]); hi.append(ci[1] - m)
        yy = y + (j - (len(bands6) - 1) / 2) * 0.085
        a.errorbar(xs, yy, xerr=[lo, hi], fmt="none", ecolor=col6[bnd], elinewidth=0.8, alpha=0.7, zorder=2)
        a.scatter(xs, yy, marker=style6[bnd], color=col6[bnd], s=28, lw=0, label=BAND_NAME[bnd], zorder=3)
    a.axvline(1, color=SLOT[7], lw=1.0)
    a.set_xscale("log")
    a.set_yticks(y, [labels[d] for d in designs])
    a.set(xlabel="pedestal margin, worst of $10^6$ channels ($s$ = 33.7 dec/V, 99.99%, untracked)", title="(a)",
          xlim=(0.2, 400))
    a.legend(loc="upper left", bbox_to_anchor=(1.01, 1.02), handletextpad=0.3)

    vs = get(designs[0], "300 K")["v_hold"]
    extra = {}
    for line in (ROOT / "results" / "extra_bands_channels.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["seed"] == 0 and "pedestal" in r:
            extra[(r["design"], r["variant"])] = r
    bands_b = bands + ["4 K, steep (T_eff 120 K)", "4 K, steep (T_eff 30 K)", "4 K, steep (T_eff 20 K)"] + trees
    img = np.full((len(designs), len(bands_b)), np.nan)
    for i, d in enumerate(designs):
        for j, bnd in enumerate(bands_b):
            r = get(d, bnd) if bnd in bands else extra.get((d, bnd))
            if r:
                img[i, j] = sum(abs(e) >= 0.1e-3 for e in r["track_error"])
    b.imshow(img, cmap="Blues", vmin=0, vmax=len(vs), aspect="auto")
    for i in range(len(designs)):
        for j in range(len(bands_b)):
            b.text(j, i, "–" if np.isnan(img[i, j]) else f"{img[i, j]:.0f}", ha="center", va="center", fontsize=9,
                   color="white" if img[i, j] > len(vs) / 2 else INK)
    b.set_xticks(range(len(bands_b)), [BAND_NAME[x] for x in bands_b], rotation=40, ha="right")
    b.set_yticks(range(len(designs)), [labels[d] for d in designs])
    b.grid(False)
    b.set_title(f"(b) held voltages not passed (of {len(vs)})", loc="left")

    es = [x for x in res["esd_pulse"] if x and "error" not in x]
    xx = np.arange(len(es))
    c.bar(xx - 0.2, [max(x["f_dyn"]) for x in es], 0.38, color=SLOT[0], label="amplitude per electrode")
    c.bar(xx + 0.2, [max(x["f_dyn_global_k"]) for x in es], 0.38, color=SLOT[1], label="shared amplitude")
    c.axhline(1e-3, color=INK2, lw=0.8)               # 99.9% (solid) and 99.99% (dashed), named in the caption
    c.axhline(1e-4, color=INK2, lw=0.8, ls="--")
    c.set_yscale("log")
    c.set_xticks(xx, [f"{x['temp_c']:g} °C".replace("-", "−") for x in es])
    c.set(ylabel="infidelity from pulse distortion", title="(c)", ylim=(5e-5, 5e-2))
    c.yaxis.set_label_position("right")
    c.yaxis.tick_right()
    c.spines["left"].set_visible(False)
    c.spines["right"].set_visible(True)
    c.legend(loc="upper left")
    save(fig, "fig6_temperature")


# ============================================================================ Supplementary figures

def fig7():
    """Supplementary Fig. S1: benchmark against Polat et al."""
    p = load("results/benchmark_polat.json")
    rows = p["fig2_curve"]
    t = np.array([r["t_gate_ns"] for r in rows])
    ours = np.array([r["ours"] for r in rows])
    pol = np.array([r["polat"] for r in rows])
    fig, ax = plt.subplots(2, 1, figsize=(W, 5.0), sharex=True, gridspec_kw={"height_ratios": [2.2, 1], "hspace": 0.25})
    ax[0].semilogy(t, pol, color=INK2, lw=3.2, alpha=0.45, label="Polat et al., Figure 2")
    ax[0].semilogy(t, ours, color=SLOT[0], lw=1.2, label="this work")
    ax[0].set(ylabel="CZ infidelity", title="(a)")
    ax[0].legend(loc="upper right")
    ax[1].plot(t, (ours / pol - 1) * 100, color=SLOT[0], lw=1.2)
    ax[1].set(xlabel="gate time (ns)", ylabel="deviation (%)", title="(b)")
    chk = p["checks"]["fig2_simulated_curve"]
    ax[1].text(0.98, 0.92, f"median {chk['median_rel_dev'] * 100:.2f}%, maximum {chk['max_rel_dev'] * 100:.2f}%",
               transform=ax[1].transAxes, ha="right", va="top", fontsize=8.5, color=INK2)
    save(fig, "fig7_benchmark_polat")


def figS2():
    """Supplementary Fig. S2: switching models against the 77 K SkyWater data of Beall et al."""
    data = load("results/beall_check.json")
    fig = plt.figure(figsize=(W, 6.2))
    gs = fig.add_gridspec(2, 2, hspace=0.45, wspace=0.32)
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0])]
    title = {"nMOS L 0.15 W 1.6": "(a) NMOS, L = 0.15 µm", "nMOS L 1 W 1.6": "(b) NMOS, L = 1 µm",
             "pMOS L 0.35 W 1.6": "(c) PMOS, L = 0.35 µm"}
    for ax, (name, r) in zip(axes, data.items()):
        cv = r["curves"]
        for k, st, col, lab in (("pdk300", "-", INK2, "process models, 300 K"),
                                ("beall77", "--", SLOT[1], "Beall et al., models, 77 K"),
                                ("proxy_best", ":", SLOT[0], "fitted to the 77 K models"),
                                ("proxy_band77", "-.", SLOT[2], "77 K band")):
            ax.semilogy(cv[k][0], np.maximum(cv[k][1], 1e-13), st, color=col, label=lab)
        ax.semilogy(cv["measured77"][0], np.maximum(cv["measured77"][1], 1e-13), "o", color=INK, ms=3,
                    label="Beall et al., measured, 77 K")
        ax.set(xlabel="gate voltage magnitude (V)", ylabel="drain current (A)", ylim=(1e-12, None),
               title=title.get(name, name))
    h, lab = axes[0].get_legend_handles_labels()
    leg = fig.add_subplot(gs[1, 1])
    leg.axis("off")
    leg.legend(h, lab, loc="center")
    save(fig, "figS2_beall_check")


FIGS = {"fig1": fig1, "fig2": fig2, "fig3": fig3, "fig4": fig4, "fig5": fig5, "fig6": fig6, "fig7": fig7,
        "figS2": figS2}

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    recompute = "--recompute" in sys.argv
    for name in args or FIGS:
        if name == "fig2":
            fig2(recompute)
        else:
            FIGS[name]()
