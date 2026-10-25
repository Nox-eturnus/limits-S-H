"""Transistor-level sample-and-hold stages on SKY130, measured against the error budget.

One transient deck per configuration holds N independent S/H instances, one per held voltage, all
driven by the same clocks. Timeline (en = switch control):

    0 .. t1            switch open, node starts at 0
    t1 .. t_open       track (switch closed) long enough to settle (30 R_on C)
    t_open             switch opens  ->  pedestal (turn-off injection + feedthrough)
    t_line             DAC line steps by +dv_line for 10 ns and back  ->  feedthrough with switch off
    t_reclose          switch closes again (refresh)  ->  refresh transient on the node
    t_reopen           switch opens again  ->  second pedestal (repeatability)

A second deck forces each hold node with a voltage source, switch off, DAC line at 0 or VDD, and
reads the source current: the node leakage, switch plus ESD, from which droop = I / C.

Architectures:
    NSW   single NMOS (thin oxide)
    TG    CMOS transmission gate
    TGD   TG with half-size dummy switches (charge-injection compensation)
    BOOT  NMOS with a bootstrapped gate drive (behavioural: V_gate = V_src + VDD while on, 500 ohm)
    CLK   charge-locked cell (Pauka 2021, Bartee 2025): TG + pulse capacitor C_pulse = C_node
    TSW   thick-oxide (g5v0d10v5) T-switch, 3.3 V gate drive, break-before-make shunt (after Caglar 2025)

Droop mitigations:
    TGH   TG with a high-V_T PMOS (the TG's off PMOS is its dominant leak)
    TSWB  thick-oxide T-switch with the middle node driven to the held voltage by a buffer
    NTB   thin-oxide NMOS T-switch with the same buffered middle node
    v_underdrive  off-state gate drive beyond the rails: NMOS gates at -v_ud, PMOS gates at VDD + v_ud
The buffer is behavioural (unity gain, offset v_os, no noise); the hold-side device then sees only
v_os across it.

Every hold node carries C_node (gate electrode + interconnect + hold capacitor) and a pad ESD pair.
All models are SKY130 at room temperature; cryogenic bands enter through cfg.cryo (flow/pdk.py).
"""
from dataclasses import dataclass, field, replace

import numpy as np

from . import config, spice
from .pdk import fet18_lib_line

KB = 1.380649e-23
T_NOV = 0.2e-9                   # non-overlap gap of the T-switch shunt clock
R_BOOT = 500.0                   # output resistance of the behavioural bootstrap gate drive
ARCHS_D = ("NSW", "TG", "TGD", "BOOT", "CLK", "TSW", "TGH", "TSWB", "NTB")   # the nine cells of the room-temperature study
ARCHS = ARCHS_D + ("TSWO", "BOOTT")  # TSWB with a transistor-level buffer; BOOT at transistor level
BUFFERED = ("TSWB", "NTB")
HOLD_LIB = config.SPICE_DIR / "sky130_hold.lib"
CELLS = config.SPICE_DIR / "sky130_cells.lib"


@dataclass(frozen=True)
class HoldConfig:
    arch: str = "TG"
    wn: float = 1.0               # NMOS width (um); PMOS is 2x; thick-oxide devices use wn as well
    l: float = 0.15               # thin-oxide length (um); TSW uses 0.5
    c_node: float = 1e-12         # hold-node capacitance (F): gate + interconnect + hold capacitor
    t_edge: float = 200e-12       # clock edge time
    esd_area: float = 100.0       # um^2 per ESD diode (0 = no ESD)
    corner: str = "tt"
    temp: float = 27.0
    vdd: float = 1.8
    vddh: float = 3.3             # thick-oxide gate drive (TSW)
    r_src: float = 50.0           # DAC output resistance
    dv_line: float = 0.5          # DAC-line step used to measure feedthrough
    v_hold: tuple = tuple(np.round(np.linspace(0.3, 1.5, 7), 3))
    v_underdrive: float = 0.0     # off-state gate overdrive beyond the rails (V)
    v_os: float = 1e-3            # offset of the middle-node buffer (TSWB, NTB)
    i_buf: float = 10e-9          # TSWO: OTA tail current (A)
    cryo: tuple = None            # (dV_T in V, mobility factor) cryogenic proxy; None = PDK models
    mismatch: bool = False
    seed: int = 1
    workdir: str = "build/holdstage"
    extra: dict = field(default_factory=dict)

    def tag(self):
        return (f"{self.arch}_w{self.wn:g}_c{self.c_node * 1e15:g}f_e{self.t_edge * 1e12:g}p_"
                f"esd{self.esd_area:g}_{self.corner}_{self.temp:g}C_l{self.l:g}_ud{self.v_underdrive:g}"
                f"_os{self.v_os * 1e3:g}m" + (f"_ib{self.i_buf * 1e9:g}n" if self.arch == "TSWO" else "")
                + (f"_mm{self.seed}" if self.mismatch else "")
                + (f"_cryo{self.cryo[0] * 1e3:g}m{self.cryo[1]:g}" if self.cryo else "")
                + (f"mm{self.cryo[2]:g}" if self.cryo and len(self.cryo) > 2 else "")
                + (f"p{self.cryo[3] * 1e3:g}m{self.cryo[4]:g}" if self.cryo and len(self.cryo) > 4 else ""))


