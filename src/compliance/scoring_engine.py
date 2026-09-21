# src/compliance/scoring_engine.py
# NIST CSF 2.0 Maturity Scoring Engine

import sys
import os
from datetime import date
from tabulate import tabulate
from colorama import Fore, Style, init

# Add project root to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.compliance.csf_data import (
    CSF_FUNCTIONS,
    REMEDIATION_PRIORITY,
    GAP_METADATA,
    DEFAULT_TARGET_SCORE,
)
from src.database.db_manager import (
    initialise_database,
    insert_assessment,
    insert_function_score,
    insert_control_gap,
    get_assessment_scores,
    get_assessment_gaps,
)

init(autoreset=True)  # initialise colorama

# A function scoring below this is treated as a control gap.
# 3 = "Defined" — documented and consistently followed.
GAP_THRESHOLD = 3


def get_score_colour(score):
    """Returns a colour based on the score value."""
    if score >= 4:
        return Fore.GREEN
    elif score == 3:
        return Fore.YELLOW
    else:
        return Fore.RED


def print_header():
    print("\n" + "=" * 65)
    print("   FINANCIAL SERVICES GRC PLATFORM")
    print("   NIST CSF 2.0 Maturity Assessment Engine")
    print("=" * 65)


def collect_assessment_info():
    """Asks the analyst for basic assessment details."""
    print(f"\n{Fore.CYAN}--- Assessment Setup ---{Style.RESET_ALL}")
    org_name = input("Organisation name: ").strip() or "First National Bank (Fictional)"
    assessor  = input("Assessor name:     ").strip() or "Ameer Khan"
    today     = date.today().isoformat()
    print(f"Date: {today}")
    return org_name, assessor, today


def score_one_function(func_name, func_data):
    """Walks the analyst through scoring a single CSF function."""
    print(f"\n{Fore.CYAN}{'─' * 55}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Function: {func_name} ({func_data['code']}){Style.RESET_ALL}")
    print(f"  {func_data['description']}")

    print(f"\n  {Fore.YELLOW}Key assessment questions:{Style.RESET_ALL}")
    for i, q in enumerate(func_data["questions"], 1):
        print(f"    {i}. {q}")

    print(f"\n  {Fore.YELLOW}Maturity descriptors:{Style.RESET_ALL}")
    for level, desc in func_data["maturity_descriptors"].items():
        print(f"    {level} — {desc}")

    # Get a valid score
    while True:
        try:
            score = int(input(f"\n  Enter score for {func_name} (1-5): "))
            if 1 <= score <= 5:
                break
            print("  Please enter a number between 1 and 5.")
        except ValueError:
            print("  Please enter a number.")

    rationale = input(f"  Briefly explain why (press Enter to skip): ").strip()
    return score, rationale


def generate_gaps(func_name, score, assessment_id=None):
    """
    Returns the control gap for a function scoring below the target, or None.

    Gap text and framework references come from GAP_METADATA in csf_data.py so
    there is exactly one place where a control ID is written down. Pass an
    assessment_id to also persist the gap to the database.
    """
    if score >= GAP_THRESHOLD:
        return None

    gap_info = GAP_METADATA[func_name]

    if assessment_id is not None:
        insert_control_gap(
            assessment_id=assessment_id,
            function_name=func_name,
            gap_description=gap_info["gap"],
            priority=gap_info["priority"],
            nist_ref=gap_info["nist_ref"],
            iso27001_ref=gap_info["iso_ref"],
            soc2_ref=gap_info["soc2_ref"],
            remediation=gap_info["remediation"],
        )
    return gap_info


def print_results(org_name, scores, gaps):
    """Prints the final assessment results table."""
    print(f"\n\n{'=' * 65}")
    print(f"  ASSESSMENT RESULTS — {org_name.upper()}")
    print(f"{'=' * 65}")

    # Scores table
    table_data = []
    for func_name, (score, rationale) in scores.items():
        colour    = get_score_colour(score)
        bar       = "█" * score + "░" * (5 - score)
        status    = "✅ OK" if score >= GAP_THRESHOLD else "⚠️  GAP"
        table_data.append([
            func_name,
            f"{colour}{score}/5{Style.RESET_ALL}",
            f"{colour}{bar}{Style.RESET_ALL}",
            status,
        ])

    avg_score = sum(s for s, _ in scores.values()) / len(scores)

    print(tabulate(
        table_data,
        headers=["Function", "Score", "Visual", "Status"],
        tablefmt="rounded_outline"
    ))

    print(f"\n  Overall Maturity Score: {avg_score:.1f} / 5.0")

    # Gaps table
    if gaps:
        print(f"\n{Fore.RED}  ⚠️  CONTROL GAPS IDENTIFIED{Style.RESET_ALL}")
        gap_table = []
        for func_name, gap_info in gaps.items():
            gap_table.append([
                func_name,
                gap_info["priority"],
                gap_info["nist_ref"],
                gap_info["iso_ref"],
                gap_info["soc2_ref"],
            ])
        print(tabulate(
            gap_table,
            headers=["Function", "Priority", "NIST Ref", "ISO 27001", "SOC 2"],
            tablefmt="rounded_outline"
        ))

        print(f"\n{Fore.YELLOW}  REMEDIATION ACTIONS{Style.RESET_ALL}")
        for func_name, gap_info in gaps.items():
            print(f"\n  [{gap_info['priority']}] {func_name}")
            print(f"  → {gap_info['remediation']}")
    else:
        print(f"\n{Fore.GREEN}  ✅ No critical gaps identified.{Style.RESET_ALL}")

    print(f"\n{'=' * 65}\n")


def run_assessment():
    """Main function — runs the full interactive assessment."""
    initialise_database()
    print_header()

    org_name, assessor, today = collect_assessment_info()

    # Save assessment to DB
    assessment_id = insert_assessment(org_name, assessor, today)

    scores = {}
    gaps   = {}

    for func_name, func_data in CSF_FUNCTIONS.items():
        score, rationale = score_one_function(func_name, func_data)
        insert_function_score(assessment_id, func_name, score, rationale,
                              target_score=DEFAULT_TARGET_SCORE)
        scores[func_name] = (score, rationale)

        gap = generate_gaps(func_name, score, assessment_id)
        if gap:
            gaps[func_name] = gap

    print_results(org_name, scores, gaps)
    print(f"  ✅ Assessment saved to database (ID: {assessment_id})")


if __name__ == "__main__":
    run_assessment()