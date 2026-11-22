# System figures away from the reference operating point

## A. Table S25 at the reference point and the strictest point

| point | droop | design | per DAC | DACs | hold (s) | slot (us) | refresh / addressing per electrode | cold load |
|---|---|---|---|---|---|---|---|---|
| 10|0.001 | 46.5 mV/s | NMOS, 0.3 V underdrive | 1.3e+05 | 8 | 0.0524 | 0.403 | 733 / 1.36e+03 pW | 2.09e+03 uW |
| 10|0.001 | 46.5 mV/s | bootstrapped (transistor level), 0.3 V underdrive | 1.19e+05 | 9 | 0.0513 | 0.431 | 680 / 1.33e+03 pW | 2.01e+03 uW |
| 10|0.001 | 46.5 mV/s | T-switch + OTA buffer | 1.22e+05 | 9 | 0.0521 | 0.428 | 737 / 1.31e+03 pW | 2.05e+03 uW |
| 10|0.001 | 46.5 mV/s | TG + dummies | 7.5e+04 | 14 | 0.0524 | 0.699 | 680 / 1.42e+03 pW | 2.1e+03 uW |
| 10|0.001 | 46.5 mV/s | TG, no ESD | 7.15e+04 | 14 | 0.0485 | 0.679 | 725 / 1.52e+03 pW | 2.25e+03 uW |
| 10|0.001 | 3.1 mV/s | NMOS, 0.3 V underdrive | 6.76e+05 | 2 | 0.786 | 1.16 | 76.5 / 113 pW | 190 uW |
| 10|0.001 | 3.1 mV/s | bootstrapped (transistor level), 0.3 V underdrive | 6.46e+05 | 2 | 0.77 | 1.19 | 72.2 / 115 pW | 187 uW |
| 10|0.001 | 3.1 mV/s | T-switch + OTA buffer | 6.5e+05 | 2 | 0.782 | 1.2 | 70.8 / 113 pW | 184 uW |
| 10|0.001 | 3.1 mV/s | TG + dummies | 4.55e+05 | 3 | 0.786 | 1.73 | 73.6 / 102 pW | 176 uW |
| 10|0.001 | 3.1 mV/s | TG, no ESD | 4.31e+05 | 3 | 0.728 | 1.69 | 76.3 / 141 pW | 218 uW |
| 10|0.001 | 5.5 uV/s | NMOS, 0.3 V underdrive | 1.75e+07 | 1 | 443 | 25.2 | 0.554 / 0.825 pW | 1.38 uW |
| 10|0.001 | 5.5 uV/s | bootstrapped (transistor level), 0.3 V underdrive | 1.71e+07 | 1 | 434 | 25.4 | 0.563 / 0.841 pW | 1.4 uW |
| 10|0.001 | 5.5 uV/s | T-switch + OTA buffer | 1.73e+07 | 1 | 440 | 25.4 | 0.556 / 0.829 pW | 1.38 uW |
| 10|0.001 | 5.5 uV/s | TG + dummies | 1.64e+07 | 1 | 443 | 27 | 0.456 / 0.482 pW | 0.938 uW |
| 10|0.001 | 5.5 uV/s | TG, no ESD | 1.64e+07 | 1 | 410 | 25 | 0.492 / 0.52 pW | 1.01 uW |
| 33.69|0.0001 | 46.5 mV/s | NMOS, 0.3 V underdrive | 2.13e+04 | 47 | 0.00471 | 0.221 | 5.68e+03 / 1.39e+04 pW | 1.96e+04 uW |
| 33.69|0.0001 | 46.5 mV/s | bootstrapped (transistor level), 0.3 V underdrive | 1.6e+04 | 63 | 0.00363 | 0.227 | 6.52e+03 / 1.68e+04 pW | 2.34e+04 uW |
| 33.69|0.0001 | 46.5 mV/s | T-switch + OTA buffer | 1.88e+04 | 54 | 0.00442 | 0.235 | 6.07e+03 / 1.46e+04 pW | 2.07e+04 uW |
| 33.69|0.0001 | 46.5 mV/s | TG + dummies | 1.08e+04 | 93 | 0.00469 | 0.436 | 5.48e+03 / 1.36e+04 pW | 1.91e+04 uW |
| 33.69|0.0001 | 46.5 mV/s | TG, no ESD | 3.22e+03 | 311 | 0.000863 | 0.268 | 2.56e+04 / 6.76e+04 pW | 9.33e+04 uW |
| 33.69|0.0001 | 3.1 mV/s | NMOS, 0.3 V underdrive | 1.37e+05 | 8 | 0.0707 | 0.514 | 548 / 1.01e+03 pW | 1.56e+03 uW |
| 33.69|0.0001 | 3.1 mV/s | bootstrapped (transistor level), 0.3 V underdrive | 1.05e+05 | 10 | 0.0544 | 0.519 | 630 / 1.25e+03 pW | 1.88e+03 uW |
| 33.69|0.0001 | 3.1 mV/s | T-switch + OTA buffer | 1.23e+05 | 9 | 0.0663 | 0.537 | 581 / 1.03e+03 pW | 1.61e+03 uW |
| 33.69|0.0001 | 3.1 mV/s | TG + dummies | 8.1e+04 | 13 | 0.0704 | 0.869 | 517 / 1.13e+03 pW | 1.64e+03 uW |
| 33.69|0.0001 | 3.1 mV/s | TG, no ESD | 2.61e+04 | 39 | 0.0129 | 0.495 | 2.28e+03 / 5.11e+03 pW | 7.39e+03 uW |
| 33.69|0.0001 | 5.5 uV/s | NMOS, 0.3 V underdrive | 4.96e+06 | 1 | 39.8 | 8.03 | 3.15 / 5.44 pW | 8.59 uW |
| 33.69|0.0001 | 5.5 uV/s | bootstrapped (transistor level), 0.3 V underdrive | 4.22e+06 | 1 | 30.7 | 7.27 | 3.84 / 6.71 pW | 10.6 uW |
| 33.69|0.0001 | 5.5 uV/s | T-switch + OTA buffer | 4.74e+06 | 1 | 37.4 | 7.89 | 3.3 / 5.71 pW | 9.02 uW |
| 33.69|0.0001 | 5.5 uV/s | TG + dummies | 4.1e+06 | 1 | 39.7 | 9.69 | 2.78 / 3.4 pW | 6.18 uW |
| 33.69|0.0001 | 5.5 uV/s | TG, no ESD | 1.51e+06 | 1 | 7.3 | 4.84 | 12.2 / 14.1 pW | 26.2 uW |

