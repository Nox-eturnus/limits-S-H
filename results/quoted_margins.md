## Margins quoted in the article (one cell per channel, before the tail correction)

Budgets: s33.69_t0.0001: b_eq 111 µV, b_ind 168 µV, s33.69_t0.001: b_eq 349 µV, b_ind 524 µV, s10_t0.001: b_eq 799 µV, b_ind 1373 µV, s10_t0.0001: b_eq 253 µV, b_ind 437 µV

### Equal sizing (strictest per-channel | shared | exceed | 99.9 % 33.69 | 10 dec/V | move 20 / 50 mV)

- NMOS, 0.3 V underdrive, W 1 | 4 K proxy (n 20, window [0.3, 0.8]): 13.39 [12.90, 14.09] pass | shared 3.63 [2.85, 5.09] pass | exceed 0 | 41.95 [40.38, 44.14] pass | 98.71 [95.45, 103.19] pass | 48.46 [46.73, 50.87] pass / 19.38 [18.69, 20.35] pass
- NMOS, 0.3 V underdrive, W 1 | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 0.9]): 7.55 [7.28, 7.96] pass | shared 3.66 [3.02, 5.02] pass | exceed 0 | 23.65 [22.79, 24.95] pass | 55.64 [53.93, 58.28] pass | 31.20 [30.23, 32.66] pass / 12.48 [12.09, 13.06] pass
- NMOS, 0.3 V underdrive, W 3 | 4 K proxy (n 20, window [0.3, 0.9]): 2.35 [2.33, 2.39] pass | shared 1.55 [1.33, 1.93] pass | exceed 0 | 7.38 [7.30, 7.49] pass | 17.12 [16.96, 17.33] pass | 9.96 [9.87, 10.08] pass / 3.98 [3.95, 4.03] pass
- NMOS, 0.3 V underdrive, W 3 | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 0.9]): 3.79 [3.71, 3.89] pass | shared 2.21 [1.83, 2.83] pass | exceed 0 | 11.86 [11.62, 12.17] pass | 27.75 [27.27, 28.38] pass | 14.61 [14.36, 14.94] pass / 5.85 [5.74, 5.98] pass
- NMOS, 0.3 V underdrive | 4 K proxy (n 20, window [0.3, 0.8]): 31.89 [30.61, 33.71] pass | shared 6.71 [5.59, 9.28] pass | exceed 0 | 99.86 [95.83, 105.59] pass | 236.38 [227.42, 248.17] pass | 82.97 [79.88, 87.26] pass / 44.82 [43.11, 47.20] pass
- NMOS, 0.3 V underdrive | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 0.8]): 34.44 [32.90, 36.58] pass | shared 6.91 [5.85, 9.33] pass | exceed 0 | 107.83 [102.96, 114.56] pass | 256.02 [245.32, 269.96] pass | 122.35 [116.90, 129.87] pass / 48.94 [46.76, 51.95] pass
- T-switch + OTA buffer, W 0.42 | 4 K proxy (n 20, window [0.3, 1.5]): 7.82 [7.16, 9.20] pass | shared 0.48 [0.39, 0.66] fail | exceed 0 | 24.40 [22.35, 28.71] pass | 63.21 [57.85, 74.26] pass | 68.82 [57.86, 77.81] pass / 27.53 [23.15, 31.12] pass
- T-switch + OTA buffer, W 0.42 | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 1.5]): 12.26 [10.26, 15.52] pass | shared 0.48 [0.39, 0.65] fail | exceed 0 | 38.25 [32.00, 48.43] pass | 100.12 [83.73, 126.80] pass | 103.08 [86.64, 123.87] pass / 41.23 [34.66, 49.55] pass
- T-switch + OTA buffer | 4 K proxy (n 20, window [0.3, 1.5]): 5.42 [4.95, 6.15] pass | shared 0.40 [0.34, 0.54] fail | exceed 0 | 16.92 [15.46, 19.21] pass | 42.47 [38.89, 48.12] pass | 22.77 [19.76, 28.53] pass / 11.52 [10.03, 15.09] pass
- T-switch + OTA buffer | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 1.5]): 5.98 [5.38, 6.80] pass | shared 0.41 [0.34, 0.52] fail | exceed 0 | 18.68 [16.80, 21.20] pass | 48.35 [43.59, 54.88] pass | 48.28 [42.50, 53.29] pass / 19.31 [17.00, 21.32] pass
- TG + dummies, W 0.84 | 4 K proxy (n 20, window [0.3, 1.5]): 3.90 [3.09, 6.42] pass | shared 0.64 [0.49, 1.15] indet | exceed 0 | 12.16 [9.64, 20.05] pass | 31.63 [25.05, 52.01] pass | 32.58 [25.70, 55.34] pass / 13.03 [10.28, 22.14] pass
- TG + dummies, W 0.84 | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 1.5]): 4.11 [3.16, 6.88] pass | shared 0.64 [0.48, 1.22] indet | exceed 0 | 12.83 [9.85, 21.47] pass | 33.46 [25.65, 56.13] pass | 35.00 [26.53, 60.96] pass / 14.00 [10.61, 24.38] pass
- TG + dummies | 4 K proxy (n 20, window [0.3, 1.5]): 5.25 [4.33, 6.72] pass | shared 0.75 [0.66, 0.96] fail | exceed 0 | 16.37 [13.50, 20.96] pass | 42.67 [35.08, 54.51] pass | 42.33 [35.28, 53.24] pass / 21.20 [17.68, 26.77] pass
- TG + dummies | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 1.5]): 5.61 [4.70, 7.52] pass | shared 0.76 [0.66, 0.97] fail | exceed 0 | 17.51 [14.65, 23.46] pass | 45.84 [38.34, 61.45] pass | 48.49 [40.74, 63.50] pass / 19.39 [16.29, 25.40] pass
- TG, ESD on the node | 4 K proxy (n 100, window [0.3, 1.5]): 1.27 [1.26, 1.28] pass | shared 0.78 [0.73, 0.84] fail | exceed 0 | 3.98 [3.95, 4.01] pass | 9.19 [9.14, 9.26] pass | 17.96 [17.57, 18.58] pass / 8.99 [8.79, 9.30] pass
- TG, ESD on the node | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 1.5]): 1.27 [1.25, 1.30] pass | shared 0.91 [0.82, 1.08] indet | exceed 0 | 3.99 [3.91, 4.08] pass | 9.24 [9.08, 9.41] pass | 12.74 [12.59, 12.95] pass / 5.10 [5.03, 5.18] pass
- TG, no ESD, W 0.42, 0.3 V underdrive | 4 K proxy (n 20, window [0.3, 1.5]): 2.75 [2.71, 2.82] pass | shared 1.28 [1.13, 1.58] pass | exceed 0 | 8.63 [8.48, 8.85] pass | 20.10 [19.79, 20.55] pass | 27.67 [27.03, 28.72] pass / 11.07 [10.81, 11.49] pass
- TG, no ESD, W 0.42, 0.3 V underdrive | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 1.5]): 2.77 [2.73, 2.84] pass | shared 1.29 [1.13, 1.61] pass | exceed 0 | 8.69 [8.56, 8.90] pass | 20.25 [19.96, 20.68] pass | 28.03 [27.32, 28.92] pass / 11.21 [10.93, 11.57] pass
- TG, no ESD, W 0.42 | 4 K proxy (n 20, window [0.3, 1.5]): 2.76 [2.72, 2.82] pass | shared 1.28 [1.13, 1.60] pass | exceed 0 | 8.65 [8.53, 8.84] pass | 20.16 [19.90, 20.54] pass | 27.77 [27.08, 28.68] pass / 11.11 [10.83, 11.47] pass
- TG, no ESD, W 0.42 | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 1.5]): 2.78 [2.73, 2.85] pass | shared 1.30 [1.13, 1.59] pass | exceed 0 | 8.72 [8.56, 8.93] pass | 20.31 [19.98, 20.74] pass | 28.14 [27.38, 29.13] pass / 11.25 [10.95, 11.65] pass
- TG, no ESD, W 3 | 4 K proxy (n 20, window [0.3, 1.5]): 0.38 [0.38, 0.38] fail | shared 0.27 [0.25, 0.30] fail | exceed 1e+06 | 1.20 [1.19, 1.21] pass | 2.75 [2.74, 2.77] pass | 3.67 [3.63, 3.71] pass / 1.47 [1.45, 1.48] pass
- TG, no ESD, W 3 | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 1.5]): 0.39 [0.39, 0.40] fail | shared 0.28 [0.26, 0.31] fail | exceed 1e+06 | 1.24 [1.23, 1.25] pass | 2.84 [2.83, 2.86] pass | 3.95 [3.89, 4.01] pass / 1.58 [1.56, 1.60] pass
- TG, no ESD | 4 K proxy (n 100, window [0.3, 1.5]): 1.12 [1.11, 1.13] pass | shared 0.68 [0.64, 0.73] fail | exceed 0 | 3.51 [3.48, 3.54] pass | 8.11 [8.05, 8.16] pass | 16.45 [16.00, 16.87] pass / 8.23 [8.00, 8.44] pass
- TG, no ESD | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 1.5]): 1.12 [1.10, 1.15] pass | shared 0.80 [0.71, 0.95] fail | exceed 0 | 3.52 [3.43, 3.61] pass | 8.14 [7.98, 8.32] pass | 11.19 [11.03, 11.40] pass / 4.47 [4.41, 4.56] pass
- bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy (n 100, window [0.3, 1.5]): 2.84 [2.76, 2.94] pass | shared 0.79 [0.74, 0.94] fail | exceed 0 | 8.90 [8.64, 9.22] pass | 21.26 [20.71, 21.95] pass | 28.17 [27.33, 29.07] pass / 14.36 [13.92, 14.80] pass
- bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 1.5]): 2.32 [2.16, 2.52] pass | shared 0.46 [0.35, 0.71] fail | exceed 0 | 7.25 [6.77, 7.90] pass | 17.35 [16.31, 18.69] pass | 22.18 [20.80, 24.06] pass / 8.87 [8.32, 9.63] pass
- bootstrapped (transistor level), W 1 | 4 K proxy (n 20, window [0.3, 1.5]): 1.60 [1.52, 1.70] pass | shared 0.63 [0.54, 0.83] fail | exceed 0 | 5.00 [4.77, 5.32] pass | 11.86 [11.39, 12.51] pass | 15.50 [14.80, 16.41] pass / 6.20 [5.92, 6.56] pass
- bootstrapped (transistor level), W 1 | 4 K, tree, ESD-dominated droop (n 20, window [0.3, 1.5]): 1.11 [1.06, 1.19] pass | shared 0.27 [0.20, 0.50] fail | exceed 0 | 3.47 [3.31, 3.73] pass | 8.25 [7.91, 8.74] pass | 10.91 [10.46, 11.61] pass / 4.36 [4.18, 4.65] pass

