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

# Shared with loss_exceedance.py so the chart set reads as one system
SURFACE    = "#131316"
CURRENT    = "#4a90e2"    # same blue as the Data Breach series
TARGET     = "#9a9aa5"    # neutral, so the eye reads current first
INK        = "#f2f2f5"
INK_MUTED  = "#9a9aa5"
GRID       = "#2c2c33"


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

    overall    = sum(current) / len(current)
    avg_target = sum(target) / len(target)

    # Close the polygon by repeating the first point
    angles   = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    plot_ang = angles + angles[:1]
    cur_vals = current + current[:1]
    tgt_vals = target + target[:1]

    fig, ax = plt.subplots(figsize=(10.5, 10.2), subplot_kw=dict(projection="polar"))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    # Target first, so the current polygon sits on top of it. Dashed and
    # neutral-coloured, so the two series stay distinguishable in greyscale
    # and for a reader with colour vision deficiency.
    ax.plot(plot_ang, tgt_vals, color=TARGET, linewidth=2.2, linestyle=(0, (6, 4)),
            label=f"Target maturity ({int(avg_target)})")

    ax.plot(plot_ang, cur_vals, color=CURRENT, linewidth=3, label="Current maturity",
            solid_capstyle="round")
    ax.fill(plot_ang, cur_vals, color=CURRENT, alpha=0.30)
    ax.scatter(angles, current, color=CURRENT, s=95, zorder=6,
               edgecolors=SURFACE, linewidths=2.5)

    # Axes: function names outside, maturity 1-5 along the radius
    ax.set_theta_offset(np.pi / 2)   # Govern at the top
    ax.set_theta_direction(-1)       # then clockwise
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, color=INK, fontsize=14.5, fontweight="bold")
    ax.tick_params(axis="x", pad=18)

    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], color=INK_MUTED, fontsize=10)
    ax.set_rlabel_position(23)

    ax.spines["polar"].set_color(GRID)
    ax.grid(color=GRID, alpha=0.9, linewidth=0.9)

    # Every point carries its score, so the chart is readable without
    # counting rings.
    for angle, value in zip(angles, current):
        offset = -0.42 if value >= 2 else 0.42
        ax.annotate(str(value), xy=(angle, value + offset),
                    color=INK, fontsize=13, fontweight="bold",
                    ha="center", va="center", zorder=7)

    # Placed in figure coordinates so it cannot overflow the canvas as the
    # polar axes resize.
    legend = fig.legend(
        loc="upper right", bbox_to_anchor=(0.985, 0.918),
        facecolor="#1b1b20", edgecolor=GRID, labelcolor=INK,
        fontsize=11.5, borderpad=0.8, handlelength=1.8, labelspacing=0.6,
    )
    legend.get_frame().set_linewidth(0.8)

    fig.text(0.5, 0.985, "NIST CSF 2.0 Maturity — Current vs Target",
             color=INK, fontsize=21, fontweight="bold", ha="center", va="top")
    fig.text(0.5, 0.943,
             f"{org_name}  ·  Overall {overall:.1f} / 5.0  ·  "
             f"Target {avg_target:.1f}",
             color=INK_MUTED, fontsize=13, ha="center", va="top")

    fig.subplots_adjust(top=0.825, bottom=0.075, left=0.128, right=0.872)

    if save:
        plt.savefig(OUTPUT_FILE, dpi=150, facecolor=fig.get_facecolor())
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
