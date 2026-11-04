# Calibration accuracy, settling widths and allocation

## A. Calibrations: margin on every simulated voltage / at the standard voltages only, and the per-point accuracy for a margin of one (strictest point)

| condition | line | quadratic | 0.4 V window line | sigma_req line / quadratic / window (uV) |
|---|---|---|---|---|
| NMOS, 0.3 V underdrive|300 K | 28.8 / 28.8 | 139 / 139 | 53.3 / 53.3 | 43.9 / 34.4 / 38.7 |
| NMOS, 0.3 V underdrive|77 K proxy | 37.5 / 37.5 | 172 / 172 | 53.4 / 53.4 | 41.4 / 33.1 / 38.7 |
| NMOS, 0.3 V underdrive|4 K proxy | 29.6 / 29.6 | 135 / 135 | 42 / 42 | 41.9 / 33.8 / 39.3 |
| NMOS, 0.3 V underdrive|4 K high | 23 / 23 | 109 / 109 | 32.6 / 32.6 | 41.2 / 33.1 / 38.6 |
| NMOS, 0.3 V underdrive|77 K Beall fit | 17 / 17 | 83.8 / 83.8 | 31.3 / 31.3 | 43.6 / 34.4 / 38.6 |
| NMOS, 0.3 V underdrive|4 K, Beall pMOS | 29 / 29 | 132 / 132 | 41.1 / 41.1 | 41.3 / 33.1 / 38.7 |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 120 K) | 92.2 / 92.2 | 510 / 510 | 136 / 136 | 41.5 / 33.1 / 38.8 |
| NMOS, 0.3 V underdrive|4 K, tree, ESD-dominated droop | 31.4 / 31.4 | 132 / 132 | 44 / 44 | 41.3 / 33.1 / 38.7 |
| NMOS, 0.3 V underdrive|4 K, tree, one reticle | 31.4 / 31.4 | 132 / 132 | 44 / 44 | 41.3 / 33.1 / 38.7 |
| bootstrapped (transistor level), 0.3 V underdrive|300 K | 10.6 / 10.6 | 255 / 255 | 73.9 / 73.9 | 42.9 / 34.4 / 32.9 |
| bootstrapped (transistor level), 0.3 V underdrive|77 K proxy | 3.62 / 3.62 | 63.9 / 63.9 | 22.5 / 22.5 | 38.1 / 34.4 / 32.8 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K proxy | 2.64 / 2.64 | 44.9 / 44.9 | 16.9 / 16.9 | 35.8 / 35.1 / 33.6 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K high | 2.59 / 2.59 | 44.5 / 44.5 | 17.1 / 17.1 | 34.5 / 34.3 / 32.8 |
| bootstrapped (transistor level), 0.3 V underdrive|77 K Beall fit | 5.75 / 5.75 | 34.8 / 34.8 | 27.8 / 27.8 | 41.7 / 34.3 / 32.9 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, Beall pMOS | 5.48 / 5.48 | 43 / 43 | 29.2 / 29.2 | 41.2 / 34.3 / 32.9 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 120 K) | 2.01 / 2.01 | 10.6 / 10.6 | 8.08 / 8.08 | 31.3 / 33.9 / 32.5 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, ESD-dominated droop | 2.11 / 2.11 | 31.1 / 31.1 | 13.7 / 13.7 | 32.0 / 34.3 / 32.7 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, one reticle | 2.02 / 2.02 | 30.9 / 30.9 | 13 / 13 | 31.5 / 34.3 / 32.7 |
| T-switch + OTA buffer|300 K | 9.34 / 9.34 | 17.8 / 17.8 | 20.5 / 20.5 | 43.7 / 34.3 / 32.8 |
| T-switch + OTA buffer|77 K proxy | 4.6 / 4.6 | 6.31 / 6.31 | 7.46 / 7.46 | 41.8 / 34.0 / 32.8 |
| T-switch + OTA buffer|4 K proxy | 4.9 / 4.91 | 6.45 / 6.85 | 7.05 / 8.15 | 41.5 / 33.9 / 32.7 |
| T-switch + OTA buffer|4 K high | 5.04 / 5.04 | 7.45 / 7.45 | 8.94 / 8.94 | 42.4 / 34.0 / 32.8 |
| T-switch + OTA buffer|77 K Beall fit | 5.61 / 5.61 | 11.3 / 11.3 | 13.4 / 13.4 | 42.8 / 34.1 / 32.8 |
| T-switch + OTA buffer|4 K, Beall pMOS | 5.68 / 5.68 | 12.6 / 12.6 | 14.9 / 14.9 | 43.0 / 34.1 / 32.8 |
| T-switch + OTA buffer|4 K, steep (T_eff 120 K) | 2.64 / 2.64 | 4.53 / 4.53 | 4.86 / 4.86 | 40.8 / 33.8 / 32.5 |
| T-switch + OTA buffer|4 K, tree, ESD-dominated droop | 5.46 / 5.46 | 6.95 / 6.95 | 8.78 / 8.78 | 43.5 / 34.3 / 32.8 |
| T-switch + OTA buffer|4 K, tree, one reticle | 6.86 / 6.86 | 10.4 / 10.4 | 10.7 / 10.7 | 43.8 / 34.3 / 32.8 |
| TG + dummies|300 K | 6.72 / 6.72 | 6.78 / 6.78 | 13.1 / 13.1 | 43.7 / 34.2 / 32.9 |
| TG + dummies|77 K proxy | 4.92 / 4.92 | 5.91 / 5.91 | 10.8 / 10.8 | 43.5 / 34.1 / 32.8 |
| TG + dummies|4 K proxy | 4.37 / 4.65 | 6.05 / 6.1 | 11 / 11.5 | 42.7 / 34.0 / 32.7 |
| TG + dummies|4 K high | 4.5 / 4.5 | 6.81 / 6.81 | 13.3 / 13.3 | 43.3 / 34.2 / 32.9 |
| TG + dummies|77 K Beall fit | 5.41 / 5.41 | 18.9 / 18.9 | 33.9 / 33.9 | 33.9 / 30.9 / 32.9 |
| TG + dummies|4 K, Beall pMOS | 7.61 / 7.61 | 56.5 / 56.5 | 75.2 / 75.2 | 32.0 / 30.6 / 32.9 |
| TG + dummies|4 K, steep (T_eff 120 K) | 2.75 / 2.75 | 3.19 / 3.19 | 104 / 104 | 42.1 / 33.5 / 32.9 |
| TG + dummies|4 K, tree, ESD-dominated droop | 5.09 / 5.09 | 6.76 / 6.76 | 12.6 / 12.6 | 43.6 / 34.2 / 32.9 |
| TG + dummies|4 K, tree, one reticle | 5.09 / 5.09 | 6.76 / 6.76 | 12.6 / 12.6 | 43.6 / 34.2 / 32.9 |
| TG, no ESD|300 K | 1.05 / 1.05 | 4.24 / 4.24 | 4.35 / 4.35 | 5.5 / 34.4 / 33.7 |
| TG, no ESD|77 K proxy | 1.09 / 1.09 | 7.17 / 7.17 | 5.15 / 5.15 | 7.4 / 33.9 / 31.7 |
| TG, no ESD|4 K proxy | 1.02 / 1.02 | 4.58 / 4.58 | 4.68 / 4.68 | 2.8 / 32.3 / 31.6 |
| TG, no ESD|4 K high | 0.983 / 0.983 | 3.39 / 3.39 | 3.99 / 3.99 | 0.0 / 31.6 / 32.1 |
| TG, no ESD|77 K Beall fit | 2.02 / 2.02 | 19.1 / 19.1 | 11.5 / 11.5 | 26.3 / 30.9 / 32.6 |
| TG, no ESD|4 K, Beall pMOS | 2.04 / 2.04 | 27.4 / 27.4 | 26.1 / 26.1 | 28.9 / 30.6 / 32.8 |
| TG, no ESD|4 K, steep (T_eff 120 K) | 1.13 / 1.13 | 4.72 / 4.72 | 28 / 28 | 13.6 / 33.7 / 32.8 |
| TG, no ESD|4 K, tree, ESD-dominated droop | 1.02 / 1.02 | 5.63 / 5.63 | 5 / 5 | 3.3 / 32.8 / 31.7 |
| TG, no ESD|4 K, tree, one reticle | 1.02 / 1.02 | 5.63 / 5.63 | 5 / 5 | 3.3 / 32.8 / 31.7 |
| TG, ESD on the node|300 K | 1.1 / 1.1 | 4.47 / 4.47 | 4.58 / 4.58 | 7.8 / 32.1 / 31.4 |
| TG, ESD on the node|77 K proxy | 1.23 / 1.23 | 8.46 / 8.46 | 5.84 / 5.84 | 13.7 / 34.1 / 31.9 |
| TG, ESD on the node|4 K proxy | 1.16 / 1.16 | 5.35 / 5.35 | 5.36 / 5.36 | 10.5 / 32.8 / 31.8 |
| TG, ESD on the node|4 K high | 1.21 / 1.21 | 3.58 / 3.58 | 7.56 / 7.56 | 13.6 / 31.0 / 32.3 |
| TG, ESD on the node|77 K Beall fit | 10.7 / 10.7 | 43.4 / 43.4 | 13.8 / 13.8 | 35.2 / 30.8 / 32.7 |
| TG, ESD on the node|4 K, Beall pMOS | 34.4 / 34.4 | 1e+04 / 1e+04 | 34.4 / 34.4 | 32.9 / 29.6 / 32.9 |
| TG, ESD on the node|4 K, steep (T_eff 120 K) | 1.26 / 1.26 | 5.34 / 5.34 | 30.7 / 30.7 | 17.7 / 33.8 / 32.8 |
| TG, ESD on the node|4 K, tree, ESD-dominated droop | 1.16 / 1.16 | 6.59 / 6.59 | 5.71 / 5.71 | 11.0 / 33.2 / 31.9 |
| TG, ESD on the node|4 K, tree, one reticle | 1.16 / 1.16 | 6.59 / 6.59 | 5.71 / 5.71 | 11.0 / 33.2 / 31.9 |
| GF180 NMOS, 0.3 V underdrive|300 K | 541 / 541 | 1e+04 / 1e+04 | 1.33e+03 / 1.33e+03 | 44.1 / 34.4 / 38.8 |
| GF180 NMOS, 0.3 V underdrive|4 K proxy | 661 / 661 | 1e+04 / 1e+04 | 1.59e+03 / 1.59e+03 | 44.1 / 34.4 / 38.8 |
| GF180 NMOS, 0.3 V underdrive|4 K high | 620 / 620 | 1e+04 / 1e+04 | 1.48e+03 / 1.48e+03 | 44.1 / 34.4 / 38.8 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|300 K | 34.6 / 34.6 | 194 / 194 | 143 / 143 | 43.9 / 34.4 / 32.9 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|4 K proxy | 13.5 / 13.5 | 80 / 80 | 58.4 / 58.4 | 43.2 / 34.4 / 32.9 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|4 K high | 13.9 / 13.9 | 81.6 / 81.6 | 60.1 / 60.1 | 43.2 / 34.4 / 32.9 |
| GF180 TG + dummies|300 K | 5.39 / 5.39 | 6.58 / 6.58 | 9.19 / 9.19 | 43.6 / 34.1 / 32.8 |
| GF180 TG + dummies|4 K proxy | 5.15 / 5.15 | 6.68 / 6.68 | 8.81 / 8.81 | 43.6 / 34.3 / 32.8 |
| GF180 TG + dummies|4 K high | 5.49 / 5.49 | 7.74 / 7.74 | 9.57 / 9.57 | 43.6 / 34.3 / 32.8 |
| GF180 TG, no ESD|300 K | 0.586 / 0.586 | 2.26 / 2.26 | 2.2 / 2.2 | 0.0 / 28.0 / 28.5 |
| GF180 TG, no ESD|4 K proxy | 0.62 / 0.62 | 1.94 / 1.94 | 2.24 / 2.24 | 0.0 / 25.9 / 28.6 |
| GF180 TG, no ESD|4 K high | 0.66 / 0.66 | 2.13 / 2.13 | 2.33 / 2.33 | 0.0 / 25.1 / 28.9 |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|300 K | 118 / 118 | 2.61e+03 / 2.61e+03 | 735 / 735 | 44.0 / 34.4 / 32.9 |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|4 K proxy | 122 / 122 | 1.38e+03 / 1.38e+03 | 652 / 652 | 44.0 / 34.4 / 32.9 |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|4 K high | 112 / 112 | 1.22e+03 / 1.22e+03 | 595 / 595 | 44.0 / 34.4 / 32.9 |
| GF180 TG, no ESD, W 0.42|300 K | 1.41 / 1.41 | 5.76 / 5.76 | 5.47 / 5.47 | 17.7 / 33.0 / 31.8 |
| GF180 TG, no ESD, W 0.42|4 K proxy | 1.45 / 1.45 | 4.57 / 4.57 | 5.03 / 5.03 | 19.6 / 31.8 / 31.6 |
| GF180 TG, no ESD, W 0.42|4 K high | 1.52 / 1.52 | 4.73 / 4.73 | 5.57 / 5.57 | 21.5 / 31.6 / 31.9 |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 30 K) | 154 / 154 | 2.11e+03 / 2.11e+03 | 242 / 242 | 41.5 / 33.1 / 38.8 |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 20 K) | 297 / 297 | 4.92e+03 / 4.92e+03 | 297 / 297 | 38.8 / 31.9 / 38.8 |
| NMOS, 0.3 V underdrive|4 K, mismatch x 1.5 | 27.1 / 27.1 | 124 / 124 | 38.5 / 38.5 | 41.3 / 33.1 / 38.7 |
| NMOS, 0.3 V underdrive|4 K, mismatch x 2 | 61.8 / 61.8 | 301 / 301 | 61.8 / 61.8 | 38.7 / 31.9 / 38.7 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 30 K) | 1.23 / 1.23 | 6.28 / 6.28 | 5.13 / 5.13 | 15.6 / 33.8 / 32.4 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 20 K) | 1.19 / 1.19 | 4.09 / 4.09 | 4.79 / 4.79 | 16.3 / 34.0 / 32.7 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 1.5 | 2.41 / 2.41 | 39 / 39 | 15.6 / 15.6 | 34.7 / 34.4 / 32.8 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 2 | 2.19 / 2.19 | 34.4 / 34.4 | 14.4 / 14.4 | 34.1 / 34.4 / 32.8 |
| TG + dummies|4 K, steep (T_eff 30 K) | 2.46 / 2.46 | 2.82 / 2.82 | 443 / 443 | 41.9 / 33.4 / 32.9 |
| TG + dummies|4 K, steep (T_eff 20 K) | 2.44 / 2.44 | 2.79 / 2.79 | 456 / 456 | 41.9 / 33.4 / 32.9 |
| TG + dummies|4 K, mismatch x 1.5 | 3.37 / 3.37 | 4.54 / 4.54 | 8.52 / 8.52 | 42.8 / 34.0 / 32.8 |
| TG + dummies|4 K, mismatch x 2 | 2.6 / 2.6 | 3.65 / 3.65 | 6.82 / 6.82 | 41.7 / 33.8 / 32.8 |
| TG, no ESD|4 K, mismatch x 1.5 | 0.984 / 0.984 | 4.47 / 4.47 | 4.58 / 4.58 | 0.0 / 32.3 / 31.6 |
| TG, no ESD|4 K, mismatch x 2 | 0.961 / 0.961 | 3.97 / 3.97 | 4.35 / 4.35 | 0.0 / 32.2 / 31.6 |

