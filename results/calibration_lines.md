## Calibration lines, verdict rule and fixed NMOS window

Margins at the strictest point (99.99 %, 33.69 dec/V, untracked), levels set open-loop, per-channel calibration,
closed form corrected for tau; [90 % bootstrap interval]; verdict with the 0.9-1.1 rule.

Best pairs (4 K band): NMOS, 0.3 V underdrive: 0.4/0.8 V, bootstrapped (transistor level), 0.3 V underdrive: 0.5/1.3 V, T-switch + OTA buffer: 0.3/1.3 V, TG + dummies: 0.5/1.5 V, TG, no ESD: 0.5/1.3 V, TG, ESD on the node: 0.5/1.3 V

| Design | Condition | Least squares, 7 points | Two points, ends | Two points, best pair | yield8 (IS) |
|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 300 K | 28.8 [27.6, 30.2] pass | 18.8 [18.1, 19.8] pass | 22.4 [21.7, 23.5] pass | 28.8 |
| NMOS, 0.3 V underdrive | 77 K proxy | 37.5 [36.1, 39.7] pass | 22.6 [21.7, 23.9] pass | 30.1 [28.9, 31.9] pass | 37.5 |
| NMOS, 0.3 V underdrive | 4 K proxy | 29.6 [28.5, 31.3] pass | 17.9 [17.1, 19] pass | 23.6 [22.6, 25.2] pass | 29.7 |
| NMOS, 0.3 V underdrive | 4 K high | 23 [22, 24.2] pass | 13.8 [13.3, 14.5] pass | 18.2 [17.4, 19.3] pass | 23 |
| NMOS, 0.3 V underdrive | 77 K Beall fit | 17 [16.4, 17.9] pass | 11.1 [10.7, 11.7] pass | 13.3 [12.8, 13.9] pass | 17 |
| NMOS, 0.3 V underdrive | 4 K, Beall pMOS | 29 [27.9, 30.7] pass | 17.5 [16.8, 18.6] pass | 23.1 [22.2, 24.5] pass | 29 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 92.2 [88.1, 97.8] pass | 55.1 [53.1, 58.1] pass | 76.2 [73, 80.5] pass | 92.2 |
| NMOS, 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 31.4 [30.1, 33.6] pass | 19.1 [18.2, 20.3] pass | 25 [23.9, 26.7] pass | 31.4 |
| NMOS, 0.3 V underdrive | 4 K, tree, one reticle | 31.4 [30, 33.6] pass | 19.1 [18.1, 20.4] pass | 25 [23.9, 26.7] pass | 31.4 |
| bootstrapped (transistor level), 0.3 V underdrive | 300 K | 10.6 [9.72, 11.9] pass | 5.98 [5.49, 6.76] pass | 10.3 [9.43, 11.7] pass | 10.6 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K proxy | 3.62 [3.38, 4.02] pass | 2.13 [1.97, 2.37] pass | 3.37 [3.1, 3.75] pass | 3.62 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy | 2.64 [2.57, 2.71] pass | 1.54 [1.5, 1.59] pass | 2.46 [2.41, 2.54] pass | 2.65 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K high | 2.59 [2.48, 2.79] pass | 1.5 [1.43, 1.63] pass | 2.46 [2.35, 2.6] pass | 2.59 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K Beall fit | 5.75 [5.08, 6.69] pass | 3.65 [3.24, 4.22] pass | 4.77 [4.3, 5.57] pass | 5.75 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, Beall pMOS | 5.48 [5, 6.09] pass | 3.41 [3.12, 3.83] pass | 4.72 [4.34, 5.24] pass | 5.48 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 2.01 [1.88, 2.18] pass | 1.3 [1.23, 1.4] pass | 1.6 [1.49, 1.74] pass | 2.01 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 2.11 [1.98, 2.32] pass | 1.24 [1.16, 1.35] unresolved | 1.97 [1.86, 2.13] pass | 2.11 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, one reticle | 2.02 [1.86, 2.26] pass | 1.18 [1.09, 1.32] unresolved | 1.91 [1.78, 2.09] pass | 2.02 |
| T-switch + OTA buffer | 300 K | 9.34 [8.05, 11.6] pass | 6.5 [5.59, 8.04] pass | 7.19 [6.35, 8.53] pass | 9.34 |
| T-switch + OTA buffer | 77 K proxy | 4.6 [4.27, 5.14] pass | 2.91 [2.65, 3.25] pass | 3.31 [2.91, 3.63] pass | 4.59 |
| T-switch + OTA buffer | 4 K proxy | 4.91 [4.54, 5.57] pass | 3.09 [2.78, 3.51] pass | 3.55 [3.17, 3.9] pass | 4.93 |
| T-switch + OTA buffer | 4 K high | 5.04 [4.55, 5.86] pass | 3.14 [2.82, 3.71] pass | 3.64 [3.29, 4.06] pass | 5.04 |
| T-switch + OTA buffer | 77 K Beall fit | 5.61 [5.02, 6.75] pass | 3.53 [3.2, 4.34] pass | 4.04 [3.6, 4.66] pass | 5.61 |
| T-switch + OTA buffer | 4 K, Beall pMOS | 5.68 [5.04, 7.05] pass | 3.59 [3.22, 4.43] pass | 4.15 [3.7, 5.06] pass | 5.69 |
| T-switch + OTA buffer | 4 K, steep (T_eff 120 K) | 2.64 [2.33, 3.43] pass | 1.79 [1.58, 2.33] pass | 1.88 [1.67, 2.47] pass | 2.65 |
| T-switch + OTA buffer | 4 K, tree, ESD-dominated droop | 5.46 [4.9, 6.21] pass | 3.63 [3.26, 4.22] pass | 3.99 [3.52, 4.53] pass | 5.45 |
| T-switch + OTA buffer | 4 K, tree, one reticle | 6.86 [6.03, 8.91] pass | 4.61 [4.02, 5.46] pass | 4.87 [4.24, 6.25] pass | 6.86 |
| TG + dummies | 300 K | 6.72 [5.73, 8.19] pass | 4.93 [4.11, 5.78] pass | 3.95 [3.43, 4.97] pass | 6.72 |
| TG + dummies | 77 K proxy | 4.92 [4.02, 6.3] pass | 3.25 [2.73, 4.38] pass | 3.93 [3.34, 5.05] pass | 4.9 |
| TG + dummies | 4 K proxy | 4.65 [3.94, 6.14] pass | 2.89 [2.39, 3.92] pass | 3.81 [3.24, 4.92] pass | 4.78 |
| TG + dummies | 4 K high | 4.5 [3.78, 6.05] pass | 2.7 [2.28, 3.68] pass | 3.78 [3.18, 5.35] pass | 4.53 |
| TG + dummies | 77 K Beall fit | 5.41 [4.55, 7.43] pass | 3.22 [2.76, 4.44] pass | 4.08 [3.44, 6] pass | 5.41 |
| TG + dummies | 4 K, Beall pMOS | 7.61 [6.51, 10.3] pass | 4.62 [4, 5.84] pass | 7.25 [6.44, 8.9] pass | 7.6 |
| TG + dummies | 4 K, steep (T_eff 120 K) | 2.75 [2.35, 3.61] pass | 2.07 [1.73, 2.75] pass | 2.74 [2.33, 3.43] pass | 2.76 |
| TG + dummies | 4 K, tree, ESD-dominated droop | 5.09 [4.16, 6.64] pass | 3.14 [2.59, 4.31] pass | 4.24 [3.61, 5.32] pass | 5.11 |
| TG + dummies | 4 K, tree, one reticle | 5.09 [4.3, 6.61] pass | 3.14 [2.63, 4.36] pass | 4.24 [3.58, 5.37] pass | 5.13 |
| TG, no ESD | 300 K | 1.05 [1.04, 1.07] unresolved | 0.623 [0.614, 0.634] fail | 0.97 [0.947, 1] unresolved | 1.05 |
| TG, no ESD | 77 K proxy | 1.09 [1.06, 1.11] unresolved | 0.574 [0.56, 0.589] fail | 1.05 [1.03, 1.09] unresolved | 1.09 |
| TG, no ESD | 4 K proxy | 1.02 [1.01, 1.03] unresolved | 0.579 [0.573, 0.585] fail | 0.933 [0.926, 0.942] unresolved | 1.02 |
| TG, no ESD | 4 K high | 0.983 [0.956, 1.02] unresolved | 0.596 [0.579, 0.615] fail | 0.849 [0.84, 0.861] fail | 0.983 |
| TG, no ESD | 77 K Beall fit | 2.02 [1.98, 2.08] pass | 1.11 [1.09, 1.13] unresolved | – | 2.02 |
| TG, no ESD | 4 K, Beall pMOS | 2.04 [2.02, 2.07] pass | 1.22 [1.21, 1.24] pass | – | 2.04 |
| TG, no ESD | 4 K, steep (T_eff 120 K) | 1.13 [1.09, 1.19] unresolved | 0.596 [0.583, 0.619] fail | 1.15 [1.11, 1.19] unresolved | 1.13 |
| TG, no ESD | 4 K, tree, ESD-dominated droop | 1.02 [1, 1.05] unresolved | 0.58 [0.563, 0.6] fail | 0.973 [0.96, 0.993] unresolved | 1.02 |
| TG, no ESD | 4 K, tree, one reticle | 1.02 [1, 1.05] unresolved | 0.58 [0.562, 0.6] fail | 0.973 [0.959, 0.992] unresolved | 1.02 |
| TG, ESD on the node | 300 K | 1.1 [1.08, 1.12] unresolved | 0.652 [0.643, 0.662] fail | 1.01 [0.987, 1.04] unresolved | 1.1 |
| TG, ESD on the node | 77 K proxy | 1.23 [1.21, 1.25] pass | 0.648 [0.632, 0.664] fail | 1.19 [1.16, 1.23] pass | 1.23 |
| TG, ESD on the node | 4 K proxy | 1.16 [1.15, 1.16] pass | 0.653 [0.647, 0.66] fail | 1.06 [1.06, 1.07] unresolved | 1.16 |
| TG, ESD on the node | 4 K high | 1.21 [1.18, 1.25] pass | 0.654 [0.635, 0.675] fail | 0.938 [0.927, 0.955] unresolved | 1.21 |
| TG, ESD on the node | 77 K Beall fit | 10.7 [10.3, 11.3] pass | 6 [5.74, 6.32] pass | – | 10.7 |
| TG, ESD on the node | 4 K, Beall pMOS | 34.4 [32.8, 36.8] pass | 22.9 [21.8, 24.5] pass | – | 34.4 |
| TG, ESD on the node | 4 K, steep (T_eff 120 K) | 1.26 [1.21, 1.33] pass | 0.664 [0.648, 0.691] fail | 1.29 [1.24, 1.33] pass | 1.26 |
| TG, ESD on the node | 4 K, tree, ESD-dominated droop | 1.16 [1.14, 1.19] pass | 0.655 [0.636, 0.677] fail | 1.11 [1.09, 1.13] unresolved | 1.16 |
| TG, ESD on the node | 4 K, tree, one reticle | 1.16 [1.13, 1.19] pass | 0.655 [0.636, 0.679] fail | 1.11 [1.1, 1.13] unresolved | 1.16 |

