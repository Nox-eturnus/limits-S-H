# Supplementary tables with the tail correction

## Table S10

| Cell | Reference | Overlap × 0.7 | Overlap × 1.3 | Junction × 0.7 | Junction × 1.3 |
|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 29.6 / 6.17 | 29.2 / 6.06 | 28.9 / 6.03 | 29 / 6.04 | 29 / 6.04 |
| bootstrapped (transistor level), 0.3 V underdrive | 2.72 / 0.78 | 2.87 / 0.805 | 2.49 / 0.727 | 2.76 / 0.762 | 2.56 / 0.762 |
| TG + dummies | 4.65 / 0.686 | 4.69 / 0.685 | 4.62 / 0.687 | 4.65 / 0.686 | 4.66 / 0.687 |
| TG, no ESD | 1.01 / 0.716 | 1 / 0.714 | 1.01 / 0.717 | 1.01 / 0.716 | 1.01 / 0.716 |

## Table S19

| point | device | DAC | share | NMOS alone / joint | bootstrapped | TG + dummies |
|---|---|---|---|---|---|---|
| s33.69_t0.0001 | 0 | 0 | 0.00206 | 29.7 / 26.7 | 2.65 / 2.38 | 4.78 / 4.3 |
| s33.69_t0.0001 | 0 | 50 | 0.0907 | 29.7 / 25.3 | 2.65 / 2.26 | 4.78 / 4.08 |
| s33.69_t0.0001 | 0 | 120 | 0.513 | 29.7 / 17.7 | 2.65 / 1.59 | 4.78 / 2.86 |
| s33.69_t0.0001 | 0 | 188 | 1.26 | 29.7 / 0 | 2.65 / 0 | 4.78 / 0 |
| s33.69_t0.0001 | 9 | 0 | 0.0618 | 29.7 / 25.8 | 2.65 / 2.3 | 4.78 / 4.15 |
| s33.69_t0.0001 | 9 | 50 | 0.15 | 29.7 / 24.4 | 2.65 / 2.18 | 4.78 / 3.93 |
| s33.69_t0.0001 | 9 | 120 | 0.572 | 29.7 / 16.4 | 2.65 / 1.47 | 4.78 / 2.65 |
| s33.69_t0.0001 | 9 | 188 | 1.32 | 29.7 / 0 | 2.65 / 0 | 4.78 / 0 |
| s33.69_t0.0001 | 49 | 0 | 1.77 | 29.7 / 0 | 2.65 / 0 | 4.78 / 0 |
| s33.69_t0.0001 | 49 | 50 | 1.86 | 29.7 / 0 | 2.65 / 0 | 4.78 / 0 |
| s33.69_t0.0001 | 49 | 120 | 2.28 | 29.7 / 0 | 2.65 / 0 | 4.78 / 0 |
| s33.69_t0.0001 | 49 | 188 | 3.03 | 29.7 / 0 | 2.65 / 0 | 4.78 / 0 |
| s10_t0.001 | 0 | 0 | 3.08e-05 | 220 / 198 | 19.8 / 17.9 | 38.9 / 35 |
| s10_t0.001 | 0 | 50 | 0.00136 | 220 / 198 | 19.8 / 17.8 | 38.9 / 35 |
| s10_t0.001 | 0 | 120 | 0.00767 | 220 / 197 | 19.8 / 17.8 | 38.9 / 34.8 |
| s10_t0.001 | 0 | 188 | 0.0188 | 220 / 196 | 19.8 / 17.7 | 38.9 / 34.6 |
| s10_t0.001 | 9 | 0 | 0.000908 | 220 / 198 | 19.8 / 17.8 | 38.9 / 35 |
| s10_t0.001 | 9 | 50 | 0.00223 | 220 / 198 | 19.8 / 17.8 | 38.9 / 34.9 |
| s10_t0.001 | 9 | 120 | 0.00855 | 220 / 197 | 19.8 / 17.8 | 38.9 / 34.8 |
| s10_t0.001 | 9 | 188 | 0.0197 | 220 / 196 | 19.8 / 17.7 | 38.9 / 34.6 |
| s10_t0.001 | 49 | 0 | 0.026 | 220 / 195 | 19.8 / 17.6 | 38.9 / 34.5 |
| s10_t0.001 | 49 | 50 | 0.0274 | 220 / 195 | 19.8 / 17.6 | 38.9 / 34.5 |
| s10_t0.001 | 49 | 120 | 0.0337 | 220 / 194 | 19.8 / 17.5 | 38.9 / 34.3 |
| s10_t0.001 | 49 | 188 | 0.0448 | 220 / 193 | 19.8 / 17.4 | 38.9 / 34.1 |

