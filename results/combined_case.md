# Combined worst case and related quantities

## A. Combined worst case (strictest point; 99.9% at 33.69 dec/V in brackets)

| design | condition | window (V) | line | quadratic | line over 0.4 V | shared line |
|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 4 K proxy | 0.3 to 0.8 | 29.6 (92.8) | 135 (423) | 42 (132) | 6.17 (19.3) |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 0.3 to 0.7 | 297 (930) | 4.92e+03 (1e+04) | 297 (930) | 5.71 (17.8) |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 2 | 0.3 to 0.7 | 61.8 (193) | 301 (941) | 61.8 (193) | 3.24 (10.1) |
| NMOS, 0.3 V underdrive | 4 K, tree, one reticle | 0.3 to 0.8 | 31.4 (98.3) | 132 (412) | 44 (138) | 6.29 (19.6) |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 20 K), mismatch x 2, tree of one reticle | 0.3 to 0.7 | 480 (1.5e+03) | 9.72e+03 (1e+04) | 480 (1.5e+03) | 2.93 (9.15) |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy | 0.3 to 1.5 | 2.64 (8.25) | 44.9 (140) | 16.9 (52.8) | 0.747 (2.33) |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 0.3 to 1.5 | 1.19 (3.72) | 4.09 (12.8) | 4.79 (14.9) | 0.835 (2.61) |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, mismatch x 2 | 0.3 to 1.5 | 2.19 (6.84) | 34.4 (107) | 14.4 (45.2) | 0.358 (1.12) |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, one reticle | 0.3 to 1.5 | 2.02 (6.33) | 30.9 (96.8) | 13 (40.8) | 0.339 (1.06) |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 20 K), mismatch x 2, tree of one reticle | 0.3 to 1.5 | 0.577 (1.8) | 1.17 (3.65) | 1.47 (4.59) | 0.333 (1.04) |
| T-switch + OTA buffer | 4 K proxy | 0.3 to 1.5 | 4.91 (15.4) | 6.85 (21.4) | 8.15 (25.5) | 0.363 (1.13) |
| T-switch + OTA buffer | 4 K, tree, one reticle | 0.3 to 1.5 | 6.86 (21.4) | 10.4 (32.5) | 10.7 (33.3) | 0.369 (1.15) |
| T-switch + OTA buffer | 4 K, steep (T_eff 20 K), mismatch x 2, tree of one reticle | 0.3 to 1.5 | 2.1 (6.55) | 2.54 (7.93) | 2.83 (8.84) | 0.167 (0.52) |
| TG + dummies | 4 K proxy | 0.3 to 1.5 | 4.65 (14.5) | 6.1 (19) | 11.5 (35.8) | 0.686 (2.14) |
| TG + dummies | 4 K, steep (T_eff 20 K) | 0.3 to 1.5 | 2.44 (7.61) | 2.79 (8.71) | 456 (1.42e+03) | 0.61 (1.9) |
| TG + dummies | 4 K, mismatch x 2 | 0.3 to 1.5 | 2.6 (8.12) | 3.65 (11.4) | 6.82 (21.3) | 0.349 (1.09) |
| TG + dummies | 4 K, tree, one reticle | 0.3 to 1.5 | 5.09 (15.9) | 6.76 (21.1) | 12.6 (39.2) | 0.689 (2.15) |
| TG + dummies | 4 K, steep (T_eff 20 K), mismatch x 2, tree of one reticle | 0.3 to 1.5 | 1.39 (4.32) | 1.62 (5.05) | 99.9 (313) | 0.313 (0.976) |
| TG, no ESD | 4 K proxy | 0.3 to 1.5 | 1.02 (3.19) | 4.58 (14.3) | 4.68 (14.7) | 0.613 (1.92) |
| TG, no ESD | 4 K, mismatch x 2 | 0.3 to 1.5 | 0.961 (3.01) | 3.97 (12.4) | 4.35 (13.6) | 0.518 (1.62) |
| TG, no ESD | 4 K, tree, one reticle | 0.3 to 1.5 | 1.02 (3.2) | 5.63 (17.6) | 5 (15.7) | 0.728 (2.28) |
| TG, no ESD | 4 K, steep (T_eff 20 K), mismatch x 2, tree of one reticle | 0.3 to 1.5 | 0.893 (2.8) | 2.33 (7.28) | 46.9 (147) | 0.55 (1.72) |
| TG, ESD on the node | 4 K proxy | 0.3 to 1.5 | 1.16 (3.62) | 5.35 (16.7) | 5.36 (16.8) | 0.699 (2.19) |
| TG, ESD on the node | 4 K, tree, one reticle | 0.3 to 1.5 | 1.16 (3.64) | 6.59 (20.6) | 5.71 (17.9) | 0.829 (2.59) |
| TG, ESD on the node | 4 K, steep (T_eff 20 K), mismatch x 2, tree of one reticle | 0.3 to 1.5 | 0.991 (3.1) | 2.62 (8.18) | 48.8 (153) | 0.611 (1.91) |