Smallest over conditions (SKY130 Figure-6 conditions incl. trees, steep bands, mismatch; GF180 separate):

- SKY130 line: smallest margin 0.961 (TG, no ESD|4 K, mismatch x 2); largest std/all factor 1.065; smallest sigma_req among passing 2.8 uV = 0.025 b_eq (TG, no ESD|4 K proxy)
- SKY130 quadratic: smallest margin 2.79 (TG + dummies|4 K, steep (T_eff 20 K)); largest std/all factor 1.062; smallest sigma_req among passing 29.6 uV = 0.266 b_eq (TG, ESD on the node|4 K, Beall pMOS)
- SKY130 window: smallest margin 3.99 (TG, no ESD|4 K high); largest std/all factor 1.156; smallest sigma_req among passing 31.4 uV = 0.282 b_eq (TG, ESD on the node|300 K)
- GF180 line: smallest margin 0.586 (GF180 TG, no ESD|300 K); largest std/all factor 1.000; smallest sigma_req among passing 17.7 uV = 0.159 b_eq (GF180 TG, no ESD, W 0.42|300 K)
- GF180 quadratic: smallest margin 1.94 (GF180 TG, no ESD|4 K proxy); largest std/all factor 1.000; smallest sigma_req among passing 25.1 uV = 0.225 b_eq (GF180 TG, no ESD|4 K high)
- GF180 window: smallest margin 2.2 (GF180 TG, no ESD|300 K); largest std/all factor 1.000; smallest sigma_req among passing 28.5 uV = 0.256 b_eq (GF180 TG, no ESD|300 K)

