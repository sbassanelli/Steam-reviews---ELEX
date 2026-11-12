"""Loud problems and scattered ones: mechanics against the four most negative themes (challenge, UI, system, onboarding).
Compares negative extracts, reviews that criticize each block, recommendation, playtime at the time of the review, the share of
complaints among reviews written after less than five hours of play (a proxy for early abandonment), and specificity.
Usage (from pipeline/): ../../venv/bin/python ../scripts/17_hidden_problems.py   Output: ../results/hidden_problems.csv"""
import json

import numpy as np
import pandas as pd

LOUD, OTHERS, LOW_HOURS = ["MECHANICS"], ["CHALLENGE", "UI", "SYSTEM", "ONBOARDING"], 5
d = pd.read_csv("sample/thematic_analysis_final_reassigned.csv", dtype={"item_id": str})
r = pd.DataFrame([{"item_id": str(x["recommendationid"]), "rec": int(x["voted_up"]), "hours_at_review": (x["author"].get("playtime_at_review") or 0) / 60}
                  for x in json.load(open("sample/sample_items.json", encoding="utf-8"))]).set_index("item_id")
sp = pd.read_csv("../results/extract_specificity.csv", dtype={"item_id": str})
neg, spn = d[d.polarity == "Negative"], sp[sp.polarity == "Negative"]
loud, others = set(neg[neg.theme.isin(LOUD)].item_id), set(neg[neg.theme.isin(OTHERS)].item_id)
not_rec, low = r[r.rec == 0].index, r[r.hours_at_review < LOW_HOURS].index
rows = []
for name, ids, themes in [("mechanics", loud, LOUD), ("four most negative themes", others, OTHERS), ("mechanics only", loud - others, None),
                          ("four themes only", others - loud, None), ("both", loud & others, None), ("neither", set(r.index) - loud - others, None)]:
    x = r.loc[sorted(ids)]
    row = {"block": name, "reviews": len(x), "recommend_%": round(100 * x.rec.mean(), 1), "median_hours_at_review": round(x.hours_at_review.median(), 1),
           "share_of_not_recommending_%": round(100 * np.mean([i in ids for i in not_rec]), 1),
           f"share_of_reviews_under_{LOW_HOURS}h_%": round(100 * np.mean([i in ids for i in low]), 1)}
    if themes:
        row["negative_extracts"] = int(neg.theme.isin(themes).sum())
        row["specific_or_suggestion_%"] = round(100 * (spn[spn.theme.isin(themes)].label != "JUDGMENT").mean(), 1)
    rows.append(row)
for t in LOUD + OTHERS:
    ids = set(neg[neg.theme == t].item_id)
    rows.append({"block": f"theme {t}", "reviews": len(ids), f"share_of_reviews_under_{LOW_HOURS}h_%": round(100 * np.mean([i in ids for i in low]), 1),
                 "share_of_all_reviews_%": round(100 * len(ids) / len(r), 1)})
out = pd.DataFrame(rows)
out.to_csv("../results/hidden_problems.csv", index=False)
print(f"reviews under {LOW_HOURS} h at review: {len(low)}, recommending {100 * r.loc[low].rec.mean():.1f}%")
print(out.to_string(index=False))
