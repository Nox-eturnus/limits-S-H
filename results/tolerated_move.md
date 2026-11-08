# Largest tolerated move from a tuned level

## A. Designs of Figure 6 and GF180 (worst of 10^6, per-channel line, tail-corrected; 90 % bootstrap interval)

| condition | window (V) | 99.99 %, 33.69 dec/V: Delta_max (mV) [90 %] | margin at 1 mV | 99.9 %: Delta_max (mV) [90 %] |
|---|---|---|---|---|
| NMOS, 0.3 V underdrive|300 K | 0.6 | 600 (whole window) [600, 600] | 1.48e+03 | 600 (whole window) [600, 600] |
| NMOS, 0.3 V underdrive|77 K proxy | 0.5 | 500 (whole window) [500, 500] | 1.67e+03 | 500 (whole window) [500, 500] |
| NMOS, 0.3 V underdrive|4 K proxy | 0.5 | 500 (whole window) [500, 500] | 1.32e+03 | 500 (whole window) [500, 500] |
| NMOS, 0.3 V underdrive|4 K high | 0.5 | 500 (whole window) [500, 500] | 1.03e+03 | 500 (whole window) [500, 500] |
| NMOS, 0.3 V underdrive|77 K Beall fit | 0.6 | 600 (whole window) [600, 600] | 876 | 600 (whole window) [600, 600] |
| NMOS, 0.3 V underdrive|4 K, Beall pMOS | 0.5 | 500 (whole window) [500, 500] | 1.29e+03 | 500 (whole window) [500, 500] |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 120 K) | 0.5 | 500 (whole window) [500, 500] | 4.2e+03 | 500 (whole window) [500, 500] |
| NMOS, 0.3 V underdrive|4 K, tree, ESD-dominated droop | 0.5 | 500 (whole window) [500, 500] | 1.38e+03 | 500 (whole window) [500, 500] |
| NMOS, 0.3 V underdrive|4 K, tree, one reticle | 0.5 | 500 (whole window) [500, 500] | 1.38e+03 | 500 (whole window) [500, 500] |
| bootstrapped (transistor level), 0.3 V underdrive|300 K | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 646 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| bootstrapped (transistor level), 0.3 V underdrive|77 K proxy | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 214 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| bootstrapped (transistor level), 0.3 V underdrive|4 K proxy | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 156 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| bootstrapped (transistor level), 0.3 V underdrive|4 K high | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 155 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| bootstrapped (transistor level), 0.3 V underdrive|77 K Beall fit | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 313 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, Beall pMOS | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 307 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 120 K) | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 105 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, ESD-dominated droop | 1.2 | 1.2e+03 (whole window) [400, 1.2e+03] | 125 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, tree, one reticle | 1.2 | 400 [200, 1.2e+03] | 121 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| T-switch + OTA buffer|300 K | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 398 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| T-switch + OTA buffer|77 K proxy | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 189 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| T-switch + OTA buffer|4 K proxy | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 207 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| T-switch + OTA buffer|4 K high | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 222 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| T-switch + OTA buffer|77 K Beall fit | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 270 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| T-switch + OTA buffer|4 K, Beall pMOS | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 277 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| T-switch + OTA buffer|4 K, steep (T_eff 120 K) | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 104 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| T-switch + OTA buffer|4 K, tree, ESD-dominated droop | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 273 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| T-switch + OTA buffer|4 K, tree, one reticle | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 371 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|300 K | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 286 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|77 K proxy | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 252 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|4 K proxy | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 246 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|4 K high | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 246 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|77 K Beall fit | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 507 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|4 K, Beall pMOS | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 499 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|4 K, steep (T_eff 120 K) | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 198 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|4 K, tree, ESD-dominated droop | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 274 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|4 K, tree, one reticle | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 274 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, no ESD|300 K | 1.2 | 175 [171, 181] | 63.5 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, no ESD|77 K proxy | 1.2 | 198 [195, 200] | 71 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, no ESD|4 K proxy | 1.2 | 169 [167, 170] | 61.3 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, no ESD|4 K high | 1.2 | 154 [152, 157] | 56.5 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, no ESD|77 K Beall fit | 1.2 | 400 [400, 400] | 139 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, no ESD|4 K, Beall pMOS | 1.2 | 200 [200, 200] | 125 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, no ESD|4 K, steep (T_eff 120 K) | 1.2 | 200 [193, 200] | 71.9 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, no ESD|4 K, tree, ESD-dominated droop | 1.2 | 174 [172, 178] | 63.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, no ESD|4 K, tree, one reticle | 1.2 | 174 [172, 178] | 63.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, ESD on the node|300 K | 1.2 | 183 [179, 189] | 66.1 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, ESD on the node|77 K proxy | 1.2 | 200 [200, 200] | 80.7 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, ESD on the node|4 K proxy | 1.2 | 194 [193, 196] | 69.8 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, ESD on the node|4 K high | 1.2 | 172 [169, 175] | 62.3 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, ESD on the node|77 K Beall fit | 0.6 | 600 (whole window) [600, 600] | 361 | 600 (whole window) [600, 600] |
| TG, ESD on the node|4 K, Beall pMOS | 0.4 | 400 (whole window) [400, 400] | 1.42e+03 | 400 (whole window) [400, 400] |
| TG, ESD on the node|4 K, steep (T_eff 120 K) | 1.2 | 200 [200, 200] | 80.5 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, ESD on the node|4 K, tree, ESD-dominated droop | 1.2 | 200 [198, 200] | 72 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, ESD on the node|4 K, tree, one reticle | 1.2 | 200 [199, 200] | 72 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 NMOS, 0.3 V underdrive|300 K | 0.6 | 600 (whole window) [600, 600] | 6.18e+03 | 600 (whole window) [600, 600] |
| GF180 NMOS, 0.3 V underdrive|4 K proxy | 0.6 | 600 (whole window) [600, 600] | 6.18e+03 | 600 (whole window) [600, 600] |
| GF180 NMOS, 0.3 V underdrive|4 K high | 0.6 | 600 (whole window) [600, 600] | 6.18e+03 | 600 (whole window) [600, 600] |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|300 K | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 1.83e+03 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|4 K proxy | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 718 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 bootstrapped (transistor level), 0.3 V underdrive|4 K high | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 738 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 TG + dummies|300 K | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 218 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 TG + dummies|4 K proxy | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 230 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 TG + dummies|4 K high | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 206 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 TG, no ESD|300 K | 1.2 | 94.9 [94.2, 95.8] | 36.1 | 200 [200, 200] |
| GF180 TG, no ESD|4 K proxy | 1.2 | 85.6 [85.5, 85.7] | 32.8 | 200 [200, 200] |
| GF180 TG, no ESD|4 K high | 1.2 | 85.7 [85.5, 85.9] | 32.9 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|300 K | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 3.1e+03 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|4 K proxy | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 3.1e+03 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V|4 K high | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 3.1e+03 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 TG, no ESD, W 0.42|300 K | 1.2 | 200 [200, 200] | 88.5 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 TG, no ESD, W 0.42|4 K proxy | 1.2 | 200 [200, 200] | 79.4 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| GF180 TG, no ESD, W 0.42|4 K high | 1.2 | 200 [200, 200] | 79.3 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 30 K) | 0.5 | 500 (whole window) [500, 500] | 6.18e+03 | 500 (whole window) [500, 500] |
| NMOS, 0.3 V underdrive|4 K, steep (T_eff 20 K) | 0.4 | 400 (whole window) [400, 400] | 6.18e+03 | 400 (whole window) [400, 400] |
| NMOS, 0.3 V underdrive|4 K, mismatch x 1.5 | 0.5 | 500 (whole window) [500, 500] | 1.21e+03 | 500 (whole window) [500, 500] |
| NMOS, 0.3 V underdrive|4 K, mismatch x 2 | 0.4 | 400 (whole window) [400, 400] | 2.31e+03 | 400 (whole window) [400, 400] |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 30 K) | 1.2 | 184 [172, 200] | 66.4 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, steep (T_eff 20 K) | 1.2 | 176 [160, 200] | 63.9 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 1.5 | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 143 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| bootstrapped (transistor level), 0.3 V underdrive|4 K, mismatch x 2 | 1.2 | 1.2e+03 (whole window) [400, 1.2e+03] | 131 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|4 K, steep (T_eff 30 K) | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 179 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|4 K, steep (T_eff 20 K) | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 177 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|4 K, mismatch x 1.5 | 1.2 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] | 178 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG + dummies|4 K, mismatch x 2 | 1.2 | 1.2e+03 (whole window) [200, 1.2e+03] | 138 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, no ESD|4 K, mismatch x 1.5 | 1.2 | 164 [161, 170] | 59.8 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |
| TG, no ESD|4 K, mismatch x 2 | 1.2 | 160 [155, 166] | 58.3 | 1.2e+03 (whole window) [1.2e+03, 1.2e+03] |

