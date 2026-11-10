"""Writes the LaTeX tables of the paper from results/ and the coding outputs. Usage (from pipeline/): ../../venv/bin/python ../scripts/07_tables.py. Run 09_design_triage.py first.
Needs praxiology_macros.tex in the preamble (colortbl, arydshln, adjustbox, fontawesome5, the pr* colors and \\prgroup).
Colors have one meaning everywhere: coral = problem or lower odds, lilac = accepted friction, blue = strength or higher odds."""
import json

import pandas as pd

NAME = {"STORYTELLING": "Storytelling", "MECHANICS": "Mechanics", "CHALLENGE": "Challenge", "PROGRESSION_CONTENT": "Progression and content",
        "ONBOARDING": "Onboarding", "UI": "UI", "AUDIOVISUAL": "Audiovisual", "SYSTEM": "System", "LIVE_DEVELOPMENT": "Live development"}
ICON = {"STORYTELLING": r"\faBook", "MECHANICS": r"\faCogs", "CHALLENGE": r"\faMountain", "PROGRESSION_CONTENT": r"\faChartLine", "ONBOARDING": r"\faMapSigns",
        "UI": r"\faDesktop", "AUDIOVISUAL": r"\faMusic", "SYSTEM": r"\faBug", "LIVE_DEVELOPMENT": r"\faTools"}
ORDER = list(NAME)
T = "../Paper/tables/"
num = lambda x, d=1: f"{x:.{d}f}"
tex = lambda s: s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
sc = lambda t: rf"\textsc{{{NAME[t]}}}"
scicon = lambda t: rf"\textcolor{{prIcon}}{{{ICON[t]}}}\hspace{{0.5em}}\textsc{{{NAME[t]}}}"
star = lambda p: "$^{***}$" if p < .001 else "$^{**}$" if p < .01 else "$^{*}$" if p < .05 else ""
hi = lambda text, color: rf"\cellcolor{{{color}}}\textbf{{{text}}}"
key = lambda text, color: rf"\colorbox{{{color}}}{{{text}}}"
STARS = r"$^{*}p<.05$, $^{**}p<.01$, $^{***}p<.001$"
BLACK, DASH = r"\arrayrulecolor{black}\midrule", r"\arrayrulecolor{prRule}\hdashline"
STYLE = {"Repair first": ("prNegBand", "prNegIcon", r"\faWrench", "prNeg"), "Accepted friction": ("prAccBand", "prAccIcon", r"\faBalanceScale", "prAcc"),
         "Protect": ("prPosBand", "prPosIcon", r"\faHeart", "prPos")}


def group(cols, color, icon_color, icon, name, text=""):
    return ("group", rf"\prgroup{{{cols}}}{{{color}}}{{{icon_color}}}{{{icon}}}{{{name}}}{{{text}}}")


def bold_header(line):
    if line.startswith(r"\arrayrulecolor"):
        return "    " + line
    cells = [c.strip() for c in line.split("&")]
    cells = [c if not c or "multicolumn" in c or "textbf" in c else rf"\textbf{{{c}}}" for c in cells]
    return "    \\rowcolor{prHead}\n    " + " & ".join(cells) + r" \\"