## B. Factor by which the deviation of the mean channel may grow before the margin is one (smallest over conditions)

| design | line (at) | quadratic (at) | line over 0.4 V (at) | mean deviation from a line over conditions (uV) |
|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 19.6 (77 K Beall fit) | 93.9 (77 K Beall fit) | 35.9 (77 K Beall fit) | 0.951 to 5.14 (x5.4) |
| bootstrapped (transistor level), 0.3 V underdrive | 2.25 (4 K, steep (T_eff 120 K)) | 13.8 (4 K, steep (T_eff 120 K)) | 10.1 (4 K, steep (T_eff 120 K)) | 7.19 to 41.1 (x5.7) |
| T-switch + OTA buffer | 7.54 (77 K proxy) | 10.3 (4 K, steep (T_eff 120 K)) | 12.1 (4 K, steep (T_eff 120 K)) | 3.96 to 12.4 (x3.1) |
| TG + dummies | 12.4 (4 K, steep (T_eff 120 K)) | 13.6 (4 K, steep (T_eff 120 K)) | 50 (77 K proxy) | 2.93 to 6.23 (x2.1) |
| TG, no ESD | 0.982 (4 K high) | 3.75 (4 K high) | 4.22 (4 K high) | 45 to 101 (x2.2) |
| TG, ESD on the node | 1.1 (300 K) | 3.9 (4 K high) | 4.96 (300 K) | 2.49 to 88.7 (x36) |
| GF180 NMOS, 0.3 V underdrive | 562 (300 K) | 1e+03 (300 K) | 1e+03 (300 K) | 0.143 to 0.18 (x1.3) |
| GF180 bootstrapped (transistor level), 0.3 V underdrive | 14.1 (4 K proxy) | 83.8 (4 K proxy) | 60.9 (4 K proxy) | 2.75 to 7.18 (x2.6) |
| GF180 TG + dummies | 18.9 (4 K proxy) | 17.8 (300 K) | 24.6 (4 K proxy) | 4.31 to 4.93 (x1.1) |
| GF180 TG, no ESD | 0.585 (300 K) | 1.98 (4 K proxy) | 2.27 (300 K) | 149 to 173 (x1.2) |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V | 121 (4 K high) | 1e+03 (300 K) | 650 (4 K high) | 0.768 to 0.834 (x1.1) |
| GF180 TG, no ESD, W 0.42 | 1.41 (300 K) | 4.67 (4 K proxy) | 5.31 (4 K proxy) | 64 to 71.7 (x1.1) |

## C. Width and overlap spread between channels, 4 K band, strictest point: line per channel / shared line (shared at 99.9%, 10 dec/V)

| design | no spread | 2% | 5% |
|---|---|---|---|
| NMOS, 0.3 V underdrive | 29.6 / 6.17 (50.1) | 29.2 / 2.31 (18.9) | 27.6 / 0.997 (8.15) |
| bootstrapped (transistor level), 0.3 V underdrive | 2.64 / 0.747 (6.06) | 2.62 / 0.627 (5.1) | 2.57 / 0.398 (3.25) |
| TG + dummies | 4.65 / 0.686 (5.59) | 4.65 / 0.686 (5.59) | 4.64 / 0.685 (5.59) |
| TG, no ESD | 1.02 / 0.613 (4.78) | 1.01 / 0.601 (4.69) | 0.974 / 0.55 (4.32) |

## D. Shared-error budgets with summed cross-coupling S (uV): equal signs / independent signs

| point | S = -0.5 | 0 | 0.5 | 1 |
|---|---|---|---|---|
| 99.9%, 33.69 | 698 / 1048 | 349 / 524 | 233 / 349 | 174 / 262 |
| 99.99%, 33.69 | 223 / 336 | 111 / 168 | 74 / 112 | 56 / 84 |
| 99.9%, 10 | 1598 / 2746 | 799 / 1373 | 533 / 915 | 399 / 687 |

## E. Dense array: pulse-driver bound with the fan-in capacitance on the node (10^6 barriers)

