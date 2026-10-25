## Worst-of-10^6 margins, per-gate and operational budget

Budgets (mV): s33.69_t0.0001: per-gate 0.168, operational 0.091; s33.69_t0.001: per-gate 0.524, operational 0.287; s10_t0.001: per-gate 1.373, operational 0.967

### 300 K, nine cells (20 channels)

| cell | per-gate 99.99 % s 33.69: per-ch / shared | operational 99.99 % s 33.69 | operational 99.9 % s 33.69 | operational 99.9 % s 10 |
|---|---|---|---|---|
| NMOS switch | 6.37 / 3.77 | 3.46 / 2.05 | 10.87 / 6.43 | 36.66 / 21.68 |
| TG | 1.24 / 0.71 | 0.68 / 0.38 | 2.12 / 1.21 | 7.15 / 4.07 |
| TG with dummies | 1.32 / 0.61 | 0.72 / 0.33 | 2.25 / 1.04 | 7.59 / 3.50 |
| bootstrapped NMOS | 5.89 / 3.25 | 3.20 / 1.77 | 10.06 / 5.56 | 33.93 / 18.74 |
| charge-locked TG | 2.33 / 1.33 | 1.27 / 0.72 | 3.98 / 2.26 | 13.42 / 7.64 |
| thick-oxide T-switch | 0.64 / 0.33 | 0.35 / 0.18 | 1.10 / 0.57 | 3.70 / 1.93 |
| TG, high-threshold PMOS | 1.27 / 0.86 | 0.69 / 0.47 | 2.17 / 1.48 | 7.33 / 4.98 |
| T-switch, buffered, thick oxide | 0.64 / 0.33 | 0.35 / 0.18 | 1.09 / 0.57 | 3.69 / 1.93 |
| T-switch, buffered, thin oxide | 1.96 / 1.11 | 1.06 / 0.60 | 3.34 / 1.89 | 11.26 / 6.37 |

### Bands (20 channels)

