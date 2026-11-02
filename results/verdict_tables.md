# Tail-corrected margins and floored probabilities

tau: TG, no ESD|300 K 2.0 %, TG, no ESD|4 K proxy 9.8 %, TG, no ESD|4 K high 6.1 %, bootstrapped (transistor level), 0.3 V underdrive|4 K proxy 7.2 %, NMOS, 0.3 V underdrive|4 K proxy 7.5 %; elsewhere 9.8 %.

## Verdicts other than pass (all conditions, strictest point, levels set open-loop)

| design | condition | calibration | corrected margin [90 %] | verdict |
|---|---|---|---|---|
| D NTB | 300 K | shared | 1.1 [0.915, 1.56] | unresolved |
| D TGH | 300 K | full | 1.02 [1.01, 1.03] | unresolved |
| D TG | 300 K | full | 1.1 [1.08, 1.11] | unresolved |
| D TG | 300 K | shared | 0.914 [0.797, 0.985] | unresolved |
| TG + dummies, W 0.84 | 4 K proxy | shared | 0.583 [0.448, 1.05] | unresolved |
| TG + dummies, W 0.84 | 4 K, tree, ESD-dominated droop | shared | 0.587 [0.437, 1.11] | unresolved |
| TG, ESD on the node | 300 K | full | 1.1 [1.08, 1.12] | unresolved |
| TG, ESD on the node | 300 K | shared | 0.914 [0.805, 0.978] | unresolved |
| TG, ESD on the node | 4 K high | shared | 0.866 [0.777, 1.01] | unresolved |
| TG, ESD on the node | 4 K, steep (T_eff 120 K) | shared | 0.898 [0.782, 1.09] | unresolved |
| TG, ESD on the node | 4 K, tree, ESD-dominated droop | shared | 0.83 [0.744, 0.982] | unresolved |
| TG, ESD on the node | 4 K, tree, one reticle | shared | 0.83 [0.731, 0.971] | unresolved |
| TG, ESD on the node | 77 K proxy | shared | 0.845 [0.743, 1.02] | unresolved |
| TG, no ESD, W 0.42, 0.3 V underdrive | 4 K proxy | shared | 1.17 [1.03, 1.44] | unresolved |
| TG, no ESD, W 0.42, 0.3 V underdrive | 4 K, tree, ESD-dominated droop | shared | 1.18 [1.03, 1.46] | unresolved |
| TG, no ESD, W 0.42 | 4 K proxy | shared | 1.17 [1.03, 1.46] | unresolved |
| TG, no ESD, W 0.42 | 4 K, tree, ESD-dominated droop | shared | 1.18 [1.03, 1.45] | unresolved |
| TG, no ESD, W 3 | 4 K proxy | full | 0.348 [0.346, 0.351] | fail |
| TG, no ESD, W 3 | 4 K, tree, ESD-dominated droop | full | 0.36 [0.358, 0.362] | fail |
| TG, no ESD | 300 K | full | 1.05 [1.03, 1.07] | unresolved |
| TG, no ESD | 300 K | shared | 0.868 [0.758, 0.933] | unresolved |
| TG, no ESD | 4 K high | full | 0.983 [0.955, 1.01] | unresolved |
| TG, no ESD | 4 K proxy | full | 1.02 [1.01, 1.03] | unresolved |
| TG, no ESD | 4 K, steep (T_eff 120 K) | full | 1.13 [1.08, 1.19] | unresolved |
| TG, no ESD | 4 K, steep (T_eff 120 K) | shared | 0.803 [0.69, 0.974] | unresolved |
| TG, no ESD | 4 K, tree, ESD-dominated droop | full | 1.02 [0.999, 1.05] | unresolved |
| TG, no ESD | 4 K, tree, one reticle | full | 1.02 [0.999, 1.05] | unresolved |
| TG, no ESD | 77 K proxy | full | 1.09 [1.06, 1.11] | unresolved |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K high | shared | 0.779 [0.618, 1.13] | unresolved |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, Beall pMOS | shared | 1.05 [0.821, 1.54] | unresolved |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 600 ps | shared | 0.72 [0.575, 1.06] | unresolved |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 67 ps | shared | 0.894 [0.712, 1.27] | unresolved |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 120 K) | shared | 0.791 [0.643, 1.17] | unresolved |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 20 K) | full | 1.19 [1.13, 1.29] | unresolved |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 20 K) | shared | 0.834 [0.738, 1.01] | unresolved |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 30 K) | shared | 0.759 [0.675, 0.925] | unresolved |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K Beall fit | shared | 0.816 [0.633, 1.21] | unresolved |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K proxy | shared | 0.873 [0.721, 1.41] | unresolved |
| bootstrapped (transistor level), W 1 | 4 K, tree, ESD-dominated droop | full | 1.01 [0.964, 1.09] | unresolved |