| s | case | energy (fJ) | 1 us rounds (mW, stage) | 10 us rounds (mW, stage) |
|---|---|---|---|---|
| 3.87 | C_o 3 pF, k 0.5 | 2.71e+03 | 2.71e+03 (above 4.2 K) | 271 (4.2 K) |
| 3.87 | C_o 3 pF, k 0.9 | 1.51e+03 | 1.51e+03 (above 4.2 K) | 151 (4.2 K) |
| 3.87 | C_o 3 pF, k 1 | 1.36e+03 | 1.36e+03 (4.2 K) | 136 (4.2 K) |
| 3.87 | C_o 4.5 pF, k 0.5 | 4.07e+03 | 4.07e+03 (above 4.2 K) | 407 (4.2 K) |
| 3.87 | C_o 4.5 pF, k 0.9 | 2.26e+03 | 2.26e+03 (above 4.2 K) | 226 (4.2 K) |
| 3.87 | C_o 4.5 pF, k 1 | 2.03e+03 | 2.03e+03 (above 4.2 K) | 203 (4.2 K) |
| 10 | C_o 3 pF, k 0.5 | 406 | 406 (4.2 K) | 40.6 (4.2 K) |
| 10 | C_o 3 pF, k 0.9 | 226 | 226 (4.2 K) | 22.6 (1.2 K) |
| 10 | C_o 3 pF, k 1 | 203 | 203 (4.2 K) | 20.3 (1.2 K) |
| 10 | C_o 4.5 pF, k 0.5 | 609 | 609 (4.2 K) | 60.9 (4.2 K) |
| 10 | C_o 4.5 pF, k 0.9 | 339 | 339 (4.2 K) | 33.9 (1.2 K) |
| 10 | C_o 4.5 pF, k 1 | 305 | 305 (4.2 K) | 30.5 (1.2 K) |
| 16.6 | C_o 3 pF, k 0.5 | 147 | 147 (4.2 K) | 14.7 (1.2 K) |
| 16.6 | C_o 3 pF, k 0.9 | 81.9 | 81.9 (4.2 K) | 8.19 (1.2 K) |
| 16.6 | C_o 3 pF, k 1 | 73.7 | 73.7 (4.2 K) | 7.37 (1.2 K) |
| 16.6 | C_o 4.5 pF, k 0.5 | 221 | 221 (4.2 K) | 22.1 (1.2 K) |
| 16.6 | C_o 4.5 pF, k 0.9 | 123 | 123 (4.2 K) | 12.3 (1.2 K) |
| 16.6 | C_o 4.5 pF, k 1 | 111 | 111 (4.2 K) | 11.1 (1.2 K) |
| 33.69 | C_o 3 pF, k 0.5 | 35.8 | 35.8 (1.2 K) | 3.58 (1.2 K) |
| 33.69 | C_o 3 pF, k 0.9 | 19.9 | 19.9 (1.2 K) | 1.99 (1.2 K) |
| 33.69 | C_o 3 pF, k 1 | 17.9 | 17.9 (1.2 K) | 1.79 (1.2 K) |
| 33.69 | C_o 4.5 pF, k 0.5 | 53.7 | 53.7 (4.2 K) | 5.37 (1.2 K) |
| 33.69 | C_o 4.5 pF, k 0.9 | 29.8 | 29.8 (1.2 K) | 2.98 (1.2 K) |
| 33.69 | C_o 4.5 pF, k 1 | 26.8 | 26.8 (1.2 K) | 2.68 (1.2 K) |

## E. Limits rescaled to a 70 fF node

- select-line coupling (aF): 99.99% 33.69 / 99.9% 33.69 / 99.9% 10: 4.2, 13.3, 45.5
- pulse-line coupling to a neighbour running a CZ (fF), 99.99%: 3.87 / 10 / 33.69: 0.0399, 0.0672, 0.084
- allowance for electrode, connection and switch (fF): k 0.5 / k 0.9: 35, 7
- kT/C noise (uV): 4.2 K / 1.2 K / 0.14 K: 28.8, 15.4, 5.25
- droop at 5.5 aA (uV/s): 78.6
- equivalent width on 1 pF (um): 1 um switch / 0.42 um switch: 14.3, 6
- largest move, 1 um TG (mV, nominal), 99.99% 33.69: 300 K / 4 K: 12.6, 14.7
- largest move, 1 um TG with dummies (mV): 300 K / 4 K: 287, 109
- largest move, 0.42 um NMOS (mV): 300 K / 4 K: 600, 105
- largest move, 0.42 um bootstrapped (mV): 300 K / 4 K: 1.2e+03, 1.2e+03
