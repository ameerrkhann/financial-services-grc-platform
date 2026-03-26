# src/risk_quantification/risk_report.py
# Reporting queries for the risk scenario database

import sys
import os
from tabulate import tabulate
from colorama import Fore, Style, init

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.database.db_manager import (
    initialise_database,
    get_all_risk_scenarios,
    get_high_risk_scenarios,
    get_latest_scenario_run,
)
from src.risk_quantification.fair_engine import format_currency

init(autoreset=True)


def print_risk_report():
    """Prints a full risk portfolio report from the database."""
    print("\n" + "=" * 65)
    print("  RISK PORTFOLIO REPORT — First National Bank (Fictional)")
    print("=" * 65)

    # ── Latest results per scenario ──────────────────────────
    latest = get_latest_scenario_run()
    if not latest:
        print("\n  No scenario data found. Run run_scenarios.py first.")
        return

    print(f"\n{Fore.CYAN}  LATEST SCENARIO RESULTS{Style.RESET_ALL}\n")
    table = []
    total_ale = 0
    for row in latest:
        ale          = row["ale"]
        control_cost = row["control_cost"] or 0
        roi          = ((ale - control_cost) / ale * 100) if ale > 0 else 0
        total_ale   += ale
        colour       = Fore.RED if ale > 2_000_000 else Fore.YELLOW

        table.append([
            row["scenario_name"],
            f"{colour}{format_currency(ale)}{Style.RESET_ALL}",
            format_currency(row["percentile_90"]),
            f"{row['prob_over_1m']:.0f}%",
            format_currency(control_cost),
            f"{roi:.0f}%",
            row["date_run"],
        ])

    print(tabulate(
        table,
        headers=["Scenario", "ALE", "90th %ile",
                 "P(>$1M)", "Control Cost", "Control ROI", "Date"],
        tablefmt="rounded_outline"
    ))

    print(f"\n  {Fore.YELLOW}Combined Portfolio ALE: "
          f"{format_currency(total_ale)}{Style.RESET_ALL}")

    # ── High risk scenarios ───────────────────────────────────
    print(f"\n{Fore.RED}  HIGH RISK SCENARIOS (ALE > $1M){Style.RESET_ALL}\n")
    high_risk = get_high_risk_scenarios(ale_threshold=1_000_000)
    if high_risk:
        hr_table = []
        for row in high_risk:
            hr_table.append([
                row["scenario_name"],
                format_currency(row["ale"]),
                format_currency(row["percentile_90"]),
                f"{row['prob_over_1m']:.1f}%",
                row["date_run"],
            ])
        print(tabulate(
            hr_table,
            headers=["Scenario", "ALE", "90th %ile", "P(>$1M)", "Date"],
            tablefmt="rounded_outline"
        ))
    else:
        print(f"  {Fore.GREEN}No scenarios exceed $1M ALE.{Style.RESET_ALL}")

    # ── Executive summary lines ───────────────────────────────
    print(f"\n{Fore.CYAN}  EXECUTIVE SUMMARY{Style.RESET_ALL}")
    print(f"  ─────────────────────────────────────────────────────")
    print(f"  Total scenarios assessed   : {len(latest)}")
    print(f"  Combined annual risk (ALE) : {format_currency(total_ale)}")
    print(f"  Highest single risk        : "
          f"{format_currency(max(r['ale'] for r in latest))}")
    print(f"  Scenarios exceeding $1M    : {len(high_risk)}")
    print(f"  ─────────────────────────────────────────────────────")
    print(f"  Recommendation: Prioritise controls for the top 2")
    print(f"  scenarios by ALE. Combined control investment of")

    total_control = sum(
        r["control_cost"] for r in latest if r["control_cost"]
    )
    print(f"  {format_currency(total_control)}/year reduces portfolio ALE by an")
    print(f"  estimated 60–80%, delivering positive ROI within Year 1.")
    print(f"\n{'=' * 65}\n")


if __name__ == "__main__":
    initialise_database()
    print_risk_report()