"""Reader for binary SPICE .raw files written by ngspice and LTspice.

ngspice writes an ASCII header and float64 for every variable.
LTspice writes a UTF-16 header, float64 for time and float32 for the other
traces (float64 throughout when the Flags line contains "double").
"""
import numpy as np


def read_raw(path):
    """Return {lower-case trace name: ndarray}, always including 'time'."""
    with open(path, "rb") as f:
        data = f.read()

    enc = "utf-16-le" if data[1:2] == b"\x00" else "latin-1"
    marker = "Binary:".encode(enc)
    idx = data.find(marker)
    if idx < 0:
        raise ValueError(f"{path}: no 'Binary:' section (ASCII raw files are not supported)")
    newline = "\n".encode(enc)
    body_start = data.find(newline, idx) + len(newline)
    header = data[:idx].decode(enc)
    body = data[body_start:]

    n_vars = n_points = None
    flags = ""
    names = []
    in_vars = False
    for line in header.splitlines():
        if in_vars:
            parts = line.split()
            if len(parts) >= 3 and parts[0].isdigit():
                names.append(parts[1].lower())
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        if key == "no. variables":
            n_vars = int(value)
        elif key == "no. points":
            n_points = int(value)
        elif key == "flags":
            flags = value.lower()
        elif key == "variables":
            in_vars = True

    if n_vars is None or n_points is None or len(names) != n_vars:
        raise ValueError(f"{path}: could not parse raw-file header")

    is_ltspice = enc == "utf-16-le"
    if is_ltspice and "double" not in flags:
        dtype = np.dtype([("time", "<f8")] + [(f"v{i}", "<f4") for i in range(1, n_vars)])
        rec = np.frombuffer(body, dtype=dtype, count=n_points)
        cols = [rec[name].astype(float) for name in dtype.names]
    else:
        arr = np.frombuffer(body, dtype="<f8", count=n_points * n_vars).reshape(n_points, n_vars)
        cols = [arr[:, i].copy() for i in range(n_vars)]

    out = dict(zip(names, cols))
    # LTspice flags compressed time points with a negative sign.
    out["time"] = np.abs(out["time"])
    return out
