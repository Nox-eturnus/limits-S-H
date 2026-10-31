#!/usr/bin/env bash
# Reproduce the figures, the tests or the results of this repository.
#   ./reproduce.sh          figures from the stored results (about 1 min)
#   ./reproduce.sh tests    the test suite, then the figures (about 5 min)
#   ./reproduce.sh fast     every study that runs from the stored channels in minutes, the Markdown summaries,
#                           then the figures (about 1.5 h)
#   ./reproduce.sh full     every study in dependency order, then the figures (see README.md for the run time)
# Run in the activated conda environment of environment.yml.
set -euo pipefail
cd "$(dirname "$0")"
mode="${1:-}"
beall=0; [ -d build/external/beall2026 ] && beall=1
gf180=0; [ -d "$HOME/pdk/gf180mcu_fd_pr_models" ] && gf180=1
run() { for s in "$@"; do python "studies/$s.py"; done; }
if [ "$mode" = "tests" ]; then
    python -m pytest -q
fi
if [ "$mode" = "fast" ]; then
    run repeated_gates frame_tracking partial_tracking plunger_detuning pulse_distortion margins cells_report \
        design_space_report cryogenic_report
    python studies/mismatch_bands.py analyse
    run partial_tracking_qec surface_code_distance droop_anchors coupling stark_scan mixed_sign polat_offset \
        pulse_drivers mc_cell mc_cell_extra mc_cell_tg
    python studies/extra_bands.py collect
    python studies/high_sigma.py report
    python studies/interval_coverage.py report
    python studies/residual_accounting.py merge
    python studies/cell_margins.py merge
    run scaled_sigma_nmos well_groups allocation quoted_margins array_yield scaled_sigma_capacitance system_operation \
        tail_optimism tail_corrected tail_corrected_tables quoted_numbers system_integration surface_code_parallel
    python studies/gf180.py analyse
    run tree_spice anchor_charge offset_well instance_check qubit_bounds system qubit_calibration tail_surrogate
    python studies/tail_surrogate.py extra
    if [ $beall = 1 ]; then run subthreshold; else echo "skipping subthreshold: 77 K data not in build/external/beall2026"; fi
    run summaries
fi
if [ "$mode" = "full" ]; then
    python -m pytest -q
    run benchmark_polat error_budget cells cells_report design_space design_space_report cryogenic
    if [ $beall = 1 ]; then run beall_check; else echo "skipping beall_check: 77 K models not in build/external/beall2026"; fi
    run cryogenic_report repeated_gates frame_tracking partial_tracking plunger_detuning pulse_distortion mismatch tree \
        mismatch_bands system_budget margins
    # error correction and budgets
    run surface_code surface_code_distance surface_code_parallel mixed_sign partial_tracking_qec stark_scan polat_offset
    python studies/surface_code.py refine
    # multi-voltage decks
    python studies/tail_surrogate.py collect
    if [ $beall = 1 ]; then run subthreshold; else echo "skipping subthreshold: 77 K data not in build/external/beall2026"; fi
    run system extra_bands tail_surrogate
    python studies/tail_surrogate.py extra
    run interval_coverage qubit_bounds anchor_charge offset_well droop_anchors high_sigma tree_source_1pf \
        residual_accounting qubit_calibration tree_spice coupling
    # one cell per channel
    run instance_check
    python studies/mc_cell.py fig6 s7 s3 sizing hundred buffer sss
    run cell_margins cell_coverage scaled_sigma_nmos allocation quoted_margins well_groups pulse_drivers
    python studies/mc_cell_extra.py sss
    for k in ov jn; do for f in 0.7 1.3; do python studies/mc_cell_extra.py cap $k $f; done; done
    run array_yield scaled_sigma_capacitance system_operation
    if [ $gf180 = 1 ]; then for m in run full tgmin; do python studies/gf180.py $m; done
    else echo "skipping the GF180 Monte Carlo: models not in ~/pdk/gf180mcu_fd_pr_models"; fi
    python studies/gf180.py analyse
    python studies/mc_cell_tg.py sss
    run tail_optimism tail_corrected tail_corrected_tables quoted_numbers system_integration
    python figures/make_figures.py --recompute
    exit 0
fi
python figures/make_figures.py
