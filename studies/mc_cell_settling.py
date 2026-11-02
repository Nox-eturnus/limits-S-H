"""Single-cell SPICE runs (as studies/mc_cell.py) for switch speed, charge partition and a second fine-grid band.

Subcommands (each in its own process, because some rewrite model files):
  wide          the TG with dummies, the transistor-level bootstrapped switch and the NMOS switch sized for settling,
                5 to 40 um on 1 pF, simulated as their exact scaled equivalent, nominal cell, 20 mV grid, 300 K and 4 K.
  ref           the four deciding designs nominal on the 20 mV grid in the 4 K band, unmodified models.
  part <x>      the charge partition xpart of every FET bin set to x (0.5 or 1; the process models use 0, 40/60),
                4 K band: four deciding designs with 20 channels on the seven standard voltages, the four nominal on
                the 20 mV grid, and the TG sized for settling (5 and 40 um) nominal on the 20 mV grid.
  nqs           as part, with the transient non-quasi-static charge model (trnqsmod = 1) instead.
  band <name>   the six designs of Figure 6, 20 channels on the fine windows, in a second band.
  collect       write the pedestal file (on the held voltages that the channels share).

Run:  python studies/mc_cell_settling.py wide ; ... ref ; ... part 0.5 ; ... part 1 ; ... nqs ; ... band "4 K high"
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

M.LOG = OUT / "mc_cell_settling_channels.jsonl"
M.OUT = OUT
M.WORK = ROOT / "build" / "mc_cell_settling"
M.THREADS = 28

NMOS, BOOT, TGD, TG = ("NMOS, 0.3 V underdrive", "bootstrapped (transistor level), 0.3 V underdrive",
                       "TG + dummies", "TG, no ESD")
DECIDING = (NMOS, BOOT, TGD, TG)
WIDE = (5.0, 10.0, 20.0, 40.0)
W_SIM = 5.0
FINE = [round(0.3 + 0.02 * k, 3) for k in range(61)]
ARCH = {"TG": dict(arch="TG"), "TG + dummies": dict(arch="TGD"),
        "bootstrapped": dict(arch="BOOTT", v_underdrive=0.3), "NMOS": dict(arch="NSW", v_underdrive=0.3)}

_conditions = M.conditions


def conditions():
    c = _conditions()
    for x in ("0.5", "1"):
        c[f"4 K, xpart {x}"] = dict(cryo=M.BAND_4K)
    c["4 K, NQS"] = dict(cryo=M.BAND_4K)
    return c


M.conditions = conditions


def wide_name(a, w):
    return f"{a} sized for settling, W {w:g}"


for _a, _kw in ARCH.items():
    for _w in WIDE:
        _k = _w / W_SIM
        M.DESIGNS[wide_name(_a, _w)] = dict(_kw, wn=W_SIM, esd_area=0.0, c_node=1e-12 / _k, r_src=50.0 * _k)

_grid = M.grid


def grid(design, fine=False):
    if " sized for settling" in design or fine == "all":
        return FINE
    return _grid(design, fine)


M.grid = grid


def rewrite(tag, pattern, value):
    """The 4 K model files in a build directory of their own, with one parameter of every bin replaced."""
    config.BUILD_DIR = ROOT / "build" / "mc_cell_settling" / f"pdk_{tag}"
    pat = re.compile(rf"^(\+\s*)({pattern})(\s*=\s*)([-+0-9.eE]+)(.*)$", re.I)
    for mm in (False, True):
        pdk.write_fet18_lib("tt", "hold", mm, M.BAND_4K)
    n = 0
    for p in config.BUILD_DIR.glob("pdk/*/tt/*.spice"):
        mark = p.with_suffix(".rewritten")
        if mark.exists():
            continue
        lines = p.read_text().splitlines()
        for i, line in enumerate(lines):
            m = pat.match(line)
            if m:
                lines[i] = f"{m.group(1)}{m.group(2)}{m.group(3)}{value}{m.group(5)}"
                n += 1
        p.write_text("\n".join(lines) + "\n")
        mark.write_text("")
    print(f"{n} {pattern} parameters set to {value} in {config.BUILD_DIR}", flush=True)


def collect():
    """As mc_cell.collect, but on the held voltages that the channels share: the nominal cell of a condition may
    also have been run on the 20 mV grid, which the 20 channels were not."""
    import json
    import numpy as np
    log = M.load_log()
    keys = {}
    for (d, c, s, v), r in log.items():
        keys.setdefault((d, c), {}).setdefault(s, {})[v] = r
    out = {}
    for (d, c), by_seed in keys.items():
        if 0 not in by_seed or 1 not in by_seed:
            continue
        vs = sorted(set(by_seed[0]) & set(by_seed[1]))
        seeds = [s for s in sorted(by_seed) if s > 0 and all(v in by_seed[s] and "error" not in by_seed[s][v] for v in vs)]
        if len(seeds) < 10 or any("error" in by_seed[0][v] for v in vs):
            continue
        ped = np.array([[by_seed[s][v]["ped"] for v in vs] for s in seeds])
        trk = np.array([[by_seed[s][v]["track"] for v in vs] for s in seeds])
        nom = by_seed[0]
        out[f"{d}|{c}"] = {"v": vs, "peds": ped.tolist(), "track": trk.tolist(), "seeds": seeds,
                           "nominal": [nom[v]["ped"] for v in vs],
                           "ok_nominal": [abs(nom[v]["track"]) < M.R.TRACK_TOL for v in vs],
                           "ok_all": (np.abs(trk) < M.R.TRACK_TOL).all(0).tolist()}
    (OUT / "mc_cell_settling_pedestals.json").write_text(json.dumps(out), encoding="utf-8")
    print(f"{len(out)} design-condition pairs written", flush=True)
    return out


M.collect = collect


def run(name, s):
    M.sets = lambda: s
    M.simulate([name])


def variant_set(cond):
    return ([(d, cond, 20, False) for d in DECIDING] + [(d, cond, 0, "all") for d in DECIDING]
            + [(wide_name("TG", w), cond, 0, False) for w in (5.0, 40.0)])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "wide":
        run("wide", {"wide": [(wide_name(x, w), c, 0, False) for x in ("TG + dummies", "bootstrapped", "NMOS")
                              for w in WIDE for c in ("300 K", "4 K proxy")]})
    elif a and a[0] == "ref":
        run("ref", {"ref": [(d, "4 K proxy", 0, "all") for d in DECIDING]
                    + [(wide_name("TG", w), "4 K proxy", 0, False) for w in (5.0, 40.0)]})
    elif a and a[0] == "part":
        rewrite(f"xpart{a[1]}", "xpart", a[1])
        run("part", {"part": variant_set(f"4 K, xpart {a[1]}")})
    elif a and a[0] == "nqs":
        rewrite("nqs", "trnqsmod", "1")
        run("nqs", {"nqs": variant_set("4 K, NQS")})
    elif a and a[0] == "band":
        run("band", {"band": [(d, a[1], 20, True) for d in M.FIG6]})
    M.collect()
