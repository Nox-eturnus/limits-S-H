"""Circuit-to-fidelity co-simulation of multiplexed S/H gate drivers.

flow/holdstage.py characterises one S/H cell at a time and judges each error term on its own against
the error budget. This module puts the cells where they will be used and feeds the resulting node
waveform, not idealised errors, through the CZ model.

**Multiplexed deck** (`mux_deck`). One DAC line (source resistance r_src) serves K explicit cells; the
other N - K switches on the line are lumped into c_line. Every cell is used in charge-locked mode: its
node capacitance C_node is split into C_pulse = f_pulse * C_node to a pulse driver drv<k> (Pauka 2021,
Bartee 2025) and the rest to ground. The schedule:

    round 1   each cell is sampled to its target minus the droop budget b0 (it then sits where a
              drooped node would sit just before its refresh)
    round 2   each cell is refreshed to its target: a steady-state refresh, settling from b0
    gate      the CZ pulse is applied to cell 0 through C_pulse, pre-distorted for the exponential
              J(V) (Xue 2022) with the coupling k calibrated once at a reference bias; during the
              gate, cell 1 is refreshed again, so the DAC line swings at mid-gate (crosstalk)

Per slot the DAC first moves the line (t_line), then the cell's switch closes for t_close. The DAC
code is pre-compensated with a per-cell linear pedestal calibration, measured on a single cell
(holdstage.measure), as a real controller would learn it.

**What the waveform contains** that the single-cell terms do not: the pedestal after a real refresh on a
loaded line (charge sharing with the line, incomplete settling), the coupling error of the capacitive
pulse when the node's junction capacitance depends on the held voltage (ESD diodes), the pulse
feeding back through the off switch, and crosstalk from the line swinging during the gate. Droop over
the hold time is added from the leakage measurement (seconds cannot be simulated at ps resolution;
`long_hold_check` validates the extrapolation).

**Cell parameters for scaling** (`cell_params`): node settling time constant on refresh, off-switch
capacitance seen from the DAC line, clock charge per refresh, buffer supply current. With these the
slot time and the number of electrodes per line follow from `slot_time` and `n_max`.
"""
from dataclasses import dataclass, replace

import numpy as np

from . import holdstage as H
from . import spice
from .budget import TWO_PI  # noqa: F401  (re-exported for scripts)

T_EDGE_LINE = 1e-9          # DAC line step edge
V_LINE_SWING = 1.2          # worst-case line swing between neighbours (0.3-1.5 V)
F_PULSE = 0.5               # C_pulse / C_node (k ~ 0.5)
C_ELECTRODE = 50e-15        # gate electrode + interconnect (van Staveren 2025: ~50 fF per gate)
MIM_DENSITY = 2e-15         # F/um^2, SKY130 MIM (cap_mim_m3_1, camimc = 2 fF/um^2)


# ==================================================================================== clocks

def _multi_clock(name, off, on, windows, te):
    """PWL source `name`: level `off`, at `on` during each (t_start, t_end) window, edges te."""
    pts = [(0.0, off)]
    for a, b in windows:
        pts += [(a, off), (a + te, on), (b, on), (b + te, off)]
    return f"V{name} {name} 0 PWL(" + " ".join(f"{t:.6e} {v:.4f}" for t, v in pts) + ")"


def _clocks(cfg, k, windows):
    """All clock nets of cell k (suffix _k), on during `windows` (series switches closed)."""
    te, ud = cfg.t_edge, cfg.v_underdrive
    d = te + H.T_NOV
    shunt = [(a - d, b + d) for a, b in windows]          # break-before-make (T-switch shunt / buffer)
    ck = f"_{k}"
    return [_multi_clock("en" + ck, -ud, cfg.vdd, windows, te),
            _multi_clock("enb" + ck, cfg.vdd + ud, 0.0, windows, te),
            _multi_clock("enh" + ck, -ud, cfg.vddh, windows, te),
            _multi_clock("enhb" + ck, cfg.vddh, 0.0, shunt, te),
            _multi_clock("ensh" + ck, cfg.vdd, 0.0, shunt, te)]


def _node(cfg, k, hold, f_pulse):
    s = (f"CH{k} {hold} 0 {cfg.c_node * (1 - f_pulse):.6e}\n"
         f"CP{k} {hold} drv{k} {cfg.c_node * f_pulse:.6e}")
    if cfg.esd_area > 0:
        s += f"\nXESD{k} {hold} vdd 0 ESD a={cfg.esd_area:g} p={4 * np.sqrt(cfg.esd_area):g}"
    return s


