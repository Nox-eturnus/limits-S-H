"""Tests of the multiplexed co-simulation, transistor-level buffer, scaling model (flow/cosim.py)."""
import numpy as np
import pytest

from conftest import needs_spice
from flow import budget as B
from flow import cosim as C
from flow import holdstage as H

WORK = "build/tests/cosim"
CELL = {"tau_node": 10e-9, "c_line_cell": 1.5e-15, "e_clk": 1e-14, "p_static": 0.0}


def cfg(**kw):
    return H.HoldConfig(workdir=WORK, **kw)


@pytest.fixture(scope="module")
def lay():
    return B.layer(s_dec_per_v=10.0)


# ---------------------------------------------------------------- scaling model (no SPICE)

def test_n_max_fills_the_hold_time():
    n = C.n_max(1.0, CELL, 1.37e-3, 2.4e-3)
    assert n * C.slot_time(n, CELL, 1.37e-3, 2.4e-3) == pytest.approx(1.0, rel=1e-4)


def test_flat_line_scales_as_sqrt_of_hold_time_when_line_limited():
    """With n * c_line_cell >> c_wire, t_slot ~ n, so n_max ~ sqrt(hold time)."""
    line = C.LineConfig(c_wire=0.0, t_overhead=0.0)
    cell = dict(CELL, tau_node=0.0)
    n1 = C.n_max(1.0, cell, 1.37e-3, 2.4e-3, line)
    n100 = C.n_max(100.0, cell, 1.37e-3, 2.4e-3, line)
    assert n100 / n1 == pytest.approx(10.0, rel=1e-3)


def test_tree_demux_beats_flat_line():
    tree = C.LineConfig(c_line_fixed=10e-12)
    assert C.n_max(10.0, CELL, 1.37e-3, 2.4e-3, tree) > 5 * C.n_max(10.0, CELL, 1.37e-3, 2.4e-3)


def test_hold_budget_is_linear_in_the_static_terms():
    """Deterministic offsets add as voltages: spec (1 - eps) - |residual|, doubled when centred."""
    assert C.hold_budget(1e-3, 2e-4, 0.1, centred=False) == pytest.approx(0.7e-3)
    assert C.hold_budget(1e-3, 2e-4, 0.1, centred=True) == pytest.approx(1.4e-3)
    assert C.hold_budget(1e-3, 2e-4, 0.1, comp_residual=0.1, centred=False) == pytest.approx(7e-3)
    assert C.hold_budget(1e-3, 2e-3) == 0.0


def test_area_grows_with_hold_capacitance():
    a1 = C.area_um2(H.HoldConfig(arch="TG", c_node=1e-12))["total"]
    a3 = C.area_um2(H.HoldConfig(arch="TG", c_node=3e-12))["total"]
    assert a3 - a1 == pytest.approx(2e-12 / C.MIM_DENSITY, rel=1e-9)        # 1000 um^2 per 2 pF


def test_deterministic_errors_add_in_phase(lay):
    """Phase-additive combination is exact to first order for slow errors; adding infidelities is not
    (a static offset and an opposite droop cancel)."""
    a, b = 0.6e-3, -0.6e-3
    real = lay.excess_infidelity(B.static(lay, a + b))
    ph = lay.phase_errors(B.static(lay, a)) + lay.phase_errors(B.static(lay, b))
    assert B.phase_infidelity(ph) == pytest.approx(real, abs=2e-7)
    assert lay.excess_infidelity(B.static(lay, a)) + lay.excess_infidelity(B.static(lay, b)) > 1e-4


# ---------------------------------------------------------------- SPICE

@needs_spice
def test_transistor_buffer_matches_behavioural_droop():
    """TSWO (5T OTA, thick oxide) holds the middle node as well as the ideal buffer of TSWB."""
    d_ideal = H.run(cfg(arch="TSWB", esd_area=0.0))[2]["droop_max"]
    d_ota = H.run(cfg(arch="TSWO", esd_area=0.0))[2]["droop_max"]
    assert d_ota == pytest.approx(d_ideal, rel=0.5)
    assert d_ota < 1e-3                                                      # junction floor, V/s


@needs_spice
def test_droop_extrapolation_matches_a_long_transient():
    drift, pred = C.long_hold_check(cfg(arch="TSWB", esd_area=100.0), 30e-3, v=0.6)
    assert drift == pytest.approx(pred, rel=0.02)


