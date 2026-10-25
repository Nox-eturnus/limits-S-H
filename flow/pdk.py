"""Trimmed SKY130 model library for fast simulation.

The full `sky130.lib.spice <corner>` section loads every device in the PDK (HV, RF, ESD, BJTs,
resistors), which costs about 45 s per ngspice run. The flow only needs a few devices, so this
module writes a library that includes only their model files (taken verbatim from the PDK's own
corner file) plus the shared parameter files. The device models themselves are unchanged.

Device sets:

* ``core`` (default): sky130_fd_pr__nfet_01v8 and __pfet_01v8.
* ``hold``: core plus the thick-oxide 5 V FETs (nfet/pfet_g5v0d10v5, for the T-switch),
  the high-V_T PMOS (pfet_01v8_hvt, low-leakage TG),
  and the corner's non-FET parameters, which the junction-diode models (ESD) need. The diode models
  themselves come in through all.spice.

Corners: tt, ff, ss, fs, sf, and ``leak``, the PDK's leakage corner (corners/leak.spice), which the
droop study uses.

Use `fet18_lib_line(corner)` in place of `spice.sky130_lib_line(corner)`; the core set is checked
against the full library in tests/test_spice.py.
"""
import os
import re
import threading
from pathlib import Path

from . import config

DEVICE_SETS = {
    "core": ("sky130_fd_pr__nfet_01v8__", "sky130_fd_pr__pfet_01v8__"),
    "hold": ("sky130_fd_pr__nfet_01v8__", "sky130_fd_pr__pfet_01v8__",
             "sky130_fd_pr__nfet_g5v0d10v5__", "sky130_fd_pr__pfet_g5v0d10v5__",
             "sky130_fd_pr__pfet_01v8_hvt__"),
    # low-V_T devices, for the cross-check against the Beall 2026 77 K models
    "lvt": ("sky130_fd_pr__nfet_01v8_lvt__", "sky130_fd_pr__pfet_01v8_lvt__"),
}
CORNERS = ("tt", "ff", "ss", "fs", "sf", "leak")


_WRITE_LOCK = threading.Lock()


def _atomic_write(path, text):
    # one writer at a time: on Windows, os.replace fails while another thread's ngspice has the file open
    with _WRITE_LOCK:
        if not path.exists() or path.read_text() != text:
            tmp = path.parent / f"{path.name}.{os.getpid()}_{threading.get_ident()}.tmp"
            tmp.write_text(text)
            os.replace(tmp, path)


# a parameter assignment anywhere on a model line: value is a {...} expression or a bare token
_PARAM = re.compile(r"(?<![A-Za-z0-9_])(vth0|u0|lu0|wu0|pu0)(\s*=\s*)(\{[^{}]*\}|[^\s{}]+)", re.I)
_MODEL = re.compile(r"^\.model\s+\S+\s+(nmos|pmos)", re.I)
_VT_SLOPE = re.compile(r"^(\.param\s+\S+__(?:vth0|toxe|voff|nfactor)_slope\d*\s*=\s*)([-+0-9.eE]+)(.*)$", re.I)
_INCLUDE = re.compile(r'^(\s*\.include\s+")([^"]+)(".*)$', re.I)


def _cryo_copy(src, dvt, mu, outdir, done, mm=1.0, dvt_p=None, mu_p=None):
    """Copy a FET model file with |V_T| raised by dvt (V) and the mobility (u0, lu0, wu0, pu0)
    scaled by mu, in every bin; follow relative .include lines. Returns the copy's path."""
    src = Path(src).resolve()
    dst = outdir / src.name
    if src in done:
        return dst
    done.add(src)
    if dst.exists():                  # the directory is specific to (dvt, mu, corner): content is fixed
        for line in src.read_text().splitlines():          # still make sure its includes exist
            m = _INCLUDE.match(line)
            if m and not Path(m.group(2)).is_absolute():
                _cryo_copy(src.parent / m.group(2), dvt, mu, outdir, done, mm, dvt_p, mu_p)
        return dst
    kind = None
    out = []
    for line in src.read_text().splitlines():
        m = _MODEL.match(line)
        if m:
            kind = m.group(1).lower()
        m = _INCLUDE.match(line)
        if m and not Path(m.group(2)).is_absolute():
            child = _cryo_copy(src.parent / m.group(2), dvt, mu, outdir, done, mm, dvt_p, mu_p)
            out.append(f'{m.group(1)}{child.as_posix()}{m.group(3)}')
            continue
        m = _VT_SLOPE.match(line)
        if m and mm != 1.0:                 # mismatch slopes (V_T, oxide, voff, nfactor) scaled by mm
            out.append(f"{m.group(1)}{float(m.group(2)) * mm:.6g}{m.group(3)}")
            continue
        if kind and line.lstrip().startswith("+"):
            def sub(m):
                name, eq, val = m.group(1).lower(), m.group(2), m.group(3).strip("{}")
                d, u = (dvt, mu) if kind == "nmos" else (dvt if dvt_p is None else dvt_p, mu if mu_p is None else mu_p)
                if name == "vth0":
                    return f"{m.group(1)}{eq}{{({val}) {'+' if kind == 'nmos' else '-'} {d:g}}}"
                return f"{m.group(1)}{eq}{{({val}) * {u:g}}}"
            line = _PARAM.sub(sub, line)
        out.append(line)
    _atomic_write(dst, "\n".join(out) + "\n")
    return dst


