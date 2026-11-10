"""
Analysis of the 1,200 sampled ELEX reviews (simple random sample of the filtered Steam purchasers).
Unit: the review, with theme or sub-theme mentions from the reassigned coding (extract level for sentiment shares).
 1. themes_prevalence.csv     share of reviews mentioning each theme (Wilson 95% CI), positive/negative extracts
 2. subthemes.csv             per sub-theme: extracts, reviews, polarity, OR of recommending if mentioned (BH over sub-themes)
 3. recommendation_model.csv  logit recommended ~ any positive / any negative mention of each theme + log hours + language (HC1)
 4. playtime_model.csv        OLS log(1+hours) ~ theme mentions + recommended + language (HC3), BH over themes; also playtime at review
 5. comparison_*.csv          reviews naming Gothic, Risen or Piranha Bytes vs the others
Robustness: the recommendation model is repeated on extracts proposed by both encoders.
Usage (from pipeline/): ../../venv/bin/python ../scripts/06_analysis.py
"""
import json
import os
import re

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

RES = os.path.join("..", "results")
os.makedirs(RES, exist_ok=True)
THEMES = ["STORYTELLING", "MECHANICS", "CHALLENGE", "PROGRESSION_CONTENT", "ONBOARDING", "UI", "AUDIOVISUAL", "SYSTEM", "LIVE_DEVELOPMENT"]
COMPARE = re.compile(r"gothic|g0thic|готик|risen|ризен|哥特|piranha|пиран", re.I)

ex = pd.read_csv("sample/thematic_analysis_final_reassigned.csv", dtype={"item_id": str})
rows = [{"item_id": str(r["recommendationid"]), "recommended": int(r["voted_up"]), "language": r["language"], "text": r["review"],
         "hours": r["author"]["playtime_forever"] / 60, "hours_at_review": (r["author"].get("playtime_at_review") or 0) / 60}
        for r in json.load(open("sample/sample_items.json", encoding="utf-8"))]
d = pd.DataFrame(rows).set_index("item_id")
d["lang"] = d["language"].where(d["language"].isin(["english", "russian", "german"]), "other")
d["log_hours"] = np.log1p(d["hours"])
d["log_hours_review"] = np.log1p(d["hours_at_review"])
d["compare"] = d["text"].apply(lambda t: int(bool(COMPARE.search(t))))
N = len(d)
lang = pd.get_dummies(d["lang"], drop_first=True).astype(float).add_prefix("lang_")


def flags(extracts):
    out = pd.DataFrame(index=d.index)
    for t in THEMES:
        s = extracts[extracts["theme"] == t]
        out[f"{t}"] = d.index.isin(s["item_id"]).astype(int)
        out[f"{t}_pos"] = d.index.isin(s[s["polarity"] == "Positive"]["item_id"]).astype(int)
        out[f"{t}_neg"] = d.index.isin(s[s["polarity"] == "Negative"]["item_id"]).astype(int)
    return out


F = flags(ex)

# 1. Themes
t1 = []
for t in THEMES:
    s = ex[ex["theme"] == t]
    k = int(F[t].sum())
    lo, hi = proportion_confint(k, N, method="wilson")
    t1.append({"theme": t, "reviews": k, "reviews_%": round(100 * k / N, 1), "ci_low": round(100 * lo, 1), "ci_high": round(100 * hi, 1),
               "extracts": len(s), "positive_%": round(100 * (s["polarity"] == "Positive").mean(), 1),
               "neutral_%": round(100 * (s["polarity"] == "Neutral").mean(), 1),
               "negative_%": round(100 * (s["polarity"] == "Negative").mean(), 1),
               "reviews_pos": int(F[f"{t}_pos"].sum()), "reviews_neg": int(F[f"{t}_neg"].sum()),
               "neg_in_recommending_%": round(100 * d.loc[F[f"{t}_neg"] == 1, "recommended"].mean(), 1)})
t1 = pd.DataFrame(t1)
t1.to_csv(os.path.join(RES, "themes_prevalence.csv"), index=False)


def or_2x2(flag):
    a = int(((flag == 1) & (d["recommended"] == 1)).sum()); b = int(((flag == 1) & (d["recommended"] == 0)).sum())
    c = int(((flag == 0) & (d["recommended"] == 1)).sum()); e = int(((flag == 0) & (d["recommended"] == 0)).sum())
    a2, b2, c2, e2 = [x + 0.5 for x in (a, b, c, e)]
    lor, se = np.log(a2 * e2 / (b2 * c2)), np.sqrt(1 / a2 + 1 / b2 + 1 / c2 + 1 / e2)
    return np.exp(lor), np.exp(lor - 1.96 * se), np.exp(lor + 1.96 * se), stats.fisher_exact([[a, b], [c, e]])[1]


# 2. Sub-themes
t2 = []
for (t, sid, name), s in ex.groupby(["theme", "subtheme_id", "subtheme"]):
    flag = pd.Series(d.index.isin(s["item_id"]).astype(int), index=d.index)
    o, lo, hi, p = or_2x2(flag)
    t2.append({"theme": t, "subtheme_id": sid, "subtheme": name, "extracts": len(s), "reviews": int(flag.sum()),
               "share_of_theme_%": round(100 * len(s) / (ex["theme"] == t).sum(), 1),
               "positive_%": round(100 * (s["polarity"] == "Positive").mean(), 1), "negative_%": round(100 * (s["polarity"] == "Negative").mean(), 1),
               "or_recommend": round(o, 2), "or_low": round(lo, 2), "or_high": round(hi, 2), "p": p,
               "top_codes": "; ".join(s["code"].astype(str).str.lower().value_counts().head(5).index)})
