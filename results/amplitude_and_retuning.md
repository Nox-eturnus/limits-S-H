## Locally held pulse amplitude

| s (dec/V) | target | v0 peak (V) | eps untracked | eps tracked, M = 2 | held amplitude, untracked / tracked (mV, k = 0.5) |
|---|---|---|---|---|---|
| 3.87 | 0.001 | 0.672 | 0.362 % | 0.56 % | 4.87 / 7.52 |
| 3.87 | 0.0001 | 0.672 | 0.115 % | 0.179 % | 1.54 / 2.4 |
| 10 | 0.001 | 0.260 | 0.603 % | 0.56 % | 3.13 / 2.91 |
| 10 | 0.0001 | 0.260 | 0.192 % | 0.179 % | 0.999 / 0.93 |
| 16.6 | 0.001 | 0.157 | 0.682 % | 0.56 % | 2.14 / 1.75 |
| 16.6 | 0.0001 | 0.157 | 0.218 % | 0.179 % | 0.683 / 0.56 |
| 33.69 | 0.001 | 0.077 | 0.735 % | 0.56 % | 1.13 / 0.864 |
| 33.69 | 0.0001 | 0.077 | 0.236 % | 0.179 % | 0.364 / 0.276 |

Energy bound per pulse C_node (1 - k) v0^2 / k on 1 pF and power for 10^6 barriers (1 / 10 us rounds):

| s | k = 0.5 | k = 0.8 | k = 0.9 |
|---|---|---|---|
| 3.87 | 451 fJ, 451 / 45.1 mW | 113 fJ, 113 / 11.3 mW | 50.2 fJ, 50.2 / 5.02 mW |
| 10 | 67.6 fJ, 67.6 / 6.76 mW | 16.9 fJ, 16.9 / 1.69 mW | 7.51 fJ, 7.51 / 0.751 mW |
| 33.69 | 5.96 fJ, 5.96 / 0.596 mW | 1.49 fJ, 1.49 / 0.149 mW | 0.662 fJ, 0.662 / 0.0662 mW |

## Device noise at 1 K against the 1/f budget (µV/√Hz at 1 Hz)

9 to 49 µV/√Hz at 0.1 K become 28 to 155 at 1 K for a noise power linear in T, 90 to 490 for an amplitude linear in T.

| target | slope | budget | quiet / noisy device at 1 K (power-linear) |
|---|---|---|---|
| 99.9 % | 3.87 | 438 | ok / ok |
| 99.9 % | 7.25 | 359 | ok / ok |
| 99.9 % | 10 | 304 | ok / ok |
| 99.9 % | 16.6 | 214 | ok / ok |
| 99.9 % | 33.69 | 116 | ok / exceeds |
| 99.99 % | 3.87 | 139 | ok / exceeds |
| 99.99 % | 7.25 | 114 | ok / exceeds |
| 99.99 % | 10 | 96 | ok / exceeds |
| 99.99 % | 16.6 | 68 | ok / exceeds |
| 99.99 % | 33.69 | 37 | ok / exceeds |

## Pulse-driver power for 10^6 barriers

- s = 3.87: C V^2 bound k = 0.5: 451 / 45.1 mW, k = 0.9: 50.2 / 5.02 mW (1 / 10 us rounds)
- s = 10: C V^2 bound k = 0.5: 67.6 / 6.76 mW, k = 0.9: 7.51 / 0.751 mW (1 / 10 us rounds)
- s = 33.69: C V^2 bound k = 0.5: 5.96 / 0.596 mW, k = 0.9: 0.662 / 0.0662 mW (1 / 10 us rounds)
- switched-capacitor cells (Pauka et al., 18 nW per cell, 100 mV pulses): 18 mW
- one cryo-CMOS DAC per barrier (157 uW, Enthoven et al.): 157 W
- stages: 20 mK 0.019 mW, 140 mK 0.2 mW, 1.2 K 40 mW, 4.2 K 1500 mW

## Retuning every pair on the qubits

5.71e+05 pairs (barriers of 10^6 electrodes)

| case | per pair | 100 / 1e4 pairs at once | fraction of time, retuned daily / hourly / every 100 s |
|---|---|---|---|
| lean | 15 ms | 85.7 / 0.857 s | 9.9e-06-0.00099 / 0.00024-0.024 / 0.0086-0.86 |
| careful | 180 ms | 1.03e+03 / 10.3 s | 0.00012-0.012 / 0.0029-0.29 / 0.1-10 |

## Calibration time with ten measurements per channel (seven pedestal points, two droop, one pulse)

- strictest: 100 at once 1 h to 38 d; 1000 at once 6.1 min to 3.8 d; 10000 at once 37 s to 9.2 h
- 99.9 %, 10 dec/V: 100 at once 1.2 min to 17 h; 1000 at once 6.9 s to 1.7 h; 10000 at once 0.69 s to 10 min

