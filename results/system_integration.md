## Load at the qubit stage: tree and hold cells plus the lower bound on the pulse drivers (10^6 electrodes, 10^6 barriers)

| droop | s (dec/V) | round | static array | pulse drivers (lower bound) | total | stages that can carry it |
|---|---|---|---|---|---|---|
| 46.5 mV/s | 3.87 | 1 µs | 2.25 mW | 452 mW | 454 mW | 4.2 K |
| 46.5 mV/s | 3.87 | 10 µs | 2.25 mW | 45.2 mW | 47.4 mW | 4.2 K |
| 46.5 mV/s | 10 | 1 µs | 2.25 mW | 67.7 mW | 69.9 mW | 4.2 K |
| 46.5 mV/s | 10 | 10 µs | 2.25 mW | 6.77 mW | 9.02 mW | 1.2 K, 4.2 K |
| 46.5 mV/s | 33.69 | 1 µs | 2.25 mW | 5.97 mW | 8.22 mW | 1.2 K, 4.2 K |
| 46.5 mV/s | 33.69 | 10 µs | 2.25 mW | 0.597 mW | 2.85 mW | 1.2 K, 4.2 K |
| 3.1 mV/s | 3.87 | 1 µs | 0.218 mW | 452 mW | 452 mW | 4.2 K |
| 3.1 mV/s | 3.87 | 10 µs | 0.218 mW | 45.2 mW | 45.4 mW | 4.2 K |
| 3.1 mV/s | 10 | 1 µs | 0.218 mW | 67.7 mW | 67.9 mW | 4.2 K |
| 3.1 mV/s | 10 | 10 µs | 0.218 mW | 6.77 mW | 6.99 mW | 1.2 K, 4.2 K |
| 3.1 mV/s | 33.69 | 1 µs | 0.218 mW | 5.97 mW | 6.19 mW | 1.2 K, 4.2 K |
| 3.1 mV/s | 33.69 | 10 µs | 0.218 mW | 0.597 mW | 0.815 mW | 1.2 K, 4.2 K |
| 5.5 uV/s | 3.87 | 1 µs | 0.0014 mW | 452 mW | 452 mW | 4.2 K |
| 5.5 uV/s | 3.87 | 10 µs | 0.0014 mW | 45.2 mW | 45.2 mW | 4.2 K |
| 5.5 uV/s | 10 | 1 µs | 0.0014 mW | 67.7 mW | 67.7 mW | 4.2 K |
| 5.5 uV/s | 10 | 10 µs | 0.0014 mW | 6.77 mW | 6.77 mW | 1.2 K, 4.2 K |
| 5.5 uV/s | 33.69 | 1 µs | 0.0014 mW | 5.97 mW | 5.97 mW | 1.2 K, 4.2 K |
| 5.5 uV/s | 33.69 | 10 µs | 0.0014 mW | 0.597 mW | 0.598 mW | 1.2 K, 4.2 K |

## Placement of hold cells and pulse drivers

10^6 electrodes at 3.5 electrodes per qubit = 2.86e+05 qubits; every electrode needs its own connection from its hold cell, static or pulsed.

| placement | assumption | qubit pitch |
|---|---|---|
| hold cells under their electrodes | cell pitch for 1 pF | 41.2 to 41.2 µm |
| hold cells under their electrodes | cell pitch for 200 fF | 16.8 to 20.6 µm |
| hold cells under their electrodes | cell pitch for 70 fF | 7.5 to 16.8 µm |
| separate hold array, in-plane fan-in through the edge | 4 routing layers, 200 nm per line | 23.4 µm (region side 12.5 mm) |
| separate hold array, in-plane fan-in through the edge | 6 routing layers, 200 nm per line | 15.6 µm (region side 8.3 mm) |
| separate hold array, in-plane fan-in through the edge | 10 routing layers, 200 nm per line | 9.4 µm (region side 5.0 mm) |
| separate hold tier, face-to-face bonds | bond pitch 1 µm | 1.9 µm (region side 1 mm) |
| separate hold tier, face-to-face bonds | bond pitch 3 µm | 5.6 µm (region side 3 mm) |
| separate hold tier, face-to-face bonds | bond pitch 10 µm | 18.7 µm (region side 10 mm) |

