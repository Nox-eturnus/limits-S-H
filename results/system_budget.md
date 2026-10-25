## Electrodes per DAC with the operational budget and a finite DAC settling time

s = 10 dec/V, 99.9 %, 4 K switching models. Untracked single-gate budget 1.373 mV (per gate); operational budget 0.967 mV = frame-tracked, M = 4 repeated gates per QEC round. Best tree over fan-outs and switch widths. DAC power share: 157 µW (Enthoven et al. 2026) / N.

| design | droop | N, untracked, 2 ns | N, operational, 2 ns | 10 ns | 100 ns | 1 µs | flat met2, operational | refresh power / electrode (operational, 2 ns) | DAC power / electrode |
|---|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | ESD-dominated, 3.1 mV/s | 6.8e+05 | 5.3e+05 | 5.3e+05 | 5e+05 | 3.2e+05 | 1.9e+04 | 1e-10 W | 3e-10 W |
| NMOS, 0.3 V underdrive | Darnas et al., 5.5 µV/s | 1.8e+07 | 1.6e+07 | 1.6e+07 | 1.6e+07 | 1.6e+07 | 1.7e+05 | 6.4e-13 W | 9.6e-12 W |
| bootstrapped (transistor level), 0.3 V underdrive | ESD-dominated, 3.1 mV/s | 6.5e+05 | 5e+05 | 5e+05 | 4.7e+05 | 3e+05 | 1.8e+04 | 9.7e-11 W | 3.1e-10 W |
| bootstrapped (transistor level), 0.3 V underdrive | Darnas et al., 5.5 µV/s | 1.7e+07 | 1.6e+07 | 1.6e+07 | 1.6e+07 | 1.6e+07 | 1.6e+05 | 6.6e-13 W | 9.6e-12 W |
| T-switch + OTA buffer | ESD-dominated, 3.1 mV/s | 6.5e+05 | 5.1e+05 | 5.1e+05 | 4.8e+05 | 3.1e+05 | 1.9e+04 | 9.5e-11 W | 3.1e-10 W |
| T-switch + OTA buffer | Darnas et al., 5.5 µV/s | 1.7e+07 | 1.6e+07 | 1.6e+07 | 1.6e+07 | 1.6e+07 | 1.6e+05 | 6.4e-13 W | 9.6e-12 W |
| TG + dummies | ESD-dominated, 3.1 mV/s | 4.6e+05 | 3.5e+05 | 3.5e+05 | 3.4e+05 | 2.6e+05 | 1.7e+04 | 9.5e-11 W | 4.4e-10 W |
| TG + dummies | Darnas et al., 5.5 µV/s | 1.6e+07 | 1.5e+07 | 1.5e+07 | 1.5e+07 | 1.5e+07 | 1.5e+05 | 6.5e-13 W | 1e-11 W |
| TG, no ESD | ESD-dominated, 3.1 mV/s | 4.3e+05 | 3.3e+05 | 3.3e+05 | 3.1e+05 | 2.4e+05 | 1.6e+04 | 1e-10 W | 4.8e-10 W |
| TG, no ESD | Darnas et al., 5.5 µV/s | 1.6e+07 | 1.4e+07 | 1.4e+07 | 1.4e+07 | 1.4e+07 | 1.4e+05 | 7.1e-13 W | 1.1e-11 W |
| TG, ESD on the node | ESD-dominated, 3.1 mV/s | 4.3e+05 | 3.3e+05 | 3.2e+05 | 3.1e+05 | 2.3e+05 | 1.6e+04 | 1e-10 W | 4.8e-10 W |
| TG, ESD on the node | Darnas et al., 5.5 µV/s | 1.6e+07 | 1.4e+07 | 1.4e+07 | 1.4e+07 | 1.4e+07 | 1.4e+05 | 7e-13 W | 1.1e-11 W |

Largest droop rate at which the best tree refreshes a full reticle (1.8e+06 electrodes), operational budget, 2 ns DAC:

- NMOS, 0.3 V underdrive: 316 µV/s
- bootstrapped (transistor level), 0.3 V underdrive: 316 µV/s
- T-switch + OTA buffer: 316 µV/s
- TG + dummies: 178 µV/s
- TG, no ESD: 178 µV/s
- TG, ESD on the node: 178 µV/s
