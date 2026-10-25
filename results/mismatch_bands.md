## Worst-channel margins in every band (s = 33.69 dec/V, 99.99 %, worst of 10^6 channels)

20 Monte Carlo channels per design and band, mismatch × 1. Nominal: spec / nominal residual. Shared: spec / (|r| + z σ). Per-channel: spec / (mean + z sd) of the per-channel two-point residual.

| design | band | n | nominal | shared cal. | shared, σ 95 % upper | per-channel cal. |
|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 300 K | 20 | 54 | 5.24 | 3.93 | 7.78 |
| NMOS, 0.3 V underdrive | 77 K proxy | 20 | 32.4 | 5.07 | 3.87 | 7.55 |
| NMOS, 0.3 V underdrive | 4 K proxy | 20 | 25.8 | 4.96 | 3.82 | 8 |
| NMOS, 0.3 V underdrive | 4 K high | 20 | 43.1 | 5.5 | 4.15 | 7.86 |
| NMOS, 0.3 V underdrive | 77 K Beall fit | 20 | 31.9 | 5.03 | 3.84 | 7.49 |
| NMOS, 0.3 V underdrive | 4 K, Beall pMOS | 20 | 25.8 | 4.96 | 3.82 | 8 |
| bootstrapped (transistor level), 0.3 V underdrive | 300 K | 20 | 23 | 1 | 0.741 | 1.88 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K proxy | 20 | 7.36 | 0.672 | 0.503 | 1.31 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy | 20 | 5.3 | 0.583 | 0.439 | 1.13 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K high | 20 | 5.05 | 0.602 | 0.454 | 1.16 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K Beall fit | 20 | 13.2 | 0.709 | 0.525 | 1.45 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, Beall pMOS | 20 | 11.7 | 0.84 | 0.625 | 1.77 |
| T-switch + OTA buffer | 300 K | 20 | 39.6 | 0.329 | 0.241 | 0.549 |
| T-switch + OTA buffer | 77 K proxy | 20 | 11.3 | 0.334 | 0.246 | 0.564 |
| T-switch + OTA buffer | 4 K proxy | 20 | 12.7 | 0.342 | 0.251 | 0.574 |
| T-switch + OTA buffer | 4 K high | 20 | 13.9 | 0.349 | 0.256 | 0.587 |
| T-switch + OTA buffer | 77 K Beall fit | 20 | 16.6 | 0.339 | 0.249 | 0.566 |
| T-switch + OTA buffer | 4 K, Beall pMOS | 20 | 19.3 | 0.345 | 0.253 | 0.58 |
| TG + dummies | 300 K | 20 | 36 | 0.529 | 0.388 | 1.15 |
| TG + dummies | 77 K proxy | 20 | 25.3 | 0.547 | 0.402 | 1.18 |
| TG + dummies | 4 K proxy | 20 | 24.2 | 0.559 | 0.41 | 1.2 |
| TG + dummies | 4 K high | 20 | 25.6 | 0.572 | 0.42 | 1.2 |
| TG + dummies | 77 K Beall fit | 20 | 28.4 | 1.32 | 0.977 | 3.11 |
| TG + dummies | 4 K, Beall pMOS | 20 | 32.6 | 1.33 | 0.981 | 3.4 |
| TG, no ESD | 300 K | 20 | 1.67 | 0.621 | 0.504 | 1.09 |
| TG, no ESD | 77 K proxy | 20 | 1.88 | 0.663 | 0.535 | 1.03 |
| TG, no ESD | 4 K proxy | 20 | 1.75 | 0.654 | 0.531 | 0.944 |
| TG, no ESD | 4 K high | 20 | 1.66 | 0.65 | 0.531 | 0.894 |
| TG, no ESD | 77 K Beall fit | 20 | 3.71 | 1.65 | 1.37 | 2.32 |
| TG, no ESD | 4 K, Beall pMOS | 20 | 3.6 | 1.63 | 1.35 | 2.26 |
| TG, ESD on the node | 300 K | 20 | 1.87 | 0.708 | 0.575 | 1.24 |
| TG, ESD on the node | 77 K proxy | 20 | 2.13 | 0.758 | 0.612 | 1.18 |
| TG, ESD on the node | 4 K proxy | 20 | 1.98 | 0.748 | 0.608 | 1.08 |
| TG, ESD on the node | 4 K high | 20 | 1.88 | 0.743 | 0.607 | 1.07 |
| TG, ESD on the node | 77 K Beall fit | 20 | 4.42 | 2.2 | 1.86 | 6.37 |
| TG, ESD on the node | 4 K, Beall pMOS | 20 | 4.41 | 2.23 | 1.89 | 8.43 |

## Tail check, 4 K band

| design | n | σ (µV) | shared, worst of 10^6 | per-channel, worst of 10^6 | Shapiro p (pedestal) | max |z| seen / expected | excess kurtosis | Shapiro p (per-channel residual) |
|---|---|---|---|---|---|---|---|---|
| bootstrapped (transistor level), 0.3 V underdrive | 100 | 35.4 | 0.81 | 1.38 | 0.83 | 3.13 / 2.70 | 0.19 | 0.43 |
| TG + dummies | 100 | 51 | 0.645 | 1.24 | 0.18 | 3.02 / 2.70 | -0.21 | 0.005 |
