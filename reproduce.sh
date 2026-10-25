#!/usr/bin/env bash
# Reproduce the figures, the tests or every result of this repository.
#   ./reproduce.sh          figures from the stored results (about 1 min)
#   ./reproduce.sh tests    the test suite, then the figures (about 5 min)
#   ./reproduce.sh full     every study from scratch in dependency order, then the figures (about 8 h)
# Run in the activated conda environment of environment.yml.
set -euo pipefail
cd "$(dirname "$0")"
mode="${1:-}"
if [ "$mode" = "tests" ]; then
    python -m pytest -q
fi
if [ "$mode" = "full" ]; then
    python -m pytest -q
    python studies/benchmark_polat.py
    python studies/error_budget.py
    python studies/cells.py
    python studies/cells_report.py
    python studies/design_space.py
    python studies/design_space_report.py
    python studies/cryogenic.py
    if [ -d build/external/beall2026 ]; then python studies/beall_check.py; else echo "skipping beall_check: 77 K models not in build/external/beall2026"; fi
    python studies/cryogenic_report.py
    python studies/repeated_gates.py
    python studies/frame_tracking.py
    python studies/partial_tracking.py
    python studies/plunger_detuning.py
    python studies/pulse_distortion.py
    python studies/mismatch.py
    python studies/tree.py
    python studies/mismatch_bands.py
    python studies/system_budget.py
    python studies/margins.py
    python figures/make_figures.py --recompute
    exit 0
fi
python figures/make_figures.py
