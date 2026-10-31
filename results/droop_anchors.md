## Droop anchors converted to a 1 pF node

van Staveren et al.: 3.1 mV/s on 15 pF = 46.5 fA, i.e. 46.5 mV/s on 1 pF (range 0.9 mV/s to 0.27 V/s). Darnas et al.: 5.5 µV/s on 70 fF + ~1 pF, unchanged. s = 10 dec/V, 99.9 %, 4 K switching models.

Operational budget 1.361 mV, per-gate 1.373 mV; one reticle holds 1.77e+06 cells.

### System rows, operational budget

| design | droop | hold (s) | flat N | flat wire (m) / square (mm) | tree N, 2 ns / 100 ns / 1 µs | levels, config | tree source R / C_leaf | refresh / addressing / DAC per electrode | 10^6 electrodes: cold-stage / DACs at 4 K |
|---|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | ESD-dominated on 1 pF, 46.5 mV/s | 0.0524 | 8.2e+03 | 0.18 / 2.0 | 1.3e+05 / 1.1e+05 / 4.3e+04 | 5, F4_w100 | 13.4 kΩ / 2.53 pF | 7.3e-10 / 1.4e-09 / 1.2e-09 W | 2.09e+03 µW / 8 × 157 µW = 1.26 mW |
| NMOS, 0.3 V underdrive | reference, 3.1 mV/s | 0.786 | 2.2e+04 | 0.48 / 3.3 | 6.8e+05 / 6.4e+05 / 4.2e+05 | 6, F4_w100 | 23.6 kΩ / 2.53 pF | 7.6e-11 / 1.1e-10 / 2.3e-10 W | 190 µW / 2 × 157 µW = 0.314 mW |
| bootstrapped (transistor level), 0.3 V underdrive | ESD-dominated on 1 pF, 46.5 mV/s | 0.0513 | 7.8e+03 | 0.17 / 1.9 | 1.2e+05 / 1e+05 / 4.1e+04 | 5, F4_w10 | 13.7 kΩ / 3.06 pF | 6.8e-10 / 1.3e-09 / 1.3e-09 W | 2.01e+03 µW / 9 × 157 µW = 1.41 mW |
| bootstrapped (transistor level), 0.3 V underdrive | reference, 3.1 mV/s | 0.77 | 2.1e+04 | 0.45 / 3.2 | 6.5e+05 / 6.1e+05 / 4e+05 | 6, F4_w10 | 23.9 kΩ / 3.06 pF | 7.2e-11 / 1.1e-10 / 2.4e-10 W | 187 µW / 2 × 157 µW = 0.314 mW |
| T-switch + OTA buffer | ESD-dominated on 1 pF, 46.5 mV/s | 0.0521 | 8e+03 | 0.18 / 2.0 | 1.2e+05 / 1e+05 / 4.2e+04 | 5, F4_w100 | 13.3 kΩ / 2.75 pF | 7.4e-10 / 1.3e-09 / 1.3e-09 W | 2.05e+03 µW / 9 × 157 µW = 1.41 mW |
| T-switch + OTA buffer | reference, 3.1 mV/s | 0.782 | 2.1e+04 | 0.47 / 3.2 | 6.5e+05 / 6.2e+05 / 4.1e+05 | 6, F4_w10 | 25.6 kΩ / 2.75 pF | 7.1e-11 / 1.1e-10 / 2.4e-10 W | 184 µW / 2 × 157 µW = 0.314 mW |
| TG + dummies | ESD-dominated on 1 pF, 46.5 mV/s | 0.0524 | 7.3e+03 | 0.16 / 1.9 | 7.5e+04 / 6.8e+04 / 3.4e+04 | 3, F10_w100 | 12.5 kΩ / 3.88 pF | 6.8e-10 / 1.4e-09 / 2.1e-09 W | 2.1e+03 µW / 14 × 157 µW = 2.2 mW |
| TG + dummies | reference, 3.1 mV/s | 0.786 | 1.9e+04 | 0.42 / 3.1 | 4.5e+05 / 4.4e+05 / 3.2e+05 | 6, F4_w100 | 23.8 kΩ / 3.88 pF | 7.4e-11 / 1e-10 / 3.5e-10 W | 176 µW / 3 × 157 µW = 0.471 mW |
| TG, no ESD | ESD-dominated on 1 pF, 46.5 mV/s | 0.0485 | 7.1e+03 | 0.16 / 1.9 | 7.2e+04 / 6.5e+04 / 3.2e+04 | 3, F10_w100 | 12.4 kΩ / 3.88 pF | 7.2e-10 / 1.5e-09 / 2.2e-09 W | 2.25e+03 µW / 14 × 157 µW = 2.2 mW |
| TG, no ESD | reference, 3.1 mV/s | 0.728 | 1.9e+04 | 0.41 / 3.0 | 4.3e+05 / 4.2e+05 / 3e+05 | 4, F10_w100 | 22 kΩ / 3.88 pF | 7.6e-11 / 1.4e-10 / 3.6e-10 W | 218 µW / 3 × 157 µW = 0.471 mW |
| TG, ESD on the node | ESD-dominated on 1 pF, 46.5 mV/s | 0.049 | 7.1e+03 | 0.16 / 1.9 | 7e+04 / 6.4e+04 / 3.2e+04 | 3, F10_w100 | 12.4 kΩ / 3.88 pF | 7.1e-10 / 1.5e-09 / 2.3e-09 W | 2.22e+03 µW / 15 × 157 µW = 2.35 mW |
| TG, ESD on the node | reference, 3.1 mV/s | 0.735 | 1.9e+04 | 0.41 / 3.0 | 4.3e+05 / 4.1e+05 / 3e+05 | 4, F10_w100 | 22.2 kΩ / 3.88 pF | 7.5e-11 / 1.4e-10 / 3.7e-10 W | 215 µW / 3 × 157 µW = 0.471 mW |

