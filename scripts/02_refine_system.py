"""
Single manual refinement of the inductive codebook: the definitions of SYSTEM were widened because 16% of its codes
found no sub-theme (performance, and reports that the game runs without problems). The theme is then tested again
with the same two models, the same 160 codes and the same thresholds. The codebook is updated only if the test improves.
Usage (from pipeline/): ../../venv/bin/python ../scripts/02_refine_system.py
"""
import asyncio
import copy
import importlib
import json
import os
import shutil
import sys

import httpx
import numpy as np

sys.path.insert(0, os.getcwd())
import common as K
H = importlib.import_module("2_harmonization")

THEME = "SYSTEM"
EDITS = {
    "SY1": {"definition_add": " It also includes reports that bugs and glitches are few or absent, and audio or voice bugs.",
            "examples_add": ["no major bugs encountered", "absence of bugs", "audio malfunction"]},
    "SY2": {"definition_add": " It also includes reports that the game is stable or does not crash.",
            "examples_add": ["no crashes experienced", "stable gameplay"]},
    "SY3": {"name": "Performance and Technical Implementation",
            "definition_add": " It also includes performance: frame rate, stuttering, optimization and loading speed, whether good or bad.",
            "examples_add": ["poor optimization", "stuttering combat experience", "fast loading and saving"]},
}


async def main():
    cfg = K.load_config("study_config_sample.json")
    path = cfg.path("codebook")
    book = K.load_json(path)
    data = K.load_json(cfg.path("encoded"))
    ind = cfg["harmonization"]["codebook_induction"]

    codes = H.collect_codes(cfg, data)                      # same draw of test codes as generate_codebook
    rng = np.random.default_rng(cfg["ollama"]["seed"])
    samples = {}
    for theme in cfg.themes:
        names, freqs = list(codes[theme]), np.array(list(codes[theme].values()), dtype=float)
        size = min(ind["evaluation_sample"], len(names))
        samples[theme] = [names[i] for i in rng.choice(len(names), size=size, replace=False, p=freqs / freqs.sum())]

    subs = copy.deepcopy(book["themes"][THEME])
    for s in subs:
        e = EDITS.get(s["id"])
        if e:
            s["name"] = e.get("name", s["name"])
            s["definition"] += e["definition_add"]
            s["example_codes"] = s.get("example_codes", []) + e["examples_add"]

    async with httpx.AsyncClient(timeout=cfg["ollama"]["timeout"]) as client:
        out = []
        for model in ind["evaluation_models"]:
            out.append(await H.assign_sample(cfg, client, model, THEME, subs, samples[THEME]))
            await K.unload_model(cfg, client, model)
    diag = H.diagnose(cfg, subs, samples[THEME], out[0], out[1])
    print({k: diag[k] for k in ("kappa", "unassigned_%", "shares_%", "failed_criteria", "problems")})

    before = book["diagnostics"][THEME][-1]
    better = (diag["failed_criteria"], -(diag["kappa"] or 0)) < (before["failed_criteria"], -(before["kappa"] or 0))
    if not better:
        print("No improvement: codebook left unchanged.")
        return
    backup = path.replace(".json", "_before_refinement.json")
    if not os.path.exists(backup):
        shutil.copy(path, backup)
    book["themes"][THEME] = subs
    book["diagnostics"][THEME].append({"round": "manual refinement", "subthemes": subs, **diag})
    book["manual_refinement"] = {"theme": THEME, "edits": EDITS}
    K.save_json(path, book)
    print("Codebook updated; backup:", backup)


asyncio.run(main())
