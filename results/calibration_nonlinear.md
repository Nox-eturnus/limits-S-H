## Nonlinear calibration, calibration-point error and a common window

Closed-form worst-of-10^6 margins at the strictest point (99.99 %, 33.69 dec/V, untracked), levels set open-loop,
corrected for tau; [90 % bootstrap interval] and verdict (resolved outside 0.9 to 1.1).

| Design | Condition | line | line, noise | quadratic | quadratic, noise | shared | shared, noise | 0.4 V window, line (worst window) |
|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 300 K | 28.8 [27.8, 30.2] pass | 3.78 [3.78, 3.79] pass | 139 [134, 146] pass | 3.09 [3.09, 3.09] pass | 135 [112, 184] pass | 3.96 [3.96, 3.96] pass | 53.3 (0.5-0.9 V) |
| NMOS, 0.3 V underdrive | 77 K proxy | 37.5 [36, 39.9] pass | 3.63 [3.62, 3.63] pass | 172 [163, 184] pass | 2.98 [2.98, 2.98] pass | 164 [135, 245] pass | 3.73 [3.73, 3.73] pass | 53.4 (0.4-0.8 V) |
| NMOS, 0.3 V underdrive | 4 K proxy | 29.6 [28.4, 31.4] pass | 3.65 [3.65, 3.66] pass | 135 [130, 143] pass | 3.04 [3.04, 3.04] pass | 131 [107, 178] pass | 3.8 [3.8, 3.81] pass | 42 (0.4-0.8 V) |
| NMOS, 0.3 V underdrive | 4 K high | 23 [22.1, 24.3] pass | 3.51 [3.5, 3.52] pass | 109 [106, 113] pass | 2.97 [2.97, 2.97] pass | 108 [90.7, 155] pass | 3.73 [3.72, 3.73] pass | 32.6 (0.4-0.8 V) |
| NMOS, 0.3 V underdrive | 77 K Beall fit | 17 [16.5, 18] pass | 3.6 [3.59, 3.61] pass | 83.8 [81.8, 86.5] pass | 3.08 [3.08, 3.08] pass | 80.5 [66.4, 117] pass | 3.96 [3.95, 3.96] pass | 31.3 (0.5-0.9 V) |
| NMOS, 0.3 V underdrive | 4 K, Beall pMOS | 29 [27.8, 30.5] pass | 3.58 [3.57, 3.58] pass | 132 [127, 139] pass | 2.97 [2.97, 2.97] pass | 129 [107, 174] pass | 3.73 [3.73, 3.73] pass | 41.1 (0.4-0.8 V) |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 92.2 [88, 98] pass | 3.71 [3.7, 3.71] pass | 510 [458, 592] pass | 2.98 [2.98, 2.98] pass | 439 [360, 637] pass | 3.73 [3.73, 3.73] pass | 136 (0.4-0.8 V) |
| NMOS, 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 31.4 [30, 33.5] pass | 3.6 [3.59, 3.6] pass | 132 [126, 139] pass | 2.97 [2.97, 2.97] pass | 128 [106, 180] pass | 3.73 [3.73, 3.73] pass | 44 (0.4-0.8 V) |
| NMOS, 0.3 V underdrive | 4 K, tree, one reticle | 31.4 [29.8, 33.3] pass | 3.6 [3.59, 3.6] pass | 132 [127, 140] pass | 2.97 [2.97, 2.97] pass | 128 [105, 171] pass | 3.73 [3.73, 3.73] pass | 44 (0.4-0.8 V) |
| bootstrapped (transistor level), 0.3 V underdrive | 300 K | 10.6 [9.68, 11.8] pass | 3.34 [3.31, 3.38] pass | 255 [212, 331] pass | 3.09 [3.09, 3.09] pass | 28.8 [23.1, 45.6] pass | 3.92 [3.9, 3.94] pass | 73.9 (1.1-1.5 V) |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K proxy | 3.62 [3.37, 4] pass | 2.31 [2.25, 2.38] pass | 63.9 [58.9, 69.7] pass | 3.08 [3.07, 3.08] pass | 12.3 [9.62, 20.5] pass | 3.77 [3.68, 3.89] pass | 22.5 (1.1-1.5 V) |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy | 2.64 [2.57, 2.73] pass | 1.96 [1.93, 1.99] pass | 44.9 [43.6, 46.2] pass | 3.13 [3.13, 3.13] pass | 8.96 [8.22, 10.1] pass | 3.69 [3.63, 3.76] pass | 16.9 (1.1-1.5 V) |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K high | 2.59 [2.45, 2.75] pass | 1.9 [1.85, 1.94] pass | 44.5 [42.8, 46.3] pass | 3.05 [3.05, 3.05] pass | 10.2 [7.93, 15.4] pass | 3.67 [3.54, 3.81] pass | 17.1 (0.9-1.3 V) |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K Beall fit | 5.75 [5.13, 6.7] pass | 2.91 [2.82, 2.99] pass | 34.8 [32, 38.9] pass | 3.03 [3.03, 3.03] pass | 14.2 [10.7, 22.2] pass | 3.82 [3.72, 3.91] pass | 27.8 (1.1-1.5 V) |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, Beall pMOS | 5.48 [4.98, 6.17] pass | 2.82 [2.75, 2.88] pass | 43 [41.9, 44.3] pass | 3.04 [3.04, 3.05] pass | 15.8 [12.3, 23.7] pass | 3.84 [3.78, 3.91] pass | 29.2 (1.1-1.5 V) |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 2.01 [1.89, 2.17] pass | 1.62 [1.56, 1.67] pass | 10.6 [9.93, 11.7] pass | 2.82 [2.8, 2.84] pass | 7.15 [5.87, 10.4] pass | 3.49 [3.3, 3.73] pass | 8.08 (1.1-1.5 V) |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 2.11 [1.97, 2.31] pass | 1.68 [1.62, 1.74] pass | 31.1 [29.8, 32.7] pass | 3.02 [3.02, 3.03] pass | 7.14 [5.81, 10.3] pass | 3.45 [3.23, 3.71] pass | 13.7 (0.9-1.3 V) |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, one reticle | 2.02 [1.9, 2.25] pass | 1.64 [1.58, 1.72] pass | 30.9 [29.8, 32.4] pass | 3.02 [3.02, 3.03] pass | 6.4 [5.26, 10.2] pass | 3.35 [3.09, 3.66] pass | 13 (0.9-1.3 V) |
| T-switch + OTA buffer | 300 K | 9.34 [7.88, 11.5] pass | 3.59 [3.5, 3.67] pass | 17.8 [16.4, 19.9] pass | 2.99 [2.98, 3] pass | 10.8 [9.15, 14.5] pass | 3.71 [3.63, 3.8] pass | 20.5 (0.3-0.7 V) |
| T-switch + OTA buffer | 77 K proxy | 4.6 [4.26, 5.13] pass | 2.79 [2.71, 2.91] pass | 6.31 [5.18, 11.2] pass | 2.86 [2.84, 2.87] pass | 7.23 [5.57, 8.72] pass | 3.48 [3.38, 3.65] pass | 7.46 (0.3-0.7 V) |
| T-switch + OTA buffer | 4 K proxy | 4.91 [4.47, 5.67] pass | 2.88 [2.79, 3] pass | 6.85 [5.64, 11.5] pass | 2.87 [2.86, 2.89] pass | 7.43 [5.87, 8.74] pass | 3.48 [3.37, 3.63] pass | 8.15 (0.3-0.7 V) |
| T-switch + OTA buffer | 4 K high | 5.04 [4.55, 5.76] pass | 2.92 [2.83, 3.06] pass | 7.45 [6.13, 12.1] pass | 2.88 [2.87, 2.9] pass | 7.13 [6.18, 8.45] pass | 3.45 [3.32, 3.62] pass | 8.94 (0.3-0.7 V) |
| T-switch + OTA buffer | 77 K Beall fit | 5.61 [5.07, 6.56] pass | 3.07 [2.97, 3.22] pass | 11.3 [10.1, 15.3] pass | 2.93 [2.91, 2.94] pass | 8.05 [6.86, 10.4] pass | 3.53 [3.4, 3.68] pass | 13.4 (0.3-0.7 V) |
| T-switch + OTA buffer | 4 K, Beall pMOS | 5.68 [5.06, 6.82] pass | 3.12 [3, 3.28] pass | 12.6 [11.3, 15.5] pass | 2.94 [2.93, 2.95] pass | 7.56 [6.47, 9.59] pass | 3.49 [3.36, 3.64] pass | 14.9 (0.3-0.7 V) |
| T-switch + OTA buffer | 4 K, steep (T_eff 120 K) | 2.64 [2.3, 3.46] pass | 2.18 [1.98, 2.65] pass | 4.53 [4, 5.57] pass | 2.71 [2.64, 2.82] pass | 2.91 [2.59, 3.86] pass | 2.35 [2.16, 2.76] pass | 4.86 (0.3-0.7 V) |
| T-switch + OTA buffer | 4 K, tree, ESD-dominated droop | 5.46 [4.87, 6.15] pass | 3.45 [3.37, 3.54] pass | 6.95 [6.19, 8.18] pass | 3 [2.98, 3.01] pass | 5.85 [5, 6.62] pass | 3.6 [3.49, 3.72] pass | 8.78 (0.5-0.9 V) |
| T-switch + OTA buffer | 4 K, tree, one reticle | 6.86 [5.92, 8.93] pass | 3.62 [3.56, 3.67] pass | 10.4 [8.97, 11.7] pass | 3.02 [3.01, 3.03] pass | 6.59 [5.5, 8.94] pass | 3.67 [3.62, 3.75] pass | 10.7 (0.7-1.1 V) |
| TG + dummies | 300 K | 6.72 [5.58, 8.24] pass | 3.57 [3.44, 3.68] pass | 6.78 [5.67, 8.85] pass | 2.92 [2.86, 2.99] pass | 6.96 [5.89, 8.32] pass | 3.57 [3.47, 3.68] pass | 13.1 (0.5-0.9 V) |
| TG + dummies | 77 K proxy | 4.92 [4.15, 6.39] pass | 3.28 [3.07, 3.57] pass | 5.91 [5.21, 7.38] pass | 2.9 [2.83, 2.97] pass | 5.1 [4.31, 6.54] pass | 3.3 [3.1, 3.59] pass | 10.8 (0.5-0.9 V) |
| TG + dummies | 4 K proxy | 4.65 [4, 6.26] pass | 3.12 [2.9, 3.47] pass | 6.1 [5.34, 7.61] pass | 2.9 [2.83, 2.97] pass | 4.78 [3.97, 6.29] pass | 3.14 [2.93, 3.49] pass | 11.5 (0.5-0.9 V) |
| TG + dummies | 4 K high | 4.5 [3.74, 6.34] pass | 3.01 [2.72, 3.42] pass | 6.81 [5.89, 8.71] pass | 2.91 [2.86, 2.97] pass | 4.49 [3.83, 6.48] pass | 3 [2.77, 3.4] pass | 13.3 (0.5-0.9 V) |
| TG + dummies | 77 K Beall fit | 5.41 [4.68, 7.5] pass | 2.85 [2.76, 2.95] pass | 18.9 [16.8, 24.4] pass | 2.78 [2.78, 2.78] pass | 5.48 [4.84, 7.43] pass | 2.9 [2.87, 2.98] pass | 33.9 (0.5-0.9 V) |
| TG + dummies | 4 K, Beall pMOS | 7.61 [6.52, 10.1] pass | 2.84 [2.82, 2.85] pass | 56.5 [48.8, 72.3] pass | 2.75 [2.75, 2.75] pass | 8.38 [7.42, 10.7] pass | 2.85 [2.85, 2.86] pass | 75.2 (0.3-0.7 V) |
| TG + dummies | 4 K, steep (T_eff 120 K) | 2.75 [2.33, 3.59] pass | 2.5 [2.15, 3.07] pass | 3.19 [2.77, 4.1] pass | 2.51 [2.27, 2.79] pass | 2.81 [2.45, 3.65] pass | 2.54 [2.23, 3.15] pass | 104 (0.3-0.7 V) |
| TG + dummies | 4 K, tree, ESD-dominated droop | 5.09 [4.24, 6.57] pass | 3.26 [3.01, 3.58] pass | 6.76 [5.7, 8.52] pass | 2.96 [2.91, 3.01] pass | 4.8 [4.03, 6.28] pass | 3.14 [2.94, 3.46] pass | 12.6 (0.5-0.9 V) |
| TG + dummies | 4 K, tree, one reticle | 5.09 [4.3, 6.52] pass | 3.26 [3, 3.52] pass | 6.76 [5.84, 8.69] pass | 2.96 [2.91, 3.01] pass | 4.8 [4.07, 6.49] pass | 3.14 [2.94, 3.48] pass | 12.6 (0.5-0.9 V) |
| TG, no ESD | 300 K | 1.05 [1.04, 1.07] unresolved | 0.927 [0.92, 0.934] unresolved | 4.24 [3.88, 4.66] pass | 2.44 [2.42, 2.47] pass | 14 [10.6, 18.2] pass | 4.09 [4.02, 4.16] pass | 4.35 (0.5-0.9 V) |
| TG, no ESD | 77 K proxy | 1.09 [1.06, 1.11] unresolved | 0.945 [0.937, 0.954] unresolved | 7.17 [6.96, 7.48] pass | 2.8 [2.79, 2.82] pass | 10.5 [8.11, 14.8] pass | 3.73 [3.61, 3.86] pass | 5.15 (0.7-1.1 V) |
| TG, no ESD | 4 K proxy | 1.02 [1.01, 1.03] unresolved | 0.892 [0.889, 0.895] fail | 4.58 [4.39, 4.8] pass | 2.39 [2.38, 2.41] pass | 7.05 [6.35, 7.98] pass | 3.52 [3.44, 3.62] pass | 4.68 (0.9-1.3 V) |
| TG, no ESD | 4 K high | 0.983 [0.955, 1.01] unresolved | 0.878 [0.867, 0.889] fail | 3.39 [3.3, 3.53] pass | 2.17 [2.15, 2.18] pass | 7.88 [5.83, 12.9] pass | 3.74 [3.56, 3.94] pass | 3.99 (0.9-1.3 V) |
| TG, no ESD | 77 K Beall fit | 2.02 [1.99, 2.08] pass | 1.61 [1.6, 1.62] pass | 19.1 [17.8, 21.3] pass | 2.77 [2.77, 2.77] pass | 12.4 [10.7, 16.2] pass | 3.04 [3.03, 3.05] pass | 11.5 (0.5-0.9 V) |
| TG, no ESD | 4 K, Beall pMOS | 2.04 [2.02, 2.07] pass | 1.67 [1.66, 1.69] pass | 27.4 [26, 29.4] pass | 2.75 [2.75, 2.75] pass | 19.9 [17.4, 25.5] pass | 2.87 [2.87, 2.87] pass | 26.1 (0.3-0.7 V) |
| TG, no ESD | 4 K, steep (T_eff 120 K) | 1.13 [1.08, 1.19] unresolved | 1.04 [1.02, 1.06] unresolved | 4.72 [3.86, 6.06] pass | 2.81 [2.68, 2.86] pass | 6.29 [5.11, 8.89] pass | 3.62 [3.5, 3.74] pass | 28 (1.1-1.5 V) |
| TG, no ESD | 4 K, tree, ESD-dominated droop | 1.02 [0.998, 1.05] unresolved | 0.899 [0.89, 0.907] unresolved | 5.63 [5.28, 5.94] pass | 2.48 [2.47, 2.5] pass | 9.78 [7.59, 15.1] pass | 3.7 [3.57, 3.85] pass | 5 (0.9-1.3 V) |
| TG, no ESD | 4 K, tree, one reticle | 1.02 [1, 1.05] unresolved | 0.899 [0.89, 0.908] unresolved | 5.63 [5.23, 5.95] pass | 2.48 [2.46, 2.5] pass | 9.78 [7.6, 14.8] pass | 3.7 [3.56, 3.85] pass | 5 (0.9-1.3 V) |
| TG, ESD on the node | 300 K | 1.1 [1.08, 1.12] unresolved | 0.949 [0.942, 0.957] unresolved | 4.47 [4.1, 4.89] pass | 2.36 [2.33, 2.38] pass | 15 [11.4, 18.2] pass | 3.84 [3.79, 3.89] pass | 4.58 (0.5-0.9 V) |
| TG, ESD on the node | 77 K proxy | 1.23 [1.2, 1.26] pass | 1.05 [1.04, 1.05] unresolved | 8.46 [8.23, 8.85] pass | 2.87 [2.85, 2.89] pass | 12 [9.24, 17.6] pass | 3.78 [3.68, 3.88] pass | 5.84 (0.7-1.1 V) |
| TG, ESD on the node | 4 K proxy | 1.16 [1.15, 1.16] pass | 0.989 [0.986, 0.992] unresolved | 5.35 [5.13, 5.61] pass | 2.5 [2.49, 2.52] pass | 8.09 [7.32, 9.05] pass | 3.62 [3.55, 3.7] pass | 5.36 (0.9-1.3 V) |
| TG, ESD on the node | 4 K high | 1.21 [1.17, 1.24] pass | 1.05 [1.03, 1.06] unresolved | 3.58 [3.5, 3.68] pass | 2.22 [2.21, 2.24] pass | 10.1 [8.02, 15.7] pass | 3.69 [3.6, 3.79] pass | 7.56 (1.1-1.5 V) |
| TG, ESD on the node | 77 K Beall fit | 10.7 [10.3, 11.2] pass | 2.88 [2.87, 2.89] pass | 43.4 [42.4, 45] pass | 2.76 [2.76, 2.76] pass | 56.5 [47.7, 82.2] pass | 3.22 [3.22, 3.22] pass | 13.8 (0.5-0.9 V) |
| TG, ESD on the node | 4 K, Beall pMOS | 34.4 [32.8, 36.5] pass | 2.93 [2.93, 2.93] pass | 1e+04 [1e+04, 1e+04] pass | 2.66 [2.66, 2.66] pass | 145 [117, 220] pass | 2.96 [2.96, 2.96] pass | 34.4 (0.3-0.7 V) |
| TG, ESD on the node | 4 K, steep (T_eff 120 K) | 1.26 [1.21, 1.33] pass | 1.14 [1.12, 1.15] pass | 5.34 [4.32, 6.9] pass | 2.86 [2.78, 2.89] pass | 7.12 [5.57, 10.5] pass | 3.67 [3.59, 3.78] pass | 30.7 (1.1-1.5 V) |
| TG, ESD on the node | 4 K, tree, ESD-dominated droop | 1.16 [1.13, 1.19] pass | 0.997 [0.987, 1.01] unresolved | 6.59 [6.21, 6.98] pass | 2.58 [2.57, 2.6] pass | 11.2 [8.67, 17.2] pass | 3.76 [3.66, 3.88] pass | 5.71 (0.9-1.3 V) |
| TG, ESD on the node | 4 K, tree, one reticle | 1.16 [1.14, 1.19] pass | 0.997 [0.989, 1.01] unresolved | 6.59 [6.16, 6.99] pass | 2.58 [2.57, 2.6] pass | 11.2 [8.93, 17.2] pass | 3.76 [3.67, 3.88] pass | 5.71 (0.9-1.3 V) |
| GF180 NMOS, 0.3 V underdrive | 300 K | 541 [538, 545] pass | 3.96 [3.96, 3.96] pass | 1e+04 [1e+04, 1e+04] pass | 3.09 [3.09, 3.09] pass | 8.57e+03 [7.4e+03, 1e+04] pass | 3.96 [3.96, 3.96] pass | 1.33e+03 (0.4-0.8 V) |
| GF180 NMOS, 0.3 V underdrive | 4 K proxy | 661 [655, 673] pass | 3.96 [3.96, 3.96] pass | 1e+04 [1e+04, 1e+04] pass | 3.09 [3.09, 3.09] pass | 5.8e+03 [5.19e+03, 7.02e+03] pass | 3.96 [3.96, 3.96] pass | 1.59e+03 (0.5-0.9 V) |
| GF180 NMOS, 0.3 V underdrive | 4 K high | 620 [614, 631] pass | 3.96 [3.96, 3.96] pass | 1e+04 [1e+04, 1e+04] pass | 3.09 [3.09, 3.09] pass | 5.92e+03 [5.22e+03, 7.5e+03] pass | 3.96 [3.96, 3.96] pass | 1.48e+03 (0.5-0.9 V) |
| GF180 bootstrapped (transistor level), 0.3 V underdrive | 300 K | 34.6 [34.2, 35.1] pass | 3.8 [3.8, 3.81] pass | 194 [192, 197] pass | 3.09 [3.09, 3.09] pass | 299 [245, 405] pass | 3.96 [3.96, 3.96] pass | 143 (0.3-0.7 V) |
| GF180 bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy | 13.5 [13.4, 13.6] pass | 3.41 [3.41, 3.42] pass | 80 [79.1, 81.2] pass | 3.08 [3.08, 3.08] pass | 184 [152, 258] pass | 3.96 [3.96, 3.96] pass | 58.4 (0.3-0.7 V) |
| GF180 bootstrapped (transistor level), 0.3 V underdrive | 4 K high | 13.9 [13.8, 14] pass | 3.43 [3.43, 3.44] pass | 81.6 [80.4, 83.5] pass | 3.08 [3.08, 3.08] pass | 189 [157, 271] pass | 3.96 [3.96, 3.96] pass | 60.1 (0.3-0.7 V) |
| GF180 TG + dummies | 300 K | 5.39 [4.51, 7.09] pass | 3.43 [3.29, 3.59] pass | 6.58 [5.47, 8.42] pass | 2.89 [2.85, 2.95] pass | 5.81 [4.57, 8.57] pass | 3.57 [3.37, 3.79] pass | 9.19 (0.7-1.1 V) |
| GF180 TG + dummies | 4 K proxy | 5.15 [4.34, 6.98] pass | 3.39 [3.21, 3.62] pass | 6.68 [5.63, 8.89] pass | 2.99 [2.97, 3.02] pass | 5.43 [4.32, 8.09] pass | 3.47 [3.24, 3.71] pass | 8.81 (1.1-1.5 V) |
| GF180 TG + dummies | 4 K high | 5.49 [4.52, 7.46] pass | 3.4 [3.25, 3.61] pass | 7.74 [6.49, 9.82] pass | 3.04 [3.03, 3.06] pass | 5.74 [4.61, 8.18] pass | 3.44 [3.19, 3.71] pass | 9.57 (1.1-1.5 V) |
| GF180 TG, no ESD | 300 K | 0.586 [0.586, 0.586] fail | 0.534 [0.534, 0.534] fail | 2.26 [2.19, 2.33] pass | 1.79 [1.77, 1.8] pass | 9.58 [7.82, 13.7] pass | 3.84 [3.77, 3.9] pass | 2.2 (0.9-1.3 V) |
| GF180 TG, no ESD | 4 K proxy | 0.62 [0.618, 0.624] fail | 0.572 [0.57, 0.574] fail | 1.94 [1.93, 1.96] pass | 1.56 [1.56, 1.57] pass | 9.56 [7.94, 13.2] pass | 3.78 [3.7, 3.87] pass | 2.24 (0.9-1.3 V) |
| GF180 TG, no ESD | 4 K high | 0.66 [0.656, 0.667] fail | 0.609 [0.606, 0.611] fail | 2.13 [2.1, 2.18] pass | 1.56 [1.55, 1.56] pass | 9.61 [7.87, 13.9] pass | 3.75 [3.65, 3.86] pass | 2.33 (1.1-1.5 V) |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V | 300 K | 118 [118, 120] pass | 3.94 [3.94, 3.94] pass | 2.61e+03 [2.57e+03, 2.69e+03] pass | 3.09 [3.09, 3.09] pass | 1.37e+03 [1.19e+03, 1.69e+03] pass | 3.96 [3.96, 3.96] pass | 735 (1.1-1.5 V) |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V | 4 K proxy | 122 [120, 124] pass | 3.94 [3.94, 3.94] pass | 1.38e+03 [1.35e+03, 1.42e+03] pass | 3.09 [3.09, 3.09] pass | 976 [844, 1.27e+03] pass | 3.96 [3.96, 3.96] pass | 652 (1.1-1.5 V) |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V | 4 K high | 112 [111, 114] pass | 3.94 [3.94, 3.94] pass | 1.22e+03 [1.19e+03, 1.25e+03] pass | 3.09 [3.09, 3.09] pass | 911 [810, 1.17e+03] pass | 3.96 [3.96, 3.96] pass | 595 (1.1-1.5 V) |
| GF180 TG, no ESD, W 0.42 | 300 K | 1.41 [1.41, 1.41] pass | 1.13 [1.13, 1.13] pass | 5.76 [5.47, 6.15] pass | 2.53 [2.52, 2.54] pass | 16.6 [13.4, 23.8] pass | 3.92 [3.9, 3.94] pass | 5.47 (0.9-1.3 V) |
| GF180 TG, no ESD, W 0.42 | 4 K proxy | 1.45 [1.44, 1.46] pass | 1.18 [1.17, 1.18] pass | 4.57 [4.55, 4.62] pass | 2.37 [2.37, 2.38] pass | 14.9 [12.6, 21.6] pass | 3.89 [3.86, 3.93] pass | 5.03 (0.9-1.3 V) |
| GF180 TG, no ESD, W 0.42 | 4 K high | 1.52 [1.51, 1.54] pass | 1.23 [1.23, 1.24] pass | 4.73 [4.66, 4.84] pass | 2.32 [2.32, 2.33] pass | 15.8 [12.9, 22.1] pass | 3.88 [3.84, 3.92] pass | 5.57 (0.9-1.3 V) |

