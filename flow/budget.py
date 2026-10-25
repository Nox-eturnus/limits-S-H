"""Error budget: CZ fidelity against barrier-voltage errors left after calibration.

One *CZ layer* is an adiabatic raised-cosine CZ pulse of length t_gate followed by an optional idle
segment t_idle at the residual exchange J_idle. The barrier voltage is

    V(t) = V0(t) + dv(t)

with V0 the nominal pulse (pre-distorted for the exponential J(V), Xue 2022) and dv the error.
V is measured from the idle bias point, so V0 = 0 at idle. The voltage acts on the qubits through:

* exchange:  J(V) = J_idle * 10 ** (s V)            (flow/exchange.py)
* Stark:     E_Z1 -> E_Z1 + a1 V,  E_Z2 -> E_Z2 + a2 V   (Bartee 2025: ~1 MHz per 10 mV, a = 1e8 Hz/V)

so dEz(t) = dEz + (a2 - a1) V and the mean Zeeman energy moves by (a1 + a2) V / 2. In the frame of
the idle qubit frequencies the Hamiltonian is diag(Ez_avg(t), B(t), -Ez_avg(t)) with B as in
flow/cz.py.

Calibration (amplitude and single-qubit Z angles) is done once on the nominal pulse, with the Stark
shift of the nominal pulse included, and then kept fixed: dv is an error that appears after
calibration (drift, droop, refresh scatter, noise). This is the case the paper budgets.

Three ways to evaluate the error:

* `CZLayer.infidelity(dv)`: exact numerics (piecewise-constant propagator, flow/cz.py).
* `CZLayer.infidelity_adiabatic(dv)`: adiabatic phase model. In the adiabatic limit each basis
  state only picks up a phase, theta_k = -2 pi integral E_k dt, with the instantaneous energies
  E_00 = Ez_avg, E_11 = -Ez_avg, E_01 = (-J - R)/2, E_10 = (-J + R)/2, R = sqrt(dEz^2 + J^2).
  With fixed Z angles, 1 - F = 1 - (4 + |sum_k exp(i dtheta_k)|^2) / 20, dtheta = theta(dv) -
  theta(0). Fast, and exact for slow errors.
* `CZLayer.noise_infidelity(psd)`: filter-function average over Gaussian voltage noise, from the
  linearised phases: E[1 - F] = (1/5) sum_k integral_0^inf S_V(f) |H_k(f)|^2 df, with H_k the
  Fourier transform of the projected sensitivity h_k(t) = g_k(t) - mean_k g_k(t),
  g_k(t) = d theta_k / d V(t). S_V is one-sided (V^2/Hz).

Small-angle form: 1 - F = (1/5) sum_k (dtheta_k - mean dtheta)^2. A pure
conditional-phase error delta (dtheta = (0, d/2, d/2, 0)) gives 0.05 delta^2; a Z error phi on one
qubit gives 0.2 phi^2; the two patterns are orthogonal, so their infidelities add.
"""
from dataclasses import dataclass, replace

import numpy as np
from scipy.optimize import brentq, minimize_scalar

from . import cz, pulses
from .exchange import ExponentialExchange

TWO_PI = 2.0 * np.pi
LN10 = np.log(10.0)
STARK_BARTEE = 1e8          # Hz/V: ~1 MHz per 10 mV on Q2 (Bartee 2025, exchange-gate voltage)


@dataclass(frozen=True)
class LayerConfig:
    s_dec_per_v: float = 10.0     # exchange tunability (published devices: 4-34 dec/V)
    j_idle: float = 50e3          # residual exchange at idle (Xue 2022: 20-100 kHz)
    d_ez: float = 100e6           # Zeeman difference (Hz)
    t_gate: float = 50e-9         # CZ duration (s)
    t_idle: float = 0.0           # idle time after the CZ, same barrier bias (s)
    stark_q1: float = 0.0         # Hz/V
    stark_q2: float = STARK_BARTEE
    dt: float = 5e-12             # step during the pulse
    dt_idle: float = 1e-9         # step during the idle segment


