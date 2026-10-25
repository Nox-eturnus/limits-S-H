"""End-to-end flow: SPICE barrier-gate waveform -> J(t) -> CZ fidelity.

Circuit (the charge-locked cell of Pauka 2021 / Bartee 2025, on SKY130):
a TG samples the DAC bias v_bias onto the gate node, then opens (pedestal). The CZ pulse is applied
by driving the bottom plate of C_PULSE, so the floating gate moves by k * v_drive with
k ~ C_PULSE / (C_PULSE + C_GATE + switch parasitics). The drive waveform is pre-distorted for the
exponential J(V) (Xue 2022), using k measured from a calibration run.

Three fidelities are reported:
  ideal      target J(t), amplitude and Z angles calibrated on it;
  as_built   SPICE J(t) with the amplitude and Z angles of the ideal pulse (error appears after
             calibration: this is what the paper budgets);
  recal      SPICE J(t) with amplitude and Z angles re-calibrated on it (a static pedestal is
             removable this way; dynamic errors are not).
"""
from dataclasses import dataclass, field

import numpy as np

from . import benches, cz, pulses, spice
from .exchange import ExponentialExchange


@dataclass
class PipelineConfig:
    # qubit and exchange
    d_ez: float = 100e6          # Zeeman difference (Hz)
    t_gate: float = 50e-9        # CZ duration (s)
    s_dec_per_v: float = 10.0    # exchange tunability (dec/V), mid-range of published devices
    j_idle: float = 50e3         # residual exchange at the bias point (Xue 2022: 20-100 kHz)
    dt_qubit: float = 2e-12
    # circuit
    v_bias: float = 0.9
    c_gate: float = 50e-15       # gate electrode + interconnect (about 50 fF per gate)
    c_pulse: float = 50e-15
    wn: float = 1.0
    wp: float = 2.0
    t_edge: float = 200e-12
    t_open: float = 10e-9        # switch opens
    t_start: float = 30e-9       # CZ pulse starts
    corner: str = "tt"
    temp: float = 27
    workdir: str = "build/pipeline"
    extra: dict = field(default_factory=dict)


def _pwl(times, values):
    pts = " ".join(f"{t:.6e} {v:.6e}" for t, v in zip(times, values))
    # wrap long lines with SPICE continuation
    words, lines, cur = pts.split(" "), [], []
    for i in range(0, len(words), 2):
        cur.append(words[i] + " " + words[i + 1])
        if len(cur) == 8:
            lines.append(" ".join(cur))
            cur = []
    if cur:
        lines.append(" ".join(cur))
    return "PWL(" + "\n+ ".join(lines) + ")"


def charge_lock_deck(cfg, drive_times, drive_values, t_stop):
    return benches._header("Charge-locked barrier gate with capacitive CZ pulse", cfg.corner, cfg.temp) + f"""
VDD vdd 0 1.8
VBIAS vbias 0 {cfg.v_bias}
RSRC vbias src 50
VEN en 0 PULSE(0 1.8 1n {cfg.t_edge} {cfg.t_edge} {cfg.t_open - 1e-9 - cfg.t_edge} 1)
VENB enb 0 PULSE(1.8 0 1n {cfg.t_edge} {cfg.t_edge} {cfg.t_open - 1e-9 - cfg.t_edge} 1)
XSW src gate en enb vdd 0 TG wn={cfg.wn} wp={cfg.wp} l=0.15
CGATE gate 0 {cfg.c_gate}
CPULSE drive gate {cfg.c_pulse}
VDRIVE drive 0 {_pwl(drive_times, drive_values)}
.save v(gate) v(drive)
.tran 5p {t_stop}
.end
"""


