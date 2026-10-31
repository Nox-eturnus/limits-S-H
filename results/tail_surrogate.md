## Worst-of-10^6 margins from a Gaussian-copula surrogate (10^7 synthetic channels), 90 % bootstrap interval

Margin = budget / error of the worst of 10^6 channels (median of the maximum). Budgets (µV): s33.69_t0.0001: per gate 168, operational 129; s33.69_t0.001: per gate 524, operational 404; s10_t0.001: per gate 1373, operational 1361; s10_t0.0001: per gate 437, operational 435

Class: pass if the whole 90 % interval is above one, fail if below, otherwise indeterminate. Exceed: expected number of channels in 10^6 above the budget.

### Operational budget at s33.69_t0.0001 (129 µV)

| design | band | n | per-channel margin [90 % CI] | class | rev. 2 Gaussian | exceed / 10^6 | shared margin [90 % CI] | class | exceed / 10^6 |
|---|---|---|---|---|---|---|---|---|---|
| NMOS switch | 300 K (nine cells) | 20 | 4.21 [3.29, 4.52] | pass | 4.89 | 0 | 3.11 [2.52, 3.48] | pass | 0 |
| TG | 300 K (nine cells) | 20 | 0.83 [0.73, 0.98] | fail | 0.95 | 305 | 0.65 [0.54, 0.84] | fail | 6.36e+03 |
| TG with dummies | 300 K (nine cells) | 20 | 0.68 [0.55, 0.79] | fail | 1.01 | 1.01e+03 | 0.47 [0.38, 0.60] | fail | 2.07e+04 |
| bootstrapped NMOS | 300 K (nine cells) | 20 | 2.88 [2.35, 3.24] | pass | 4.53 | 0 | 2.50 [2.10, 2.70] | pass | 0 |
| charge-locked TG | 300 K (nine cells) | 20 | 1.52 [1.36, 1.80] | pass | 1.79 | 0 | 1.21 [1.00, 1.58] | pass | 0 |
| thick-oxide T-switch | 300 K (nine cells) | 20 | 0.29 [0.25, 0.32] | fail | 0.49 | 3.98e+05 | 0.25 [0.21, 0.28] | fail | 5.82e+05 |
| TG, high-threshold PMOS | 300 K (nine cells) | 17 | 0.92 [0.84, 1.02] | indeterminate | 0.98 | 76 | 0.71 [0.64, 0.82] | fail | 2.1e+04 |
| T-switch, buffered, thick oxide | 300 K (nine cells) | 20 | 0.29 [0.25, 0.32] | fail | 0.49 | 4e+05 | 0.25 [0.21, 0.27] | fail | 5.84e+05 |
| T-switch, buffered, thin oxide | 300 K (nine cells) | 20 | 1.13 [0.93, 1.37] | indeterminate | 1.50 | 0.1 | 0.90 [0.73, 1.10] | indeterminate | 7.1 |
| NMOS, 0.3 V underdrive | 77 K proxy | 20 | 4.69 [3.86, 5.36] | pass | 5.80 | 0 | 4.55 [3.65, 4.82] | pass | 0 |
| NMOS, 0.3 V underdrive | 300 K | 20 | 4.50 [3.74, 5.27] | pass | 5.98 | 0 | 4.35 [3.56, 4.65] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K proxy | 20 | 5.04 [4.04, 5.74] | pass | 6.15 | 0 | 4.63 [3.84, 5.06] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K high | 20 | 5.00 [4.15, 5.93] | pass | 6.04 | 0 | 4.81 [3.93, 5.17] | pass | 0 |
| NMOS, 0.3 V underdrive | 77 K Beall fit | 20 | 4.68 [3.85, 5.32] | pass | 5.76 | 0 | 4.44 [3.66, 4.80] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 300 K | 20 | 1.23 [1.00, 1.38] | pass | 1.44 | 0 | 0.70 [0.58, 0.91] | fail | 823 |
| NMOS, 0.3 V underdrive | 4 K, Beall pMOS | 20 | 5.00 [4.08, 5.81] | pass | 6.15 | 0 | 4.63 [3.81, 5.05] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy | 20 | 0.72 [0.62, 0.82] | fail | 0.87 | 1.08e+03 | 0.43 [0.38, 0.55] | fail | 5.73e+04 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy (100 channels) | 100 | 0.91 [0.83, 0.95] | fail | 1.06 | 14.3 | 0.62 [0.56, 0.69] | fail | 5.48e+03 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K proxy | 20 | 0.83 [0.71, 0.97] | fail | 1.01 | 79.7 | 0.50 [0.42, 0.65] | fail | 2.34e+04 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K high | 20 | 0.73 [0.64, 0.85] | fail | 0.89 | 768 | 0.45 [0.39, 0.58] | fail | 4.96e+04 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K Beall fit | 20 | 0.85 [0.72, 0.96] | fail | 1.11 | 44.1 | 0.52 [0.44, 0.66] | fail | 1.49e+04 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, Beall pMOS | 20 | 1.00 [0.87, 1.13] | indeterminate | 1.36 | 0.8 | 0.62 [0.54, 0.79] | fail | 2.99e+03 |
| T-switch + OTA buffer | 300 K | 20 | 0.33 [0.26, 0.37] | fail | 0.42 | 2.81e+05 | 0.25 [0.20, 0.30] | fail | 5.6e+05 |
| T-switch + OTA buffer | 4 K proxy | 20 | 0.34 [0.27, 0.39] | fail | 0.44 | 2.35e+05 | 0.26 [0.21, 0.31] | fail | 4.79e+05 |
| T-switch + OTA buffer | 77 K proxy | 20 | 0.33 [0.26, 0.38] | fail | 0.43 | 2.52e+05 | 0.26 [0.21, 0.31] | fail | 5.01e+05 |
| T-switch + OTA buffer | 4 K high | 20 | 0.35 [0.28, 0.39] | fail | 0.45 | 2.16e+05 | 0.26 [0.21, 0.32] | fail | 4.53e+05 |
| T-switch + OTA buffer | 77 K Beall fit | 20 | 0.34 [0.27, 0.39] | fail | 0.43 | 2.51e+05 | 0.25 [0.20, 0.31] | fail | 5.02e+05 |
| TG + dummies | 300 K | 20 | 0.57 [0.49, 0.69] | fail | 0.88 | 4.72e+03 | 0.40 [0.33, 0.52] | fail | 4.9e+04 |
| T-switch + OTA buffer | 4 K, Beall pMOS | 20 | 0.36 [0.27, 0.38] | fail | 0.45 | 2.29e+05 | 0.26 [0.21, 0.32] | fail | 4.73e+05 |
| TG + dummies | 4 K proxy | 20 | 0.65 [0.53, 0.79] | fail | 0.92 | 1.28e+03 | 0.43 [0.35, 0.57] | fail | 3.3e+04 |
| TG + dummies | 4 K proxy (100 channels) | 100 | 0.70 [0.63, 0.76] | fail | 0.96 | 669 | 0.52 [0.46, 0.56] | fail | 1.42e+04 |
| TG + dummies | 77 K proxy | 20 | 0.64 [0.52, 0.76] | fail | 0.90 | 2.23e+03 | 0.44 [0.35, 0.55] | fail | 3.81e+04 |
| TG + dummies | 4 K high | 20 | 0.69 [0.56, 0.83] | fail | 0.92 | 675 | 0.45 [0.36, 0.59] | fail | 2.84e+04 |
| TG + dummies | 77 K Beall fit | 20 | 1.92 [1.44, 2.45] | pass | 2.39 | 0 | 1.00 [0.80, 1.44] | indeterminate | 0.7 |
| TG + dummies | 4 K, Beall pMOS | 20 | 2.10 [1.61, 2.74] | pass | 2.61 | 0 | 1.04 [0.80, 1.48] | indeterminate | 0.1 |
| TG, no ESD | 300 K | 20 | 0.73 [0.64, 0.85] | fail | 0.84 | 6.87e+03 | 0.58 [0.47, 0.74] | fail | 2.81e+04 |
| TG, no ESD | 77 K proxy | 20 | 0.69 [0.61, 0.80] | fail | 0.79 | 2.22e+04 | 0.55 [0.46, 0.70] | fail | 6.04e+04 |
| TG, no ESD | 4 K proxy | 20 | 0.67 [0.60, 0.77] | fail | 0.73 | 4.11e+04 | 0.53 [0.45, 0.68] | fail | 8.55e+04 |
| TG, no ESD | 4 K high | 20 | 0.67 [0.60, 0.77] | fail | 0.69 | 6.39e+04 | 0.53 [0.45, 0.68] | fail | 1.1e+05 |
| TG, no ESD | 77 K Beall fit | 20 | 1.64 [1.49, 1.88] | pass | 1.78 | 0 | 1.38 [1.22, 1.58] | pass | 0 |
| TG, no ESD | 4 K, Beall pMOS | 20 | 1.75 [1.61, 1.91] | pass | 1.74 | 0 | 1.63 [1.41, 1.73] | pass | 0 |
| TG, ESD on the node | 300 K | 20 | 0.81 [0.73, 0.98] | fail | 0.95 | 312 | 0.64 [0.55, 0.85] | fail | 6.35e+03 |
| TG, ESD on the node | 77 K proxy | 20 | 0.79 [0.70, 0.92] | fail | 0.91 | 2.1e+03 | 0.62 [0.53, 0.80] | fail | 1.82e+04 |
| TG, ESD on the node | 4 K proxy | 20 | 0.77 [0.69, 0.89] | fail | 0.83 | 4.41e+03 | 0.61 [0.53, 0.77] | fail | 2.73e+04 |
| TG, ESD on the node | 4 K high | 20 | 0.80 [0.73, 0.90] | fail | 0.82 | 1.37e+03 | 0.64 [0.54, 0.81] | fail | 1.45e+04 |
| TG, ESD on the node | 77 K Beall fit | 20 | 4.32 [3.62, 5.32] | pass | 4.89 | 0 | 3.19 [2.62, 3.85] | pass | 0 |
| TG, ESD on the node | 4 K, Beall pMOS | 20 | 5.23 [4.27, 7.52] | pass | 6.48 | 0 | 3.40 [2.69, 4.50] | pass | 0 |