## B. Switches sized for settling (nominal, 20 mV grid)

| key | tau (ns) | between-point factor line / quad / window | spline/chord 20 mV | 99.99: open line / quad / window | 50 mV line / quad | 1 mV chord / spline | 99.9: 50 mV line / quad |
|---|---|---|---|---|---|---|---|
| TG|5|300 K | 1.52 | 1.000 / 1.190 / 1.011 | 1.005 | 0.217 / 0.884 / 1.02 | 1.05 / 2.07 | 41.6 / 41.4 | 3.28 / 6.5 |
| TG|5|4 K proxy | 1.52 | 1.000 / 1.130 / 1.000 | 1.004 | 0.234 / 1.02 / 1.08 | 1.06 / 2.64 | 42.1 / 41.9 | 3.32 / 8.26 |
| TG|10|300 K | 0.797 | 1.000 / 1.151 / 1.000 | 1.008 | 0.107 / 0.446 / 0.542 | 0.489 / 0.977 | 19.4 / 19.2 | 1.53 / 3.06 |
| TG|10|4 K proxy | 0.797 | 1.000 / 1.042 / 1.000 | 1.001 | 0.115 / 0.499 / 0.497 | 0.531 / 1.55 | 21.2 / 21.2 | 1.66 / 4.86 |
| TG|20|300 K | 0.436 | 1.000 / 1.104 / 1.000 | 1.011 | 0.0513 / 0.21 / 0.284 | 0.221 / 0.422 | 8.72 / 8.63 | 0.692 / 1.32 |
| TG|20|4 K proxy | 0.436 | 1.000 / 1.000 / 1.000 | 1.002 | 0.0567 / 0.241 / 0.225 | 0.268 / 0.8 | 10.7 / 10.7 | 0.84 / 2.51 |
| TG|40|300 K | 0.259 | 1.000 / 1.068 / 1.009 | 1.010 | 0.0246 / 0.0908 / 0.133 | 0.101 / 0.172 | 3.98 / 3.94 | 0.316 / 0.54 |
| TG|40|4 K proxy | 0.259 | 1.000 / 1.000 / 1.000 | 1.003 | 0.0289 / 0.12 / 0.103 | 0.135 / 0.386 | 5.4 / 5.39 | 0.424 / 1.21 |
| TG + dummies|5|300 K | 1.53 | 1.069 / 1.056 / 1.078 | 1.008 | 5.18 / 5.91 / 8.24 | 14.4 / 14.4 | 574 / 569 | 45.1 / 45.1 |
| TG + dummies|5|4 K proxy | 1.53 | 1.036 / 1.021 / 1.007 | 1.002 | 2.79 / 4.02 / 6.12 | 12.3 / 14.8 | 491 / 491 | 38.5 / 46.5 |
| TG + dummies|10|300 K | 0.809 | 1.282 / 1.164 / 1.080 | 1.004 | 1.79 / 2.03 / 2.83 | 4.92 / 4.94 | 195 / 194 | 15.4 / 15.5 |
| TG + dummies|10|4 K proxy | 0.809 | 1.070 / 1.056 / 1.032 | 1.001 | 1.02 / 1.31 / 1.98 | 4.4 / 4.94 | 175 / 175 | 13.8 / 15.5 |
| TG + dummies|20|300 K | 0.45 | 1.382 / 1.385 / 1.014 | 1.048 | 0.739 / 0.737 / 0.99 | 1.82 / 1.82 | 70.4 / 67.1 | 5.7 / 5.7 |
| TG + dummies|20|4 K proxy | 0.45 | 1.161 / 1.160 / 1.094 | 1.006 | 0.434 / 0.489 / 0.742 | 1.64 / 1.75 | 64.3 / 63.9 | 5.13 / 5.49 |
| TG + dummies|40|300 K | 0.275 | 1.015 / 1.002 / 1.000 | 1.034 | 0.309 / 0.313 / 0.338 | 0.581 / 0.626 | 22.4 / 21.7 | 1.82 / 1.96 |
| TG + dummies|40|4 K proxy | 0.275 | 1.260 / 1.229 / 1.023 | 1.006 | 0.214 / 0.216 / 0.322 | 0.657 / 0.66 | 26.1 / 25.9 | 2.06 / 2.07 |
| bootstrapped|5|300 K | 0.223 | 1.000 / 1.145 / 1.014 | 1.030 | 9.95 / 30.3 / 33.8 | 29.3 / 57.8 | 1.14e+03 / 1.1e+03 | 91.9 / 181 |
| bootstrapped|5|4 K proxy | 0.223 | 1.000 / 1.002 / 1.006 | 1.020 | 3.1 / 30.7 / 15.2 | 11.1 / 47.6 | 435 / 426 | 34.8 / 149 |
| bootstrapped|10|300 K | 0.128 | 1.000 / 1.125 / 1.062 | 1.034 | 4.95 / 8.84 / 11.4 | 11.6 / 16.4 | 450 / 435 | 36.5 / 51.4 |
| bootstrapped|10|4 K proxy | 0.128 | 1.000 / 1.024 / 1.023 | 1.031 | 2.68 / 6.71 / 6.86 | 6.51 / 10.5 | 251 / 243 | 20.4 / 33.1 |
| bootstrapped|20|300 K | 0.0959 | 1.000 / 1.143 / 1.051 | 1.035 | 1.51 / 2.84 / 3.69 | 3.69 / 5.37 | 142 / 138 | 11.6 / 16.8 |
| bootstrapped|20|4 K proxy | 0.0959 | 1.000 / 1.056 / 1.089 | 1.040 | 1.36 / 1.92 / 2.3 | 2.62 / 3.23 | 101 / 96.6 | 8.22 / 10.1 |
| bootstrapped|40|300 K | 0.0876 | 1.000 / 1.128 / 1.000 | 1.027 | 0.414 / 1.18 / 1.36 | 1.2 / 2.27 | 46.8 / 45.6 | 3.78 / 7.11 |
| bootstrapped|40|4 K proxy | 0.0876 | 1.000 / 1.108 / 1.004 | 1.035 | 0.41 / 0.715 / 0.926 | 0.952 / 1.34 | 36.7 / 35.5 | 2.98 / 4.21 |
| NMOS|5|300 K | 0.339 | 1.000 / 1.445 / 1.078 | 1.085 | 4.1 / 7.57 / 4.57 | 5.56 / 10.6 | 205 / 189 | 17.4 / 33.1 |
| NMOS|5|4 K proxy | 0.339 | 1.011 / 1.259 / 1.026 | 1.055 | 1.6 / 4.21 / 1.96 | 2.54 / 6.54 | 95.9 / 90.9 | 7.95 / 20.5 |
| NMOS|10|300 K | 0.195 | 1.114 / 1.454 / 1.166 | 1.069 | 2.1 / 2.51 / 2.11 | 2.7 / 3.5 | 98.9 / 92.5 | 8.45 / 11 |
| NMOS|10|4 K proxy | 0.195 | 1.000 / 1.244 / 1.042 | 1.051 | 0.726 / 1.44 / 0.822 | 1.13 / 2.33 | 42.7 / 40.7 | 3.53 / 7.31 |
| NMOS|20|300 K | 0.125 | 1.005 / 1.568 / 1.020 | 1.033 | 0.872 / 0.868 / 0.902 | 1.36 / 1.2 | 51.5 / 49.8 | 4.26 / 3.77 |
| NMOS|20|4 K proxy | 0.125 | 1.055 / 1.327 / 1.110 | 1.054 | 0.35 / 0.483 / 0.36 | 0.525 / 0.794 | 19.9 / 18.8 | 1.65 / 2.49 |
| NMOS|40|300 K | 0.0888 | 1.028 / 1.626 / 1.001 | 1.036 | 0.214 / 0.382 / 0.266 | 0.377 / 0.487 | 14.4 / 13.9 | 1.18 / 1.53 |
| NMOS|40|4 K proxy | 0.0888 | 1.353 / 1.473 / 1.289 | 1.058 | 0.172 / 0.181 / 0.171 | 0.266 / 0.29 | 9.98 / 9.43 | 0.835 / 0.909 |

