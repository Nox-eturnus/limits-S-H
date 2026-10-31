## System quantities, s = 10 dec/V, 99.9 %, operational budget 1.361 mV, 4 K switching models

One reticle (26 × 33 mm²) holds 1.77e+06 cells of 1 pF at 22 µm pitch.

| design | droop | flat line N | flat wire (m) / square side (mm) | tree N, 2 ns / 100 ns / 1 µs | capped at reticle | levels, config | refresh / addressing / DAC power per electrode | 10^6 electrodes: cold-stage load / DACs at 4 K |
|---|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | ESD-dominated, 3.1 mV/s | 2.2e+04 | 0.48 / 3.3 | 6.8e+05 / 6.4e+05 / 4.2e+05 | 6.8e+05 | 6, F4_w100 | 7.6e-11 / 1.1e-10 / 2.3e-10 W | 190 µW / 2 × 157 µW = 0.314 mW |
| NMOS, 0.3 V underdrive | Darnas et al., 5.5 µV/s | 1.9e+05 | 4.18 / 9.6 | 1.8e+07 / 1.7e+07 / 1.7e+07 | 1.8e+06 (area) | 6, F10_w10 | 5.5e-13 / 8.3e-13 / 8.9e-11 W | 1.38 µW / 1 × 157 µW = 0.157 mW |
| bootstrapped (transistor level), 0.3 V underdrive | ESD-dominated, 3.1 mV/s | 2.1e+04 | 0.45 / 3.2 | 6.5e+05 / 6.1e+05 / 4e+05 | 6.5e+05 | 6, F4_w10 | 7.2e-11 / 1.1e-10 / 2.4e-10 W | 187 µW / 2 × 157 µW = 0.314 mW |
| bootstrapped (transistor level), 0.3 V underdrive | Darnas et al., 5.5 µV/s | 1.8e+05 | 3.90 / 9.3 | 1.7e+07 / 1.7e+07 / 1.7e+07 | 1.8e+06 (area) | 6, F10_w10 | 5.6e-13 / 8.4e-13 / 8.9e-11 W | 1.4 µW / 1 × 157 µW = 0.157 mW |
| T-switch + OTA buffer | ESD-dominated, 3.1 mV/s | 2.1e+04 | 0.47 / 3.2 | 6.5e+05 / 6.2e+05 / 4.1e+05 | 6.5e+05 | 6, F4_w10 | 7.1e-11 / 1.1e-10 / 2.4e-10 W | 184 µW / 2 × 157 µW = 0.314 mW |
| T-switch + OTA buffer | Darnas et al., 5.5 µV/s | 1.8e+05 | 4.06 / 9.5 | 1.7e+07 / 1.7e+07 / 1.7e+07 | 1.8e+06 (area) | 6, F10_w10 | 5.6e-13 / 8.3e-13 / 8.9e-11 W | 1.38 µW / 1 × 157 µW = 0.157 mW |
| TG + dummies | ESD-dominated, 3.1 mV/s | 1.9e+04 | 0.42 / 3.1 | 4.5e+05 / 4.4e+05 / 3.2e+05 | 4.5e+05 | 6, F4_w100 | 7.4e-11 / 1e-10 / 3.5e-10 W | 176 µW / 3 × 157 µW = 0.471 mW |
| TG + dummies | Darnas et al., 5.5 µV/s | 1.7e+05 | 3.63 / 8.9 | 1.6e+07 / 1.6e+07 / 1.6e+07 | 1.8e+06 (area) | 8, F4_w10 | 4.6e-13 / 4.8e-13 / 8.9e-11 W | 0.938 µW / 1 × 157 µW = 0.157 mW |
| TG, no ESD | ESD-dominated, 3.1 mV/s | 1.9e+04 | 0.41 / 3.0 | 4.3e+05 / 4.2e+05 / 3e+05 | 4.3e+05 | 4, F10_w100 | 7.6e-11 / 1.4e-10 / 3.6e-10 W | 218 µW / 3 × 157 µW = 0.471 mW |
| TG, no ESD | Darnas et al., 5.5 µV/s | 1.6e+05 | 3.54 / 8.8 | 1.6e+07 / 1.6e+07 / 1.6e+07 | 1.8e+06 (area) | 8, F4_w10 | 4.9e-13 / 5.2e-13 / 8.9e-11 W | 1.01 µW / 1 × 157 µW = 0.157 mW |
| TG, ESD on the node | ESD-dominated, 3.1 mV/s | 1.9e+04 | 0.41 / 3.0 | 4.3e+05 / 4.1e+05 / 3e+05 | 4.3e+05 | 4, F10_w100 | 7.5e-11 / 1.4e-10 / 3.7e-10 W | 215 µW / 3 × 157 µW = 0.471 mW |
| TG, ESD on the node | Darnas et al., 5.5 µV/s | 1.6e+05 | 3.55 / 8.8 | 1.6e+07 / 1.6e+07 / 1.6e+07 | 1.8e+06 (area) | 8, F4_w10 | 4.9e-13 / 5.1e-13 / 8.9e-11 W | 1 µW / 1 × 157 µW = 0.157 mW |

Cooling power (Krinner et al. 2019): 4.2 K: 1.5 W, 1.2 K (still): 0.04 W, 140 mK (cold plate): 0.0002 W, 20 mK (mixing chamber): 1.9e-05 W

Largest droop rate at which the best tree refreshes a full reticle:

- NMOS, 0.3 V underdrive: 422 µV/s
- bootstrapped (transistor level), 0.3 V underdrive: 422 µV/s
- T-switch + OTA buffer: 422 µV/s
- TG + dummies: 316 µV/s
- TG, no ESD: 237 µV/s
- TG, ESD on the node: 237 µV/s

### Calibration time for 10^6 channels, 5 measurements per channel (s)

| time per measurement | 1 in parallel | 100 | 10^4 |
|---|---|---|---|
| 3e-06 s | 15 | 0.15 | 0.0015 |
| 0.001 s | 5e+03 | 50 | 0.5 |
| 0.1 s | 5e+05 | 5e+03 | 50 |

### Largest coupling from a toggling select line (2.1 V) to a 1 pF hold node (fF)

- s33.69_t0.0001: 0.0614 fF
- s33.69_t0.001: 0.192 fF
- s10_t0.001: 0.648 fF
- s10_t0.0001: 0.207 fF