### Operational budget at s33.69_t0.001 (404 µV)

| design | band | n | per-channel margin [90 % CI] | class | rev. 2 Gaussian | exceed / 10^6 | shared margin [90 % CI] | class | exceed / 10^6 |
|---|---|---|---|---|---|---|---|---|---|
| NMOS switch | 300 K (nine cells) | 20 | 13.16 [10.29, 14.14] | pass | 15.31 | 0 | 9.74 [7.89, 10.90] | pass | 0 |
| TG | 300 K (nine cells) | 20 | 2.60 [2.30, 3.05] | pass | 2.99 | 0 | 2.03 [1.70, 2.63] | pass | 0 |
| TG with dummies | 300 K (nine cells) | 20 | 2.12 [1.73, 2.47] | pass | 3.17 | 0 | 1.48 [1.19, 1.87] | pass | 0 |
| bootstrapped NMOS | 300 K (nine cells) | 20 | 9.03 [7.36, 10.15] | pass | 14.17 | 0 | 7.82 [6.57, 8.45] | pass | 0 |
| charge-locked TG | 300 K (nine cells) | 20 | 4.76 [4.26, 5.65] | pass | 5.60 | 0 | 3.78 [3.14, 4.94] | pass | 0 |
| thick-oxide T-switch | 300 K (nine cells) | 20 | 0.91 [0.77, 1.00] | indeterminate | 1.54 | 12.4 | 0.78 [0.65, 0.86] | fail | 149 |
| TG, high-threshold PMOS | 300 K (nine cells) | 17 | 2.87 [2.62, 3.20] | pass | 3.06 | 0 | 2.23 [2.00, 2.58] | pass | 0 |
| T-switch, buffered, thick oxide | 300 K (nine cells) | 20 | 0.90 [0.77, 1.00] | fail | 1.54 | 13.4 | 0.79 [0.66, 0.86] | fail | 156 |
| T-switch, buffered, thin oxide | 300 K (nine cells) | 20 | 3.55 [2.91, 4.30] | pass | 4.70 | 0 | 2.82 [2.29, 3.43] | pass | 0 |
| NMOS, 0.3 V underdrive | 77 K proxy | 20 | 14.69 [12.07, 16.77] | pass | 18.15 | 0 | 14.23 [11.41, 15.07] | pass | 0 |
| NMOS, 0.3 V underdrive | 300 K | 20 | 14.09 [11.71, 16.49] | pass | 18.71 | 0 | 13.61 [11.13, 14.55] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K proxy | 20 | 15.77 [12.65, 17.98] | pass | 19.24 | 0 | 14.50 [12.00, 15.84] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K high | 20 | 15.66 [12.99, 18.56] | pass | 18.90 | 0 | 15.07 [12.30, 16.17] | pass | 0 |
| NMOS, 0.3 V underdrive | 77 K Beall fit | 20 | 14.66 [12.04, 16.64] | pass | 18.02 | 0 | 13.90 [11.46, 15.01] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 300 K | 20 | 3.85 [3.13, 4.33] | pass | 4.52 | 0 | 2.20 [1.83, 2.86] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, Beall pMOS | 20 | 15.66 [12.77, 18.18] | pass | 19.24 | 0 | 14.50 [11.92, 15.81] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy | 20 | 2.24 [1.95, 2.57] | pass | 2.72 | 0 | 1.36 [1.18, 1.73] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy (100 channels) | 100 | 2.84 [2.61, 2.98] | pass | 3.32 | 0 | 1.95 [1.76, 2.16] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K proxy | 20 | 2.60 [2.22, 3.03] | pass | 3.16 | 0 | 1.56 [1.32, 2.02] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K high | 20 | 2.28 [2.01, 2.65] | pass | 2.79 | 0 | 1.41 [1.23, 1.81] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K Beall fit | 20 | 2.66 [2.26, 3.00] | pass | 3.49 | 0 | 1.61 [1.39, 2.08] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, Beall pMOS | 20 | 3.12 [2.72, 3.53] | pass | 4.26 | 0 | 1.95 [1.68, 2.47] | pass | 0 |
| T-switch + OTA buffer | 300 K | 20 | 1.02 [0.82, 1.16] | indeterminate | 1.32 | 0.2 | 0.78 [0.63, 0.95] | fail | 133 |
| T-switch + OTA buffer | 4 K proxy | 20 | 1.07 [0.86, 1.21] | indeterminate | 1.38 | 0 | 0.82 [0.66, 0.98] | fail | 65.5 |
| T-switch + OTA buffer | 77 K proxy | 20 | 1.04 [0.82, 1.18] | indeterminate | 1.36 | 0.3 | 0.80 [0.65, 0.97] | fail | 92 |
| T-switch + OTA buffer | 4 K high | 20 | 1.09 [0.88, 1.23] | indeterminate | 1.41 | 0 | 0.81 [0.67, 1.01] | indeterminate | 49.6 |
| T-switch + OTA buffer | 77 K Beall fit | 20 | 1.06 [0.83, 1.21] | indeterminate | 1.36 | 0.2 | 0.79 [0.64, 0.97] | fail | 93.2 |
| TG + dummies | 300 K | 20 | 1.78 [1.55, 2.16] | pass | 2.75 | 0 | 1.26 [1.04, 1.63] | pass | 0 |
| T-switch + OTA buffer | 4 K, Beall pMOS | 20 | 1.11 [0.86, 1.20] | indeterminate | 1.39 | 0.1 | 0.82 [0.65, 0.99] | fail | 66.8 |
| TG + dummies | 4 K proxy | 20 | 2.05 [1.66, 2.49] | pass | 2.87 | 0 | 1.35 [1.09, 1.79] | pass | 0 |
| TG + dummies | 4 K proxy (100 channels) | 100 | 2.20 [1.98, 2.39] | pass | 2.99 | 0 | 1.62 [1.43, 1.77] | pass | 0 |
| TG + dummies | 77 K proxy | 20 | 2.01 [1.62, 2.39] | pass | 2.83 | 0 | 1.36 [1.09, 1.72] | pass | 0 |
| TG + dummies | 4 K high | 20 | 2.17 [1.74, 2.60] | pass | 2.88 | 0 | 1.40 [1.12, 1.85] | pass | 0 |
| TG + dummies | 77 K Beall fit | 20 | 5.99 [4.52, 7.66] | pass | 7.47 | 0 | 3.13 [2.51, 4.51] | pass | 0 |
| TG + dummies | 4 K, Beall pMOS | 20 | 6.56 [5.05, 8.58] | pass | 8.17 | 0 | 3.25 [2.51, 4.63] | pass | 0 |
| TG, no ESD | 300 K | 20 | 2.30 [2.00, 2.67] | pass | 2.63 | 0 | 1.80 [1.47, 2.32] | pass | 0 |
| TG, no ESD | 77 K proxy | 20 | 2.15 [1.92, 2.50] | pass | 2.48 | 0 | 1.72 [1.43, 2.19] | pass | 0 |
| TG, no ESD | 4 K proxy | 20 | 2.10 [1.89, 2.42] | pass | 2.27 | 0 | 1.67 [1.42, 2.11] | pass | 0 |
| TG, no ESD | 4 K high | 20 | 2.09 [1.87, 2.42] | pass | 2.15 | 0 | 1.67 [1.42, 2.14] | pass | 0 |
| TG, no ESD | 77 K Beall fit | 20 | 5.12 [4.65, 5.88] | pass | 5.56 | 0 | 4.32 [3.81, 4.95] | pass | 0 |
| TG, no ESD | 4 K, Beall pMOS | 20 | 5.48 [5.04, 5.98] | pass | 5.43 | 0 | 5.10 [4.42, 5.42] | pass | 0 |
| TG, ESD on the node | 300 K | 20 | 2.53 [2.30, 3.05] | pass | 2.99 | 0 | 1.99 [1.72, 2.66] | pass | 0 |
| TG, ESD on the node | 77 K proxy | 20 | 2.47 [2.19, 2.87] | pass | 2.83 | 0 | 1.95 [1.65, 2.50] | pass | 0 |
| TG, ESD on the node | 4 K proxy | 20 | 2.40 [2.17, 2.79] | pass | 2.59 | 0 | 1.90 [1.64, 2.43] | pass | 0 |
| TG, ESD on the node | 4 K high | 20 | 2.51 [2.29, 2.82] | pass | 2.58 | 0 | 1.99 [1.70, 2.54] | pass | 0 |
| TG, ESD on the node | 77 K Beall fit | 20 | 13.52 [11.32, 16.64] | pass | 15.30 | 0 | 9.97 [8.19, 12.05] | pass | 0 |
| TG, ESD on the node | 4 K, Beall pMOS | 20 | 16.37 [13.36, 23.54] | pass | 20.27 | 0 | 10.65 [8.42, 14.10] | pass | 0 |

