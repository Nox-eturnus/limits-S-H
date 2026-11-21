# The strictest point with the budgets of a 15 MHz device

## A. Budgets (µV): single gate / equal signs / frame-tracked M = 2; gate 50 ns x 100 MHz / Zeeman difference

| Zeeman | target | 3.87 dec/V | 10 dec/V | 16.6 dec/V | 33.69 dec/V |
|---|---|---|---|---|---|
| 100 MHz | 0.001 | 1986.3 / 1035.5 / 3517.1 | 1373.8 / 798.9 / 1361.1 | 966.3 / 602.7 / 820.0 | 524.7 / 348.9 / 404.0 |
| 100 MHz | 0.0001 | 628.8 / 327.5 / 1124.0 | 437.3 / 253.4 / 435.0 | 308.7 / 191.6 / 262.0 | 168.2 / 111.3 / 129.1 |
| 25 MHz | 0.001 | 556.5 / 279.1 / 3517.2 | 529.1 / 269.7 / 1361.1 | 487.6 / 255.5 / 820.0 | 376.8 / 213.6 / 404.0 |
| 25 MHz | 0.0001 | 175.9 / 88.2 / 1124.0 | 167.4 / 85.3 / 435.0 | 154.4 / 80.8 / 262.0 | 119.8 / 67.7 / 129.1 |
| 15 MHz | 0.001 | 336.2 / 168.3 / 3517.1 | 329.1 / 165.8 / 1361.1 | 317.3 / 161.7 / 820.0 | 277.5 / 147.9 / 404.0 |
| 15 MHz | 0.0001 | 106.3 / 53.2 / 1124.0 | 104.1 / 52.4 / 435.0 | 100.4 / 51.1 / 262.0 | 88.0 / 46.8 / 129.1 |
| 10 MHz | 0.001 | 224.6 / 112.4 / 3517.3 | 222.3 / 111.5 / 1361.1 | 218.2 / 110.1 / 820.0 | 202.9 / 104.8 / 404.0 |
| 10 MHz | 0.0001 | 71.0 / 35.5 / 1124.0 | 70.3 / 35.3 / 435.0 | 69.0 / 34.8 / 262.0 | 64.2 / 33.2 / 129.1 |

Change from 100 MHz (single gate / equal signs):

- 25 MHz, 3.87 dec/V, 0.001: x0.280 / x0.270
- 25 MHz, 3.87 dec/V, 0.0001: x0.280 / x0.269
- 25 MHz, 10 dec/V, 0.001: x0.385 / x0.338
- 25 MHz, 10 dec/V, 0.0001: x0.383 / x0.337
- 25 MHz, 16.6 dec/V, 0.001: x0.505 / x0.424
- 25 MHz, 16.6 dec/V, 0.0001: x0.500 / x0.422
- 25 MHz, 33.69 dec/V, 0.001: x0.718 / x0.612
- 25 MHz, 33.69 dec/V, 0.0001: x0.712 / x0.608
- 15 MHz, 3.87 dec/V, 0.001: x0.169 / x0.163
- 15 MHz, 3.87 dec/V, 0.0001: x0.169 / x0.162
- 15 MHz, 10 dec/V, 0.001: x0.240 / x0.207
- 15 MHz, 10 dec/V, 0.0001: x0.238 / x0.207
- 15 MHz, 16.6 dec/V, 0.001: x0.328 / x0.268
- 15 MHz, 16.6 dec/V, 0.0001: x0.325 / x0.267
- 15 MHz, 33.69 dec/V, 0.001: x0.529 / x0.424
- 15 MHz, 33.69 dec/V, 0.0001: x0.523 / x0.421
- 10 MHz, 3.87 dec/V, 0.001: x0.113 / x0.109
- 10 MHz, 3.87 dec/V, 0.0001: x0.113 / x0.108
- 10 MHz, 10 dec/V, 0.001: x0.162 / x0.140
- 10 MHz, 10 dec/V, 0.0001: x0.161 / x0.139
- 10 MHz, 16.6 dec/V, 0.001: x0.226 / x0.183
- 10 MHz, 16.6 dec/V, 0.0001: x0.223 / x0.182
- 10 MHz, 33.69 dec/V, 0.001: x0.387 / x0.300
- 10 MHz, 33.69 dec/V, 0.0001: x0.382 / x0.298

