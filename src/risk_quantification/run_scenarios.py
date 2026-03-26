# src/risk_quantification/run_scenarios.py
# Runs FAIR simulations for all defined scenarios
# Week 2 — Days 9 & 10

import sys
import os
from tabulate import tabulate
from colorama import Fore, Style, init

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.risk_quantification.fair_engine import run_fair_simulation, format_currency
from src.risk_quantification.scenarios import SCENARIOS
from src.database.db_manager import initialise_database, get_connection

init(autoreset=True)


def save_scenario_result(scenario_key, scenario, result):
    """Saves a scenario result using the central db_manager."""
    from src.database.db_manager import save_risk_scenario
    save_risk_scenario(
        scenario_key  = scenario_key,
        scenario_name = scenario["name"],
        loss_low      = scenario["loss_low"],
        loss_high     = scenario["loss_high"],
        freq_low      = scenario["freq_low"],
        freq_high     = scenario["freq_high"],
        ale           = result["ale"],
        median        = result["median"],
        percentile_90 = result["percentile_90"],
        percentile_95 = result["percentile_95"],
        prob_over_1m  = result["prob_over_1m"],
        prob_over_5m  = result["prob_over_5m"],
        control_cost  = scenario.get("control_cost"),
        osfi_ref      = scenario["osfi_ref"],
    )


def print_scenario_result(scenario_key, scenario, result):
    """Prints a detailed result for one scenario."""
    colour = Fore.RED if result["ale"] > 2_000_000 else Fore.YELLOW

    print(f"\n{colour}{'─' * 60}{Style.RESET_ALL}")
    print(f"{colour}  Scenario {scenario['id']}: {scenario['name']}{Style.RESET_ALL}")
    print(f"{'─' * 60}")
    print(f"  {scenario['description']}\n")
    print(f"  FAIR Inputs:")
    print(f"    Loss range  : {format_currency(scenario['loss_low'])} – {format_currency(scenario['loss_high'])} per event")
    print(f"    Frequency   : {scenario['freq_low']}–{scenario['freq_high']} attempts/year")
    print(f"    Simulations : 100,000 Monte Carlo runs\n")

    # Results table
    table = [
        ["Annualised Loss Expectancy (ALE)", format_currency(result["ale"])],
        ["Median annual loss",               format_currency(result["median"])],
        ["90th percentile (1-in-10 year)",   format_currency(result["percentile_90"])],
        ["95th percentile (1-in-20 year)",   format_currency(result["percentile_95"])],
        ["Probability loss exceeds $1M/yr",  f"{result['prob_over_1m']:.1f}%"],
        ["Probability loss exceeds $5M/yr",  f"{result['prob_over_5m']:.1f}%"],
    ]
    print(tabulate(table, tablefmt="rounded_outline"))

    # ROI of controls
    ale         = result["ale"]
    control_cost = scenario["control_cost"]
    roi         = ((ale - control_cost) / ale) * 100 if ale > 0 else 0

    print(f"\n  {Fore.GREEN}Cost-Benefit Analysis:{Style.RESET_ALL}")
    print(f"    Annual expected loss (no controls) : {format_currency(ale)}")
    print(f"    Estimated control cost             : {format_currency(control_cost)}")
    print(f"    Risk reduction value               : {format_currency(ale - control_cost)}")
    print(f"    ROI of implementing controls       : {roi:.0f}%")

    print(f"\n  Recommended Controls:")
    for ctrl in scenario["controls"]:
        print(f"    ✓ {ctrl}")

    print(f"\n  Regulatory Reference: {scenario['osfi_ref']}")
    print(f"  NIST CSF Reference  : {scenario['nist_ref']}")


def run_scenarios(scenario_keys=None):
    """Runs FAIR simulations for specified scenarios (or all if None)."""
    initialise_database()

    print("\n" + "=" * 60)
    print("  FINANCIAL SERVICES CYBER RISK INTELLIGENCE PLATFORM")
    print("  Quantitative Risk Engine — FAIR Methodology")
    print("  Organisation: First National Bank (Fictional)")
    print("=" * 60)

    keys = scenario_keys or list(SCENARIOS.keys())

    results = {}
    for key in keys:
        if key not in SCENARIOS:
            print(f"  Scenario '{key}' not found.")
            continue

        scenario = SCENARIOS[key]
        print(f"\n  Running simulation: {scenario['name']}...", end=" ")
        result = run_fair_simulation(
            loss_low  = scenario["loss_low"],
            loss_high = scenario["loss_high"],
            freq_low  = scenario["freq_low"],
            freq_high = scenario["freq_high"],
        )
        print("done.")
        save_scenario_result(key, scenario, result)
        results[key] = result

    # Print all results
    for key in keys:
        if key in results:
            print_scenario_result(key, SCENARIOS[key], results[key])

    # Summary comparison table
    if len(results) > 1:
        print(f"\n\n{'=' * 60}")
        print(f"  SCENARIO COMPARISON SUMMARY")
        print(f"{'=' * 60}")
        summary = []
        for key in keys:
            if key in results:
                r = results[key]
                s = SCENARIOS[key]
                summary.append([
                    s["name"],
                    format_currency(r["ale"]),
                    format_currency(r["percentile_90"]),
                    f"{r['prob_over_1m']:.0f}%",
                    format_currency(s["control_cost"]),
                ])
        print(tabulate(
            summary,
            headers=["Scenario", "ALE", "90th %ile", "P(>$1M)", "Control Cost"],
            tablefmt="rounded_outline"
        ))

    print(f"\n  ✅ Results saved to database.\n")
    return results


if __name__ == "__main__":
    run_scenarios()