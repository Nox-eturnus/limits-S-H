# A separate hold array of 10^6 cells packed at the 22 um pitch

Cells cover 484 mm^2 of the 858 mm^2 reticle. Earlier estimate (whole reticle): mean 14.8 mm, largest 29.5 mm.

| layers | qubit region (mm) | outer side (mm) | mean (mm) | largest (mm) |
|---|---|---|---|---|
| 4 | 12.5 | 25.3 | 14.7 | 25.3 |
| 6 | 8.3 | 23.5 | 12.8 | 23.5 |
| 10 | 5.0 | 22.6 | 11.7 | 22.5 |

Connection 2.35 to 4.42 pF, k 0.185 to 0.299; R 29 to 37 kohm, tau 34 to 81 ns, widening line x0.38 to x0.66.

| s (dec/V) | swing (V) | bound, 10 us rounds (mW) | coldest stage |
|---|---|---|---|
| 3.87 | 2.25 to 3.64 | 202.8 to 617.4 | 4.2 K / 4.2 K |
| 10 | 0.87 to 1.41 | 30.4 to 92.5 | 1.2 K / 4.2 K |
| 16.6 | 0.52 to 0.85 | 11.0 to 33.6 | 1.2 K / 1.2 K |
| 33.69 | 0.26 to 0.42 | 2.7 to 8.1 | 1.2 K / 1.2 K |

Coupling of adjacent connections: unshielded 587 to 1473 fF, shielded 5.9 to 74 fF.
- target 0.0001: limit 3.8 to 12.8 fF; compensation shielded 5.2% to 217%, unshielded 0.26% to 2.17% (above 100 %: none needed)
- target 0.001: limit 12.1 to 39.8 fF; compensation shielded 16.5% to 678%, unshielded 0.82% to 6.78% (above 100 %: none needed)