Smallest margin over the Figure 6 bands and trees (SKY130), per design and calibration:

| Design | line | line, noise | quadratic | quadratic, noise | shared | shared, noise | window | 99.9 %, 33.69: line / quadratic, noise | 99.9 %, 10: line / quadratic, noise |
|---|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 17 | 3.51 | 83.8 | 2.97 | 80.5 | 3.73 | 31.3 | 53.4 / 2.96 | 126 / 3.39 |
| bootstrapped (transistor level), 0.3 V underdrive | 2.01 | 1.62 | 10.6 | 2.82 | 6.4 | 3.35 | 8.08 | 6.29 / 3.03 | 15 / 3.51 |
| T-switch + OTA buffer | 2.64 | 2.18 | 4.53 | 2.71 | 2.91 | 2.35 | 4.86 | 8.24 / 3.02 | 21.4 / 3.51 |
| TG + dummies | 2.75 | 2.5 | 3.19 | 2.51 | 2.81 | 2.54 | 10.8 | 8.59 / 2.74 | 22.4 / 3.13 |
| TG, no ESD | 0.983 | 0.878 | 3.39 | 2.17 | 6.29 | 2.87 | 3.99 | 3.08 / 2.74 | 7.15 / 3.13 |
| TG, ESD on the node | 1.1 | 0.949 | 3.58 | 2.22 | 7.12 | 2.96 | 4.58 | 3.44 / 2.65 | 7.95 / 3.03 |