def _pwl(times, values):
    pts = [f"{t:.6e} {v:.6e}" for t, v in zip(times, values)]
    lines = [" ".join(pts[i:i + 6]) for i in range(0, len(pts), 6)]
    return "PWL(" + "\n+ ".join(lines) + ")"


def _base_arch(cfg):
    """CLK is the TG with a pulse capacitor; here every cell has one, so CLK is simulated as TG."""
    return replace(cfg, arch="TG") if cfg.arch == "CLK" else cfg


# ==================================================================================== cell parameters

def cell_deck(cfg, v0=0.9, delta=10e-3):
    """One cell: track at v0 - delta, open, DAC to v0, close (settling), open; then line ramp, switch
    off (off capacitance seen from the line). Clock source currents are saved for the clock charge."""
    cfg = _base_arch(cfg)
    tau = H._r_on_estimate(cfg) * cfg.c_node
    settle = max(20e-9, 30 * tau)
    te = cfg.t_edge
    t1 = 2e-9
    t_open1 = t1 + settle
    t_dac = t_open1 + 2 * te + 2e-9
    t_close = t_dac + T_EDGE_LINE + 3e-9
    t_open2 = t_close + settle
    t_ramp0 = t_open2 + 2 * te + 5e-9
    t_ramp1 = t_ramp0 + 10e-9
    t_stop = t_ramp1 + 1e-9
    windows = [(t1, t_open1), (t_close, t_open2)]
    dac = _pwl([0, t_dac, t_dac + T_EDGE_LINE, t_ramp0, t_ramp1, t_stop],
               [v0 - delta, v0 - delta, v0, v0, v0 + 0.01, v0 + 0.01])
    lines = [H._header(cfg), f"VDD vdd 0 {cfg.vdd}", f"VDDH vddh 0 {cfg.vddh}", "VDRV0 drv0 0 0",
             f"VDAC dac 0 {dac}", f"RS dac line {cfg.r_src}"] + _clocks(cfg, 0, windows) + H.globals_(cfg)
    lines += [H._switch(cfg, 0, "line", "hold0", ck="_0"), _node(cfg, 0, "hold0", F_PULSE)]
    srcs = ["ven_0", "venb_0", "venh_0", "venhb_0", "vensh_0", "vdac", "vddh", "vdd"]
    srcs += (["vneg"] if cfg.arch == "BOOTT" else [])
    lines += [".save v(hold0) v(line) " + " ".join(f"i({s})" for s in srcs),
              f".tran {min(10e-12, te / 10):.3e} {t_stop:.6e}", ".end", ""]
    tl = dict(t1=t1, t_open1=t_open1, t_dac=t_dac, t_close=t_close, t_open2=t_open2,
              t_ramp0=t_ramp0, t_ramp1=t_ramp1, t_stop=t_stop)
    return "\n".join(lines), tl


def _integrate(t, y, a, b):
    m = (t >= a) & (t <= b)
    return float(np.trapezoid(y[m], t[m])) if m.sum() > 1 else 0.0


