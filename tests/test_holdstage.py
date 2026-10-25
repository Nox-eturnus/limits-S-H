"""Tests of the S/H testbench extracts physically consistent error terms (flow/holdstage.py)."""
import numpy as np
import pytest

from conftest import needs_spice
from flow import holdstage as H

WORK = "build/tests/holdstage"


def run(**kw):
    return H.run(workdir=WORK, **kw)


@pytest.fixture(scope="module")
def tg():
    return run(arch="TG")


@needs_spice
def test_tg_tracks_and_has_mv_scale_pedestal(tg):
    _, m, s = tg
    assert s["track_error_max"] < 10e-6                       # settled before the switch opens
    assert 0.05e-3 < s["pedestal_span"] < 5e-3                # ~mV on 1 pF


@needs_spice
def test_pedestal_scales_inversely_with_node_capacitance():
    """Injected charge is fixed by the switch, so the pedestal ~ 1/C. Without ESD diodes, whose
    junctions add ~170 fF at 100 um^2 and would dilute the ratio."""
    _, _, s1 = run(arch="TG", esd_area=0.0)
    _, _, s5 = run(arch="TG", c_node=200e-15, esd_area=0.0)
    assert s5["pedestal_span"] / s1["pedestal_span"] == pytest.approx(5.0, rel=0.1)


@needs_spice
def test_measured_node_capacitance():
    """The ramp measurement recovers C_node without ESD, and shows the ESD junction capacitance."""
    _, _, bare = run(arch="TG", esd_area=0.0)
    _, _, esd = run(arch="TG", esd_area=100.0)
    assert bare["c_eff"] == pytest.approx(1e-12, rel=0.02)
    assert 50e-15 < esd["c_eff"] - bare["c_eff"] < 400e-15


@needs_spice
def test_dummy_switches_cancel_most_of_the_injection(tg):
    _, _, s_tg = tg
    _, _, s_d = run(arch="TGD")
    assert s_d["pedestal_span"] < 0.2 * s_tg["pedestal_span"]


@needs_spice
def test_slow_edges_reduce_injection():
    """With slow clock edges part of the channel charge returns to the low-impedance source. Shown
    on a small node (50 fF): on 1 pF the overlap feedthrough dominates and edges hardly matter."""
    kw = dict(arch="NSW", c_node=50e-15, esd_area=0.0, v_hold=(0.3, 0.5, 0.7))
    _, _, fast = run(t_edge=50e-12, **kw)
    _, _, slow = run(t_edge=5e-9, **kw)
    assert abs(slow["pedestal_mean"]) < 0.75 * abs(fast["pedestal_mean"])


@needs_spice
def test_nmos_switch_cannot_pass_high_voltages():
    _, m, _ = run(arch="NSW")
    assert abs(m["track_error"][-1]) > 0.1                    # 1.5 V is above VDD - V_T


@needs_spice
def test_t_switch_isolates_the_dac_line(tg):
    """The shunted middle node of the T-switch blocks DAC-line feedthrough."""
    _, _, s_tg = tg
    _, _, s_t = run(arch="TSW")
    assert s_t["feedthrough_max"] < 0.1 * s_tg["feedthrough_max"]


@needs_spice
def test_leak_corner_leaks_more_than_typical():
    _, _, tt = run(arch="NSW", v_hold=(0.5,))
    _, _, lk = run(arch="NSW", v_hold=(0.5,), corner="leak")
    assert lk["leakage_max"] > 3 * tt["leakage_max"]


@needs_spice
def test_droop_is_leakage_over_capacitance(tg):
    _, m, _ = tg
    assert np.allclose(m["droop"], m["leakage"] / m["c_eff"])


# ---------------------------------------------------------------- droop mitigations (second pass)

def _leak(**kw):
    return run(**kw)[2]["leakage_max"]


@needs_spice
def test_high_vt_pmos_removes_the_tg_leak():
    """The plain TG's off PMOS dominates its leakage; a high-V_T PMOS cuts it by > 100x."""
    assert _leak(arch="TGH", esd_area=0.0) < 0.01 * _leak(arch="TG", esd_area=0.0)


@needs_spice
def test_underdrive_cuts_nmos_channel_leakage():
    kw = dict(arch="NSW", esd_area=0.0, v_hold=(0.3, 0.6, 0.9))
    assert _leak(v_underdrive=0.3, **kw) < 0.05 * _leak(**kw)


@needs_spice
def test_buffered_middle_node_cuts_t_switch_leakage():
    """Driving the T-switch middle node to the held voltage removes the hold-side channel leakage."""
    assert _leak(arch="TSWB", esd_area=0.0) < 0.01 * _leak(arch="TSW", esd_area=0.0)


@needs_spice
def test_esd_sets_the_floor_once_channel_leakage_is_gone():
    with_esd = _leak(arch="TSWB", esd_area=100.0)
    without = _leak(arch="TSWB", esd_area=0.0)
    assert with_esd > 100 * without


@needs_spice
def test_junction_floor_scales_with_drain_area():
    """With channel leakage suppressed, the remaining leak is the drain junction: ~ W (needs the
    diffusion geometry in sky130_hold.lib; with ad = 0 the model gives a fixed ~10 fA)."""
    kw = dict(arch="NSW", esd_area=0.0, v_underdrive=0.3, v_hold=(0.3, 0.6, 0.9))
    ratio = _leak(wn=10.0, **kw) / _leak(wn=1.0, **kw)
    assert 5 < ratio < 15
