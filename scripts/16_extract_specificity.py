"""What do reviews offer to design? Each coded extract is labelled by two models (Phi-4 and Gemma 4) as:
  JUDGMENT    an evaluation or feeling about an aspect, without saying what in it causes the judgment ("combat is clunky")
  SPECIFIC    points to a concrete element, cause, moment, value or behaviour of the game ("enemies one-shot you at level 5")
  SUGGESTION  proposes or asks for a change, or says how something should be ("stamina should use 20% less per hit")
The final label is Phi-4's (Gemma's if Phi-4 fails); agreement is reported as Cohen's kappa. Resumable.
Second pass: Phi-4 splits the SUGGESTION extracts into DEVELOPERS (a change to the game) and PLAYERS (advice to other players).
Usage (from pipeline/): ../../venv/bin/python ../scripts/16_extract_specificity.py
Outputs: ../results/extract_specificity.csv (one row per extract), extract_specificity_summary.csv"""
import asyncio
import importlib
import json
import os
import sys
import time

import httpx
import pandas as pd

sys.path.insert(0, os.getcwd())
import common as K
H = importlib.import_module("2_harmonization")

MODELS, BATCH, CK = ["phi4:latest", "gemma4:latest"], 30, "sample/specificity_checkpoint.json"
LABELS = ["JUDGMENT", "SPECIFIC", "SUGGESTION"]
def schema(ids):
    """One required field per extract id, so that the model must label every extract."""
    return {"type": "object", "properties": {f"e{i}": {"type": "string", "enum": LABELS} for i in ids}, "required": [f"e{i}" for i in ids]}
PROMPT = """You classify short extracts from player reviews of a video game by what they offer to a game designer.
Game: {context}

Labels:
- JUDGMENT: an evaluation or a feeling about an aspect of the game, without saying what in it causes the judgment.
  Examples: "combat is clunky", "the story is great", "too many bugs", "I loved the world".
- SPECIFIC: points to a concrete element, cause, moment, value or behaviour of the game that a designer could locate.
  Examples: "enemies at level 5 kill you in one hit", "the E key cannot be rebound", "the game crashes in the final cutscene",
  "you can loot everything without weight limits".
- SUGGESTION: proposes or asks for a change, or says how something should be. If an extract is both specific and a suggestion,
  choose SUGGESTION. Examples: "stamina should use 20% less per hit", "make it a different key to sit and to loot".

Extracts may be in any language. Return one label for every extract: the key is "e" followed by its number, e.g. "e12".

{listing}"""


TARGETS = ["DEVELOPERS", "PLAYERS"]
TARGET_PROMPT = """Each extract below comes from a player review of a video game and contains a suggestion.
Game: {context}
Label each extract:
- DEVELOPERS: it proposes or asks for a change to the game (its rules, content, balance, interface, technology or support).
  Examples: "stamina should use 20% less per hit", "make it a different key to sit and to loot", "please fix the save bug".
- PLAYERS: it advises other players how to play, what to buy or what to expect, without asking for a change to the game.
  Examples: "set it to easy", "get some proper gear", "don't be afraid to run from battles at the beginning".
Return one label for every extract: the key is "e" followed by its number.

{listing}"""


def target_schema(ids):
    return {"type": "object", "properties": {f"e{i}": {"type": "string", "enum": TARGETS} for i in ids}, "required": [f"e{i}" for i in ids]}


