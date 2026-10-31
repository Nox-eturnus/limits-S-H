## Probability that an array of 10^6 channels has a channel above the budget

Strictest point (99.99 %, 33.69 dec/V, untracked), levels set open-loop. P(array) from the union bound (an upper bound); 'boot 95 %' is its 95th percentile over 300 bootstrap resamples of the channels. 'closed margin' is the margin at which P(array) = 1/2, against the median worst channel of residual6.py.

| design | condition | n | margin (residual6) | closed margin | P(array), per-channel line | boot 95 % | mismatch x 1.5 | mismatch x 2 | curvature x 1.3 | mismatch x 2, curvature x 1.3 | P(array), shared line |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D BOOT | 300 K | 20 | 229.22 | 229.31 | 0 | 0 | 0 | 0 | 0 | 0 | 2.2e-48 |
| D CLK | 300 K | 20 | 2.29 | 2.29 | 0 | 0 | 0 | 0 | 0 | 0 | 5.2e-36 |
| D NSW | 300 K | 20 | 18.10 | 18.10 | 0 | 0 | 0 | 0 | 0 | 0 | 2.1e-92 |
| D NTB | 300 K | 20 | 4.16 | 4.17 | 0 | 1.2e-290 | 8.1e-178 | 2.1e-98 | 0 | 6.8e-90 | 1.9e-03 |
| D TGD | 300 K | 20 | 8.40 | 8.39 | 0 | 0 | 1.6e-213 | 1.7e-118 | 0 | 2.8e-117 | 1.00 |
| D TGH | 300 K | 20 | 1.12 | 1.12 | 1.6e-89 | 4.3e-61 | 1.2e-37 | 2.1e-19 | 1.00 | 1.00 | 1.00 |
| D TG | 300 K | 20 | 1.20 | 1.20 | 1.7e-153 | 1.2e-100 | 3.9e-66 | 1.7e-35 | 1.00 | 1.00 | 0.40 |
| D TSWB | 300 K | 20 | 8.23 | 8.23 | 0 | 0 | 4.9e-292 | 1.1e-162 | 0 | 2.6e-160 | 1.00 |
| D TSW | 300 K | 20 | 8.29 | 8.30 | 0 | 0 | 1.7e-292 | 5.8e-163 | 0 | 1.3e-160 | 1.00 |
| NMOS, 0.3 V underdrive, W 1 | 4 K proxy | 20 | 13.39 | 13.40 | 0 | 0 | 0 | 0 | 0 | 0 | 1.2e-72 |
| NMOS, 0.3 V underdrive, W 1 | 4 K, tree, ESD-dominated droop | 20 | 7.55 | 7.55 | 0 | 0 | 0 | 0 | 0 | 0 | 3.2e-82 |
| NMOS, 0.3 V underdrive, W 3 | 4 K proxy | 20 | 2.35 | 2.35 | 0 | 0 | 0 | 0 | 0 | 0 | 5.8e-13 |
| NMOS, 0.3 V underdrive, W 3 | 4 K, tree, ESD-dominated droop | 20 | 3.79 | 3.79 | 0 | 0 | 0 | 0 | 0 | 0 | 1.3e-28 |
| NMOS, 0.3 V underdrive | 300 K | 20 | 31.66 | 31.65 | 0 | 0 | 0 | 0 | 0 | 0 | 2.6e-263 |
| NMOS, 0.3 V underdrive | 4 K high | 20 | 25.23 | 25.23 | 0 | 0 | 0 | 0 | 0 | 0 | 2.3e-315 |
| NMOS, 0.3 V underdrive | 4 K proxy | 20 | 31.89 | 31.87 | 0 | 0 | 0 | 0 | 0 | 0 | 4.0e-301 |
| NMOS, 0.3 V underdrive | 4 K, Beall pMOS | 20 | 31.87 | 31.87 | 0 | 0 | 0 | 0 | 0 | 0 | 4.0e-301 |
| NMOS, 0.3 V underdrive | 4 K, clock edge 600 ps | 20 | 34.32 | 34.32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NMOS, 0.3 V underdrive | 4 K, clock edge 67 ps | 20 | 30.98 | 30.98 | 0 | 0 | 0 | 0 | 0 | 0 | 1.0e-291 |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 1.5 | 20 | 29.83 | 29.80 | 0 | 0 | 0 | 0 | 0 | 0 | 2.7e-129 |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 2 | 20 | 67.73 | 67.80 | 0 | 0 | 0 | 0 | 0 | 0 | 9.2e-71 |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 2.5 | 20 | 63.30 | 63.26 | 0 | 0 | 0 | 0 | 0 | 0 | 6.4e-43 |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 3 | 20 | 59.14 | 59.16 | 0 | 0 | 0 | 0 | 0 | 0 | 6.7e-28 |
| NMOS, 0.3 V underdrive | 4 K, mismatch x 5.3 | 20 | 265.59 | 265.28 | 0 | 0 | 0 | 0 | 0 | 0 | 4.1e-05 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 20 | 101.20 | 101.23 | 0 | 0 | 0 | 0 | 0 | 0 | 4.1e-250 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 20 | 325.80 | 325.76 | 0 | 0 | 0 | 0 | 0 | 0 | 6.7e-230 |
| NMOS, 0.3 V underdrive | 4 K, steep (T_eff 30 K) | 20 | 169.03 | 169.00 | 0 | 0 | 0 | 0 | 0 | 0 | 6.9e-231 |
| NMOS, 0.3 V underdrive | 4 K, tree source | 20 | 34.44 | 34.45 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NMOS, 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 20 | 34.44 | 34.45 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NMOS, 0.3 V underdrive | 4 K, tree, one reticle | 20 | 34.45 | 34.45 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NMOS, 0.3 V underdrive | 77 K Beall fit | 20 | 18.71 | 18.71 | 0 | 0 | 0 | 0 | 0 | 0 | 1.8e-279 |
| NMOS, 0.3 V underdrive | 77 K proxy | 20 | 41.18 | 41.18 | 0 | 0 | 0 | 0 | 0 | 0 | 5.3e-289 |
| T-switch + OTA buffer, W 0.42 | 4 K proxy | 20 | 7.82 | 7.83 | 0 | 0 | 5.9e-203 | 1.5e-112 | 0 | 7.4e-111 | 1.00 |
| T-switch + OTA buffer, W 0.42 | 4 K, tree, ESD-dominated droop | 20 | 12.26 | 12.29 | 0 | 0 | 0 | 9.0e-213 | 0 | 3.3e-212 | 1.00 |
| T-switch + OTA buffer | 300 K | 20 | 10.25 | 10.25 | 0 | 0 | 0 | 1.6e-208 | 0 | 5.9e-206 | 1.00 |
| T-switch + OTA buffer | 4 K high | 20 | 5.54 | 5.53 | 0 | 1.5e-262 | 3.2e-164 | 9.5e-91 | 0 | 5.6e-90 | 1.00 |
| T-switch + OTA buffer | 4 K proxy | 20 | 5.42 | 5.39 | 0 | 2.3e-255 | 1.2e-178 | 8.5e-99 | 0 | 4.0e-94 | 1.00 |
| T-switch + OTA buffer | 4 K, Beall pMOS | 20 | 6.24 | 6.23 | 0 | 1.0e-287 | 1.8e-174 | 1.6e-96 | 0 | 1.6e-93 | 1.00 |
| T-switch + OTA buffer | 4 K, steep (T_eff 120 K) | 20 | 2.91 | 2.90 | 4.5e-53 | 2.4e-40 | 2.2e-21 | 3.2e-10 | 8.5e-51 | 1.2e-09 | 1.00 |
| T-switch + OTA buffer | 4 K, tree, ESD-dominated droop | 20 | 5.98 | 5.99 | 1.3e-258 | 1.2e-176 | 8.8e-113 | 1.2e-61 | 1.6e-258 | 1.2e-61 | 1.00 |
| T-switch + OTA buffer | 4 K, tree, one reticle | 20 | 7.53 | 7.53 | 0 | 1.0e-230 | 4.2e-140 | 3.6e-77 | 4.9e-318 | 9.3e-77 | 1.00 |
| T-switch + OTA buffer | 77 K Beall fit | 20 | 6.16 | 6.16 | 0 | 1.8e-312 | 5.7e-196 | 1.3e-108 | 0 | 9.6e-105 | 1.00 |
| T-switch + OTA buffer | 77 K proxy | 20 | 5.04 | 5.05 | 0 | 2.1e-226 | 7.9e-167 | 3.5e-92 | 0 | 3.4e-87 | 1.00 |
| TG + dummies, W 0.84 | 4 K proxy | 20 | 3.90 | 3.90 | 5.2e-98 | 5.7e-55 | 2.0e-41 | 1.5e-21 | 1.8e-95 | 6.5e-21 | 1.00 |
| TG + dummies, W 0.84 | 4 K, tree, ESD-dominated droop | 20 | 4.11 | 4.10 | 9.5e-101 | 1.2e-60 | 1.2e-42 | 3.1e-22 | 6.7e-99 | 9.0e-22 | 1.00 |
| TG + dummies | 300 K | 20 | 7.37 | 7.38 | 0 | 3.1e-252 | 5.7e-162 | 2.3e-89 | 0 | 2.0e-88 | 1.00 |
| TG + dummies | 4 K high | 20 | 4.97 | 4.94 | 2.1e-145 | 9.8e-110 | 1.6e-62 | 1.8e-33 | 1.0e-143 | 4.9e-33 | 1.00 |
| TG + dummies | 4 K proxy | 20 | 5.25 | 5.11 | 7.0e-165 | 7.6e-123 | 3.4e-71 | 2.4e-38 | 2.4e-162 | 1.0e-37 | 1.00 |
| TG + dummies | 4 K, Beall pMOS | 20 | 8.34 | 8.35 | 0 | 0 | 1.9e-223 | 4.3e-124 | 0 | 1.8e-122 | 2.1e-16 |
| TG + dummies | 4 K, clock edge 600 ps | 20 | 5.57 | 5.52 | 2.8e-171 | 7.0e-122 | 4.8e-74 | 6.0e-40 | 4.9e-170 | 1.2e-39 | 1.00 |
| TG + dummies | 4 K, clock edge 67 ps | 20 | 4.97 | 4.95 | 3.0e-162 | 3.4e-115 | 5.0e-70 | 1.1e-37 | 3.5e-159 | 6.4e-37 | 1.00 |
| TG + dummies | 4 K, mismatch x 1.5 | 20 | 3.73 | 3.69 | 6.9e-74 | 6.7e-53 | 1.2e-30 | 2.0e-15 | 3.8e-73 | 3.0e-15 | 1.00 |
| TG + dummies | 4 K, mismatch x 2 | 20 | 2.90 | 2.86 | 1.4e-41 | 6.2e-27 | 4.9e-16 | 5.8e-07 | 2.0e-41 | 6.0e-07 | 1.00 |
| TG + dummies | 4 K, steep (T_eff 120 K) | 20 | 3.03 | 3.02 | 1.5e-51 | 6.9e-36 | 1.1e-20 | 7.7e-10 | 3.2e-50 | 1.7e-09 | 1.00 |
| TG + dummies | 4 K, steep (T_eff 20 K) | 20 | 2.68 | 2.68 | 6.0e-40 | 3.2e-28 | 1.6e-15 | 6.7e-07 | 1.3e-38 | 1.5e-06 | 1.00 |
| TG + dummies | 4 K, steep (T_eff 30 K) | 20 | 2.71 | 2.70 | 1.2e-40 | 4.3e-28 | 8.0e-16 | 4.5e-07 | 2.6e-39 | 9.7e-07 | 1.00 |
| TG + dummies | 4 K, tree source | 20 | 5.62 | 5.59 | 2.0e-171 | 1.4e-120 | 4.1e-74 | 5.6e-40 | 1.5e-170 | 9.1e-40 | 1.00 |
| TG + dummies | 4 K, tree, ESD-dominated droop | 20 | 5.61 | 5.59 | 2.0e-171 | 4.1e-124 | 4.1e-74 | 5.6e-40 | 1.5e-170 | 9.1e-40 | 1.00 |
| TG + dummies | 4 K, tree, one reticle | 20 | 5.63 | 5.59 | 2.0e-171 | 2.3e-123 | 4.1e-74 | 5.6e-40 | 1.5e-170 | 9.2e-40 | 1.00 |
| TG + dummies | 77 K Beall fit | 20 | 5.94 | 5.94 | 7.5e-216 | 1.7e-162 | 6.9e-94 | 3.9e-51 | 2.2e-213 | 1.6e-50 | 4.7e-17 |
| TG + dummies | 77 K proxy | 20 | 5.38 | 5.40 | 6.0e-185 | 7.3e-126 | 3.9e-80 | 2.2e-43 | 3.6e-182 | 1.1e-42 | 1.00 |
| TG, ESD on the node | 300 K | 20 | 1.20 | 1.20 | 1.7e-153 | 1.4e-101 | 3.9e-66 | 1.7e-35 | 1.00 | 1.00 | 0.40 |
| TG, ESD on the node | 4 K high | 20 | 1.32 | 1.32 | 7.6e-169 | 3.6e-91 | 5.8e-73 | 2.4e-39 | 8.2e-11 | 1.00 | 1.00 |
| TG, ESD on the node | 4 K proxy | 100 | 1.27 | 1.27 | 5.1e-130 | 9.4e-105 | 1.1e-55 | 1.4e-29 | 1.00 | 1.00 | 1.00 |
| TG, ESD on the node | 4 K, Beall pMOS | 20 | 37.76 | 37.76 | 0 | 0 | 0 | 0 | 0 | 0 | 1.8e-104 |
| TG, ESD on the node | 4 K, steep (T_eff 120 K) | 20 | 1.38 | 1.38 | 1.0e-74 | 2.4e-44 | 4.9e-31 | 1.1e-15 | 4.5e-16 | 0.56 | 0.74 |
| TG, ESD on the node | 4 K, tree, ESD-dominated droop | 20 | 1.27 | 1.27 | 9.4e-194 | 3.2e-104 | 4.7e-84 | 1.4e-45 | 1.00 | 1.00 | 1.00 |
| TG, ESD on the node | 4 K, tree, one reticle | 20 | 1.27 | 1.27 | 9.6e-194 | 2.5e-100 | 4.8e-84 | 1.4e-45 | 1.00 | 1.00 | 1.00 |
| TG, ESD on the node | 77 K Beall fit | 20 | 11.73 | 11.73 | 0 | 0 | 0 | 0 | 0 | 0 | 9.5e-96 |
| TG, ESD on the node | 77 K proxy | 20 | 1.35 | 1.35 | 2.9e-201 | 5.5e-130 | 2.2e-87 | 1.8e-47 | 5.2e-23 | 0.01 | 1.00 |
| TG, no ESD, W 0.42, 0.3 V underdrive | 4 K proxy | 20 | 2.75 | 2.75 | 0 | 0 | 0 | 1.3e-237 | 0 | 5.8e-192 | 2.0e-07 |
| TG, no ESD, W 0.42, 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 20 | 2.77 | 2.77 | 0 | 0 | 0 | 9.3e-248 | 0 | 2.0e-199 | 9.1e-08 |
| TG, no ESD, W 0.42 | 4 K proxy | 20 | 2.76 | 2.76 | 0 | 0 | 0 | 3.3e-239 | 0 | 2.6e-193 | 1.7e-07 |
| TG, no ESD, W 0.42 | 4 K, tree, ESD-dominated droop | 20 | 2.78 | 2.78 | 0 | 0 | 0 | 4.0e-249 | 0 | 1.3e-200 | 7.9e-08 |
| TG, no ESD, W 3 | 4 K proxy | 20 | 0.38 | 0.38 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| TG, no ESD, W 3 | 4 K, tree, ESD-dominated droop | 20 | 0.39 | 0.39 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| TG, no ESD | 300 K | 20 | 1.07 | 1.07 | 1.6e-31 | 3.4e-18 | 9.7e-12 | 9.2e-05 | 1.00 | 1.00 | 1.00 |
| TG, no ESD | 4 K high | 20 | 1.04 | 1.04 | 9.5e-12 | 0.01 | 7.3e-03 | 1.00 | 1.00 | 1.00 | 1.00 |
| TG, no ESD | 4 K proxy | 100 | 1.12 | 1.12 | 6.8e-70 | 2.7e-51 | 8.0e-29 | 2.4e-14 | 1.00 | 1.00 | 1.00 |
| TG, no ESD | 4 K, Beall pMOS | 20 | 2.24 | 2.24 | 0 | 0 | 0 | 0 | 0 | 1.8e-224 | 9.2e-43 |
| TG, no ESD | 4 K, steep (T_eff 120 K) | 20 | 1.24 | 1.24 | 2.0e-37 | 2.9e-21 | 2.2e-14 | 2.9e-06 | 1.00 | 1.00 | 1.00 |
| TG, no ESD | 4 K, tree, ESD-dominated droop | 20 | 1.12 | 1.12 | 3.0e-55 | 2.5e-27 | 2.4e-22 | 9.0e-11 | 1.00 | 1.00 | 1.00 |
| TG, no ESD | 4 K, tree, one reticle | 20 | 1.12 | 1.12 | 3.0e-55 | 8.5e-27 | 2.4e-22 | 8.9e-11 | 1.00 | 1.00 | 1.00 |
| TG, no ESD | 77 K Beall fit | 20 | 2.22 | 2.22 | 0 | 0 | 5.8e-238 | 2.9e-132 | 0 | 8.8e-91 | 7.2e-36 |
| TG, no ESD | 77 K proxy | 20 | 1.19 | 1.19 | 4.7e-92 | 8.0e-53 | 9.2e-39 | 4.7e-20 | 1.00 | 1.00 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 300 K | 20 | 11.61 | 11.62 | 0 | 0 | 0 | 0 | 0 | 0 | 9.0e-14 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K high | 20 | 2.84 | 2.84 | 0 | 0 | 2.9e-213 | 2.3e-118 | 0 | 7.7e-96 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K proxy | 100 | 2.84 | 2.82 | 0 | 1.6e-291 | 6.5e-157 | 1.2e-86 | 8.7e-294 | 1.1e-70 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, Beall pMOS | 20 | 6.02 | 6.01 | 0 | 0 | 0 | 0 | 0 | 0 | 8.5e-03 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, buffered leaf line | 20 | 2.42 | 2.42 | 5.4e-248 | 1.1e-164 | 3.5e-108 | 3.4e-59 | 4.4e-191 | 6.4e-45 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 600 ps | 20 | 2.58 | 2.58 | 0 | 4.8e-195 | 3.9e-145 | 5.3e-80 | 4.1e-261 | 1.8e-62 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 67 ps | 20 | 3.42 | 3.42 | 0 | 0 | 0 | 0 | 0 | 0 | 0.65 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, mismatch x 1.5 | 20 | 2.65 | 2.65 | 5.2e-191 | 1.0e-115 | 7.8e-83 | 6.6e-45 | 1.7e-157 | 1.7e-36 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, mismatch x 2 | 20 | 2.40 | 2.40 | 2.9e-103 | 4.1e-64 | 9.2e-44 | 7.1e-23 | 1.1e-84 | 3.4e-18 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 120 K) | 20 | 2.21 | 2.21 | 3.2e-195 | 3.6e-128 | 1.1e-84 | 5.8e-46 | 6.1e-143 | 7.7e-33 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 20 K) | 20 | 1.31 | 1.31 | 2.0e-23 | 8.7e-14 | 4.1e-08 | 0.01 | 8.2e-05 | 1.00 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 30 K) | 20 | 1.35 | 1.35 | 3.2e-71 | 7.1e-41 | 1.8e-29 | 8.4e-15 | 2.0e-11 | 1.00 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree source | 20 | 2.33 | 2.33 | 8.3e-213 | 2.3e-140 | 1.6e-92 | 2.3e-50 | 1.5e-161 | 1.6e-37 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, ESD diodes on 1 pF | 20 | 2.37 | 2.38 | 5.2e-233 | 8.7e-150 | 1.6e-101 | 1.9e-55 | 3.2e-178 | 1.1e-41 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, ESD-dominated droop | 20 | 2.32 | 2.32 | 1.5e-206 | 1.8e-130 | 9.4e-90 | 8.3e-49 | 1.7e-156 | 3.0e-36 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, one reticle | 20 | 2.22 | 2.22 | 5.3e-163 | 1.0e-100 | 2.3e-70 | 7.0e-38 | 1.1e-121 | 1.7e-27 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K Beall fit | 20 | 6.32 | 6.31 | 0 | 0 | 0 | 0 | 0 | 3.9e-303 | 1.00 |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K proxy | 20 | 3.97 | 3.97 | 0 | 0 | 0 | 1.2e-206 | 0 | 1.7e-183 | 0.87 |
| bootstrapped (transistor level), W 1 | 4 K proxy | 20 | 1.60 | 1.60 | 6.3e-89 | 8.0e-58 | 2.3e-37 | 2.9e-19 | 2.9e-42 | 1.7e-07 | 1.00 |
| bootstrapped (transistor level), W 1 | 4 K, tree, ESD-dominated droop | 20 | 1.11 | 1.11 | 2.0e-09 | 7.1e-05 | 0.08 | 1.00 | 1.00 | 1.00 | 1.00 |