def cell_params(cfg, v0=0.9, delta=10e-3, workdir=None):
    """Settling time constant on refresh, off capacitance seen from the line, clock charge and energy
    per refresh, static supply current (buffer). Returns a dict."""
    cfg = _base_arch(cfg)
    deck, tl = cell_deck(cfg, v0, delta)
    w = spice.run_ngspice(deck, workdir or cfg.workdir, cfg.tag() + "_cell")
    t, v = w["time"], w["v(hold0)"]
    # settling: error to the final (closed) value, fitted as a single exponential over 30 % -> 0.3 %
    m = (t >= tl["t_close"]) & (t <= tl["t_open2"])
    tc, err = t[m] - tl["t_close"], v[m] - np.mean(v[m][-20:])
    a0 = np.max(np.abs(err))
    sel = (np.abs(err) < 0.3 * a0) & (np.abs(err) > 3e-3 * a0)
    idx = np.nonzero(sel)[0]
    if idx.size > 5:
        k0 = idx[0]
        k1 = k0 + np.argmax(np.abs(err[k0:]) < 3e-3 * a0) if np.any(np.abs(err[k0:]) < 3e-3 * a0) else idx[-1]
        p = np.polyfit(tc[k0:k1], np.log(np.abs(err[k0:k1]) + 1e-15), 1)
        tau = -1.0 / p[0]
    else:
        tau = np.nan
    # off capacitance seen from the line: extra DAC current during the 10 mV / 10 ns line ramp
    slope = 0.01 / (tl["t_ramp1"] - tl["t_ramp0"])
    i_dac = -w["i(vdac)"]
    i0 = np.interp(tl["t_ramp0"] - 0.5e-9, t, i_dac)
    i1 = np.interp(0.5 * (tl["t_ramp0"] + tl["t_ramp1"]), t, i_dac)
    c_line_cell = (i1 - i0) / slope
    # clock charge per refresh: charge drawn from each clock source on its turn-on and turn-off
    # edges of the second window, times its swing (what a CMOS clock driver takes from its supply)
    te = cfg.t_edge
    swings = {"ven_0": cfg.vdd + cfg.v_underdrive, "venb_0": cfg.vdd + cfg.v_underdrive,
              "venh_0": cfg.vddh + cfg.v_underdrive, "venhb_0": cfg.vddh, "vensh_0": cfg.vdd}
    used = {"NSW": ("ven_0",), "TG": ("ven_0", "venb_0"), "TGD": ("ven_0", "venb_0"),
            "TGH": ("ven_0", "venb_0"), "BOOT": ("ven_0",), "TSW": ("venh_0", "venhb_0"),
            "TSWB": ("venh_0", "venhb_0"), "TSWO": ("venh_0", "venhb_0"), "NTB": ("ven_0", "vensh_0"),
            "BOOTT": ("venh_0", "venhb_0")}
    e_clk = 0.0
    d = te + H.T_NOV + 0.5e-9
    for s in used[cfg.arch]:
        i = w[f"i({s})"]
        q_on = abs(_integrate(t, i, tl["t_close"] - d, tl["t_close"] + d + te))
        q_off = abs(_integrate(t, i, tl["t_open2"] - d, tl["t_open2"] + d + te))
        e_clk += 0.5 * (q_on + q_off) * swings[s]
    if cfg.arch == "BOOT":
        # behavioural bootstrap: gate charge ~ that of the NMOS; a real bootstrap capacitor is
        # recharged from VDD each cycle, assumed 2x the gate charge (capacitor + parasitics)
        e_clk *= 2.0
    if cfg.arch == "BOOTT":
        # transistor-level bootstrap: add the charge VDD supplies to recharge the bootstrap capacitor
        # and the charge the gate dumps into the underdrive rail, over one full cycle (measured)
        q_vdd = abs(_integrate(t, w["i(vdd)"], tl["t_close"] - d, tl["t_ramp0"] - 1e-9))
        q_neg = abs(_integrate(t, w["i(vneg)"], tl["t_close"] - d, tl["t_ramp0"] - 1e-9))
        e_clk += q_vdd * cfg.vdd + q_neg * cfg.v_underdrive
    # static supply current of the cell (TSWO: the OTA; the shared bias reference is excluded)
    i_static = -float(np.interp(tl["t_ramp0"] - 1e-9, t, w["i(vddh)"])) - (cfg.i_buf if cfg.arch == "TSWO" else 0.0)
    return dict(tau_node=float(tau), c_line_cell=float(c_line_cell), e_clk=float(e_clk),
                p_static=float(i_static * cfg.vddh) if cfg.arch == "TSWO" else 0.0,
                settle_amp=float(a0))


# ==================================================================================== area model

def _fet_area(w, l, thick=False):
    """Layout estimate (um^2): drawn device plus contacts and spacing; thick oxide needs wider rules."""
    return (w + 0.5) * (l + 2 * 0.29 + 0.5) * (2.5 if thick else 1.5)


