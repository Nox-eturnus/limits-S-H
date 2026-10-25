"""SPICE testbench generators for the SKY130 flow.

Each function returns a netlist string; run it with flow.spice.run_ngspice and measure the
waveforms in Python (no .meas statements, so the same decks work in other simulators).
"""
from . import config
from .pdk import fet18_lib_line
from .spice import sky130_lib_line

CELLS = config.SPICE_DIR / "sky130_cells.lib"


def _header(title, corner="tt", temp=27, full_lib=False):
    """full_lib=True loads the whole PDK library (slow, ~45 s per run); the default trimmed library
    holds only the 1.8 V nfet/pfet models and gives identical results (tests/test_spice.py)."""
    lib = sky130_lib_line(corner) if full_lib else fet18_lib_line(corner)
    return (f"* {title}\n{lib}\n.include \"{CELLS.as_posix()}\"\n"
            f".temp {temp}\n.option method=gear reltol=1e-4\n")


def cell_check(vdd=1.8, corner="tt", full_lib=False):
    """INV, NAND2 and TG driven by one 10 MHz clock, to check the SKY130 port switches rail to rail."""
    return _header("SKY130 cell port check", corner, full_lib=full_lib) + f"""
VDD vdd 0 {vdd}
VA a 0 PULSE(0 {vdd} 10n 100p 100p 49.9n 100n)
VB b 0 PULSE(0 {vdd} 35n 100p 100p 49.9n 100n)
XINV a inv_out vdd 0 INV
XNAND a b nand_out vdd 0 NAND2
XINVB a ab vdd 0 INV
XTG vin tg_out a ab vdd 0 TG
VIN vin 0 {0.5 * vdd}
CINV inv_out 0 10f
CNAND nand_out 0 10f
CTG tg_out 0 10f
.save v(a) v(b) v(inv_out) v(nand_out) v(tg_out)
.tran 50p 200n
.end
"""


def sample_and_hold(v_in=0.9, c_hold=50e-15, wn=1.0, wp=2.0, l=0.15, switch="TG", t_edge=200e-12,
                    t_open=20e-9, t_stop=120e-9, vdd=1.8, corner="tt", temp=27, r_src=50.0,
                    full_lib=False):
    """Switch samples a DC source onto c_hold, then opens at t_open.

    Measures (in Python): pedestal = v(hold) after opening - v_in, and droop from the hold slope.
    switch: 'TG' (transmission gate) or 'NSW' (single NMOS). r_src models the DAC output resistance.
    """
    if switch == "TG":
        sw = f"XSW src hold en enb vdd 0 TG wn={wn} wp={wp} l={l}"
    elif switch == "NSW":
        sw = f"XSW src hold en 0 NSW wn={wn} l={l}"
    else:
        raise ValueError(switch)
    t_hi = t_open - 2e-9
    return _header(f"S/H {switch} pedestal and droop", corner, temp, full_lib) + f"""
VDD vdd 0 {vdd}
VIN vin 0 {v_in}
RSRC vin src {r_src}
* Switch closed from 1 ns to t_open; edges of t_edge.
VEN en 0 PULSE(0 {vdd} 1n {t_edge} {t_edge} {t_hi} 1)
VENB enb 0 PULSE({vdd} 0 1n {t_edge} {t_edge} {t_hi} 1)
{sw}
CHOLD hold 0 {c_hold}
.save v(hold) v(src) v(en)
.tran 10p {t_stop}
.end
"""


# A generic BSIM4 NMOS card for the simulator cross-check. Not a SKY130 model: LTspice cannot read
# the SKY130 library, so the cross-check compares the two simulators on one explicit card.
# ngspice selects BSIM4 with level=54, LTspice with level=14; the parameters are identical.
_BSIM4_PARAMS = ("version=4.5 binunit=1 capmod=2 toxe=4.1e-9 toxp=4.1e-9 toxm=4.1e-9 "
                 "vth0=0.45 k1=0.5 u0=0.03 vsat=8e4 rdsw=150 nfactor=1.2 "
                 "cgso=2.5e-10 cgdo=2.5e-10 cgbo=1e-12 xpart=0.5")


def crosscheck_switch(simulator, w=1e-6, l=0.15e-6, c_hold=50e-15, v_in=0.6, vdd=1.8, t_edge=200e-12):
    """NMOS sample-and-hold transient with an explicit BSIM4 card, for ngspice or LTspice."""
    level = {"ngspice": 54, "ltspice": 14}[simulator]
    # LTspice compresses saved waveforms by default; plotwinsize=0 and a 10 ps max step keep every point.
    tran = ".tran 10p 60n" if simulator == "ngspice" else ".options plotwinsize=0\n.tran 0 60n 0 10p"
    return f"""* BSIM4 switch transient, simulator cross-check ({simulator})
.model NBSIM nmos level={level} {_BSIM4_PARAMS}
VDD vdd 0 {vdd}
VIN vin 0 {v_in}
RSRC vin src 50
VEN en 0 PULSE(0 {vdd} 1n {t_edge} {t_edge} 18n 1)
M1 src en hold 0 NBSIM W={w} L={l}
CHOLD hold 0 {c_hold}
.save V(hold) V(en)
{tran}
.end
"""
