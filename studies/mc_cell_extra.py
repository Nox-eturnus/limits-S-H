"""Further one-cell-per-channel Monte Carlo runs (with studies/mc_cell.py).

Sets:
  sss   scaled-sigma sampling of the TG and the transistor-level bootstrapped switch in the 4 K band, at mismatch
        scales 1.5, 2, 2.5 and 3 (the bootstrapped switch at 1.5 and 2 is already in results/mc_cell_channels.jsonl).
  cap   the overlap capacitances (cgso, cgdo, cgsl, cgdl, cgbo, cf) or the junction capacitances (cj, cjs, cjd,
        cjsw, cjsws, cjswd, cjswg, cjswgs, cjswgd) of every FET scaled by 0.7 or 1.3, in the 4 K band, for the four
        designs that decide the comparison. Each scaling runs in its own process, because the scaled model files are
        written once into their own build directory.

Run:  python studies/mc_cell_extra.py sss
      python studies/mc_cell_extra.py cap ov 0.7    (and ov 1.3, jn 0.7, jn 1.3)
      python studies/mc_cell_extra.py               (collect only)
Appends to results/mc_cell_extra_channels.jsonl; collect writes results/mc_cell_extra_pedestals.json.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import mc_cell as M  # noqa: E402
from flow import config, pdk  # noqa: E402

M.LOG = OUT / "mc_cell_extra_channels.jsonl"
M.PEDS = OUT / "mc_cell_extra_pedestals.json"
M.WORK = ROOT / "build" / "mc_cell_extra"
M.THREADS = 28

TG, BOOT = "TG, no ESD", "bootstrapped (transistor level), 0.3 V underdrive"
CAP_DESIGNS = ("NMOS, 0.3 V underdrive", BOOT, "TG + dummies", TG)
CAP_PARAMS = {
    "ov": ("cgso", "cgdo", "cgsl", "cgdl", "cgbo", "cf"),
    "jn": ("cj", "cjs", "cjd", "cjsw", "cjsws", "cjswd", "cjswg", "cjswgs", "cjswgd"),
}
CAP_NAME = {"ov": "overlap capacitances", "jn": "junction capacitances"}

_conditions = M.conditions


def conditions():
    c = _conditions()
    for s in (2.5, 3.0):
        c.setdefault(f"4 K, mismatch x {s:g}", dict(cryo=M.BAND_4K[:2] + (s,), mm=s))
    for kind in CAP_PARAMS:
        for f in (0.7, 1.3):
            c[f"4 K, {CAP_NAME[kind]} x {f:g}"] = dict(cryo=M.BAND_4K)
    return c


M.conditions = conditions


def sets(kind=None, f=None):
    s = {"sss": [(TG, f"4 K, mismatch x {x:g}", 20, False) for x in (1.5, 2.0, 2.5, 3.0)]
         + [(BOOT, f"4 K, mismatch x {x:g}", 20, False) for x in (2.5, 3.0)]}
    if kind:
        s["cap"] = [(d, f"4 K, {CAP_NAME[kind]} x {f:g}", 20, False) for d in CAP_DESIGNS]
    return s


def scale_caps(kind, f):
    """Write the 4 K model files once into a build directory of their own, then scale the capacitance parameters."""
    config.BUILD_DIR = ROOT / "build" / "mc_cell_extra" / f"pdk_{kind}{f:g}"
    pat = re.compile(r"^(\+\s*)(" + "|".join(CAP_PARAMS[kind]) + r")(\s*=\s*)([-+0-9.eE]+)(.*)$", re.I)
    for mm in (False, True):
        pdk.write_fet18_lib("tt", "hold", mm, M.BAND_4K)
    n = 0
    for p in config.BUILD_DIR.glob("pdk/*/tt/*.spice"):
        mark = p.with_suffix(".capscaled")
        if mark.exists():
            continue
        lines = p.read_text().splitlines()
        for i, line in enumerate(lines):
            m = pat.match(line)
            if m:
                lines[i] = f"{m.group(1)}{m.group(2)}{m.group(3)}{float(m.group(4)) * f:.7g}{m.group(5)}"
                n += 1
        p.write_text("\n".join(lines) + "\n")
        mark.write_text("")
    print(f"{n} capacitance parameters scaled by {f:g} in {config.BUILD_DIR}", flush=True)


def run(names, s):
    M.sets = lambda: s
    M.simulate(names)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "sss":
        run(["sss"], sets())
    elif a and a[0] == "cap":
        kind, f = a[1], float(a[2])
        scale_caps(kind, f)
        run(["cap"], sets(kind, f))
    M.collect()
