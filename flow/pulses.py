"""Exchange pulse shapes J(t) on a uniform time grid.

Window definitions follow Polat 2026, Appendix A. All windows are normalised to unit mean over the
gate, so `amplitude * window` has integral `amplitude * t_gate`.
"""
import numpy as np


def time_grid(t_gate, dt):
    """Midpoints of n equal steps covering [0, t_gate]; returns (t_mid, dt_actual)."""
    n = max(int(np.ceil(t_gate / dt)), 1)
    step = t_gate / n
    return (np.arange(n) + 0.5) * step, step


def raised_cosine(t, t_gate):
    """w(t) = 1 - cos(2 pi t / t_gate) on [0, t_gate]; mean 1 (Polat 2026, Eq. A2 normalised)."""
    t = np.asarray(t, dtype=float)
    w = 1.0 - np.cos(2.0 * np.pi * t / t_gate)
    return np.where((t >= 0) & (t <= t_gate), w, 0.0)


def square(t, t_gate):
    t = np.asarray(t, dtype=float)
    return np.where((t >= 0) & (t <= t_gate), 1.0, 0.0)


def cz_amplitude(t_gate):
    """Mean J for a CZ in the J << dEz limit: integral of J dt = 1/2 (Polat 2026, Eq. 6)."""
    return 0.5 / t_gate


def zero_order_hold(t, t_gate, f_samp, shape=raised_cosine):
    """Shape sampled at f_samp and held (ZOH), as from a DAC (Polat 2026, Sec. II F).

    Samples are taken at the start of each sample period, k / f_samp, which matches Polat's
    Eq. 20 aliasing picture (sinc envelope with images at k * f_samp).
    """
    t = np.asarray(t, dtype=float)
    k = np.floor(t * f_samp)
    return shape(k / f_samp, t_gate) * ((t >= 0) & (t <= t_gate))
