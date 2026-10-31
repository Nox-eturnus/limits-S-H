## Scaled-sigma check (4 K band, 20 channels per scale)

| design | s | depth (sigma) | window on every channel | voltages lost | largest residual (µV) | surrogate (µV) |
|---|---|---|---|---|---|---|
| TG | 1 | 1.8 | 0.3-1.5 V | – | 102.8 | 98.9 |
| TG | 1.5 | 2.7 | 0.3-1.5 V | – | 106.1 | 100.5 |
| TG | 2 | 3.6 | 0.3-1.5 V | – | 109.4 | 102.1 |
| TG | 2.5 | 4.6 | 0.3-1.5 V | – | 112.7 | 103.8 |
| TG | 3 | 5.5 | 0.3-1.5 V | – | 115.8 | 105.5 |
| bootstrapped | 1 | 1.8 | 0.3-1.5 V | – | 38.8 | 37.7 |
| bootstrapped | 1.5 | 2.7 | 0.3-1.5 V | – | 42.7 | 40.7 |
| bootstrapped | 2 | 3.6 | 0.3-1.5 V | – | 46.5 | 43.6 |
| bootstrapped | 2.5 | 4.6 | 0.3-1.5 V | – | 50.0 | 46.6 |
| bootstrapped | 3 | 5.5 | 0.3-1.5 V | – | 50.7 | 49.6 |

## Capacitance sensitivity (4 K band, 20 channels; closed-form margins at the strictest point)

| design | condition | window | curvature of the mean channel (µV) | per channel | P(array) | shared | 99.9 %, per channel |
|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 4 K proxy | 0.3-0.8 | 3.0 | 31.87 | 0.0e+00 | 6.63 | 99.80 |
| NMOS, 0.3 V underdrive | 4 K, overlap capacitances x 0.7 | 0.3-0.8 | 3.0 | 32.04 | 0.0e+00 | 6.65 | 100.32 |
| NMOS, 0.3 V underdrive | 4 K, overlap capacitances x 1.3 | 0.3-0.8 | 3.0 | 31.71 | 0.0e+00 | 6.62 | 99.27 |
| NMOS, 0.3 V underdrive | 4 K, junction capacitances x 0.7 | 0.3-0.8 | 3.0 | 31.87 | 0.0e+00 | 6.63 | 99.78 |
| NMOS, 0.3 V underdrive | 4 K, junction capacitances x 1.3 | 0.3-0.8 | 3.0 | 31.88 | 0.0e+00 | 6.63 | 99.81 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy | 0.3-1.5 | 31.2 | 2.91 | 0.0e+00 | 0.84 | 9.12 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, overlap capacitances x 0.7 | 0.3-1.5 | 28.7 | 3.15 | 0.0e+00 | 0.88 | 9.87 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, overlap capacitances x 1.3 | 0.3-1.5 | 33.9 | 2.73 | 0.0e+00 | 0.80 | 8.54 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, junction capacitances x 0.7 | 0.3-1.5 | 29.4 | 3.03 | 0.0e+00 | 0.84 | 9.49 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, junction capacitances x 1.3 | 0.3-1.5 | 32.9 | 2.81 | 0.0e+00 | 0.84 | 8.81 |
| TG + dummies | 4 K proxy | 0.3-1.5 | 4.0 | 5.11 | 7.0e-165 | 0.75 | 15.94 |
| TG + dummies | 4 K, overlap capacitances x 0.7 | 0.3-1.5 | 3.8 | 5.15 | 2.3e-165 | 0.75 | 16.07 |
| TG + dummies | 4 K, overlap capacitances x 1.3 | 0.3-1.5 | 4.2 | 5.07 | 1.9e-164 | 0.75 | 15.83 |
| TG + dummies | 4 K, junction capacitances x 0.7 | 0.3-1.5 | 4.0 | 5.11 | 1.4e-164 | 0.75 | 15.93 |
| TG + dummies | 4 K, junction capacitances x 1.3 | 0.3-1.5 | 4.0 | 5.11 | 3.6e-165 | 0.75 | 15.96 |
| TG, no ESD | 4 K proxy | 0.3-1.5 | 95.6 | 1.11 | 2.3e-41 | 0.79 | 3.47 |
| TG, no ESD | 4 K, overlap capacitances x 0.7 | 0.3-1.5 | 95.9 | 1.10 | 7.0e-40 | 0.78 | 3.46 |
| TG, no ESD | 4 K, overlap capacitances x 1.3 | 0.3-1.5 | 95.4 | 1.11 | 6.9e-43 | 0.79 | 3.48 |
| TG, no ESD | 4 K, junction capacitances x 0.7 | 0.3-1.5 | 95.7 | 1.11 | 4.3e-41 | 0.79 | 3.46 |
| TG, no ESD | 4 K, junction capacitances x 1.3 | 0.3-1.5 | 95.6 | 1.11 | 1.2e-41 | 0.79 | 3.47 |