### Nine cells, 300 K (Table S3): per-channel | shared | exceed | 99.9 % 33.69 | 10 dec/V | shared 10 dec/V | move 50 mV

- D NSW: 18.10 [17.26, 19.20] pass | shared 4.19 [3.37, 5.88] pass | exceed 0 | 56.67 | 134.19 | 34.23 | 28.83 [27.57, 30.49] pass
- D TG: 1.20 [1.19, 1.22] pass | shared 1.00 [0.87, 1.08] indet | exceed 0 | 3.77 | 8.72 | 7.50 | 4.67 [4.58, 4.79] pass
- D TGD: 8.40 [7.06, 10.29] pass | shared 0.80 [0.70, 0.98] fail | exceed 0 | 26.21 | 68.31 | 6.50 | 23.02 [19.26, 29.30] pass
- D BOOT: 229.22 [218.22, 247.78] pass | shared 3.12 [2.81, 3.65] pass | exceed 0 | 717.00 | 1742.46 | 25.47 | 631.26 [610.53, 665.44] pass
- D CLK: 2.29 [2.26, 2.32] pass | shared 1.89 [1.68, 2.03] pass | exceed 0 | 7.17 | 16.58 | 14.17 | 8.94 [8.78, 9.20] pass
- D TSW: 8.29 [7.46, 9.73] pass | shared 0.33 [0.28, 0.42] fail | exceed 0 | 25.88 | 65.48 | 2.67 | 30.54 [27.78, 35.11] pass
- D TGH: 1.12 [1.11, 1.13] pass | shared 0.91 [0.84, 0.99] fail | exceed 0 | 3.51 | 8.10 | 6.89 | 4.99 [4.90, 5.09] pass
- D TSWB: 8.23 [7.45, 9.90] pass | shared 0.33 [0.28, 0.42] fail | exceed 0 | 25.72 | 65.03 | 2.66 | 30.23 [27.68, 35.32] pass
- D NTB: 4.16 [3.91, 4.69] pass | shared 1.21 [1.00, 1.71] pass | exceed 0 | 13.02 | 31.93 | 9.86 | 6.06 [5.75, 6.68] pass