## B. Every condition: per-channel line margin 99.99 % and 99.9 % (33.69 dec/V), tolerated move (mV); 100 / 15 MHz

| condition | 99.99 % | 99.9 % | tolerated move |
|---|---|---|---|
| NMOS, 0.3 V underdrive|300 K | 28.8 / 12.7 | 90.3 / 40.2 | 600 / 600 |
| NMOS, 0.3 V underdrive|77 K proxy | 37.5 / 16.6 | 117 / 52.4 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K proxy | 29.6 / 13.1 | 92.8 / 41.4 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K high | 23 / 10.1 | 72 / 32 | 500 / 500 |
| NMOS, 0.3 V underdrive|77 K Beall fit | 17 / 7.51 | 53.4 / 23.7 | 600 / 600 |
| NMOS, 0.3 V underdrive|4 K, Beall pMOS | 29 / 12.8 | 90.9 / 40.6 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 120 K) | 92.2 / 40.6 | 289 / 128 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K, tree, ESD-dominated droop | 31.4 / 13.9 | 98.3 / 44 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K, tree, one reticle | 31.4 / 13.9 | 98.3 / 44 | 500 / 500 |
| bootstrapped (transistor level), 0.3 V underdrive|300 K | 10.6 / 4.84 | 33.1 / 15.3 | 1200 / 1200 |
| bootstrapped (transistor level), 0.3 V underdrive|77 K proxy | 3.62 / 1.63 | 11.3 / 5.14 | 1200 / 200 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K proxy | 2.64 / 1.18 | 8.25 / 3.74 | 1200 / 195.3 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K high | 2.59 / 1.15 | 8.11 / 3.64 | 1200 / 191.5 |
| bootstrapped (transistor level), 0.3 V underdrive|77 K Beall fit | 5.75 / 2.65 | 18 / 8.38 | 1200 / 1200 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, Beall pMOS | 5.48 / 2.49 | 17.1 / 7.87 | 1200 / 1200 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 120 K) | 2.01 / 0.9 | 6.29 / 2.84 | 1200 / 126.8 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, ESD-dominated droop | 2.11 / 0.949 | 6.61 / 3 | 1200 / 153.7 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, one reticle | 2.02 / 0.913 | 6.33 / 2.88 | 400 / 148.2 |
| T-switch + OTA buffer|300 K | 9.34 / 4.77 | 29.1 / 15 | 1200 / 1200 |
| T-switch + OTA buffer|77 K proxy | 4.6 / 2.22 | 14.4 / 7.02 | 1200 / 1200 |
| T-switch + OTA buffer|4 K proxy | 4.91 / 2.39 | 15.4 / 7.54 | 1200 / 1200 |
| T-switch + OTA buffer|4 K high | 5.04 / 2.46 | 15.7 / 7.78 | 1200 / 1200 |
| T-switch + OTA buffer|77 K Beall fit | 5.61 / 2.77 | 17.5 / 8.74 | 1200 / 1200 |
| T-switch + OTA buffer|4 K, Beall pMOS | 5.68 / 2.83 | 17.7 / 8.94 | 1200 / 1200 |
| T-switch + OTA buffer|4 K, steep (T_eff 120 K) | 2.64 / 1.36 | 8.24 / 4.28 | 1200 / 144.2 |
| T-switch + OTA buffer|4 K, tree, ESD-dominated droop | 5.46 / 2.79 | 17 / 8.82 | 1200 / 1200 |
| T-switch + OTA buffer|4 K, tree, one reticle | 6.86 / 3.58 | 21.4 / 11.3 | 1200 / 1200 |
| TG + dummies|300 K | 6.72 / 3.48 | 21 / 11 | 1200 / 1200 |
| TG + dummies|77 K proxy | 4.92 / 2.55 | 15.3 / 8.04 | 1200 / 1200 |
| TG + dummies|4 K proxy | 4.65 / 2.41 | 14.5 / 7.62 | 1200 / 1200 |
| TG + dummies|4 K high | 4.5 / 2.34 | 14 / 7.39 | 1200 / 1200 |
| TG + dummies|77 K Beall fit | 5.41 / 2.81 | 16.9 / 8.86 | 1200 / 1200 |
| TG + dummies|4 K, Beall pMOS | 7.61 / 3.91 | 23.7 / 12.3 | 1200 / 1200 |
| TG + dummies|4 K, steep (T_eff 120 K) | 2.75 / 1.43 | 8.59 / 4.51 | 1200 / 200 |
| TG + dummies|4 K, tree, ESD-dominated droop | 5.09 / 2.66 | 15.9 / 8.39 | 1200 / 1200 |
| TG + dummies|4 K, tree, one reticle | 5.09 / 2.66 | 15.9 / 8.39 | 1200 / 1200 |
| TG, no ESD|300 K | 1.05 / 0.448 | 3.29 / 1.42 | 175.1 / 69.93 |
| TG, no ESD|77 K proxy | 1.09 / 0.464 | 3.4 / 1.47 | 197.7 / 79 |
| TG, no ESD|4 K proxy | 1.02 / 0.434 | 3.19 / 1.37 | 168.6 / 67.25 |
| TG, no ESD|4 K high | 0.983 / 0.421 | 3.08 / 1.33 | 154.3 / 61.3 |
| TG, no ESD|77 K Beall fit | 2.02 / 0.882 | 6.33 / 2.79 | 400 / 164.1 |
| TG, no ESD|4 K, Beall pMOS | 2.04 / 0.876 | 6.38 / 2.77 | 200 / 145.2 |
| TG, no ESD|4 K, steep (T_eff 120 K) | 1.13 / 0.494 | 3.54 / 1.56 | 200 / 81.02 |
| TG, no ESD|4 K, tree, ESD-dominated droop | 1.02 / 0.437 | 3.2 / 1.38 | 174.4 / 69.45 |
| TG, no ESD|4 K, tree, one reticle | 1.02 / 0.437 | 3.2 / 1.38 | 174.4 / 69.45 |
| TG, ESD on the node|300 K | 1.1 / 0.468 | 3.44 / 1.48 | 183 / 73.05 |
| TG, ESD on the node|77 K proxy | 1.23 / 0.525 | 3.85 / 1.66 | 200 / 90.78 |
| TG, ESD on the node|4 K proxy | 1.16 / 0.493 | 3.62 / 1.56 | 194.1 / 77.44 |
| TG, ESD on the node|4 K high | 1.21 / 0.518 | 3.78 / 1.64 | 171.6 / 68.14 |
| TG, ESD on the node|77 K Beall fit | 10.7 / 4.68 | 33.5 / 14.8 | 600 / 600 |
| TG, ESD on the node|4 K, Beall pMOS | 34.4 / 15.3 | 108 / 48.2 | 400 / 400 |
| TG, ESD on the node|4 K, steep (T_eff 120 K) | 1.26 / 0.551 | 3.95 / 1.74 | 200 / 91.61 |
| TG, ESD on the node|4 K, tree, ESD-dominated droop | 1.16 / 0.496 | 3.64 / 1.57 | 200 / 79.97 |
| TG, ESD on the node|4 K, tree, one reticle | 1.16 / 0.496 | 3.64 / 1.57 | 200 / 79.97 |
| GF180 NMOS, 0.3 V underdrive|300 K | 541 / 231 | 1.7e+03 / 728 | 600 / 600 |
| GF180 NMOS, 0.3 V underdrive|4 K proxy | 661 / 285 | 2.07e+03 / 900 | 600 / 600 |
| GF180 NMOS, 0.3 V underdrive|4 K high | 620 / 267 | 1.94e+03 / 843 | 600 / 600 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|300 K | 34.6 / 14.9 | 108 / 47 | 1200 / 1200 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|4 K proxy | 13.5 / 5.76 | 42.3 / 18.2 | 1200 / 1200 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|4 K high | 13.9 / 5.93 | 43.5 / 18.7 | 1200 / 1200 |
| GF180 TG + dummies|300 K | 5.39 / 2.78 | 16.8 / 8.77 | 1200 / 1200 |
| GF180 TG + dummies|4 K proxy | 5.15 / 2.66 | 16.1 / 8.4 | 1200 / 1200 |
| GF180 TG + dummies|4 K high | 5.49 / 2.84 | 17.1 / 8.97 | 1200 / 1200 |
| GF180 TG, no ESD|300 K | 0.586 / 0.246 | 1.84 / 0.779 | 94.92 / 34.52 |
| GF180 TG, no ESD|4 K proxy | 0.62 / 0.263 | 1.94 / 0.831 | 85.56 / 30.01 |
| GF180 TG, no ESD|4 K high | 0.66 / 0.281 | 2.07 / 0.887 | 85.69 / 30.11 |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|300 K | 118 / 50.8 | 371 / 160 | 1200 / 1200 |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|4 K proxy | 122 / 52.6 | 381 / 166 | 1200 / 1200 |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|4 K high | 112 / 48.5 | 352 / 153 | 1200 / 1200 |
| GF180 TG, no ESD, W 0.42|300 K | 1.41 / 0.594 | 4.42 / 1.88 | 200 / 99.27 |
| GF180 TG, no ESD, W 0.42|4 K proxy | 1.45 / 0.617 | 4.55 / 1.95 | 200 / 87.5 |
| GF180 TG, no ESD, W 0.42|4 K high | 1.52 / 0.649 | 4.77 / 2.05 | 200 / 87.17 |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 30 K) | 154 / 66.2 | 482 / 209 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 20 K) | 297 / 127 | 930 / 403 | 400 / 400 |
| NMOS, 0.3 V underdrive|4 K, mismatch x 1.5 | 27.1 / 12.3 | 85 / 38.7 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K, mismatch x 2 | 61.8 / 28.4 | 193 / 89.7 | 400 / 400 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 30 K) | 1.23 / 0.537 | 3.85 / 1.7 | 183.9 / 77.35 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 20 K) | 1.19 / 0.535 | 3.72 / 1.69 | 176.4 / 78.09 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 1.5 | 2.41 / 1.11 | 7.55 / 3.5 | 1200 / 181.8 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 2 | 2.19 / 1.02 | 6.84 / 3.23 | 1200 / 167.8 |
| TG + dummies|4 K, steep (T_eff 30 K) | 2.46 / 1.28 | 7.68 / 4.02 | 1200 / 200 |
| TG + dummies|4 K, steep (T_eff 20 K) | 2.44 / 1.26 | 7.61 / 3.99 | 1200 / 200 |
| TG + dummies|4 K, mismatch x 1.5 | 3.37 / 1.76 | 10.5 / 5.54 | 1200 / 200 |
| TG + dummies|4 K, mismatch x 2 | 2.6 / 1.36 | 8.12 / 4.3 | 1200 / 200 |
| TG, no ESD|4 K, mismatch x 1.5 | 0.984 / 0.425 | 3.08 / 1.34 | 164.2 / 66 |
| TG, no ESD|4 K, mismatch x 2 | 0.961 / 0.418 | 3.01 / 1.32 | 159.6 / 64.76 |

