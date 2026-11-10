"""Figure of the pipeline, in the style used for the figures of the paper. Counts are those of the ELEX use case (see the paper).
Usage (from pipeline/): ../../venv/bin/python ../scripts/11_fig_pipeline.py [preview_dir]"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

INK, INK2, LINE, FILL, ACCENT, BLUE = "#0b0b0b", "#52514e", "#b9b8b2", "#f5f4f1", "#e8eef8", "#2a78d6"
THEMES = ["STORYTELLING", "MECHANICS", "CHALLENGE", "PROGRESSION", "ONBOARDING", "UI", "AUDIOVISUAL", "SYSTEM", "LIVE DEV."]
GROUPS = [("Repair first", "#eb6834"), ("Accepted friction", "#6b4fbb"), ("Protect", "#2a78d6"), ("Not decisive", "#8f8e88")]


def box(ax, x, y, w, h, fill=FILL, edge=LINE, dashed=False, lw=0.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", facecolor=fill, edgecolor=edge, linewidth=lw, linestyle=(0, (3, 2)) if dashed else "-"))


def head(ax, x, y, h, num, title):
    ax.text(x + 1.4, y + h - 1.6, str(num), fontsize=7 if num < 10 else 6, color="white", fontweight="bold", ha="center", va="center", bbox=dict(boxstyle="circle,pad=0.25", facecolor=INK, edgecolor="none"))
    ax.text(x + 3.0, y + h - 1.6, title, fontsize=7.6, fontweight="bold", color=INK, va="center")


def count(ax, x, y, value, label):
    ax.text(x + 1.2, y + 1.6, value, fontsize=8.5, fontweight="bold", color=INK, va="center")
    ax.text(x + 1.2 + 1.0 * len(value) + 1.0, y + 1.6, label, fontsize=6, color=INK2, va="center")


def step(ax, x, y, w, h, num, title, lines, value=None, label="", **kw):
    box(ax, x, y, w, h, **kw)
    head(ax, x, y, h, num, title)
    ax.text(x + 1.2, y + h - 4.0, "\n".join(lines), fontsize=6.1, color=INK2, va="top", linespacing=1.35)
    if value:
        count(ax, x, y, value, label)


def arrow(ax, p, q, dashed=False):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=7, color=INK2, linewidth=0.8, linestyle=(0, (3, 2)) if dashed else "-", shrinkA=0, shrinkB=0))


fig = plt.figure(figsize=(7.2, 6.38))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100); ax.set_ylim(0, 89); ax.axis("off")

for y0, top, tint, dark, label in [(60.0, 89.0, "#eef4ee", "#5f8a64", "PHASE A   CORPUS AND SAMPLING"), (26.6, 59.4, "#edf1f8", "#4f6fa3", "PHASE B   LLM-ASSISTED CODING AND CHECKS"),
                                   (0.0, 26.0, "#f8f1ea", "#b5734a", "PHASE C   DESIGN READING: FROM CODED REVIEWS TO DECISIONS")]:
    ax.add_patch(FancyBboxPatch((0, y0), 100, top - y0, boxstyle="round,pad=0,rounding_size=1.2", facecolor=tint, edgecolor="none", zorder=0))
    ax.text(1.4, top - 1.5, label, fontsize=6.3, color="white", fontweight="bold", va="center", bbox=dict(boxstyle="round,pad=0.3,rounding_size=0.5", facecolor=dark, edgecolor="none"))

# Phase A
y1, h1, w1, gap = 61.8, 15, 22.5, 3.0
xs = [0.5 + i * (w1 + gap) for i in range(4)]
step(ax, xs[0], y1, w1, h1, 1, "Collection", ["Public Steam reviews of the", "game, every language;", "author identifiers removed;", "population rule applied"], "12,404", "eligible reviews")
step(ax, xs[1], y1, w1, h1, 2, "Deterministic cleaning", ["Length ≥ 20 effective chars", "≥ 60% letters", "No duplicates", "(no LLM)"], "11,092", "reviews")
step(ax, xs[2], y1, w1, h1, 3, "LLM content filter", ["Gemma 4: keep reviews with", "at least one specific", "statement about the game"], "10,027", "population")
step(ax, xs[3], y1, w1, h1, 4, "Random sample", ["Optional; size checked", "afterwards with saturation", "(step 7)"], "1,200", "reviews (360 neg.)")
for i in range(3):
    arrow(ax, (xs[i] + w1, y1 + h1 / 2), (xs[i + 1], y1 + h1 / 2))
box(ax, xs[0], 79.6, w1 + 25.5, 5.2, fill="white", dashed=True)
ax.text(xs[0] + 1.2 + 23.6, 83.1, "Study configuration: one JSON file", fontsize=6.5, fontweight="bold", color=INK, ha="center", va="center")
ax.text(xs[0] + 1.2 + 23.6, 81.1, "game, themes with definitions, few-shot examples, models", fontsize=5.6, color=INK2, ha="center", va="center")
arrow(ax, (xs[0] + w1 / 2, 79.6), (xs[0] + w1 / 2, y1 + h1), dashed=True)

# Phase B
y2, h2 = 27.6, 23.0
ex, ew = 0.5, 28.5
box(ax, ex, y2, ew, h2)
head(ax, ex, y2, h2, 5, "Encoding (deductive themes)")
for row, names in enumerate((THEMES[:4], THEMES[4:])):
    tx = ex + 1.0
    for name in names:
        w = 0.5 * len(name) + 1.0
        ax.text(tx + w / 2, y2 + h2 - 4.1 - row * 2.1, name, fontsize=4.0, color="white", fontweight="bold", ha="center", va="center", bbox=dict(boxstyle="round,pad=0.2,rounding_size=0.4", facecolor="#4f6fa3", edgecolor="none"))
        tx += w + 0.45
for i, (model, sub) in enumerate((("Encoder 1", "Gemma 4"), ("Encoder 2", "Qwen 2.5 14B"))):
    bx = ex + 1.2 + i * 13.3
    box(ax, bx, y2 + 6.9, 12.7, 6.4, fill="white")
    ax.text(bx + 6.35, y2 + 11.6, model, fontsize=6.4, fontweight="bold", color=INK, ha="center", va="center")
    ax.text(bx + 6.35, y2 + 9.9, sub, fontsize=5.8, color=INK2, ha="center", va="center")
    ax.text(bx + 6.35, y2 + 8.2, "snippet, code,\nsentiment", fontsize=5.3, color=INK2, ha="center", va="center")
ax.text(ex + 1.2, y2 + 5.8, "Verbatim check of every snippet;\nverification pass by each model", fontsize=5.9, color=INK2, va="top", linespacing=1.35)
count(ax, ex, y2 - 0.1, "10,406", "valid extracts")

hx, hw = ex + ew + 3.0, 40.0
box(ax, hx, y2, hw, h2)
head(ax, hx, y2, h2, 6, "Codebook and harmonization (Phi-4)")
sub_w = (hw - 3.6) / 2
blocks = [("6a  Inductive codebook", ["Embeddings of the initial codes", "Weighted spherical k-means", "LLM names the clusters", "2-model test (κ, coverage)", "Merge / revise", "≤ 5 sub-themes per theme"]),
          ("6b  Adjudication", ["Pair the encoders' candidates", "Choose the verbatim snippet", "Reconcile code and sentiment", "Keep a justification"])]
for i, (title, lines) in enumerate(blocks):
    bx = hx + 1.2 + i * (sub_w + 1.2)
    box(ax, bx, y2 + 1.2, sub_w, 17.2, fill=ACCENT if i == 0 else "white")
    ax.text(bx + 0.9, y2 + 16.8, title, fontsize=6.0, fontweight="bold", color=INK, va="center")
    ax.text(bx + 0.9, y2 + 14.9, "\n".join(lines), fontsize=5.5, color=INK2, va="top", linespacing=1.4)
arrow(ax, (hx + 1.2 + sub_w, y2 + 9.8), (hx + 2.4 + sub_w, y2 + 9.8))

ax7 = hx + hw + 3.0
w7 = 100 - 0.5 - ax7
step(ax, ax7, y2, w7, h2, 7, "Assignment and checks", ["Each distinct code assigned", "by Phi-4 and Gemma 4", "", "Order check: list reversed", "Drift check: shares against", "the codebook test", "Saturation check"], "5,962", "extracts", fill=ACCENT, edge=BLUE, lw=1.0)
arrow(ax, (ex + ew, y2 + h2 / 2), (hx, y2 + h2 / 2))
arrow(ax, (hx + hw, y2 + h2 / 2), (ax7, y2 + h2 / 2))
sx = xs[3] + w1 / 2
ax.plot([sx, sx, ex + ew / 2], [y1, 54.2, 54.2], color=INK2, linewidth=0.8)
arrow(ax, (ex + ew / 2, 54.2), (ex + ew / 2, y2 + h2))

# Phase C
y3, h3 = 1.0, 16.8
wc, gc = 17.4, 3.0
xc = [0.5 + i * (wc + gc) for i in range(5)]
step(ax, xc[0], y3, wc, h3, 8, "Locate", ["Share of reviews and", "tone of the extracts,", "by sub-theme"], "43", "sub-themes")
step(ax, xc[1], y3, wc, h3, 9, "Weigh", ["Tone and odds of", "recommending"])
for i, (name, col) in enumerate(GROUPS):
    cx = xc[1] + 1.0 + (i % 2) * 7.1
    ax.text(cx + 0.3, y3 + 7.2 - (i // 2) * 2.3, name, fontsize=4.1, color="white", fontweight="bold", va="center", bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.4", facecolor=col, edgecolor="none"))
count(ax, xc[1], y3 - 0.1, "14", "priorities")
step(ax, xc[2], y3, wc, h3, 10, "Diagnose", ["Designers read the", "extracts of each", "priority, also by", "group of players"])
step(ax, xc[3], y3, wc, h3, 11, "Design brief", ["PDF for designers:", "Phi-4 drafts the", "requirements and", "flags tensions"], fill=ACCENT, edge=BLUE, lw=1.0)
count(ax, xc[3], y3 + 2.4, "14", "requirements")
ax.text(xc[3] + 1.2, y3 + 1.6, "accept / modify / reject", fontsize=5.6, color=INK, fontstyle="italic", va="center")
step(ax, xc[4], y3, wc, h3, 12, "Act, re-read", ["Change the game,", "run again on", "later reviews"], fill="white", dashed=True)
ax.text(xc[4] + 1.2, y3 + 1.9, "not performed here", fontsize=5.6, color=INK2, fontstyle="italic", va="center")
for i in range(4):
    arrow(ax, (xc[i] + wc, y3 + h3 / 2), (xc[i + 1], y3 + h3 / 2))
sx = ax7 + w7 / 2
ROUTE = 21.2
AX = xc[0] + wc / 2
ax.plot([sx, sx, AX], [y2, ROUTE, ROUTE], color=INK2, linewidth=0.8, zorder=2)
arrow(ax, (AX, ROUTE), (AX, y3 + h3))

fig.savefig("../Paper/figures/fig_pipeline.pdf", dpi=300)
if len(sys.argv) > 1:
    fig.savefig(sys.argv[1] + "/fig_pipeline.png", dpi=200)
print("done")
