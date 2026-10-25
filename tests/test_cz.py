"""Qubit-side tests: the CZ simulator against exact and analytic results."""
import numpy as np
import pytest

from flow import cz, pulses
from flow.exchange import ExponentialExchange


def rc(t_gate, dt):
    t, step = pulses.time_grid(t_gate, dt)
    return pulses.raised_cosine(t, t_gate), step


def test_ideal_waveform_pure_exchange_limit_is_exact():
    """Plan test 1. With dEz >> J the flip-flop term is frozen out and an ideal CZ pulse with
    integral J dt = 1/2 must give fidelity 1 to numerical precision, with no calibration."""
    w, dt = rc(100e-9, 10e-12)
    block = cz.propagate_block(pulses.cz_amplitude(100e-9) * w, 1e13, dt)
    assert 1 - cz.cz_fidelity(block) < 1e-9


def test_ideal_adiabatic_cz_at_realistic_zeeman_difference():
    """Plan test 1, realistic case: 100 ns raised-cosine CZ, dEz = 100 MHz, amplitude calibrated.
    Xue 2022 quotes < 1e-6 infidelity without noise for its 100 ns cosine pulse."""
    w, dt = rc(100e-9, 5e-12)
    _, fid, _ = cz.calibrate_amplitude(w, 100e6, dt, pulses.cz_amplitude(100e-9))
    assert 1 - fid < 1e-6


@pytest.mark.parametrize("rel_error", [0.003, 0.01, 0.03, 0.1, -0.05])
def test_static_offset_matches_analytic_formula(rel_error):
    """Plan test 2. A static J error (as from a barrier pedestal) with the Z angles of the nominal
    pulse must match 1 - F = 0.4 (1 - cos(pi e / 2)) in the adiabatic limit."""
    w, dt = rc(50e-9, 5e-12)
    amp, _, z_nominal = cz.calibrate_amplitude(w, 10e9, dt, pulses.cz_amplitude(50e-9))
    sim = 1 - cz.pulse_fidelity(w, amp * (1 + rel_error), 10e9, dt, z_nominal)
    assert sim == pytest.approx(cz.infidelity_static_scale(rel_error), rel=2e-3)


def test_static_offset_not_removed_by_reoptimising_z():
    """The J-scale error is a pure conditional phase, so virtual-Z re-calibration cannot remove it."""
    w, dt = rc(50e-9, 5e-12)
    amp, _, z_nominal = cz.calibrate_amplitude(w, 10e9, dt, pulses.cz_amplitude(50e-9))
    f_fixed = cz.pulse_fidelity(w, amp * 1.03, 10e9, dt, z_nominal)
    f_opt = cz.pulse_fidelity(w, amp * 1.03, 10e9, dt, "optimal")
    assert f_opt == pytest.approx(f_fixed, abs=1e-8)


def test_barrier_offset_through_exponential_exchange():
    """A barrier-voltage offset dv scales J by 10**(s dv): check the full chain V -> J -> F."""
    ex = ExponentialExchange(s_dec_per_v=10.0, j_ref_hz=1e6, v_ref=0.0)
    w, dt = rc(50e-9, 5e-12)
    amp, _, z_nominal = cz.calibrate_amplitude(w, 10e9, dt, pulses.cz_amplitude(50e-9))
    v = ex.v_of_j(amp * w + 1e-30)          # barrier waveform for the nominal J(t)
    dv = 1e-3
    j_err = ex.j_of_v(v + dv)
    sim = 1 - cz.cz_fidelity(cz.propagate_block(j_err, 10e9, dt), z_nominal)
    assert sim == pytest.approx(cz.infidelity_static_scale(ex.relative_error(dv)), rel=2e-3)


def test_fast_propagator_agrees_with_qutip():
    """The exact-step 2x2 propagator against QuTiP's ODE solver on a smooth pulse."""
    t_gate, d_ez = 30e-9, 100e6
    amp = pulses.cz_amplitude(t_gate)
    w, dt = rc(t_gate, 1e-12)
    u_fast = cz.full_unitary(cz.propagate_block(amp * w, d_ez, dt))
    u_ref = cz.propagate_qutip(lambda t: amp * (1 - np.cos(2 * np.pi * t / t_gate)), d_ez, t_gate)
    assert np.max(np.abs(u_fast - u_ref)) < 1e-6
    f_fast = cz.cz_fidelity(u_fast[1:3, 1:3])
    f_ref = cz.cz_fidelity(u_ref[1:3, 1:3])
    assert f_fast == pytest.approx(f_ref, abs=1e-9)


@pytest.mark.parametrize("t_gate", [25e-9, 30e-9, 40e-9, 50e-9])
def test_nonadiabatic_error_matches_polat_eq8(t_gate):
    """Calibrated raised-cosine CZ at dEz = 100 MHz against Polat 2026 Eq. 8 (with 1 - F = 2 eps / 5).
    Polat's Fig. 2 shows the two agree for gates longer than ~20 ns; we require within 30 %."""
    w, dt = rc(t_gate, 1e-12)
    amp, fid, _ = cz.calibrate_amplitude(w, 100e6, dt, pulses.cz_amplitude(t_gate))
    analytic = cz.infidelity_nonadiabatic(amp * w, 100e6, dt)
    assert (1 - fid) == pytest.approx(analytic, rel=0.3)


def test_exchange_map_round_trip():
    ex = ExponentialExchange(33.69, 50e3, 0.9)
    j = np.array([50e3, 1e6, 20e6])
    assert np.allclose(ex.j_of_v(ex.v_of_j(j)), j, rtol=1e-12)
    assert ex.relative_error(1 / 33.69) == pytest.approx(9.0)
