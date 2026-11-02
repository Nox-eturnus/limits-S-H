# 90 % interval of the tail optimism tau

| design, band | tau (point estimate) | 90 % interval | spread of the largest of 20 (q05 to q95 of max/median) |
|---|---|---|---|
| TG|300 K | 2.0 % | -3.0 to 6.3 % | 0.96 to 1.05 |
| TG|4 K high | 6.1 % | -1.0 to 12.3 % | 0.94 to 1.07 |
| TG|4 K proxy | 9.8 % | 4.3 to 14.1 % | 0.96 to 1.05 |
| bootstrapped|4 K proxy | 7.3 % | -8.3 to 23.1 % | 0.87 to 1.17 |
| NMOS|4 K proxy | 7.5 % | -7.0 to 21.6 % | 0.88 to 1.16 |

Largest upper end: 23.1 %.

Upper ends applied: TG 14.1 %, bootstrapped 23.1 %, NMOS 21.6 %, other 23.1 %.

Verdicts (every margin of results/tail_corrected.json, Table S6 and the variants) that change when each margin is divided by 1 + the upper end for its design instead of 1 + its measured tau:

- TG, no ESD, 4 K, steep (T_eff 120 K), s33.69_t0.0001|move200mV|mixed: pass -> unresolved (margin 1.16 -> 1.11)
- TG, ESD on the node, 4 K proxy, s33.69_t0.0001|full|mixed: pass -> unresolved (margin 1.16 -> 1.11)
- TG, ESD on the node, 4 K proxy, s33.69_t0.0001|fullfine|mixed: pass -> unresolved (margin 1.16 -> 1.11)
- TG, ESD on the node, 4 K proxy, s33.69_t0.0001|move200mV|mixed: pass -> unresolved (margin 1.13 -> 1.08)
- TG, ESD on the node, 4 K, tree, ESD-dominated droop, s33.69_t0.0001|full|mixed: pass -> unresolved (margin 1.16 -> 1.12)
- TG, ESD on the node, 4 K, tree, ESD-dominated droop, s33.69_t0.0001|move200mV|mixed: pass -> unresolved (margin 1.16 -> 1.12)
- NMOS, 0.3 V underdrive, W 3, 4 K proxy, s33.69_t0.0001|shared|mixed: pass -> unresolved (margin 1.41 -> 1.27)
- NMOS, 0.3 V underdrive, W 3, 4 K proxy, s33.69_t0.0001|move200mV|mixed: pass -> unresolved (margin 1.28 -> 1.16)
- TG, no ESD, W 3, 4 K, tree, ESD-dominated droop, s33.69_t0.001|full|mixed: pass -> unresolved (margin 1.13 -> 1.08)
- bootstrapped (transistor level), 0.3 V underdrive, 300 K, s33.69_t0.0001|shared|mixed: pass -> unresolved (margin 1.66 -> 1.48)
- TG, no ESD, 300 K, s33.69_t0.0001|shared|mixed: unresolved -> fail (margin 0.868 -> 0.776)
- TG, no ESD, 77 K proxy, s33.69_t0.0001|move200mV|mixed: pass -> unresolved (margin 1.14 -> 1.1)
- TG, no ESD, 4 K high, s33.69_t0.0001|move200mV|mixed: unresolved -> fail (margin 0.91 -> 0.846)
- TG, ESD on the node, 4 K, tree, one reticle, s33.69_t0.0001|full|mixed: pass -> unresolved (margin 1.16 -> 1.12)
- TG, ESD on the node, 4 K, tree, one reticle, s33.69_t0.0001|move200mV|mixed: pass -> unresolved (margin 1.16 -> 1.12)
- bootstrapped (transistor level), 0.3 V underdrive, 4 K, steep (T_eff 30 K), s33.69_t0.0001|full|mixed: pass -> unresolved (margin 1.23 -> 1.1)
- bootstrapped (transistor level), 0.3 V underdrive, 4 K, steep (T_eff 30 K), s33.69_t0.0001|shared|mixed: unresolved -> fail (margin 0.759 -> 0.677)
- bootstrapped (transistor level), 0.3 V underdrive, 4 K, mismatch x 1.5, s33.69_t0.001|shared|mixed: pass -> unresolved (margin 1.6 -> 1.43)
- TG + dummies, 4 K, mismatch x 1.5, s33.69_t0.001|shared|mixed: pass -> unresolved (margin 1.44 -> 1.29)
- bootstrapped (transistor level), 0.3 V underdrive, 4 K, tree, ESD diodes on 1 pF, s33.69_t0.001|shared|mixed: pass -> unresolved (margin 1.48 -> 1.32)
- D TG, 300 K, s33.69_t0.0001|shared|mixed: unresolved -> fail (margin 0.914 -> 0.815)
- bootstrapped (transistor level), 0.3 V underdrive, 4 K, buffered leaf line, s33.69_t0.001|shared|mixed: pass -> unresolved (margin 1.6 -> 1.43)

1908 verdicts checked.
