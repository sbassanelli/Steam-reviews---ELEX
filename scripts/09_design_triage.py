"""Design triage of the sub-themes. Usage (from pipeline/): ../../venv/bin/python ../scripts/09_design_triage.py
Groups each sub-theme by two rules fixed in advance:
  tone: net negative if negative extracts > positive extracts, otherwise net positive
  weight: odds ratio of recommending, significant after Benjamini-Hochberg (subthemes.csv)
Repair first = net negative, OR < 1. Accepted friction = net negative, OR > 1. Protect = net positive, OR > 1.
Contested = net positive, OR < 1. Not decisive = no significant association."""
import re

import pandas as pd

COMPARE = re.compile(r"gothic|g0thic|готик|risen|ризен|哥特|piranha|пиран", re.I)
s = pd.read_csv("../results/subthemes.csv")
d = pd.read_csv("sample/thematic_analysis_final_reassigned.csv")
d["veteran"] = d["full_text"].fillna("").apply(lambda t: bool(COMPARE.search(t)))


def group(r):
    if r.p_bh >= 0.05:
        return "Not decisive"
    net_negative = r["negative_%"] > r["positive_%"]
    if r.or_recommend < 1:
        return "Repair first" if net_negative else "Contested"
    return "Accepted friction" if net_negative else "Protect"


s["group"] = s.apply(group, axis=1)
rows = []
rev = d.groupby("item_id").agg(rec=("voted_up", "first"), veteran=("veteran", "first"))
for r in s.itertuples():
    g = d[(d.theme == r.theme) & (d.subtheme_id == r.subtheme_id)]
    critics = rev.loc[g[g.polarity == "Negative"].item_id.unique()]
    v, o = critics[critics.veteran], critics[~critics.veteran]
    rows.append({"critics": len(critics), "critics_recommend_%": round(100 * critics.rec.mean(), 1) if len(critics) else None,
                 "critics_veteran": len(v), "critics_veteran_recommend_%": round(100 * v.rec.mean(), 1) if len(v) else None,
                 "critics_other": len(o), "critics_other_recommend_%": round(100 * o.rec.mean(), 1) if len(o) else None})
out = pd.concat([s.drop(columns=["top_codes"]), pd.DataFrame(rows)], axis=1)
out.to_csv("../results/design_triage.csv", index=False)
print(out.group.value_counts().to_string())
print(out[out.group != "Not decisive"].sort_values(["group", "reviews"], ascending=[True, False])[["subtheme", "group", "reviews", "negative_%", "positive_%", "or_recommend", "critics", "critics_recommend_%", "critics_veteran", "critics_veteran_recommend_%", "critics_other", "critics_other_recommend_%"]].to_string())
