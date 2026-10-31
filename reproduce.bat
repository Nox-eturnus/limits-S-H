@echo off
rem Reproduce the figures, the tests or the results of this repository (Windows).
rem   reproduce.bat          figures from the stored results (about 1 min)
rem   reproduce.bat tests    the test suite, then the figures (about 5 min)
rem   reproduce.bat fast     every study that runs from the stored channels in minutes, the Markdown summaries,
rem                          then the figures (about 1.5 h)
rem   reproduce.bat full     every study in dependency order, then the figures (see README.md for the run time)
rem Run in the activated conda environment of environment.yml.
setlocal
cd /d "%~dp0"
set BEALL=0
if exist build\external\beall2026 set BEALL=1
set GF180=0
if exist "%USERPROFILE%\pdk\gf180mcu_fd_pr_models" set GF180=1
if /i "%1"=="tests" (
    python -m pytest -q || exit /b 1
)
if /i "%1"=="fast" (
    for %%s in (repeated_gates frame_tracking partial_tracking plunger_detuning pulse_distortion margins cells_report design_space_report cryogenic_report) do (
        python studies\%%s.py || exit /b 1
    )
    python studies\mismatch_bands.py analyse || exit /b 1
    for %%s in (partial_tracking_qec surface_code_distance droop_anchors coupling stark_scan mixed_sign polat_offset pulse_drivers mc_cell mc_cell_extra mc_cell_tg) do (
        python studies\%%s.py || exit /b 1
    )
    python studies\extra_bands.py collect || exit /b 1
    python studies\high_sigma.py report || exit /b 1
    python studies\interval_coverage.py report || exit /b 1
    python studies\residual_accounting.py merge || exit /b 1
    python studies\cell_margins.py merge || exit /b 1
    for %%s in (scaled_sigma_nmos well_groups allocation quoted_margins array_yield scaled_sigma_capacitance system_operation tail_optimism tail_corrected tail_corrected_tables quoted_numbers system_integration surface_code_parallel) do (
        python studies\%%s.py || exit /b 1
    )
    python studies\gf180.py analyse || exit /b 1
    for %%s in (tree_spice anchor_charge offset_well instance_check qubit_bounds system qubit_calibration tail_surrogate) do (
        python studies\%%s.py || exit /b 1
    )
    python studies\tail_surrogate.py extra || exit /b 1
    if %BEALL%==1 (python studies\subthreshold.py || exit /b 1) else (echo skipping subthreshold: 77 K data not in build\external\beall2026)
    python studies\summaries.py || exit /b 1
)
if /i "%1"=="full" (
    python -m pytest -q || exit /b 1
    for %%s in (benchmark_polat error_budget cells cells_report design_space design_space_report cryogenic) do (
        python studies\%%s.py || exit /b 1
    )
    if %BEALL%==1 (python studies\beall_check.py || exit /b 1) else (echo skipping beall_check: 77 K models not in build\external\beall2026)
    for %%s in (cryogenic_report repeated_gates frame_tracking partial_tracking plunger_detuning pulse_distortion mismatch tree mismatch_bands system_budget margins) do (
        python studies\%%s.py || exit /b 1
    )
    rem error correction and budgets
    for %%s in (surface_code surface_code_distance surface_code_parallel mixed_sign partial_tracking_qec stark_scan polat_offset) do (
        python studies\%%s.py || exit /b 1
    )
    python studies\surface_code.py refine || exit /b 1
    rem multi-voltage decks
    python studies\tail_surrogate.py collect || exit /b 1
    if %BEALL%==1 (python studies\subthreshold.py || exit /b 1) else (echo skipping subthreshold: 77 K data not in build\external\beall2026)
    for %%s in (system extra_bands tail_surrogate) do (
        python studies\%%s.py || exit /b 1
    )
    python studies\tail_surrogate.py extra || exit /b 1
    for %%s in (interval_coverage qubit_bounds anchor_charge offset_well droop_anchors high_sigma tree_source_1pf residual_accounting qubit_calibration tree_spice coupling) do (
        python studies\%%s.py || exit /b 1
    )
    rem one cell per channel
    python studies\instance_check.py || exit /b 1
    python studies\mc_cell.py fig6 s7 s3 sizing hundred buffer sss || exit /b 1
    for %%s in (cell_margins cell_coverage scaled_sigma_nmos allocation quoted_margins well_groups pulse_drivers) do (
        python studies\%%s.py || exit /b 1
    )
    python studies\mc_cell_extra.py sss || exit /b 1
    for %%k in (ov jn) do for %%f in (0.7 1.3) do (
        python studies\mc_cell_extra.py cap %%k %%f || exit /b 1
    )
    for %%s in (array_yield scaled_sigma_capacitance system_operation) do (
        python studies\%%s.py || exit /b 1
    )
    if %GF180%==1 (
        for %%m in (run full tgmin) do (python studies\gf180.py %%m || exit /b 1)
    ) else (echo skipping the GF180 Monte Carlo: models not in %USERPROFILE%\pdk\gf180mcu_fd_pr_models)
    python studies\gf180.py analyse || exit /b 1
    python studies\mc_cell_tg.py sss || exit /b 1
    for %%s in (tail_optimism tail_corrected tail_corrected_tables quoted_numbers system_integration) do (
        python studies\%%s.py || exit /b 1
    )
    python figures\make_figures.py --recompute
    exit /b %errorlevel%
)
python figures\make_figures.py
exit /b %errorlevel%