### Table S6 (per-channel / shared at the strictest point; class)

| design | 300 K | 77 K proxy | 4 K proxy | 4 K high | 77 K Beall fit | 4 K, Beall pMOS | 4 K, steep (T_eff 120 K) | 4 K, tree, ESD-dominated droop | 4 K, tree, one reticle |
|---|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 31.66 / 6.29 pass | 41.18 / 6.64 pass | 31.89 / 6.71 pass | 25.23 / 6.60 pass | 18.71 / 6.11 pass | 31.87 / 6.64 pass | 101.20 / 6.47 pass | 34.44 / 6.91 pass | 34.45 / 6.90 pass |
| bootstrapped (transistor level), 0.3 V underdrive | 11.61 / 1.83 pass | 3.97 / 0.96 pass | 2.84 / 0.79 pass | 2.84 / 0.85 pass | 6.32 / 0.90 pass | 6.02 / 1.16 pass | 2.21 / 0.87 pass | 2.32 / 0.46 pass | 2.22 / 0.37 pass |
| T-switch + OTA buffer | 10.25 / 0.38 pass | 5.04 / 0.39 pass | 5.42 / 0.40 pass | 5.54 / 0.41 pass | 6.16 / 0.40 pass | 6.24 / 0.40 pass | 2.91 / 0.38 pass | 5.98 / 0.41 pass | 7.53 / 0.41 pass |
| TG + dummies | 7.37 / 0.69 pass | 5.38 / 0.73 pass | 5.25 / 0.75 pass | 4.97 / 0.78 pass | 5.94 / 1.98 pass | 8.34 / 1.93 pass | 3.03 / 0.70 pass | 5.61 / 0.76 pass | 5.63 / 0.76 pass |
| TG, no ESD | 1.07 / 0.89 pass | 1.19 / 0.82 pass | 1.12 / 0.68 pass | 1.04 / 0.77 pass | 2.22 / 1.75 pass | 2.24 / 1.76 pass | 1.24 / 0.88 pass | 1.12 / 0.80 pass | 1.12 / 0.80 pass |
| TG, ESD on the node | 1.20 / 1.00 pass | 1.35 / 0.93 pass | 1.27 / 0.78 pass | 1.32 / 0.95 pass | 11.73 / 4.06 pass | 37.76 / 4.46 pass | 1.38 / 0.99 pass | 1.27 / 0.91 pass | 1.27 / 0.91 pass |