async def main():
    cfg = K.load_config("study_config_sample.json")
    d = pd.read_csv("sample/thematic_analysis_final_reassigned.csv", dtype={"item_id": str})
    d = d.reset_index(drop=True)
    d["eid"] = d.index
    state = K.load_json(CK) if os.path.exists(CK) else {m: {} for m in MODELS}
    for m in MODELS:
        state.setdefault(m, {})
    async with httpx.AsyncClient(timeout=cfg["ollama"]["timeout"]) as client:
        for m in MODELS:
            t0 = time.time()
            todo = [i for i in d.eid if str(i) not in state[m]]
            for s in range(0, len(todo), BATCH):
                ids = todo[s:s + BATCH]
                listing = "\n".join(f"[{i}] {str(d.at[i, 'snippet'])[:300]}" for i in ids)
                res = await K.call_llm(cfg, client, m, [{"role": "user", "content": PROMPT.format(context=cfg["study"]["context"], listing=listing)}], schema(ids))
                got = {int(k[1:]): v for k, v in res["raw"].items() if k.startswith("e") and k[1:].isdigit()}
                for i in ids:
                    state[m][str(i)] = got.get(i) if got.get(i) in LABELS else "NONE"
                K.save_json(CK, state)
                if (s // BATCH) % 20 == 0:
                    print(f"{m}: {s + len(ids)}/{len(todo)} ({time.time() - t0:.0f} s)", flush=True)
            await K.unload_model(cfg, client, m)
            print(f"{m}: done in {time.time() - t0:.0f} s", flush=True)
    a, b = [d.eid.astype(str).map(state[m]) for m in MODELS]
    sugg = [i for i in d.eid if (a[i] if a[i] != "NONE" else b[i]) == "SUGGESTION"]
    state.setdefault("target", {})
    todo = [i for i in sugg if str(i) not in state["target"]]
    async with httpx.AsyncClient(timeout=cfg["ollama"]["timeout"]) as client:
        for s in range(0, len(todo), BATCH):
            ids = todo[s:s + BATCH]
            listing = "\n".join(f"[{i}] {str(d.at[i, 'snippet'])[:300]}" for i in ids)
            res = await K.call_llm(cfg, client, MODELS[0], [{"role": "user", "content": TARGET_PROMPT.format(context=cfg["study"]["context"], listing=listing)}], target_schema(ids))
            got = {int(k[1:]): v for k, v in res["raw"].items() if k.startswith("e") and k[1:].isdigit()}
            for i in ids:
                state["target"][str(i)] = got.get(i) if got.get(i) in TARGETS else "NONE"
            K.save_json(CK, state)
    d["suggestion_target"] = d.eid.astype(str).map(state["target"])
    d["label_phi4"], d["label_gemma4"] = a, b
    d["label"] = a.where(a != "NONE", b)
    tri = pd.read_csv("../results/design_triage.csv")[["theme", "subtheme_id", "group"]]
    d = d.merge(tri, on=["theme", "subtheme_id"], how="left")
    keep = ["item_id", "language", "voted_up", "theme", "subtheme_id", "subtheme", "group", "polarity", "code", "snippet", "label_phi4", "label_gemma4", "label", "suggestion_target"]
    d[keep].to_csv("../results/extract_specificity.csv", index=False)
    both = (a != "NONE") & (b != "NONE")
    k = H.kappa(list(a[both]), list(b[both]))
    rows = []
    for name, g in [("all", d), *[(f"polarity={p}", g) for p, g in d.groupby("polarity")], *[(f"group={p}", g) for p, g in d.groupby("group")], *[(f"theme={p}", g) for p, g in d.groupby("theme")]]:
        vc = g["label"].value_counts(normalize=True) * 100
        rows.append({"subset": name, "extracts": len(g), **{f"{l}_%": round(vc.get(l, 0), 1) for l in LABELS},
                     "suggestion_to_developers_%": round(100 * ((g.label == "SUGGESTION") & (g.suggestion_target == "DEVELOPERS")).mean(), 1),
                     "suggestion_to_players_%": round(100 * ((g.label == "SUGGESTION") & (g.suggestion_target == "PLAYERS")).mean(), 1),
                     "reviews_with_suggestion": int(g.loc[g.label == "SUGGESTION", "item_id"].nunique()),
                     "reviews_with_suggestion_to_developers": int(g.loc[(g.label == "SUGGESTION") & (g.suggestion_target == "DEVELOPERS"), "item_id"].nunique()),
                     "reviews_with_specific_or_suggestion": int(g.loc[g.label.isin(["SPECIFIC", "SUGGESTION"]), "item_id"].nunique())})
    s = pd.DataFrame(rows)
    s.insert(0, "kappa_phi4_gemma4", round(k, 3))
    s.to_csv("../results/extract_specificity_summary.csv", index=False)
    print(s.to_string(index=False))
    print("identical %", round(100 * (a[both] == b[both]).mean(), 1), "| none phi4", int((a == "NONE").sum()), "| none gemma", int((b == "NONE").sum()))


asyncio.run(main())