Margin factors at 15 MHz: 99.99 % x0.421 to x0.523; 99.9 % x0.424 to x0.529.
Smallest tolerated move at 15 MHz: SKY130 61.3 mV, GF180 30.0 mV.
Smallest per-channel line margin at 99.9 %, 15 MHz: 0.779.

## C. Combined worst case

Tolerated move (bootstrapped switch): 100 MHz 71.5 mV, 15 MHz 35.6 mV

| design | 100 MHz: line / quadratic / 0.4 V at 99.99 % (99.9 %) | 15 MHz: same |
|---|---|---|
| NMOS, 0.3 V underdrive | 480 (1.5e+03) / 9.72e+03 (1e+04) / 480 (1.5e+03) | 213 (674) / 4.43e+03 (1e+04) / 213 (674) |
| bootstrapped (transistor level), 0.3 V underdrive | 0.577 (1.8) / 1.17 (3.65) / 1.47 (4.59) | 0.281 (0.888) / 0.607 (1.92) / 0.769 (2.43) |
| T-switch + OTA buffer | 2.1 (6.55) / 2.54 (7.93) / 2.83 (8.84) | 1.09 (3.45) / 1.33 (4.19) / 1.48 (4.67) |
| TG + dummies | 1.39 (4.32) / 1.62 (5.05) / 99.9 (313) | 0.724 (2.29) / 0.846 (2.67) / 44.6 (141) |
| TG, no ESD | 0.893 (2.8) / 2.33 (7.28) / 46.9 (147) | 0.402 (1.27) / 1.15 (3.64) / 20.3 (64.2) |
| TG, ESD on the node | 0.991 (3.1) / 2.62 (8.18) / 48.8 (153) | 0.446 (1.41) / 1.3 (4.09) / 21.1 (66.6) |

