## Worst-of-10^6 margins from a Gaussian-copula surrogate (10^7 synthetic channels), 90 % bootstrap interval

Margin = budget / error of the worst of 10^6 channels (median of the maximum). Budgets (µV): s33.69_t0.0001: per gate 168, operational 129; s33.69_t0.001: per gate 524, operational 404; s10_t0.001: per gate 1373, operational 1361; s10_t0.0001: per gate 437, operational 435

Class: pass if the whole 90 % interval is above one, fail if below, otherwise indeterminate. Exceed: expected number of channels in 10^6 above the budget.

### Operational budget at s33.69_t0.0001 (129 µV)

| design | band | n | per-channel margin [90 % CI] | class | rev. 2 Gaussian | exceed / 10^6 | shared margin [90 % CI] | class | exceed / 10^6 |
|---|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 20 | 4.50 [3.67, 5.26] | pass | 6.21 | 0 | 4.15 [3.47, 4.49] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 20 | 0.78 [0.69, 0.87] | fail | 0.88 | 377 | 0.49 [0.43, 0.63] | fail | 4.11e+04 |
| T-switch + OTA buffer | 4 K, steep (T_eff 120 K) | 20 | 0.32 [0.25, 0.36] | fail | 0.42 | 2.89e+05 | 0.24 [0.20, 0.29] | fail | 5.47e+05 |
| TG + dummies | 4 K, steep (T_eff 120 K) | 20 | 0.56 [0.47, 0.66] | fail | 0.77 | 8.06e+03 | 0.43 [0.34, 0.52] | fail | 5.08e+04 |
| TG, no ESD | 4 K, steep (T_eff 120 K) | 20 | 0.67 [0.60, 0.79] | fail | 0.86 | 9.66e+03 | 0.56 [0.47, 0.71] | fail | 3.51e+04 |
| TG, ESD on the node | 4 K, steep (T_eff 120 K) | 20 | 0.76 [0.68, 0.88] | fail | 0.96 | 1.29e+03 | 0.64 [0.53, 0.79] | fail | 1.04e+04 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 30 K) | 20 | 4.65 [3.78, 5.55] | pass | 6.85 | 0 | 4.14 [3.33, 4.47] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 30 K) | 20 | 0.73 [0.65, 0.80] | fail | 0.84 | 4.35e+03 | 0.56 [0.49, 0.64] | fail | 6.03e+04 |
| TG + dummies | 4 K, steep (T_eff 30 K) | 20 | 0.53 [0.45, 0.62] | fail | 0.73 | 1.21e+04 | 0.40 [0.32, 0.50] | fail | 6.17e+04 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 20 | 4.47 [3.83, 5.58] | pass | 6.82 | 0 | 4.14 [3.34, 4.46] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 20 | 0.78 [0.68, 0.88] | fail | 0.98 | 565 | 0.64 [0.54, 0.72] | fail | 8.29e+03 |
| TG + dummies | 4 K, steep (T_eff 20 K) | 20 | 0.51 [0.44, 0.63] | fail | 0.73 | 1.27e+04 | 0.40 [0.32, 0.50] | fail | 6.34e+04 |
| NMOS, 0.3 V underdrive | 4 K, clock edge 600 ps | 20 | 5.00 [4.17, 5.96] | pass | 6.40 | 0 | 4.73 [3.97, 5.20] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 600 ps | 20 | 0.69 [0.60, 0.79] | fail | 0.82 | 2.22e+03 | 0.42 [0.36, 0.55] | fail | 7.62e+04 |
| TG + dummies | 4 K, clock edge 600 ps | 20 | 0.66 [0.53, 0.81] | fail | 0.92 | 1.26e+03 | 0.45 [0.35, 0.57] | fail | 3.26e+04 |
| NMOS, 0.3 V underdrive | 4 K, clock edge 67 ps | 20 | 5.00 [4.02, 5.77] | pass | 6.06 | 0 | 4.66 [3.81, 5.03] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 67 ps | 20 | 0.84 [0.73, 0.97] | fail | 1.06 | 50 | 0.53 [0.47, 0.67] | fail | 1.51e+04 |
| TG + dummies | 4 K, clock edge 67 ps | 20 | 0.65 [0.53, 0.79] | fail | 0.92 | 1.33e+03 | 0.44 [0.34, 0.57] | fail | 3.34e+04 |
| NMOS, 0.3 V underdrive | 4 K, tree source | 20 | 5.14 [4.15, 5.93] | pass | 6.37 | 0 | 4.78 [3.88, 5.18] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree source | 20 | 0.41 [0.34, 0.50] | fail | 0.48 | 9.37e+04 | 0.25 [0.20, 0.34] | fail | 3.22e+05 |
| TG + dummies | 4 K, tree source | 20 | 0.68 [0.54, 0.79] | fail | 0.92 | 1.24e+03 | 0.44 [0.36, 0.57] | fail | 3.24e+04 |
| NMOS, 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 20 | 5.15 [4.17, 5.87] | pass | 6.37 | 0 | 4.77 [3.92, 5.16] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 20 | 0.40 [0.33, 0.50] | fail | 0.47 | 1.01e+05 | 0.24 [0.20, 0.33] | fail | 3.32e+05 |
| T-switch + OTA buffer | 4 K, tree, ESD-dominated droop | 20 | 0.35 [0.27, 0.40] | fail | 0.44 | 2.23e+05 | 0.26 [0.21, 0.32] | fail | 4.69e+05 |
| TG + dummies | 4 K, tree, ESD-dominated droop | 20 | 0.66 [0.53, 0.81] | fail | 0.92 | 1.24e+03 | 0.44 [0.35, 0.57] | fail | 3.24e+04 |
| TG, no ESD | 4 K, tree, ESD-dominated droop | 20 | 0.68 [0.61, 0.79] | fail | 0.74 | 3.35e+04 | 0.55 [0.46, 0.69] | fail | 7.63e+04 |
| TG, ESD on the node | 4 K, tree, ESD-dominated droop | 20 | 0.77 [0.71, 0.91] | fail | 0.85 | 3.12e+03 | 0.62 [0.53, 0.79] | fail | 2.29e+04 |
| NMOS, 0.3 V underdrive | 4 K, tree, one reticle | 20 | 5.00 [4.19, 5.89] | pass | 6.37 | 0 | 4.78 [3.95, 5.18] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, one reticle | 20 | 0.33 [0.28, 0.44] | fail | 0.39 | 1.78e+05 | 0.21 [0.17, 0.29] | fail | 4.34e+05 |
| T-switch + OTA buffer | 4 K, tree, one reticle | 20 | 0.35 [0.28, 0.39] | fail | 0.45 | 2.19e+05 | 0.26 [0.21, 0.32] | fail | 4.63e+05 |
| TG + dummies | 4 K, tree, one reticle | 20 | 0.68 [0.53, 0.79] | fail | 0.92 | 1.25e+03 | 0.44 [0.36, 0.58] | fail | 3.23e+04 |
| TG, no ESD | 4 K, tree, one reticle | 20 | 0.69 [0.61, 0.79] | fail | 0.74 | 3.35e+04 | 0.54 [0.46, 0.69] | fail | 7.62e+04 |
| TG, ESD on the node | 4 K, tree, one reticle | 20 | 0.78 [0.70, 0.90] | fail | 0.85 | 3.12e+03 | 0.61 [0.53, 0.79] | fail | 2.29e+04 |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 1.5 | 20 | 3.41 [2.76, 3.99] | pass | 4.43 | 0 | 3.16 [2.57, 3.44] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, mismatch x 1.5 | 20 | 0.48 [0.41, 0.57] | fail | 0.60 | 4.03e+04 | 0.29 [0.24, 0.38] | fail | 2.25e+05 |
| TG + dummies | 4 K, mismatch x 1.5 | 20 | 0.44 [0.36, 0.53] | fail | 0.62 | 4.27e+04 | 0.30 [0.23, 0.38] | fail | 1.98e+05 |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 2 | 20 | 2.63 [2.22, 3.26] | pass | 3.90 | 0 | 2.35 [1.92, 2.59] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, mismatch x 2 | 20 | 0.35 [0.29, 0.42] | fail | 0.43 | 1.65e+05 | 0.21 [0.17, 0.27] | fail | 4.3e+05 |
| TG + dummies | 4 K, mismatch x 2 | 20 | 0.33 [0.26, 0.40] | fail | 0.46 | 1.58e+05 | 0.22 [0.18, 0.28] | fail | 4.09e+05 |