Shortest node time constant (ns), largest over 300 K and the 4 K band:

| arch | 99.99|open_line | 99.99|open_quadratic | 99.99|open_window | 99.99|move50_line | 99.99|move50_quadratic | 99.9|open_line | 99.9|open_quadratic | 99.9|open_window | 99.9|move50_line | 99.9|move50_quadratic |
|---|---|---|---|---|---|---|---|---|---|---|
| TG | 6.09 | 1.71 | 1.49 | 1.46 | 0.812 | 2.15 | 0.609 | 0.569 | 0.577 | 0.371 |
| TG + dummies | 0.8 | 0.69 | 0.538 | 0.347 | 0.341 | 0.363 | 0.347 | 0.273 | 0.212 | 0.201 |
| bootstrapped | 0.0937 | 0.0903 | 0.0882 | 0.088 | 0.0849 | 0.086 | 0.0813 | 0.0787 | 0.0794 | 0.0755 |
| NMOS | 0.244 | 0.168 | 0.221 | 0.182 | 0.137 | 0.119 | 0.108 | 0.118 | 0.0971 | 0.0916 |

## C. GF180 1 mV moves (strictest point, closed form, slope ratio applied)

- GF180 NMOS, 0.3 V underdrive|300 K: 1e+04 (spacing 0.1 V, ratio 1.617)
- GF180 NMOS, 0.3 V underdrive|4 K proxy: 1e+04 (spacing 0.1 V, ratio 1.617)
- GF180 NMOS, 0.3 V underdrive|4 K high: 1e+04 (spacing 0.1 V, ratio 1.617)
- GF180 bootstrapped (transistor level), 0.3 V underdrive|300 K: 1.83e+03 (spacing 0.2 V, ratio 3.222)
- GF180 bootstrapped (transistor level), 0.3 V underdrive|4 K proxy: 718 (spacing 0.2 V, ratio 3.222)
- GF180 bootstrapped (transistor level), 0.3 V underdrive|4 K high: 738 (spacing 0.2 V, ratio 3.222)
- GF180 TG + dummies|300 K: 218 (spacing 0.2 V, ratio 3.222)
- GF180 TG + dummies|4 K proxy: 230 (spacing 0.2 V, ratio 3.222)
- GF180 TG + dummies|4 K high: 206 (spacing 0.2 V, ratio 3.222)
- GF180 TG, no ESD|300 K: 36.1 (spacing 0.2 V, ratio 3.222)
- GF180 TG, no ESD|4 K proxy: 32.8 (spacing 0.2 V, ratio 3.222)
- GF180 TG, no ESD|4 K high: 32.9 (spacing 0.2 V, ratio 3.222)
- GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|300 K: 7.04e+03 (spacing 0.2 V, ratio 3.222)
- GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|4 K proxy: 6.94e+03 (spacing 0.2 V, ratio 3.222)
- GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|4 K high: 6.38e+03 (spacing 0.2 V, ratio 3.222)
- GF180 TG, no ESD, W 0.42|300 K: 88.5 (spacing 0.2 V, ratio 3.222)
- GF180 TG, no ESD, W 0.42|4 K proxy: 79.4 (spacing 0.2 V, ratio 3.222)
- GF180 TG, no ESD, W 0.42|4 K high: 79.3 (spacing 0.2 V, ratio 3.222)