class CZLayer:
    def __init__(self, cfg=LayerConfig()):
        self.cfg = cfg
        self.ex = ExponentialExchange(cfg.s_dec_per_v, cfg.j_idle, 0.0)
        tg, self.dt_gate = pulses.time_grid(cfg.t_gate, cfg.dt)
        self.w = pulses.raised_cosine(tg, cfg.t_gate)
        n_i = int(np.ceil(cfg.t_idle / cfg.dt_idle)) if cfg.t_idle > 0 else 0
        dti = cfg.t_idle / n_i if n_i else 0.0
        ti = cfg.t_gate + (np.arange(n_i) + 0.5) * dti
        self.t = np.concatenate([tg, ti])
        self.dts = np.concatenate([np.full(tg.size, self.dt_gate), np.full(n_i, dti)])
        self.n_gate = tg.size
        self._calibrate()

    # ---------------------------------------------------------------- nominal pulse and calibration

    def _shape(self, amp):
        j = np.full(self.t.size, self.cfg.j_idle)
        j[:self.n_gate] += amp * self.w
        return j

    def _parts(self, v, n=None):
        """(block, theta00, theta11) for the barrier waveform v(t), over the first n steps."""
        c = self.cfg
        v, dts = v[:n], self.dts[:n]
        j = self.ex.j_of_v(v)
        d_ez = c.d_ez + (c.stark_q2 - c.stark_q1) * v
        ez_avg = 0.5 * (c.stark_q1 + c.stark_q2) * v
        block = cz.propagate_block(j, d_ez, dts)
        th = TWO_PI * np.sum(ez_avg * dts)
        return block, -th, th

    def _calibrate(self):
        """Amplitude and Z angles on the CZ pulse alone (idle segment excluded)."""
        guess = pulses.cz_amplitude(self.cfg.t_gate)
        n = self.n_gate

        def infid(a):
            block, t00, t11 = self._parts(self.ex.v_of_j(self._shape(a)), n)
            return 1.0 - cz.cz_fidelity(block, "optimal", t00, t11)

        res = minimize_scalar(infid, bounds=(guess * 0.6, guess * 1.4), method="bounded",
                              options={"xatol": guess * 1e-12})
        self.amp = float(res.x)
        self.j0 = self._shape(self.amp)
        self.v0 = self.ex.v_of_j(self.j0)
        block, t00, t11 = self._parts(self.v0, n)
        self.z = cz.optimal_z_angles(block, t00, t11)
        self.f_nominal = cz.cz_fidelity(block, self.z, t00, t11)
        self._u0 = self._parts(self.v0)
        self._theta0 = self._adiabatic_phases(self.v0)

    # ---------------------------------------------------------------- exact numerics

    def fidelity(self, dv, recalibrate_z=False):
        """Fidelity of the CZ pulse (idle segment excluded) to an ideal CZ, Z angles fixed."""
        dv = np.broadcast_to(np.asarray(dv, dtype=float), self.t.shape)
        block, t00, t11 = self._parts(self.v0 + dv, self.n_gate)
        return cz.cz_fidelity(block, "optimal" if recalibrate_z else self.z, t00, t11)

    def infidelity(self, dv, recalibrate_z=False):
        return 1.0 - self.fidelity(dv, recalibrate_z)

    def excess_infidelity(self, dv):
        """1 - F of the layer with error dv against the calibrated layer without it (Z fixed).

        This is the error that appears after calibration. The calibrated gate's own error and the
        nominal idle ZZ (2 pi J_idle t_idle, handled by echoes or compilation) are not counted."""
        dv = np.broadcast_to(np.asarray(dv, dtype=float), self.t.shape)
        block, t00, t11 = self._parts(self.v0 + dv)
        b0, s00, s11 = self._u0
        tr = (np.exp(1j * (t00 - s00)) + np.exp(1j * (t11 - s11))
              + np.trace(b0.conj().T @ block))
        return float(1.0 - (4.0 + np.abs(tr) ** 2) / 20.0)

    # ---------------------------------------------------------------- adiabatic phase model

    def _adiabatic_phases(self, v):
        c = self.cfg
        j = self.ex.j_of_v(v)
        d_ez = c.d_ez + (c.stark_q2 - c.stark_q1) * v
        ez_avg = 0.5 * (c.stark_q1 + c.stark_q2) * v
        r = np.hypot(d_ez, j)
        e = np.stack([ez_avg, 0.5 * (-j - r), 0.5 * (-j + r), -ez_avg])
        return -TWO_PI * np.sum(e * self.dts, axis=1)

    def phase_errors(self, dv):
        """Adiabatic phase errors (00, 01, 10, 11) caused by dv, in rad."""
        dv = np.broadcast_to(np.asarray(dv, dtype=float), self.t.shape)
        return self._adiabatic_phases(self.v0 + dv) - self._theta0

    def infidelity_adiabatic(self, dv):
        """Excess infidelity from the adiabatic phase model (compare with excess_infidelity)."""
        return phase_infidelity(self.phase_errors(dv))

    # ---------------------------------------------------------------- noise (filter functions)

    def sensitivities(self):
        """g_k(t) = d theta_k / d V(t) per unit time (rad / (V s)), shape (4, n)."""
        c = self.cfg
        j = self.j0
        dj = j * c.s_dec_per_v * LN10
        d_ez = c.d_ez + (c.stark_q2 - c.stark_q1) * self.v0
        r = np.hypot(d_ez, j)
        da = 0.5 * (c.stark_q1 + c.stark_q2)
        dd = c.stark_q2 - c.stark_q1
        de = np.stack([np.full_like(j, da),
                       0.5 * (-1 - j / r) * dj - 0.5 * d_ez / r * dd,
                       0.5 * (-1 + j / r) * dj + 0.5 * d_ez / r * dd,
                       np.full_like(j, -da)])
        return -TWO_PI * de

    def projected_sensitivities(self):
        g = self.sensitivities()
        return g - g.mean(axis=0)

    def transverse_sensitivity(self):
        """g_x(t) e^{i phi(t)}: |01> <-> |10> transition amplitude per volt per unit time.

        A barrier error tilts the exchange/Zeeman field of the |01>, |10> block; its component
        perpendicular to the instantaneous field, (dEz dJ - J d(dEz)) / (2R), drives transitions at
        the splitting R. First order: amplitude c = -i 2 pi integral (perp. coupling) e^{i phi} dt,
        phi = 2 pi integral R dt, and the infidelity is 0.4 |c|^2. Slow errors (static, 1/f) barely
        excite it; white noise near R does.
        """
        c = self.cfg
        j = self.j0
        d_ez = c.d_ez + (c.stark_q2 - c.stark_q1) * self.v0
        r = np.hypot(d_ez, j)
        gx = np.pi * j * (d_ez * c.s_dec_per_v * LN10 - (c.stark_q2 - c.stark_q1)) / r
        phi = TWO_PI * (np.cumsum(r * self.dts) - 0.5 * r * self.dts)
        return gx * np.exp(1j * phi)

    def kernel(self, f):
        """Infidelity kernel K(f) with E[1 - F] = integral_0^inf S_V(f) K(f) df (one-sided S_V).

        K = (1/5) sum_k |H_k(f)|^2 (phases) + 0.4 (|G(f)|^2 + |G(-f)|^2) / 2 (transitions).
        """
        h = self.projected_sensitivities()
        gx = self.transverse_sensitivity()
        f = np.atleast_1d(np.asarray(f, dtype=float))
        out = np.empty(f.size)
        for i0 in range(0, f.size, 64):
            fs = f[i0:i0 + 64]
            ph = np.exp(-1j * TWO_PI * np.outer(fs, self.t)) * self.dts      # (nf, n)
            hk = ph @ h.T                                                     # (nf, 4)
            gp = ph @ gx
            gm = ph.conj() @ gx
            out[i0:i0 + 64] = (np.sum(np.abs(hk) ** 2, axis=1) / 5.0
                               + 0.2 * (np.abs(gp) ** 2 + np.abs(gm) ** 2))
        return out

    def static_curvature(self):
        """c in 1 - F ~ c dv^2 for a small static dv (V^-2): K(0)."""
        return float(self.kernel([0.0])[0])

    def white_noise_infidelity(self, s_v, split=False):
        """E[1 - F] for white voltage noise of one-sided PSD s_v (V^2/Hz), by Parseval.

        Linear order; see `rectification` for the condition on the noise bandwidth. With
        split=True returns (phase part, transition part)."""
        h = self.projected_sensitivities()
        gx = self.transverse_sensitivity()
        ph = s_v * 0.5 * np.sum(h ** 2 * self.dts) / 5.0
        tr = s_v * 0.5 * 0.4 * np.sum(np.abs(gx) ** 2 * self.dts)
        return (float(ph), float(tr)) if split else float(ph + tr)

    def noise_infidelity(self, psd, f_lo, f_hi=None, n_f=600):
        """E[1 - F] for Gaussian noise with one-sided PSD psd(f) (V^2/Hz) on [f_lo, f_hi].

        Log-spaced quadrature. f_hi defaults to 2000 / t_gate, beyond which the kernel of the
        smooth pulse has decayed.
        """
        f_hi = f_hi or 2000.0 / self.cfg.t_gate
        lf = np.linspace(np.log(f_lo), np.log(f_hi), n_f)
        f = np.exp(lf)
        y = psd(f) * self.kernel(f) * f          # integrand in d(ln f)
        return float(np.trapezoid(y, lf))


