"""
Reassigns the sub-theme of every extract with the procedure of the codebook test: each distinct code of a theme is
assigned, in batches, by the two evaluation models (Phi-4, then Gemma 4). Themes, snippets, codes and sentiment are not
changed. Reason: during harmonization the choice of sub-theme favoured the first sub-theme listed.
Rule: Phi-4's sub-theme; if NONE, Gemma's; if both NONE, the sub-theme given at harmonization (flagged).
Outputs in pipeline/sample: thematic_analysis_final_reassigned.csv, thematic_analysis_summary_reassigned.csv,
reassignment_report.csv. The original files are not modified.
Usage (from pipeline/): ../../venv/bin/python ../scripts/03_reassign_subthemes.py
"""
import asyncio
import importlib
import json
import os
import sys

import httpx
import pandas as pd

sys.path.insert(0, os.getcwd())
import common as K
H = importlib.import_module("2_harmonization")

OUT = "sample"
CK = os.path.join(OUT, "reassign_checkpoint.json")


async def main():
    cfg = K.load_config("study_config_sample.json")
    book = K.load_json(cfg.path("codebook"))
    df = pd.read_csv(cfg.path("final"), dtype={"item_id": str})
    models = cfg["harmonization"]["codebook_induction"]["evaluation_models"]
    key = H.codebook_hash(book)
    done = {}
    if os.path.exists(CK):
        state = K.load_json(CK)
        done = state["done"] if state.get("key") == key else {}

    async with httpx.AsyncClient(timeout=cfg["ollama"]["timeout"]) as client:
        for model in models:
            for theme, subs in book["themes"].items():
                tag = f"{model}|{theme}"
                if tag in done:
                    continue
                codes = sorted(df.loc[df["theme"] == theme, "code"].astype(str).unique())
                done[tag] = dict(zip(codes, await H.assign_sample(cfg, client, model, theme, subs, codes)))
                K.save_json(CK, {"key": key, "done": done})
                print(f"{model} {theme}: {len(codes)} codes", flush=True)
            await K.unload_model(cfg, client, model)

    report, frames = [], []
    for theme, subs in book["themes"].items():
        names = {s["id"]: s["name"] for s in subs}
        a, b = done[f"{models[0]}|{theme}"], done[f"{models[1]}|{theme}"]
        codes = list(a)
        s = df[df["theme"] == theme].copy()
        s["original_subtheme_id"], s["original_subtheme"] = s["subtheme_id"], s["subtheme"]
        src, new = [], []
        for code, old in zip(s["code"].astype(str), s["subtheme_id"]):
            if a[code] != "NONE":
                new.append(a[code]); src.append("phi4")
            elif b[code] != "NONE":
                new.append(b[code]); src.append("gemma4")
            else:
                new.append(old); src.append("both_none_kept_original")
        s["subtheme_id"], s["reassign_source"] = new, src
        s["subtheme"] = s["subtheme_id"].map(names)
        frames.append(s)
        x, y = [a[c] for c in codes], [b[c] for c in codes]
        report.append({"theme": theme, "distinct_codes": len(codes), "kappa": round(H.kappa(x, y), 3),
                       "unassigned_%": round(100 * (x + y).count("NONE") / (2 * len(codes)), 1),
                       "both_none_extracts": src.count("both_none_kept_original"),
                       "changed_extracts_%": round(100 * (s["subtheme_id"] != s["original_subtheme_id"]).mean(), 1),
                       **{f"{i}_%": round(100 * (s["subtheme_id"] == i).mean(), 1) for i in names}})
    final = pd.concat(frames, ignore_index=True)
    final.to_csv(os.path.join(OUT, "thematic_analysis_final_reassigned.csv"), index=False, encoding="utf-8-sig")
    H.build_summary(cfg, final, book).to_csv(os.path.join(OUT, "thematic_analysis_summary_reassigned.csv"), index=False, encoding="utf-8-sig")
    pd.DataFrame(report).to_csv(os.path.join(OUT, "reassignment_report.csv"), index=False, encoding="utf-8-sig")
    print(pd.DataFrame(report)[["theme", "distinct_codes", "kappa", "unassigned_%", "both_none_extracts", "changed_extracts_%"]].to_string(index=False))


asyncio.run(main())
