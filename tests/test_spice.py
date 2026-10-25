"""Circuit-side tests: SKY130 port, trimmed library, simulator cross-check,
and the end-to-end SPICE -> J -> fidelity pipeline."""
import numpy as np
import pytest

from conftest import needs_ltspice, needs_spice
from flow import benches, cz, pipeline, spice

WORK = "build/tests"


def _at(w, name, t):
    return float(np.interp(t, w["time"], w[name]))


@needs_spice
def test_sky130_cells_switch_rail_to_rail():
    w = spice.run_ngspice(benches.cell_check(), WORK, "cells")
    # (time, a, b) -> expected INV, NAND2
    for t, a, b in [(5e-9, 0, 0), (30e-9, 1, 0), (50e-9, 1, 1), (70e-9, 0, 1)]:
        inv = _at(w, "v(inv_out)", t)
        nand = _at(w, "v(nand_out)", t)
        assert abs(inv - 1.8 * (1 - a)) < 0.01
        assert abs(nand - 1.8 * (1 - a * b)) < 0.01
    assert abs(_at(w, "v(tg_out)", 50e-9) - 0.9) < 1e-3     # TG on passes the mid-rail input


@needs_spice
@pytest.mark.slow
def test_trimmed_library_matches_full_pdk_library():
    fast = spice.run_ngspice(benches.sample_and_hold(), WORK, "sh_trim")
    full = spice.run_ngspice(benches.sample_and_hold(full_lib=True), WORK, "sh_full")
    for t in (15e-9, 30e-9, 110e-9):
        assert _at(fast, "v(hold)", t) == pytest.approx(_at(full, "v(hold)", t), abs=1e-6)


@needs_spice
def test_tg_pedestal_is_physical():
    """A minimum-length TG on 50 fF must give a pedestal of order mV, not zero (LEVEL=1 gave none)."""
    w = spice.run_ngspice(benches.sample_and_hold(), WORK, "sh_ped")
    pedestal = _at(w, "v(hold)", 60e-9) - 0.9
    assert 0.1e-3 < abs(pedestal) < 20e-3


@needs_spice
@needs_ltspice
def test_ngspice_and_ltspice_agree_on_switch_transient():
    """Plan test 3: two simulators, one explicit BSIM4 card, same switch transient."""
    a = spice.run_ngspice(benches.crosscheck_switch("ngspice"), WORK, "xc_ng")
    b = spice.run_ltspice(benches.crosscheck_switch("ltspice"), WORK, "xc_lt")
    tg = np.linspace(0, 60e-9, 6001)
    va = np.interp(tg, a["time"], a["v(hold)"])
    vb = np.interp(tg, b["time"], b["v(hold)"])
    ped_a, ped_b = va[-1] - 0.6, vb[-1] - 0.6
    assert abs(ped_a) > 1e-3                                  # there is a pedestal to compare
    assert ped_a == pytest.approx(ped_b, rel=0.01)            # pedestal within 1 %
    assert np.max(np.abs(va - vb)) < 1e-3                     # waveform within 1 mV everywhere


@needs_spice
def test_pipeline_end_to_end():
    """SPICE gate waveform -> J -> fidelity. The as-built error must match the analytic static-offset
    prediction from the measured pedestal, and re-calibration must recover the ideal fidelity."""
    r = pipeline.run(pipeline.PipelineConfig(workdir=WORK + "/pipeline"))
    cfg = r["config"]
    assert 1 - r["fidelity_ideal"] < 1e-6
    dv = np.mean(r["v_gate"] - (cfg.v_bias + np.log10(r["j_target"] / cfg.j_idle) / cfg.s_dec_per_v))
    predicted = cz.infidelity_static_scale(10 ** (cfg.s_dec_per_v * dv) - 1)
    assert (1 - r["fidelity_as_built"]) == pytest.approx(predicted, rel=0.15)
    assert 1 - r["fidelity_recal"] < 1e-6