Sampled DAC noise at which the joint margin falls to one (strictest point, 9 µV/√Hz device): NMOS 161 µV rms, bootstrapped 142 µV rms, TG + dummies 154 µV rms

## Table S20

| device | s | target | NMOS | bootstrapped | T-switch + OTA | TG + dummies | TG | TG with ESD |
|---|---|---|---|---|---|---|---|---|
| Park et al., conventional gates (Si/SiGe) | 7.25 | 0.001 | 251 / 59.1 / 223 | 22.6 / 7.14 / 20.1 | 44.9 / 3.51 / 40 | 44.8 / 6.61 / 39.9 | 8.37 / 5.55 / 7.45 | 9.49 / 6.32 / 8.45 |
| Park et al., conventional gates (Si/SiGe) | 7.25 | 0.0001 | 79.5 / 18.8 / 63.8 | 7.17 / 2.27 / 5.75 | 14.2 / 1.11 / 11.4 | 14.2 / 2.1 / 11.4 | 2.65 / 1.76 / 2.13 | 3 / 2.01 / 2.41 |
| Park et al., interchanged gates (Si/SiGe) | 16.6 | 0.001 | 163 / 35.4 / 142 | 14.6 / 4.28 / 12.7 | 27.8 / 2.09 / 24.3 | 26.7 / 3.95 / 23.4 | 5.54 / 3.45 / 4.84 | 6.29 / 3.94 / 5.49 |
| Park et al., interchanged gates (Si/SiGe) | 16.6 | 0.0001 | 51.9 / 11.3 / 30.6 | 4.64 / 1.37 / 2.74 | 8.86 / 0.668 / 5.22 | 8.54 / 1.26 / 5.04 | 1.76 / 1.1 / 1.04 | 2 / 1.26 / 1.18 |
| Nickl et al., foundry SiMOS | 33.69 | 0.001 | 92.9 / 19.3 / 75 | 8.26 / 2.34 / 6.66 | 15.4 / 1.14 / 12.4 | 14.6 / 2.15 / 11.7 | 3.19 / 1.92 / 2.58 | 3.62 / 2.19 / 2.92 |
| Nickl et al., foundry SiMOS | 33.69 | 0.0001 | 29.7 / 6.18 / 0 | 2.64 / 0.748 / 0 | 4.92 / 0.364 / 0 | 4.66 / 0.687 / 0 | 1.02 / 0.614 / 0 | 1.16 / 0.7 / 0 |
- target 0.001 (strictest point excluded at 99.99 %), full: lowest 3.19 (TG, Nickl et al., foundry SiMOS)
- target 0.001 (strictest point excluded at 99.99 %), shared: lowest 1.14 (T-switch + OTA, Nickl et al., foundry SiMOS)
- target 0.001 (strictest point excluded at 99.99 %), joint_49: lowest 2.58 (TG, Nickl et al., foundry SiMOS)
- target 0.0001 (strictest point excluded at 99.99 %), full: lowest 1.76 (TG, Park et al., interchanged gates (Si/SiGe))
- target 0.0001 (strictest point excluded at 99.99 %), shared: lowest 0.668 (T-switch + OTA, Park et al., interchanged gates (Si/SiGe))
- target 0.0001 (strictest point excluded at 99.99 %), joint_49: lowest 1.04 (TG, Park et al., interchanged gates (Si/SiGe))

## Table S26

| Cell | SKY130, 4 K | GF180, 300 K | GF180, 4 K | GF180, 4 K, high shift | GF180, 99.9%, 10 dec/V, per channel | GF180, 50 mV moves |
|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive, 0.3 to 0.9 V | 29.7 / 6.24 | 541 / 5.76 | 661 / 5.75 | 620 / 5.74 | 3.92e+03 | 1.08e+03 |  (pass, pass, pass)
| NMOS, 0.3 V underdrive, 0.3 to 1.5 V | – | 118 / 5.63 | 122 / 5.63 | 112 / 5.61 | 819 | 411 |  (pass, pass, pass)
| Bootstrapped NMOS, transistor level | 2.65 / 0.741 | 34.6 / 3.82 | 13.5 / 3.18 | 13.9 / 3.18 | 97.8 | 46.3 |  (pass, pass, pass)
| TG with dummies | 4.78 / 0.683 | 5.4 / 1.47 | 5.15 / 1.51 | 5.55 / 1.52 | 41.9 | 13.2 |  (pass, pass, pass)
| TG, 1 µm | 1.02 / 0.619 | 0.586 / 0.486 | 0.62 / 0.52 | 0.66 / 0.551 | 4.21 | 2.12 |  (fail, fail, fail)
| TG, 0.42 µm | 2.52 / 1.17 | 1.41 / 1.07 | 1.45 / 1.12 | 1.52 / 1.17 | 10.1 | 5.11 |  (pass, pass, pass)

