import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow import config  # noqa: E402

needs_spice = pytest.mark.skipif(bool(config.check()), reason="; ".join(config.check()) or "ok")
needs_ltspice = pytest.mark.skipif(not config.LTSPICE_EXE.is_file(), reason="LTspice not installed")
