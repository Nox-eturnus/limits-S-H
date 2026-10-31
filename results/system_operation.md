## Margins at the operating points of measured devices (4 K band, worst of 10^6, levels set open-loop)

Closed-form margins (studies/array_yield.py) with the budgets of each slope; joint: within the allocation of Supplementary Section S12 with device noise of 9 or 49 µV/√Hz at 1 Hz and kT/C at 4.2 K.

| device | s (dec/V) | target | b_eq / b_ind (µV) | device share 9 / 49 µV/√Hz | NMOS: per channel / shared / joint 9 / joint 49 | bootstrapped: per channel / shared / joint 9 / joint 49 | T-switch + OTA: per channel / shared / joint 9 / joint 49 | TG + dummies: per channel / shared / joint 9 / joint 49 | TG: per channel / shared / joint 9 / joint 49 | TG with ESD: per channel / shared / joint 9 / joint 49 |
|---|---|---|---|---|---|---|---|---|---|---|
| Park et al., conventional gates (Si/SiGe) | 7.25 | 0.001 | 903 / 1626 | 0.001 / 0.02 | 269.78 / 63.53 / 242.71 / 240.27 | 24.23 / 7.66 / 21.80 / 21.58 | 49.27 / 3.85 / 44.33 / 43.88 | 49.13 / 7.26 / 44.20 / 43.76 | 9.18 / 6.09 / 8.26 / 8.18 | 10.41 / 6.94 / 9.37 / 9.27 |
| Park et al., conventional gates (Si/SiGe) | 7.25 | 0.0001 | 286 / 516 | 0.007 / 0.19 | 85.50 / 20.17 / 76.67 / 68.56 | 7.68 / 2.43 / 6.89 / 6.16 | 15.63 / 1.22 / 14.02 / 12.54 | 15.60 / 2.31 / 13.99 / 12.51 | 2.91 / 1.93 / 2.61 / 2.33 | 3.30 / 2.20 / 2.96 / 2.65 |
| Park et al., interchanged gates (Si/SiGe) | 16.6 | 0.001 | 603 / 967 | 0.002 / 0.05 | 175.37 / 38.07 / 157.67 / 153.17 | 15.62 / 4.59 / 14.04 / 13.64 | 30.48 / 2.29 / 27.40 / 26.62 | 29.36 / 4.33 / 26.40 / 25.64 | 6.08 / 3.79 / 5.47 / 5.31 | 6.90 / 4.32 / 6.20 / 6.03 |
| Park et al., interchanged gates (Si/SiGe) | 16.6 | 0.0001 | 192 / 309 | 0.018 / 0.52 | 55.83 / 12.16 / 49.74 / 32.92 | 4.97 / 1.47 / 4.43 / 2.93 | 9.72 / 0.73 / 8.66 / 5.73 | 9.38 / 1.38 / 8.35 / 5.53 | 1.94 / 1.21 / 1.72 / 1.14 | 2.19 / 1.38 / 1.96 / 1.29 |
| Nickl et al., foundry SiMOS | 33.69 | 0.001 | 349 / 525 | 0.006 / 0.18 | 99.85 / 20.74 / 89.56 / 80.58 | 8.85 / 2.50 / 7.94 / 7.14 | 16.87 / 1.25 / 15.13 / 13.62 | 15.98 / 2.35 / 14.33 / 12.89 | 3.51 / 2.11 / 3.14 / 2.83 | 3.98 / 2.40 / 3.57 / 3.21 |
| Nickl et al., foundry SiMOS | 33.69 | 0.0001 | 111 / 168 | 0.062 / 1.77 | 31.89 / 6.65 / 27.70 / 0.00 | 2.83 / 0.80 / 2.46 / 0.00 | 5.40 / 0.40 / 4.69 / 0.00 | 5.12 / 0.75 / 4.45 / 0.00 | 1.12 / 0.67 / 0.97 / 0.00 | 1.27 / 0.77 / 1.10 / 0.00 |

## Device drift between qubit-level retunings (1/f, measured from 1 Hz down to 1/T)

| noise at 1 Hz | drift rms over 100 s / 1 h / 1 day (µV) | retune interval for drift = b_eq/2, strictest point | same, 99.9 % and 10 dec/V |
|---|---|---|---|
| 9 µV/√Hz | 19 / 26 / 30 | 3.15e+07 s | 3.15e+07 s |
| 49 µV/√Hz | 105 / 140 / 165 | 3.63 s | 3.15e+07 s |

## Lines per qubit and the fan-in

Gates per qubit in a square lattice: plunger 1, barrier 2, screening, reservoir, sensor 0.5.

| scenario | individual lines per qubit without multiplexing | individual fast lines with multiplexing | share removed |
|---|---|---|---|
| plungers static (single-qubit gates by a shared drive) | 3.5 | 2 | 43 % |
| plungers pulsed individually | 3.5 | 3 | 14 % |

| routing layers | lines through the edge of a 1 mm² region | side of a region for 10^6 lines | qubit pitch for 10^6 qubits |
|---|---|---|---|
| 4 | 8e+04 | 12.5 mm | 12.5 µm |
| 6 | 1.2e+05 | 8.3 mm | 8.3 µm |
| 10 | 2e+05 | 5.0 mm | 5.0 µm |

Wire from the hold array to a central qubit region: mean 14.8 mm, largest 29.5 mm. Coupling to an adjacent line over the mean length: unshielded 738 to 1476 fF, shielded (1 to 5 % residual) 7.4 to 74 fF, against 0.57 to 1.2 fF at 99.99 % for a neighbour running its own CZ.

## Move margins corrected for the measured interpolation bias (strictest point, Figure 6 designs)

| move | overstatement in the fine windows (interpolated / simulated) | lowest corrected margin outside the fine windows | lowest fine-grid margin |
|---|---|---|---|
| 20 mV | 1.00 to 1.60 | 6.0 (TG, no ESD|4 K high) | 16.4 (TG, no ESD|4 K proxy) |
| 50 mV | 0.80 to 1.27 | 3.0 (TG, no ESD|4 K high) | 8.2 (TG, no ESD|4 K proxy) |

## Power terms left out of the array estimate

| term | energy per refresh |
|---|---|
| clock buffer of the selected path (2 to 5 fF internal per level, 3 to 7 levels, 2.1 V) | 26 to 154 fJ |
| level shifters, -0.3 V and 3.3 V drives (10 to 20 fF each, two per refresh, 3.6 V) | 259 to 518 fJ |
| bootstrap capacitor recharge (50 fF to 1.8 V, bootstrapped switch only) | 162 to 162 fJ |
| total | 0.45 to 0.83 pJ |

Share of the counted refresh and addressing energy: 46.5 mV/s: 0.40 to 0.8 %, 5.5 uV/s: 0.07 to 0.2 %.
Static leakage allowed per cell for the lowest-droop array (1.4 µW) to stay within 19 µW at the mixing chamber: 8.4 pA at 2.1 V. Isolated-well supplies for the NMOS switch: groups of 100 (1e+04 supplies) 1.8 nW each, groups of 25 (4e+04 supplies) 0.4 nW each.

## Gate-referred noise of a pedestal measurement through a charge sensor

S_q from Noiri et al. (SNR 6 in 0.8 µs): 1.5e-05 to 4.5e-05 e/√Hz; S_V = 1.5 to 45 µV/√Hz.

- strictest: 0.0092 to 8.3 s per point; 10^6 channels, 100 in parallel: 9.2 min to 1.4e+02 h
- 99.9 %, 10 dec/V: 0.00017 to 0.16 s per point; 10^6 channels, 100 in parallel: 0.17 min to 2.6 h

