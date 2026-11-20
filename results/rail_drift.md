# Pedestal sensitivity to the clock and supply rails (4 K band, nominal cells, +-100 mV)

Largest |dP/dV_rail| over the held voltages, in uV of pedestal per mV of rail drift.

| design | node | rail | max (uV/mV) | per held voltage |
|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 1 pF | vdd | 0.317 | -0.32, -0.31, -0.31, -0.3, -0.28 |
| NMOS, 0.3 V underdrive | 1 pF | v_underdrive | 0.104 | -0.1, -0.1, -0.1, -0.1, -0.1 |
| NMOS, 0.3 V underdrive | 70 fF | vdd | 4.13 | -3.8, -4, -4.1, -4.1, -3.9 |
| NMOS, 0.3 V underdrive | 70 fF | v_underdrive | 1.55 | -1.6, -1.5, -1.5, -1.5, -1.5 |
| bootstrapped (transistor level), 0.3 V underdrive | 1 pF | vdd | 1.63 | -0.53, -0.67, -0.81, -0.98, -1.2, -1.4, -1.6 |
| bootstrapped (transistor level), 0.3 V underdrive | 1 pF | vddh | 0.0415 | -0.041, -0.033, -0.023, -0.012, -0.0015, 0.015, 0.041 |
| bootstrapped (transistor level), 0.3 V underdrive | 1 pF | v_underdrive | 0.0731 | -0.065, -0.072, -0.073, -0.062, -0.033, 0.0084, 0.059 |
| bootstrapped (transistor level), 0.3 V underdrive | 70 fF | vdd | 8.51 | -4.6, -4.9, -5.3, -5.9, -6.5, -7.4, -8.5 |
| bootstrapped (transistor level), 0.3 V underdrive | 70 fF | vddh | 0.179 | -0.058, -0.044, -0.015, 0.019, 0.034, 0.08, 0.18 |
| bootstrapped (transistor level), 0.3 V underdrive | 70 fF | v_underdrive | 1.31 | -1, -1.1, -1.2, -1.3, -1.3, -1.3, -1.2 |
| T-switch + OTA buffer | 1 pF | vdd | 0 | 0, 0, 0, 0, 0, 0, 0 |
| T-switch + OTA buffer | 1 pF | vddh | 1.38 | -1.4, -1.4, -1.4, -1.4, -1.4, -1.4, -1.4 |
| T-switch + OTA buffer | 70 fF | vdd | 0 | 0, 0, 0, 0, 0, 0, 0 |
| T-switch + OTA buffer | 70 fF | vddh | 18.4 | -16, -16, -17, -17, -18, -18, -18 |
| TG + dummies | 1 pF | vdd | 0.0204 | -0.02, -0.016, 0.0021, 0.015, 0.0093, 0.0067, 0.0095 |
| TG + dummies | 70 fF | vdd | 2.48 | 2.5, 0.96, 0.19, 0.2, 0.15, 0.36, 1.1 |
| TG, no ESD | 1 pF | vdd | 0.626 | -0.63, -0.61, -0.55, -0.4, -0.29, -0.28, -0.33 |
| TG, no ESD | 70 fF | vdd | 7.45 | -5.3, -7, -7.5, -5.6, -4, -3.7, -3.5 |
| TG, ESD on the node | 1 pF | vdd | 0.543 | -0.54, -0.53, -0.48, -0.35, -0.25, -0.24, -0.27 |
| TG, ESD on the node | 70 fF | vdd | 2.56 | -2.4, -2.6, -2.4, -2.2, -1.3, -1.1, -1.1 |