### Table S7 (strictest (exceed) | 99.9 % 33.69)

| variant | NMOS, 0.3 V underdrive strictest | NMOS, 0.3 V underdrive 99.9 % | bootstrapped (transistor level), 0.3 V underdrive strictest | bootstrapped (transistor level), 0.3 V underdrive 99.9 % | TG + dummies strictest | TG + dummies 99.9 % |
|---|---|---|---|---|---|---|
| 4 K proxy | 31.89 pass (0) | 99.9 | 2.84 pass (0) | 8.9 | 5.25 pass (0) | 16.4 |
| 4 K, steep (T_eff 120 K) | 101.20 pass (0) | 317 | 2.21 pass (0) | 6.91 | 3.03 pass (0) | 9.46 |
| 4 K, steep (T_eff 30 K) | 169.03 pass (0) | 530 | 1.35 pass (0) | 4.23 | 2.71 pass (0) | 8.44 |
| 4 K, steep (T_eff 20 K) | 325.80 pass (0) | 1.02e+03 | 1.31 pass (0) | 4.08 | 2.68 pass (0) | 8.35 |
| 4 K, clock edge 600 ps | 34.32 pass (0) | 107 | 2.58 pass (0) | 8.08 | 5.57 pass (0) | 17.4 |
| 4 K, clock edge 67 ps | 30.98 pass (0) | 97 | 3.42 pass (0) | 10.7 | 4.97 pass (0) | 15.5 |
| 4 K, tree source | 34.44 pass (0) | 108 | 2.33 pass (0) | 7.3 | 5.62 pass (0) | 17.5 |
| 4 K, tree, ESD-dominated droop | 34.44 pass (0) | 108 | 2.32 pass (0) | 7.25 | 5.61 pass (0) | 17.5 |
| 4 K, tree, one reticle | 34.45 pass (0) | 108 | 2.22 pass (0) | 6.95 | 5.63 pass (0) | 17.6 |
| 4 K, tree, ESD diodes on 1 pF | – | – | 2.37 pass (0) | 7.43 | – | – |
| 4 K, buffered leaf line | – | – | 2.42 pass (0) | 7.56 | – | – |
| 4 K, mismatch x 1.5 | 29.83 pass (0) | 93.3 | 2.65 pass (0) | 8.3 | 3.73 pass (0) | 11.6 |
| 4 K, mismatch x 2 | 67.73 pass (0) | 212 | 2.40 pass (0) | 7.5 | 2.90 pass (0) | 9.05 |

### Moves from a tuned level, strictest point (fine grid where simulated)