## Table S3 (margin columns)

| Cell | Margin, per-channel calibration | Margin, shared calibration | P(any of 10^6 channels over budget), per channel / shared |
|---|---|---|---|
| NMOS switch | 16.5 [15.7, 17.5] | 3.82 [3.07, 5.35] | < 10^-6 / < 10^-6 |
| TG | 1.1 [1.08, 1.11], unresolved | 0.914 [0.797, 0.985], unresolved | < 10^-6 / 1.00 |
| TG with dummies | 7.65 [6.44, 9.37] | 0.727 [0.635, 0.89], fail | < 10^-6 / 1.00 |
| Bootstrapped NMOS | 209 [199, 226] | 2.84 [2.56, 3.33] | < 10^-6 / < 10^-6 |
| Charge-locked TG | 2.08 [2.06, 2.12] | 1.72 [1.53, 1.85] | < 10^-6 / < 10^-6 |
| Thick-oxide T-switch | 7.55 [6.79, 8.86] | 0.298 [0.256, 0.38], fail | < 10^-6 / 1.00 |
| TG, high-threshold PMOS | 1.02 [1.01, 1.03], unresolved | 0.83 [0.765, 0.898], fail | < 10^-6 / 1.00 |
| T-switch, buffered, thick oxide | 7.5 [6.78, 9.02] | 0.296 [0.254, 0.379], fail | < 10^-6 / 1.00 |
| T-switch, buffered, thin oxide | 3.79 [3.56, 4.27] | 1.1 [0.915, 1.56], unresolved | < 10^-6 / 0.05 |

## Table S6

| Cell | 300 K | 77 K proxy | 4 K proxy | 4 K high | 77 K Beall fit | 4 K, Beall pMOS | 4 K, steep (T_eff 120 K) | 4 K, tree, ESD-dominated droop | 4 K, tree, one reticle |
|---|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 28.8 / 5.73 | 37.5 / 6.05 | 29.7 / 6.24 | 23 / 6.01 | 17 / 5.57 | 29 / 6.05 | 92.2 / 5.9 | 31.4 / 6.3 | 31.4 / 6.29 |
| bootstrapped (transistor level), 0.3 V underdrive | 10.6 / 1.66 | 3.62 / 0.873 | 2.65 / 0.741 | 2.59 / 0.779 | 5.75 / 0.816 | 5.48 / 1.05 | 2.01 / 0.791 | 2.11 / 0.417 | 2.02 / 0.339 |
| T-switch + OTA buffer | 9.34 / 0.35 | 4.59 / 0.358 | 4.93 / 0.367 | 5.04 / 0.373 | 5.61 / 0.36 | 5.69 / 0.367 | 2.65 / 0.348 | 5.45 / 0.372 | 6.86 / 0.375 |
| TG + dummies | 6.72 / 0.633 | 4.9 / 0.668 | 4.78 / 0.683 | 4.53 / 0.708 | 5.41 / 1.81 | 7.6 / 1.76 | 2.76 / 0.639 | 5.11 / 0.69 | 5.13 / 0.688 |
| TG, no ESD | 1.05 / 0.868 (unresolved) | 1.09 / 0.743 (unresolved) | 1.02 / 0.619 (unresolved) | 0.983 / 0.722 (unresolved) | 2.02 / 1.59 | 2.04 / 1.6 | 1.13 / 0.803 (unresolved) | 1.02 / 0.728 (unresolved) | 1.02 / 0.727 (unresolved) |
| TG, ESD on the node | 1.1 / 0.914 (unresolved) | 1.23 / 0.845 | 1.16 / 0.711 | 1.21 / 0.866 | 10.7 / 3.7 | 34.4 / 4.06 | 1.26 / 0.898 | 1.16 / 0.83 | 1.16 / 0.83 |

## Table S7

