# Fidelity limits of sample-and-hold gate drivers for silicon spin qubits: code and data

An open simulation flow that runs from transistor-level sample-and-hold (S/H) gate drivers in the SkyWater
SKY130 process to the fidelity of an adiabatic controlled-phase (CZ) gate between two silicon spin qubits.
It contains the flow, the stored results of every study and the scripts that regenerate every figure and
quoted number of the accompanying article.

The flow has three layers:

- **Qubit model** (`flow/exchange.py`, `flow/cz.py`, `flow/budget.py`): exchange that rises by *s* decades
  per volt of barrier voltage, Stark shift of the qubit frequencies, an exact piecewise-constant propagator
  of the CZ gate, an adiabatic phase model and a filter-function noise kernel. It turns a barrier-voltage
  waveform into the added infidelity after calibration and gives the error budget against the exchange slope.
- **Circuit layer** (`flow/holdstage.py`, `flow/cosim.py`, `spice/`): nine S/H architectures in SKY130,
  characterised one cell at a time and on a shared DAC line, with ngspice. Leakage is resolved to 0.1 fA,
  mismatch from Monte Carlo, and cryogenic operation enters as sensitivity bands on the device models
  (`flow/pdk.py`).
- **System layer** (`flow/cosim.py`): hold time, electrodes per DAC for a flat line and a multiplexer tree
  with its upper levels, refresh energy and area.

## Repository layout

| Path | Contents |
|---|---|
| `flow/` | the simulation library: ngspice runner and raw-file reader, SKY130 model handling and cryogenic proxy, exchange and CZ models, error budget, S/H testbenches, line co-simulation and scaling model |
| `spice/` | SKY130 switch and hold-cell libraries |
| `studies/` | one script per study, each writing `results/<study>.json` (and a Markdown summary) |
| `results/` | the stored results that the figures and the quoted numbers come from |
| `figures/` | `make_figures.py` and the figures it draws (`cache/` holds dense curves of Fig. 2) |
| `tests/` | pytest suite of the models, the testbenches and the line model |

## Studies and results

| Study | Script | Result | Run time |
|---|---|---|---|
| Benchmark against the simulated CZ of Polat et al. 2026 | `studies/benchmark_polat.py` | `benchmark_polat.json` | 15 min |
| Error budget against the exchange slope | `studies/error_budget.py` | `error_budget.json` | 3 min |
| Single-cell characterisation of nine S/H cells | `studies/cells.py`, `cells_report.py` | `cells.json` | 80 min |
| Co-simulation on a DAC line and design space of 810 designs | `studies/design_space.py`, `design_space_report.py` | `design_space.json` | 90 min |
| Cryogenic bands, process corners, leakage trend | `studies/cryogenic.py`, `cryogenic_report.py` | `cryogenic.json` | 30 min |
| Check of the cryogenic proxy against 77 K models and data | `studies/beall_check.py` | `beall_check.json` | 2 min |
| Coherent accumulation over repeated gates | `studies/repeated_gates.py` | `repeated_gates.json` | 1 min |
| Frame tracking and idle time | `studies/frame_tracking.py` | `frame_tracking.json` | 1 min |
| Partially tracked droop | `studies/partial_tracking.py` | `partial_tracking.json` | 1 min |
| Plunger (detuning) offsets | `studies/plunger_detuning.py` | `plunger_detuning.json` | seconds |
| Pulse distortion by voltage-dependent node capacitance | `studies/pulse_distortion.py` | `pulse_distortion.json` | seconds |
| Mismatch on the worst channel, room temperature | `studies/mismatch.py` | `mismatch.json` | 1 min |
| Mismatch on the worst channel in every temperature band | `studies/mismatch_bands.py` | `mismatch_bands.json`, `mismatch_bands_channels.jsonl` | 2.5 h |
| Multiplexer tree with its upper levels | `studies/tree.py` | `tree.json` | 10 min |
| Electrodes per DAC with the operational budget, DAC settling and power | `studies/system_budget.py` | `system_budget.json` | 15 min |
| All margins against the per-gate and operational budgets | `studies/margins.py` | `margins.json` | seconds |

The studies below build on these. Error correction and budgets:

| Study | Script | Result | Run time |
|---|---|---|---|
| Static ZZ errors in a distance-3 surface code, state vector | `studies/surface_code.py` | `surface_code.json`, `surface_code_refine.json` | 1 h + 40 min |
| Coherent excess to leading order, d = 3, 5, 7 | `studies/surface_code_distance.py` | `surface_code_distance.json` | 5 min |
| The same for a parallel syndrome schedule, with echoes | `studies/surface_code_parallel.py` | `surface_code_parallel.json` | 2 min |
| Mixed common and random offsets against the combined error measure | `studies/mixed_sign.py` | `mixed_sign.json` | 2 min |
| Operational budget under error correction (module) | `studies/operational_budget.py` | | |
| Partially tracked droop under error correction | `studies/partial_tracking_qec.py` | `partial_tracking_qec.json` | 2 min |
| Untracked budgets against the Stark coefficient | `studies/stark_scan.py` | `stark_scan.json` | 3 min |
| Non-exponential J(V), Stark on both qubits, 1/f budget, joint allocation | `studies/qubit_bounds.py` | `qubit_bounds.json` | 10 min |
| Pulse distortion under four calibrations | `studies/qubit_calibration.py` | `qubit_calibration.json` | 15 min |
| Agreement with Polat et al. without the fitted duration offset | `studies/polat_offset.py` | `polat_offset.json` | 3 min |

Circuit layer: one cell per Monte Carlo channel, worst-channel margins and their checks:

| Study | Script | Result | Run time |
|---|---|---|---|
| Is the SKY130 mismatch drawn per instance or per deck? | `studies/instance_check.py` | `instance_check.json` | 5 min |
| Pedestal Monte Carlo, one cell per channel | `studies/mc_cell.py` | `mc_cell_channels.jsonl`, `mc_cell_pedestals.json` | 10-12 h |
| Worst-channel margins (untracked budget, common and mismatch parts, moves) | `studies/cell_margins.py` | `cell_margins.json` | 3 h |
| Normality, KS and interval coverage on 100 channels | `studies/cell_coverage.py` | `cell_coverage.json` | 2 h |
| Scaled-sigma check of the NMOS switch | `studies/scaled_sigma_nmos.py` | `scaled_sigma_nmos.json` | seconds |
| Scaled-sigma runs of the TG and bootstrapped switch; capacitances x 0.7, 1.3 | `studies/mc_cell_extra.py` | `mc_cell_extra_channels.jsonl`, `mc_cell_extra_pedestals.json` | 30 min |
| Their analysis | `studies/scaled_sigma_capacitance.py` | `scaled_sigma_capacitance.json` | 1 min |
| Scaled-sigma runs of the TG at 300 K and 4 K high | `studies/mc_cell_tg.py` | `mc_cell_tg_channels.jsonl`, `mc_cell_tg_pedestals.json` | 6 min |
| Tail optimism of the surrogate | `studies/tail_optimism.py` | `tail_optimism.json` | seconds |
| Array-failure probability in closed form, model-error variants | `studies/array_yield.py` | `array_yield.json` | 1 min |
| Margins and probabilities with the tail correction (Fig. 6a) | `studies/tail_corrected.py` | `tail_corrected.json` | 1 min |
| Supplementary tables with the tail correction | `studies/tail_corrected_tables.py` | `tail_corrected_tables.json` | seconds |
| Joint error allocation with the untracked budgets | `studies/allocation.py` | `allocation.json` | seconds |
| Every quoted margin, before and after the tail correction | `studies/quoted_margins.py`, `quoted_numbers.py` | Markdown only | seconds |
| The deciding designs in GF180MCU | `studies/gf180.py` | `gf180.json`, `gf180_channels.jsonl`, `gf180_pedestals.json` | 30 min |
| Injected charge against van Staveren et al. (15 pF) | `studies/anchor_charge.py` | `anchor_charge.json` | 10 min |
| NMOS switch in an offset well | `studies/offset_well.py` | `offset_well.json` | 5 min |
| Electrodes per isolated well, and its area | `studies/well_groups.py` | `well_groups.json` | seconds |

Circuit layer on multi-voltage decks (one Monte Carlo seed per row; these rows hold one independently mismatched
cell per held voltage, see `studies/instance_check.py`, so the margins of the article come from `cell_margins.py`):

| Study | Script | Result | Run time |
|---|---|---|---|
| Steep-subthreshold bands calibrated on measured 77 K data | `studies/subthreshold.py` | `subthreshold.json` | 3 min |
| Monte Carlo in further variants (steep bands, clock edges, tree sources, mismatch x 1.5, x 2) | `studies/extra_bands.py` | `extra_bands_channels.jsonl`, `extra_bands_pedestals.json` | several hours |
| Gaussian surrogate of the worst of 10^6 channels | `studies/tail_surrogate.py` | `tail_surrogate.json`, `tail_surrogate_extra.json`, `tail_surrogate_pedestals.json` | 10 min |
| Coverage of its intervals | `studies/interval_coverage.py` | `interval_coverage.json` | 40 min |
| Scaled-sigma check of the NMOS switch | `studies/high_sigma.py` | `high_sigma.json`, `high_sigma_channels.jsonl` | 1.5 h |
| Common and mismatch parts of the residual, moves from a tuned level | `studies/residual_accounting.py` | `residual_accounting.json` | 1 h |
| Bootstrapped switch through its tree at the protection-diode droop of 1 pF | `studies/tree_source_1pf.py` | `tree_source_1pf_channels.jsonl`, `tree_source_1pf_pedestals.json` | 1 h |

