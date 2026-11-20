# Budgets for equal signs against the Zeeman difference, and of a held amplitude

## A. Untracked budgets (µV): single gate / equal signs; gate 50, 100, 200 ns for 100, 50, 25 MHz

| Zeeman | target | 3.87 dec/V | 10 dec/V | 16.6 dec/V | 33.69 dec/V |
|---|---|---|---|---|---|
| 100 MHz | 0.001 | 1986.3 / 1035.5 | 1373.8 / 798.9 | 966.3 / 602.7 | 524.7 / 348.9 |
| 100 MHz | 0.0001 | 628.8 / 327.5 | 437.3 / 253.4 | 308.7 / 191.6 | 168.2 / 111.3 |
| 50 MHz | 0.001 | 1083.0 / 548.0 | 930.5 / 495.5 | 760.3 / 430.3 | 477.2 / 298.0 |
| 50 MHz | 0.0001 | 342.5 / 173.3 | 294.9 / 156.8 | 241.7 / 136.4 | 152.5 / 94.8 |
| 25 MHz | 0.001 | 556.5 / 279.1 | 529.1 / 269.7 | 487.6 / 255.5 | 376.8 / 213.6 |
| 25 MHz | 0.0001 | 175.9 / 88.2 | 167.4 / 85.3 | 154.4 / 80.8 | 119.8 / 67.7 |

Change from 100 to 25 MHz (single gate / equal signs):

- 3.87 dec/V, 0.001: x0.280 / x0.270
- 3.87 dec/V, 0.0001: x0.280 / x0.269
- 10 dec/V, 0.001: x0.385 / x0.338
- 10 dec/V, 0.0001: x0.383 / x0.337
- 16.6 dec/V, 0.001: x0.505 / x0.424
- 16.6 dec/V, 0.0001: x0.500 / x0.422
- 33.69 dec/V, 0.001: x0.718 / x0.612
- 33.69 dec/V, 0.0001: x0.712 / x0.608

## B. Stark coefficient on both qubits, 100 MHz, 99.9 % (mV): single gate / equal signs

- 3.87|one: 1.986 / 1.035
- 3.87|both_equal: 1.514 / 0.775
- 3.87|both_opposite: 1.480 / 0.757
- 10|one: 1.374 / 0.799
- 10|both_equal: 1.216 / 0.681
- 10|both_opposite: 1.148 / 0.635
- 33.69|one: 0.525 / 0.349
- 33.69|both_equal: 0.525 / 0.349
- 33.69|both_opposite: 0.500 / 0.322

## C. Held CZ amplitude: fractional error eps (%) and swing of the pulse line at k = 0.5 (mV)

| s (dec/V) | target | v0 (V) | eps single gate | eps equal signs | swing single | swing equal |
|---|---|---|---|---|---|---|
| 3.87 | 0.001 | 0.672 | 0.362 | 0.191 | 4.87 | 2.57 |
| 3.87 | 0.0001 | 0.672 | 0.115 | 0.0606 | 1.54 | 0.814 |
| 10 | 0.001 | 0.260 | 0.603 | 0.36 | 3.13 | 1.87 |
| 10 | 0.0001 | 0.260 | 0.192 | 0.114 | 0.999 | 0.594 |
| 16.6 | 0.001 | 0.157 | 0.682 | 0.434 | 2.14 | 1.36 |
| 16.6 | 0.0001 | 0.157 | 0.218 | 0.138 | 0.683 | 0.433 |
| 33.69 | 0.001 | 0.077 | 0.735 | 0.493 | 1.13 | 0.761 |
| 33.69 | 0.0001 | 0.077 | 0.236 | 0.157 | 0.364 | 0.243 |

## D. Strictest point with the budgets of a 25 MHz device (b_eq x0.608, b_ind x0.712)