@needs_spice
def test_cell_parameters():
    p = C.cell_params(cfg(arch="TG", esd_area=0.0))
    assert 0.5e-15 < p["c_line_cell"] < 5e-15                                # off TG seen from the line
    assert 3e-9 < p["tau_node"] < 30e-9                                     # ~R_on * 1 pF
    assert 1e-15 < p["e_clk"] < 1e-13


@needs_spice
def test_slot_model_settles_within_eps():
    """A multiplexed line on 100 pF refreshed with the model's slot (margin 1) settles to the same
    level as with a 3x longer slot, within eps = 10 % of the static spec."""
    c = cfg(arch="TG", esd_area=0.0)
    cell = C.cell_params(c)
    eps = 0.137e-3
    lv = []
    for margin in (1.0, 3.0):
        mux = C.MuxConfig(c_line=100e-12, margin=margin, t_gap=20e-9)
        tg = [0.9, 0.3, 1.2, 0.6]
        deck, tl = C.mux_deck(c, mux, tg, tg, cell, eps, None)
        w = C.spice.run_ngspice(deck, WORK, c.tag() + f"_slot_m{margin:g}")
        t = w["time"]
        lv.append([np.mean(w[f"v(hold{k})"][(t > tl["t_cz"] - 3e-9) & (t <= tl["t_cz"])]) for k in range(4)])
    assert np.max(np.abs(np.subtract(*lv))) < eps


@needs_spice
def test_cosim_no_esd_after_insitu_calibration(lay):
    """TG without ESD on a multiplexed line: after in-situ calibration the static error is the
    pedestal's nonlinearity (~0.1 mV) and the real waveform costs < 1e-5."""
    res, cal, _ = C.cosim(cfg(arch="TG", esd_area=0.0), lay, (0.3, 0.9, 1.5), mux=C.MuxConfig(t_gap=50e-9))
    assert max(abs(r["static"]) for r in res) < 150e-6
    assert max(r["infidelity"] for r in res) < 1e-5


@needs_spice
def test_esd_capacitance_distorts_the_capacitive_pulse(lay):
    """With a 100 um^2 ESD pair on the node, the coupling k depends on the held voltage and the pulse
    is distorted: > 30x the infidelity of the same cell without ESD, at 0.3 V."""
    kw = dict(mux=C.MuxConfig(t_gap=50e-9))
    with_esd, cal, _ = C.cosim(cfg(arch="TG", esd_area=100.0), lay, (0.3, 0.9, 1.5), **kw)
    without, _, _ = C.cosim(cfg(arch="TG", esd_area=0.0), lay, (0.3, 0.9, 1.5), **kw)
    dyn = lambda r: lay.excess_infidelity(r["dv"] - r["static"])  # noqa: E731
    assert dyn(with_esd[0]) > 30 * dyn(without[0])
    assert cal["k"][0] < cal["k"][-1]                   # more junction capacitance at low voltage


@needs_spice
@pytest.mark.parametrize("r_src", [50.0, 2000.0])
def test_distributed_line_settling_model_is_conservative(r_src):
    """The slot model's line term (Elmore: R_src + R_wire / 2) against an RC ladder in SPICE: the far
    end settles a 1.2 V step to eps within the model's time, and not much faster (< 40 % margin)."""
    n, r_seg, c_seg = 200, 20.0, 5e-15
    eps = 0.137e-3
    lines = ["* RC ladder", f"VS s 0 PWL(0 0 1n 1.2)", f"RS s n0 {r_src}"]
    for k in range(n):
        lines += [f"R{k} n{k} n{k + 1} {r_seg}", f"C{k} n{k + 1} 0 {c_seg}"]
    line = C.LineConfig(r_src=r_src, c_wire=0.0, t_overhead=0.0, r_wire_per=r_seg, c_wire_per=c_seg)
    cell = {"c_line_cell": 0.0, "tau_node": 0.0}
    t_model = C.slot_time(n, cell, eps / 0.1, 0.0, line)
    lines += [".save v(n%d)" % n, f".tran 1p {3 * t_model + 1e-9:.3e}", ".end", ""]
    w = C.spice.run_ngspice("\n".join(lines), WORK, f"ladder_{r_src:g}")
    t, v = w["time"], w[f"v(n{n})"]
    late = np.nonzero(np.abs(v - 1.2) > eps)[0]
    t_spice = t[late[-1]] - 1e-9
    assert t_spice <= t_model
    assert t_spice > 0.6 * t_model


# ---------------------------------------------------------------- tree demultiplexer