def _r_on_estimate(cfg):
    """Rough on-resistance (ohm) used only to size the track and settle times."""
    # mid-rail values (TG resistance peaks there); NSW is only used below ~1 V, where it passes
    base = {"NSW": 10e3, "TG": 10e3, "TGD": 10e3, "BOOT": 3e3, "CLK": 10e3, "TSW": 15e3,
            "TGH": 15e3, "TSWB": 15e3, "TSWO": 15e3, "NTB": 25e3, "BOOTT": 3e3}[cfg.arch]
    scale_l = cfg.l / 0.15 if cfg.arch not in ("TSW", "TSWB", "TSWO") else 1.0
    if cfg.cryo:                # cryogenic proxy: a raised V_T leaves less overdrive near mid-rail
        base *= 5.0
    return base / cfg.wn * scale_l + cfg.r_src


def timeline(cfg):
    tau = _r_on_estimate(cfg) * cfg.c_node * (2 if cfg.arch == "CLK" else 1)
    settle = max(20e-9, 30 * tau)
    t1 = 1.5e-9 + 2 * cfg.t_edge         # room for the non-overlapping shunt clock (TSW)
    t_open = t1 + cfg.t_edge + settle
    t_ped = t_open + 2 * cfg.t_edge + 3e-9
    t_line = t_ped + 1e-9
    t_reclose = t_line + 30e-9 + 2 * cfg.t_edge
    t_reopen = t_reclose + 2 * cfg.t_edge + settle
    t_stop = t_reopen + cfg.t_edge + 5e-9
    return dict(t1=t1, t_open=t_open, t_ped=t_ped, t_line=t_line, t_reclose=t_reclose,
                t_reopen=t_reopen, t_stop=t_stop, tau=tau)


def _header(cfg, abstol=1e-14):
    """abstol: 1e-14 A for the switching transient; the leakage deck needs sub-fA resolution (1e-16 = 0.1 fA; 1e-17 fails to converge)."""
    lib = fet18_lib_line(cfg.corner, "hold", cfg.mismatch, cfg.cryo)
    seed = f".option seed={cfg.seed}\n" if cfg.mismatch else ""
    return (f"* hold stage {cfg.tag()}\n{lib}\n.include \"{CELLS.as_posix()}\"\n"
            f".include \"{HOLD_LIB.as_posix()}\"\n.temp {cfg.temp}\n{seed}"
            f".option method=gear reltol=1e-5 abstol={abstol:g} vntol=1e-7 gmin=1e-18\n")


def _clock(name, lo, hi, t_on, t_off, t_on2, t_off2, te):
    pts = [(0, lo), (t_on, lo), (t_on + te, hi), (t_off, hi), (t_off + te, lo),
           (t_on2, lo), (t_on2 + te, hi), (t_off2, hi), (t_off2 + te, lo)]
    return f"V{name} {name} 0 PWL(" + " ".join(f"{t:.6e} {v:.4f}" for t, v in pts) + ")"