## C2. SKY130 Figure-6 designs, 1 mV moves, same method

- NMOS, 0.3 V underdrive|300 K: 1.48e+03 (spacing 0.1 V, ratio 1.617)
- NMOS, 0.3 V underdrive|77 K proxy: 1.67e+03 (spacing 0.1 V, ratio 1.617)
- NMOS, 0.3 V underdrive|4 K proxy: 1.32e+03 (spacing 0.1 V, ratio 1.617)
- NMOS, 0.3 V underdrive|4 K high: 1.03e+03 (spacing 0.1 V, ratio 1.617)
- NMOS, 0.3 V underdrive|77 K Beall fit: 876 (spacing 0.1 V, ratio 1.617)
- NMOS, 0.3 V underdrive|4 K, Beall pMOS: 1.29e+03 (spacing 0.1 V, ratio 1.617)
- NMOS, 0.3 V underdrive|4 K, steep (T_eff 120 K): 4.2e+03 (spacing 0.1 V, ratio 1.617)
- NMOS, 0.3 V underdrive|4 K, tree, ESD-dominated droop: 1.38e+03 (spacing 0.1 V, ratio 1.617)
- NMOS, 0.3 V underdrive|4 K, tree, one reticle: 1.38e+03 (spacing 0.1 V, ratio 1.617)
- bootstrapped (transistor level), 0.3 V underdrive|300 K: 646 (spacing 0.2 V, ratio 3.222)
- bootstrapped (transistor level), 0.3 V underdrive|77 K proxy: 214 (spacing 0.2 V, ratio 3.222)
- bootstrapped (transistor level), 0.3 V underdrive|4 K proxy: 156 (spacing 0.2 V, ratio 3.222)
- bootstrapped (transistor level), 0.3 V underdrive|4 K high: 155 (spacing 0.2 V, ratio 3.222)
- bootstrapped (transistor level), 0.3 V underdrive|77 K Beall fit: 313 (spacing 0.2 V, ratio 3.222)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, Beall pMOS: 307 (spacing 0.2 V, ratio 3.222)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 120 K): 105 (spacing 0.2 V, ratio 3.222)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, ESD-dominated droop: 125 (spacing 0.2 V, ratio 3.222)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, one reticle: 121 (spacing 0.2 V, ratio 3.222)
- T-switch + OTA buffer|300 K: 398 (spacing 0.2 V, ratio 3.222)
- T-switch + OTA buffer|77 K proxy: 189 (spacing 0.2 V, ratio 3.222)
- T-switch + OTA buffer|4 K proxy: 207 (spacing 0.2 V, ratio 3.222)
- T-switch + OTA buffer|4 K high: 222 (spacing 0.2 V, ratio 3.222)
- T-switch + OTA buffer|77 K Beall fit: 270 (spacing 0.2 V, ratio 3.222)
- T-switch + OTA buffer|4 K, Beall pMOS: 277 (spacing 0.2 V, ratio 3.222)
- T-switch + OTA buffer|4 K, steep (T_eff 120 K): 104 (spacing 0.2 V, ratio 3.222)
- T-switch + OTA buffer|4 K, tree, ESD-dominated droop: 273 (spacing 0.2 V, ratio 3.222)
- T-switch + OTA buffer|4 K, tree, one reticle: 371 (spacing 0.2 V, ratio 3.222)
- TG + dummies|300 K: 286 (spacing 0.2 V, ratio 3.222)
- TG + dummies|77 K proxy: 252 (spacing 0.2 V, ratio 3.222)
- TG + dummies|4 K proxy: 246 (spacing 0.2 V, ratio 3.222)
- TG + dummies|4 K high: 246 (spacing 0.2 V, ratio 3.222)
- TG + dummies|77 K Beall fit: 507 (spacing 0.2 V, ratio 3.222)
- TG + dummies|4 K, Beall pMOS: 499 (spacing 0.2 V, ratio 3.222)
- TG + dummies|4 K, steep (T_eff 120 K): 198 (spacing 0.2 V, ratio 3.222)
- TG + dummies|4 K, tree, ESD-dominated droop: 274 (spacing 0.2 V, ratio 3.222)
- TG + dummies|4 K, tree, one reticle: 274 (spacing 0.2 V, ratio 3.222)
- TG, no ESD|300 K: 63.5 (spacing 0.2 V, ratio 3.222)
- TG, no ESD|77 K proxy: 71 (spacing 0.2 V, ratio 3.222)
- TG, no ESD|4 K proxy: 61.3 (spacing 0.2 V, ratio 3.222)
- TG, no ESD|4 K high: 56.5 (spacing 0.2 V, ratio 3.222)
- TG, no ESD|77 K Beall fit: 139 (spacing 0.2 V, ratio 3.222)
- TG, no ESD|4 K, Beall pMOS: 125 (spacing 0.2 V, ratio 3.222)
- TG, no ESD|4 K, steep (T_eff 120 K): 71.9 (spacing 0.2 V, ratio 3.222)
- TG, no ESD|4 K, tree, ESD-dominated droop: 63.2 (spacing 0.2 V, ratio 3.222)
- TG, no ESD|4 K, tree, one reticle: 63.2 (spacing 0.2 V, ratio 3.222)
- TG, ESD on the node|300 K: 66.1 (spacing 0.2 V, ratio 3.222)
- TG, ESD on the node|77 K proxy: 80.7 (spacing 0.2 V, ratio 3.222)
- TG, ESD on the node|4 K proxy: 69.8 (spacing 0.2 V, ratio 3.222)
- TG, ESD on the node|4 K high: 62.3 (spacing 0.2 V, ratio 3.222)
- TG, ESD on the node|77 K Beall fit: 361 (spacing 0.2 V, ratio 3.222)
- TG, ESD on the node|4 K, Beall pMOS: 1.42e+03 (spacing 0.2 V, ratio 3.222)
- TG, ESD on the node|4 K, steep (T_eff 120 K): 80.6 (spacing 0.2 V, ratio 3.222)
- TG, ESD on the node|4 K, tree, ESD-dominated droop: 72 (spacing 0.2 V, ratio 3.222)
- TG, ESD on the node|4 K, tree, one reticle: 72 (spacing 0.2 V, ratio 3.222)
- NMOS, 0.3 V underdrive|4 K, steep (T_eff 30 K): 7.54e+03 (spacing 0.1 V, ratio 1.617)
- NMOS, 0.3 V underdrive|4 K, steep (T_eff 20 K): 1e+04 (spacing 0.1 V, ratio 1.617)
- NMOS, 0.3 V underdrive|4 K, mismatch x 1.5: 1.21e+03 (spacing 0.1 V, ratio 1.617)
- NMOS, 0.3 V underdrive|4 K, mismatch x 2: 2.31e+03 (spacing 0.1 V, ratio 1.617)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 30 K): 66.4 (spacing 0.2 V, ratio 3.222)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 20 K): 63.9 (spacing 0.2 V, ratio 3.222)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 1.5: 143 (spacing 0.2 V, ratio 3.222)
- bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 2: 131 (spacing 0.2 V, ratio 3.222)
- TG + dummies|4 K, steep (T_eff 30 K): 179 (spacing 0.2 V, ratio 3.222)
- TG + dummies|4 K, steep (T_eff 20 K): 177 (spacing 0.2 V, ratio 3.222)
- TG + dummies|4 K, mismatch x 1.5: 178 (spacing 0.2 V, ratio 3.222)
- TG + dummies|4 K, mismatch x 2: 138 (spacing 0.2 V, ratio 3.222)
- TG, no ESD|4 K, mismatch x 1.5: 59.8 (spacing 0.2 V, ratio 3.222)
- TG, no ESD|4 K, mismatch x 2: 58.3 (spacing 0.2 V, ratio 3.222)