Smallest Delta_max over the SKY130 conditions (Figure 6 bands, trees, steep, mismatch) and over GF180, per design:

- GF180 NMOS, 0.3 V underdrive 99.99: 600 mV [600, 600] (300 K)
- GF180 NMOS, 0.3 V underdrive 99.9: 600 mV [600, 600] (300 K)
- GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V 99.99: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- GF180 NMOS, 0.3 V underdrive, 0.3-1.5 V 99.9: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- GF180 TG + dummies 99.99: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- GF180 TG + dummies 99.9: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- GF180 TG, no ESD 99.99: 85.6 mV [85.5, 85.7] (4 K proxy)
- GF180 TG, no ESD 99.9: 200 mV [200, 200] (300 K)
- GF180 TG, no ESD, W 0.42 99.99: 200 mV [200, 200] (300 K)
- GF180 TG, no ESD, W 0.42 99.9: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- GF180 bootstrapped (transistor level), 0.3 V underdrive 99.99: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- GF180 bootstrapped (transistor level), 0.3 V underdrive 99.9: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- NMOS, 0.3 V underdrive 99.99: 400 mV [400, 400] (4 K, steep (T_eff 20 K))
- NMOS, 0.3 V underdrive 99.9: 400 mV [400, 400] (4 K, steep (T_eff 20 K))
- T-switch + OTA buffer 99.99: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- T-switch + OTA buffer 99.9: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- TG + dummies 99.99: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- TG + dummies 99.9: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- TG, ESD on the node 99.99: 172 mV [169, 175] (4 K high)
- TG, ESD on the node 99.9: 400 mV [400, 400] (4 K, Beall pMOS)
- TG, no ESD 99.99: 154 mV [152, 157] (4 K high)
- TG, no ESD 99.9: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)
- bootstrapped (transistor level), 0.3 V underdrive 99.99: 176 mV [160, 200] (4 K, steep (T_eff 20 K))
- bootstrapped (transistor level), 0.3 V underdrive 99.9: 1.2e+03 mV [1.2e+03, 1.2e+03] (300 K)

