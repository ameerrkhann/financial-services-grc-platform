# build_charts.py
# Generates the static chart images used in the README and the executive PDF.
#
# Series colours use a validated categorical palette (worst adjacent CVD
# delta-E 8.4 on the dark surface), so the five scenario curves stay
# distinguishable under deuteranopia, protanopia and tritanopia. Cyan is kept
# as a UI accent for titles and annotations only, never as a series colour.

import os
import json

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)

# ── Design tokens ─────────────────────────────────────────────────────
SURFACE      = "#0f1117"   # page background
PLOT_SURFACE = "#1a1a1a"   # chart surface (the validator's dark surface)
TEXT_PRIMARY = "#ffffff"
TEXT_SECOND  = "#a9b2c7"
GRID         = "#2a2f45"
ACCENT       = "#00d4ff"   # UI accent — titles and annotations only

# Validated categorical palette, dark mode, in fixed slot order.
SERIES = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "figure.facecolor": SURFACE,
    "axes.facecolor": PLOT_SURFACE,
    "savefig.facecolor": SURFACE,
})


def money_fmt(x, _=None):
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:.0f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:.0f}K"
    return f"${x:.0f}"


def style_axes(ax, xlabel=None, ylabel=None):
    ax.tick_params(colors=TEXT_SECOND, labelsize=9)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color(GRID)
    ax.grid(True, alpha=0.35, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    if xlabel:
        ax.set_xlabel(xlabel, color=TEXT_SECOND, fontsize=10, labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, color=TEXT_SECOND, fontsize=10, labelpad=8)


# ──────────────────────────────────────────────────────────────────────
# 1. Loss exceedance curves — all five scenarios
# ──────────────────────────────────────────────────────────────────────

def loss_exceedance_chart():
    sims = np.load(os.path.join(OUT, "simulations.npz"))
    scen = pd.read_json(os.path.join(OUT, "RiskScenarios.json"))

    fig, ax = plt.subplots(figsize=(11, 6.2))
    fig.subplots_adjust(left=0.09, right=0.97, top=0.85, bottom=0.13)

    handles = []
    for i, row in scen.iterrows():
        losses = sims[row["scenario_key"]]
        xmax = np.percentile(losses, 99.5)
        xs = np.linspace(0, xmax, 220)
        ys = [np.mean(losses > x) * 100 for x in xs]
        colour = SERIES[i % len(SERIES)]
        ax.plot(xs, ys, color=colour, linewidth=2.0, solid_capstyle="round",
                zorder=3 + i)
        handles.append(Patch(facecolor=colour,
                             label=f"{row['scenario_short']}  ·  ALE ${row['ale']/1e6:.2f}M"))

    ax.axhline(10, color=TEXT_SECOND, linestyle=":", linewidth=1, alpha=0.5, zorder=2)
    ax.annotate("1-in-10 year threshold", xy=(ax.get_xlim()[1] * 0.62, 11.5),
                color=TEXT_SECOND, fontsize=8.5, style="italic")

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.set_xlim(0, None)
    ax.set_ylim(0, 100)
    style_axes(ax, "Annual loss", "Probability of exceeding that loss")

    fig.text(0.09, 0.945, "Loss Exceedance Curves — All Threat Scenarios",
             color=TEXT_PRIMARY, fontsize=15, fontweight="bold", ha="left")
    fig.text(0.09, 0.90,
             "First National Bank (Fictional)  ·  FAIR methodology  ·  100,000 Monte Carlo simulations per scenario",
             color=TEXT_SECOND, fontsize=9.5, ha="left")

    leg = ax.legend(handles=handles, loc="upper right", frameon=True,
                    facecolor=PLOT_SURFACE, edgecolor=GRID, fontsize=9.5,
                    labelcolor=TEXT_PRIMARY, borderpad=0.8, labelspacing=0.65)
    leg.get_frame().set_linewidth(0.8)

    path = os.path.join(OUT, "lec_all_scenarios.png")
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)
    print(f"  wrote {os.path.basename(path)}")
    return path


# ──────────────────────────────────────────────────────────────────────
# 2. NIST CSF 2.0 maturity radar — current vs target
# ──────────────────────────────────────────────────────────────────────

def csf_radar_chart():
    csf = pd.read_json(os.path.join(OUT, "CSFScores.json")).sort_values("function_order")
    labels = csf["function_name"].tolist()
    current = csf["score"].tolist()
    target = csf["target_score"].tolist()

    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    cur = current + current[:1]
    tgt = target + target[:1]

    fig = plt.figure(figsize=(8.6, 8.0))
    ax = fig.add_subplot(111, polar=True)
    fig.subplots_adjust(top=0.82, bottom=0.10)
    ax.set_facecolor(PLOT_SURFACE)

    ax.plot(angles, tgt, color=TEXT_SECOND, linewidth=1.6, linestyle="--",
            label="Target maturity (4)", zorder=3)
    ax.plot(angles, cur, color=SERIES[0], linewidth=2.4, label="Current maturity",
            zorder=5, solid_capstyle="round")
    ax.fill(angles, cur, color=SERIES[0], alpha=0.22, zorder=4)
    ax.scatter(angles[:-1], current, s=70, color=SERIES[0],
               edgecolors=PLOT_SURFACE, linewidths=2, zorder=6)

    # Direct-label each vertex with its score — identity is never colour-alone
    for ang, val, lo in zip(angles[:-1], current, labels):
        ax.annotate(f"{val}", xy=(ang, val), xytext=(0, -16),
                    textcoords="offset points", ha="center", va="center",
                    color=TEXT_PRIMARY, fontsize=10, fontweight="bold", zorder=7)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color=TEXT_PRIMARY, fontsize=11.5, fontweight="bold")
    ax.tick_params(axis="x", pad=18)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], color=TEXT_SECOND, fontsize=8.5)
    ax.grid(color=GRID, alpha=0.7, linewidth=0.8)
    ax.spines["polar"].set_color(GRID)

    overall = float(np.mean(current))
    fig.text(0.5, 0.945, "NIST CSF 2.0 Maturity — Current vs Target",
             color=TEXT_PRIMARY, fontsize=15.5, fontweight="bold", ha="center")
    fig.text(0.5, 0.902,
             f"First National Bank (Fictional)  ·  Overall {overall:.1f} / 5.0  ·  Target 4.0",
             color=TEXT_SECOND, fontsize=10, ha="center")

    leg = ax.legend(loc="upper right", bbox_to_anchor=(1.16, 1.09), frameon=True,
                    facecolor=PLOT_SURFACE, edgecolor=GRID, fontsize=9.5,
                    labelcolor=TEXT_PRIMARY)
    leg.get_frame().set_linewidth(0.8)

    path = os.path.join(OUT, "csf_radar.png")
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)
    print(f"  wrote {os.path.basename(path)}")
    return path


