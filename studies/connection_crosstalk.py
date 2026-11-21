"""Crosstalk between the adjacent 15 mm connections of a separate hold array.

The limits of 0.57 to 3.7 fF for a neighbour that runs its own CZ belong to a pulse line that swings v0/k (k = 0.5)
and couples into a 1 pF node: C_c < eps C_node k, with eps the fractional error of the CZ amplitude that one gate
tolerates untracked (results/zeeman_equal_sign.json part C, 100 MHz). The connections of a separate hold array are
part of the hold node: each adds 3 to 4.5 pF to the 1 pF of its cell and carries the barrier pulse v0. An aggressor
connection therefore swings v0, and the victim node of 4 to 5.5 pF sees the fractional error C_c / C_node, so the
limit is C_c < eps C_node. The coupling over the mean fan-in length is that of studies/system_operation.py
(0.05 to 0.1 fF/um unshielded; a grounded shield leaving an assumed 1 to 5 %). The compensation accuracy that
schedule-dependent crosstalk needs is the limit over the coupling (none where the limit exceeds the coupling).

Run:  python studies/connection_crosstalk.py     (seconds; writes results/connection_crosstalk.{json,md})
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
C = json.loads((ROOT / "results" / "zeeman_equal_sign.json").read_text(encoding="utf-8"))["C"]
SLOPES = (3.87, 10, 16.6, 33.69)
L_WIRE = json.loads((ROOT / "results" / "system_operation.json").read_text(encoding="utf-8"))["lines_fan_in"]["wire_mean_m"]   # 14.8 mm
COUP = {"unshielded": (0.05e-15 / 1e-6 * L_WIRE, 0.1e-15 / 1e-6 * L_WIRE),
        "shielded": (0.01 * 0.05e-15 / 1e-6 * L_WIRE, 0.05 * 0.1e-15 / 1e-6 * L_WIRE)}
C_NODE = (1e-12 + 3e-12, 1e-12 + 4.5e-12)

L = ["# Crosstalk between adjacent 15 mm connections of a separate hold array", ""]
res = {}
for tgt in ("0.0001", "0.001"):
    eps = [C[f"{s:g}|{tgt}"]["eps_single"] for s in SLOPES]
    old = (min(eps) * 1e-12 * 0.5, max(eps) * 1e-12 * 0.5)
    new = (min(eps) * C_NODE[0], max(eps) * C_NODE[1])
    row = {"eps_pct": [e * 100 for e in eps], "limit_1pF_k0.5_fF": [x * 1e15 for x in old],
           "limit_connection_fF": [x * 1e15 for x in new]}
    for lab, (c_lo, c_hi) in COUP.items():
        row[f"coupling_{lab}_fF"] = [c_lo * 1e15, c_hi * 1e15]
        row[f"accuracy_{lab}"] = [new[0] / c_hi, new[1] / c_lo]
        row[f"accuracy_{lab}_old"] = [old[0] / c_hi, old[1] / c_lo]
    res[tgt] = row
    L += [f"## Target {1 - float(tgt):.2%}".replace(".00%", "%"), "",
          f"- eps (single gate, untracked) {min(eps) * 100:.3g} to {max(eps) * 100:.3g} % (3.87 to 33.69 dec/V)",
          f"- limit for a pulse line into 1 pF, k = 0.5 (paper): {old[0] * 1e15:.2f} to {old[1] * 1e15:.2f} fF",
          f"- limit for an adjacent connection, node 4 to 5.5 pF: {new[0] * 1e15:.1f} to {new[1] * 1e15:.1f} fF"]
    for lab in COUP:
        a, ao = row[f"accuracy_{lab}"], row[f"accuracy_{lab}_old"]
        L.append(f"- {lab} coupling {row[f'coupling_{lab}_fF'][0]:.3g} to {row[f'coupling_{lab}_fF'][1]:.3g} fF: "
                 f"compensation to {a[0]:.2%} to {a[1]:.2%} (paper: {ao[0]:.2%} to {ao[1]:.2%}); above 100 % none is needed")
    L.append("")
print("\n".join(L))
(OUT / "connection_crosstalk.md").write_text("\n".join(L) + "\n", encoding="utf-8")
(OUT / "connection_crosstalk.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