## B. Switches sized for settling (nominal, 20 mV grid, spline)

| key | tau (ns) | Delta_max 99.99 % (mV) | Delta_max 99.9 % (mV) |
|---|---|---|---|
| TG|5|300 K | 1.52 | 41.5 | 135 |
| TG|5|4 K proxy | 1.52 | 42 | 136 |
| TG|10|300 K | 0.797 | 19 | 61.5 |
| TG|10|4 K proxy | 0.797 | 21 | 66.5 |
| TG|20|300 K | 0.436 | 8.5 | 27 |
| TG|20|4 K proxy | 0.436 | 10.5 | 33.5 |
| TG|40|300 K | 0.259 | 3.5 | 12 |
| TG|40|4 K proxy | 0.259 | 5 | 16.5 |
| TG + dummies|5|300 K | 1.53 | 1.2e+03 | 1.2e+03 |
| TG + dummies|5|4 K proxy | 1.53 | 1.2e+03 | 1.2e+03 |
| TG + dummies|10|300 K | 0.809 | 1.2e+03 | 1.2e+03 |
| TG + dummies|10|4 K proxy | 0.809 | 187 | 1.2e+03 |
| TG + dummies|20|300 K | 0.45 | 74.5 | 1.2e+03 |
| TG + dummies|20|4 K proxy | 0.45 | 66 | 240 |
| TG + dummies|40|300 K | 0.275 | 22 | 79 |
| TG + dummies|40|4 K proxy | 0.275 | 26 | 85 |
| bootstrapped|5|300 K | 0.223 | 1.2e+03 | 1.2e+03 |
| bootstrapped|5|4 K proxy | 0.223 | 1.2e+03 | 1.2e+03 |
| bootstrapped|10|300 K | 0.128 | 1.2e+03 | 1.2e+03 |
| bootstrapped|10|4 K proxy | 0.128 | 1.2e+03 | 1.2e+03 |
| bootstrapped|20|300 K | 0.0959 | 212 | 1.2e+03 |
| bootstrapped|20|4 K proxy | 0.0959 | 130 | 1.2e+03 |
| bootstrapped|40|300 K | 0.0876 | 48.5 | 196 |
| bootstrapped|40|4 K proxy | 0.0876 | 37.5 | 150 |
| NMOS|5|300 K | 0.339 | 600 | 600 |
| NMOS|5|4 K proxy | 0.339 | 142 | 600 |
| NMOS|10|300 K | 0.195 | 600 | 600 |
| NMOS|10|4 K proxy | 0.195 | 45.5 | 600 |
| NMOS|20|300 K | 0.125 | 58 | 600 |
| NMOS|20|4 K proxy | 0.125 | 19.5 | 73 |
| NMOS|40|300 K | 0.0888 | 14 | 48 |
| NMOS|40|4 K proxy | 0.0888 | 9.5 | 32.5 |
