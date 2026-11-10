"""
Builds the study population from the collected reviews: reviews of copies bought on Steam, excluding copies the
author declared as received for free. Output: Data/elex_population.json (input of 0_filtering.py) and
Data/population_flow.csv (counts for the paper).
Usage (from this folder): ../../venv/bin/python 01_population.py
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "Data", "raw", "reviews_411300.json")

with open(RAW, encoding="utf-8") as f:
    reviews = json.load(f)

steam = [r for r in reviews if r.get("steam_purchase")]
population = [r for r in steam if not r.get("received_for_free")]

with open(os.path.join(ROOT, "Data", "elex_population.json"), "w", encoding="utf-8") as f:
    json.dump(population, f, ensure_ascii=False, indent=1)

flow = [("collected", len(reviews)), ("not_bought_on_steam", len(reviews) - len(steam)),
        ("received_for_free", len(steam) - len(population)), ("population", len(population))]
with open(os.path.join(ROOT, "Data", "population_flow.csv"), "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows([("step", "reviews"), *flow])
for step, n in flow:
    print(f"{step:22} {n:>7}")