### Operational budget at s10_t0.001 (1361 µV)

| design | band | n | per-channel margin [90 % CI] | class | rev. 2 Gaussian | exceed / 10^6 | shared margin [90 % CI] | class | exceed / 10^6 |
|---|---|---|---|---|---|---|---|---|---|
| NMOS switch | 300 K (nine cells) | 20 | 44.37 [34.70, 47.69] | pass | 51.61 | 0 | 32.83 [26.60, 36.77] | pass | 0 |
| TG | 300 K (nine cells) | 20 | 8.77 [7.75, 10.30] | pass | 10.07 | 0 | 6.83 [5.72, 8.88] | pass | 0 |
| TG with dummies | 300 K (nine cells) | 20 | 7.13 [5.83, 8.33] | pass | 10.69 | 0 | 5.01 [4.00, 6.31] | pass | 0 |
| bootstrapped NMOS | 300 K (nine cells) | 20 | 30.43 [24.82, 34.21] | pass | 47.77 | 0 | 26.36 [22.16, 28.50] | pass | 0 |
| charge-locked TG | 300 K (nine cells) | 20 | 16.03 [14.36, 19.04] | pass | 18.89 | 0 | 12.76 [10.58, 16.65] | pass | 0 |
| thick-oxide T-switch | 300 K (nine cells) | 20 | 3.06 [2.59, 3.38] | pass | 5.20 | 0 | 2.63 [2.19, 2.91] | pass | 0 |
| TG, high-threshold PMOS | 300 K (nine cells) | 17 | 9.68 [8.82, 10.80] | pass | 10.32 | 0 | 7.51 [6.76, 8.69] | pass | 0 |
| T-switch, buffered, thick oxide | 300 K (nine cells) | 20 | 3.03 [2.59, 3.36] | pass | 5.19 | 0 | 2.66 [2.21, 2.90] | pass | 0 |
| T-switch, buffered, thin oxide | 300 K (nine cells) | 20 | 11.96 [9.81, 14.49] | pass | 15.85 | 0 | 9.50 [7.72, 11.58] | pass | 0 |
| NMOS, 0.3 V underdrive | 77 K proxy | 20 | 49.53 [40.70, 56.56] | pass | 61.18 | 0 | 47.98 [38.47, 50.81] | pass | 0 |
| NMOS, 0.3 V underdrive | 300 K | 20 | 47.51 [39.50, 55.61] | pass | 63.08 | 0 | 45.90 [37.54, 49.05] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K proxy | 20 | 53.17 [42.65, 60.61] | pass | 64.88 | 0 | 48.91 [40.47, 53.42] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K high | 20 | 52.79 [43.81, 62.58] | pass | 63.73 | 0 | 50.80 [41.46, 54.53] | pass | 0 |
| NMOS, 0.3 V underdrive | 77 K Beall fit | 20 | 49.43 [40.60, 56.10] | pass | 60.75 | 0 | 46.88 [38.64, 50.62] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 300 K | 20 | 12.98 [10.57, 14.61] | pass | 15.23 | 0 | 7.40 [6.17, 9.63] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, Beall pMOS | 20 | 52.80 [43.07, 61.29] | pass | 64.88 | 0 | 48.88 [40.21, 53.29] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy | 20 | 7.56 [6.57, 8.67] | pass | 9.18 | 0 | 4.57 [3.97, 5.82] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy (100 channels) | 100 | 9.58 [8.81, 10.05] | pass | 11.21 | 0 | 6.58 [5.93, 7.28] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K proxy | 20 | 8.77 [7.49, 10.20] | pass | 10.64 | 0 | 5.27 [4.47, 6.81] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K high | 20 | 7.69 [6.78, 8.95] | pass | 9.39 | 0 | 4.77 [4.15, 6.09] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K Beall fit | 20 | 8.95 [7.61, 10.13] | pass | 11.76 | 0 | 5.44 [4.67, 7.01] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, Beall pMOS | 20 | 10.53 [9.18, 11.90] | pass | 14.38 | 0 | 6.59 [5.66, 8.34] | pass | 0 |
| T-switch + OTA buffer | 300 K | 20 | 3.45 [2.77, 3.93] | pass | 4.45 | 0 | 2.62 [2.12, 3.20] | pass | 0 |
| T-switch + OTA buffer | 4 K proxy | 20 | 3.61 [2.89, 4.06] | pass | 4.65 | 0 | 2.75 [2.21, 3.32] | pass | 0 |
| T-switch + OTA buffer | 77 K proxy | 20 | 3.50 [2.77, 3.99] | pass | 4.57 | 0 | 2.71 [2.19, 3.26] | pass | 0 |
| T-switch + OTA buffer | 4 K high | 20 | 3.69 [2.96, 4.16] | pass | 4.76 | 0 | 2.74 [2.26, 3.41] | pass | 0 |
| T-switch + OTA buffer | 77 K Beall fit | 20 | 3.59 [2.81, 4.06] | pass | 4.59 | 0 | 2.66 [2.15, 3.28] | pass | 0 |
| TG + dummies | 300 K | 20 | 6.00 [5.22, 7.30] | pass | 9.29 | 0 | 4.24 [3.51, 5.49] | pass | 0 |
| T-switch + OTA buffer | 4 K, Beall pMOS | 20 | 3.76 [2.89, 4.06] | pass | 4.70 | 0 | 2.77 [2.20, 3.33] | pass | 0 |
| TG + dummies | 4 K proxy | 20 | 6.91 [5.60, 8.38] | pass | 9.69 | 0 | 4.55 [3.67, 6.03] | pass | 0 |
| TG + dummies | 4 K proxy (100 channels) | 100 | 7.43 [6.67, 8.06] | pass | 10.09 | 0 | 5.45 [4.83, 5.96] | pass | 0 |
| TG + dummies | 77 K proxy | 20 | 6.79 [5.46, 8.07] | pass | 9.54 | 0 | 4.60 [3.68, 5.81] | pass | 0 |
| TG + dummies | 4 K high | 20 | 7.33 [5.86, 8.78] | pass | 9.72 | 0 | 4.73 [3.79, 6.25] | pass | 0 |
| TG + dummies | 77 K Beall fit | 20 | 20.21 [15.24, 25.83] | pass | 25.18 | 0 | 10.55 [8.48, 15.20] | pass | 0 |
| TG + dummies | 4 K, Beall pMOS | 20 | 22.12 [17.04, 28.93] | pass | 27.54 | 0 | 10.96 [8.48, 15.61] | pass | 0 |
| TG, no ESD | 300 K | 20 | 7.74 [6.76, 9.00] | pass | 8.87 | 0 | 6.07 [4.97, 7.83] | pass | 0 |
| TG, no ESD | 77 K proxy | 20 | 7.24 [6.46, 8.45] | pass | 8.37 | 0 | 5.80 [4.83, 7.39] | pass | 0 |
| TG, no ESD | 4 K proxy | 20 | 7.09 [6.38, 8.17] | pass | 7.65 | 0 | 5.62 [4.79, 7.13] | pass | 0 |
| TG, no ESD | 4 K high | 20 | 7.04 [6.32, 8.18] | pass | 7.25 | 0 | 5.64 [4.78, 7.21] | pass | 0 |
| TG, no ESD | 77 K Beall fit | 20 | 17.27 [15.68, 19.82] | pass | 18.76 | 0 | 14.57 [12.85, 16.70] | pass | 0 |
| TG, no ESD | 4 K, Beall pMOS | 20 | 18.47 [17.00, 20.16] | pass | 18.32 | 0 | 17.19 [14.90, 18.28] | pass | 0 |
| TG, ESD on the node | 300 K | 20 | 8.52 [7.75, 10.29] | pass | 10.07 | 0 | 6.72 [5.79, 8.97] | pass | 0 |
| TG, ESD on the node | 77 K proxy | 20 | 8.32 [7.38, 9.69] | pass | 9.56 | 0 | 6.58 [5.56, 8.42] | pass | 0 |
| TG, ESD on the node | 4 K proxy | 20 | 8.11 [7.33, 9.42] | pass | 8.73 | 0 | 6.42 [5.54, 8.18] | pass | 0 |
| TG, ESD on the node | 4 K high | 20 | 8.46 [7.71, 9.51] | pass | 8.70 | 0 | 6.71 [5.74, 8.55] | pass | 0 |
| TG, ESD on the node | 77 K Beall fit | 20 | 45.60 [38.15, 56.10] | pass | 51.60 | 0 | 33.61 [27.63, 40.63] | pass | 0 |
| TG, ESD on the node | 4 K, Beall pMOS | 20 | 55.21 [45.03, 79.38] | pass | 68.35 | 0 | 35.90 [28.40, 47.53] | pass | 0 |

### Validation on 100 SPICE channels (4 K band)

| design | KS p (surrogate vs SPICE per-channel residual) | p90 surrogate / SPICE (µV) | p99 surrogate / SPICE (µV) |
|---|---|---|---|
| bootstrapped (transistor level), 0.3 V underdrive|4 K proxy (100 channels) | 0.52 | 67.0 / 68.0 | 88.4 / 75.0 |
| TG + dummies|4 K proxy (100 channels) | 0.96 | 70.6 / 70.3 | 101.0 / 92.5 |
