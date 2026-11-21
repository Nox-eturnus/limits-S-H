# A centred droop with a rate error, the Si-MOS device at 15 MHz, the converter at 15 MHz

## A. Operational budget (mV) for a droop whose rate is in error by eps

| case | s (dec/V) | target | b(0) | centred b(0.03) | centred b(0.1) | centred eps_10 | plain b(0.1) | plain eps_10 |
|---|---|---|---|---|---|---|---|---|
| 100 MHz | 3.87 | 0.001 | 3.52 | 3.26 | 2.58 | 0.040 | 3.07 | 0.080 |
| 100 MHz | 3.87 | 0.0001 | 1.12 | 1.04 | 0.822 | 0.040 | 0.979 | 0.080 |
| 100 MHz | 10 | 0.001 | 1.36 | 1.28 | 1.11 | 0.051 | 1.23 | 0.102 |
| 100 MHz | 10 | 0.0001 | 0.435 | 0.409 | 0.353 | 0.051 | 0.392 | 0.102 |
| 100 MHz | 16.6 | 0.001 | 0.82 | 0.773 | 0.675 | 0.053 | 0.743 | 0.107 |
| 100 MHz | 16.6 | 0.0001 | 0.262 | 0.247 | 0.216 | 0.053 | 0.237 | 0.107 |
| 100 MHz | 33.69 | 0.001 | 0.404 | 0.381 | 0.335 | 0.055 | 0.367 | 0.109 |
| 100 MHz | 33.69 | 0.0001 | 0.129 | 0.122 | 0.107 | 0.055 | 0.117 | 0.109 |
| 15 MHz | 3.87 | 0.001 | 3.52 | 2.15 | 0.81 | 0.011 | 1.49 | 0.021 |
| 15 MHz | 3.87 | 0.0001 | 1.12 | 0.681 | 0.256 | 0.010 | 0.473 | 0.021 |
| 15 MHz | 10 | 0.001 | 1.36 | 1.17 | 0.674 | 0.023 | 0.996 | 0.046 |
| 15 MHz | 10 | 0.0001 | 0.435 | 0.372 | 0.214 | 0.023 | 0.317 | 0.046 |
| 15 MHz | 16.6 | 0.001 | 0.82 | 0.745 | 0.527 | 0.032 | 0.68 | 0.065 |
| 15 MHz | 16.6 | 0.0001 | 0.262 | 0.238 | 0.168 | 0.032 | 0.217 | 0.064 |
| 15 MHz | 33.69 | 0.001 | 0.404 | 0.377 | 0.31 | 0.044 | 0.358 | 0.088 |
| 15 MHz | 33.69 | 0.0001 | 0.129 | 0.121 | 0.0989 | 0.044 | 0.114 | 0.088 |
| 100 MHz, 1 us idle | 10 | 0.001 | 1.24 | 0.708 | 0.258 | 0.010 | 0.482 | 0.019 |
| 100 MHz, 1 us idle | 10 | 0.0001 | 0.396 | 0.224 | 0.0816 | 0.009 | 0.153 | 0.019 |
| 100 MHz, 1 us idle | 33.69 | 0.001 | 0.368 | 0.323 | 0.199 | 0.026 | 0.282 | 0.051 |
| 100 MHz, 1 us idle | 33.69 | 0.0001 | 0.117 | 0.103 | 0.0632 | 0.025 | 0.0897 | 0.051 |

## B. Supplementary Table S22, device of Nickl et al. (33.69 dec/V), 4 K band, closed form with the tail correction: per channel / shared / joint with 49 uV/rtHz

| Zeeman | target | b_eq / b_ind (uV) | 1/f budget, daily (uV/rtHz) | share 9 / 49 | NMOS | bootstrapped | TG + dummies | TG | T-switch + OTA |
|---|---|---|---|---|---|---|---|---|---|
| 100 MHz | 0.001 | 348.9 / 524.7 | 101.3 | 0.008 / 0.23 | 92.9 / 19.3 / 72 | 8.25 / 2.33 / 6.4 | 14.5 / 2.14 / 11.3 | 3.19 / 1.92 / 2.48 | 15.4 / 1.14 / 11.9 |
| 100 MHz | 0.0001 | 111.3 / 168.2 | 32.0 | 0.081 / 2.34 | 29.7 / 6.18 / 0 | 2.64 / 0.748 / 0 | 4.66 / 0.687 / 0 | 1.02 / 0.614 / 0 | 4.92 / 0.364 / 0 |
| 15 MHz | 0.001 | 147.9 / 277.5 | 55.1 | 0.027 / 0.79 | 41.4 / 10.1 / 14.8 | 3.74 / 1.22 / 1.34 | 7.63 / 1.13 / 2.73 | 1.37 / 0.93 / 0.491 | 7.54 / 0.599 / 2.7 |
| 15 MHz | 0.0001 | 46.8 / 88.0 | 17.4 | 0.274 / 7.91 | 13.1 / 3.19 / 0 | 1.18 / 0.385 / 0 | 2.42 / 0.357 / 0 | 0.434 / 0.295 / 0 | 2.39 / 0.19 / 0 |

## C. Converter

- 100|33.69|0.0001: step < 0.336 mV (11.8 bits over 1.2 V); sampled noise, tuned level 160 uV rms; open-loop NMOS 160 uV, bootstrapped 140 uV, TG + dummies 152 uV
- 100|10|0.001: step < 2.75 mV (8.8 bits over 1.2 V)
- 15|33.69|0.0001: step < 0.176 mV (12.7 bits over 1.2 V); sampled noise, tuned level 74 uV rms; open-loop NMOS 73 uV, bootstrapped 0 uV, TG + dummies 60 uV
- 15|10|0.001: step < 0.658 mV (10.8 bits over 1.2 V)

## D. White-noise transitions, 10 dec/V, no Stark shift

- 100 MHz: 65% of the white-noise error; 80% of the transition kernel between 86.5 and 116 MHz, peak 102 MHz
- 15 MHz: 65% of the white-noise error; 80% of the transition kernel between 13 and 17.4 MHz, peak 15.2 MHz