def phase_infidelity(dtheta):
    """1 - F for diagonal phase errors dtheta (4,) with fixed Z angles (exact, not small-angle)."""
    return float(1.0 - (4.0 + np.abs(np.sum(np.exp(1j * np.asarray(dtheta)))) ** 2) / 20.0)


# ==================================================================================== error waveforms

def static(layer, dv):
    return np.full(layer.t.shape, float(dv))


def droop(layer, rate, t_since_refresh):
    """Linear droop: dv = rate * (t_since_refresh + t), t measured from the start of the layer."""
    return rate * (t_since_refresh + layer.t)


def glitch(layer, amp, tau, t_event=0.0):
    """Step-and-decay transient amp * exp(-(t - t_event) / tau) for t >= t_event, else 0.

    t_event is measured from the start of the CZ: t_event <= 0 is a refresh of this electrode just
    before the gate; 0 < t_event < t_gate is a transient during the gate, e.g. crosstalk from the
    refresh of another electrode on the same DAC line."""
    x = layer.t - t_event
    return np.where(x >= 0, amp * np.exp(-np.maximum(x, 0.0) / tau), 0.0)


def spectral_noise(layer, psd, f_lo, f_hi, rng, n_f=400):
    """Gaussian noise with one-sided PSD psd(f) on [f_lo, f_hi], as a sum of random-phase tones on a
    log-spaced grid (same quadrature as `CZLayer.noise_infidelity`)."""
    lf = np.linspace(np.log(f_lo), np.log(f_hi), n_f)
    f = np.exp(lf)
    df = np.gradient(lf) * f
    a = np.sqrt(psd(f) * df)
    x, y = rng.standard_normal((2, n_f))
    arg = TWO_PI * np.outer(layer.t, f)
    return np.cos(arg) @ (a * x) + np.sin(arg) @ (a * y)


