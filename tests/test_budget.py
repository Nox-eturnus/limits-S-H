"""Tests of the error-budget model (flow/budget.py) against exact numerics and closed forms."""
import numpy as np
import pytest

from flow import budget as B
from flow import cz


@pytest.fixture(scope="module")
def stark_layer():
    return B.layer()                                   # s = 10 dec/V, dEz = 100 MHz, Stark on Q2


@pytest.fixture(scope="module")
def j_only_layer():
    return B.layer(stark_q2=0.0)


def test_nominal_layer_is_a_good_cz(stark_layer, j_only_layer):
    assert 1 - j_only_layer.f_nominal < 1e-6
    assert 1 - stark_layer.f_nominal < 1e-5           # nominal pulse Stark shift ~26 MHz on Q2
    assert stark_layer.excess_infidelity(B.static(stark_layer, 0.0)) == pytest.approx(0, abs=1e-12)
    assert stark_layer.infidelity(B.static(stark_layer, 0.0)) == pytest.approx(1 - stark_layer.f_nominal)


@pytest.mark.parametrize("dv", [3e-4, 1e-3, -1e-3, 3e-3])
@pytest.mark.parametrize("which", ["stark_layer", "j_only_layer"])
def test_adiabatic_model_matches_numerics_static(dv, which, request):
    lay = request.getfixturevalue(which)
    err = B.static(lay, dv)
    assert lay.infidelity_adiabatic(err) == pytest.approx(lay.excess_infidelity(err), rel=5e-3)


def test_adiabatic_model_reduces_to_phase_b_formula():
    """dEz >> J and no Stark: the J-scale error is a pure conditional phase, 0.4 (1 - cos(pi e/2))."""
    lay = B.layer(d_ez=20e9, stark_q2=0.0)
    for dv in (5e-4, 2e-3, -2e-3):
        e = lay.ex.relative_error(dv)
        assert lay.infidelity_adiabatic(B.static(lay, dv)) == pytest.approx(
            cz.infidelity_static_scale(e), rel=1e-3)


def test_finite_zeeman_difference_adds_local_phase_error():
    """At dEz = 100 MHz the J error also moves R = sqrt(dEz^2 + J^2): a local Z error that the fixed
    Z angles do not absorb. It makes the error a few per cent larger than the conditional-phase
    formula (flow/pipeline.py: 2.8e-4 against 2.7e-4)."""
    lay = B.layer(stark_q2=0.0)
    e = lay.ex.relative_error(1e-3)
    ratio = lay.excess_infidelity(B.static(lay, 1e-3)) / cz.infidelity_static_scale(e)
    assert 1.01 < ratio < 1.10


def test_stark_error_adds_in_quadrature_as_single_qubit_z():
    """Stark on Q2 alone is a Z error phi = 2 pi a2 dv t_gate, 1 - F = 0.2 phi^2, orthogonal to the
    conditional-phase error (dEz >> J so that R tracks dEz)."""
    dv = 1e-3
    on = B.layer(d_ez=20e9)
    off = B.layer(d_ez=20e9, stark_q2=0.0)
    phi = 2 * np.pi * on.cfg.stark_q2 * dv * on.cfg.t_gate
    extra = on.infidelity_adiabatic(B.static(on, dv)) - off.infidelity_adiabatic(B.static(off, dv))
    assert extra == pytest.approx(0.4 * (1 - np.cos(phi)), rel=2e-2)


def test_idle_segment_scales_conditional_phase_error():
    """J_idle keeps accumulating conditional phase in the idle time: delta = pi e (1 + 2 J_idle t_idle)
    (pure-exchange limit, no Stark)."""
    lay = B.layer(d_ez=20e9, stark_q2=0.0, j_idle=100e3, t_idle=2e-6, dt_idle=2e-9)
    dv = 1e-3
    e = lay.ex.relative_error(dv)
    delta = np.pi * e * (1 + 2 * 100e3 * 2e-6)
    expected = 0.4 * (1 - np.cos(delta / 2))
    assert lay.excess_infidelity(B.static(lay, dv)) == pytest.approx(expected, rel=5e-3)
    assert lay.infidelity_adiabatic(B.static(lay, dv)) == pytest.approx(expected, rel=5e-3)


