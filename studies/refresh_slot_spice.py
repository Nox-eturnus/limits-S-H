"""A whole refresh slot in SPICE, with the drooped node at the far end of the path.

The slot model (Eq. 4; flow/cosim.tree_slot_time) settles the path from the DAC to the far end of the selected leaf
line with its Elmore delay times ln(dV / eps), and then the node through its own switch, tau_node ln(b / eps + 1).
When the switch closes, however, the drooped node shares its charge with the line, and the path, not the switch,
has to restore it. studies/tree_spice.py checks the path alone. Here the same RC networks (best tree of each design
at the three droop rates, 60 segments per line) carry at the far end of the leaf line a switch of the cell's
on-resistance (tau_node / 1 pF) to a 1 pF node held at 1.2 V - b, b being the droop budget of the design (doubled by
centring, as in the hold time). The DAC steps the line by 1.2 V at t = 0, and the switch closes either when the far
end of the line has settled to eps in SPICE (the earliest a controller could close it) or at the model's line time.
The SPICE slot is the time after which both the far end of the line and the node stay within eps of 1.2 V; it is
compared with the model's slot, line term plus node term.

Run:  python studies/refresh_slot_spice.py     (a few minutes; needs ngspice; writes results/refresh_slot_spice.{json,md})
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies"))
import tree as T  # noqa: E402
import tree_spice as TS  # noqa: E402
from flow import cosim as C  # noqa: E402

WORK = ROOT / "build" / "refresh_slot_spice" / "slot"


def settle_time(t, v, eps, target=1.2):
    late = np.nonzero(np.abs(v - target) > eps)[0]
    return float(t[late[-1]]) if late.size else 0.0


def main():
    res = json.loads((ROOT / "results" / "cryogenic.json").read_text(encoding="utf-8"))
    an = json.loads((ROOT / "results" / "droop_anchors.json").read_text(encoding="utf-8"))
    sysj = json.loads((ROOT / "results" / "system.json").read_text(encoding="utf-8"))
    ts = {(r["design"], r["anchor"]): r for r in json.loads((ROOT / "results" / "tree_spice.json")
                                                             .read_text(encoding="utf-8"))["rows"]}
    eps = 0.1 * an["spec_operational"]
    designs = T.designs(res)
    b_of = {r["design"]: r["hold_s"] * r["rate"] for r in an["rows"]}
    cases = [(r["design"], r["anchor"], r["config"], r["tree_n"]["2e-09"]) for r in an["rows"]]
    cases += [(r["design"], r["anchor"], r["config"], min(r["tree"]["2e-09"]["n"], sysj["n_per_reticle"]))
              for r in sysj["rows"] if r["anchor"].startswith("Darnas")]
    out = {"eps": eps, "n_seg": TS.N_SEG, "rows": []}
    WORK.mkdir(parents=True, exist_ok=True)
    for i, (d, anchor, cfg, n) in enumerate(cases):
        cell, b = designs[d]["cell"], b_of[d]
        fan = None if cfg.startswith("Fone") else float(cfg[1:].split("_")[0])
        tree = C.TreeConfig(fanout=fan, w_tree=float(cfg.split("_w")[1]))
        tau, _, _ = C.tree_path(n, cell, tree)
        t_line = tau * np.log(tree.dv_line / eps)
        t_node = cell["tau_node"] * np.log(b / eps + 1.0)
        r_on = cell["tau_node"] / tree.c_node
        row = {"design": d, "anchor": anchor, "config": cfg, "n": n, "b": b, "t_line_model": float(t_line),
               "t_node_model": float(t_node), "t_slot_model": float(t_line + t_node)}
        for label, t_close in (("close_at_spice_line", ts[(d, anchor)]["t_spice"]), ("close_at_model_line", t_line)):
            L, far = TS.netlist(n, cell, tree)
            L += [f"VC ctl 0 PWL(0 0 {t_close:.6e} 0 {t_close + 20e-12:.6e} 1)",
                  "SW1 " + far + " hold ctl 0 swm", f".model swm sw(vt=0.5 vh=0.1 ron={r_on:.6g} roff=1e15)",
                  f"CH hold 0 {tree.c_node:.6g}", f".ic v(hold)={1.2 - b:.9f}",
                  f".save v({far}) v(hold)", f".tran {t_line / 4000:.3e} {3.0 * t_line:.3e}", ".end", ""]
            w = C.spice.run_ngspice("\n".join(L), WORK, f"slot{i}_{label}")
            t = w["time"]
            t_end = max(settle_time(t, w[f"v({far})"], eps), settle_time(t, w["v(hold)"], eps))
            row[label] = {"t_close": float(t_close), "t_slot_spice": t_end, "ratio": t_end / (t_line + t_node)}
        out["rows"].append(row)
        print(f"{d[:34]:34s} {anchor[:20]:20s} N {n:.2g}: model {row['t_slot_model'] * 1e9:.4g} ns, SPICE "
              f"{row['close_at_spice_line']['t_slot_spice'] * 1e9:.4g} ns ({row['close_at_spice_line']['ratio']:.3f}), "
              f"closing at model line time {row['close_at_model_line']['t_slot_spice'] * 1e9:.4g} ns "
              f"({row['close_at_model_line']['ratio']:.3f})", flush=True)
    (OUT / "refresh_slot_spice.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["# A whole refresh slot in SPICE, drooped 1 pF node at the far end of the path", "",
         f"eps = {eps * 1e6:.0f} µV, 1.2 V step, {TS.N_SEG} RC segments per line; node at 1.2 V - b.", "",
         "| design | droop | electrodes | b (mV) | model slot (ns) | SPICE, closed when the line settles (ns, ratio) | "
         "SPICE, closed at the model's line time (ns, ratio) |", "|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        a, m = r["close_at_spice_line"], r["close_at_model_line"]
        L.append(f"| {r['design']} | {r['anchor']} | {r['n']:.2g} | {r['b'] * 1e3:.3g} | {r['t_slot_model'] * 1e9:.4g} | "
                 f"{a['t_slot_spice'] * 1e9:.4g} ({a['ratio']:.3f}) | {m['t_slot_spice'] * 1e9:.4g} ({m['ratio']:.3f}) |")
    ra = [r["close_at_spice_line"]["ratio"] for r in out["rows"]]
    rm = [r["close_at_model_line"]["ratio"] for r in out["rows"]]
    L += ["", f"SPICE / model, closed when the line settles: {min(ra):.3f} to {max(ra):.3f}; "
          f"closed at the model's line time: {min(rm):.3f} to {max(rm):.3f}."]
    (OUT / "refresh_slot_spice.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[-1:]))


if __name__ == "__main__":
    main()
