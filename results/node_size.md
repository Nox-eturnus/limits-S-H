# Node size, static array and pulse drivers

## Static array at the lowest measured droop (5.5 aA of leakage), 10^6 electrodes

| node | pitch (um) | design | droop (uV/s) | electrodes per DAC | per reticle | cold load (uW) |
|---|---|---|---|---|---|---|
| 1000 fF | 22 | NMOS, 0.3 V underdrive | 5.5 | 1.8e+07 | 1.8e+06 | 1.38 |
| 1000 fF | 22 | bootstrapped (transistor level), 0.3 V underdrive | 5.5 | 1.7e+07 | 1.8e+06 | 1.4 |
| 1000 fF | 22 | TG + dummies | 5.5 | 1.6e+07 | 1.8e+06 | 0.938 |
| 200 fF | 11 | NMOS, 0.3 V underdrive | 27.5 | 1.6e+07 | 7.1e+06 | 2.49 |
| 200 fF | 11 | bootstrapped (transistor level), 0.3 V underdrive | 27.5 | 1.6e+07 | 7.1e+06 | 2.79 |
| 200 fF | 11 | TG + dummies | 27.5 | 1.5e+07 | 7.1e+06 | 2.49 |
| 70 fF | 9 | NMOS, 0.3 V underdrive | 78.6 | 1.2e+07 | 1.1e+07 | 5.64 |
| 70 fF | 9 | bootstrapped (transistor level), 0.3 V underdrive | 78.6 | 9.5e+06 | 1.1e+07 | 7.68 |
| 70 fF | 9 | TG + dummies | 78.6 | 8.9e+06 | 1.1e+07 | 5.49 |

## Pulse drivers at the resistive bound, 10^6 barriers, with the static load of the same node

| node | s (dec/V) | energy k=0.5 / 0.9 (fJ) | 1 us rounds (mW): k=0.5 / 0.9, stage | 10 us rounds (mW): k=0.5 / 0.9, stage |
|---|---|---|---|---|
| 1000 fF | 3.87 | 452 / 50.2 | 452 / 50.2, 4.2 K / 4.2 K | 45.2 / 5.02, 4.2 K / 1.2 K |
| 1000 fF | 10 | 67.7 / 7.52 | 67.7 / 7.52, 4.2 K / 1.2 K | 6.77 / 0.752, 1.2 K / 1.2 K |
| 1000 fF | 16.6 | 24.6 / 2.73 | 24.6 / 2.73, 1.2 K / 1.2 K | 2.46 / 0.273, 1.2 K / 1.2 K |
| 1000 fF | 33.69 | 5.97 / 0.663 | 5.97 / 0.663, 1.2 K / 1.2 K | 0.597 / 0.0663, 1.2 K / 140 mK |
| 200 fF | 3.87 | 90.4 / 10 | 90.4 / 10, 4.2 K / 1.2 K | 9.04 / 1, 1.2 K / 1.2 K |
| 200 fF | 10 | 13.5 / 1.5 | 13.5 / 1.5, 1.2 K / 1.2 K | 1.35 / 0.15, 1.2 K / 140 mK |
| 200 fF | 16.6 | 4.91 / 0.546 | 4.91 / 0.546, 1.2 K / 1.2 K | 0.491 / 0.0546, 1.2 K / 140 mK |
| 200 fF | 33.69 | 1.19 / 0.133 | 1.19 / 0.133, 1.2 K / 140 mK | 0.119 / 0.0133, 140 mK / 20 mK |
| 70 fF | 3.87 | 31.6 / 3.52 | 31.6 / 3.52, 1.2 K / 1.2 K | 3.16 / 0.352, 1.2 K / 1.2 K |
| 70 fF | 10 | 4.74 / 0.527 | 4.74 / 0.527, 1.2 K / 1.2 K | 0.474 / 0.0527, 1.2 K / 140 mK |
| 70 fF | 16.6 | 1.72 / 0.191 | 1.72 / 0.191, 1.2 K / 140 mK | 0.172 / 0.0191, 140 mK / 140 mK |
| 70 fF | 33.69 | 0.418 / 0.0464 | 0.418 / 0.0464, 1.2 K / 140 mK | 0.0418 / 0.00464, 140 mK / 20 mK |
