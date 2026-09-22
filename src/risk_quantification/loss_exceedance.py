# src/risk_quantification/loss_exceedance.py
# Generates Loss Exceedance Curves for all 5 FAIR scenarios

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.risk_quantification.fair_engine import (
    run_fair_simulation,
    format_currency,
    seed_for,
    N_SIMULATIONS,
)
from src.risk_quantification.scenarios import SCENARIOS

# Output folder for saved charts
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "../../dashboards")
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Chart theme ──────────────────────────────────────────────
# Shared with csf_radar.py so the chart set reads as one system.
# The five categorical hues are assigned in fixed order and validated for
# colour-vision-deficiency separation against the dark surface, so a reader
# with deuteranopia or protanopia can still tell adjacent series apart.
SURFACE   = "#131316"
INK       = "#f2f2f5"
INK_MUTED = "#9a9aa5"
GRID      = "#2c2c33"

SERIES_COLOURS = {
    "data_breach":            "#4a90e2",   # blue
    "ransomware":             "#d95f2e",   # orange
    "insider_threat":         "#1f9d74",   # green
    "vendor_failure":         "#bf8a10",   # gold
    "cloud_misconfiguration": "#dd4f86",   # pink
}


# Compact labels for legends and chart titles, where the full scenario name
# would dominate the plot area.
SHORT_NAMES = {
    "data_breach":            "Data Breach",
    "ransomware":             "Ransomware",
    "insider_threat":         "Insider Threat",
    "vendor_failure":         "Vendor Failure",
    "cloud_misconfiguration": "Cloud Misconfig",
}


def short_name(key, name):
    """Compact label for a scenario, falling back to the name before the dash."""
    return SHORT_NAMES.get(key, name.split(" — ")[0])


def money_formatter(x, _):
    if x >= 1_000_000:
        return f"${x/1_000_000:.0f}M"
    if x >= 1_000:
        return f"${x/1_000:.0f}K"
    return "$0"


def style_axes(ax):
    """Applies the shared dark theme to a cartesian axis."""
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=INK_MUTED, labelsize=11)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color(GRID)
    ax.grid(True, alpha=0.35, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def compute_exceedance_curve(annual_losses, n_points=500):
    """
    Computes the Loss Exceedance Curve data points.
    Returns (loss_values, exceedance_probabilities).
    """
    max_loss    = np.percentile(annual_losses, 99.5)
    loss_values = np.linspace(0, max_loss, n_points)
    exceedance  = [np.mean(annual_losses > x) * 100 for x in loss_values]
    return loss_values, exceedance


def plot_individual_curve(scenario_key, scenario, result, save=True):
    """Plots a single scenario's Loss Exceedance Curve."""
    losses         = result["annual_losses"]
    loss_vals, exc = compute_exceedance_curve(losses)
    colour         = SERIES_COLOURS.get(scenario_key, "#4a90e2")

    fig, ax = plt.subplots(figsize=(11, 6.2))
    fig.patch.set_facecolor(SURFACE)
    style_axes(ax)

    ax.plot(loss_vals, exc, color=colour, linewidth=2.6, solid_capstyle="round")
    ax.fill_between(loss_vals, exc, alpha=0.12, color=colour, linewidth=0)

    ale = result["ale"]
    p90 = result["percentile_90"]
    p95 = result["percentile_95"]

    for value, label, style in (
        (ale, f"ALE {format_currency(ale)}", "-"),
        (p90, f"90th %ile {format_currency(p90)}", "--"),
        (p95, f"95th %ile {format_currency(p95)}", ":"),
    ):
        ax.axvline(value, color=INK_MUTED, linestyle=style, linewidth=1.1, alpha=0.65)
        ax.annotate(label, xy=(value, 100), xytext=(4, -12),
                    textcoords="offset points", rotation=90,
                    color=INK_MUTED, fontsize=8.5, va="top")

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(money_formatter))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.set_xlim(left=0)
    ax.set_ylim(0, 100)

    ax.set_xlabel("Annual loss", color=INK_MUTED, fontsize=11, labelpad=10)
    ax.set_ylabel("Probability of exceeding that loss", color=INK_MUTED,
                  fontsize=11, labelpad=10)

    fig.text(0.055, 0.955, f"Loss Exceedance Curve — {short_name(scenario_key, scenario['name'])}",
             color=INK, fontsize=19, fontweight="bold", va="top")
    fig.text(0.055, 0.895,
             f"First National Bank (Fictional)  ·  FAIR methodology  ·  "
             f"ALE {format_currency(ale)}  ·  "
             f"P(>$1M) {result['prob_over_1m']:.0f}%",
             color=INK_MUTED, fontsize=11, va="top")

    fig.subplots_adjust(top=0.80, left=0.09, right=0.97, bottom=0.13)

    if save:
        path = os.path.join(CHARTS_DIR, f"lec_{scenario_key}.png")
        plt.savefig(path, dpi=150, facecolor=fig.get_facecolor())
        print(f"  ✅ Saved: dashboards/lec_{scenario_key}.png")

    plt.close()