| condition | per-channel line 100 / 25 MHz | shared line 100 / 25 MHz | Delta_max 100 / 25 MHz (mV) |
|---|---|---|---|
| NMOS, 0.3 V underdrive|300 K | 28.8 / 18.2 | 5.72 / 4.04 | 600 / 600 |
| NMOS, 0.3 V underdrive|77 K proxy | 37.5 / 23.7 | 6.05 / 4.28 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K proxy | 29.6 / 18.7 | 6.17 / 4.35 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K high | 23 / 14.5 | 6.01 / 4.23 | 500 / 500 |
| NMOS, 0.3 V underdrive|77 K Beall fit | 17 / 10.7 | 5.56 / 3.91 | 600 / 600 |
| NMOS, 0.3 V underdrive|4 K, Beall pMOS | 29 / 18.4 | 6.04 / 4.26 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 120 K) | 92.2 / 58.1 | 5.86 / 4.16 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K, tree, ESD-dominated droop | 31.4 / 19.9 | 6.29 / 4.44 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K, tree, one reticle | 31.4 / 19.9 | 6.29 / 4.44 | 500 / 500 |
| bootstrapped (transistor level), 0.3 V underdrive|300 K | 10.6 / 6.86 | 1.66 / 1.18 | 1200 / 1200 |
| bootstrapped (transistor level), 0.3 V underdrive|77 K proxy | 3.62 / 2.32 | 0.875 / 0.62 | 1200 / 1200 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K proxy | 2.64 / 1.69 | 0.747 / 0.526 | 1200 / 200 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K high | 2.59 / 1.64 | 0.776 / 0.549 | 1200 / 200 |
| bootstrapped (transistor level), 0.3 V underdrive|77 K Beall fit | 5.75 / 3.75 | 0.815 / 0.579 | 1200 / 1200 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, Beall pMOS | 5.48 / 3.53 | 1.05 / 0.748 | 1200 / 1200 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 120 K) | 2.01 / 1.28 | 0.792 / 0.558 | 1200 / 186.1 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, ESD-dominated droop | 2.11 / 1.35 | 0.417 / 0.295 | 1200 / 200 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, one reticle | 2.02 / 1.3 | 0.339 / 0.24 | 400 / 200 |
| T-switch + OTA buffer|300 K | 9.34 / 6.54 | 0.347 / 0.247 | 1200 / 1200 |
| T-switch + OTA buffer|77 K proxy | 4.6 / 3.1 | 0.356 / 0.253 | 1200 / 1200 |
| T-switch + OTA buffer|4 K proxy | 4.91 / 3.33 | 0.363 / 0.258 | 1200 / 1200 |
| T-switch + OTA buffer|4 K high | 5.04 / 3.42 | 0.37 / 0.263 | 1200 / 1200 |
| T-switch + OTA buffer|77 K Beall fit | 5.61 / 3.84 | 0.358 / 0.254 | 1200 / 1200 |
| T-switch + OTA buffer|4 K, Beall pMOS | 5.68 / 3.91 | 0.364 / 0.259 | 1200 / 1200 |
| T-switch + OTA buffer|4 K, steep (T_eff 120 K) | 2.64 / 1.86 | 0.345 / 0.246 | 1200 / 1200 |
| T-switch + OTA buffer|4 K, tree, ESD-dominated droop | 5.46 / 3.83 | 0.367 / 0.261 | 1200 / 1200 |
| T-switch + OTA buffer|4 K, tree, one reticle | 6.86 / 4.88 | 0.369 / 0.263 | 1200 / 1200 |
| TG + dummies|300 K | 6.72 / 4.76 | 0.631 / 0.448 | 1200 / 1200 |
| TG + dummies|77 K proxy | 4.92 / 3.48 | 0.666 / 0.473 | 1200 / 1200 |
| TG + dummies|4 K proxy | 4.65 / 3.3 | 0.686 / 0.487 | 1200 / 1200 |
| TG + dummies|4 K high | 4.5 / 3.19 | 0.708 / 0.502 | 1200 / 1200 |
| TG + dummies|77 K Beall fit | 5.41 / 3.83 | 1.8 / 1.28 | 1200 / 1200 |
| TG + dummies|4 K, Beall pMOS | 7.61 / 5.35 | 1.75 / 1.25 | 1200 / 1200 |
| TG + dummies|4 K, steep (T_eff 120 K) | 2.75 / 1.95 | 0.638 / 0.453 | 1200 / 200 |
| TG + dummies|4 K, tree, ESD-dominated droop | 5.09 / 3.62 | 0.689 / 0.489 | 1200 / 1200 |
| TG + dummies|4 K, tree, one reticle | 5.09 / 3.62 | 0.689 / 0.489 | 1200 / 1200 |
| TG, no ESD|300 K | 1.05 / 0.646 | 0.869 / 0.556 | 175.1 / 103.9 |
| TG, no ESD|77 K proxy | 1.09 / 0.669 | 0.743 / 0.494 | 197.7 / 117.3 |
| TG, no ESD|4 K proxy | 1.02 / 0.626 | 0.613 / 0.411 | 168.6 / 99.9 |
| TG, no ESD|4 K high | 0.983 / 0.607 | 0.722 / 0.475 | 154.3 / 91.15 |
| TG, no ESD|77 K Beall fit | 2.02 / 1.26 | 1.59 / 1.06 | 400 / 200 |
| TG, no ESD|4 K, Beall pMOS | 2.04 / 1.26 | 1.6 / 1.03 | 200 / 200 |
| TG, no ESD|4 K, steep (T_eff 120 K) | 1.13 / 0.708 | 0.803 / 0.539 | 200 / 120 |
| TG, no ESD|4 K, tree, ESD-dominated droop | 1.02 / 0.63 | 0.728 / 0.481 | 174.4 / 103.2 |
| TG, no ESD|4 K, tree, one reticle | 1.02 / 0.63 | 0.728 / 0.481 | 174.4 / 103.2 |
| TG, ESD on the node|300 K | 1.1 / 0.674 | 0.914 / 0.583 | 183 / 108.5 |
| TG, ESD on the node|77 K proxy | 1.23 / 0.757 | 0.845 / 0.561 | 200 / 134.8 |
| TG, ESD on the node|4 K proxy | 1.16 / 0.71 | 0.699 / 0.469 | 194.1 / 115 |
| TG, ESD on the node|4 K high | 1.21 / 0.746 | 0.865 / 0.573 | 171.6 / 101.3 |
| TG, ESD on the node|77 K Beall fit | 10.7 / 6.71 | 3.68 / 2.59 | 600 / 600 |
| TG, ESD on the node|4 K, Beall pMOS | 34.4 / 21.8 | 4 / 2.84 | 400 / 400 |
| TG, ESD on the node|4 K, steep (T_eff 120 K) | 1.26 / 0.79 | 0.899 / 0.604 | 200 / 135.7 |
| TG, ESD on the node|4 K, tree, ESD-dominated droop | 1.16 / 0.714 | 0.829 / 0.547 | 200 / 118.9 |
| TG, ESD on the node|4 K, tree, one reticle | 1.16 / 0.714 | 0.829 / 0.547 | 200 / 118.8 |
| GF180 NMOS, 0.3 V underdrive|300 K | 541 / 332 | 5.4 / 3.85 | 600 / 600 |
| GF180 NMOS, 0.3 V underdrive|4 K proxy | 661 / 410 | 5.41 / 3.85 | 600 / 600 |
| GF180 NMOS, 0.3 V underdrive|4 K high | 620 / 384 | 5.4 / 3.85 | 600 / 600 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|300 K | 34.6 / 21.4 | 3.76 / 2.68 | 1200 / 1200 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|4 K proxy | 13.5 / 8.31 | 3.16 / 2.24 | 1200 / 1200 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|4 K high | 13.9 / 8.55 | 3.17 / 2.25 | 1200 / 1200 |
| GF180 TG + dummies|300 K | 5.39 / 3.8 | 1.46 / 1.04 | 1200 / 1200 |
| GF180 TG + dummies|4 K proxy | 5.15 / 3.64 | 1.51 / 1.07 | 1200 / 1200 |
| GF180 TG + dummies|4 K high | 5.49 / 3.89 | 1.52 / 1.09 | 1200 / 1200 |
| GF180 TG, no ESD|300 K | 0.586 / 0.357 | 0.486 / 0.308 | 94.92 / 55.67 |
| GF180 TG, no ESD|4 K proxy | 0.62 / 0.38 | 0.52 / 0.331 | 85.56 / 49.92 |
| GF180 TG, no ESD|4 K high | 0.66 / 0.405 | 0.552 / 0.352 | 85.69 / 50.05 |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|300 K | 118 / 73.1 | 5.37 / 3.82 | 1200 / 1200 |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|4 K proxy | 122 / 75.6 | 5.38 / 3.83 | 1200 / 1200 |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|4 K high | 112 / 69.7 | 5.37 / 3.82 | 1200 / 1200 |
| GF180 TG, no ESD, W 0.42|300 K | 1.41 / 0.858 | 1.07 / 0.691 | 200 / 147.8 |
| GF180 TG, no ESD, W 0.42|4 K proxy | 1.45 / 0.89 | 1.12 / 0.724 | 200 / 130.5 |
| GF180 TG, no ESD, W 0.42|4 K high | 1.52 / 0.935 | 1.17 / 0.76 | 200 / 130.1 |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 30 K) | 154 / 95.2 | 5.68 / 4.04 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 20 K) | 297 / 183 | 5.71 / 4.06 | 400 / 400 |
| NMOS, 0.3 V underdrive|4 K, mismatch x 1.5 | 27.1 / 17.4 | 4.15 / 2.94 | 500 / 500 |
| NMOS, 0.3 V underdrive|4 K, mismatch x 2 | 61.8 / 40.2 | 3.24 / 2.3 | 400 / 400 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 30 K) | 1.23 / 0.77 | 0.758 / 0.519 | 183.9 / 113.4 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 20 K) | 1.19 / 0.762 | 0.835 / 0.572 | 176.4 / 112.9 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 1.5 | 2.41 / 1.57 | 0.51 / 0.362 | 1200 / 200 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 2 | 2.19 / 1.44 | 0.358 / 0.255 | 1200 / 200 |
| TG + dummies|4 K, steep (T_eff 30 K) | 2.46 / 1.74 | 0.614 / 0.435 | 1200 / 200 |
| TG + dummies|4 K, steep (T_eff 20 K) | 2.44 / 1.73 | 0.61 / 0.433 | 1200 / 200 |
| TG + dummies|4 K, mismatch x 1.5 | 3.37 / 2.39 | 0.462 / 0.328 | 1200 / 1200 |
| TG + dummies|4 K, mismatch x 2 | 2.6 / 1.85 | 0.349 / 0.248 | 1200 / 200 |
| TG, no ESD|4 K, mismatch x 1.5 | 0.984 / 0.61 | 0.604 / 0.408 | 164.2 / 97.86 |
| TG, no ESD|4 K, mismatch x 2 | 0.961 / 0.6 | 0.518 / 0.355 | 159.6 / 95.8 |

Margin ratio 25 / 100 MHz over all conditions: 0.609 to 0.712.
Delta_max ratio where below the whole window: 0.500 to 1.000.
Smallest Delta_max at 25 MHz: SKY130 91.15 mV, GF180 49.92 mV.
