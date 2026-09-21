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
    total_ale      = 0
    total_residual = 0
    for row in latest:
        ale           = row["ale"]
        control_cost  = row["control_cost"] or 0
        effectiveness = row["control_effectiveness"] or 0
        residual      = (row["residual_ale"]
                         if row["residual_ale"] is not None
                         else ale * (1 - effectiveness))
        rosi          = row["rosi"] or 0
        total_ale     += ale
        total_residual += residual
        colour        = Fore.RED if ale > 2_000_000 else Fore.YELLOW

        table.append([
            row["scenario_name"],
            f"{colour}{format_currency(ale)}{Style.RESET_ALL}",
            format_currency(row["percentile_90"]),
            f"{row['prob_over_1m']:.0f}%",
            format_currency(control_cost),
            f"{effectiveness:.0%}",
            format_currency(residual),
            f"{rosi * 100:.0f}%",
        ])

    print(tabulate(
        table,
        headers=["Scenario", "ALE", "90th %ile", "P(>$1M)", "Control Cost",
                 "Ctrl Eff.", "Residual ALE", "ROSI"],
        tablefmt="rounded_outline"
    ))
    print("  Ctrl Eff. = assumed control effectiveness (an assumption, "
          "not a measurement).")
    print("  ROSI = (risk reduction − control cost) / control cost.")

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
    total_control = sum(
        r["control_cost"] for r in latest if r["control_cost"]
    )
    reduction     = total_ale - total_residual
    portfolio_rosi = ((reduction - total_control) / total_control * 100
                      if total_control else 0)

    print(f"  Residual ALE after controls : {format_currency(total_residual)}")
    print(f"  Total control investment   : {format_currency(total_control)}/year")
    print(f"  Portfolio risk reduction   : {format_currency(reduction)}/year "
          f"({reduction / total_ale:.0%} of ALE)")
    print(f"  Portfolio ROSI             : {portfolio_rosi:.0f}%")
    print(f"  ─────────────────────────────────────────────────────")
    print(f"  Recommendation: Prioritise controls for the top 2 scenarios by")
    print(f"  ALE. On the documented control-effectiveness assumptions, the")
    print(f"  full programme returns {portfolio_rosi:.0f}% in Year 1.")
    print(f"\n{'=' * 65}\n")


if __name__ == "__main__":
    initialise_database()
    print_risk_report()