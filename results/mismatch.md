## Mismatch on the worst channel of an array

Margin = static spec / (|nominal residual| + z(N) σ), s = 33.69 dec/V, 99.99 % (168 µV). z(1e+03) = 3.39, z(1e+04) = 3.98, z(1e+06) = 4.96, z(2e+06) = 5.08. 'σ, 95 % upper' uses the one-sided chi-square bound on σ. Per-channel: every Monte Carlo channel calibrated on its own straight line; margin = spec / (mean + z(N) sd) of its remaining nonlinearity.

### 300 K (studies/cells.py, 20 channels per held voltage)

| cell | σ (µV) | RMS margin (budget / σ) | shared cal., worst of 10^4 | worst of 10^6 | worst of 10^6, σ 95 % upper | per-channel cal., worst of 10^6 | per-channel, Monte Carlo max |
|---|---|---|---|---|---|---|---|
| NMOS switch | 7.96 | 21.1 | 4.57 | 3.77 | 2.84 | 6.38 | 10.1 |
| TG | 29.8 | 5.65 | 0.808 | 0.709 | 0.576 | 1.24 | 1.54 |
| TG with dummies | 54.8 | 3.07 | 0.757 | 0.609 | 0.446 | 1.32 | 1.9 |
| bootstrapped NMOS | 10.3 | 16.3 | 4.06 | 3.26 | 2.38 | 5.9 | 8.6 |
| charge-locked TG | 16 | 10.5 | 1.52 | 1.33 | 1.08 | 2.33 | 2.92 |
| thick-oxide T-switch | 99.8 | 1.69 | 0.416 | 0.335 | 0.245 | 0.643 | 0.939 |
| TG, high-threshold PMOS | 19.7 | 8.55 | 0.962 | 0.866 | 0.716 | 1.27 | 1.56 |
| T-switch, buffered, thick oxide | 99.8 | 1.68 | 0.416 | 0.335 | 0.245 | 0.641 | 0.936 |
| T-switch, buffered, thin oxide | 27 | 6.23 | 1.34 | 1.11 | 0.835 | 1.96 | 3.16 |

### 4 K proxy (studies/cryogenic.py, 12 channels per held voltage, mismatch scaled)

| cell | mismatch × | σ (µV) | RMS margin (budget / σ) | shared cal., worst of 10^4 | worst of 10^6 | worst of 10^6, σ 95 % upper | per-channel cal., worst of 10^6 |
|---|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 1 | 6.25 | 26.9 | 5.35 | 4.48 | 3.08 | 7.53 |
| NMOS, 0.3 V underdrive | 1.5 | 9.38 | 17.9 | 3.83 | 3.16 | 2.13 | 5.32 |
| NMOS, 0.3 V underdrive | 2 | 12.5 | 13.4 | 2.98 | 2.45 | 1.63 | 4.83 |
| bootstrapped (transistor level), 0.3 V underdrive | 1 | 52.7 | 3.18 | 0.695 | 0.572 | 0.384 | 1.06 |
| bootstrapped (transistor level), 0.3 V underdrive | 1.5 | 83.2 | 2.02 | 0.463 | 0.378 | 0.25 | 0.712 |
| bootstrapped (transistor level), 0.3 V underdrive | 2 | 117 | 1.44 | 0.339 | 0.275 | 0.181 | 0.512 |
| T-switch + OTA buffer | 1 | 110 | 1.52 | 0.371 | 0.299 | 0.195 | 0.664 |
| T-switch + OTA buffer | 1.5 | 167 | 1.01 | 0.248 | 0.199 | 0.129 | 0.444 |
| T-switch + OTA buffer | 2 | 225 | 0.747 | 0.185 | 0.149 | 0.0963 | 0.33 |
| TG + dummies | 1 | 62 | 2.71 | 0.663 | 0.534 | 0.347 | 1.16 |
| TG + dummies | 1.5 | 92.8 | 1.81 | 0.446 | 0.359 | 0.233 | 0.769 |
| TG + dummies | 2 | 124 | 1.36 | 0.337 | 0.271 | 0.175 | 0.574 |