| Cell | $W_n$ (µm) | 50 Ω | Tree |
|---|---|---|---|
| NMOS, 0.3 V underdrive | 0.42 | 29.7 / 6.24 | 31.4 / 6.3 |
| NMOS, 0.3 V underdrive | 1 | 12.2 / 3.3 | 6.88 / 3.33 |
| NMOS, 0.3 V underdrive | 3 | 2.14 / 1.41 | 3.45 / 2.02 |
| bootstrapped (transistor level), 0.3 V underdrive | 0.42 | 2.65 / 0.741 | 2.11 / 0.417 |
| bootstrapped (transistor level), 0.3 V underdrive | 1 | 1.46 / 0.571 | 1.01 / 0.25 (unresolved) |
| T-switch + OTA buffer | 0.42 | 7.12 / 0.433 | 11.2 / 0.436 |
| T-switch + OTA buffer | 0.84 | 4.93 / 0.367 | 5.45 / 0.372 |
| TG + dummies | 0.84 | 3.55 / 0.583 | 3.74 / 0.587 |
| TG + dummies | 1 | 4.78 / 0.683 | 5.11 / 0.69 |
| TG, no ESD | 0.42 | 2.52 / 1.17 | 2.53 / 1.18 |
| TG, no ESD, 0.3 V underdrive | 0.42 | 2.51 / 1.17 | 2.53 / 1.18 |
| TG, no ESD | 1 | 1.02 / 0.619 (unresolved) | 1.02 / 0.728 (unresolved) |
| TG, no ESD | 3 | 0.348 / 0.244 (fail) | 0.36 / 0.254 (fail) |

## Table S8

| Variant | NMOS, 0.3 V underdrive: 99.99% | 99.9% | Bootstrapped NMOS: 99.99% | 99.9% | TG with dummies: 99.99% | 99.9% |
|---|---|---|---|---|---|---|
| 4 K | 29.7 (0) | 92.9 | 2.65 (0) | 8.3 | 4.78 (0) | 14.9 |
| Steep, $T_{\mathrm{eff}}$ = 120 K | 92.2 (0) | 289 | 2.01 (0) | 6.29 | 2.76 (0) | 8.61 |
| Steep, $T_{\mathrm{eff}}$ = 30 K | 154 (0) | 483 | 1.23 (0) | 3.85 | 2.46 (0) | 7.69 |
| Steep, $T_{\mathrm{eff}}$ = 20 K | 297 (0) | 930 | 1.19 (0), unresolved | 3.72 | 2.44 (0) | 7.61 |
| Clock edges 600 ps | 31.3 (0) | 97.9 | 2.35 (0) | 7.36 | 5.07 (0) | 15.8 |
| Clock edges 67 ps | 28.2 (0) | 88.4 | 3.11 (0) | 9.75 | 4.53 (0) | 14.1 |
| Tree source, fan-out 10 at 5 × 10^5 | 31.4 (0) | 98.2 | 2.12 (0) | 6.65 | 5.12 (0) | 16 |
| Tree source, best tree at 3.1 mV/s | 31.4 (0) | 98.2 | 2.11 (0) | 6.61 | 5.11 (0) | 16 |
| Tree source, best tree on one reticle | 31.4 (0) | 98.2 | 2.02 (0) | 6.33 | 5.13 (0) | 16 |
| Tree source, best tree with protection diodes on 1 pF | – | – | 2.16 (0) | 6.77 | – | – |
| Buffered final line | – | – | 2.2 (0) | 6.89 | – | – |
| Mismatch × 1.5 | 27.2 (0) | 85 | 2.42 (0) | 7.56 | 3.4 (0) | 10.6 |
| Mismatch × 2 | 61.7 (0) | 193 | 2.19 (0) | 6.84 | 2.64 (0) | 8.24 |

## Table S9

| Cell | Per channel: model | 95th bootstrap percentile | Mismatch × 2 | Curvature × 1.3 | Both | Shared, 4 K band |
|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | < 10^-6 | < 10^-6 | < 10^-6 | < 10^-6 | < 10^-6 | < 10^-6 |
| bootstrapped (transistor level), 0.3 V underdrive | < 10^-6 | < 10^-6 | < 10^-6 | < 10^-6 | < 10^-6 | 1.00 |
| T-switch + OTA buffer | < 10^-6 | < 10^-6 | < 10^-6 | < 10^-6 | < 10^-6 | 1.00 |
| TG + dummies | < 10^-6 | < 10^-6 | < 10^-6 | < 10^-6 | < 10^-6 | 1.00 |
| TG, no ESD | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| TG, ESD on the node | < 10^-6 | < 10^-6 | < 10^-6 | 1.00 | 1.00 | 1.00 |

## Ledoit-Wolf check and dimensionality (4 K band, strictest point, per channel)