Electronic compensation accuracy that a 15 mm pulse line needs when its crosstalk depends on the schedule (a neighbour that sometimes pulses and sometimes idles); with a fixed schedule the crosstalk is absorbed by qubit-level tuning of the CZ amplitude.

| target | line | coupling | limit | required accuracy |
|---|---|---|---|---|
| 99.99 % | unshielded | 740 to 1.5e+03 fF | 0.57 to 1.2 fF | 0.038 to 0.16 % |
| 99.99 % | shielded (1 to 5 % residual) | 7 to 74 fF | 0.57 to 1.2 fF | 0.77 to 17 % |
| 99.9 % | unshielded | 740 to 1.5e+03 fF | 1.8 to 3.7 fF | 0.12 to 0.5 % |
| 99.9 % | shielded (1 to 5 % residual) | 7 to 74 fF | 1.8 to 3.7 fF | 2.4 to 52 % |

## Open-loop moves between qubit-level tunings

Drift of a level between tunings (1/f, studies/system_operation.py): 9 uV/rtHz: 30 µV per day; 49 uV/rtHz: 165 µV per day.
A virtual-gate correction moves a barrier by the drift of a neighbour times a normalised cross-coupling below one, so drift compensation needs moves below about 0.2 mV per day.

| lowest 20 mV margin | 0.2 mV | 1 mV | 5 mV |
|---|---|---|---|
| interpolated, corrected (6) | 600 | 120 | 24 |
| fine grid (16) | 1600 | 320 | 64 |

## Calibration time of 10^6 channels, differential points, against the number of sensors read at once

| point accuracy | 100 at once | 1000 at once | 10000 at once |
|---|---|---|---|
| strictest | 37 min to 23 d | 3.7 min to 2.3 d | 0.37 min to 5.5 h |
| 99.9 %, 10 dec/V | 0.69 min to 10 h | 0.069 min to 1 h | 0.0069 min to 6.2 min |

## Electrodes per DAC over the measured leakage range of the protection diodes (1 pF node, 99.9 %, 10 dec/V, 4 K switching models)

| design | low (0.9 mV/s): flat / tree | typical (46.5 mV/s): flat / tree | high (0.27 V/s): flat / tree |
|---|---|---|---|
| NMOS, 0.3 V underdrive | 3.4e+04 / 1.2e+06 | 8.2e+03 / 1.3e+05 | 4.2e+03 / 4.2e+04 |
| bootstrapped (transistor level), 0.3 V underdrive | 3.2e+04 / 1.1e+06 | 7.8e+03 / 1.2e+05 | 4e+03 / 3.7e+04 |
| T-switch + OTA buffer | 3.3e+04 / 1.1e+06 | 8e+03 / 1.2e+05 | 4.1e+03 / 3.9e+04 |
| TG + dummies | 2.9e+04 / 1e+06 | 7.3e+03 / 7.5e+04 | 3.7e+03 / 1.9e+04 |
| TG, no ESD | 2.9e+04 / 1e+06 | 7.1e+03 / 7.2e+04 | 3.6e+03 / 1.8e+04 |
| TG, ESD on the node | 2.9e+04 / 9.9e+05 | 7.1e+03 / 7e+04 | 3.6e+03 / 1.7e+04 |

## Untracked single-gate static budget against the Zeeman difference (Stark 10^8 Hz/V on one qubit)

The gate time is lengthened in proportion to 1/ΔE_Z below 100 MHz so that the peak exchange stays at ΔE_Z/5.

| ΔE_Z | gate time | nominal 1 - F | 3.87 dec/V: 99.9 % / 99.99 % (mV) | 10 dec/V: 99.9 % / 99.99 % (mV) | 33.69 dec/V: 99.9 % / 99.99 % (mV) |
|---|---|---|---|---|---|
| 1000 MHz | 50 ns | 5.7e-10 | 2.04 / 0.646 | 1.45 / 0.462 | 0.549 / 0.176 |
| 100 MHz | 50 ns | 3.8e-06 | 1.99 / 0.629 | 1.37 / 0.437 | 0.525 / 0.168 |
| 50 MHz | 100 ns | 2.5e-06 | 1.08 / 0.342 | 0.931 / 0.295 | 0.477 / 0.152 |
| 25 MHz | 200 ns | 7.9e-08 | 0.556 / 0.176 | 0.529 / 0.167 | 0.377 / 0.12 |