def write(name, label, caption, spec, head, items, size="footnotesize", stretch="1.15", place="ht", inner=False):
    """head: header rows. items: rows, or (kind, text) with kind group or total. inner: dashed line between the rows of a group too."""
    previous, body = None, []
    for item in items:
        kind, text = item if isinstance(item, tuple) else ("row", item)
        if kind == "row":
            if previous == "row" and inner:
                body.append("    " + DASH)
            body.append("    " + text + r" \\")
        elif kind == "group":
            if previous is not None:
                body.append("    " + DASH)
            body.append("    " + text + r" \\")
        else:
            body.append("    " + BLACK)
            body.append("    \\rowcolor{prTotal}\n    " + text + r" \\")
        previous = kind
    text = rf"""\begin{{table*}}[{place}]
  \centering
  \{size}
  \caption{{{caption}}}
  \label{{{label}}}
  \setlength{{\tabcolsep}}{{4pt}}
  \renewcommand{{\arraystretch}}{{{stretch}}}
  \setlength{{\aboverulesep}}{{0pt}}
  \setlength{{\belowrulesep}}{{0pt}}
  \setlength{{\dashlinedash}}{{2pt}}
  \setlength{{\dashlinegap}}{{2pt}}
  \begin{{adjustbox}}{{max width=\linewidth, max totalheight=0.85\textheight}}
  \begin{{tabular}}{{{spec}}}
    \toprule
""" + "\n".join(bold_header(h) for h in head) + "\n    " + BLACK + "\n" + "\n".join(body) + r"""
    \arrayrulecolor{black}\bottomrule
  \end{tabular}
  \end{adjustbox}
\end{table*}
"""
    open(T + name, "w", encoding="utf-8").write(text)


P = r">{\raggedright\arraybackslash}p"

# 1. Themes
a = pd.read_csv("../results/themes_prevalence.csv").set_index("theme").sort_values("negative_%", ascending=False)


def reading(r):
    if r["negative_%"] >= 70:
        return "Mostly criticized", "prNeg"
    if abs(r["positive_%"] - r["negative_%"]) < 5:
        return "Divided", "prButter"
    return ("Leans negative", "prPeach") if r["negative_%"] > r["positive_%"] else ("Leans positive", "prPos")


rows = []
for t, r in a.iterrows():
    neg = num(r["negative_%"]); pos = num(r["positive_%"])
    rows.append(rf"{scicon(t)} & {int(r.reviews)} & {num(r['reviews_%'])} [{num(r.ci_low)}, {num(r.ci_high)}] & {int(r.extracts):,} & {hi(neg, 'prNeg') if r['negative_%'] >= 70 else neg} & {num(r['neutral_%'])} & {hi(pos, 'prPos') if r['positive_%'] >= 50 else pos} & \cellcolor{{{reading(r)[1]}}}{reading(r)[0]}")
write("tab_themes.tex", "tab:themes", r"Themes in the 1,200 sampled reviews, from the most to the least criticized: reviews mentioning the theme (share with 95\% Wilson CI), extracts, and tone of the extracts (\%). " + key("Coral", "prNeg") + r": at least 70\% negative. " + key("Blue", "prPos") + r": at least 50\% positive.",
      "l r c r r r r l", [r"Theme & Reviews & \% [95\% CI] & Extracts & Neg.\ \% & Neu.\ \% & Pos.\ \% & Reading"], rows, size="small")

# 2. Design triage
s = pd.read_csv("../results/design_triage.csv")


def or_cell(r):
    text = f"{num(r.or_recommend, 2)} [{num(r.or_low, 2)}, {num(r.or_high, 2)}]{star(r.p_bh)}"
    return hi(text, "prPos" if r.or_recommend > 1 else "prNeg") if r.p_bh < .05 else text


def critics(v):
    return hi(num(v), "prNeg") if v < 50 else hi(num(v), "prPos") if v >= 70 else num(v)


items = []
for g, text in [("Repair first", "criticized, and goes with not recommending"), ("Accepted friction", "criticized, yet goes with recommending"), ("Protect", "praised, and goes with recommending")]:
    band, icon_color, icon, _ = STYLE[g]
    items.append(group(7, band, icon_color, icon, g, text))
    for i, r in s[s.group == g].sort_values("reviews", ascending=False).iterrows():
        items.append(rf"{tex(r.subtheme)} & {sc(r.theme)} & {r.reviews} & {num(r['negative_%'])} & {num(r['positive_%'])} & {or_cell(r)} & {critics(r['critics_recommend_%'])}")