## D. Joint allocation, 1/f budget for daily retuning (device share x 1.328)

- s33.69_t0.0001 dev 0 dac 0: share 0.00206; NMOS 29.7 / 26.7; bootstrapped 2.65 / 2.38; TG + dummies 4.78 / 4.3
- s33.69_t0.0001 dev 0 dac 50: share 0.0907; NMOS 29.7 / 25.3; bootstrapped 2.65 / 2.26; TG + dummies 4.78 / 4.08
- s33.69_t0.0001 dev 0 dac 120: share 0.513; NMOS 29.7 / 17.7; bootstrapped 2.65 / 1.59; TG + dummies 4.78 / 2.86
- s33.69_t0.0001 dev 0 dac 188: share 1.26; NMOS 29.7 / 0; bootstrapped 2.65 / 0; TG + dummies 4.78 / 0
- s33.69_t0.0001 dev 9 dac 0: share 0.0814; NMOS 29.7 / 25.5; bootstrapped 2.65 / 2.28; TG + dummies 4.78 / 4.1
- s33.69_t0.0001 dev 9 dac 50: share 0.17; NMOS 29.7 / 24.1; bootstrapped 2.65 / 2.15; TG + dummies 4.78 / 3.88
- s33.69_t0.0001 dev 9 dac 120: share 0.592; NMOS 29.7 / 16; bootstrapped 2.65 / 1.43; TG + dummies 4.78 / 2.58
- s33.69_t0.0001 dev 9 dac 188: share 1.33; NMOS 29.7 / 0; bootstrapped 2.65 / 0; TG + dummies 4.78 / 0
- s33.69_t0.0001 dev 49 dac 0: share 2.35; NMOS 29.7 / 0; bootstrapped 2.65 / 0; TG + dummies 4.78 / 0
- s33.69_t0.0001 dev 49 dac 50: share 2.44; NMOS 29.7 / 0; bootstrapped 2.65 / 0; TG + dummies 4.78 / 0
- s33.69_t0.0001 dev 49 dac 120: share 2.87; NMOS 29.7 / 0; bootstrapped 2.65 / 0; TG + dummies 4.78 / 0
- s33.69_t0.0001 dev 49 dac 188: share 3.61; NMOS 29.7 / 0; bootstrapped 2.65 / 0; TG + dummies 4.78 / 0
- s10_t0.001 dev 0 dac 0: share 3.08e-05; NMOS 220 / 198; bootstrapped 19.8 / 17.9; TG + dummies 38.9 / 35
- s10_t0.001 dev 0 dac 50: share 0.00136; NMOS 220 / 198; bootstrapped 19.8 / 17.8; TG + dummies 38.9 / 35
- s10_t0.001 dev 0 dac 120: share 0.00767; NMOS 220 / 197; bootstrapped 19.8 / 17.8; TG + dummies 38.9 / 34.8
- s10_t0.001 dev 0 dac 188: share 0.0188; NMOS 220 / 196; bootstrapped 19.8 / 17.7; TG + dummies 38.9 / 34.6
- s10_t0.001 dev 9 dac 0: share 0.0012; NMOS 220 / 198; bootstrapped 19.8 / 17.8; TG + dummies 38.9 / 35
- s10_t0.001 dev 9 dac 50: share 0.00252; NMOS 220 / 198; bootstrapped 19.8 / 17.8; TG + dummies 38.9 / 34.9
- s10_t0.001 dev 9 dac 120: share 0.00883; NMOS 220 / 197; bootstrapped 19.8 / 17.8; TG + dummies 38.9 / 34.8
- s10_t0.001 dev 9 dac 188: share 0.0199; NMOS 220 / 196; bootstrapped 19.8 / 17.7; TG + dummies 38.9 / 34.6
- s10_t0.001 dev 49 dac 0: share 0.0346; NMOS 220 / 194; bootstrapped 19.8 / 17.5; TG + dummies 38.9 / 34.3
- s10_t0.001 dev 49 dac 50: share 0.0359; NMOS 220 / 194; bootstrapped 19.8 / 17.5; TG + dummies 38.9 / 34.3
- s10_t0.001 dev 49 dac 120: share 0.0422; NMOS 220 / 193; bootstrapped 19.8 / 17.4; TG + dummies 38.9 / 34.2
- s10_t0.001 dev 49 dac 188: share 0.0533; NMOS 220 / 192; bootstrapped 19.8 / 17.3; TG + dummies 38.9 / 33.9
- DAC limits (strictest, 9 uV/rtHz): NMOS 159 uV, bootstrapped 140 uV, TG + dummies 152 uV
- Park et al., conventional gates (Si/SiGe) s 7.25 t 0.001: share 9/49 0.000857/0.0248; NMOS 251/59.1/223; bootstrapped 22.6/7.14/20.1; TG + dummies 44.8/6.61/39.7; TG 8.37/5.55/7.43; T-switch + OTA 44.9/3.51/39.8
- Park et al., conventional gates (Si/SiGe) s 7.25 t 0.0001: share 9/49 0.00857/0.248; NMOS 79.5/18.8/61; bootstrapped 7.17/2.27/5.5; TG + dummies 14.2/2.1/10.9; TG 2.65/1.76/2.03; T-switch + OTA 14.2/1.11/10.9
- Park et al., interchanged gates (Si/SiGe) s 16.6 t 0.001: share 9/49 0.00241/0.0696; NMOS 163/35.4/141; bootstrapped 14.6/4.28/12.6; TG + dummies 26.7/3.95/23.1; TG 5.54/3.45/4.79; T-switch + OTA 27.8/2.09/24
- Park et al., interchanged gates (Si/SiGe) s 16.6 t 0.0001: share 9/49 0.0241/0.696; NMOS 51.9/11.3/23.4; bootstrapped 4.64/1.37/2.09; TG + dummies 8.54/1.26/3.85; TG 1.76/1.1/0.796; T-switch + OTA 8.86/0.668/4
- Nickl et al., foundry SiMOS s 33.69 t 0.001: share 9/49 0.00815/0.235; NMOS 92.9/19.3/71.9; bootstrapped 8.26/2.34/6.39; TG + dummies 14.6/2.15/11.3; TG 3.19/1.92/2.47; T-switch + OTA 15.4/1.14/11.9
- Nickl et al., foundry SiMOS s 33.69 t 0.0001: share 9/49 0.0814/2.35; NMOS 29.7/6.18/0; bootstrapped 2.64/0.748/0; TG + dummies 4.66/0.687/0; TG 1.02/0.614/0; T-switch + OTA 4.92/0.364/0