### Operational budget at s33.69_t0.001 (404 µV)

| design | band | n | per-channel margin [90 % CI] | class | rev. 2 Gaussian | exceed / 10^6 | shared margin [90 % CI] | class | exceed / 10^6 |
|---|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 20 | 14.07 [11.49, 16.47] | pass | 19.45 | 0 | 12.99 [10.86, 14.06] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 20 | 2.44 [2.17, 2.72] | pass | 2.75 | 0 | 1.52 [1.34, 1.96] | pass | 0 |
| T-switch + OTA buffer | 4 K, steep (T_eff 120 K) | 20 | 1.01 [0.78, 1.14] | indeterminate | 1.31 | 0.4 | 0.76 [0.63, 0.92] | fail | 199 |
| TG + dummies | 4 K, steep (T_eff 120 K) | 20 | 1.74 [1.47, 2.05] | pass | 2.41 | 0 | 1.34 [1.05, 1.63] | pass | 0 |
| TG, no ESD | 4 K, steep (T_eff 120 K) | 20 | 2.10 [1.89, 2.46] | pass | 2.69 | 0 | 1.76 [1.46, 2.21] | pass | 0 |
| TG, ESD on the node | 4 K, steep (T_eff 120 K) | 20 | 2.39 [2.14, 2.76] | pass | 3.02 | 0 | 2.01 [1.65, 2.47] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 30 K) | 20 | 14.56 [11.82, 17.36] | pass | 21.42 | 0 | 12.96 [10.43, 13.97] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 30 K) | 20 | 2.28 [2.03, 2.50] | pass | 2.63 | 0 | 1.74 [1.53, 2.00] | pass | 0 |
| TG + dummies | 4 K, steep (T_eff 30 K) | 20 | 1.67 [1.40, 1.95] | pass | 2.29 | 0 | 1.26 [1.01, 1.56] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 20 | 13.99 [11.97, 17.47] | pass | 21.36 | 0 | 12.95 [10.46, 13.96] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 20 | 2.44 [2.14, 2.74] | pass | 3.06 | 0 | 2.01 [1.70, 2.24] | pass | 0 |
| TG + dummies | 4 K, steep (T_eff 20 K) | 20 | 1.60 [1.38, 1.97] | pass | 2.28 | 0 | 1.26 [1.00, 1.56] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, clock edge 600 ps | 20 | 15.66 [13.05, 18.67] | pass | 20.04 | 0 | 14.79 [12.42, 16.26] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 600 ps | 20 | 2.17 [1.88, 2.48] | pass | 2.58 | 0 | 1.31 [1.12, 1.72] | pass | 0 |
| TG + dummies | 4 K, clock edge 600 ps | 20 | 2.05 [1.66, 2.53] | pass | 2.87 | 0 | 1.41 [1.10, 1.80] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, clock edge 67 ps | 20 | 15.65 [12.58, 18.07] | pass | 18.97 | 0 | 14.57 [11.92, 15.73] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 67 ps | 20 | 2.64 [2.29, 3.03] | pass | 3.33 | 0 | 1.67 [1.48, 2.08] | pass | 0 |
| TG + dummies | 4 K, clock edge 67 ps | 20 | 2.04 [1.65, 2.48] | pass | 2.87 | 0 | 1.37 [1.08, 1.77] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, tree source | 20 | 16.09 [12.97, 18.56] | pass | 19.95 | 0 | 14.95 [12.16, 16.20] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree source | 20 | 1.27 [1.05, 1.56] | pass | 1.51 | 0 | 0.77 [0.64, 1.05] | indeterminate | 216 |
| TG + dummies | 4 K, tree source | 20 | 2.14 [1.68, 2.48] | pass | 2.89 | 0 | 1.38 [1.12, 1.79] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 20 | 16.11 [13.05, 18.38] | pass | 19.95 | 0 | 14.93 [12.26, 16.15] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 20 | 1.26 [1.04, 1.57] | pass | 1.48 | 0 | 0.76 [0.62, 1.03] | indeterminate | 274 |
| T-switch + OTA buffer | 4 K, tree, ESD-dominated droop | 20 | 1.08 [0.84, 1.24] | indeterminate | 1.38 | 0.1 | 0.83 [0.65, 0.99] | fail | 56.2 |
| TG + dummies | 4 K, tree, ESD-dominated droop | 20 | 2.08 [1.66, 2.53] | pass | 2.89 | 0 | 1.37 [1.10, 1.80] | pass | 0 |
| TG, no ESD | 4 K, tree, ESD-dominated droop | 20 | 2.14 [1.90, 2.48] | pass | 2.32 | 0 | 1.71 [1.42, 2.16] | pass | 0 |
| TG, ESD on the node | 4 K, tree, ESD-dominated droop | 20 | 2.41 [2.21, 2.84] | pass | 2.65 | 0 | 1.93 [1.66, 2.49] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, tree, one reticle | 20 | 15.64 [13.12, 18.45] | pass | 19.95 | 0 | 14.95 [12.37, 16.22] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, one reticle | 20 | 1.05 [0.87, 1.37] | indeterminate | 1.23 | 0.2 | 0.64 [0.53, 0.90] | fail | 2.27e+03 |
| T-switch + OTA buffer | 4 K, tree, one reticle | 20 | 1.11 [0.87, 1.21] | indeterminate | 1.42 | 0 | 0.82 [0.66, 1.00] | indeterminate | 53.4 |
| TG + dummies | 4 K, tree, one reticle | 20 | 2.13 [1.67, 2.48] | pass | 2.89 | 0 | 1.37 [1.12, 1.80] | pass | 0 |
| TG, no ESD | 4 K, tree, one reticle | 20 | 2.15 [1.92, 2.48] | pass | 2.32 | 0 | 1.69 [1.44, 2.17] | pass | 0 |
| TG, ESD on the node | 4 K, tree, one reticle | 20 | 2.43 [2.20, 2.82] | pass | 2.65 | 0 | 1.91 [1.65, 2.47] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 1.5 | 20 | 10.68 [8.63, 12.49] | pass | 13.85 | 0 | 9.89 [8.03, 10.75] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, mismatch x 1.5 | 20 | 1.51 [1.27, 1.77] | pass | 1.87 | 0 | 0.90 [0.74, 1.18] | indeterminate | 13.7 |
| TG + dummies | 4 K, mismatch x 1.5 | 20 | 1.37 [1.11, 1.66] | pass | 1.93 | 0 | 0.93 [0.72, 1.19] | indeterminate | 5.7 |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 2 | 20 | 8.24 [6.95, 10.19] | pass | 12.22 | 0 | 7.35 [6.00, 8.10] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, mismatch x 2 | 20 | 1.08 [0.92, 1.30] | indeterminate | 1.36 | 0.2 | 0.65 [0.55, 0.85] | fail | 1.93e+03 |
| TG + dummies | 4 K, mismatch x 2 | 20 | 1.03 [0.83, 1.25] | indeterminate | 1.45 | 0.3 | 0.68 [0.55, 0.89] | fail | 707 |