def area_um2(cfg, f_pulse=F_PULSE):
    """Area per electrode (um^2): MIM for the hold and pulse capacitors (C_node minus the electrode's
    own ~50 fF, at least the pulse capacitor), switch devices, ESD pair, buffer or bootstrap."""
    a, wn, l = cfg.arch, cfg.wn, cfg.l
    c_mim = max(cfg.c_node - C_ELECTRODE, f_pulse * cfg.c_node)
    area = {"mim": c_mim / MIM_DENSITY, "esd": 2 * cfg.esd_area}
    if a == "NSW":
        sw = _fet_area(wn, l)
    elif a in ("TG", "CLK", "TGH"):
        sw = _fet_area(wn, l) + _fet_area(2 * wn, l) * 1.5          # PMOS in an n-well
    elif a == "TGD":
        sw = _fet_area(wn, l) + _fet_area(2 * wn, l) * 1.5 + _fet_area(max(wn / 2, .42), l) \
            + _fet_area(max(wn, .42), l) * 1.5
    elif a == "BOOT":
        sw = _fet_area(wn, l) + 4 * _fet_area(0.42, 0.15) + 10e-15 / MIM_DENSITY   # bootstrap cap 10 fF
    elif a == "BOOTT":
        # sky130_hold.lib BOOTT: main switch, 7 thick-oxide devices (two of them 2x), 50 fF MIM
        sw = _fet_area(wn, l) + 5 * _fet_area(0.42, 0.5, True) + 2 * _fet_area(0.84, 0.5, True)             + 50e-15 / MIM_DENSITY
    elif a in ("TSW", "TSWB", "TSWO"):
        sw = 3 * _fet_area(wn, 0.5, thick=True)
    elif a == "NTB":
        sw = 3 * _fet_area(wn, l)
    else:
        raise ValueError(a)
    area["switch"] = sw
    if a in ("TSWB", "TSWO", "NTB"):
        # the OTA5T of sky130_hold.lib (TSWB/NTB: same buffer assumed)
        area["buffer"] = (_fet_area(2, 2, True) * 3 + _fet_area(1, 4, True) * 2)
    area["total"] = sum(area.values())
    return area


# ==================================================================================== scaling model

@dataclass(frozen=True)
class LineConfig:
    r_src: float = 50.0             # DAC output resistance (ohm)
    c_wire: float = 10e-12          # line wiring capacitance (F)
    dv_line: float = V_LINE_SWING   # line swing between consecutive electrodes (worst case)
    t_overhead: float = 2e-9        # clock edges, non-overlap, decoder
    eps_frac: float = 0.1           # settling error allowed, as a fraction of the static spec
    c_line_fixed: float = None      # if set: hierarchical (tree) demux, line capacitance fixed
    # distributed wire: resistance and capacitance of the line per electrode it passes (one cell
    # pitch). 0 = a lumped line.
    r_wire_per: float = 0.0         # ohm per electrode pitch
    c_wire_per: float = 0.0         # F per electrode pitch


def slot_time(n, cell, spec, droop_budget, line=LineConfig()):
    """Time per refresh slot for n electrodes on one line: the line settles the swing to eps, then the
    node settles from the drooped value (droop_budget) to eps through the switch."""
    eps = line.eps_frac * spec
    n_seg = n
    c_line = line.c_wire + n * (cell["c_line_cell"] + line.c_wire_per)
    if line.c_line_fixed is not None:                 # a tree never loads the line more than a flat one
        c_fixed = line.c_line_fixed + 1000 * line.c_wire_per if line.c_wire_per else line.c_line_fixed
        if c_fixed < c_line:
            c_line, n_seg = c_fixed, min(n, 1000)
    # Elmore delay of a source resistance driving a uniformly distributed RC line: the wire's own
    # resistance counts half (validated against an RC ladder in tests/test_cosim.py)
    r_eff = line.r_src + 0.5 * n_seg * line.r_wire_per
    t_line = r_eff * c_line * np.log(max(line.dv_line / eps, 1.0))
    t_node = cell["tau_node"] * np.log(max(droop_budget / eps, 1.0) + 1.0)
    return line.t_overhead + t_line + t_node


def n_max(hold_time, cell, spec, droop_budget, line=LineConfig()):
    """Largest n with n * slot_time(n) <= hold_time (bisection on the monotone n * t_slot(n))."""
    if not np.isfinite(hold_time) or hold_time <= 0:
        return 0.0
    f = lambda n: n * slot_time(n, cell, spec, droop_budget, line) - hold_time  # noqa: E731
    lo, hi = 1.0, 1.0
    if f(lo) > 0:
        return 0.0
    while f(hi) <= 0 and hi < 1e15:
        hi *= 4
    for _ in range(200):
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if f(mid) <= 0 else (lo, mid)
        if hi / lo < 1 + 1e-6:
            break
    return lo