def _switch(cfg, i, src, hold, ck=""):
    """Switch instance i between src and hold. ck suffixes the clock nets (en{ck}, enb{ck}, ...), so
    several cells on one DAC line can have their own clocks (flow/cosim.py)."""
    a, wn, l = cfg.arch, cfg.wn, cfg.l
    en, enb, enh, enhb, ensh = (f"{n}{ck}" for n in ("en", "enb", "enh", "enhb", "ensh"))
    if a == "NSW":
        return f"XSW{i} {src} {hold} {en} 0 NSWG wn={wn} l={l}"
    if a in ("TG", "CLK"):
        s = f"XSW{i} {src} {hold} {en} {enb} vdd 0 TGG wn={wn} wp={2 * wn} l={l}"
        if a == "CLK":
            s += f"\nCP{i} {hold} drv {cfg.c_node:.6e}"
        return s
    if a == "TGD":
        return f"XSW{i} {src} {hold} {en} {enb} vdd 0 TGD wn={wn} wp={2 * wn} l={l}"
    if a == "BOOT":
        ud = cfg.v_underdrive
        r = f"((v({en}) + {ud}) / {cfg.vdd + ud})"
        geo = f"ad={wn * 0.29:g} as={wn * 0.29:g} pd={2 * (wn + 0.29):g} ps={2 * (wn + 0.29):g}"
        return (f"XSW{i} {src} g{i} {hold} 0 sky130_fd_pr__nfet_01v8 w={wn} l={l} {geo}\n"
                f"BG{i} gd{i} 0 V = {r} * (v({src}) + {cfg.vdd}) - (1 - {r}) * {ud}\n"
                f"RG{i} gd{i} g{i} {R_BOOT}")
    if a == "TSW":
        return f"XSW{i} {src} {hold} {enh} {enhb} 0 TSW wn={wn} l=0.5"
    if a == "TGH":
        return f"XSW{i} {src} {hold} {en} {enb} vdd 0 TGH wn={wn} wp={2 * wn} l={l}"
    if a == "BOOTT":
        # transistor-level bootstrapped switch (sky130_hold.lib); gate underdrive via the vneg rail
        return f"XSW{i} {src} {hold} {enh} {enhb} vdd vneg 0 BOOTT wn={wn} l={l}"
    if a == "TSWO":
        # the buffer is a transistor-level thick-oxide OTA in unity gain (sky130_hold.lib)
        return (f"XSW{i} {src} {hold} {enh} {enhb} buf{i} 0 TSWB wn={wn} l=0.5\n"
                f"XOTA{i} {hold} buf{i} buf{i} vddh vbp 0 OTA5T")
    if a in BUFFERED:
        buf = f"EB{i} bx{i} 0 {hold} 0 1\nVOS{i} buf{i} bx{i} {cfg.v_os}"
        if a == "TSWB":
            return f"XSW{i} {src} {hold} {enh} {enhb} buf{i} 0 TSWB wn={wn} l=0.5\n" + buf
        return f"XSW{i} {src} {hold} {en} {ensh} buf{i} 0 NTB wn={wn} l={l}\n" + buf
    raise ValueError(a)


def globals_(cfg):
    """Nets shared by all cells: the OTA bias reference (one per chip) for TSWO; the negative
    gate-underdrive rail for BOOTT."""
    if cfg.arch == "BOOTT":
        return [f"VNEG vneg 0 {-cfg.v_underdrive}"]
    if cfg.arch != "TSWO":
        return []
    return [f"IREF vbp 0 {cfg.i_buf:.4e}",
            "XMREF vbp vbp vddh vddh sky130_fd_pr__pfet_g5v0d10v5 w=2 l=2 ad=0.58 as=0.58 pd=4.58 ps=4.58"]


def _node(cfg, i, hold):
    s = f"CH{i} {hold} 0 {cfg.c_node:.6e}"
    if cfg.esd_area > 0:
        p = 4 * np.sqrt(cfg.esd_area)
        s += f"\nXESD{i} {hold} vdd 0 ESD a={cfg.esd_area:g} p={p:g}"
    return s