def measure_coupling(cfg, step=0.1):
    """Coupling ratio k = dV_gate / dV_drive of the floating gate, from a step on the drive."""
    t_step = cfg.t_start
    times = [0.0, t_step, t_step + 100e-12, t_step + 10e-9]
    vals = [0.0, 0.0, step, step]
    w = spice.run_ngspice(charge_lock_deck(cfg, times, vals, t_step + 10e-9), cfg.workdir, "coupling")
    t, v = w["time"], w["v(gate)"]
    before = np.interp(t_step - 1e-9, t, v)
    after = np.interp(t_step + 9e-9, t, v)
    pedestal = before - cfg.v_bias
    return (after - before) / step, pedestal


def run(cfg=None):
    cfg = cfg or PipelineConfig()
    ex = ExponentialExchange(cfg.s_dec_per_v, cfg.j_idle, cfg.v_bias)

    # 1. ideal target: J = j_idle + A * raised_cosine, calibrated for a CZ
    t, dt = pulses.time_grid(cfg.t_gate, cfg.dt_qubit)
    w = pulses.raised_cosine(t, cfg.t_gate)
    amp, f_ideal, z_ideal = cz.calibrate_amplitude(
        w, cfg.d_ez, dt, pulses.cz_amplitude(cfg.t_gate))
    # Re-solve with the idle floor included in the shape: J_target = j_idle + amp_eff * w
    amp_eff, f_ideal, z_ideal = _calibrate_with_floor(w, cfg.j_idle, cfg.d_ez, dt, amp)
    j_target = cfg.j_idle + amp_eff * w
    dv_target = ex.v_of_j(j_target) - cfg.v_bias

    # 2. coupling ratio and pre-distorted drive
    k, pedestal = measure_coupling(cfg)
    # The drive is smooth, so a 20 ps PWL grid is enough (the qubit grid is much finer).
    t_drv = np.linspace(0.0, cfg.t_gate, int(round(cfg.t_gate / 20e-12)) + 1)
    dv_drv = ex.v_of_j(cfg.j_idle + amp_eff * pulses.raised_cosine(t_drv, cfg.t_gate)) - cfg.v_bias
    drive_t = np.concatenate([[0.0], cfg.t_start + t_drv, [cfg.t_start + cfg.t_gate + 1e-9]])
    drive_v = np.concatenate([[0.0], dv_drv / k, [0.0]])
    t_stop = cfg.t_start + cfg.t_gate + 5e-9
    wv = spice.run_ngspice(charge_lock_deck(cfg, drive_t, drive_v, t_stop), cfg.workdir, "cz_pulse")

    # 3. SPICE gate voltage on the qubit time grid -> J(t)
    v_gate = np.interp(cfg.t_start + t, wv["time"], wv["v(gate)"])
    j_spice = ex.j_of_v(v_gate)
    block = cz.propagate_block(j_spice, cfg.d_ez, dt)
    f_as_built = cz.cz_fidelity(block, z_ideal)
    scale, f_recal, _ = cz.calibrate_amplitude(j_spice, cfg.d_ez, dt, 1.0, span=0.5)

    return {
        "fidelity_ideal": f_ideal,
        "fidelity_as_built": f_as_built,
        "fidelity_recal": f_recal,
        "recal_scale": scale,
        "pedestal_v": float(pedestal),
        "coupling_k": float(k),
        "dv_peak_v": float(dv_target.max()),
        "j_peak_hz": float(j_target.max()),
        "t": t, "j_target": j_target, "j_spice": j_spice, "v_gate": v_gate,
        "config": cfg,
    }


def _calibrate_with_floor(w, j_floor, d_ez, dt, guess):
    from scipy.optimize import minimize_scalar
    res = minimize_scalar(lambda a: 1 - cz.pulse_fidelity(j_floor / a + w, a, d_ez, dt) if a > 0 else 1,
                          bounds=(guess * 0.7, guess * 1.3), method="bounded",
                          options={"xatol": guess * 1e-12})
    a = float(res.x)
    block = cz.propagate_block(j_floor + a * w, d_ez, dt)
    z = cz.optimal_z_angles(block)
    return a, cz.cz_fidelity(block, z), z