@pytest.mark.parametrize("tau", [3e-9, 10e-9, 100e-9])
@pytest.mark.parametrize("t_event", [0.0, 25e-9])
def test_adiabatic_model_matches_numerics_glitch(stark_layer, tau, t_event):
    """Slow transients are adiabatic. A step at mid-gate (t_event = 25 ns, where J peaks) also
    drives |01> <-> |10> transitions, which the phase model omits: at tau = 3 ns it underestimates
    the exact result by ~20 %; the spec table therefore uses the exact numerics."""
    err = B.glitch(stark_layer, 1e-3, tau, t_event)
    ad, num = stark_layer.infidelity_adiabatic(err), stark_layer.excess_infidelity(err)
    if t_event > 0 and tau < 10e-9:
        assert 0.7 * num < ad < num
    else:
        assert ad == pytest.approx(num, rel=5e-2)


def test_glitch_long_tau_is_static_from_its_event(stark_layer):
    """tau >> t_gate: a glitch at the gate start is the static offset."""
    a = stark_layer.excess_infidelity(B.glitch(stark_layer, 1e-3, 1.0, 0.0))
    b = stark_layer.excess_infidelity(B.static(stark_layer, 1e-3))
    assert a == pytest.approx(b, rel=1e-6)


def test_droop_within_one_gate_is_a_static_offset(stark_layer):
    """3.1 mV/s (van Staveren 2025) moves the barrier by 0.16 nV during a 50 ns gate: the droop
    error is the offset accumulated since the refresh."""
    a = stark_layer.excess_infidelity(B.droop(stark_layer, 3.1e-3, 0.5))
    b = stark_layer.excess_infidelity(B.static(stark_layer, 3.1e-3 * 0.5))
    assert a == pytest.approx(b, rel=1e-6)


def test_kernel_zero_frequency_is_static_curvature(stark_layer):
    assert stark_layer.kernel([1e-3])[0] == pytest.approx(stark_layer.static_curvature(), rel=1e-6)
    dv = 1e-5
    assert stark_layer.excess_infidelity(B.static(stark_layer, dv)) == pytest.approx(
        stark_layer.static_curvature() * dv ** 2, rel=2e-2)


def test_band_limited_white_noise_parseval(stark_layer):
    """Flat PSD over a band wider than the gate spectrum: quadrature = Parseval."""
    s_v = 1e-16
    quad = stark_layer.noise_infidelity(B.flat(s_v), 1e3, 1e11, n_f=1200)
    assert quad == pytest.approx(stark_layer.white_noise_infidelity(s_v), rel=2e-2)


def test_white_noise_monte_carlo_matches_filter_function():
    """White noise reaches the |01>-|10> splitting (~100 MHz), so the transition term matters;
    the phase-only filter function underestimates the Monte Carlo result about 2x."""
    lay = B.layer(dt=10e-12)
    s_v, f_lo, f_hi = (40e-9) ** 2, 1e5, 2e9
    pred = lay.noise_infidelity(B.flat(s_v), f_lo, f_hi)
    assert B.rectification(10, np.sqrt(s_v * f_hi)) < 2e-3       # linear regime
    rng = np.random.default_rng(7)
    mc = np.array([lay.excess_infidelity(B.spectral_noise(lay, B.flat(s_v), f_lo, f_hi, rng, n_f=200))
                   for _ in range(200)])
    assert mc.mean() == pytest.approx(pred, rel=0.2)


def test_one_over_f_monte_carlo_matches_filter_function():
    lay = B.layer(dt=10e-12)
    psd, f_lo, f_hi = B.one_over_f(50e-6), 1e5, 1e10
    pred = lay.noise_infidelity(psd, f_lo, f_hi)
    rng = np.random.default_rng(11)
    mc = np.array([lay.excess_infidelity(B.spectral_noise(lay, psd, f_lo, f_hi, rng, n_f=200))
                   for _ in range(200)])
    assert mc.mean() == pytest.approx(pred, rel=0.2)


def test_one_over_f_is_quasi_static_at_low_cutoff(stark_layer):
    """1/f noise down to f_lo behaves as a static offset of variance a^2 ln(1 / (f_lo t_gate))."""
    for f_lo in (1e-2, 1.0):
        ff = stark_layer.noise_infidelity(B.one_over_f(1.0), f_lo)
        qs = stark_layer.static_curvature() * np.log(1 / (f_lo * stark_layer.cfg.t_gate))
        assert ff == pytest.approx(qs, rel=0.06)


def test_static_solver_hits_target(stark_layer):
    for sign in (+1, -1):
        dv = B.max_static(stark_layer, 1e-3, sign)
        assert stark_layer.excess_infidelity(B.static(stark_layer, sign * dv)) == pytest.approx(1e-3, rel=1e-4)