System layer:

| Study | Script | Result | Run time |
|---|---|---|---|
| Electrode counts, power per stage, calibration time, addressing | `studies/system.py` | `system.json` | 15 min |
| Measured droop converted to a 1 pF node, and every count at that droop | `studies/droop_anchors.py` | `droop_anchors.json` | 2 min |
| Tree settling model against SPICE at full depth | `studies/tree_spice.py` | `tree_spice.json` | 1 min |
| Pulse coupling into neighbours and through a shared well | `studies/coupling.py` | `coupling.json` | seconds |
| Lower bound on the pulse-driver power | `studies/pulse_drivers.py` | `pulse_drivers.json` | seconds |
| Measured devices, drift, lines per qubit, power left out, sensor noise | `studies/system_operation.py` | `system_operation.json` | 1 min |
| Stage load with pulse drivers, placement, drift moves, leakage range, Zeeman difference, calibration time | `studies/system_integration.py` | `system_integration.json` | 3 min |

Run times are on 24 to 30 threads. `results/polat_fig2_extracted.json` holds the simulated curve of Fig. 2 of
Polat et al. (npj Quantum Information 12, 130, 2026), read from the vector data of the published figure
with `studies/extract_polat_fig2.py`; it is used for the benchmark only.

## Installation

| Tool | Version |
|---|---|
| Python | 3.12 with NumPy, SciPy, Matplotlib, QuTiP 5.3, pytest (`environment.yml`) |
| ngspice | 40 or later (the results were produced with ngspice 47) |
| SkyWater SKY130 PDK | `sky130_fd_pr`, version `c6d73a35f524070e85faff4a6a9eef49553ebc2b`, installed with volare |
| LTspice | optional, for the simulator cross-check in the tests |

```bash
conda env create -f environment.yml
conda activate sample-hold-fidelity
volare enable --pdk sky130 --pdk-root ~/pdk -l sky130_fd_pr c6d73a35f524070e85faff4a6a9eef49553ebc2b
```

The tool locations are set in `flow/config.py` and can be overridden with environment variables:
`NGSPICE_EXE` (ngspice console binary; by default the one on the PATH), `SKY130_ROOT` (the `sky130A`
directory of the PDK) and `LTSPICE_EXE`. On Windows, volare cannot create its `sky130A` symlink without
symlink rights; the default `SKY130_ROOT` points at the versioned directory, so this is harmless. Run Python
from the activated environment, since some Windows installations place a foreign BLAS library on the PATH.

`studies/beall_check.py` and `studies/subthreshold.py` also need the 77 K SKY130 models and data of Beall
et al., cloned from github.com/UTA-Advanced-Detector-Technologies/Skywater-130nm-77K-Cryogenic-Models into
`build/external/beall2026`. `studies/gf180.py` needs the ngspice models of the GF180MCU PDK
(`models/ngspice` of github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_pr, commit `9f992d5`) in
`~/pdk/gf180mcu_fd_pr_models`. Without them these studies are skipped and their stored results are kept.

## Reproducing the results

All commands run from the repository root.

```bash
python figures/make_figures.py
```

redraws every figure from the stored results (about 1 min). The PNG files come out byte-identical to the
stored ones; the PDF files differ only in their creation date.

```bash
python -m pytest -q
```

runs the test suite (about 5 min; tests that need ngspice or the PDK are skipped when these are missing).

```bash
reproduce.bat full
```

(or `./reproduce.sh full`) runs every study in dependency order and then the figures. The Monte Carlo studies
of the later analyses append every channel to a `results/*_channels.jsonl` log and skip the channels already
logged, so with the stored logs they only collect and analyse them; delete the logs to simulate every channel
again, which takes about two days on 24 to 30 threads (the one-cell-per-channel Monte Carlo of
`studies/mc_cell.py` alone takes 10 to 12 h). Simulation decks go to `build/`, which is not part of the
repository. `studies/mismatch.py` and `studies/tail_surrogate.py collect` re-read the Monte Carlo decks that
`studies/cells.py` leaves in `build/cells`, so they run after `cells.py` on the same machine.

```bash
reproduce.bat fast
```

(or `./reproduce.sh fast`) reruns, in about an hour, every study that does not simulate new Monte Carlo
channels or need hours, from the stored channels and results, writes the Markdown summaries in `results/`,
and redraws the figures. Each of these runs reproduces its stored JSON file exactly.

## Licence and citation

Code and data are released under the MIT licence (`LICENSE`). If you use the flow or its data, please cite
the accompanying article (reference added on publication) and this repository (`CITATION.cff`).