def hold_budget(spec, residual, eps_frac=0.1, centred=True, comp_residual=1.0):
    """Static budget left for droop, and the factor that turns it into a hold time.

    Deterministic offsets on one electrode add linearly (they are one barrier offset; validated by
    the co-simulation): |residual| + eps + droop excursion <= spec. Centring pre-offsets each sample
    by half the expected droop, so the excursion is half the droop; feed-forward compensation leaves
    a fraction comp_residual of it. Returns (droop budget in V of accumulated droop)."""
    left = spec * (1 - eps_frac) - abs(residual)
    if left <= 0:
        return 0.0
    return left * (2.0 if centred else 1.0) / comp_residual


# ==================================================================================== tree demultiplexer

@dataclass(frozen=True)
class TreeConfig:
    """Hierarchical demultiplexer with its upper levels modelled. The DAC drives the root
    line; each upper-level line carries `fanout` series switches, one per child region, and each leaf
    line carries `leaf` cells. Only the selected path conducts, so the siblings load every line with
    their off capacitance and the selected switch adds its on-resistance. Every line runs past its
    children at the side length of a child region (for the leaf: the cell pitch), the rule of the flat
    met2 line. LineConfig(c_line_fixed=...) is the leaf line alone, without the levels above it."""
    leaf: int = 1000                  # cells per leaf line
    fanout: float = None              # children per upper-level line; None = a single upper level
    r_src: float = 50.0
    c_root: float = 10e-12            # lumped capacitance at the DAC (LineConfig.c_wire)
    pitch: float = 22e-6              # cell pitch (m); one electrode per pitch^2 of area
    r_wire: float = 5.5 / 22e-6       # ohm/m, SKY130 met2, 0.5 um wide
    c_wire: float = 2.2e-15 / 22e-6   # F/m
    w_tree: float = 10.0              # tree switch = cell switch scaled in width by w_tree
    c_node: float = 1e-12             # R_on of the cell switch = tau_node / c_node
    c_gate_unit: float = 2e-15        # gate capacitance of a unit-width switch (control energy)
    v_ctrl: float = 2.1               # control swing: 1.8 V plus the 0.3 V underdrive
    v_supply: float = 1.8             # supply the DAC charges the line from
    dv_avg: float = 0.4               # mean |line swing| for targets uniform over 0.3-1.5 V
    dv_line: float = V_LINE_SWING
    t_overhead: float = 2e-9
    eps_frac: float = 0.1
    n_seg: int = 40                   # RC segments per line in the Elmore sum


def tree_levels(n, tree):
    """Lines on the path from the DAC to one electrode, root first: (children, child side (m), leaf?)."""
    a_cell = tree.pitch ** 2
    if n <= tree.leaf:
        return [(n, tree.pitch, True)]
    n_lines = n / tree.leaf
    if tree.fanout is None or n_lines <= tree.fanout:
        fan = [n_lines]
    else:
        depth = int(np.ceil(np.log(n_lines) / np.log(tree.fanout) - 1e-9))
        fan = [n_lines / tree.fanout ** (depth - 1)] + [tree.fanout] * (depth - 1)
    levels, below = [], n
    for f in fan:
        below = below / f                             # electrodes under one child of this line
        levels.append((f, np.sqrt(below * a_cell), False))
    return levels + [(tree.leaf, tree.pitch, True)]


def tree_path(n, cell, tree):
    """Elmore delay (s) from the DAC to the far end of the selected leaf line, the capacitance the
    DAC charges per refresh (F), and the control-wire capacitance toggled per refresh (F)."""
    r_on = cell["tau_node"] / tree.c_node
    r_up, tau = tree.r_src, tree.r_src * tree.c_root
    c_path, c_ctrl = tree.c_root, 0.0
    for k, (f, side, leaf) in enumerate(tree_levels(n, tree)):
        if k:                                          # the selected switch into this line
            r_up += r_on / tree.w_tree
        length = f * side
        c_sw = f * (cell["c_line_cell"] if leaf else tree.w_tree * cell["c_line_cell"])
        c_seg = (tree.c_wire * length + c_sw) / tree.n_seg
        r_seg = tree.r_wire * length / tree.n_seg
        m = tree.n_seg                                 # sum over segments i = 1..m of (r_up + i r_seg) c_seg
        tau += c_seg * (m * r_up + r_seg * m * (m + 1) / 2)
        r_up += m * r_seg
        c_path += c_seg * m
        # the selected switch's control wire runs along this line
        c_ctrl += tree.c_wire * length + tree.c_gate_unit * (1.0 if leaf else tree.w_tree)
    return tau, c_path, c_ctrl