n = int((s.group == "Not decisive").sum())
items.append(group(7, "prGrey", "prIcon", r"\faMinusCircle", "Not decisive", rf"{n} further sub-themes with no significant association (Appendix~\ref{{sec:appendix}})"))
write("tab_triage.tex", "tab:triage", r"Design triage: the 14 of 43 sub-themes that call for a decision. Reviews mentioning the sub-theme, negative and positive extracts (\%), odds ratio of recommending the game for reviews that mention it (95\% CI, unadjusted), and share of reviews with at least one negative extract on the sub-theme that still recommend the game (\%; 70\% of all reviews do). Odds ratios: " + key("lower", "prNeg") + " or " + key("higher", "prPos") + " odds of recommending. Critics: " + key(r"below 50\%", "prNeg") + " or " + key(r"70\% or more", "prPos") + ". " + STARS + ", Benjamini--Hochberg over the 43 sub-themes.",
      "l l r r r c r", [r"Sub-theme & Theme & Rev. & Neg.\ \% & Pos.\ \% & OR [95\% CI] & Critics rec.\ \%"], items)

# 3. From complaint to design change. Quotes are verbatim from the reviews; the changes are the authors' hypotheses.
CARDS = [
    ("Repair first", [
        ("Control and Customization", "Design", r"``Keybinds are NOT fully customizable''; ``make it a different key to sit in chairs and lay in beds then it is to loot''", "Full key rebinding; separate the interaction keys that collide", "Fewer negative extracts on bindings and context keys"),
        ("Combat Dynamics", "Design", r"``your guy just stands there and doesn't swing his weapon''; ``enemy animations that will hit even when you are not in there `shown' hit zone''; ``stamina on NORMAL needs to be like 20\% less use per hit''", "Input response on attacks; align hit zones with animations; retune stamina cost by difficulty", "Codes on response, hit detection and stamina, separately"),
        ("Movement and Evasion", "Design", r"``even rolling around is a waste of stamina during combat''; ``character's movement feels like pushing a bag of rice''", "Lower the stamina cost of dodging; shorten acceleration and stopping", "Share of critics who still recommend (now 33\%)"),
        ("Enemy Strength and Balance", "Design", r"``Strong NPCs are randomly distributed and they can one-shot you''", "Keep dangerous enemies, but signal their strength before contact", "Complaints about surprise deaths versus complaints about strength"),
        ("Crash and Stability", "System", r"``the game black screens at the 5 hour mark''; ``this game continues to crash to desktop upon starting''", "Use the moments players name (start-up, first city, final cutscene) as reproduction cases", "Crash codes by the moment reported"),
        ("Performance and Technical Implementation", "System", r"``Game needs updating for 5000 series gpu's''", "Compatibility pass on current hardware", "Reviews by date: does the complaint follow new hardware?"),
    ]),
    ("Accepted friction", [
        ("Early Game Difficulty", "Design", r"``Combat is tough until you reach level 15 or so and then it becomes pretty easy''", "Keep the weak start; state it as a promise of growth; look at the later drop in challenge instead", "Critics who recommend should stay above the average"),
    ]),
    ("Protect", [
        ("Character Growth and Replayability", "Design", r"``rewarding progress, with actual zero to hero''; ``replay value with 3 different factions and different play styles''", "Check every balance change against the length of the growth arc", "Positive extracts should not fall after a rebalance"),
    ]),
]
items = []
for g, cards in CARDS:
    band, icon_color, icon, _ = STYLE[g]
    items.append(group(4, band, icon_color, icon, g))
    items += [rf"\textbf{{{sub}}} ({kind}) & {quote} & {change} & {check}" for sub, kind, quote, change, check in cards]
write("tab_cards.tex", "tab:cards", r"From complaint to design change. For each priority: what players point at, in their own words; a possible change; what to look for in the reviews written after it. Quotes are verbatim. The changes and checks are the authors' hypotheses and have not been tested.",
      rf"{P}{{0.19\textwidth}} {P}{{0.33\textwidth}} {P}{{0.2\textwidth}} {P}{{0.17\textwidth}}", ["Issue & What players point at & Possible change & What to re-read"], items, inner=True)

