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

Run times are on 24 threads. `results/polat_fig2_extracted.json` holds the simulated curve of Fig. 2 of
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

`studies/beall_check.py` also needs the 77 K SKY130 models and data of Beall et al., cloned from
github.com/UTA-Advanced-Detector-Technologies/Skywater-130nm-77K-Cryogenic-Models into
`build/external/beall2026`.

## Reproducing the results

All commands run from the repository root.

```bash
python figures/make_figures.py
```

redraws every figure from the stored results (about 1 min).

```bash
python -m pytest -q
```

runs the test suite (about 5 min; tests that need ngspice or the PDK are skipped when these are missing).

```bash
reproduce.bat full
```

(or `./reproduce.sh full`) recomputes every result from scratch in dependency order and then the figures,
in about 8 h on 24 threads. Simulation decks go to `build/`, which is not part of the repository.
`studies/mismatch.py` re-reads the Monte Carlo decks that `studies/cells.py` leaves in `build/cells`, so it
runs after `cells.py` on the same machine.

## Licence and citation

Code and data are released under the MIT licence (`LICENSE`). If you use the flow or its data, please cite
the accompanying article (reference added on publication) and this repository (`CITATION.cff`).