## E. Pair spread without calibration-point error (strictest point)

- NMOS, 0.3 V underdrive|33.69 dec/V, 99.99%|line: none 29.7, slope 0.1, Stark 0.2 21.6, slope 0.1, Stark 0.5 9.36, slope 0.2, Stark 0.5 9.32
- NMOS, 0.3 V underdrive|33.69 dec/V, 99.99%|quadratic: none 135, slope 0.1, Stark 0.2 98.8, slope 0.1, Stark 0.5 42.7, slope 0.2, Stark 0.5 42.6
- bootstrapped (transistor level), 0.3 V underdrive|33.69 dec/V, 99.99%|line: none 2.64, slope 0.1, Stark 0.2 1.99, slope 0.1, Stark 0.5 0.88, slope 0.2, Stark 0.5 0.876
- bootstrapped (transistor level), 0.3 V underdrive|33.69 dec/V, 99.99%|quadratic: none 44.9, slope 0.1, Stark 0.2 34.1, slope 0.1, Stark 0.5 15.1, slope 0.2, Stark 0.5 15
- T-switch + OTA buffer|33.69 dec/V, 99.99%|line: none 4.92, slope 0.1, Stark 0.2 4.18, slope 0.1, Stark 0.5 2.35, slope 0.2, Stark 0.5 2.33
- T-switch + OTA buffer|33.69 dec/V, 99.99%|quadratic: none 6.86, slope 0.1, Stark 0.2 6.06, slope 0.1, Stark 0.5 4.41, slope 0.2, Stark 0.5 4.22
- TG + dummies|33.69 dec/V, 99.99%|line: none 4.66, slope 0.1, Stark 0.2 4.18, slope 0.1, Stark 0.5 3.45, slope 0.2, Stark 0.5 3.1
- TG + dummies|33.69 dec/V, 99.99%|quadratic: none 6.11, slope 0.1, Stark 0.2 5.45, slope 0.1, Stark 0.5 4.36, slope 0.2, Stark 0.5 3.99
- TG, no ESD|33.69 dec/V, 99.99%|line: none 1.02, slope 0.1, Stark 0.2 0.679, slope 0.1, Stark 0.5 0.284, slope 0.2, Stark 0.5 0.284
- TG, no ESD|33.69 dec/V, 99.99%|quadratic: none 4.58, slope 0.1, Stark 0.2 3.68, slope 0.1, Stark 0.5 1.61, slope 0.2, Stark 0.5 1.61
- TG, ESD on the node|33.69 dec/V, 99.99%|line: none 1.16, slope 0.1, Stark 0.2 0.769, slope 0.1, Stark 0.5 0.322, slope 0.2, Stark 0.5 0.322
- TG, ESD on the node|33.69 dec/V, 99.99%|quadratic: none 5.35, slope 0.1, Stark 0.2 4.32, slope 0.1, Stark 0.5 1.9, slope 0.2, Stark 0.5 1.89
