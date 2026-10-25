"""Two-spin exchange gate: propagation, CZ fidelity, and analytic error formulas.

Hamiltonian (Polat 2026, Eq. 2; units of Hz, basis |00>, |01>, |10>, |11>), with the average
Zeeman term dropped because it is a local Z rotation that the virtual-Z correction absorbs:

    H = diag(0, B, 0),   B = [[(-dEz - J)/2,  J/2         ],
                              [ J/2,          (dEz - J)/2 ]]

|00> and |11> do not evolve, so only the 2x2 block B is propagated. For piecewise-constant J the
block propagator of every time step is exact (closed-form SU(2) exponential), and the steps are
multiplied with a pairwise tree reduction. Accuracy is therefore set only by how finely J(t) is
sampled; the QuTiP reference in `propagate_qutip` checks this independently.

Fidelity is the average gate fidelity F = (d + |Tr(V^dag U)|^2) / (d (d + 1)), d = 4 (Polat 2026,
Eq. B4), against V = CZ . diag(1, e^{i b}, e^{i a}, e^{i (a + b)}), i.e. CZ up to single-qubit
Z rotations (virtual-Z gates). Two choices for the Z angles:

* 'optimal': maximise F over (a, b), as for a gate calibrated on this very pulse;
* fixed (a, b): Z angles calibrated on a nominal pulse and kept, as for an error that appears
  after calibration (drift, droop, refresh scatter). This is the case the paper budgets.
"""
import numpy as np
from scipy.optimize import minimize, minimize_scalar

TWO_PI = 2.0 * np.pi


# ------------------------------------------------------------------------------------ propagation

def block_steps(j, d_ez, dt):
    """Exact propagators exp(-i 2 pi B_k dt) for each sample J_k; shape (n, 2, 2).

    d_ez and dt may be scalars or arrays matching j (time-dependent Zeeman difference, as from a
    Stark shift; non-uniform steps, as for a long idle segment).
    """
    j = np.asarray(j, dtype=float)
    # B = -J/2 I + (-dEz/2) sz + (J/2) sx  =  c0 I + r (n . sigma)
    c0 = -0.5 * j
    hz = -0.5 * d_ez * np.ones_like(j)
    hx = 0.5 * j
    r = np.hypot(hz, hx)
    phi = TWO_PI * r * dt
    cos_p, sin_p = np.cos(phi), np.sin(phi)
    with np.errstate(invalid="ignore", divide="ignore"):
        nz = np.where(r > 0, hz / r, 0.0)
        nx = np.where(r > 0, hx / r, 0.0)
    glob = np.exp(-1j * TWO_PI * c0 * dt)
    u = np.empty((j.size, 2, 2), dtype=complex)
    u[:, 0, 0] = glob * (cos_p - 1j * sin_p * nz)
    u[:, 1, 1] = glob * (cos_p + 1j * sin_p * nz)
    u[:, 0, 1] = glob * (-1j * sin_p * nx)
    u[:, 1, 0] = u[:, 0, 1]
    return u


def ordered_product(mats):
    """mats[n-1] @ ... @ mats[1] @ mats[0] by pairwise reduction (time order: index 0 first)."""
    m = np.asarray(mats)
    while m.shape[0] > 1:
        if m.shape[0] % 2:
            m = np.concatenate([m, np.eye(m.shape[1], dtype=m.dtype)[None]], axis=0)
        m = m[1::2] @ m[0::2]
    return m[0]


def propagate_block(j, d_ez, dt):
    """2x2 block propagator for the exchange waveform samples j (Hz), step dt (s)."""
    return ordered_product(block_steps(j, d_ez, dt))


def full_unitary(block):
    u = np.eye(4, dtype=complex)
    u[1:3, 1:3] = block
    return u


def propagate_qutip(j_of_t, d_ez, t_gate, n_eval=2001, atol=1e-12, rtol=1e-10):
    """Reference propagator from QuTiP's ODE solver, for a callable J(t). Returns the 4x4 unitary."""
    import qutip

    h0 = np.zeros((4, 4))
    h0[1, 1], h0[2, 2] = -d_ez / 2, d_ez / 2
    h1 = np.zeros((4, 4))
    h1[1, 1] = h1[2, 2] = -0.5
    h1[1, 2] = h1[2, 1] = 0.5
    H = [qutip.Qobj(TWO_PI * h0), [qutip.Qobj(TWO_PI * h1), lambda t: j_of_t(t)]]
    tlist = np.linspace(0.0, t_gate, n_eval)
    opts = {"atol": atol, "rtol": rtol, "max_step": t_gate / 400}
    u = qutip.propagator(H, tlist, options=opts)[-1]
    return np.asarray(u.full())