t2 = pd.DataFrame(t2)
t2["p_bh"] = multipletests(t2["p"], method="fdr_bh")[1]
t2.sort_values(["theme", "subtheme_id"]).to_csv(os.path.join(RES, "subthemes.csv"), index=False)


# 3. Recommendation
def rec_model(fl):
    terms = [f"{t}_{k}" for t in THEMES for k in ("pos", "neg")]
    # A term present in only one outcome class has no finite OR (perfect separation): left out and reported
    separated = [x for x in terms if fl.groupby(d["recommended"])[x].sum().min() == 0 or fl[x].sum() < 5]
    if separated:
        print("Left out of the recommendation model (separation or fewer than 5 reviews):", separated)
    terms = [x for x in terms if x not in separated]
    X = sm.add_constant(pd.concat([fl[terms], d[["log_hours"]], lang], axis=1).astype(float))
    m = sm.Logit(d["recommended"], X).fit(disp=0, maxiter=200, cov_type="HC1")
    r = pd.DataFrame({"or": np.exp(m.params), "low": np.exp(m.conf_int()[0]), "high": np.exp(m.conf_int()[1]), "p": m.pvalues}).drop("const")
    idx = r.index.isin(terms)
    r["p_bh"] = np.nan
    r.loc[idx, "p_bh"] = multipletests(r.loc[idx, "p"], method="fdr_bh")[1]
    return r.round(4), m.prsquared


r3, r2 = rec_model(F)
r3.to_csv(os.path.join(RES, "recommendation_model.csv"))
both, _ = rec_model(flags(ex[ex["source"] == "both"]))
both.to_csv(os.path.join(RES, "recommendation_model_both_encoders.csv"))


# 4. Playtime
def play(y):
    X = sm.add_constant(pd.concat([F[THEMES], d[["recommended"]], lang], axis=1).astype(float))
    m = sm.OLS(d[y], X).fit(cov_type="HC3")
    ci = m.conf_int()
    r = pd.DataFrame({"pct_change": 100 * (np.exp(m.params) - 1), "low": 100 * (np.exp(ci[0]) - 1), "high": 100 * (np.exp(ci[1]) - 1), "p": m.pvalues}).drop("const")
    idx = r.index.isin(THEMES)
    r["p_bh"] = np.nan
    r.loc[idx, "p_bh"] = multipletests(r.loc[idx, "p"], method="fdr_bh")[1]
    return r.round(4), m.rsquared


p1, pr = play("log_hours")
p2, _ = play("log_hours_review")
p1.to_csv(os.path.join(RES, "playtime_model.csv"))
p2.to_csv(os.path.join(RES, "playtime_model_at_review.csv"))

# 5. Comparisons
cmp_flag = d["compare"]
o, lo, hi, p = or_2x2(cmp_flag)
summary = {"reviews_comparing": int(cmp_flag.sum()), "share_%": round(100 * cmp_flag.mean(), 1),
           "recommended_compare_%": round(100 * d.loc[cmp_flag == 1, "recommended"].mean(), 1),
           "recommended_other_%": round(100 * d.loc[cmp_flag == 0, "recommended"].mean(), 1), "or": round(o, 2), "low": round(lo, 2), "high": round(hi, 2), "p": p,
           "median_hours_compare": round(d.loc[cmp_flag == 1, "hours"].median(), 1), "median_hours_other": round(d.loc[cmp_flag == 0, "hours"].median(), 1),
           "mannwhitney_p": stats.mannwhitneyu(d.loc[cmp_flag == 1, "hours"], d.loc[cmp_flag == 0, "hours"]).pvalue,
           "median_chars_compare": d.loc[cmp_flag == 1, "text"].str.len().median(), "median_chars_other": d.loc[cmp_flag == 0, "text"].str.len().median()}
pd.DataFrame([summary]).to_csv(os.path.join(RES, "comparison_summary.csv"), index=False)
t5 = []
for t in THEMES:
    a, b = F.loc[cmp_flag == 1, t], F.loc[cmp_flag == 0, t]
    t5.append({"theme": t, "compare_%": round(100 * a.mean(), 1), "other_%": round(100 * b.mean(), 1), "diff": round(100 * (a.mean() - b.mean()), 1),
               "p": stats.fisher_exact([[a.sum(), len(a) - a.sum()], [b.sum(), len(b) - b.sum()]])[1]})
t5 = pd.DataFrame(t5)
t5["p_bh"] = multipletests(t5["p"], method="fdr_bh")[1]
t5.to_csv(os.path.join(RES, "comparison_themes.csv"), index=False)

pd.set_option("display.width", 200, "display.max_columns", 30, "display.max_colwidth", 42)
print("N", N, "recommended %", round(100 * d["recommended"].mean(), 1), "reviews with extracts", int((F[THEMES].sum(axis=1) > 0).sum()))
print(t1.drop(columns=["ci_low", "ci_high"]).to_string(index=False))
print("\nRECOMMENDATION pseudo-R2", round(r2, 3)); print(r3.to_string())
print("\nBOTH ENCODERS"); print(both.loc[[i for i in both.index if i.endswith(("_pos", "_neg"))], ["or", "p_bh"]].T.to_string())
print("\nPLAYTIME R2", round(pr, 3)); print(p1.to_string())
print("\nAT REVIEW"); print(p2[["pct_change", "p_bh"]].T.to_string())
print("\nCOMPARE", summary); print(t5.to_string(index=False))
print("\nSUBTHEMES"); print(t2.sort_values("or_recommend")[["subtheme_id", "subtheme", "extracts", "reviews", "positive_%", "negative_%", "or_recommend", "or_low", "or_high", "p_bh"]].to_string(index=False))