def transient_deck(cfg):
    tl = timeline(cfg)
    te = cfg.t_edge
    clk = (tl["t1"], tl["t_open"], tl["t_reclose"], tl["t_reopen"], te)
    # Break-before-make for the T-switch shunt: it opens before the series switches close and closes
    # after they open, with a gap T_NOV. With overlapping clocks, slow edges short the node to ground.
    d = te + T_NOV
    clk_shunt = (tl["t1"] - d, tl["t_open"] + d, tl["t_reclose"] - d, tl["t_reopen"] + d, te)
    ud = cfg.v_underdrive
    lines = [_header(cfg), f"VDD vdd 0 {cfg.vdd}", f"VDDH vddh 0 {cfg.vddh}", "VDRV drv 0 0",
             _clock("en", -ud, cfg.vdd, *clk), _clock("enb", cfg.vdd + ud, 0, *clk),
             _clock("enh", -ud, cfg.vddh, *clk), _clock("enhb", cfg.vddh, 0, *clk_shunt),
             _clock("ensh", cfg.vdd, 0, *clk_shunt)] + globals_(cfg)
    tl0, tl1 = tl["t_line"], tl["t_line"] + 1e-9
    for i, v in enumerate(cfg.v_hold):
        dv = cfg.dv_line if v + cfg.dv_line <= cfg.vdd else -cfg.dv_line
        pwl = (f"PWL(0 {v} {tl0:.6e} {v} {tl1:.6e} {v + dv} {tl1 + 10e-9:.6e} {v + dv} "
               f"{tl1 + 11e-9:.6e} {v})")
        lines += [f"VIN{i} vin{i} 0 {pwl}", f"RS{i} vin{i} src{i} {cfg.r_src}",
                  _switch(cfg, i, f"src{i}", f"hold{i}"), _node(cfg, i, f"hold{i}")]
    saves = " ".join(f"v(hold{i})" for i in range(len(cfg.v_hold)))
    lines += [f".save {saves}", f".tran {min(10e-12, te / 10):.3e} {tl['t_stop']:.6e}", ".end", ""]
    return "\n".join(lines)


RAMP_V, RAMP_T0, RAMP_T1 = 0.01, 10e-9, 20e-9
LEAK_ABSTOLS = (1e-16, 1e-15, 1e-14)


def leakage_deck(cfg, v_line, abstol=1e-16):
    """Switch off, hold node forced to v, DAC line at v_line: the source current is the leakage.

    After 10 ns the forcing source ramps by 10 mV in 10 ns; the extra current during the ramp gives
    the node's total capacitance (C_node + ESD junctions + switch), used for droop and kT/C."""
    lines = [_header(cfg, abstol=abstol), f"VDD vdd 0 {cfg.vdd}", f"VDDH vddh 0 {cfg.vddh}", "VDRV drv 0 0",
             f"VEN en 0 {-cfg.v_underdrive}", f"VENB enb 0 {cfg.vdd + cfg.v_underdrive}",
             f"VENH enh 0 {-cfg.v_underdrive}", f"VENHB enhb 0 {cfg.vddh}", f"VENSH ensh 0 {cfg.vdd}",
             f"VLINE line 0 {v_line}"] + globals_(cfg)
    for i, v in enumerate(cfg.v_hold):
        lines += [_switch(cfg, i, "line", f"hold{i}"), _node(cfg, i, f"hold{i}"),
                  f"VH{i} hold{i} 0 PWL(0 {v} {RAMP_T0:.3e} {v} {RAMP_T1:.3e} {v + RAMP_V} 1 {v + RAMP_V})"]
    saves = " ".join(f"i(vh{i})" for i in range(len(cfg.v_hold)))
    lines += [f".save {saves}", f".tran 0.1n {RAMP_T1:.3e}", ".end", ""]
    return "\n".join(lines)


def _settled(t, v, t_end, span=1e-9):
    m = (t > t_end - span) & (t <= t_end)
    return float(np.mean(v[m])) if m.any() else float(np.interp(t_end, t, v))


