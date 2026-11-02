## Body effect (k1, k2) scaled, 4 K band, strictest point, per channel / shared (closed form)

| Design | reference (same 20 channels) | k x 0.7 | k x 1.3 | curvature of the mean channel (µV): ref / 0.7 / 1.3 |
|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 29.6 / 6.17 | 25.4 / 6.61 | 34.6 / 5.78 | 2.98 / 3.5 / 2.55 |
| bootstrapped (transistor level), 0.3 V underdrive | 2.72 / 0.78 | 2.41 / 0.912 | 2.58 / 0.608 | 31.2 / 39.4 / 29.8 |
| TG + dummies | 4.65 / 0.686 | 2.05 / 0.388 | 2.46 / 1.19 | 3.99 / 20.7 / 28.5 |
| TG, no ESD | 1.01 / 0.716 | 0.982 / 0.534 | 1.01 / 0.79 | 95.6 / 100 / 93.1 |

## Numerical tolerance (4 K band, seeds 0 to 10)

| Design | Setting | largest change of a pedestal (µV) | largest change of a deviation from the line (µV) | largest deviation, ref / new (µV) |
|---|---|---|---|---|
| NMOS, 0.3 V underdrive | 4 K, reltol 1e-6 | 0.00374 | 0.00245 | 3.15 / 3.15 |
| NMOS, 0.3 V underdrive | 4 K, reltol 1e-7 | 0.0625 | 0.0121 | 3.15 / 3.15 |
| NMOS, 0.3 V underdrive | 4 K, max step 5 ps | 0.0702 | 0.0065 | 3.15 / 3.15 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, reltol 1e-6 | 1.08 | 0.845 | 36.2 / 35.7 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, reltol 1e-7 | 1.43 | 0.753 | 36.2 / 35.6 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, max step 5 ps | 1.16 | 0.507 | 36.2 / 35.8 |
| TG, no ESD | 4 K, reltol 1e-6 | 0.129 | 0.0515 | 103 / 103 |
| TG, no ESD | 4 K, reltol 1e-7 | 0.299 | 0.0442 | 103 / 103 |
| TG, no ESD | 4 K, max step 5 ps | 0.305 | 0.0531 | 103 / 103 |

## Transmission gates sized for settling, on 1 pF, nominal cell, 20 mV grid

Margins against the untracked budget for equal signs: open-loop / move of 50 mV / move of 20 mV.

| W (um) | band | tau_node (ns) | window | 99.99 %, 33.69 | 99.99 %, 16.6 | 99.9 %, 33.69 | 99.9 %, 10 |
|---|---|---|---|---|---|---|---|
| 5 | 300 K | 1.52 | 0.3-1.5 V | 0.217 / 1.05 / 2.08 | 0.374 / 1.8 / 3.59 | 0.681 / 3.28 / 6.53 | 1.56 / 7.51 / 14.9 |
| 5 | 4 K proxy | 1.52 | 0.3-1.5 V | 0.234 / 1.06 / 2.11 | 0.403 / 1.82 / 3.63 | 0.734 / 3.32 / 6.6 | 1.68 / 7.59 / 15.1 |
| 10 | 300 K | 0.797 | 0.3-1.5 V | 0.107 / 0.489 / 0.969 | 0.184 / 0.841 / 1.67 | 0.335 / 1.53 / 3.04 | 0.767 / 3.51 / 6.95 |
| 10 | 4 K proxy | 0.797 | 0.3-1.5 V | 0.115 / 0.531 / 1.06 | 0.198 / 0.914 / 1.83 | 0.361 / 1.66 / 3.33 | 0.826 / 3.81 / 7.62 |
| 20 | 300 K | 0.436 | 0.3-1.5 V | 0.0513 / 0.221 / 0.436 | 0.0883 / 0.38 / 0.751 | 0.161 / 0.692 / 1.37 | 0.368 / 1.58 / 3.13 |
| 20 | 4 K proxy | 0.436 | 0.3-1.5 V | 0.0567 / 0.268 / 0.535 | 0.0976 / 0.461 / 0.922 | 0.178 / 0.84 / 1.68 | 0.407 / 1.92 / 3.84 |
| 40 | 300 K | 0.259 | 0.3-1.5 V | 0.0246 / 0.101 / 0.199 | 0.0423 / 0.174 / 0.343 | 0.077 / 0.316 / 0.624 | 0.176 / 0.723 / 1.43 |
| 40 | 4 K proxy | 0.259 | 0.3-1.5 V | 0.0289 / 0.135 / 0.27 | 0.0497 / 0.233 / 0.465 | 0.0905 / 0.424 / 0.847 | 0.207 / 0.97 / 1.94 |

## GF180 with current-factor mismatch, 4 K band, strictest point (closed form, tau 9.8 %)

| Design | threshold only: per channel / shared | with current factor: per channel / shared | spread of the pedestal (µV): old / new |
|---|---|---|---|
| GF180 NMOS, 0.3 V underdrive | 661 / 5.41 | 661 / 5.41 | 5.34 / 5.33 |
| GF180 bootstrapped (transistor level), 0.3 V underdrive | 13.5 / 3.16 | 13.4 / 3.13 | 8.86 / 9.09 |
| GF180 TG + dummies | 5.15 / 1.51 | 5.52 / 1.2 | 20.3 / 24.8 |
| GF180 TG, no ESD | 0.62 / 0.52 | 0.622 / 0.525 | 14.5 / 14.6 |
| GF180 TG, no ESD, W 0.42 | 1.45 / 1.12 | 1.46 / 1.14 | 8.97 / 9.07 |