# ------------------------------------------------------------------------------------ fidelity

def _trace_overlap(block, a, b, theta00=0.0, theta11=0.0):
    """Tr(V^dag U) for U = diag(e^{i theta00}, block, e^{i theta11}),
    V = CZ . diag(1, e^{ib}, e^{ia}, e^{i(a+b)}).

    theta00 and theta11 are the phases of |00> and |11>; they are zero unless the average Zeeman
    energy changes during the gate (Stark shift, flow/budget.py)."""
    return (np.exp(1j * theta00) + np.exp(-1j * b) * block[0, 0] + np.exp(-1j * a) * block[1, 1]
            - np.exp(-1j * (a + b)) * np.exp(1j * theta11))


def _fidelity_from_overlap(tr, d=4):
    return (d + np.abs(tr) ** 2) / (d * (d + 1))


def optimal_z_angles(block, theta00=0.0, theta11=0.0):
    """Single-qubit Z angles (a, b) that maximise the CZ fidelity of this block."""
    a0, b0 = np.angle(block[1, 1]) - theta00, np.angle(block[0, 0]) - theta00
    res = minimize(lambda x: -np.abs(_trace_overlap(block, x[0], x[1], theta00, theta11)), [a0, b0],
                   method="Nelder-Mead", options={"xatol": 1e-12, "fatol": 1e-15, "maxiter": 4000})
    return tuple(res.x)


def cz_fidelity(block, z_angles="optimal", theta00=0.0, theta11=0.0):
    """Average gate fidelity of diag(e^{i theta00}, block, e^{i theta11}) to CZ up to Z rotations.

    z_angles: 'optimal' or a fixed pair (a, b) from `optimal_z_angles` of a nominal pulse.
    """
    a, b = optimal_z_angles(block, theta00, theta11) if isinstance(z_angles, str) else z_angles
    return float(_fidelity_from_overlap(_trace_overlap(block, a, b, theta00, theta11)))


def pulse_fidelity(shape_samples, amplitude, d_ez, dt, z_angles="optimal"):
    return cz_fidelity(propagate_block(amplitude * np.asarray(shape_samples), d_ez, dt), z_angles)


def calibrate_amplitude(shape_samples, d_ez, dt, guess, span=0.3):
    """Amplitude that maximises the CZ fidelity of `amplitude * shape` (Polat 2026, Fig. 1-2).

    Searches guess * (1 +- span). Returns (amplitude, fidelity, z_angles).
    """
    shape_samples = np.asarray(shape_samples, dtype=float)
    res = minimize_scalar(lambda a: 1.0 - pulse_fidelity(shape_samples, a, d_ez, dt),
                          bounds=(guess * (1 - span), guess * (1 + span)), method="bounded",
                          options={"xatol": guess * 1e-12})
    amp = float(res.x)
    block = propagate_block(amp * shape_samples, d_ez, dt)
    angles = optimal_z_angles(block)
    return amp, cz_fidelity(block, angles), angles


# ------------------------------------------------------------------------------------ analytic

def infidelity_static_scale(rel_error):
    """Infidelity when J is scaled by (1 + e), adiabatic limit, Z angles from the nominal pulse.

    The block phases of |01> and |10> each gain pi e / 2. With delta = pi e the conditional-phase
    error, |Tr|^2 = 8 + 8 cos(delta / 2), so 1 - F = 0.4 (1 - cos(delta / 2)) ~ 0.05 delta^2.
    Re-optimising the Z angles does not help: the error is a pure conditional phase.
    """
    delta = np.pi * np.asarray(rel_error, dtype=float)
    return 0.4 * (1.0 - np.cos(delta / 2.0))


def infidelity_nonadiabatic(j, d_ez, dt):
    """Leading-order non-adiabatic error, 1 - F ~ (2/5) eps (Polat 2026, Eqs. 8, 12 and C11).

    eps = | integral (dEz / 2) (dJ/dt) / f_osc^2  exp(-i 2 pi integral f_osc dt') dt |^2,
    f_osc = sqrt(dEz^2 + J^2). Assumes J(0) = J(t_gate) = 0 and J << dEz is not required.
    """
    j = np.asarray(j, dtype=float)
    jdot = np.gradient(j, dt)
    f_osc = np.hypot(d_ez, j)
    phase = TWO_PI * (np.cumsum(f_osc) - 0.5 * f_osc) * dt
    amp = np.sum(0.5 * d_ez * jdot / f_osc ** 2 * np.exp(-1j * phase)) * dt
    return 0.4 * np.abs(amp) ** 2
