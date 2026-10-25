"""Run ngspice (or LTspice) in batch mode and read the resulting waveforms.

Raw files are read with flow/raw.py.
"""
import re
import subprocess
import sys
from pathlib import Path

from . import config

from .raw import read_raw

# SKY130 models need HSPICE compatibility mode; ng_nomodcheck skips a slow model-parameter check.
SPICEINIT = "set ngbehavior=hsa\nset ng_nomodcheck\nset num_threads=4\nset filetype=binary\n"


# Resume support: when True, a deck whose .cir is unchanged and whose .raw is complete is
# not simulated again. Off by default.
REUSE = False
# STRICT treats a run that ngspice aborted ("timestep too small") as failed even when it
# left a truncated raw file; RETRY_RELAXED then retries it with reltol 1e-4, and failing that with a
# 50 ps maximum step, and records it in RELAXED_RUNS. Both off by default.
STRICT = False
RETRY_RELAXED = False
RELAXED_RUNS = []
TIMEOUT = 900            # s per deck; the design-space study raises it for the 15 pF decks under parallel load


class SpiceError(RuntimeError):
    pass


def sky130_lib_line(corner="tt"):
    return f'.lib "{config.SKY130_NGSPICE_LIB.as_posix()}" {corner}'


def run_ngspice(netlist, workdir, name="deck", timeout=None):
    """Write `netlist` to workdir/name.cir, run ngspice -b, return the waveforms of name.raw.

    The netlist must not contain a .control block that writes its own raw file; the raw file is
    requested on the command line (-r), which saves all node voltages and branch currents unless
    the deck has .save lines.
    """
    timeout = timeout or TIMEOUT
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    init = workdir / ".spiceinit"
    if not init.exists() or init.read_text() != SPICEINIT:
        init.write_text(SPICEINIT)
    cir = workdir / f"{name}.cir"
    raw = workdir / f"{name}.raw"
    log = workdir / f"{name}.log"
    if REUSE and cir.exists() and raw.exists() and raw.stat().st_mtime >= cir.stat().st_mtime \
            and cir.read_text() == netlist and _completed(log) and not (STRICT and _aborted(log)):
        try:                       # a run interrupted mid-write leaves an unreadable raw: rerun it
            return read_raw(raw)
        except Exception:
            pass
    try:
        return _run(netlist, cir, raw, log, workdir, timeout)
    except SpiceError:
        if not RETRY_RELAXED:
            raise
    # "Timestep too small": retry with reltol 1e-4, then (original reltol) with the maximum step
    # raised from tstep (10 ps) to 50 ps. With TMAX = 10 ps over a long transient, ngspice can land so
    # close to a waveform breakpoint that the remaining step falls below its minimum; every PWL corner
    # still forces a time point, so the 50 ps cap leaves the settled levels unchanged (checked against
    # converged 3 pF decks: within 0.06 uV). Each retry is recorded in RELAXED_RUNS.
    tmax = re.sub(r"(?m)^(\.tran\s+\S+\s+\S+)\s*$", r"\1 0 5e-11", netlist)
    retries = [("reltol 1e-4", netlist.replace("reltol=1e-5", "reltol=1e-4")), ("tmax 50 ps", tmax)]
    err = None
    for label, deck in retries:
        if deck == netlist:
            continue
        try:
            out = _run(deck, cir, raw, log, workdir, timeout)
        except SpiceError as e:
            err = e
            continue
        RELAXED_RUNS.append(f"{cir} [{label}]")
        return out
    raise err or SpiceError(f"ngspice failed on {cir}")


def _completed(log):
    """ngspice writes the raw file as it simulates, so a killed run leaves a readable but truncated
    raw; only a log with the final timing summary marks a finished run."""
    return log.exists() and "Total elapsed time" in log.read_text(errors="replace")


def _aborted(log):
    return log.exists() and bool(re.search(r"simulation\(s\) aborted|Timestep too small",
                                           log.read_text(errors="replace")))


def _run(netlist, cir, raw, log, workdir, timeout):
    cir.write_text(netlist)
    if raw.exists():
        raw.unlink()
    proc = subprocess.run(
        [str(config.NGSPICE_EXE), "-b", "-r", raw.name, "-o", log.name, cir.name],
        cwd=workdir, capture_output=True, text=True, timeout=timeout)
    text = log.read_text(errors="replace") if log.exists() else proc.stdout + proc.stderr
    if proc.returncode != 0 or not raw.exists() or (STRICT and _aborted(log)):
        errors = [ln for ln in text.splitlines() if re.search(r"error|fatal|too small", ln, re.I)]
        raise SpiceError(f"ngspice failed on {cir} (exit {proc.returncode}):\n" + "\n".join(errors[:20]))
    return read_raw(raw)


def run_ltspice(netlist, workdir, name="deck_lt", timeout=900):
    """Write `netlist` to workdir/name.net, run LTspice -b, return the waveforms of name.raw."""
    workdir = Path(workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    net = workdir / f"{name}.net"
    raw = workdir / f"{name}.raw"
    net.write_text(netlist)
    if raw.exists():
        raw.unlink()
    proc = subprocess.run([str(config.LTSPICE_EXE), "-b", str(net)],
                          cwd=workdir, capture_output=True, timeout=timeout)
    if not raw.exists():
        log = workdir / f"{name}.log"
        text = log.read_text(encoding="utf-16-le", errors="replace") if log.exists() else ""
        raise SpiceError(f"LTspice failed on {net} (exit {proc.returncode}):\n{text[-2000:]}")
    return read_raw(raw)