Lowest margins at 99.9 % (33.69 and 10 dec/V), per calibration:
- least squares, 7 points, s33.69_t0.001: 3.08 (TG, no ESD|4 K high)
- least squares, 7 points, s10_t0.001: 7.15 (TG, no ESD|4 K high)
- two points, window ends, s33.69_t0.001: 1.8 (TG, no ESD|77 K proxy)
- two points, window ends, s10_t0.001: 4.17 (TG, no ESD|77 K proxy)

## Verdict changes under the 0.9-1.1 rule (73)

- bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 120 K) s33.69_t0.0001|shared|mixed: near one -> unresolved (0.791)
- TG, no ESD|4 K, steep (T_eff 120 K) s33.69_t0.0001|full|mixed: pass -> unresolved (1.13)
- TG, no ESD|4 K, steep (T_eff 120 K) s33.69_t0.0001|shared|mixed: fail -> unresolved (0.803)
- TG, no ESD|4 K proxy s33.69_t0.0001|full|mixed: near one -> unresolved (1.02)
- TG, ESD on the node|4 K, steep (T_eff 120 K) s33.69_t0.0001|shared|mixed: near one -> unresolved (0.898)
- T-switch + OTA buffer|4 K, steep (T_eff 120 K) s33.69_t0.001|shared|mixed: near one -> unresolved (1.09)
- T-switch + OTA buffer|4 K proxy s33.69_t0.001|shared|mixed: near one -> unresolved (1.14)
- TG, no ESD|4 K, tree, ESD-dominated droop s33.69_t0.0001|full|mixed: near one -> unresolved (1.02)
- TG, ESD on the node|4 K, tree, ESD-dominated droop s33.69_t0.0001|shared|mixed: fail -> unresolved (0.83)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, ESD-dominated droop s33.69_t0.001|shared|mixed: near one -> unresolved (1.3)
- T-switch + OTA buffer|4 K, tree, ESD-dominated droop s33.69_t0.001|shared|mixed: near one -> unresolved (1.16)
- bootstrapped (transistor level), W 1|4 K, tree, ESD-dominated droop s33.69_t0.0001|full|mixed: near one -> unresolved (1.01)
- bootstrapped (transistor level), W 1|4 K, tree, ESD-dominated droop s33.69_t0.001|shared|mixed: near one -> unresolved (0.779)
- TG, no ESD, W 0.42|4 K proxy s33.69_t0.0001|shared|mixed: pass -> unresolved (1.17)
- TG, no ESD, W 0.42|4 K, tree, ESD-dominated droop s33.69_t0.0001|shared|mixed: pass -> unresolved (1.18)
- TG, no ESD, W 3|4 K proxy s33.69_t0.001|full|mixed: pass -> unresolved (1.09)
- TG + dummies, W 0.84|4 K proxy s33.69_t0.0001|shared|mixed: near one -> unresolved (0.583)
- TG + dummies, W 0.84|4 K, tree, ESD-dominated droop s33.69_t0.0001|shared|mixed: near one -> unresolved (0.587)
- TG, no ESD, W 0.42, 0.3 V underdrive|4 K proxy s33.69_t0.0001|shared|mixed: pass -> unresolved (1.17)
- TG, no ESD, W 0.42, 0.3 V underdrive|4 K, tree, ESD-dominated droop s33.69_t0.0001|shared|mixed: pass -> unresolved (1.18)
- T-switch + OTA buffer, W 0.42|4 K proxy s33.69_t0.001|shared|mixed: pass -> unresolved (1.35)
- T-switch + OTA buffer, W 0.42|4 K, tree, ESD-dominated droop s33.69_t0.001|shared|mixed: pass -> unresolved (1.36)
- bootstrapped (transistor level), 0.3 V underdrive|77 K proxy s33.69_t0.0001|shared|mixed: near one -> unresolved (0.873)
- bootstrapped (transistor level), 0.3 V underdrive|4 K high s33.69_t0.0001|shared|mixed: near one -> unresolved (0.779)
- bootstrapped (transistor level), 0.3 V underdrive|77 K Beall fit s33.69_t0.0001|shared|mixed: near one -> unresolved (0.816)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, Beall pMOS s33.69_t0.0001|shared|mixed: near one -> unresolved (1.05)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, one reticle s33.69_t0.001|shared|mixed: near one -> unresolved (1.06)
- T-switch + OTA buffer|300 K s33.69_t0.001|shared|mixed: near one -> unresolved (1.09)
- T-switch + OTA buffer|77 K proxy s33.69_t0.001|shared|mixed: near one -> unresolved (1.12)
- T-switch + OTA buffer|4 K high s33.69_t0.001|shared|mixed: near one -> unresolved (1.16)
- T-switch + OTA buffer|77 K Beall fit s33.69_t0.001|shared|mixed: near one -> unresolved (1.12)
- T-switch + OTA buffer|4 K, Beall pMOS s33.69_t0.001|shared|mixed: near one -> unresolved (1.15)
- T-switch + OTA buffer|4 K, tree, one reticle s33.69_t0.001|shared|mixed: near one -> unresolved (1.17)
- TG, no ESD|300 K s33.69_t0.0001|full|mixed: pass -> unresolved (1.05)
- TG, no ESD|300 K s33.69_t0.0001|shared|mixed: fail -> unresolved (0.868)
- TG, no ESD|77 K proxy s33.69_t0.0001|full|mixed: pass -> unresolved (1.09)
- TG, no ESD|4 K high s33.69_t0.0001|full|mixed: near one -> unresolved (0.983)
- TG, no ESD|4 K, tree, one reticle s33.69_t0.0001|full|mixed: near one -> unresolved (1.02)
- TG, ESD on the node|300 K s33.69_t0.0001|full|mixed: pass -> unresolved (1.1)
- TG, ESD on the node|300 K s33.69_t0.0001|shared|mixed: fail -> unresolved (0.914)
- TG, ESD on the node|77 K proxy s33.69_t0.0001|shared|mixed: near one -> unresolved (0.845)
- TG, ESD on the node|4 K high s33.69_t0.0001|shared|mixed: near one -> unresolved (0.866)
- TG, ESD on the node|4 K, tree, one reticle s33.69_t0.0001|shared|mixed: fail -> unresolved (0.83)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 30 K) s33.69_t0.0001|shared|mixed: fail -> unresolved (0.759)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 20 K) s33.69_t0.0001|full|mixed: pass -> unresolved (1.19)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 20 K) s33.69_t0.0001|shared|mixed: near one -> unresolved (0.834)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, clock edge 600 ps s33.69_t0.0001|shared|mixed: near one -> unresolved (0.72)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, clock edge 67 ps s33.69_t0.0001|shared|mixed: near one -> unresolved (0.894)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, tree source s33.69_t0.001|shared|mixed: near one -> unresolved (1.34)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 2 s33.69_t0.001|shared|mixed: near one -> unresolved (1.12)
- TG + dummies|4 K, mismatch x 2 s33.69_t0.001|shared|mixed: near one -> unresolved (1.09)
- D TG|300 K s33.69_t0.0001|full|mixed: pass -> unresolved (1.1)
- D TG|300 K s33.69_t0.0001|shared|mixed: fail -> unresolved (0.914)
- D TSW|300 K s33.69_t0.001|shared|mixed: near one -> unresolved (0.93)
- D TGH|300 K s33.69_t0.0001|full|mixed: near one -> unresolved (1.02)
- D TSWB|300 K s33.69_t0.001|shared|mixed: near one -> unresolved (0.925)
- D NTB|300 K s33.69_t0.0001|shared|mixed: near one -> unresolved (1.1)
- NMOS, 0.3 V underdrive|4 K, mismatch x 5.3 s33.69_t0.0001|shared|mixed: near one -> unresolved (1.2)

