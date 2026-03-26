# src/risk_quantification/loss_exceedance.py
# Generates Loss Exceedance Curves for all 5 FAIR scenarios

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.risk_quantification.fair_engine import run_fair_simulation, format_currency
from src.risk_quantification.scenarios import SCENARIOS

# Output folder for saved charts
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "../../dashboards")
os.makedirs(CHARTS_DIR, exist_ok=True)


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
    losses          = result["annual_losses"]
    loss_vals, exc  = compute_exceedance_curve(losses)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#0f0f0f")
    ax.set_facecolor("#1a1a1a")

    # Main curve
    ax.plot(loss_vals, exc, color="#00d4ff", linewidth=2.5, label="Loss Exceedance")
    ax.fill_between(loss_vals, exc, alpha=0.15, color="#00d4ff")

    # Key reference lines
    ale = result["ale"]
    p90 = result["percentile_90"]
    p95 = result["percentile_95"]

    ax.axvline(ale, color="#ffdd00", linestyle="--", linewidth=1.5,
               label=f"ALE: {format_currency(ale)}")
    ax.axvline(p90, color="#ff6b35", linestyle="--", linewidth=1.5,
               label=f"90th %ile: {format_currency(p90)}")
    ax.axvline(p95, color="#ff2d55", linestyle="--", linewidth=1.5,
               label=f"95th %ile: {format_currency(p95)}")

    # Formatting
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x/1_000_000:.1f}M" if x >= 1_000_000
                              else f"${x/1_000:.0f}K")
    )
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:.0f}%"))

    ax.set_xlabel("Annual Loss ($)", color="white", fontsize=12)
    ax.set_ylabel("Probability of Exceeding Loss", color="white", fontsize=12)
    ax.set_title(
        f"Loss Exceedance Curve — {scenario['name']}\nFirst National Bank (Fictional)",
        color="white", fontsize=14, fontweight="bold", pad=15
    )

    ax.tick_params(colors="white")
    ax.spines["bottom"].set_color("#444")
    ax.spines["left"].set_color("#444")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.15, color="white")

    legend = ax.legend(facecolor="#2a2a2a", edgecolor="#444",
                       labelcolor="white", fontsize=10)

    # Annotation box
    textstr = (
        f"ALE: {format_currency(ale)}\n"
        f"P(>$1M): {result['prob_over_1m']:.1f}%\n"
        f"P(>$5M): {result['prob_over_5m']:.1f}%"
    )
    ax.text(0.98, 0.97, textstr, transform=ax.transAxes,
            fontsize=9, verticalalignment="top", horizontalalignment="right",
            bbox=dict(boxstyle="round", facecolor="#2a2a2a", edgecolor="#444"),
            color="white")

    plt.tight_layout()

    if save:
        path = os.path.join(CHARTS_DIR, f"lec_{scenario_key}.png")
        plt.savefig(path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"  ✅ Saved: dashboards/lec_{scenario_key}.png")

    plt.show()
    plt.close()


def plot_combined_curves(all_results, save=True):
    """Plots all 5 scenarios on one chart for comparison."""
    colours = {
        "data_breach":           "#00d4ff",
        "ransomware":            "#ff2d55",
        "insider_threat":        "#ffdd00",
        "vendor_failure":        "#ff6b35",
        "cloud_misconfiguration":"#32d74b",
    }

    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor("#0f0f0f")
    ax.set_facecolor("#1a1a1a")

    for key, (scenario, result) in all_results.items():
        losses         = result["annual_losses"]
        loss_vals, exc = compute_exceedance_curve(losses)
        colour         = colours.get(key, "#ffffff")
        ale            = result["ale"]

        ax.plot(loss_vals, exc, color=colour, linewidth=2,
                label=f"{scenario['name']} (ALE: {format_currency(ale)})")
        ax.fill_between(loss_vals, exc, alpha=0.05, color=colour)

    # Reference line at 10% probability
    ax.axhline(10, color="white", linestyle=":", linewidth=1, alpha=0.4,
               label="10% probability threshold")

    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x/1_000_000:.1f}M" if x >= 1_000_000
                              else f"${x/1_000:.0f}K")
    )
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:.0f}%"))

    ax.set_xlabel("Annual Loss ($)", color="white", fontsize=12)
    ax.set_ylabel("Probability of Exceeding Loss", color="white", fontsize=12)
    ax.set_title(
        "Loss Exceedance Curves — All Threat Scenarios\n"
        "First National Bank (Fictional) | FAIR Methodology",
        color="white", fontsize=14, fontweight="bold", pad=15
    )

    ax.tick_params(colors="white")
    ax.spines["bottom"].set_color("#444")
    ax.spines["left"].set_color("#444")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.15, color="white")

    ax.legend(facecolor="#2a2a2a", edgecolor="#444",
              labelcolor="white", fontsize=9,
              loc="upper right")

    plt.tight_layout()

    if save:
        path = os.path.join(CHARTS_DIR, "lec_all_scenarios.png")
        plt.savefig(path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"\n  ✅ Saved: dashboards/lec_all_scenarios.png")

    plt.show()
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