# 4. Models
m, b = [pd.read_csv(f"../results/{f}.csv", index_col=0) for f in ("recommendation_model", "recommendation_model_both_encoders")]
p = pd.read_csv("../results/playtime_model.csv", index_col=0)


def cell(d, k):
    if k not in d.index:
        return "--"
    text = f"{num(d.loc[k, 'or'], 2)} [{num(d.loc[k, 'low'], 2)}, {num(d.loc[k, 'high'], 2)}]{star(d.loc[k, 'p_bh'])}"
    return hi(text, "prPos" if d.loc[k, "or"] > 1 else "prNeg") if d.loc[k, "p_bh"] < .05 else text


def play(t):
    text = f"{num(p.loc[t, 'pct_change'], 0)} [{num(p.loc[t, 'low'], 0)}, {num(p.loc[t, 'high'], 0)}]{star(p.loc[t, 'p_bh'])}"
    return hi(text, "prPos" if p.loc[t, "pct_change"] > 0 else "prNeg") if p.loc[t, "p_bh"] < .05 else text


write("tab_models.tex", "tab:models", r"Models at review level ($N=1{,}200$). Odds ratios of recommending the game for at least one positive or negative extract on the theme (logit with log hours and language, HC1 errors); the third column repeats the negative term using only extracts proposed by both encoders. Last column: difference in total playtime (\%) for reviews that mention the theme (OLS on log hours with recommendation and language, HC3 errors). In brackets, 95\% CIs. Significant results: " + key("lower", "prNeg") + " or " + key("higher", "prPos") + ". -- = term left out (perfect separation). " + STARS + ", Benjamini--Hochberg within each family.",
      "l c c c c", ["Theme & Praised & Criticized & Criticized (both encoders) & Playtime, \\%"],
      [rf"{scicon(t)} & {cell(m, t + '_pos')} & {cell(m, t + '_neg')} & {cell(b, t + '_neg')} & {play(t)}" for t in ORDER], size="small")

# 5. Coding quality
c = pd.read_csv("../results/position_check.csv").set_index("theme")
r = pd.read_csv("sample/reassignment_report.csv").set_index("theme")
book = json.load(open("sample/subtheme_codebook.json", encoding="utf-8"))
flag = lambda bad, text: hi(text, "prNeg") if bad else text
rows = []
for t in ORDER:
    if t not in book["themes"]:
        continue
    last = book["diagnostics"][t][-1]
    k, u, ka, ua, ko = float(last["kappa"]), float(last["unassigned_%"]), r.loc[t, "kappa"], r.loc[t, "unassigned_%"], c.loc[t, "kappa_forward_reversed"]
    rows.append(rf"{scicon(t)} & {len(book['themes'][t])} & {flag(k < .7, num(k, 2))} & {flag(u > 10, num(u))} & {flag(ka < .7, num(ka, 2))} & {flag(ua > 10, num(ua))} & {flag(ko < .7, num(ko, 2))}")
write("tab_codebook.tex", "tab:codebook", r"Sub-theme coding: number of sub-themes; Cohen's $\kappa$ between Phi-4 and Gemma~4 and unassigned codes (\%) in the final codebook test (160 codes per theme) and on all distinct codes at reassignment; $\kappa$ between the original and the reversed order of the sub-themes. " + key("Coral", "prNeg") + r": $\kappa<0.70$ or more than 10\% unassigned.",
      "l r r r r r r", [r"& & \multicolumn{2}{c}{\textbf{Codebook test}} & \multicolumn{2}{c}{\textbf{All codes}} & \textbf{Order}", r"\arrayrulecolor{prRule}\cdashline{3-4}\cdashline{5-6}", r"Theme & Sub. & $\kappa$ & Unass. & $\kappa$ & Unass. & $\kappa$"], rows, size="small")

