# src/compliance/csf_radar.py
# NIST CSF 2.0 maturity radar — current vs target across the 6 functions
# Saves dashboards/csf_radar.png
#
# Power BI web may block the AppSource radar visual on a university tenant,
# so this matplotlib version is the reliable one for the README and LinkedIn.

import sys
import os

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.compliance.csf_data import CSF_FUNCTIONS, DEFAULT_TARGET_SCORE
from src.database.db_manager import get_connection, initialise_database

CHARTS_DIR = os.path.join(os.path.dirname(__file__), "../../dashboards")
os.makedirs(CHARTS_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(CHARTS_DIR, "csf_radar.png")

# Same palette as loss_exceedance.py so the charts read as one set
FIG_BG     = "#0f0f0f"
PLOT_BG    = "#1a1a1a"
CURRENT    = "#00d4ff"
TARGET     = "#ffdd00"
INK        = "#ffffff"
INK_MUTED  = "#9a9a9a"
GRID       = "#444444"


def get_latest_scores():
    """
    Returns (org_name, [(function, current, target), ...]) for the latest
    assessment, ordered by the CSF 2.0 function order.

    Functions are read from the database, not hardcoded, so the chart always
    matches whatever seed_demo_data.py or the interactive scorer last wrote.
    """
    conn = get_connection()
    assessment = conn.execute(
        "SELECT id, org_name FROM assessments ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if assessment is None:
        conn.close()
        raise SystemExit(
            "  No assessment found. Run src/database/seed_demo_data.py first."
        )

    rows = conn.execute(
        """SELECT function_name, score, target_score
           FROM function_scores WHERE assessment_id = ?""",
        (assessment["id"],),
    ).fetchall()
    conn.close()

    by_name = {r["function_name"]: r for r in rows}
    scores  = []
    for func_name in CSF_FUNCTIONS:
        row = by_name.get(func_name)
        if row is None:
            continue
        target = row["target_score"] or DEFAULT_TARGET_SCORE
        scores.append((func_name, row["score"], target))

    return assessment["org_name"], scores


def plot_radar(org_name, scores, save=True):
    """Draws the current-vs-target maturity radar and saves it as a PNG."""
    labels   = [f for f, _, _ in scores]
    current  = [c for _, c, _ in scores]
    target   = [t for _, _, t in scores]

    # Close the polygon by repeating the first point
    angles   = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles  += angles[:1]
    current += current[:1]
    target  += target[:1]

    fig, ax = plt.subplots(figsize=(7.5, 7.5), subplot_kw=dict(projection="polar"))
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(PLOT_BG)

    # Target first so the current polygon sits on top of it.
    # Dashed, so the two series are distinguishable without relying on colour.
    ax.plot(angles, target, color=TARGET, linewidth=2, linestyle="--",
            label=f"Target ({DEFAULT_TARGET_SCORE}.0 — Managed)")

    ax.plot(angles, current, color=CURRENT, linewidth=2.5, label="Current")
    ax.fill(angles, current, color=CURRENT, alpha=0.25)
    ax.scatter(angles[:-1], current[:-1], color=CURRENT, s=60, zorder=5,
               edgecolors=PLOT_BG, linewidths=2)

    # Axes: function names around the outside, maturity 1-5 on the radius
    ax.set_theta_offset(np.pi / 2)   # Govern at the top
    ax.set_theta_direction(-1)       # then clockwise
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color=INK, fontsize=16, fontweight="bold")
    ax.tick_params(axis="x", pad=14)

    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], color=INK_MUTED, fontsize=11)
    ax.set_rlabel_position(180 / len(labels))

    ax.spines["polar"].set_color(GRID)
    ax.grid(color=GRID, alpha=0.5, linewidth=0.8)

    ax.set_title(
        "NIST CSF 2.0 Maturity — Current vs Target\n"
        f"{org_name}",
        color=INK, fontsize=17, fontweight="bold", pad=30,
    )

    # Current is plotted second so it sits on top; reverse the handles so the
    # legend still reads Current first.
    handles, labels_ = ax.get_legend_handles_labels()
    ax.legend(
        handles[::-1], labels_[::-1],
        loc="upper right", bbox_to_anchor=(1.16, 1.12),
        facecolor="#2a2a2a", edgecolor=GRID, labelcolor=INK, fontsize=12,
    )

    # Direct-label only the weakest function — the one to act on first.
    worst_i = int(np.argmin(current[:-1]))
    ax.annotate(
        f"{labels[worst_i]} {current[worst_i]}/5\nlargest gap",
        xy=(angles[worst_i], current[worst_i]),
        xytext=(angles[worst_i], current[worst_i] + 1.5),
        color=INK, fontsize=11, ha="center",
        arrowprops=dict(arrowstyle="->", color=INK_MUTED, linewidth=1),
    )

    # Overall score box
    overall   = sum(c for _, c, _ in scores) / len(scores)
    avg_target = sum(t for _, _, t in scores) / len(scores)
    textstr = (
        f"Overall maturity: {overall:.1f} / 5.0\n"
        f"Target: {avg_target:.1f} / 5.0\n"
        f"Average gap: {avg_target - overall:.1f}\n"
        f"Functions below 3: "
        f"{sum(1 for _, c, _ in scores if c < 3)} of {len(scores)}"
    )
    fig.text(
        0.015, 0.03, textstr, color=INK, fontsize=11, va="bottom", ha="left",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#2a2a2a", edgecolor=GRID),
    )

    fig.text(
        0.98, 0.02,
        "Simulated organisation — illustrative data",
        color=INK_MUTED, fontsize=9, va="bottom", ha="right",
    )

    if save:
        plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"  ✅ Saved: dashboards/csf_radar.png")

    plt.close()


def run_radar():
    initialise_database(verbose=False)
    org_name, scores = get_latest_scores()

    print("\n" + "=" * 60)
    print("  NIST CSF 2.0 MATURITY RADAR")
    print(f"  {org_name}")
    print("=" * 60 + "\n")
    for func_name, current, target in scores:
        bar = "█" * current + "░" * (5 - current)
        print(f"  {func_name:<10} {current}/5  {bar}  target {target}/5")

    overall = sum(c for _, c, _ in scores) / len(scores)
    print(f"\n  Overall maturity: {overall:.1f} / 5.0\n")

    plot_radar(org_name, scores)


if __name__ == "__main__":
    run_radar()