def measure(cfg):
    """Run both decks and extract the per-voltage error terms. Returns a dict of arrays/floats."""
    tl = timeline(cfg)
    w = spice.run_ngspice(transient_deck(cfg), cfg.workdir, cfg.tag())
    t = w["time"]
    vh = np.array(cfg.v_hold)
    pre, ped, ft, ped2, glitch_amp, glitch_tau, wave = [], [], [], [], [], [], []
    for i, v in enumerate(vh):
        x = w[f"v(hold{i})"]
        v_pre = _settled(t, x, tl["t_open"] - 0.1e-9)
        v_post = _settled(t, x, tl["t_ped"])
        dv = cfg.dv_line if v + cfg.dv_line <= cfg.vdd else -cfg.dv_line
        v_ft = _settled(t, x, tl["t_line"] + 10e-9)
        v_back = _settled(t, x, tl["t_reclose"] - 0.5e-9)
        v_closed = _settled(t, x, tl["t_reopen"] - 0.1e-9)
        v_post2 = _settled(t, x, tl["t_stop"])
        pre.append(v_pre - v)
        ped.append(v_post - v_pre)
        ft.append((v_ft - v_back) / dv)
        ped2.append(v_post2 - v_closed)
        # refresh transient: node relative to its final (closed) value, from the re-close edge
        m = (t >= tl["t_reclose"]) & (t <= tl["t_reopen"])
        tr, xr = t[m] - tl["t_reclose"], x[m] - v_closed
        k = int(np.argmax(np.abs(xr)))
        amp = xr[k]
        below = np.nonzero(np.abs(xr[k:]) < abs(amp) / np.e)[0]
        tau = float(tr[k + below[0]] - tr[k]) if below.size else np.nan
        glitch_amp.append(float(amp))
        glitch_tau.append(tau)
        wave.append((tr, xr))
    out = dict(v_hold=vh, track_error=np.array(pre), pedestal=np.array(ped),
               pedestal_repeat=np.array(ped2), feedthrough=np.array(ft),
               refresh_glitch=np.array(glitch_amp), refresh_tau=np.array(glitch_tau),
               refresh_waves=wave, timeline=tl)
    # leakage, worst of DAC line low / high
    leak, caps = [], []
    slope = RAMP_V / (RAMP_T1 - RAMP_T0)
    abstol_used = 0.0
    for v_line in (0.0, cfg.vdd):
        # The 0.1 fA tolerance occasionally fails to converge ("timestep too small"); fall back to
        # 1 fA, then 10 fA, and record the coarsest used (the leakage resolution of this point).
        for tol in LEAK_ABSTOLS:
            try:
                wl = spice.run_ngspice(leakage_deck(cfg, v_line, tol), cfg.workdir,
                                       cfg.tag() + f"_leak{v_line:g}")
                break
            except spice.SpiceError:
                if tol == LEAK_ABSTOLS[-1]:
                    raise
        abstol_used = max(abstol_used, tol)
        tt = wl["time"]
        i_hold = [np.interp(RAMP_T0 - 0.2e-9, tt, wl[f"i(vh{i})"]) for i in range(len(vh))]
        i_ramp = [np.interp(0.5 * (RAMP_T0 + RAMP_T1), tt, wl[f"i(vh{i})"]) for i in range(len(vh))]
        # ngspice branch current flows + -> - through the source: a node that leaks away draws
        # negative i(vh), and the drift of a floating node is dV/dt = i(vh) / C.
        leak.append(np.array(i_hold))
        caps.append(-(np.array(i_ramp) - np.array(i_hold)) / slope)
    leak = np.array(leak)                     # (2, n)
    c_eff = float(np.mean(caps))
    out["leakage"] = leak
    out["droop"] = leak / c_eff               # V/s the node would drift if left floating
    out["c_eff"] = c_eff
    out["c_node_measured"] = np.array(caps)
    out["leak_abstol"] = abstol_used
    return out


def summarize(cfg, m):
    """Scalar figures for comparison with the error budget."""
    p = m["pedestal"]
    if len(p) >= 3:
        coef = np.polyfit(m["v_hold"], p, 1)
        resid = p - np.polyval(coef, m["v_hold"])
    else:
        coef, resid = (np.nan, np.nan), np.zeros_like(p)
    return dict(
        pedestal_mean=float(np.mean(p)),
        pedestal_span=float(np.ptp(p)),
        pedestal_slope=float(coef[0]),
        pedestal_linear_residual=float(np.max(np.abs(resid))),
        pedestal_repeatability=float(np.max(np.abs(m["pedestal_repeat"] - p))),
        track_error_max=float(np.max(np.abs(m["track_error"]))),
        feedthrough_max=float(np.max(np.abs(m["feedthrough"]))),
        refresh_glitch_max=float(np.max(np.abs(m["refresh_glitch"]))),
        refresh_tau=float(np.nanmedian(m["refresh_tau"])),
        droop_max=float(np.max(np.abs(m["droop"]))),
        leakage_max=float(np.max(np.abs(m["leakage"]))),
        ktc_rms_300k=float(np.sqrt(KB * 300 / m["c_eff"])),
        ktc_rms_4k=float(np.sqrt(KB * 4 / m["c_eff"])),
        c_eff=float(m["c_eff"]),
        leak_abstol=float(m["leak_abstol"]),
    )


def run(cfg=None, **kw):
    cfg = replace(cfg or HoldConfig(), **kw)
    m = measure(cfg)
    return cfg, m, summarize(cfg, m)