# ──────────────────────────────────────────────────────────────────────
# 3. Risk vs control investment — where the money goes
# ──────────────────────────────────────────────────────────────────────

def risk_reduction_chart():
    scen = pd.read_json(os.path.join(OUT, "RiskScenarios.json")).sort_values("ale", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 5.6))
    fig.subplots_adjust(left=0.20, right=0.94, top=0.82, bottom=0.14)

    y = np.arange(len(scen))
    h = 0.62
    residual = scen["residual_ale"].values
    reduced = scen["ale"].values - residual

    ax.barh(y, residual, height=h, color=SERIES[1], zorder=3,
            label="Residual ALE (risk remaining after controls)")
    ax.barh(y, reduced, height=h, left=residual + (scen["ale"].values * 0.004),
            color=SERIES[2], zorder=3,
            label="Risk reduced by recommended controls")

    for i, row in enumerate(scen.itertuples()):
        ax.annotate(f"${row.ale/1e6:.2f}M", xy=(row.ale, y[i]), xytext=(8, 0),
                    textcoords="offset points", va="center",
                    color=TEXT_PRIMARY, fontsize=9.5, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels(scen["scenario_short"], color=TEXT_PRIMARY, fontsize=10.5)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
    ax.set_xlim(0, scen["ale"].max() * 1.16)
    style_axes(ax, "Annualised loss expectancy", None)
    ax.grid(axis="y", visible=False)

    fig.text(0.02, 0.945, "Where the Risk Sits — and What Controls Remove",
             color=TEXT_PRIMARY, fontsize=15, fontweight="bold", ha="left")
    fig.text(0.02, 0.898,
             "Control effectiveness is an assumption (60–80% by scenario), not a measured value.",
             color=TEXT_SECOND, fontsize=9.5, ha="left")

    leg = ax.legend(loc="lower right", frameon=True, facecolor=PLOT_SURFACE,
                    edgecolor=GRID, fontsize=9.5, labelcolor=TEXT_PRIMARY)
    leg.get_frame().set_linewidth(0.8)

    path = os.path.join(OUT, "risk_reduction.png")
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)
    print(f"  wrote {os.path.basename(path)}")
    return path


# ──────────────────────────────────────────────────────────────────────
# 4. Vendor portfolio by risk tier
# ──────────────────────────────────────────────────────────────────────

def vendor_tier_chart():
    v = pd.read_json(os.path.join(OUT, "VendorAssessments.json"))
    tiers = ["Critical", "High", "Medium", "Low"]
    counts = [int((v["risk_tier"] == t).sum()) for t in tiers]

    # Tier is an ordered severity scale, so this is a sequential/status encoding,
    # not categorical identity. Each bar is direct-labelled with its count.
    tier_colours = ["#c0392b", "#d95926", "#c98500", "#199e70"]

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    fig.subplots_adjust(left=0.10, right=0.96, top=0.78, bottom=0.16)

    bars = ax.bar(tiers, counts, width=0.62, color=tier_colours, zorder=3)
    for b, c in zip(bars, counts):
        ax.annotate(str(c), xy=(b.get_x() + b.get_width() / 2, c),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", color=TEXT_PRIMARY, fontsize=13, fontweight="bold")

    ax.set_ylim(0, max(counts) + 1.2)
    ax.set_yticks(range(0, max(counts) + 2))
    style_axes(ax, None, "Vendors")
    ax.grid(axis="x", visible=False)
    ax.tick_params(axis="x", labelsize=11, colors=TEXT_PRIMARY)

    overdue = int((v["is_overdue"] == "TRUE").sum())
    fig.text(0.03, 0.93, "Vendor Portfolio by Risk Tier",
             color=TEXT_PRIMARY, fontsize=14.5, fontweight="bold", ha="left")
    fig.text(0.03, 0.865,
             f"{len(v)} vendors assessed  ·  {overdue} overdue for reassessment under OSFI B-10 cycles",
             color=TEXT_SECOND, fontsize=9.5, ha="left")

    path = os.path.join(OUT, "vendor_tiers.png")
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)
    print(f"  wrote {os.path.basename(path)}")
    return path


if __name__ == "__main__":
    print("Generating charts...")
    loss_exceedance_chart()
    csf_radar_chart()
    risk_reduction_chart()
    vendor_tier_chart()
    print("Done.")
