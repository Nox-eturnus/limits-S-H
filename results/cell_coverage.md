## Surrogate and interval checks on 100 one-cell channels

| design | Shapiro p (pedestal, min over V) | Shapiro p (per-channel error) | KS p | p90 surrogate / SPICE (µV) | p99 surrogate / SPICE (µV) | coverage model (too low / too high) | coverage subsample (too low / too high) |
|---|---|---|---|---|---|---|---|
| bootstrapped (transistor level), 0.3 V underdrive|4 K proxy | 0.34 | 0.35 | 0.63 | 35.9 / 36.6 | 39.3 / 39.5 | 0.78 (0.21 / 0.01) | 0.88 (0.12 / 0.00) |
| TG, no ESD|4 K proxy | 0.33 | 0.01 | 0.50 | 97.9 / 97.9 | 99.8 / 99.6 | 0.86 (0.12 / 0.02) | 0.75 (0.24 / 0.01) |
| TG, ESD on the node|4 K proxy | 0.33 | 0.02 | 0.52 | 86.4 / 86.4 | 88.0 / 87.8 | 0.87 (0.11 / 0.02) | 0.78 (0.21 / 0.01) |