### SI Table S4 rows, per-gate budget

| design | droop | lumped | R_src 500 ohm | R_src 5 kohm | met2 wire, 0.5 um | met2 wire + R_src 500 ohm | tree, lumped | tree, met2 wire | tree, met2 wire + R_src 500 ohm | one level, w 10 | best tree |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | ESD-dominated on 1 pF, 46.5 mV/s | 5.3e+05 | 1.7e+05 | 4.6e+04 | 8.3e+03 | 8.2e+03 | 2.5e+06 | 1.6e+05 | 1.4e+05 | 7.4e+04 | 1.3e+05 |
| NMOS, 0.3 V underdrive | reference, 3.1 mV/s | 2.2e+06 | 7e+05 | 2.1e+05 | 2.2e+04 | 2.2e+04 | 3.8e+07 | 2.4e+06 | 2.1e+06 | 2.1e+05 | 6.8e+05 |
| bootstrapped (transistor level), 0.3 V underdrive | ESD-dominated on 1 pF, 46.5 mV/s | 3.5e+05 | 1.1e+05 | 3.1e+04 | 7.8e+03 | 7.8e+03 | 4.3e+06 | 1.5e+05 | 1.3e+05 | 7e+04 | 1.2e+05 |
| bootstrapped (transistor level), 0.3 V underdrive | reference, 3.1 mV/s | 1.4e+06 | 4.4e+05 | 1.4e+05 | 2.1e+04 | 2.1e+04 | 6.5e+07 | 2.3e+06 | 2e+06 | 2.1e+05 | 6.5e+05 |
| T-switch + OTA buffer | ESD-dominated on 1 pF, 46.5 mV/s | 4.2e+05 | 1.3e+05 | 3.8e+04 | 8.1e+03 | 8e+03 | 2.4e+06 | 1.5e+05 | 1.3e+05 | 7.2e+04 | 1.2e+05 |
| T-switch + OTA buffer | reference, 3.1 mV/s | 1.7e+06 | 5.5e+05 | 1.7e+05 | 2.1e+04 | 2.1e+04 | 3.6e+07 | 2.3e+06 | 2e+06 | 2.1e+05 | 6.5e+05 |
| TG + dummies | ESD-dominated on 1 pF, 46.5 mV/s | 1.7e+05 | 7e+04 | 2.3e+04 | 7.3e+03 | 7.3e+03 | 3e+05 | 1e+05 | 9.1e+04 | 5.3e+04 | 7.5e+04 |
| TG + dummies | reference, 3.1 mV/s | 9.1e+05 | 3.1e+05 | 9.8e+04 | 1.9e+04 | 1.9e+04 | 4.6e+06 | 1.5e+06 | 1.4e+06 | 1.9e+05 | 4.6e+05 |
| TG, no ESD | ESD-dominated on 1 pF, 46.5 mV/s | 1.7e+05 | 6.8e+04 | 2.2e+04 | 7.1e+03 | 7.1e+03 | 2.9e+05 | 9.5e+04 | 8.5e+04 | 5.1e+04 | 7.2e+04 |
| TG, no ESD | reference, 3.1 mV/s | 8.8e+05 | 3e+05 | 9.4e+04 | 1.9e+04 | 1.9e+04 | 4.3e+06 | 1.4e+06 | 1.3e+06 | 1.8e+05 | 4.3e+05 |
| TG, ESD on the node | ESD-dominated on 1 pF, 46.5 mV/s | 1.6e+05 | 6.7e+04 | 2.2e+04 | 7.1e+03 | 7.1e+03 | 2.5e+05 | 9.1e+04 | 8.3e+04 | 4.9e+04 | 7e+04 |
| TG, ESD on the node | reference, 3.1 mV/s | 8.7e+05 | 3e+05 | 9.5e+04 | 1.9e+04 | 1.9e+04 | 3.8e+06 | 1.4e+06 | 1.2e+06 | 1.8e+05 | 4.3e+05 |