def write_fet18_lib(corner="tt", devices="core", mismatch=False, cryo=None):
    """cryo = (dvt, mu[, mm]): cryogenic proxy, every FET's |V_T| raised by dvt and its mobility
    scaled by mu (in the manner of the Beall 2026 77 K refit, which scales VTH0 and U0). Diodes and
    the rest are unchanged; the optional mm scales the mismatch (the vth0, toxe, voff and nfactor slope parameters; the
    thick-oxide devices have no vth0 slope), and the
    optional (dvt_p, mu_p) give the pMOS its own shift and mobility factor (cryo = (dvt, mu, mm, dvt_p, mu_p)). None
    (default) leaves the PDK models untouched."""
    if corner not in CORNERS:
        raise ValueError(corner)
    names = DEVICE_SETS[devices]
    ngspice_dir = config.SKY130_NGSPICE_LIB.parent
    corner_file = ngspice_dir / "corners" / f"{corner}.spice"
    keep = []
    for line in corner_file.read_text().splitlines():
        m = re.match(r'\s*\.include\s+"([^"]+)"', line)
        if not m:
            continue
        inc = m.group(1)
        if any(d in inc for d in names) or (devices != "core" and inc.endswith("nonfet.spice")):
            keep.append((corner_file.parent / inc).resolve())
    if len(keep) < 2 * len(names):
        raise RuntimeError(f"missing model files for {names} in {corner_file}, got {keep}")
    tag = f"{corner}{'' if devices == 'core' else '_' + devices}{'_mm' if mismatch else ''}"
    if cryo is not None:
        c = tuple(cryo)
        dvt, mu = c[0], c[1]
        mm = c[2] if len(c) > 2 else 1.0
        dvt_p, mu_p = (c[3], c[4]) if len(c) > 4 else (dvt, mu)
        ctag = (f"cryo_dvt{dvt * 1e3:g}m_mu{mu:g}" + (f"_mm{mm:g}" if mm != 1.0 else "")
                + (f"_p{dvt_p * 1e3:g}m_{mu_p:g}" if (dvt_p, mu_p) != (dvt, mu) else ""))
        tag += "_" + ctag
        cdir = config.BUILD_DIR / "pdk" / ctag / corner
        cdir.mkdir(parents=True, exist_ok=True)
        done = set()
        keep = [p if p.name.endswith("nonfet.spice") else _cryo_copy(p, dvt, mu, cdir, done, mm, dvt_p, mu_p) for p in keep]
    out = config.BUILD_DIR / "pdk" / f"sky130_fet18_{tag}.lib"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"* Trimmed SKY130 library, corner {corner}, devices '{devices}'"
             f"{', mismatch on' if mismatch else ''} (generated by flow/pdk.py)",
             f".lib {corner}",
             f".param mc_mm_switch={1 if mismatch else 0}",
             ".param mc_pr_switch=0",
             f'.include "{(ngspice_dir / "all.spice").as_posix()}"']
    lines += [f'.include "{p.as_posix()}"' for p in keep]
    lines += [f".endl {corner}", ""]
    # written only when it changes, and atomically: the studies run many ngspice decks in parallel threads
    _atomic_write(out, "\n".join(lines))
    return out


def fet18_lib_line(corner="tt", devices="core", mismatch=False, cryo=None):
    return f'.lib "{write_fet18_lib(corner, devices, mismatch, cryo).as_posix()}" {corner}'