def tree_slot_time(n, cell, spec, droop_budget, tree=TreeConfig()):
    """Slot time with the whole tree path: the path settles the swing to eps, then the node settles."""
    eps = tree.eps_frac * spec
    tau, _, _ = tree_path(n, cell, tree)
    t_line = tau * np.log(max(tree.dv_line / eps, 1.0))
    t_node = cell["tau_node"] * np.log(max(droop_budget / eps, 1.0) + 1.0)
    return tree.t_overhead + t_line + t_node


def tree_refresh_energy(n, cell, tree=TreeConfig()):
    """Energy per refresh (J): the DAC charging the path, the control wires of the selected switches,
    and the cell's own clock energy."""
    _, c_path, c_ctrl = tree_path(n, cell, tree)
    return c_path * tree.dv_avg * tree.v_supply + c_ctrl * tree.v_ctrl ** 2 + cell.get("e_clk", 0.0)


def n_max_tree(hold_time, cell, spec, droop_budget, tree=TreeConfig()):
    """Largest n with n * tree_slot_time(n) <= hold_time. Adding a level makes n * t_slot(n) step, so
    the largest feasible n is found on a fine logarithmic grid and then refined by bisection."""
    if not np.isfinite(hold_time) or hold_time <= 0:
        return 0.0
    f = lambda n: n * tree_slot_time(n, cell, spec, droop_budget, tree) - hold_time  # noqa: E731
    grid = np.geomspace(1.0, 1e15, 1501)
    okn = [n for n in grid if f(n) <= 0]
    if not okn:
        return 0.0
    lo = okn[-1]
    hi = lo * (grid[1] / grid[0])
    for _ in range(100):
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if f(mid) <= 0 else (lo, mid)
        if hi / lo < 1 + 1e-6:
            break
    return lo


# ==================================================================================== co-simulation

@dataclass(frozen=True)
class MuxConfig:
    k_cells: int = 4
    c_line: float = 10e-12           # lumped line capacitance (wire + the other N - K switches)
    f_pulse: float = F_PULSE
    droop_budget: float = 1.4e-3     # round-1 offset: the node starts each refresh this far off
    v_ref: float = 0.9               # bias at which the pulse coupling k is calibrated
    t_gap: float = 1e-6              # refresh-to-gate latency (the OTA buffer settles in ~0.3-1 us)
    margin: float = 1.5              # slot = margin x estimated settling


def _slot_parts(cfg, mux, cell, eps):
    tau_line = cfg.r_src * (mux.c_line + mux.k_cells * cell["c_line_cell"])
    t_line = mux.margin * tau_line * np.log(V_LINE_SWING / eps) + T_EDGE_LINE
    glitch = max(mux.droop_budget, 5e-3)       # node error at close: droop plus clock feedthrough
    t_close = mux.margin * cell["tau_node"] * np.log(glitch / eps) + 3 * cfg.t_edge + 2 * H.T_NOV
    return t_line, t_close