| design | channels | voltages in the fit | voltages in the closed form | shrinkage | corrected margin, sample / Ledoit-Wolf |
|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 20 | 22 | 6 | 0.11 | 29.6 / 29.8 |
| bootstrapped (transistor level), 0.3 V underdrive | 100 | 25 | 7 | 0.02 | 2.64 / 2.64 |
| T-switch + OTA buffer | 20 | 25 | 7 | 0.14 | 4.91 / 4.97 |
| TG + dummies | 20 | 25 | 7 | 0.10 | 4.65 / 4.78 |
| TG, no ESD | 100 | 25 | 7 | 0.03 | 1.02 / 1.02 |
| TG, ESD on the node | 100 | 25 | 7 | 0.03 | 1.16 / 1.15 |

## Curvature scale at which the corrected per-channel margin falls to one (strictest point)

| design | lowest over Figure 6 conditions (condition) | 4 K band | curvature of the mean channel over the bands (µV) |
|---|---|---|---|
| NMOS, 0.3 V underdrive | 19.59 (77 K Beall fit) | 20.00 | 1.0 to 5.1 |
| bootstrapped (transistor level), 0.3 V underdrive | 2.25 (4 K, steep (T_eff 120 K)) | 3.05 | 7.2 to 41.1 |
| T-switch + OTA buffer | 7.54 (77 K proxy) | 8.40 | 4.0 to 12.4 |
| TG + dummies | 12.35 (4 K, steep (T_eff 120 K)) | 20.00 | 2.9 to 6.2 |
| TG, no ESD | 0.98 (4 K high) | 1.02 | 45.0 to 101.0 |
| TG, ESD on the node | 1.10 (300 K) | 1.16 | 2.5 to 88.7 |

## Summary numbers for the text

- NMOS, 0.3 V underdrive: per-channel 17 to 92.2 (cryo 50 ohm 17-92.2, trees 31.4-31.4); shared 5.57-6.3; verdicts ['pass']; 4 K 29.7 pass
- bootstrapped (transistor level), 0.3 V underdrive: per-channel 2.01 to 10.6 (cryo 50 ohm 2.01-5.75, trees 2.02-2.11); shared 0.339-1.66; verdicts ['pass']; 4 K 2.65 pass
- T-switch + OTA buffer: per-channel 2.65 to 9.34 (cryo 50 ohm 2.65-5.69, trees 5.45-6.86); shared 0.348-0.375; verdicts ['pass']; 4 K 4.93 pass
- TG + dummies: per-channel 2.76 to 7.6 (cryo 50 ohm 2.76-7.6, trees 5.11-5.13); shared 0.633-1.81; verdicts ['pass']; 4 K 4.78 pass
- TG, no ESD: per-channel 0.983 to 2.04 (cryo 50 ohm 0.983-2.04, trees 1.02-1.02); shared 0.619-1.6; verdicts ['pass', 'unresolved']; 4 K 1.02 unresolved
- TG, ESD on the node: per-channel 1.1 to 34.4 (cryo 50 ohm 1.16-34.4, trees 1.16-1.16); shared 0.711-4.06; verdicts ['pass', 'unresolved']; 4 K 1.16 pass
- 99.9 %, 33.69, full, Figure 6 designs, all conditions: lowest 3.08 (TG, no ESD|4 K high)
- 99.9 %, 33.69, shared, Figure 6 designs, all conditions: lowest 1.06 (bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, one reticle)
- 99.9 %, 10 dec/V, full, Figure 6 designs, all conditions: lowest 7.15 (TG, no ESD|4 K high)
- 99.9 %, 10 dec/V, shared, Figure 6 designs, all conditions: lowest 2.76 (bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, one reticle)
- move20mV (as stored; fine grid in the 4 K band), cryo and trees: lowest 9.1 (TG, no ESD|4 K high)
- move50mV (as stored; fine grid in the 4 K band), cryo and trees: lowest 3.64 (TG, no ESD|4 K high)
- 4 K, mismatch x 1.5: NMOS, 0.3 V underdrive 27.2 / shared 4.15, bootstrapped (transistor level), 0.3 V underdrive 2.42 / shared 0.512, TG + dummies 3.4 / shared 0.463
- 4 K, mismatch x 2: NMOS, 0.3 V underdrive 61.7 / shared 3.25, bootstrapped (transistor level), 0.3 V underdrive 2.19 / shared 0.36, TG + dummies 2.64 / shared 0.349
- Table S3 per channel: D BOOT 209 pass, D CLK 2.08 pass, D NSW 16.5 pass, D NTB 3.79 pass, D TGD 7.65 pass, D TGH 1.02 unresolved, D TG 1.1 unresolved, D TSWB 7.5 pass, D TSW 7.55 pass
- Table S3 99.9 %/10 dec/V per channel lowest: 7.38; 99.9 %/33.69 lowest: 3.2