def plot_combined_curves(all_results, save=True):
    """Plots all 5 scenarios on one chart for comparison."""
    fig, ax = plt.subplots(figsize=(9.8, 5.5))
    fig.patch.set_facecolor(SURFACE)
    style_axes(ax)

    # Fixed colour order — a scenario keeps its hue regardless of how many
    # series are drawn, so the colour always means the same thing.
    for key, (scenario, result) in all_results.items():
        loss_vals, exc = compute_exceedance_curve(result["annual_losses"])
        ax.plot(loss_vals, exc,
                color=SERIES_COLOURS.get(key, "#ffffff"),
                linewidth=2.6, solid_capstyle="round",
                label=f"{short_name(key, scenario['name'])}  ·  "
                      f"ALE {format_currency(result['ale'])}")

    # The 10% line is the 1-in-10 year loss every risk committee asks for
    ax.axhline(10, color=INK_MUTED, linestyle=":", linewidth=1.2, alpha=0.6)
    ax.annotate("1-in-10 year threshold",
                xy=(0.985, 10), xycoords=("axes fraction", "data"),
                xytext=(0, 7), textcoords="offset points",
                color=INK_MUTED, fontsize=9.5, style="italic", ha="right")

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(money_formatter))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.set_xlim(left=0)
    ax.set_ylim(0, 100)

    ax.set_xlabel("Annual loss", color=INK_MUTED, fontsize=12.5, labelpad=10)
    ax.set_ylabel("Probability of exceeding that loss", color=INK_MUTED,
                  fontsize=12.5, labelpad=10)

    legend = ax.legend(
        facecolor="#1b1b20", edgecolor=GRID, labelcolor=INK,
        fontsize=13, loc="upper right", borderpad=0.8,
        handlelength=1.6, handletextpad=0.9, labelspacing=0.7,
    )
    legend.get_frame().set_linewidth(0.8)

    fig.text(0.055, 0.962, "Loss Exceedance Curves — All Threat Scenarios",
             color=INK, fontsize=20, fontweight="bold", va="top")
    fig.text(0.055, 0.895,
             "First National Bank (Fictional)  ·  FAIR methodology  ·  "
             f"{N_SIMULATIONS:,} Monte Carlo simulations per scenario",
             color=INK_MUTED, fontsize=12, va="top")

    fig.subplots_adjust(top=0.80, left=0.095, right=0.975, bottom=0.135)

    if save:
        path = os.path.join(CHARTS_DIR, "lec_all_scenarios.png")
        plt.savefig(path, dpi=150, facecolor=fig.get_facecolor())
        print(f"\n  ✅ Saved: dashboards/lec_all_scenarios.png")

    plt.close()


def run_all_curves():
    """Runs simulations and generates all curves."""
    print("\n" + "=" * 60)
    print("  LOSS EXCEEDANCE CURVE GENERATOR")
    print("  Financial Services GRC Platform — FAIR Methodology")
    print("=" * 60)
    print("\n  Running simulations for all 5 scenarios...")

    all_results = {}
    for key, scenario in SCENARIOS.items():
        print(f"  → {scenario['name']}...", end=" ")
        result = run_fair_simulation(
            loss_low  = scenario["loss_low"],
            loss_high = scenario["loss_high"],
            freq_low  = scenario["freq_low"],
            freq_high = scenario["freq_high"],
            seed      = seed_for(scenario["id"]),
        )
        all_results[key] = (scenario, result)
        print("done.")

    print("\n  Generating individual curves...")
    for key, (scenario, result) in all_results.items():
        plot_individual_curve(key, scenario, result, save=True)

    print("\n  Generating combined comparison chart...")
    plot_combined_curves(all_results, save=True)

    # Print summary table
    print("\n" + "=" * 60)
    print("  RISK PORTFOLIO SUMMARY")
    print("=" * 60)
    from tabulate import tabulate
    from colorama import Fore, Style, init
    init(autoreset=True)

    table = []
    for key, (scenario, result) in all_results.items():
        ale = result["ale"]
        colour = Fore.RED if ale > 2_000_000 else Fore.YELLOW
        table.append([
            scenario["name"],
            f"{colour}{format_currency(ale)}{Style.RESET_ALL}",
            format_currency(result["percentile_90"]),
            f"{result['prob_over_1m']:.0f}%",
            f"{result['prob_over_5m']:.0f}%",
        ])

    print(tabulate(
        table,
        headers=["Scenario", "ALE", "90th %ile", "P(>$1M)", "P(>$5M)"],
        tablefmt="rounded_outline"
    ))

    total_ale = sum(r["ale"] for _, (_, r) in all_results.items())
    print(f"\n  Combined portfolio ALE: {format_currency(total_ale)}")
    print(f"  Charts saved to: dashboards/\n")


if __name__ == "__main__":
    run_all_curves()