### Operational budget at s10_t0.001 (1361 µV)

| design | band | n | per-channel margin [90 % CI] | class | rev. 2 Gaussian | exceed / 10^6 | shared margin [90 % CI] | class | exceed / 10^6 |
|---|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 20 | 47.44 [38.73, 55.52] | pass | 65.57 | 0 | 43.79 [36.61, 47.42] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 20 | 8.24 [7.30, 9.16] | pass | 9.27 | 0 | 5.12 [4.52, 6.61] | pass | 0 |
| T-switch + OTA buffer | 4 K, steep (T_eff 120 K) | 20 | 3.41 [2.64, 3.83] | pass | 4.41 | 0 | 2.56 [2.11, 3.11] | pass | 0 |
| TG + dummies | 4 K, steep (T_eff 120 K) | 20 | 5.88 [4.95, 6.93] | pass | 8.11 | 0 | 4.51 [3.54, 5.50] | pass | 0 |
| TG, no ESD | 4 K, steep (T_eff 120 K) | 20 | 7.09 [6.38, 8.30] | pass | 9.07 | 0 | 5.94 [4.93, 7.45] | pass | 0 |
| TG, ESD on the node | 4 K, steep (T_eff 120 K) | 20 | 8.04 [7.21, 9.30] | pass | 10.18 | 0 | 6.77 [5.55, 8.32] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 30 K) | 20 | 49.08 [39.86, 58.54] | pass | 72.24 | 0 | 43.70 [35.18, 47.12] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 30 K) | 20 | 7.70 [6.84, 8.44] | pass | 8.85 | 0 | 5.88 [5.15, 6.73] | pass | 0 |
| TG + dummies | 4 K, steep (T_eff 30 K) | 20 | 5.63 [4.71, 6.58] | pass | 7.72 | 0 | 4.26 [3.39, 5.25] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 20 | 47.17 [40.37, 58.90] | pass | 72.01 | 0 | 43.67 [35.27, 47.07] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 20 | 8.24 [7.22, 9.24] | pass | 10.32 | 0 | 6.77 [5.73, 7.56] | pass | 0 |
| TG + dummies | 4 K, steep (T_eff 20 K) | 20 | 5.39 [4.65, 6.64] | pass | 7.68 | 0 | 4.25 [3.38, 5.25] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, clock edge 600 ps | 20 | 52.81 [44.02, 62.94] | pass | 67.56 | 0 | 49.86 [41.89, 54.82] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 600 ps | 20 | 7.32 [6.33, 8.37] | pass | 8.69 | 0 | 4.42 [3.79, 5.80] | pass | 0 |
| TG + dummies | 4 K, clock edge 600 ps | 20 | 6.92 [5.60, 8.53] | pass | 9.66 | 0 | 4.74 [3.71, 6.07] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, clock edge 67 ps | 20 | 52.77 [42.42, 60.91] | pass | 63.95 | 0 | 49.13 [40.20, 53.03] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 67 ps | 20 | 8.91 [7.72, 10.20] | pass | 11.23 | 0 | 5.64 [4.98, 7.02] | pass | 0 |
| TG + dummies | 4 K, clock edge 67 ps | 20 | 6.89 [5.56, 8.37] | pass | 9.67 | 0 | 4.62 [3.64, 5.96] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, tree source | 20 | 54.27 [43.75, 62.60] | pass | 67.25 | 0 | 50.40 [40.99, 54.61] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree source | 20 | 4.29 [3.55, 5.25] | pass | 5.09 | 0 | 2.60 [2.14, 3.54] | pass | 0 |
| TG + dummies | 4 K, tree source | 20 | 7.20 [5.67, 8.36] | pass | 9.74 | 0 | 4.66 [3.78, 6.04] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 20 | 54.31 [44.01, 61.98] | pass | 67.25 | 0 | 50.34 [41.35, 54.46] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 20 | 4.25 [3.50, 5.30] | pass | 4.99 | 0 | 2.58 [2.10, 3.47] | pass | 0 |
| T-switch + OTA buffer | 4 K, tree, ESD-dominated droop | 20 | 3.65 [2.84, 4.17] | pass | 4.67 | 0 | 2.79 [2.20, 3.35] | pass | 0 |
| TG + dummies | 4 K, tree, ESD-dominated droop | 20 | 7.01 [5.61, 8.53] | pass | 9.74 | 0 | 4.63 [3.70, 6.05] | pass | 0 |
| TG, no ESD | 4 K, tree, ESD-dominated droop | 20 | 7.20 [6.42, 8.37] | pass | 7.84 | 0 | 5.78 [4.80, 7.27] | pass | 0 |
| TG, ESD on the node | 4 K, tree, ESD-dominated droop | 20 | 8.12 [7.44, 9.56] | pass | 8.94 | 0 | 6.51 [5.61, 8.38] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, tree, one reticle | 20 | 52.73 [44.25, 62.20] | pass | 67.25 | 0 | 50.40 [41.72, 54.69] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, one reticle | 20 | 3.53 [2.93, 4.63] | pass | 4.16 | 0 | 2.17 [1.77, 3.05] | pass | 0 |
| T-switch + OTA buffer | 4 K, tree, one reticle | 20 | 3.73 [2.94, 4.08] | pass | 4.77 | 0 | 2.77 [2.23, 3.37] | pass | 0 |
| TG + dummies | 4 K, tree, one reticle | 20 | 7.18 [5.62, 8.37] | pass | 9.74 | 0 | 4.63 [3.78, 6.07] | pass | 0 |
| TG, no ESD | 4 K, tree, one reticle | 20 | 7.25 [6.46, 8.37] | pass | 7.84 | 0 | 5.71 [4.85, 7.30] | pass | 0 |
| TG, ESD on the node | 4 K, tree, one reticle | 20 | 8.20 [7.40, 9.51] | pass | 8.94 | 0 | 6.44 [5.56, 8.31] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 1.5 | 20 | 36.01 [29.11, 42.11] | pass | 46.72 | 0 | 33.35 [27.09, 36.26] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, mismatch x 1.5 | 20 | 5.07 [4.28, 5.98] | pass | 6.32 | 0 | 3.02 [2.51, 3.99] | pass | 0 |
| TG + dummies | 4 K, mismatch x 1.5 | 20 | 4.62 [3.75, 5.61] | pass | 6.49 | 0 | 3.13 [2.44, 4.00] | pass | 0 |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 2 | 20 | 27.79 [23.43, 34.35] | pass | 41.19 | 0 | 24.77 [20.22, 27.30] | pass | 0 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, mismatch x 2 | 20 | 3.65 [3.11, 4.38] | pass | 4.57 | 0 | 2.18 [1.84, 2.87] | pass | 0 |
| TG + dummies | 4 K, mismatch x 2 | 20 | 3.47 [2.79, 4.20] | pass | 4.88 | 0 | 2.31 [1.85, 2.99] | pass | 0 |

### Validation on 100 SPICE channels (4 K band)

| design | KS p (surrogate vs SPICE per-channel residual) | p90 surrogate / SPICE (µV) | p99 surrogate / SPICE (µV) |
|---|---|---|---|