def mux_deck(cfg, mux, targets, dac_codes, cell, eps, drive=None, t_gate=50e-9):
    """Multiplexed line with K cells. targets/dac_codes: per cell. drive: (t, v) of cell 0's pulse
    driver relative to the gate start, or None. Returns (deck, timeline)."""
    cfg = _base_arch(cfg)
    K = mux.k_cells
    te = cfg.t_edge
    t_line, t_close = _slot_parts(cfg, mux, cell, eps)
    t_slot = t_line + t_close + 2 * te + 2 * H.T_NOV
    # round 1 (initial sampling, long), round 2 (refresh), then the gate with cell 1 refreshed again
    t_r1 = 2e-9
    slot1 = t_line + 3 * t_close + 2 * te + 2 * H.T_NOV
    win = {k: [] for k in range(K)}
    dac_t, dac_v = [0.0], [dac_codes[0] - mux.droop_budget]
    t = t_r1
    for rnd, sl in ((1, slot1), (2, t_slot)):
        for k in range(K):
            v = dac_codes[k] - (mux.droop_budget if rnd == 1 else 0.0)
            dac_t += [t, t + T_EDGE_LINE]
            dac_v += [dac_v[-1], v]
            a = t + t_line
            b = t + sl - te - 2 * H.T_NOV
            win[k].append((a, b))
            t += sl
    t_cz = t + mux.t_gap
    # cell 1's extra refresh: line swing to cell 1's code lands at mid-gate, switch closes after
    t_sw = t_cz + 0.5 * t_gate
    dac_t += [t_sw, t_sw + T_EDGE_LINE]
    dac_v += [dac_v[-1], dac_codes[1]]
    win[1].append((t_sw + t_line, t_sw + t_line + t_close))
    t_stop = max(t_cz + t_gate + 5e-9, t_sw + t_line + t_close + te + 2e-9)
    dac_t.append(t_stop)
    dac_v.append(dac_v[-1])
    lines = [H._header(cfg), f"VDD vdd 0 {cfg.vdd}", f"VDDH vddh 0 {cfg.vddh}",
             f"VDAC dac 0 {_pwl(dac_t, dac_v)}", f"RS dac line {cfg.r_src}",
             f"CLINE line 0 {mux.c_line:.6e}"] + H.globals_(cfg)
    for k in range(K):
        lines += _clocks(cfg, k, win[k])
        lines += [H._switch(cfg, k, "line", f"hold{k}", ck=f"_{k}"), _node(cfg, k, f"hold{k}", mux.f_pulse)]
        if k == 0 and drive is not None:
            dt_, dv_ = drive
            lines.append(f"VDRV0 drv0 0 {_pwl(np.concatenate([[0.0], t_cz + dt_]), np.concatenate([[0.0], dv_]))}")
        else:
            lines.append(f"VDRV{k} drv{k} 0 0")
    lines += [".save v(line) " + " ".join(f"v(hold{k})" for k in range(K)),
              f".tran {min(10e-12, te / 10):.3e} {t_stop:.6e}", ".end", ""]
    tl = dict(t_cz=t_cz, t_stop=t_stop, t_slot=t_slot, t_line=t_line, t_close=t_close,
              r2_open=[win[k][1][1] for k in range(K)], t_sw=t_sw)
    return "\n".join(lines), tl


def neighbours(cfg):
    """Fixed targets of cells 1..3. Cell 1 swings the line by ~1.2 V at mid-gate (0.6 V for the
    NMOS-only switches, which pass only 0.3-0.9 V)."""
    return [0.9, 0.3, 0.8, 0.4] if cfg.arch in ("NSW", "NTB") else [1.5, 0.3, 1.2, 0.6]


def dac_code(target, a, b):
    """DAC value whose sampled level, after an offset a + b * code, lands on target."""
    return (target - a) / (1.0 + b)


def _run(cfg, mux, targets, codes, cell, eps, drive, t_gate, name):
    deck, tl = mux_deck(cfg, mux, targets, codes, cell, eps, drive, t_gate)
    w = spice.run_ngspice(deck, cfg.workdir, cfg.tag() + name)
    t, v = w["time"], w["v(hold0)"]
    settled = float(np.mean(v[(t > tl["t_cz"] - 3e-9) & (t <= tl["t_cz"])]))
    return w, tl, settled


def insitu_calibration(cfg, mux, cell, eps, v_cal, step=0.05):
    """What a controller learns for each electrode, on the multiplexed line itself: the settled level
    against the DAC code (linear fit, the per-channel pedestal calibration of holdstage), and the pulse
    coupling k at each calibration bias (a small step on the pulse driver, as an amplitude
    calibration of the CZ at that operating point would find it).

    Calibrating in situ, after the node has settled, matters for the transistor-level buffer: its
    kickback through the input gate capacitance settles in ~0.3-1 us to an offset of 0.1-0.4 mV that a
    pedestal read 3 ns after opening (single-cell bench) misses."""
    cfg = _base_arch(cfg)
    neigh = neighbours(cfg)
    drive = (np.array([0.0, 1e-9, 20e-9]), np.array([0.0, step, step]))
    err, ks = [], []
    for v in v_cal:
        tg = [v] + neigh[1:mux.k_cells]
        w, tl, settled = _run(cfg, mux, tg, tg, cell, eps, drive, 20e-9, f"_cal{v:g}")
        t, x = w["time"], w["v(hold0)"]
        after = float(np.mean(x[(t > tl["t_cz"] + 14e-9) & (t <= tl["t_cz"] + 15e-9)]))
        err.append(settled - v)
        ks.append((after - settled) / step)
    b, a = np.polyfit(v_cal, err, 1)
    return dict(a=float(a), b=float(b), v_cal=list(map(float, v_cal)), err=list(map(float, err)),
                k=list(map(float, ks)), k_ref=float(np.interp(mux.v_ref, v_cal, ks)))


