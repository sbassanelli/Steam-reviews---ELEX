"""
Two checks on the sub-theme assignment; thresholds fixed in advance.
1. Position check: 160 codes per theme (same size as the codebook test) are assigned again by Phi-4 with the list of
   sub-themes in reverse order, and compared with the assignment in the original order (Cohen's kappa).
   If the order does not matter, the two agree and the first-listed sub-theme does not gain share.
2. Drift check: per sub-theme, final share vs share in the codebook test; flagged if the difference exceeds 10 points.
   Run for the harmonizer's assignment and for the reassignment.
Outputs in results/: position_check.csv, subtheme_drift_check.csv.
Usage (from pipeline/): ../../venv/bin/python ../scripts/05_subtheme_checks.py
"""
import asyncio
import importlib
import os
import sys

import httpx
import numpy as np
import pandas as pd

sys.path.insert(0, os.getcwd())
import common as K
H = importlib.import_module("2_harmonization")

RESULTS, N, MODEL, FLAG = os.path.join("..", "results"), 160, "phi4:latest", 10.0
os.makedirs(RESULTS, exist_ok=True)


async def main():
    cfg = K.load_config("study_config_sample.json")
    book = K.load_json(cfg.path("codebook"))
    df = pd.read_csv("sample/thematic_analysis_final_reassigned.csv", dtype={"item_id": str})
    forward = K.load_json("sample/reassign_checkpoint.json")["done"]
    rng = np.random.default_rng(cfg["ollama"]["seed"])
    rows, drift = [], []
    async with httpx.AsyncClient(timeout=cfg["ollama"]["timeout"]) as client:
        for theme, subs in book["themes"].items():
            vc = df.loc[df["theme"] == theme, "code"].astype(str).value_counts()
            names, p = vc.index.tolist(), (vc / vc.sum()).to_numpy()
            codes = [names[i] for i in rng.choice(len(names), size=min(N, len(names)), replace=False, p=p)]
            back = await H.assign_sample(cfg, client, MODEL, theme, subs[::-1], codes)
            fwd = [forward[f"{MODEL}|{theme}"][c] for c in codes]
            first, last = subs[0]["id"], subs[-1]["id"]
            rows.append({"theme": theme, "codes": len(codes), "kappa_forward_reversed": round(H.kappa(fwd, back), 3),
                         "identical_%": round(100 * np.mean([a == b for a, b in zip(fwd, back)]), 1),
                         "first_listed_forward_%": round(100 * fwd.count(first) / len(fwd), 1),
                         "first_listed_reversed_%": round(100 * back.count(first) / len(back), 1),
                         "last_listed_forward_%": round(100 * fwd.count(last) / len(fwd), 1),
                         "last_listed_reversed_%": round(100 * back.count(last) / len(back), 1)})
            print(rows[-1], flush=True)
            for R in reversed(book["diagnostics"][theme]):
                if [s["name"] for s in R["subthemes"]] == [s["name"] for s in subs]:
                    shares = R["shares_%"]
                    break
            total, s = sum(shares.values()), df[df["theme"] == theme]
            for i, x in enumerate(subs):
                test = 100 * shares.get(x["id"], 0) / total
                old, new = 100 * (s["original_subtheme_id"] == x["id"]).mean(), 100 * (s["subtheme_id"] == x["id"]).mean()
                drift.append({"theme": theme, "subtheme_id": x["id"], "position": i + 1, "test_%": round(test, 1),
                              "harmonizer_%": round(old, 1), "reassigned_%": round(new, 1),
                              "harmonizer_flag": abs(old - test) > FLAG, "reassigned_flag": abs(new - test) > FLAG})
    a, b = pd.DataFrame(rows), pd.DataFrame(drift)
    a.to_csv(os.path.join(RESULTS, "position_check.csv"), index=False)
    b.to_csv(os.path.join(RESULTS, "subtheme_drift_check.csv"), index=False)
    print("flags harmonizer", int(b["harmonizer_flag"].sum()), "| flags reassigned", int(b["reassigned_flag"].sum()), "of", len(b))
    print("finished")


asyncio.run(main())