# 6. All sub-themes (appendix)
items = []
for t in ORDER:
    items.append(group(7, "prBand", "prIcon", ICON[t], NAME[t]))
    for i, x in s[s.theme == t].sort_values("reviews", ascending=False).iterrows():
        label = rf"\cellcolor{{{STYLE[x.group][3]}}}{x.group}" if x.group in STYLE else x.group
        items.append(rf"{tex(x.subtheme)} & {x.reviews} & {x.extracts} & {num(x['negative_%'])} & {num(x['positive_%'])} & {or_cell(x)} & {label}")
write("tab_subthemes.tex", "tab:subthemes", r"All sub-themes: reviews mentioning them, extracts, negative and positive extracts (\%), odds ratio of recommending the game (95\% CI, unadjusted) and triage group. Significant odds ratios: " + key("lower", "prNeg") + " or " + key("higher", "prPos") + ". " + STARS + ", Benjamini--Hochberg over the 43 sub-themes.",
      "l r r r r c l", [r"Sub-theme & Rev. & Extr. & Neg.\ \% & Pos.\ \% & OR [95\% CI] & Group"], items, stretch="1.05", place="htbp")

# 6b. Cost and yield of smaller samples (14_sample_size_cost.py)
z = pd.read_csv("../results/sample_size_cost.csv")
rows = []
for _, q in z.iterrows():
    found = f"{q.priorities_found_mean:.1f}" if q.n < 1200 else "14"
    col = "prPos" if q.priorities_found_mean >= 14 else "prNeg" if q.priorities_found_mean < 7 else None
    rows.append(rf"{int(q.n):,} & {q.total_hours:.1f} & {int(q.distinct_codes):,} & {int(q.reviews_with_extracts):,} & {hi(found, col) if col else found} & {int(q.priorities_found_p5) if q.n < 1200 else '--'} & {q.new_priorities_mean:.1f}".replace(",", "{,}"))
write("tab_samplesize.tex", "tab:samplesize", r"Cost and yield of smaller samples, estimated by drawing 200 random subsamples of each size from the 1,200 coded reviews. Machine time from the rates measured in the use case, without the filter (which depends on the corpus). Priorities: sub-themes in a triage group other than not decisive, compared with the 14 found with 1,200 reviews (mean and 5th percentile over the draws); new: priorities not among the 14. " + key("Coral", "prNeg") + ": fewer than half of the 14 found.",
      "r r r r c r r", [r"Reviews & Hours & Distinct codes & With extracts & Priorities found & 5th pct. & New"], rows, size="small")

# 6c. The design brief as generated (pipeline/4_design_brief.py)
brief = json.load(open("sample/design_brief.json", encoding="utf-8"))
NAMES = {"R": "Repair first", "A": "Accepted friction", "P": "Protect", "C": "Contested"}
TEXT = {"Repair first": "criticized, and goes with not recommending", "Accepted friction": "criticized, yet goes with recommending", "Protect": "praised, and goes with recommending"}
items, last = [], None
for d in brief["drafts"]:
    if d["group"] != last:
        band, icon_color, icon, _ = STYLE[d["group"]]
        items.append(group(4, band, icon_color, icon, d["group"], TEXT.get(d["group"], "")))
        last = d["group"]
    q = d["quotes"][0]
    quote = "``" + tex(q["shown"].replace("’", "'")) + "''" + (r" \textit{(transl.)}" if q["translated"] else "")
    items.append(rf"\textbf{{{d['id']}}} & {tex(d['subtheme'])} & {tex(d['requirement'])} & {quote}")
write("tab_brief.tex", "tab:brief", r"The 14 requirements of the design brief, as written by Phi-4 before any review, with the first quote the model chose for each (verbatim; \textit{transl.}: translated by the model from another language). The PDF adds, for each requirement, the reason, the evidence, a second quote, a possible change, what to check in later reviews and a decision box (Appendix~\ref{sec:appendix-brief}).",
      rf"l {P}{{0.18\textwidth}} {P}{{0.38\textwidth}} {P}{{0.32\textwidth}}", ["ID & Aspect & Requirement (model draft) & Players say"], items, inner=True)

