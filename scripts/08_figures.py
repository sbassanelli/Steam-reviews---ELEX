"""Figures of the paper (PDF, in Paper/figures) from results/. Usage (from pipeline/): ../../venv/bin/python ../scripts/08_figures.py [preview_dir]"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"], "font.size": 8,
                     "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#b9b8b2",
                     "axes.linewidth": 0.6, "xtick.color": "#52514e", "ytick.color": "#0b0b0b", "xtick.major.width": 0.6, "ytick.major.size": 0})
POS, NEG, INK, INK2, LINE, FILL, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#b9b8b2", "#f5f4f0", "#8f8e88"
OUT, PREVIEW = "../Paper/figures/", (sys.argv[1] + "/" if len(sys.argv) > 1 else None)
NAME = {"STORYTELLING": "Storytelling", "MECHANICS": "Mechanics", "CHALLENGE": "Challenge", "PROGRESSION_CONTENT": "Progression and content",
        "ONBOARDING": "Onboarding", "UI": "UI", "AUDIOVISUAL": "Audiovisual", "SYSTEM": "System", "LIVE_DEVELOPMENT": "Live development"}


def save(fig, name):
    fig.savefig(OUT + name + ".pdf", bbox_inches="tight", pad_inches=0.02)
    if PREVIEW:
        fig.savefig(PREVIEW + name + ".png", bbox_inches="tight", dpi=170)
    plt.close(fig)


# The pipeline figure is in 11_fig_pipeline.py

# Saturation
c = pd.read_csv("../results/saturation_curves.csv", header=[0, 1], index_col=0).dropna()
c.index = c.index.astype(int)
ct = c["code_types"]
fig, ax = plt.subplots(figsize=(3.35, 2.15))
ax.fill_between(ct.index, ct["0.05"], ct["0.95"], color=POS, alpha=0.18, lw=0)
ax.plot(ct.index, ct["0.5"], color=POS, lw=1.6)
ax.axvline(500, color=INK2, lw=0.7, ls=(0, (3, 2)))
ax.text(512, ct["0.5"].iloc[1], "saturation,\nmedian 500 reviews", fontsize=7, color=INK, va="bottom")
ax.set_xlabel("Reviews coded", color=INK2); ax.set_ylabel("Code types", color=INK2)
ax.set_xlim(0, 1200); ax.set_ylim(0, None); ax.tick_params(axis="y", colors=INK2, length=0)
ax.grid(axis="y", color=LINE, lw=0.4, alpha=0.6); ax.set_axisbelow(True)
save(fig, "fig_saturation")

# Themes
a = pd.read_csv("../results/themes_prevalence.csv").sort_values("reviews_%")
fig, ax = plt.subplots(figsize=(3.35, 2.6))
y = np.arange(len(a))
ax.barh(y, -a["negative_%"], color=NEG, height=0.62, label="Negative extracts")
ax.barh(y, a["positive_%"], color=POS, height=0.62, label="Positive extracts")
for i, r in zip(y, a.itertuples()):
    ax.text(-a.iloc[i]["negative_%"] - 1.5, i, f"{a.iloc[i]['negative_%']:.0f}", ha="right", va="center", fontsize=6.8, color=INK)
    ax.text(a.iloc[i]["positive_%"] + 1.5, i, f"{a.iloc[i]['positive_%']:.0f}", ha="left", va="center", fontsize=6.8, color=INK)
ax.set_yticks(y); ax.set_yticklabels([f"{NAME[t]} ({p:.0f}%)" for t, p in zip(a["theme"], a["reviews_%"])], fontsize=7.4)
ax.axvline(0, color=INK2, lw=0.7)
ax.set_xlim(-105, 75); ax.set_xticks([-100, -50, 0, 50]); ax.set_xticklabels(["100", "50", "0", "50"])
ax.set_xlabel("Share of the theme's extracts (%)", color=INK2)
ax.spines["left"].set_visible(False)
ax.legend(loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=2, frameon=False, fontsize=7, handlelength=1.1, columnspacing=1.2)
save(fig, "fig_themes")

# Sub-themes
s = pd.read_csv("../results/subthemes.csv")
order = list(NAME)
fig, ax = plt.subplots(figsize=(7, 7.6))
y, ticks, labels = 0, [], []
heads = []
for t in order:
    g = s[s.theme == t].sort_values("or_recommend", ascending=False)
    heads.append((y, NAME[t])); y += 1
    for r in g.itertuples():
        sig = r.p_bh < 0.05
        col = (POS if r.or_recommend > 1 else NEG) if sig else MUTED
        ax.plot([r.or_low, r.or_high], [y, y], color=col, lw=1.1, solid_capstyle="round")
        ax.plot(r.or_recommend, y, "o", ms=4.6, mfc=col if sig else "white", mec=col, mew=1.0)
        ticks.append(y); labels.append(f"{r.subtheme}  ({r.reviews})")
        y += 1
    y += 0.45
ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=7.2)
for yy, name in heads:
    ax.text(-0.005, yy, name, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=7.8, fontweight="bold", color=INK)
ax.axvline(1, color=INK2, lw=0.8)
ax.set_xscale("log"); ax.set_xlim(0.12, 14); ax.set_xticks([0.2, 0.5, 1, 2, 5, 10]); ax.set_xticklabels(["0.2", "0.5", "1", "2", "5", "10"]); ax.minorticks_off()
ax.set_ylim(y - 0.2, -0.8); ax.set_xlabel("Odds ratio of recommending the game (log scale, 95% CI)", color=INK2)
ax.grid(axis="x", color=LINE, lw=0.4, alpha=0.6); ax.set_axisbelow(True); ax.spines["left"].set_visible(False)
ax.text(1.05, -0.55, "goes with recommending →", fontsize=7, ha="left", color=INK2, va="center"); 
ax.text(0.92 * 0.97, -0.55, "← goes with not recommending", fontsize=7, ha="right", color=INK2, va="center")
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([], [], marker="o", ls="-", color=POS, ms=4.6, label="Higher odds, p < .05 (BH)"), Line2D([], [], marker="o", ls="-", color=NEG, ms=4.6, label="Lower odds, p < .05 (BH)"),
                   Line2D([], [], marker="o", ls="-", color=MUTED, mfc="white", ms=4.6, label="Not significant")], loc="upper right", bbox_to_anchor=(1.0, 0.975), frameon=False, fontsize=7)
save(fig, "fig_subthemes_or")
# Design triage map
s = pd.read_csv("../results/design_triage.csv")
s["net"] = s["negative_%"] - s["positive_%"]
ACC = "#6b4fbb"
COL = {"Repair first": NEG, "Accepted friction": ACC, "Protect": POS, "Not decisive": "#c9c8c2"}
fig, ax = plt.subplots(figsize=(7, 4.1))
ax.axvline(0, color=INK2, lw=0.7); ax.axhline(1, color=INK2, lw=0.7)
for g in ["Not decisive", "Protect", "Accepted friction", "Repair first"]:
    x = s[s.group == g]
    ax.scatter(x.net, x.or_recommend, s=x.reviews * 0.85, color=COL[g], alpha=0.5 if g == "Not decisive" else 0.9, edgecolor="white", linewidth=0.8, zorder=3, label=g)
OFF = {"Combat Dynamics": (0, 23, "center"), "Movement and Evasion": (-11, 6, "right"), "Enemy Strength and Balance": (9, 3, "left"), "Performance and Technical Implementation": (-7, -9, "right"),
       "Control and Customization": (-7, 0, "right"), "Crash and Stability": (7, -6, "left"), "Early Game Difficulty": (10, 8, "left"), "Overall Difficulty and Mastery": (-2, 13, "center"),
       "Story Engagement": (-10, 8, "right"), "World Building": (-6, -14, "right"), "Factions and Lore": (11, -7, "left"), "Exploration and Resource Management": (9, 6, "left"),
       "Character Growth and Replayability": (7, 5, "left"), "Gameplay Duration and Engagement": (7, 2, "left"),
       "Bug Impact Spectrum": (0, 10, "center"), "Graphics Quality": (0, 11, "center")}
for r in s.itertuples():
    if r.subtheme in OFF:
        dx, dy, ha = OFF[r.subtheme]
        ax.annotate(r.subtheme.replace("Performance and Technical", "Performance and\nTechnical"), (r.net, r.or_recommend), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=6.9, color=INK if r.group != "Not decisive" else INK2, zorder=4)
ax.set_yscale("log"); ax.set_ylim(0.225, 8.5); ax.set_yticks([0.25, 0.5, 1, 2, 4, 8]); ax.set_yticklabels(["0.25", "0.5", "1", "2", "4", "8"]); ax.minorticks_off()
ax.set_xlim(-92, 112); ax.set_xticks([-75, -50, -25, 0, 25, 50, 75, 100])
ax.set_xlabel("Tone: negative minus positive extracts (percentage points)", color=INK2); ax.set_ylabel("Odds ratio of recommending (log scale)", color=INK2)
ax.tick_params(axis="y", colors=INK2)
for x, y, text, c, ha in [(-90, 7.3, "PROTECT", POS, "left"), (110, 7.3, "ACCEPTED FRICTION", ACC, "right"), (110, 0.255, "REPAIR FIRST", NEG, "right")]:
    ax.text(x, y, text, fontsize=8.2, fontweight="bold", color=c, ha=ha, va="center")
save(fig, "fig_triage")
print("done")
