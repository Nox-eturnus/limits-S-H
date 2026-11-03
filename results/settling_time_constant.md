## Shortest node time constant and mismatch of switches sized for settling

| architecture | 50 mV moves, 99.9 %, 33.69: ratio bound / interpolated / interpolated, quadratic | open-loop, 99.99 %, 33.69: same |
|---|---|---|
| TG | 0.82 / 0.577 / 0.371 ns | 10.5 / 6.09 / 1.45 ns |
| TG + dummies | 0.151 / 0.212 / 0.201 ns | 1.02 / 0.759 / 0.654 ns |
| bootstrapped | 0.0293 / 0.0794 / 0.0755 ns | 0.214 / 0.0937 / 0.0896 ns |
| NMOS | 0.132 / 0.108 / 0.107 ns | 0.404 / 0.244 / 0.151 ns |

Quadratic calibration, nominal margins (50 mV move at 99.9 %, 33.69 / open-loop at 99.99 %, 33.69):

| key | tau (ns) | 50 mV move | open-loop |
|---|---|---|---|
| TG|5|300 K | 1.52 | 6.5 | 1.05 |
| TG|5|4 K proxy | 1.52 | 8.26 | 1.16 |
| TG|10|300 K | 0.797 | 3.06 | 0.513 |
| TG|10|4 K proxy | 0.797 | 4.86 | 0.52 |
| TG|20|300 K | 0.436 | 1.32 | 0.232 |
| TG|20|4 K proxy | 0.436 | 2.51 | 0.241 |
| TG|40|300 K | 0.259 | 0.54 | 0.097 |
| TG|40|4 K proxy | 0.259 | 1.21 | 0.12 |
| TG + dummies|5|300 K | 1.53 | 45.1 | 6.24 |
| TG + dummies|5|4 K proxy | 1.53 | 46.5 | 4.1 |
| TG + dummies|10|300 K | 0.809 | 15.5 | 2.36 |
| TG + dummies|10|4 K proxy | 0.809 | 15.5 | 1.38 |
| TG + dummies|20|300 K | 0.45 | 5.7 | 1.02 |
| TG + dummies|20|4 K proxy | 0.45 | 5.49 | 0.566 |
| TG + dummies|40|300 K | 0.275 | 1.96 | 0.314 |
| TG + dummies|40|4 K proxy | 0.275 | 2.07 | 0.266 |
| bootstrapped|5|300 K | 0.223 | 181 | 34.7 |
| bootstrapped|5|4 K proxy | 0.223 | 149 | 30.8 |
| bootstrapped|10|300 K | 0.128 | 51.4 | 9.94 |
| bootstrapped|10|4 K proxy | 0.128 | 33.1 | 6.87 |
| bootstrapped|20|300 K | 0.0959 | 16.8 | 3.24 |
| bootstrapped|20|4 K proxy | 0.0959 | 10.1 | 2.02 |
| bootstrapped|40|300 K | 0.0876 | 7.11 | 1.33 |
| bootstrapped|40|4 K proxy | 0.0876 | 4.21 | 0.792 |
| NMOS|5|300 K | 0.339 | 15.2 | 10.9 |
| NMOS|5|4 K proxy | 0.339 | 15 | 5.3 |
| NMOS|10|300 K | 0.195 | 5.38 | 3.65 |
| NMOS|10|4 K proxy | 0.195 | 5.66 | 1.79 |
| NMOS|20|300 K | 0.125 | 1.65 | 1.36 |
| NMOS|20|4 K proxy | 0.125 | 1.98 | 0.641 |
| NMOS|40|300 K | 0.0888 | 0.536 | 0.621 |
| NMOS|40|4 K proxy | 0.0888 | 0.726 | 0.266 |

Switches of 20 um, 20 channels (mismatch x 2 of the real switch), closed form, tau 9.8 %: with mismatch / nominal

| design | 99.9 %, 33.69: open-loop | 20 mV move | 50 mV move | 99.99 %, 33.69: open-loop | 50 mV move | mismatch sd max (uV) |
|---|---|---|---|---|---|---|
| TG sized for settling, W 20|300 K | 0.143 / 0.146 | 1.2 / 1.25 | 0.609 / 0.63 | 0.0457 / 0.0467 | 0.194 / 0.201 | 28.8 |
| TG sized for settling, W 20|4 K proxy | 0.159 / 0.162 | 1.47 / 1.53 | 0.736 / 0.765 | 0.0509 / 0.0517 | 0.235 / 0.244 | 42.9 |
| NMOS sized for settling, W 20|300 K | 2.29 / 2.5 | 6.85 / 7.35 | 3.62 / 3.88 | 0.731 / 0.799 | 1.15 / 1.24 | 8.48 |
| NMOS sized for settling, W 20|4 K proxy | 0.953 / 1.05 | 2.73 / 2.84 | 1.44 / 1.5 | 0.304 / 0.336 | 0.459 / 0.478 | 13.1 |