### Verdicts that change under the near-one rule (widened interval reaches one)

| design | condition | point | calibration | margin [90 %] | widening | class | with widening |
|---|---|---|---|---|---|---|---|
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 120 K) | s33.69_t0.0001 | shared | 0.87 [0.71, 1.29] | 5.3 % | indeterminate | near one |
| TG, no ESD | 4 K, steep (T_eff 120 K) | s33.69_t0.0001 | shared | 0.88 [0.76, 1.07] | 1.4 % | indeterminate | near one |
| TG, ESD on the node | 4 K, steep (T_eff 120 K) | s33.69_t0.0001 | shared | 0.99 [0.86, 1.20] | 1.4 % | indeterminate | near one |
| T-switch + OTA buffer | 4 K, steep (T_eff 120 K) | s33.69_t0.001 | shared | 1.19 [1.00, 1.55] | 5.3 % | indeterminate | near one |
| TG, ESD on the node | 4 K, tree, ESD-dominated droop | s33.69_t0.0001 | shared | 0.91 [0.82, 1.08] | 1.4 % | indeterminate | near one |
| bootstrapped (transistor level), W 1 | 4 K, tree, ESD-dominated droop | s33.69_t0.001 | shared | 0.86 [0.63, 1.56] | 5.3 % | indeterminate | near one |
| TG + dummies, W 0.84 | 4 K proxy | s33.69_t0.0001 | shared | 0.64 [0.49, 1.15] | 5.3 % | indeterminate | near one |
| TG + dummies, W 0.84 | 4 K, tree, ESD-dominated droop | s33.69_t0.0001 | shared | 0.64 [0.48, 1.22] | 5.3 % | indeterminate | near one |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K proxy | s33.69_t0.0001 | shared | 0.96 [0.79, 1.55] | 5.3 % | indeterminate | near one |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K high | s33.69_t0.0001 | shared | 0.85 [0.68, 1.24] | 5.3 % | indeterminate | near one |
| bootstrapped (transistor level), 0.3 V underdrive | 77 K Beall fit | s33.69_t0.0001 | shared | 0.90 [0.70, 1.33] | 5.3 % | indeterminate | near one |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, Beall pMOS | s33.69_t0.0001 | shared | 1.16 [0.90, 1.69] | 5.3 % | indeterminate | near one |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, tree, one reticle | s33.69_t0.001 | shared | 1.16 [0.84, 2.50] | 5.3 % | indeterminate | near one |
| T-switch + OTA buffer | 300 K | s33.69_t0.001 | shared | 1.20 [1.01, 1.63] | 5.3 % | pass | near one |
| T-switch + OTA buffer | 77 K proxy | s33.69_t0.001 | shared | 1.23 [1.04, 1.64] | 5.3 % | pass | near one |
| T-switch + OTA buffer | 77 K Beall fit | s33.69_t0.001 | shared | 1.23 [1.03, 1.62] | 5.3 % | pass | near one |
| T-switch + OTA buffer | 4 K, Beall pMOS | s33.69_t0.001 | shared | 1.26 [1.05, 1.71] | 5.3 % | pass | near one |
| TG, no ESD | 4 K high | s33.69_t0.0001 | full | 1.04 [1.01, 1.07] | 1.4 % | pass | near one |
| TG, ESD on the node | 300 K | s33.69_t0.0001 | shared | 1.00 [0.88, 1.07] | 1.4 % | indeterminate | near one |
| TG, ESD on the node | 77 K proxy | s33.69_t0.0001 | shared | 0.93 [0.82, 1.12] | 1.4 % | indeterminate | near one |
| TG, ESD on the node | 4 K high | s33.69_t0.0001 | shared | 0.95 [0.85, 1.11] | 1.4 % | indeterminate | near one |
| TG, ESD on the node | 4 K, tree, one reticle | s33.69_t0.0001 | shared | 0.91 [0.80, 1.07] | 1.4 % | indeterminate | near one |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 30 K) | s33.69_t0.0001 | shared | 0.83 [0.74, 1.02] | 5.3 % | indeterminate | near one |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, steep (T_eff 20 K) | s33.69_t0.0001 | shared | 0.92 [0.81, 1.11] | 5.3 % | indeterminate | near one |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 600 ps | s33.69_t0.0001 | shared | 0.79 [0.63, 1.17] | 5.3 % | indeterminate | near one |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, clock edge 67 ps | s33.69_t0.0001 | shared | 0.98 [0.78, 1.39] | 5.3 % | indeterminate | near one |
| bootstrapped (transistor level), 0.3 V underdrive | 4 K, mismatch x 2 | s33.69_t0.001 | shared | 1.23 [0.98, 1.99] | 5.3 % | indeterminate | near one |
| TG + dummies | 4 K, mismatch x 2 | s33.69_t0.001 | shared | 1.20 [1.05, 1.50] | 5.3 % | pass | near one |
| D TG | 300 K | s33.69_t0.0001 | shared | 1.00 [0.87, 1.08] | 5.3 % | indeterminate | near one |
| D TSW | 300 K | s33.69_t0.001 | shared | 1.02 [0.88, 1.30] | 5.3 % | indeterminate | near one |
| D TSWB | 300 K | s33.69_t0.001 | shared | 1.01 [0.87, 1.30] | 5.3 % | indeterminate | near one |
| D NTB | 300 K | s33.69_t0.0001 | shared | 1.21 [1.00, 1.71] | 5.3 % | pass | near one |
