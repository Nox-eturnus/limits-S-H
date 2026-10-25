"""Map a barrier-gate voltage waveform to an exchange waveform J(t).

Model: J is exponential in the barrier voltage near the
operating point,

    J(V) = J_ref * 10 ** (s * (V - V_ref))

with s the exchange tunability in decades per volt (4-34 dec/V across Park 2026, Nickl 2025,
Jirovec 2025) and J_ref the exchange at the reference voltage V_ref. The single exponential is valid
over roughly 1-10 MHz (Park 2026); outside that range treat results as extrapolation.
"""
import numpy as np


class ExponentialExchange:
    def __init__(self, s_dec_per_v, j_ref_hz, v_ref):
        self.s = float(s_dec_per_v)
        self.j_ref = float(j_ref_hz)
        self.v_ref = float(v_ref)

    def j_of_v(self, v):
        return self.j_ref * 10.0 ** (self.s * (np.asarray(v, dtype=float) - self.v_ref))

    def v_of_j(self, j):
        """Inverse map: the barrier voltage that gives exchange j (j > 0)."""
        return self.v_ref + np.log10(np.asarray(j, dtype=float) / self.j_ref) / self.s

    def relative_error(self, dv):
        """Fractional change of J caused by a barrier-voltage error dv: 10**(s dv) - 1."""
        return 10.0 ** (self.s * np.asarray(dv, dtype=float)) - 1.0


def barrier_pulse_for(j_target, exchange, j_floor):
    """Barrier waveform that produces j_target(t), as in Xue 2022 (pre-distorted for the exponential).

    j_floor is the residual exchange at idle (Xue 2022: 20-100 kHz); J never goes below it, because
    the barrier cannot be raised without limit.
    """
    j = np.maximum(np.asarray(j_target, dtype=float), j_floor)
    return exchange.v_of_j(j)
