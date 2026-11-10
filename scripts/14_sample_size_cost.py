"""What a smaller sample would cost and find. Usage (from pipeline/): ../../venv/bin/python ../scripts/14_sample_size_cost.py
For n reviews drawn at random from the 1,200 coded (200 draws each): time per step from the rates measured on the ELEX run, and how many of the
14 priorities of the full sample the triage would find (same rules as 4_design_brief.py). Output: ../results/sample_size_cost.csv"""
import json

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

RNG = np.random.default_rng(42)
ex = pd.read_csv("sample/thematic_analysis_final_reassigned.csv", dtype={"item_id": str})
items = json.load(open("sample/sample_items.json", encoding="utf-8"))
y_all = pd.Series({str(r["recommendationid"]): int(r["voted_up"]) for r in items})
full = pd.read_csv("../results/design_triage.csv")
FULL = dict(zip(full.subtheme, full.group))
PRIOR = {k for k, g in FULL.items() if g != "Not decisive"}
# measured on ELEX (1,200 reviews): seconds
ENC_PER_REVIEW = 7 * 3600 + 16 * 60          # encoding, per sampled review below
HARM_TOTAL, HARM_REVIEWS = 5 * 3600, 1004     # harmonization, per review with extracts
ASSIGN_TOTAL, CODES_FULL = 74 * 60, ex.groupby("theme")["code"].nunique().sum()   # reassignment (incl. SYSTEM refinement), per distinct code
FIXED = {"codebook": 45 * 60, "order check": 12 * 60, "brief": 145, "analysis": 120}


def groups(ids):
    y = y_all.loc[ids]
    e = ex[ex.item_id.isin(ids)]
    rows = []
    for name, s in e.groupby("subtheme"):
        f = y.index.isin(s.item_id)
        a, b, c, d = [int(((f == i) & (y.values == o)).sum()) for i, o in ((1, 1), (1, 0), (0, 1), (0, 0))]
        lor = np.log((a + .5) * (d + .5) / ((b + .5) * (c + .5)))
        rows.append((name, lor, stats.fisher_exact([[a, b], [c, d]])[1], (s.polarity == "Negative").mean() > (s.polarity == "Positive").mean()))
    t = pd.DataFrame(rows, columns=["sub", "lor", "p", "neg"])
    t["sig"] = multipletests(t.p, method="fdr_bh")[0]
    g = np.where(~t.sig, "Not decisive", np.where(t.lor < 0, np.where(t.neg, "Repair first", "Contested"), np.where(t.neg, "Accepted friction", "Protect")))
    return dict(zip(t["sub"], g))


out = []
ids_all = y_all.index.to_numpy()
for n in (300, 400, 500, 600, 800, 1200):
    rec, same, new, codes, with_ex = [], [], [], [], []
    for _ in range(200 if n < 1200 else 1):
        ids = RNG.choice(ids_all, n, replace=False) if n < 1200 else ids_all
        g = groups(ids)
        found = {k for k, v in g.items() if v != "Not decisive"}
        rec.append(len(found & PRIOR)); same.append(sum(g.get(k) == FULL[k] for k in PRIOR)); new.append(len(found - PRIOR))
        e = ex[ex.item_id.isin(ids)]
        codes.append(e.groupby("theme")["code"].nunique().sum()); with_ex.append(e.item_id.nunique())
    c, w = np.mean(codes), np.mean(with_ex)
    secs = {"encoding": ENC_PER_REVIEW / 1200 * n, "harmonization": HARM_TOTAL / HARM_REVIEWS * w, "assignment": ASSIGN_TOTAL / CODES_FULL * c, **FIXED}
    out.append({"n": n, "priorities_found_mean": round(np.mean(rec), 1), "priorities_found_p5": int(np.percentile(rec, 5)), "same_group_mean": round(np.mean(same), 1),
                "new_priorities_mean": round(np.mean(new), 1), "distinct_codes": int(c), "reviews_with_extracts": int(w),
                **{f"{k}_min": round(v / 60) for k, v in secs.items()}, "total_hours": round(sum(secs.values()) / 3600, 1)})
r = pd.DataFrame(out)
r.to_csv("../results/sample_size_cost.csv", index=False)
print(r.to_string())