## B. Table S27: static array at each row's slope (uW, NMOS / bootstrapped / TG with dummies) and stages

- 1000|3.87|0.001: 0.516, 0.519, 0.478
- 1000|3.87|0.0001: 1.13, 1.16, 1.14
- 1000|10|0.001: 1.38, 1.4, 0.938
- 1000|10|0.0001: 2.53, 2.67, 2.48
- 1000|16.6|0.001: 1.53, 1.57, 1.49
- 1000|16.6|0.0001: 3.65, 4.03, 4.6
- 1000|33.69|0.001: 2.69, 2.85, 2.64
- 1000|33.69|0.0001: 8.59, 10.5, 6.17
- 70|3.87|0.001: 3.36, 3.76, 2.32
- 70|3.87|0.0001: 6.67, 9.53, 6.22
- 70|10|0.001: 5.64, 7.68, 5.49
- 70|10|0.0001: 20.4, none, 15.7
- 70|16.6|0.001: 8.91, 21.1, 9.97
- 70|16.6|0.0001: 29.4, none, 29.7
- 70|33.69|0.001: 22, none, 17.1
- 70|33.69|0.0001: 147, none, 172

| node fF / slope | static max (uW) 99.9 / 99.99 % | k=0.5: 1 us / 10 us | k=0.9: 1 us / 10 us | same at 99.99 % | stored-static stages, same order |
|---|---|---|---|---|---|
| 1000|3.87 | 0.519 / 1.16 | 4.2 K / 1.2 K | 1.2 K / 1.2 K | 4.2 K / 1.2 K; 1.2 K / 1.2 K | 4.2 K / 1.2 K; 1.2 K / 1.2 K |
| 1000|10 | 1.4 / 2.67 | 1.2 K / 1.2 K | 1.2 K / 1.2 K | 1.2 K / 1.2 K; 1.2 K / 1.2 K | 1.2 K / 1.2 K; 1.2 K / 1.2 K |
| 1000|16.6 | 1.57 / 4.6 | 1.2 K / 1.2 K | 1.2 K / 140 mK | 1.2 K / 1.2 K; 1.2 K / 140 mK | 1.2 K / 1.2 K; 1.2 K / 140 mK |
| 1000|33.69 | 2.85 / 10.5 | 1.2 K / 1.2 K | 1.2 K / 140 mK | 1.2 K / 1.2 K; 1.2 K / 140 mK | 1.2 K / 1.2 K; 1.2 K / 140 mK |
| 70|3.87 | 3.76 / 9.53 | 1.2 K / 1.2 K | 1.2 K / 1.2 K | 1.2 K / 1.2 K; 1.2 K / 1.2 K | 1.2 K / 1.2 K; 1.2 K / 1.2 K |
| 70|10 | 7.68 / 20.4 | 1.2 K / 1.2 K | 1.2 K / 140 mK | 1.2 K / 1.2 K; 1.2 K / 140 mK | 1.2 K / 1.2 K; 1.2 K / 140 mK |
| 70|16.6 | 21.1 / 29.7 | 1.2 K / 140 mK | 140 mK / 140 mK | 1.2 K / 140 mK; 140 mK / 140 mK | 1.2 K / 140 mK; 140 mK / 20 mK |
| 70|33.69 | 22 / 172 | 1.2 K / 140 mK | 140 mK / 140 mK | 1.2 K / 140 mK; 140 mK / 140 mK | 1.2 K / 140 mK; 140 mK / 20 mK |

