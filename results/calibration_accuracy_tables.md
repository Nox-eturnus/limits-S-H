## Switches sized for settling (nominal, 20 mV grid, calibrated range; open-loop on every grid voltage; 1 mV from the spline slope)

| TG | 5 | 1.5 | 0.22 / 0.23 | 3.3 / 3.3 | 41 / 42 |
| TG | 10 | 0.8 | 0.11 / 0.12 | 1.5 / 1.7 | 19 / 21 |
| TG | 20 | 0.44 | 0.051 / 0.057 | 0.69 / 0.84 | 8.6 / 11 |
| TG | 40 | 0.26 | 0.025 / 0.029 | 0.32 / 0.42 | 3.9 / 5.4 |
| TG with dummies | 5 | 1.5 | 5.2 / 2.8 | 45 / 39 | 569 / 491 |
| TG with dummies | 10 | 0.81 | 1.8 / 1 | 15 / 14 | 194 / 175 |
| TG with dummies | 20 | 0.45 | 0.74 / 0.43 | 5.7 / 5.1 | 67 / 64 |
| TG with dummies | 40 | 0.27 | 0.31 / 0.21 | 1.8 / 2.1 | 22 / 26 |
| Bootstrapped NMOS | 5 | 0.22 | 10 / 3.1 | 92 / 35 | 1104 / 426 |
| Bootstrapped NMOS | 10 | 0.13 | 4.9 / 2.7 | 37 / 20 | 435 / 243 |
| Bootstrapped NMOS | 20 | 0.096 | 1.5 / 1.4 | 12 / 8.2 | 138 / 97 |
| Bootstrapped NMOS | 40 | 0.088 | 0.41 / 0.41 | 3.8 / 3 | 46 / 35 |
| NMOS, 0.3 V underdrive | 5 | 0.34 | 4.1 / 1.6 | 17 / 7.9 | 189 / 91 |
| NMOS, 0.3 V underdrive | 10 | 0.2 | 2.1 / 0.73 | 8.5 / 3.5 | 93 / 41 |
| NMOS, 0.3 V underdrive | 20 | 0.12 | 0.87 / 0.35 | 4.3 / 1.6 | 50 / 19 |
| NMOS, 0.3 V underdrive | 40 | 0.089 | 0.21 / 0.17 | 1.2 / 0.84 | 14 / 9.4 |

## Shortest node time constant (ns): '<' where every width passes

| Cell | 50 mV re-bias, 99.9% | 50 mV re-bias, 99.99% | open-loop, line | open-loop, quadratic | open-loop, line over 0.4 V |
|---|---|---|---|---|---|
| TG | 0.58 | 1.5 | 6.1 | 1.7 | 1.5 |
| TG with dummies | below 0.27 | 0.35 | 0.8 | 0.69 | 0.54 |
| Bootstrapped NMOS | below 0.088 | 0.088 | 0.094 | 0.09 | 0.088 |
| NMOS, 0.3 V underdrive | 0.097 | 0.18 | 0.24 | 0.17 | 0.22 |

## Point accuracy for a margin of one (uV): line / quadratic / 0.4 V window, smallest over the conditions

| GF180 NMOS, 0.3 V underdrive | 44 / 34 / 39 |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V | 44 / 34 / 33 |
| GF180 TG + dummies | 44 / 34 / 33 |
| GF180 TG, no ESD | – / 25 / 28 |
| GF180 TG, no ESD, W 0.42 | 18 / 32 / 32 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive | 43 / 34 / 33 |
| NMOS, 0.3 V underdrive | 41 / 33 / 39 |
| T-switch + OTA buffer | 41 / 34 / 33 |
| TG + dummies | 32 / 31 / 33 |
| TG, ESD on the node | 8 / 30 / 31 |
| TG, no ESD | – / 31 / 32 |
| bootstrapped (transistor level), 0.3 V underdrive | 31 / 34 / 32 |

## Steep bands and mismatch, smallest quadratic / window margin (all voltages)

- NMOS, 0.3 V underdrive|4 K, steep (T_eff 30 K): line 154, quadratic 2.11e+03, window 242
- NMOS, 0.3 V underdrive|4 K, steep (T_eff 20 K): line 297, quadratic 4.92e+03, window 297
- NMOS, 0.3 V underdrive|4 K, mismatch x 1.5: line 27.1, quadratic 124, window 38.5
- NMOS, 0.3 V underdrive|4 K, mismatch x 2: line 61.8, quadratic 301, window 61.8
- bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 30 K): line 1.23, quadratic 6.28, window 5.13
- bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 20 K): line 1.19, quadratic 4.09, window 4.79
- bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 1.5: line 2.41, quadratic 39, window 15.6
- bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 2: line 2.19, quadratic 34.4, window 14.4
- TG + dummies|4 K, steep (T_eff 30 K): line 2.46, quadratic 2.82, window 443
- TG + dummies|4 K, steep (T_eff 20 K): line 2.44, quadratic 2.79, window 456
- TG + dummies|4 K, mismatch x 1.5: line 3.37, quadratic 4.54, window 8.52
- TG + dummies|4 K, mismatch x 2: line 2.6, quadratic 3.65, window 6.82
- TG, no ESD|4 K, mismatch x 1.5: line 0.984, quadratic 4.47, window 4.58
- TG, no ESD|4 K, mismatch x 2: line 0.961, quadratic 3.97, window 4.35

Largest margin at standard voltages / on every simulated voltage: {'line': 1.065081638661499, 'quadratic': 1.0623419190675016, 'window': 1.1562983968215115}

