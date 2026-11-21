"""The post's figure: tri-agency papers free to read vs. with a Canadian repository copy, by year.

Reads results/routes_by_year.csv (from build_monitor.py) and writes figure.png. Needs matplotlib.

    python3 scripts/make_figure.py
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent.parent
NAVY, TEAL, SKY, TEXT, MUTED, RULE = "#103f54", "#04a89f", "#a1d2ea", "#1d2a33", "#5d6b75", "#e3eaef"

names = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams["font.family"] = next((f for f in ["Avenir Next", "Avenir", "Helvetica Neue", "Arial"] if f in names), "sans-serif")

rows = [r for r in csv.DictReader(open(ROOT / "results" / "routes_by_year.csv")) if r["set"] == "tri"]
years = [int(r["y"]) for r in rows]
free = [100 * (int(r["n"]) - int(r["closed"])) / int(r["n"]) for r in rows]
repo = [100 * int(r["carepo"]) / int(r["n"]) for r in rows]

fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
fig.subplots_adjust(left=0.08, right=0.80, top=0.80, bottom=0.10)
ax.fill_between(years, repo, free, color=SKY, alpha=0.35, linewidth=0)
ax.plot(years, free, color=NAVY, linewidth=5)
ax.plot(years, repo, color=TEAL, linewidth=5)
ax.scatter([years[-1]], [free[-1]], color=NAVY, s=90, zorder=3)
ax.scatter([years[-1]], [repo[-1]], color=TEAL, s=90, zorder=3)
ax.text(years[-1] + 0.4, free[-1], f"{free[-1]:.0f}%", color=NAVY, fontsize=40, fontweight="bold", va="center")
ax.text(years[-1] + 0.4, free[-1] - 7, "free to read", color=NAVY, fontsize=19, va="center")
ax.text(years[-1] + 0.4, repo[-1] + 13, f"{repo[-1]:.0f}%", color=TEAL, fontsize=40, fontweight="bold", va="center")
ax.text(years[-1] + 0.4, repo[-1] + 2, "in a Canadian\nrepository", color=TEAL, fontsize=19, va="center", linespacing=1.1)
fig.text(0.08, 0.92, "Free to read, but rarely in a Canadian repository", color=TEXT, fontsize=27, fontweight="bold")
fig.text(0.08, 0.865, "Papers acknowledging CIHR, NSERC or SSHRC, by publication year (OpenAlex)", color=MUTED, fontsize=18)
ax.set_ylim(0, 100)
ax.set_xlim(years[0], years[-1])
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=16, color=MUTED)
ax.set_xticks([years[0], 2015, 2020, years[-1]])
ax.set_xticklabels([str(years[0]), "2015", "2020", str(years[-1])], fontsize=16, color=MUTED)
ax.grid(axis="y", color=RULE, linewidth=1.2)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(RULE)
ax.tick_params(length=0)
fig.savefig(ROOT / "figure.png", facecolor="white")
print("wrote", ROOT / "figure.png")
