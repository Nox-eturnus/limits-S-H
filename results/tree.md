## Electrodes per DAC with the upper tree levels (4 K proxy, tt, s = 10 dec/V, 99.9 %)

Leaf lines of 1000 cells. Upper levels: series switch = cell switch × w, siblings load each line with w × C_off, met2 wire past each child region at the region's side length. 'One level' = one upper line carrying all leaf lines. Best = largest N over fan-outs ['one', 1000, 100, 32, 10, 4] and w [1.0, 10.0, 100.0]. One reticle (26 × 33 mm²) holds 1.8e+06 electrodes at the 22 µm pitch.

| design | droop | flat met2 | tree, leaf line only | tree, one level (w 10) | best tree (config) | levels | refresh energy (pJ) | power per electrode | area at best N (cm²) |
|---|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | ESD-dominated, 3.1 mV/s | 2.2e+04 | 2.4e+06 | 2.1e+05 | 6.8e+05 (F4_w100) | 6 | 60.2 | 7.6e-11 W | 3.29 |
| NMOS, 0.3 V underdrive | Darnas et al., 5.5 µV/s | 1.9e+05 | 1.3e+09 | 1.9e+06 | 1.8e+07 (F10_w10) | 6 | 246 | 5.5e-13 W | 85.5 |
| bootstrapped (transistor level), 0.3 V underdrive | ESD-dominated, 3.1 mV/s | 2.1e+04 | 2.3e+06 | 2.1e+05 | 6.5e+05 (F4_w10) | 6 | 55.6 | 7.2e-11 W | 3.15 |
| bootstrapped (transistor level), 0.3 V underdrive | Darnas et al., 5.5 µV/s | 1.8e+05 | 1.3e+09 | 1.9e+06 | 1.7e+07 (F10_w10) | 6 | 245 | 5.6e-13 W | 83.1 |
| T-switch + OTA buffer | ESD-dominated, 3.1 mV/s | 2.1e+04 | 2.3e+06 | 2.1e+05 | 6.5e+05 (F4_w10) | 6 | 55.4 | 7e-11 W | 3.17 |
| T-switch + OTA buffer | Darnas et al., 5.5 µV/s | 1.9e+05 | 1.3e+09 | 1.9e+06 | 1.7e+07 (F10_w10) | 6 | 245 | 5.5e-13 W | 84.5 |
| TG + dummies | ESD-dominated, 3.1 mV/s | 1.9e+04 | 1.5e+06 | 1.9e+05 | 4.6e+05 (F4_w100) | 6 | 57.9 | 7.3e-11 W | 2.22 |
| TG + dummies | Darnas et al., 5.5 µV/s | 1.7e+05 | 8.6e+08 | 1.8e+06 | 1.6e+07 (F4_w10) | 8 | 202 | 4.5e-13 W | 79.3 |
| TG, no ESD | ESD-dominated, 3.1 mV/s | 1.9e+04 | 1.4e+06 | 1.8e+05 | 4.3e+05 (F10_w100) | 4 | 55.6 | 7.6e-11 W | 2.1 |
| TG, no ESD | Darnas et al., 5.5 µV/s | 1.6e+05 | 8e+08 | 1.8e+06 | 1.6e+07 (F4_w10) | 8 | 202 | 4.9e-13 W | 79.3 |
| TG, ESD on the node | ESD-dominated, 3.1 mV/s | 1.9e+04 | 1.4e+06 | 1.8e+05 | 4.3e+05 (F10_w100) | 4 | 55.5 | 7.5e-11 W | 2.08 |
| TG, ESD on the node | Darnas et al., 5.5 µV/s | 1.6e+05 | 7.7e+08 | 1.8e+06 | 1.6e+07 (F4_w10) | 8 | 202 | 4.8e-13 W | 79.3 |

Largest droop rate at which the best tree still refreshes a full reticle of electrodes (1.8e+06):

- NMOS, 0.3 V underdrive: 501 µV/s
- bootstrapped (transistor level), 0.3 V underdrive: 398 µV/s
- T-switch + OTA buffer: 398 µV/s
- TG + dummies: 316 µV/s
- TG, no ESD: 251 µV/s
- TG, ESD on the node: 251 µV/s