# 7. Using the pipeline: steps, cost, what the team does. Times measured on the ELEX run (timestamps of the output files); see the paper.
USE = [("Phase A: corpus and sampling", "prMint", "prMintIcon", r"\faDatabase", [("Collection", "Corpus", "under 1 h$^{a}$", "Give the Steam app id"),
                                         ("Cleaning and filter", "Corpus (0.55 s per judged review)", "1 h 41", "Choose the population; rules are preset"),
                                         ("Sampling", "--", "seconds", "Choose the sample size, or skip")]),
       ("Phase B: coding and checks", "prPosBand", "prPosIcon", r"\faRobot", [("Encoding", "Sample (22 s per review)", "7 h 16", "None, once configured"),
                                       ("Inductive codebook", "Nearly fixed", "45 min", "Read the sub-themes; fix a definition if a theme fails"),
                                       ("Harmonization", "Reviews with extracts (18 s each)", "about 5 h", "None"),
                                       ("Assignment and checks", "Distinct codes", "1 h 26", "Read the flagged sub-themes")]),
       ("Phase C: design reading", "prPeach", "prPeachIcon", r"\faLightbulb", [("Saturation, analysis, triage", "--", "minutes", "Run the scripts"),
                                       ("Design brief (PDF)", "Priorities (about 9 s each)", "about 2.5 min", "Accept, modify or reject each requirement")])]
items = []
for phase, band, icon_color, icon, steps in USE:
    items.append(group(4, band, icon_color, icon, phase))
    items += [rf"{a_} & {b_} & \textbf{{{c_}}} & {d_}" for a_, b_, c_, d_ in steps]
items.append(("total", r"\textbf{Machine time} & & \textbf{about 16 h} &"))
items.append(group(4, "prButter", "prButterIcon", r"\faUsers", "Work by people"))
items += [r"Configuration & Study & \multicolumn{2}{l}{Define themes, write few-shot examples \textbf{[TO COMPLETE: hours]}}",
          r"Design reading & Priorities & \multicolumn{2}{l}{Read the extracts of each priority, decide \textbf{[TO COMPLETE: hours]}}",
          r"Human validation & Subsample & \multicolumn{2}{l}{Blind coding of a subsample of reviews \textbf{[TO COMPLETE: hours]}}"]
write("tab_usage.tex", "tab:usage", r"Running the pipeline: what each step scales with, the time it took for 1,200 reviews sampled from 11,092 judged by the filter, and what the team has to do. Phases as in Figure~\ref{fig:pipeline}. Encoding ran one request at a time, harmonization two. $^{a}$Not logged.",
      rf"l l l {P}{{0.3\textwidth}}", ["Step & Scales with & Time & What the team does"], items)

# 8. Requirements
write("tab_requirements.tex", "tab:requirements", r"What is needed to run the pipeline. Hardware is what we used, not a tested minimum.",
      rf"l {P}{{0.5\textwidth}}", ["Requirement & Use case"],
      [group(2, "prMint", "prMintIcon", r"\faLaptop", "Machine"), "Computer & Apple M5 Pro, 18 CPU and 20 GPU cores, 24 GB of memory", "Disk & 28 GB for the four models, under 150 MB for one study", "Network & Only to collect reviews and download the models",
       group(2, "prPosBand", "prPosIcon", r"\faCode", "Software"), "Runtime & Ollama, Python 3.9 or later; a LaTeX engine (e.g. tectonic) for the PDF of the brief", r"Models & Gemma~4 (8B), Qwen~2.5 (14B), Phi-4 (14B), \texttt{nomic-embed-text}", "Cost & No API fees; reviews never leave the machine",
       group(2, "prPeach", "prPeachIcon", r"\faUsers", "People"), "Skills & Running scripts from a terminal, editing one JSON file", "Knowledge & A designer who knows the game, to read the priorities", "Languages & None required to run it; extracts are kept in the original language"], size="small")
print("tables written")
