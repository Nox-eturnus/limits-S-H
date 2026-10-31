## Settling of the full tree path: Elmore model against SPICE

eps = 136 µV, 1.2 V step, 60 RC segments per line.

| design | droop | best tree | electrodes | lines on the path | model (ns) | SPICE (ns) | SPICE / model |
|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | ESD-dominated on 1 pF, 46.5 mV/s | F4_w100 | 1.3e+05 | 5 | 386.5 | 318.8 | 0.825 |
| NMOS, 0.3 V underdrive | reference, 3.1 mV/s | F4_w100 | 6.8e+05 | 6 | 1146 | 954.5 | 0.833 |
| bootstrapped (transistor level), 0.3 V underdrive | ESD-dominated on 1 pF, 46.5 mV/s | F4_w10 | 1.2e+05 | 5 | 424 | 355.7 | 0.839 |
| bootstrapped (transistor level), 0.3 V underdrive | reference, 3.1 mV/s | F4_w10 | 6.5e+05 | 6 | 1184 | 990.3 | 0.836 |
| T-switch + OTA buffer | ESD-dominated on 1 pF, 46.5 mV/s | F4_w100 | 1.2e+05 | 5 | 411.5 | 340.2 | 0.827 |
| T-switch + OTA buffer | reference, 3.1 mV/s | F4_w10 | 6.5e+05 | 6 | 1186 | 983.4 | 0.829 |
| TG + dummies | ESD-dominated on 1 pF, 46.5 mV/s | F10_w100 | 7.5e+04 | 3 | 530.3 | 436.1 | 0.822 |
| TG + dummies | reference, 3.1 mV/s | F4_w100 | 4.5e+05 | 6 | 1559 | 1320 | 0.846 |
| TG, no ESD | ESD-dominated on 1 pF, 46.5 mV/s | F10_w100 | 7.2e+04 | 3 | 514.5 | 422.8 | 0.822 |
| TG, no ESD | reference, 3.1 mV/s | F10_w100 | 4.3e+05 | 4 | 1525 | 1292 | 0.847 |
| TG, ESD on the node | ESD-dominated on 1 pF, 46.5 mV/s | F10_w100 | 7e+04 | 3 | 514.1 | 422.6 | 0.822 |
| TG, ESD on the node | reference, 3.1 mV/s | F10_w100 | 4.3e+05 | 4 | 1533 | 1297 | 0.846 |
| NMOS, 0.3 V underdrive | Darnas et al., 5.5 µV/s | F10_w10 | 1.8e+06 | 5 | 3165 | 2623 | 0.829 |
| bootstrapped (transistor level), 0.3 V underdrive | Darnas et al., 5.5 µV/s | F10_w10 | 1.8e+06 | 5 | 3318 | 2768 | 0.834 |
| T-switch + OTA buffer | Darnas et al., 5.5 µV/s | F10_w10 | 1.8e+06 | 5 | 3263 | 2709 | 0.830 |
| TG + dummies | Darnas et al., 5.5 µV/s | F4_w10 | 1.8e+06 | 7 | 5135 | 4178 | 0.814 |
| TG, no ESD | Darnas et al., 5.5 µV/s | F4_w10 | 1.8e+06 | 7 | 5131 | 4174 | 0.814 |
| TG, ESD on the node | Darnas et al., 5.5 µV/s | F4_w10 | 1.8e+06 | 7 | 5446 | 4423 | 0.812 |
