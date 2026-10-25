@echo off
rem Reproduce the figures, the tests or every result of this repository (Windows).
rem   reproduce.bat          figures from the stored results (about 1 min)
rem   reproduce.bat tests    the test suite, then the figures (about 5 min)
rem   reproduce.bat full     every study from scratch in dependency order, then the figures (about 8 h)
rem Run in the activated conda environment of environment.yml.
setlocal
cd /d "%~dp0"
if /i "%1"=="tests" (
    python -m pytest -q || exit /b 1
)
if /i "%1"=="full" (
    python -m pytest -q || exit /b 1
    python studies\benchmark_polat.py || exit /b 1
    python studies\error_budget.py || exit /b 1
    python studies\cells.py || exit /b 1
    python studies\cells_report.py || exit /b 1
    python studies\design_space.py || exit /b 1
    python studies\design_space_report.py || exit /b 1
    python studies\cryogenic.py || exit /b 1
    if exist build\external\beall2026 (python studies\beall_check.py || exit /b 1) else (echo skipping beall_check: 77 K models not in build\external\beall2026)
    python studies\cryogenic_report.py || exit /b 1
    python studies\repeated_gates.py || exit /b 1
    python studies\frame_tracking.py || exit /b 1
    python studies\partial_tracking.py || exit /b 1
    python studies\plunger_detuning.py || exit /b 1
    python studies\pulse_distortion.py || exit /b 1
    python studies\mismatch.py || exit /b 1
    python studies\tree.py || exit /b 1
    python studies\mismatch_bands.py || exit /b 1
    python studies\system_budget.py || exit /b 1
    python studies\margins.py || exit /b 1
    python figures\make_figures.py --recompute
    exit /b %errorlevel%
)
python figures\make_figures.py
exit /b %errorlevel%