## D. Open-loop criterion: smallest margin / tolerated growth / point accuracy (µV) for line, quadratic, 0.4 V

| design | 100 MHz | 15 MHz |
|---|---|---|
| NMOS, 0.3 V underdrive | line: 17 / 19.6 / 41; quadratic: 83.8 / 93.9 / 33; window: 31.3 / 35.9 / 39 | line: 7.51 / 8.2 / 21; quadratic: 36.6 / 39.5 / 17; window: 13.8 / 15.1 / 20 |
| bootstrapped (transistor level), 0.3 V underdrive | line: 2.01 / 2.25 / 31; quadratic: 10.6 / 13.8 / 34; window: 8.08 / 10.1 / 32 | line: 0.9 / 0.883 / 0; quadratic: 4.84 / 5.72 / 17; window: 3.66 / 4.17 / 16 |
| T-switch + OTA buffer | line: 2.64 / 7.54 / 41; quadratic: 4.53 / 10.3 / 34; window: 4.86 / 12.1 / 33 | line: 1.36 / 2.41 / 15; quadratic: 2.27 / 3.95 / 17; window: 2.46 / 4.65 / 17 |
| TG + dummies | line: 2.75 / 12.4 / 32; quadratic: 3.19 / 13.6 / 31; window: 10.8 / 50 / 33 | line: 1.43 / 3.63 / 17; quadratic: 1.65 / 4.46 / 16; window: 5.59 / 20.3 / 17 |
| TG, no ESD | line: 0.983 / 0.982 / 0; quadratic: 3.39 / 3.75 / 31; window: 3.99 / 4.22 / 32 | line: 0.421 / 0.398 / 0; quadratic: 1.49 / 1.54 / 13; window: 1.72 / 1.76 / 15 |
| TG, ESD on the node | line: 1.1 / 1.1 / 8; quadratic: 3.58 / 3.9 / 30; window: 4.58 / 4.96 / 31 | line: 0.468 / 0.452 / 0; quadratic: 1.56 / 1.61 / 13; window: 1.99 / 2.06 / 15 |
| GF180 NMOS, 0.3 V underdrive | line: 541 / 562 / 44; quadratic: 1e+04 / 1e+03 / 34; window: 1.33e+03 / 1e+03 / 39 | line: 231 / 236 / 23; quadratic: 9.33e+03 / 1e+03 / 18; window: 572 / 590 / 20 |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V | line: 112 / 121 / 44; quadratic: 1.22e+03 / 1e+03 / 34; window: 595 / 650 / 33 | line: 48.5 / 51.1 / 23; quadratic: 532 / 575 / 18; window: 258 / 273 / 17 |
| GF180 TG + dummies | line: 5.15 / 18.9 / 44; quadratic: 6.58 / 17.8 / 34; window: 8.81 / 24.6 / 33 | line: 2.66 / 7.5 / 22; quadratic: 3.34 / 7.04 / 17; window: 4.47 / 9.92 / 17 |
| GF180 TG, no ESD | line: 0.586 / 0.585 / 0; quadratic: 1.94 / 1.98 / 25; window: 2.2 / 2.27 / 28 | line: 0.246 / 0.246 / 0; quadratic: 0.827 / 0.823 / 0; window: 0.942 / 0.94 / 0 |
| GF180 TG, no ESD, W 0.42 | line: 1.41 / 1.41 / 18; quadratic: 4.57 / 4.67 / 32; window: 5.03 / 5.31 / 32 | line: 0.594 / 0.593 / 0; quadratic: 1.94 / 1.96 / 14; window: 2.16 / 2.22 / 15 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive | line: 13.5 / 14.1 / 43; quadratic: 80 / 83.8 / 34; window: 58.4 / 60.9 / 33 | line: 5.76 / 5.91 / 22; quadratic: 34.2 / 35.2 / 18; window: 24.9 / 25.6 / 17 |