def flat(s_v):
    """White PSD s_v (V^2/Hz); use with an explicit band in `spectral_noise`/`noise_infidelity`."""
    return lambda f: np.full_like(np.asarray(f, dtype=float), s_v)


def rectification(s_dec_per_v, sigma_v):
    """Mean relative J shift exp((s ln10 sigma)^2 / 2) - 1 from Gaussian noise of RMS sigma_v.

    The exponential J(V) turns voltage noise into a mean J offset. It is second order and absent
    from the filter-function result, which is valid while this shift is small compared with the
    static budget (or calibrated in the presence of the same noise). sigma_v is the in-band RMS,
    sqrt(S_V * bandwidth) for white noise.
    """
    return float(np.expm1(0.5 * (s_dec_per_v * LN10 * sigma_v) ** 2))


def one_over_f(a_1hz):
    """PSD a^2 / f, with a the noise amplitude at 1 Hz in V/sqrt(Hz)."""
    return lambda f: a_1hz ** 2 / f


# ==================================================================================== budget solvers

def _solve(fun, target, lo, hi):
    """Smallest x in [lo, hi] (log search) with fun(x) = target; fun increasing near the root."""
    xs = np.geomspace(lo, hi, 60)
    vals = np.array([fun(x) for x in xs])
    above = np.nonzero(vals >= target)[0]
    if above.size == 0:
        return np.inf
    i = above[0]
    if i == 0:
        return xs[0]
    return float(brentq(lambda x: fun(x) - target, xs[i - 1], xs[i], xtol=xs[i - 1] * 1e-6))


def max_static(layer, target, sign=+1, model="numeric"):
    """Largest |dv| (V) of one sign that keeps the excess infidelity at or below target."""
    f = layer.excess_infidelity if model == "numeric" else layer.infidelity_adiabatic
    return _solve(lambda x: f(static(layer, sign * x)), target, 1e-7, 0.2)


def max_static_rms(layer, target, n_nodes=40):
    """Largest RMS of a Gaussian static offset (refresh scatter, kT/C), adiabatic model."""
    x, w = np.polynomial.hermite_e.hermegauss(n_nodes)
    w = w / w.sum()

    def mean_inf(sig):
        return sum(wi * layer.infidelity_adiabatic(static(layer, sig * xi)) for xi, wi in zip(x, w))

    return _solve(mean_inf, target, 1e-7, 0.05)


def max_glitch(layer, target, tau, t_event=0.0, sign=+1, model="numeric"):
    f = layer.excess_infidelity if model == "numeric" else layer.infidelity_adiabatic
    return _solve(lambda a: f(glitch(layer, sign * a, tau, t_event)), target, 1e-6, 2.0)


def max_white(layer, target):
    """Largest white-noise density sqrt(S_V) (V/sqrt(Hz))."""
    return float(np.sqrt(target / layer.white_noise_infidelity(1.0)))


def max_one_over_f(layer, target, f_lo):
    """Largest 1/f amplitude at 1 Hz (V/sqrt(Hz)), noise below f_lo removed by recalibration."""
    return float(np.sqrt(target / layer.noise_infidelity(one_over_f(1.0), f_lo)))


def layer(**kw):
    return CZLayer(replace(LayerConfig(), **kw))