def test_tree_levels_single_upper_level():
    tree = C.TreeConfig()
    lv = C.tree_levels(1e6, tree)
    assert [f for f, _, _ in lv] == pytest.approx([1000, 1000])
    assert lv[0][1] == pytest.approx(np.sqrt(1000) * tree.pitch)            # one leaf region per child
    assert lv[-1] == (1000, tree.pitch, True)


def test_tree_levels_with_fanout():
    lv = C.tree_levels(1e9, C.TreeConfig(fanout=10))
    assert [f for f, _, _ in lv] == pytest.approx([10] * 6 + [1000])         # 1e6 leaf lines in 6 levels
    assert np.prod([f for f, _, _ in lv]) == pytest.approx(1e9)


def test_leaf_only_tree_matches_flat_line():
    """Below one leaf line the tree is a flat met2 line. Without the lumped root capacitance the two
    Elmore sums agree; with it, the flat model is more conservative, because it places the root
    capacitance behind half of the wire resistance."""
    cell = dict(CELL)
    flat = C.LineConfig(c_wire=0.0, r_wire_per=5.5, c_wire_per=2.2e-15)
    t_flat = C.slot_time(800, cell, 1.37e-3, 2.4e-3, flat)
    t_tree = C.tree_slot_time(800, cell, 1.37e-3, 2.4e-3, C.TreeConfig(c_root=0.0))
    assert t_tree == pytest.approx(t_flat, rel=0.03)
    t_flat10 = C.slot_time(800, cell, 1.37e-3, 2.4e-3, C.LineConfig(r_wire_per=5.5, c_wire_per=2.2e-15))
    assert C.tree_slot_time(800, cell, 1.37e-3, 2.4e-3, C.TreeConfig()) < t_flat10


def test_upper_levels_reduce_the_tree_count():
    """The leaf-only tree is an upper bound: adding the levels above it lowers N."""
    cell, s, bd = dict(CELL), 1.37e-3, 2.4e-3
    leaf_only = C.LineConfig(c_line_fixed=10e-12 + 1000 * cell["c_line_cell"], r_wire_per=5.5, c_wire_per=2.2e-15)
    for hold in (0.5, 400.0):
        n_old = C.n_max(hold, cell, s, bd, leaf_only)
        n_new = C.n_max_tree(hold, cell, s, bd, C.TreeConfig())
        assert n_new < n_old
        assert n_new * C.tree_slot_time(n_new, cell, s, bd) == pytest.approx(hold, rel=1e-3)


@needs_spice
def test_tree_path_settling_model_is_conservative():
    """Elmore delay of a two-level tree path (root, one upper line with series switch, leaf line)
    against the same RC network in SPICE with 100 segments per line."""
    tree = C.TreeConfig(leaf=50, pitch=100e-6, r_src=200.0, c_root=1e-12, w_tree=4.0)
    cell = {"c_line_cell": 2e-15, "tau_node": 2e3 * 1e-12}                    # cell R_on = 2 kOhm
    n, eps = 50 * 20, 0.137e-3
    tau, _, _ = C.tree_path(n, cell, tree)
    t_model = tau * np.log(1.2 / eps)
    lines = ["* tree path", "VS s 0 PWL(0 0 1n 1.2)", f"RS s n0 {tree.r_src}", f"C0 n0 0 {tree.c_root}"]
    node, m = "n0", 100
    for k, (f, side, leaf) in enumerate(C.tree_levels(n, tree)):
        if k:
            lines.append(f"RSW{k} {node} l{k}_0 {cell['tau_node'] / tree.c_node / tree.w_tree}")
            node = f"l{k}_0"
        length = f * side
        c_sw = f * (cell["c_line_cell"] if leaf else tree.w_tree * cell["c_line_cell"])
        for j in range(m):
            nxt = f"l{k}_{j + 1}"
            lines += [f"R{k}_{j} {node} {nxt} {tree.r_wire * length / m}",
                      f"C{k}_{j} {nxt} 0 {(tree.c_wire * length + c_sw) / m}"]
            node = nxt
    lines += [f".save v({node})", f".tran 1p {3 * t_model + 1e-9:.3e}", ".end", ""]
    w = C.spice.run_ngspice("\n".join(lines), WORK, "tree_path")
    t, v = w["time"], w[f"v({node})"]
    late = np.nonzero(np.abs(v - 1.2) > eps)[0]
    t_spice = t[late[-1]] - 1e-9
    assert t_spice <= t_model
    assert t_spice > 0.6 * t_model
