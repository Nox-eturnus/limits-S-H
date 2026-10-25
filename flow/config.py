"""Tool and PDK locations for the research flow.

Every path can be overridden with an environment variable, so the flow runs on another machine
without editing code:

    NGSPICE_EXE   ngspice console binary, version >= 40 (SKY130 needs a modern ngspice)
    LTSPICE_EXE   LTspice binary, used only for the simulator cross-check
    SKY130_ROOT   the sky130A directory of a volare-installed SkyWater PDK

"""
import os
import shutil
from pathlib import Path

HOME = Path.home()

# Default: ngspice on the PATH (ngspice_con on Windows), else the unpacked official Windows build.
NGSPICE_EXE = Path(os.environ.get(
    "NGSPICE_EXE", shutil.which("ngspice_con") or shutil.which("ngspice")
    or HOME / "Downloads" / "ngspice-47_64" / "Spice64" / "bin" / "ngspice_con.exe"))

LTSPICE_EXE = Path(os.environ.get(
    "LTSPICE_EXE", HOME / "AppData" / "Local" / "Programs" / "ADI" / "LTspice" / "LTspice.exe"))

# volare could not create its 'sky130A' symlink on Windows, so point at the versioned directory.
SKY130_VERSION = "c6d73a35f524070e85faff4a6a9eef49553ebc2b"
SKY130_ROOT = Path(os.environ.get(
    "SKY130_ROOT", HOME / "pdk" / "volare" / "sky130" / "versions" / SKY130_VERSION / "sky130A"))

SKY130_NGSPICE_LIB = SKY130_ROOT / "libs.tech" / "ngspice" / "sky130.lib.spice"

PACKAGE_DIR = Path(__file__).resolve().parents[1]
SPICE_DIR = PACKAGE_DIR / "spice"
BUILD_DIR = PACKAGE_DIR / "build"


def check():
    """Return a list of human-readable problems with the configured tools (empty if all good)."""
    problems = []
    if not NGSPICE_EXE.is_file():
        problems.append(f"ngspice not found at {NGSPICE_EXE} (set NGSPICE_EXE)")
    if not SKY130_NGSPICE_LIB.is_file():
        problems.append(f"SKY130 ngspice library not found at {SKY130_NGSPICE_LIB} (set SKY130_ROOT)")
    return problems