## NMOS on 0.3 to 0.7 V

| Condition | per channel | shared | as stored (window) |
|---|---|---|---|
| 4 K, steep (T_eff 120 K) | 208 [203, 214] | 5.95 | 92.199 (0.3-0.8 V) |
| 4 K proxy | 72.5 [69.8, 77.2] | 6.53 | 29.668 (0.3-0.8 V) |
| 4 K, tree, ESD-dominated droop | 80 [76.2, 85.3] | 6.63 | 31.378 (0.3-0.8 V) |
| 300 K | 143 [139, 149] | 6.12 | 28.841 (0.3-0.9 V) |
| 77 K proxy | 91.5 [88, 97.4] | 6.31 | 37.515 (0.3-0.8 V) |
| 4 K high | 55.1 [52.3, 58.4] | 6.47 | 22.987 (0.3-0.8 V) |
| 77 K Beall fit | 89.8 [85.8, 95.4] | 6.28 | 17.042 (0.3-0.9 V) |
| 4 K, Beall pMOS | 71 [67.9, 74.9] | 6.39 | 29.033 (0.3-0.8 V) |
| 4 K, tree, one reticle | 80 [76.4, 85.3] | 6.63 | 31.382 (0.3-0.8 V) |
| 4 K, steep (T_eff 30 K) | 286 [282, 292] | 5.73 | 153.992 (0.3-0.8 V) |
| 4 K, steep (T_eff 20 K) | 297 [293, 302] | 5.71 | 296.824 (0.3-0.7 V) |
| 4 K, clock edge 600 ps | 82.3 [77.3, 89.5] | 6.74 | 31.264 (0.3-0.8 V) |
| 4 K, clock edge 67 ps | 67.7 [64.9, 71.7] | 6.28 | 28.221 (0.3-0.8 V) |
| 4 K, tree source | 80 [76.2, 85.2] | 6.63 | 31.375 (0.3-0.8 V) |
| 4 K, mismatch x 1.5 | 66.2 [62.6, 72.9] | 4.31 | 27.175 (0.3-0.8 V) |
| 4 K, mismatch x 2 | 61.8 [57.2, 69.7] | 3.24 | 61.706 (0.3-0.7 V) |
| 4 K, mismatch x 2.5 | 57.6 [52.3, 66.5] | 2.58 | 57.665 (0.3-0.7 V) |
| 4 K, mismatch x 3 | 53.9 [47.9, 66.1] | 2.15 | 53.876 (0.3-0.7 V) |
