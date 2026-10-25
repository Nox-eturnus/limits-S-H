"""Tests of the cryogenic proxy on the SKY130 FET models (flow/pdk.py, cryo=(dV_T, mu))."""
from pathlib import Path

import numpy as np
import pytest

from conftest import needs_spice
from flow import holdstage as H
from flow import spice
from flow.pdk import fet18_lib_line, write_fet18_lib

WORK = "build/tests/cryo"


def _id_vg(cryo, name="sky130_fd_pr__nfet_01v8", w=1, l=0.15, sgn=1, vdd=1.8):
    deck = f"""* proxy check
{fet18_lib_line("tt", "hold", False, cryo)}
VG g 0 PWL(0 0 1u {sgn * vdd})
VD d 0 {sgn * 0.05}
XM d g 0 0 {name} w={w} l={l}
.tran 1n 1u
.save i(vd)
.end
"""
    tag = "none" if cryo is None else f"{cryo[0]:g}_{cryo[1]:g}"
    wv = spice.run_ngspice(deck, WORK, f"{name}_{tag}")
    return wv["time"] / 1e-6 * vdd, np.abs(wv["i(vd)"])


def test_no_cryo_leaves_the_library_unchanged():
    assert write_fet18_lib("tt", "hold") == write_fet18_lib("tt", "hold", cryo=None)
    assert "cryo" not in H.HoldConfig().tag()


def test_proxy_rewrites_every_bin():
    lib = write_fet18_lib("tt", "hold", cryo=(0.15, 2.0)).read_text()
    pm3 = [ln.split('"')[1] for ln in lib.splitlines() if "nfet_01v8__tt.pm3" in ln][0]
    text = open(pm3).read()
    n_bins = text.count(".model ")
    assert text.count(") + 0.15}") >= n_bins            # vth0 shifted in every nmos bin
    assert " * 2}" in text


@needs_spice
@pytest.mark.parametrize("name,w,l,sgn,vdd", [("sky130_fd_pr__nfet_01v8", 1, 0.15, 1, 1.8),
                                              ("sky130_fd_pr__pfet_01v8", 2, 0.15, -1, 1.8)])
def test_proxy_raises_threshold_and_on_current(name, w, l, sgn, vdd):
    """Constant-current V_T rises by most of dV_T (the mobility gain offsets part of it), and the
    on-current at full gate drive rises with the mobility."""
    vg0, i0 = _id_vg(None, name, w, l, sgn, vdd)
    vg1, i1 = _id_vg((0.15, 2.0), name, w, l, sgn, vdd)
    icrit = 1e-7 * w / l
    dvt = np.interp(icrit, i1, vg1) - np.interp(icrit, i0, vg0)
    assert 0.07 < dvt < 0.15
    assert i1[-1] > 1.2 * i0[-1]


@needs_spice
def test_bootstrapped_switch_keeps_its_range_under_the_proxy():
    """The bootstrap gate drive follows the source, so a raised V_T does not cut the passed range."""
    _, m, _ = H.run(arch="BOOT", wn=0.42, esd_area=0.0, v_underdrive=0.3, cryo=(0.20, 2.0), workdir=WORK)
    assert np.max(np.abs(m["track_error"])) < 0.1e-3


def test_mismatch_scale_and_separate_pmos_shift_are_applied():
    lib = write_fet18_lib("tt", "hold", True, cryo=(0.15, 2.0, 2.0, 0.8, 3.0)).read_text()
    paths = [ln.split('"')[1] for ln in lib.splitlines() if ln.startswith(".include")]
    mm = open(next(p for p in paths if "nfet_01v8__mismatch" in p)).read()
    assert "sky130_fd_pr__nfet_01v8__vth0_slope=0.006712" in mm.replace(" ", "")      # 3.356e-3 x 2
    pfet = open(next(p for p in paths if "pfet_01v8__tt" in p)).read()
    pm3 = pfet if ".model" in pfet else open(next(
        str(Path(p).parent / "sky130_fd_pr__pfet_01v8__tt.pm3.spice") for p in paths if "pfet_01v8__tt" in p)).read()
    assert ") - 0.8}" in pm3 and " * 3}" in pm3


@needs_spice
def test_transistor_level_bootstrap_matches_the_behavioural_one():
    """BOOTT (bootstrap capacitor, thick-oxide network) passes the full range and has the same droop
    as the behavioural BOOT: both are set by the main switch's drain junction."""
    kw = dict(wn=0.42, esd_area=0.0, v_underdrive=0.3, workdir=WORK)
    _, m, s = H.run(arch="BOOTT", **kw)
    _, _, sb = H.run(arch="BOOT", **kw)
    assert np.max(np.abs(m["track_error"])) < 0.1e-3
    assert s["droop_max"] == pytest.approx(sb["droop_max"], rel=0.1)
    assert s["pedestal_linear_residual"] < 20e-6