| design | condition | move20mV | move50mV | move100mV | move200mV | full |
|---|---|---|---|---|---|---|
| D BOOT | 300 K | 1578.16 pass | 631.26 pass | 315.63 pass | 157.82 pass | 229.22 |
| D CLK | 300 K | 22.36 pass | 8.94 pass | 4.47 pass | 2.24 pass | 2.29 |
| D NSW | 300 K | 72.08 pass | 28.83 pass | 14.42 pass | 10.97 pass | 18.10 |
| D NTB | 300 K | 15.16 pass | 6.06 pass | 3.03 pass | 2.59 pass | 4.16 |
| D TGD | 300 K | 57.55 pass | 23.02 pass | 11.51 pass | 5.76 pass | 8.40 |
| D TGH | 300 K | 12.46 pass | 4.99 pass | 2.49 pass | 1.25 pass | 1.12 |
| D TG | 300 K | 11.69 pass | 4.67 pass | 2.34 pass | 1.17 pass | 1.20 |
| D TSWB | 300 K | 75.57 pass | 30.23 pass | 15.11 pass | 7.56 pass | 8.23 |
| D TSW | 300 K | 76.35 pass | 30.54 pass | 15.27 pass | 7.63 pass | 8.29 |
| NMOS, 0.3 V underdrive, W 1 | 4 K proxy | 48.46 pass | 19.38 pass | 9.69 pass | 7.55 pass | 13.39 |
| NMOS, 0.3 V underdrive, W 1 | 4 K, tree, ESD-dominated droop | 31.20 pass | 12.48 pass | 6.24 pass | 4.55 pass | 7.55 |
| NMOS, 0.3 V underdrive, W 3 | 4 K proxy | 9.96 pass | 3.98 pass | 1.99 pass | 1.41 pass | 2.35 |
| NMOS, 0.3 V underdrive, W 3 | 4 K, tree, ESD-dominated droop | 14.61 pass | 5.85 pass | 2.92 pass | 2.26 pass | 3.79 |
| NMOS, 0.3 V underdrive | 300 K | 131.12 pass | 52.45 pass | 26.22 pass | 19.38 pass | 31.66 |
| NMOS, 0.3 V underdrive | 4 K high | 91.24 pass | 36.50 pass | 18.25 pass | 14.22 pass | 25.23 |
| NMOS, 0.3 V underdrive | 4 K proxy (fine) | 82.97 pass | 44.82 pass | 22.93 pass | 18.06 pass | 31.89 |
| NMOS, 0.3 V underdrive | 4 K, Beall pMOS | 114.55 pass | 45.82 pass | 22.91 pass | 18.04 pass | 31.87 |
| NMOS, 0.3 V underdrive | 4 K, clock edge 600 ps | 120.79 pass | 48.31 pass | 24.16 pass | 19.44 pass | 34.32 |
| NMOS, 0.3 V underdrive | 4 K, clock edge 67 ps | 111.98 pass | 44.79 pass | 22.40 pass | 17.52 pass | 30.98 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 372.95 pass | 149.18 pass | 74.59 pass | 57.81 pass | 101.20 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 1061.41 pass | 424.57 pass | 212.28 pass | 164.72 pass | 325.80 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 30 K) | 669.68 pass | 267.87 pass | 133.94 pass | 94.49 pass | 169.03 |
| NMOS, 0.3 V underdrive | 4 K, tree source | 122.33 pass | 48.93 pass | 24.47 pass | 19.55 pass | 34.44 |
| NMOS, 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 122.35 pass | 48.94 pass | 24.47 pass | 19.56 pass | 34.44 |
| NMOS, 0.3 V underdrive | 4 K, tree, one reticle | 122.37 pass | 48.95 pass | 24.47 pass | 19.56 pass | 34.45 |
| NMOS, 0.3 V underdrive | 77 K Beall fit | 77.74 pass | 31.10 pass | 15.55 pass | 11.35 pass | 18.71 |
| NMOS, 0.3 V underdrive | 77 K proxy | 148.11 pass | 59.24 pass | 29.62 pass | 23.38 pass | 41.18 |
| T-switch + OTA buffer, W 0.42 | 4 K proxy | 68.82 pass | 27.53 pass | 13.76 pass | 6.88 pass | 7.82 |
| T-switch + OTA buffer, W 0.42 | 4 K, tree, ESD-dominated droop | 103.08 pass | 41.23 pass | 20.62 pass | 10.31 pass | 12.26 |
| T-switch + OTA buffer | 300 K | 70.35 pass | 28.14 pass | 14.07 pass | 7.03 pass | 10.25 |
| T-switch + OTA buffer | 4 K high | 39.27 pass | 15.71 pass | 7.85 pass | 3.93 pass | 5.54 |
| T-switch + OTA buffer | 4 K proxy (fine) | 22.77 pass | 11.52 pass | 5.04 pass | 3.65 pass | 5.42 |
| T-switch + OTA buffer | 4 K, Beall pMOS | 49.02 pass | 19.61 pass | 9.80 pass | 4.90 pass | 6.24 |
| T-switch + OTA buffer | 4 K, steep (T_eff 120 K) | 18.44 pass | 7.38 pass | 3.69 pass | 1.84 pass | 2.91 |
| T-switch + OTA buffer | 4 K, tree, ESD-dominated droop | 48.28 pass | 19.31 pass | 9.66 pass | 4.83 pass | 5.98 |
| T-switch + OTA buffer | 4 K, tree, one reticle | 65.99 pass | 26.40 pass | 13.20 pass | 6.60 pass | 7.53 |
| T-switch + OTA buffer | 77 K Beall fit | 47.58 pass | 19.03 pass | 9.52 pass | 4.76 pass | 6.16 |
| T-switch + OTA buffer | 77 K proxy | 33.45 pass | 13.38 pass | 6.69 pass | 3.35 pass | 5.04 |
| TG + dummies, W 0.84 | 4 K proxy | 32.58 pass | 13.03 pass | 6.52 pass | 3.26 pass | 3.90 |
| TG + dummies, W 0.84 | 4 K, tree, ESD-dominated droop | 35.00 pass | 14.00 pass | 7.00 pass | 3.50 pass | 4.11 |
| TG + dummies | 300 K | 50.62 pass | 20.25 pass | 10.12 pass | 5.06 pass | 7.37 |
| TG + dummies | 4 K high | 43.48 pass | 17.39 pass | 8.70 pass | 4.35 pass | 4.97 |
| TG + dummies | 4 K proxy (fine) | 42.33 pass | 21.20 pass | 8.56 pass | 4.43 pass | 5.25 |
| TG + dummies | 4 K, Beall pMOS | 88.27 pass | 35.31 pass | 17.65 pass | 8.83 pass | 8.34 |
| TG + dummies | 4 K, clock edge 600 ps | 49.23 pass | 19.69 pass | 9.85 pass | 4.92 pass | 5.57 |
| TG + dummies | 4 K, clock edge 67 ps | 41.26 pass | 16.50 pass | 8.25 pass | 4.13 pass | 4.97 |
| TG + dummies | 4 K, steep (T_eff 120 K) | 35.51 pass | 14.20 pass | 7.10 pass | 3.60 pass | 3.03 |
| TG + dummies | 4 K, steep (T_eff 20 K) | 31.46 pass | 12.58 pass | 6.29 pass | 3.37 pass | 2.68 |
| TG + dummies | 4 K, steep (T_eff 30 K) | 31.91 pass | 12.76 pass | 6.38 pass | 3.41 pass | 2.71 |
| TG + dummies | 4 K, tree source | 48.52 pass | 19.41 pass | 9.70 pass | 4.85 pass | 5.62 |
| TG + dummies | 4 K, tree, ESD-dominated droop | 48.49 pass | 19.39 pass | 9.70 pass | 4.85 pass | 5.61 |
| TG + dummies | 4 K, tree, one reticle | 48.63 pass | 19.45 pass | 9.73 pass | 4.86 pass | 5.63 |
| TG + dummies | 77 K Beall fit | 89.90 pass | 35.96 pass | 17.98 pass | 8.99 pass | 5.94 |
| TG + dummies | 77 K proxy | 44.34 pass | 17.74 pass | 8.87 pass | 4.43 pass | 5.38 |
| TG, ESD on the node | 300 K | 11.69 pass | 4.68 pass | 2.34 pass | 1.17 pass | 1.20 |
| TG, ESD on the node | 4 K high | 11.02 pass | 4.41 pass | 2.20 pass | 1.10 pass | 1.32 |
| TG, ESD on the node | 4 K proxy (fine) | 17.96 pass | 8.99 pass | 3.61 pass | 1.24 pass | 1.27 |
| TG, ESD on the node | 4 K, Beall pMOS | 251.72 pass | 100.69 pass | 50.34 pass | 25.17 pass | 37.76 |
| TG, ESD on the node | 4 K, steep (T_eff 120 K) | 14.25 pass | 5.70 pass | 2.85 pass | 1.43 pass | 1.38 |
| TG, ESD on the node | 4 K, tree, ESD-dominated droop | 12.74 pass | 5.10 pass | 2.55 pass | 1.27 pass | 1.27 |
| TG, ESD on the node | 4 K, tree, one reticle | 12.74 pass | 5.09 pass | 2.55 pass | 1.27 pass | 1.27 |
| TG, ESD on the node | 77 K Beall fit | 63.86 pass | 25.55 pass | 12.77 pass | 6.39 pass | 11.73 |
| TG, ESD on the node | 77 K proxy | 14.28 pass | 5.71 pass | 2.86 pass | 1.43 pass | 1.35 |
| TG, no ESD, W 0.42, 0.3 V underdrive | 4 K proxy | 27.67 pass | 11.07 pass | 5.53 pass | 2.77 pass | 2.75 |
| TG, no ESD, W 0.42, 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 28.03 pass | 11.21 pass | 5.61 pass | 2.80 pass | 2.77 |
| TG, no ESD, W 0.42 | 4 K proxy | 27.77 pass | 11.11 pass | 5.55 pass | 2.78 pass | 2.76 |
| TG, no ESD, W 0.42 | 4 K, tree, ESD-dominated droop | 28.14 pass | 11.25 pass | 5.63 pass | 2.81 pass | 2.78 |
| TG, no ESD, W 3 | 4 K proxy | 3.67 pass | 1.47 pass | 0.73 fail | 0.37 fail | 0.38 |
| TG, no ESD, W 3 | 4 K, tree, ESD-dominated droop | 3.95 pass | 1.58 pass | 0.79 fail | 0.39 fail | 0.39 |
| TG, no ESD | 300 K | 10.43 pass | 4.17 pass | 2.09 pass | 1.04 pass | 1.07 |
| TG, no ESD | 4 K high | 9.66 pass | 3.86 pass | 1.93 pass | 0.97 fail | 1.04 |
| TG, no ESD | 4 K proxy (fine) | 16.45 pass | 8.23 pass | 3.29 pass | 1.09 pass | 1.12 |
| TG, no ESD | 4 K, Beall pMOS | 22.04 pass | 8.81 pass | 4.41 pass | 2.20 pass | 2.24 |
| TG, no ESD | 4 K, steep (T_eff 120 K) | 12.72 pass | 5.09 pass | 2.54 pass | 1.27 pass | 1.24 |
| TG, no ESD | 4 K, tree, ESD-dominated droop | 11.19 pass | 4.47 pass | 2.24 pass | 1.12 pass | 1.12 |
| TG, no ESD | 4 K, tree, one reticle | 11.18 pass | 4.47 pass | 2.24 pass | 1.12 pass | 1.12 |
| TG, no ESD | 77 K Beall fit | 24.61 pass | 9.84 pass | 4.92 pass | 2.46 pass | 2.22 |
| TG, no ESD | 77 K proxy | 12.56 pass | 5.02 pass | 2.51 pass | 1.26 pass | 1.19 |
| bootstrapped (transistor level), 0.3 V underdrive | 300 K | 114.11 pass | 45.64 pass | 22.82 pass | 11.41 pass | 11.61 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K high | 27.45 pass | 10.98 pass | 5.49 pass | 2.74 pass | 2.84 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy (fine) | 28.17 pass | 14.36 pass | 6.05 pass | 2.71 pass | 2.84 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, Beall pMOS | 54.34 pass | 21.73 pass | 10.87 pass | 5.43 pass | 6.02 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, buffered leaf line | 23.06 pass | 9.23 pass | 4.61 pass | 2.31 pass | 2.42 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 600 ps | 23.69 pass | 9.48 pass | 4.74 pass | 2.37 pass | 2.58 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 67 ps | 34.08 pass | 13.63 pass | 6.82 pass | 3.41 pass | 3.42 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 18.57 pass | 7.43 pass | 3.71 pass | 1.86 pass | 2.21 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 11.30 pass | 4.52 pass | 2.26 pass | 1.13 pass | 1.31 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 30 K) | 11.75 pass | 4.70 pass | 2.35 pass | 1.18 pass | 1.35 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree source | 22.31 pass | 8.93 pass | 4.46 pass | 2.23 pass | 2.33 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, ESD diodes on 1 pF | 22.70 pass | 9.08 pass | 4.54 pass | 2.27 pass | 2.37 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 22.18 pass | 8.87 pass | 4.44 pass | 2.22 pass | 2.32 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, one reticle | 21.39 pass | 8.55 pass | 4.28 pass | 2.14 pass | 2.22 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K Beall fit | 55.35 pass | 22.14 pass | 11.07 pass | 5.53 pass | 6.32 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K proxy | 37.79 pass | 15.12 pass | 7.56 pass | 3.78 pass | 3.97 |
| bootstrapped (transistor level), W 1 | 4 K proxy | 15.50 pass | 6.20 pass | 3.10 pass | 1.55 pass | 1.60 |
| bootstrapped (transistor level), W 1 | 4 K, tree, ESD-dominated droop | 10.91 pass | 4.36 pass | 2.18 pass | 1.09 pass | 1.11 |

