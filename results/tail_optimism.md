## Tail optimism of the surrogate (scaled-sigma, 20 channels per scale)

| design, band | s | depth (sigma) | window on every channel | largest residual (µV) | surrogate (µV) | ratio |
|---|---|---|---|---|---|---|
| TG|300 K | 1 | 1.8 | 0.3-1.5 V | 104.4 | 103.2 | 1.011 |
| TG|300 K | 1.5 | 2.7 | 0.3-1.5 V | 106.3 | 105.0 | 1.013 |
| TG|300 K | 2 | 3.6 | 0.3-1.5 V | 108.4 | 106.8 | 1.015 |
| TG|300 K | 2.5 | 4.6 | 0.3-1.5 V | 110.5 | 108.6 | 1.017 |
| TG|300 K | 3 | 5.5 | 0.3-1.5 V | 112.6 | 110.4 | 1.020 |
| TG|4 K high | 1 | 1.8 | 0.3-1.5 V | 109.4 | 105.7 | 1.035 |
| TG|4 K high | 1.5 | 2.7 | 0.3-1.5 V | 101.2 | 97.1 | 1.042 |
| TG|4 K high | 2 | 3.6 | 0.3-1.5 V | 104.5 | 99.5 | 1.050 |
| TG|4 K high | 2.5 | 4.6 | 0.3-1.5 V | 107.6 | 101.8 | 1.057 |
| TG|4 K high | 3 | 5.5 | 0.3-1.5 V | 110.5 | 104.2 | 1.061 |
| TG|4 K proxy | 1 | 1.8 | 0.3-1.5 V | 102.8 | 98.9 | 1.040 |
| TG|4 K proxy | 1.5 | 2.7 | 0.3-1.5 V | 106.1 | 100.5 | 1.056 |
| TG|4 K proxy | 2 | 3.6 | 0.3-1.5 V | 109.4 | 102.1 | 1.072 |
| TG|4 K proxy | 2.5 | 4.6 | 0.3-1.5 V | 112.7 | 103.8 | 1.086 |
| TG|4 K proxy | 3 | 5.5 | 0.3-1.5 V | 115.8 | 105.5 | 1.098 |
| bootstrapped|4 K proxy | 1 | 1.8 | 0.3-1.5 V | 38.8 | 37.7 | 1.031 |
| bootstrapped|4 K proxy | 1.5 | 2.7 | 0.3-1.5 V | 42.7 | 40.7 | 1.050 |
| bootstrapped|4 K proxy | 2 | 3.6 | 0.3-1.5 V | 46.5 | 43.6 | 1.065 |
| bootstrapped|4 K proxy | 2.5 | 4.6 | 0.3-1.5 V | 50.0 | 46.6 | 1.072 |
| bootstrapped|4 K proxy | 3 | 5.5 | 0.3-1.5 V | 50.7 | 49.6 | 1.022 |

Tail optimism tau at 4.6 to 5.5 sigma: TG|300 K: 2.0 %, TG|4 K high: 6.1 %, TG|4 K proxy: 9.8 %, bootstrapped|4 K proxy: 7.2 %, NMOS|4 K proxy: 7.5 %.
By design (largest over bands; designs without a scaled-sigma run take the largest measured value): TG: 9.8 %, bootstrapped: 7.2 %, NMOS: 7.5 %, not measured: 9.8 %.
