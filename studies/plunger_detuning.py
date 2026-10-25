"""How a plunger (detuning) offset compares with a barrier offset.

The budget of the paper is for the barrier electrode. The same drivers also bias the plungers, whose
differential offset detunes the double dot. In the Hubbard limit t << U, J(eps) = J_sym / (1 - (eps/U)^2),
so at the symmetric operating point J is insensitive to detuning to first order (Martins 2016,
Reed 2016) and a static plunger offset dV_p (detuning eps = a_p dV_p, lever arm a_p) changes J by
the fraction x^2 / (1 - x^2), x = a_p dV_p / U. The tolerable fraction e is the J error that the
barrier budget without the Stark shift allows, e = 10^(s V_J) - 1, which is the same at every slope.
Then dV_p = (U / a_p) sqrt(e / (1 + e)), with U / a_p the plunger voltage that spans one charging
energy. The plunger's own Stark shift is a single-qubit Z error, which frame tracking removes.

Run:  python studies/plunger_detuning.py      (writes results/plunger_detuning.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flow import budget as B  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"
SLOPES = (3.87, 10.0, 33.69)
TARGETS = (1e-3, 1e-4)
U_OVER_A = (0.01, 0.03, 0.1)      # V of plunger voltage per charging energy (illustrative range)


def main():
    rows = []
    for tgt in TARGETS:
        es = []
        for s in SLOPES:
            lay = B.layer(s_dec_per_v=s, stark_q2=0.0)
            vj = min(B.max_static(lay, tgt, +1), B.max_static(lay, tgt, -1))
            es.append(10 ** (s * vj) - 1)
        e = float(np.min(es))
        x = float(np.sqrt(e / (1 + e)))
        rows.append({"target": tgt, "e_by_slope": dict(zip(map(str, SLOPES), es)), "e": e, "x": x,
                     "dv_plunger": {f"{u * 1e3:g} mV": x * u for u in U_OVER_A}})
        print(f"1-F {tgt:g}: tolerable dJ/J {e:.4f} (slopes {[round(v, 4) for v in es]}), x = {x:.3f}; "
              + ", ".join(f"U/a = {u * 1e3:g} mV -> {x * u * 1e3:.2g} mV" for u in U_OVER_A), flush=True)
    (OUT / "plunger_detuning.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    L = ["## Static plunger (detuning) offset at the symmetric point, against the barrier budget", "",
         "| target | tolerable ΔJ/J | x = a_p ΔV_p / U | " + " | ".join(f"ΔV_p for U/a_p = {u * 1e3:g} mV" for u in U_OVER_A) + " |",
         "|---|---|---|" + "---|" * len(U_OVER_A)]
    for r in rows:
        L.append(f"| {r['target']:g} | {r['e']:.4f} | {r['x']:.3f} | " +
                 " | ".join(f"{v * 1e3:.2g} mV" for v in r["dv_plunger"].values()) + " |")
    L.append("")
    (OUT / "plunger_detuning.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