## D. Lowest droop held within the untracked budget for equal signs, no tracking, no centring

- 10|0.001|100: b_eq 799.0 uV; NMOS hold 130 s, per DAC 1.05e+07 (reticle); bootstrapped hold 125 s, per DAC 1.02e+07 (reticle); TG + dummies hold 129 s, per DAC 8.94e+06 (reticle)
- 33.69|0.0001|100: b_eq 111.3 uV; NMOS hold 17 s, per DAC 3.32e+06 (reticle); bootstrapped hold 12.5 s, per DAC 2.7e+06 (reticle); TG + dummies hold 17 s, per DAC 2.64e+06 (reticle)
- 33.69|0.0001|15: b_eq 46.8 uV; NMOS hold 6.48 s, per DAC 1.74e+06 (below a reticle); bootstrapped hold 1.9 s, per DAC 9.29e+05 (below a reticle); TG + dummies hold 6.4 s, per DAC 1.28e+06 (below a reticle)
- 33.69|0.001|15: b_eq 147.9 uV; NMOS hold 23 s, per DAC 3.97e+06 (reticle); bootstrapped hold 18.4 s, per DAC 3.45e+06 (reticle); TG + dummies hold 22.9 s, per DAC 3.23e+06 (reticle)

## E. Droop of one hold period at 5.5 uV/s: accuracy needed against the device drift

- 100|3.87|0.001: hold 1.15e+03 s, needed 254.6 uV, drift 23.9-130.1 uV, ratio 0.09-0.51
- 100|3.87|0.0001: hold 368 s, needed 80.8 uV, drift 21.9-119.1 uV, ratio 0.27-1.47
- 100|10|0.001: hold 445 s, needed 125.2 uV, drift 22.2-121.0 uV, ratio 0.18-0.97
- 100|10|0.0001: hold 142 s, needed 39.9 uV, drift 20.0-109.1 uV, ratio 0.50-2.73
- 100|16.6|0.001: hold 268 s, needed 78.8 uV, drift 21.3-115.9 uV, ratio 0.27-1.47
- 100|16.6|0.0001: hold 85.8 s, needed 25.2 uV, drift 19.0-103.4 uV, ratio 0.75-4.11
- 100|33.69|0.001: hold 132 s, needed 39.7 uV, drift 19.9-108.3 uV, ratio 0.50-2.72
- 100|33.69|0.0001: hold 42.3 s, needed 12.7 uV, drift 17.4-94.8 uV, ratio 1.37-7.47
- 15|3.87|0.001: hold 1.15e+03 s, needed 66.9 uV, drift 23.9-130.1 uV, ratio 0.36-1.95
- 15|3.87|0.0001: hold 368 s, needed 21.1 uV, drift 21.9-119.1 uV, ratio 1.04-5.65
- 15|10|0.001: hold 445 s, needed 56.6 uV, drift 22.2-121.0 uV, ratio 0.39-2.14
- 15|10|0.0001: hold 142 s, needed 17.9 uV, drift 20.0-109.1 uV, ratio 1.12-6.10
- 15|16.6|0.001: hold 268 s, needed 47.6 uV, drift 21.3-115.9 uV, ratio 0.45-2.43
- 15|16.6|0.0001: hold 85.8 s, needed 15.1 uV, drift 19.0-103.4 uV, ratio 1.26-6.86
- 15|33.69|0.001: hold 132 s, needed 32.2 uV, drift 19.9-108.3 uV, ratio 0.62-3.37
- 15|33.69|0.0001: hold 42.3 s, needed 10.2 uV, drift 17.4-94.8 uV, ratio 1.70-9.28

## F. Sampled converter noise (uV rms): no droop budget / half / 90 % of the hold time

- 100|0.0001: tuned 160.2 / 134.3 / 66.6; NMOS 159.5 / 132.3 / 65.3; bootstrapped 139.4 / 106.5 / 50.3; TG + dummies 152.1 / 120.4 / 58.0
- 15|0.0001: tuned 74.0 / 61.8 / 30.6; NMOS 72.9 / 59.4 / 29.1; bootstrapped none; TG + dummies 59.3 / 44.4 / 20.7

## G. Area lost to isolated wells (groups of 100 / 25 / 4 / 1)

- pitch 22 um: 100: 8%, 25: 16%, 4: 42%, 1: 91%
- pitch 11 um: 100: 16%, 25: 33%, 4: 91%, 1: 211%
- pitch 9 um: 100: 20%, 25: 41%, 4: 115%, 1: 274%