| cell | per-gate 99.99 % s 33.69: per-ch / shared | operational 99.99 % s 33.69 | operational 99.9 % s 33.69 | operational 99.9 % s 10 |
|---|---|---|---|---|
| NMOS, 0.3 V underdrive|300 K | 7.78 / 5.24 | 4.23 / 2.85 | 13.29 / 8.95 | 44.81 / 30.17 |
| NMOS, 0.3 V underdrive|77 K proxy | 7.55 / 5.07 | 4.10 / 2.76 | 12.89 / 8.66 | 43.46 / 29.21 |
| NMOS, 0.3 V underdrive|4 K proxy | 8.00 / 4.96 | 4.35 / 2.70 | 13.67 / 8.47 | 46.09 / 28.57 |
| NMOS, 0.3 V underdrive|4 K high | 7.86 / 5.50 | 4.27 / 2.99 | 13.42 / 9.38 | 45.27 / 31.64 |
| NMOS, 0.3 V underdrive|77 K Beall fit | 7.49 / 5.03 | 4.08 / 2.74 | 12.80 / 8.60 | 43.15 / 28.99 |
| NMOS, 0.3 V underdrive|4 K, Beall pMOS | 8.00 / 4.96 | 4.35 / 2.70 | 13.67 / 8.47 | 46.09 / 28.57 |
| bootstrapped (transistor level), 0.3 V underdrive|300 K | 1.88 / 1.00 | 1.02 / 0.55 | 3.21 / 1.71 | 10.82 / 5.78 |
| bootstrapped (transistor level), 0.3 V underdrive|77 K proxy | 1.31 / 0.67 | 0.71 / 0.37 | 2.24 / 1.15 | 7.56 / 3.87 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K proxy | 1.13 / 0.58 | 0.62 / 0.32 | 1.93 / 1.00 | 6.52 / 3.36 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K high | 1.16 / 0.60 | 0.63 / 0.33 | 1.98 / 1.03 | 6.67 / 3.47 |
| bootstrapped (transistor level), 0.3 V underdrive|77 K Beall fit | 1.45 / 0.71 | 0.79 / 0.39 | 2.48 / 1.21 | 8.36 / 4.08 |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, Beall pMOS | 1.77 / 0.84 | 0.96 / 0.46 | 3.03 / 1.44 | 10.21 / 4.84 |
| T-switch + OTA buffer|300 K | 0.55 / 0.33 | 0.30 / 0.18 | 0.94 / 0.56 | 3.16 / 1.89 |
| T-switch + OTA buffer|77 K proxy | 0.56 / 0.33 | 0.31 / 0.18 | 0.96 / 0.57 | 3.25 / 1.92 |
| T-switch + OTA buffer|4 K proxy | 0.57 / 0.34 | 0.31 / 0.19 | 0.98 / 0.58 | 3.31 / 1.97 |
| T-switch + OTA buffer|4 K high | 0.59 / 0.35 | 0.32 / 0.19 | 1.00 / 0.60 | 3.38 / 2.01 |
| T-switch + OTA buffer|77 K Beall fit | 0.57 / 0.34 | 0.31 / 0.18 | 0.97 / 0.58 | 3.26 / 1.95 |
| T-switch + OTA buffer|4 K, Beall pMOS | 0.58 / 0.35 | 0.32 / 0.19 | 0.99 / 0.59 | 3.34 / 1.99 |
| TG + dummies|300 K | 1.15 / 0.53 | 0.62 / 0.29 | 1.96 / 0.90 | 6.60 / 3.05 |
| TG + dummies|77 K proxy | 1.18 / 0.55 | 0.64 / 0.30 | 2.01 / 0.93 | 6.78 / 3.15 |
| TG + dummies|4 K proxy | 1.20 / 0.56 | 0.65 / 0.30 | 2.04 / 0.95 | 6.88 / 3.22 |
| TG + dummies|4 K high | 1.20 / 0.57 | 0.65 / 0.31 | 2.05 / 0.98 | 6.90 / 3.30 |
| TG + dummies|77 K Beall fit | 3.11 / 1.32 | 1.69 / 0.72 | 5.31 / 2.26 | 17.89 / 7.61 |
| TG + dummies|4 K, Beall pMOS | 3.40 / 1.33 | 1.85 / 0.72 | 5.80 / 2.27 | 19.56 / 7.66 |
| TG, no ESD|300 K | 1.09 / 0.62 | 0.59 / 0.34 | 1.87 / 1.06 | 6.30 / 3.58 |
| TG, no ESD|77 K proxy | 1.03 / 0.66 | 0.56 / 0.36 | 1.76 / 1.13 | 5.95 / 3.82 |
| TG, no ESD|4 K proxy | 0.94 / 0.65 | 0.51 / 0.36 | 1.61 / 1.12 | 5.44 / 3.77 |
| TG, no ESD|4 K high | 0.89 / 0.65 | 0.49 / 0.35 | 1.53 / 1.11 | 5.15 / 3.74 |
| TG, no ESD|77 K Beall fit | 2.32 / 1.65 | 1.26 / 0.90 | 3.95 / 2.82 | 13.33 / 9.50 |
| TG, no ESD|4 K, Beall pMOS | 2.26 / 1.63 | 1.23 / 0.88 | 3.86 / 2.78 | 13.01 / 9.37 |
| TG, ESD on the node|300 K | 1.24 / 0.71 | 0.68 / 0.38 | 2.12 / 1.21 | 7.15 / 4.07 |
| TG, ESD on the node|77 K proxy | 1.18 / 0.76 | 0.64 / 0.41 | 2.01 / 1.29 | 6.79 / 4.36 |
| TG, ESD on the node|4 K proxy | 1.08 / 0.75 | 0.59 / 0.41 | 1.84 / 1.28 | 6.20 / 4.31 |
| TG, ESD on the node|4 K high | 1.07 / 0.74 | 0.58 / 0.40 | 1.83 / 1.27 | 6.18 / 4.28 |
| TG, ESD on the node|77 K Beall fit | 6.37 / 2.20 | 3.46 / 1.20 | 10.87 / 3.76 | 36.65 / 12.68 |
| TG, ESD on the node|4 K, Beall pMOS | 8.43 / 2.23 | 4.58 / 1.21 | 14.40 / 3.81 | 48.55 / 12.85 |

### 4 K band, long runs

| cell | per-gate 99.99 % s 33.69: per-ch / shared | operational 99.99 % s 33.69 | operational 99.9 % s 33.69 | operational 99.9 % s 10 |
|---|---|---|---|---|
| bootstrapped (transistor level), 0.3 V underdrive | 1.38 / 0.81 | 0.75 / 0.44 | 2.36 / 1.38 | 7.96 / 4.66 |
| TG + dummies | 1.24 / 0.65 | 0.68 / 0.35 | 2.12 / 1.10 | 7.16 / 3.72 |
