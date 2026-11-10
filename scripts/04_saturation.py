"""
Thematic saturation of the 1,200 sampled ELEX reviews (new-information criterion of Guest et al., 2020), over 200 random
orderings. Codes are grouped into code types by meaning (average-linkage clustering of embeddings, cosine distance 0.15;
0.10 and 0.20 as sensitivity). Saturation: first n after which the next 50 reviews add at most 5% new code types.
Also: new types in the last 100 reviews, reviews needed for 5 extracts in every sub-theme, distance of the sub-theme mix
from the full sample. Outputs in results/. Usage (from pipeline/): ../../venv/bin/python ../scripts/04_saturation.py
"""
import json
import os

import httpx
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import jensenshannon

RESULTS = os.path.join("..", "results")
os.makedirs(RESULTS, exist_ok=True)
B, STEP, RUN, TAIL, THRESHOLD, MIN_EXTRACTS, DISTANCE = 200, 25, 50, 100, 0.05, 5, 0.15
DISTANCES, RUNS, THRESHOLDS = [0.10, 0.15, 0.20], [25, 50, 100], [0.05, 0.10]
rng = np.random.default_rng(42)

ex = pd.read_csv("sample/thematic_analysis_final_reassigned.csv", dtype={"item_id": str})
ex["code_norm"] = ex["code"].astype(str).str.lower().str.strip()
reviews = [str(r["recommendationid"]) for r in json.load(open("sample/sample_items.json", encoding="utf-8"))]
codes = sorted(ex["code_norm"].unique())
X = []
for i in range(0, len(codes), 128):
    r = httpx.post("http://localhost:11434/api/embed", timeout=300,
                   json={"model": "nomic-embed-text:latest", "input": ["clustering: " + c for c in codes[i:i + 128]]})
    r.raise_for_status()
    X += r.json()["embeddings"]
X = np.array(X)
X = X / np.linalg.norm(X, axis=1, keepdims=True)
Z = linkage(X, "average", metric="cosine")
types = {t: dict(zip(codes, fcluster(Z, t, criterion="distance"))) for t in DISTANCES}
by_type = {t: ex.assign(ty=ex["code_norm"].map(m)).groupby("item_id")["ty"].apply(set).to_dict() for t, m in types.items()}
by_sub = ex.groupby("item_id")["subtheme_id"].apply(list).to_dict()
sub_ids = sorted(ex["subtheme_id"].unique())
present = [s for s in sub_ids if (ex["subtheme_id"] == s).sum() >= MIN_EXTRACTS]
full = ex["subtheme_id"].value_counts().reindex(sub_ids, fill_value=0).to_numpy(float)
full /= full.sum()
N = len(reviews)


def sat(c, run, thr):
    return next((n for n in range(STEP, N - run + 1, STEP) if c[n - 1] and (c[n - 1 + run] - c[n - 1]) / c[n - 1] <= thr), None)


points, sens, curves = [], [], []
index = {s: i for i, s in enumerate(sub_ids)}
want = [index[s] for s in present]
for b in range(B):
    order = rng.permutation(reviews)
    cum = {}
    for t in DISTANCES:
        seen, c = set(), []
        for rid in order:
            seen |= by_type[t].get(rid, set())
            c.append(len(seen))
        cum[t] = np.array(c)
        for run in RUNS:
            for thr in THRESHOLDS:
                sens.append({"type_distance": t, "run": run, "threshold": thr, "saturation": sat(cum[t], run, thr)})
    c = cum[DISTANCE]
    counts, first, pos = np.zeros(len(sub_ids)), None, 0
    for n in range(STEP, N + 1, STEP):
        for rid in order[pos:n]:
            for s in by_sub.get(rid, []):
                counts[index[s]] += 1
        pos = n
        if first is None and (counts[want] >= MIN_EXTRACTS).all():
            first = n
        curves.append({"perm": b, "n": n, "code_types": c[n - 1],
                       "js_distance": jensenshannon(counts / max(counts.sum(), 1), full) if counts.sum() else np.nan})
    points.append({"perm": b, "saturation": sat(c, RUN, THRESHOLD), "tail_new_types_%": 100 * (c[-1] - c[-TAIL - 1]) / c[-1],
                   "subthemes_min5": first, "code_types_total": c[-1]})

P, S, K = pd.DataFrame(points), pd.DataFrame(sens), pd.DataFrame(curves)
P.to_csv(os.path.join(RESULTS, "saturation_points.csv"), index=False)
K.groupby("n")[["code_types", "js_distance"]].quantile([0.05, 0.5, 0.95]).unstack().to_csv(os.path.join(RESULTS, "saturation_curves.csv"))
table = S.groupby(["type_distance", "run", "threshold"])["saturation"].agg(
    median="median", q05=lambda x: x.quantile(0.05), q95=lambda x: x.quantile(0.95),
    not_reached_pct=lambda x: 100 * x.isna().mean()).reset_index()
table.to_csv(os.path.join(RESULTS, "saturation_sensitivity.csv"), index=False)
print("distinct codes", len(codes), "| sub-themes with >=5 extracts", len(present), "of", len(sub_ids))
print(P.describe(percentiles=[0.05, 0.5, 0.95]).round(1).to_string())
print("not reached %", round(100 * P["saturation"].isna().mean(), 1))
print(table.to_string(index=False))
print(K.groupby("n")["js_distance"].median().iloc[[3, 7, 11, 19, 31, 47]].round(3).to_string())
