# A whole refresh slot in SPICE, drooped 1 pF node at the far end of the path

eps = 136 µV, 1.2 V step, 60 RC segments per line; node at 1.2 V - b.

| design | droop | electrodes | b (mV) | model slot (ns) | SPICE, closed when the line settles (ns, ratio) | SPICE, closed at the model's line time (ns, ratio) |
|---|---|---|---|---|---|---|
| NMOS, 0.3 V underdrive | ESD-dominated on 1 pF, 46.5 mV/s | 1.3e+05 | 2.44 | 400.7 | 406.2 (1.014) | 468.4 (1.169) |
| NMOS, 0.3 V underdrive | reference, 3.1 mV/s | 6.8e+05 | 2.44 | 1160 | 1129 (0.973) | 1295 (1.117) |
| bootstrapped (transistor level), 0.3 V underdrive | ESD-dominated on 1 pF, 46.5 mV/s | 1.2e+05 | 2.39 | 429 | 441 (1.028) | 502.7 (1.172) |
| bootstrapped (transistor level), 0.3 V underdrive | reference, 3.1 mV/s | 6.5e+05 | 2.39 | 1189 | 1163 (0.978) | 1330 (1.119) |
| T-switch + OTA buffer | ESD-dominated on 1 pF, 46.5 mV/s | 1.2e+05 | 2.42 | 426.4 | 428.8 (1.006) | 493.8 (1.158) |
| T-switch + OTA buffer | reference, 3.1 mV/s | 6.5e+05 | 2.42 | 1201 | 1171 (0.975) | 1349 (1.123) |
| TG + dummies | ESD-dominated on 1 pF, 46.5 mV/s | 7.5e+04 | 2.44 | 696.8 | 654.1 (0.939) | 743.6 (1.067) |
| TG + dummies | reference, 3.1 mV/s | 4.5e+05 | 2.44 | 1726 | 1623 (0.940) | 1835 (1.063) |
| TG, no ESD | ESD-dominated on 1 pF, 46.5 mV/s | 7.2e+04 | 2.26 | 676.6 | 633.7 (0.936) | 720.5 (1.065) |
| TG, no ESD | reference, 3.1 mV/s | 4.3e+05 | 2.26 | 1688 | 1575 (0.933) | 1781 (1.055) |
| TG, ESD on the node | ESD-dominated on 1 pF, 46.5 mV/s | 7e+04 | 2.28 | 701.6 | 657.4 (0.937) | 744.4 (1.061) |
| TG, ESD on the node | reference, 3.1 mV/s | 4.3e+05 | 2.28 | 1720 | 1604 (0.932) | 1814 (1.054) |
| NMOS, 0.3 V underdrive | Darnas et al., 5.5 µV/s | 1.8e+06 | 2.44 | 3179 | 2972 (0.935) | 3419 (1.076) |
| bootstrapped (transistor level), 0.3 V underdrive | Darnas et al., 5.5 µV/s | 1.8e+06 | 2.39 | 3323 | 3110 (0.936) | 3553 (1.069) |
| T-switch + OTA buffer | Darnas et al., 5.5 µV/s | 1.8e+06 | 2.42 | 3278 | 3063 (0.934) | 3518 (1.073) |
| TG + dummies | Darnas et al., 5.5 µV/s | 1.8e+06 | 2.44 | 5301 | 4861 (0.917) | 5686 (1.073) |
| TG, no ESD | Darnas et al., 5.5 µV/s | 1.8e+06 | 2.26 | 5293 | 4828 (0.912) | 5646 (1.067) |
| TG, ESD on the node | Darnas et al., 5.5 µV/s | 1.8e+06 | 2.28 | 5634 | 5135 (0.912) | 6014 (1.068) |

SPICE / model, closed when the line settles: 0.912 to 1.028; closed at the model's line time: 1.054 to 1.172.