### Summary statistics

- NMOS, 0.3 V underdrive: all 18.71-325.80 classes ['pass']; cryo 50 ohm 18.71-325.80; trees 34.44-34.45; exceed max 0; lowest lower bound 17.917; 99.9 % 33.69 58.57-1020.87; 10 dec/V 138.38-2370.44
- bootstrapped (transistor level), 0.3 V underdrive: all 1.31-11.61 classes ['pass']; cryo 50 ohm 1.31-6.32; trees 2.22-2.42; exceed max 0; lowest lower bound 1.243; 99.9 % 33.69 4.08-36.32; 10 dec/V 9.78-87.87
- T-switch + OTA buffer: all 2.91-10.25 classes ['pass']; cryo 50 ohm 2.91-6.24; trees 5.98-7.53; exceed max 0; lowest lower bound 2.529; 99.9 % 33.69 9.07-32.00; 10 dec/V 23.54-82.71
- TG + dummies: all 2.68-8.34 classes ['pass']; cryo 50 ohm 2.68-8.34; trees 5.61-5.63; exceed max 0; lowest lower bound 2.260; 99.9 % 33.69 8.35-26.04; 10 dec/V 21.77-67.58
- TG, no ESD: all 1.04-2.24 classes ['pass']; cryo 50 ohm 1.04-2.24; trees 1.12-1.12; exceed max 0; lowest lower bound 1.013; 99.9 % 33.69 3.27-7.01; 10 dec/V 7.58-16.31
- TG, ESD on the node: all 1.20-37.76 classes ['pass']; cryo 50 ohm 1.27-37.76; trees 1.27-1.27; exceed max 0; lowest lower bound 1.189; 99.9 % 33.69 3.77-118.21; 10 dec/V 8.72-280.36
- s33.69_t0.001: min per-channel 1.20 (TG, no ESD, W 3|4 K proxy); not passing: []
- s10_t0.001: min per-channel 2.75 (TG, no ESD, W 3|4 K proxy); not passing: []
- NMOS, 0.3 V underdrive x1.5 / x2 mismatch: strictest 29.83 [27.99, 32.39] pass / 67.73 [62.35, 77.56] pass; 99.9 % 211.87 [194.99, 242.82] pass
- bootstrapped (transistor level), 0.3 V underdrive x1.5 / x2 mismatch: strictest 2.65 [2.40, 2.99] pass / 2.40 [2.16, 2.74] pass; 99.9 % 7.50 [6.76, 8.59] pass
- TG + dummies x1.5 / x2 mismatch: strictest 3.73 [3.10, 4.83] pass / 2.90 [2.36, 3.77] pass; 99.9 % 9.05 [7.35, 11.77] pass
- move20mV NMOS, 0.3 V underdrive: cryo + trees 77.74-1061.41
- move50mV NMOS, 0.3 V underdrive: cryo + trees 31.10-424.57
- move20mV bootstrapped (transistor level), 0.3 V underdrive: cryo + trees 11.30-55.35
- move50mV bootstrapped (transistor level), 0.3 V underdrive: cryo + trees 4.52-22.14
- move20mV T-switch + OTA buffer: cryo + trees 18.44-65.99
- move50mV T-switch + OTA buffer: cryo + trees 7.38-26.40
- move20mV TG + dummies: cryo + trees 31.46-89.90
- move50mV TG + dummies: cryo + trees 12.58-35.96
- move20mV TG, no ESD: cryo + trees 9.66-24.61
- move50mV TG, no ESD: cryo + trees 3.86-9.84
- move20mV TG, ESD on the node: cryo + trees 11.02-251.72
- move50mV TG, ESD on the node: cryo + trees 4.41-100.69
- shared calibration, strictest, passing (> 1): D BOOT|300 K 3.12, D CLK|300 K 1.89, D NSW|300 K 4.19, D NTB|300 K 1.21, D TG|300 K 1.00, NMOS, 0.3 V underdrive, W 1|4 K proxy 3.63, NMOS, 0.3 V underdrive, W 1|4 K, tree, ESD-dominated droop 3.66, NMOS, 0.3 V underdrive, W 3|4 K proxy 1.55, NMOS, 0.3 V underdrive, W 3|4 K, tree, ESD-dominated droop 2.21, NMOS, 0.3 V underdrive|300 K 6.29, NMOS, 0.3 V underdrive|4 K high 6.60, NMOS, 0.3 V underdrive|4 K proxy 6.71, NMOS, 0.3 V underdrive|4 K, Beall pMOS 6.64, NMOS, 0.3 V underdrive|4 K, clock edge 600 ps 7.02, NMOS, 0.3 V underdrive|4 K, clock edge 67 ps 6.52, NMOS, 0.3 V underdrive|4 K, steep (T_eff 120 K) 6.47, NMOS, 0.3 V underdrive|4 K, steep (T_eff 20 K) 6.32, NMOS, 0.3 V underdrive|4 K, steep (T_eff 30 K) 6.28, NMOS, 0.3 V underdrive|4 K, tree source 6.89, NMOS, 0.3 V underdrive|4 K, tree, ESD-dominated droop 6.91, NMOS, 0.3 V underdrive|4 K, tree, one reticle 6.90, NMOS, 0.3 V underdrive|77 K Beall fit 6.11, NMOS, 0.3 V underdrive|77 K proxy 6.64, TG + dummies|4 K, Beall pMOS 1.93, TG + dummies|77 K Beall fit 1.98, TG, ESD on the node|300 K 1.00, TG, ESD on the node|4 K, Beall pMOS 4.46, TG, ESD on the node|77 K Beall fit 4.06, TG, no ESD, W 0.42, 0.3 V underdrive|4 K proxy 1.28, TG, no ESD, W 0.42, 0.3 V underdrive|4 K, tree, ESD-dominated droop 1.29, TG, no ESD, W 0.42|4 K proxy 1.28, TG, no ESD, W 0.42|4 K, tree, ESD-dominated droop 1.30, TG, no ESD|4 K, Beall pMOS 1.76, TG, no ESD|77 K Beall fit 1.75, bootstrapped (transistor level), 0.3 V underdrive|300 K 1.83, bootstrapped (transistor level), 0.3 V underdrive|4 K, Beall pMOS 1.16
- adjacent-voltage pedestal correlation of the channels: 0.76 to 1.00