def cosim(cfg, layer, targets, mux=MuxConfig(), workdir=None, spec=1.37e-3, cell=None, cal=None):
    """Co-simulate cell 0 at each target (cells 1..3 at fixed neighbours), after in-situ calibration.

    The pulse drive is v0 / k_t with k_t the coupling calibrated at the target (per-electrode CZ
    amplitude calibration). Returns per target: the barrier error dv(t) on the layer grid (SPICE node
    voltage minus target minus the nominal pulse), its static part (settled level before the gate),
    the excess infidelity of the real waveform, and the extra pulse-amplitude error dv_k if a single
    coupling k_ref (calibrated at v_ref) served all biases instead."""
    cfg = _base_arch(replace(cfg, workdir=workdir or cfg.workdir))
    eps = 0.1 * spec
    cell = cell or cell_params(cfg)
    cal = cal or insitu_calibration(cfg, mux, cell, eps, targets)
    t_gate = layer.cfg.t_gate
    t_drv = np.linspace(0.0, t_gate, int(round(t_gate / 20e-12)) + 1)   # the drive is smooth
    v0_drv = np.interp(t_drv, layer.t[:layer.n_gate], layer.v0[:layer.n_gate], left=0.0, right=0.0)
    neigh = neighbours(cfg)
    out = []
    for vt in targets:
        k_t = float(np.interp(vt, cal["v_cal"], cal["k"]))
        drive = (np.concatenate([t_drv, [t_gate + 1e-9]]), np.concatenate([v0_drv / k_t, [0.0]]))
        tg = [vt] + neigh[1:mux.k_cells]
        codes = [dac_code(v, cal["a"], cal["b"]) for v in tg]
        w, tl, settled = _run(cfg, mux, tg, codes, cell, eps, drive, t_gate, f"_mux{vt:g}")
        t, v = w["time"], w["v(hold0)"]
        dv = np.interp(tl["t_cz"] + layer.t, t, v) - vt - layer.v0
        out.append(dict(target=vt, dv=dv, static=settled - vt, k_t=k_t, k_ref=cal["k_ref"],
                        dv_k=(k_t / cal["k_ref"] - 1.0) * layer.v0,
                        infidelity=float(layer.excess_infidelity(dv)),
                        timeline=tl, line=(t, w["v(line)"]), node=(t, v)))
    return out, cal, cell


def long_hold_check(cfg, t_hold=10e-3, v=0.9, v_line=0.0, workdir=None):
    """Validate the droop extrapolation: a transient that samples v, opens, moves the DAC line to
    v_line (it serves other electrodes) and holds for t_hold with a coarse time step, against the
    leakage measurement (droop = I / C at the held voltage, same line state).
    Returns (drift from the transient, drift predicted by the leakage deck), both in V."""
    cfg = _base_arch(replace(cfg, workdir=workdir or cfg.workdir, v_hold=(v,)))
    te = cfg.t_edge
    tau = H._r_on_estimate(cfg) * cfg.c_node
    t_open = 2e-9 + max(20e-9, 30 * tau)
    t_ref = t_open + 2 * te + 10e-9
    lines = [H._header(cfg, abstol=1e-16), f"VDD vdd 0 {cfg.vdd}", f"VDDH vddh 0 {cfg.vddh}", "VDRV0 drv0 0 0",
             f"VDAC dac 0 PWL(0 {v} {t_open + 2 * te + 1e-9:.6e} {v} {t_open + 2 * te + 2e-9:.6e} {v_line})",
             f"RS dac line {cfg.r_src}"] + _clocks(cfg, 0, [(2e-9, t_open)]) + H.globals_(cfg)
    lines += [H._switch(cfg, 0, "line", "hold0", ck="_0"), _node(cfg, 0, "hold0", F_PULSE),
              ".save v(hold0)", f".tran {t_hold / 2000:.3e} {t_ref + t_hold:.6e} 0 {t_hold / 200:.3e}", ".end", ""]
    w = spice.run_ngspice("\n".join(lines), cfg.workdir, cfg.tag() + "_longhold", timeout=1800)
    t, x = w["time"], w["v(hold0)"]
    drift = float(np.interp(t_ref + t_hold, t, x) - np.interp(t_ref, t, x))
    m = H.measure(cfg)
    predicted = float(m["droop"][0 if v_line == 0.0 else 1, 0]) * t_hold     # rows: line at 0, at VDD
    return drift, predicted
