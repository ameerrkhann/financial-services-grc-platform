# src/database/seed_demo_data.py
# Rebuilds the complete demo dataset in one command.
#
# Everything a reader of this repo sees — the Power BI dashboard, the executive
# PDF, the Excel templates, the README tables — is generated from the database
# this script produces. Run it first, then run the export and report builders.
#
#     python3 src/database/seed_demo_data.py
#
# It is destructive by design: the existing database file is deleted and rebuilt
# so the dataset is reproducible rather than accumulated.

import sys
import os
from datetime import date, timedelta

from tabulate import tabulate
from colorama import Fore, Style, init

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.compliance.csf_data import CSF_FUNCTIONS, DEFAULT_TARGET_SCORE
from src.compliance.scoring_engine import generate_gaps
from src.database.db_manager import (
    get_db_path,
    initialise_database,
    insert_assessment,
    insert_function_score,
    save_risk_scenario,
    save_vendor_assessment,
    save_vendor_responses,
    get_overdue_vendors,
    get_reassessment_days,
    get_vendor_tier_summary,
)
from src.risk_quantification.fair_engine import (
    run_fair_simulation,
    compute_rosi,
    format_currency,
    seed_for,
)
from src.risk_quantification.scenarios import SCENARIOS
from src.vendor_risk.questionnaire_data import (
    UNIVERSAL_QUESTIONS,
    SERVICE_SPECIFIC_QUESTIONS,
)
from src.vendor_risk.scoring import calculate_score

init(autoreset=True)

ORG_NAME  = "First National Bank (Fictional)"
ASSESSOR  = "Ameer Khan"
TODAY     = date.today()


# ─────────────────────────────────────────────────────────────
# NIST CSF 2.0 baseline assessment
# ─────────────────────────────────────────────────────────────
CSF_SCORES = {
    "Govern":   (2, "Security policy exists but is three years old and was never "
                    "re-approved. No documented risk appetite statement."),
    "Identify": (2, "Asset inventory is a spreadsheet maintained by hand and is "
                    "known to be incomplete for cloud workloads."),
    "Protect":  (3, "MFA enforced on email and remote access, data encrypted at "
                    "rest and in transit. Access reviews happen but are not evidenced."),
    "Detect":   (2, "Logs are collected centrally but nobody owns alert triage. "
                    "No defined thresholds and no measured time to detect."),
    "Respond":  (1, "No documented incident response plan. The 24-hour OSFI "
                    "reporting path has never been walked through."),
    "Recover":  (3, "Backups tested quarterly and RTOs defined for the core "
                    "banking platform. Wider BCP not exercised this year."),
}


def seed_csf_assessment():
    """Inserts the CSF baseline, its target maturity, and its resulting gaps."""
    assessment_id = insert_assessment(
        org_name = ORG_NAME,
        assessor = ASSESSOR,
        date_run = TODAY.isoformat(),
        notes    = "Demo baseline assessment seeded by seed_demo_data.py. "
                   f"Target maturity {DEFAULT_TARGET_SCORE} for every function.",
    )

    gaps = {}
    for func_name in CSF_FUNCTIONS:
        score, rationale = CSF_SCORES[func_name]
        insert_function_score(
            assessment_id, func_name, score, rationale,
            target_score=DEFAULT_TARGET_SCORE,
        )
        # generate_gaps owns the gap text and the framework references, so the
        # seeded gaps are identical to the ones an interactive assessment
        # produces. There is no second copy of the gap map here.
        gap = generate_gaps(func_name, score, assessment_id)
        if gap:
            gaps[func_name] = gap

    return assessment_id, gaps


# ─────────────────────────────────────────────────────────────
# FAIR scenarios
# ─────────────────────────────────────────────────────────────
def seed_risk_scenarios():
    """Runs all 5 FAIR scenarios with their fixed per-scenario seeds."""
    results = {}
    for key, scenario in SCENARIOS.items():
        result = run_fair_simulation(
            loss_low  = scenario["loss_low"],
            loss_high = scenario["loss_high"],
            freq_low  = scenario["freq_low"],
            freq_high = scenario["freq_high"],
            seed      = seed_for(scenario["id"]),
        )
        econ = compute_rosi(
            result["ale"], scenario["control_cost"], scenario["control_effectiveness"]
        )
        save_risk_scenario(
            scenario_key  = key,
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
            control_cost  = scenario["control_cost"],
            osfi_ref      = scenario["osfi_ref"],
            control_effectiveness = scenario["control_effectiveness"],
            residual_ale  = econ["residual_ale"],
            rosi          = econ["rosi"],
        )
        results[key] = (result, econ)
    return results


# ─────────────────────────────────────────────────────────────
# Vendor portfolio
# ─────────────────────────────────────────────────────────────
# Eight fictional vendors across all five service types. Each one is described
# by a security posture rather than a hand-written answer sheet: a default
# answer, then overrides per question category and per individual question.
# That reads like a real assessment (a vendor is strong in some domains and
# weak in others) and keeps the profiles short.
#
# expected_tier is asserted after scoring, so if the questionnaire weights
# change this script fails loudly instead of quietly reshaping the demo.
#
# days_ago drives the overdue calculation: three vendors are deliberately past
# the reassessment window for their tier so get_overdue_vendors() returns rows.
VENDORS = [
    {
        "name":          "NorthPeak Cloud Services",
        "service_type":  "Cloud Provider",
        "criticality":   "Critical",
        "expected_tier": "Low",
        "days_ago":      200,
        "notes":         "Core banking platform hosting. ISO 27001 and SOC 2 Type II "
                         "current. Independent pen test report provided annually.",
        "default":       "Yes",
        "by_category":   {},
        "by_question":   {"U04": "Partial", "U08": "Partial",
                          "U11": "No",      "U13": "Partial"},
    },
    {
        "name":          "MapleLedger Payments",
        "service_type":  "Payment Processor",
        "criticality":   "Critical",
        "expected_tier": "Medium",
        "days_ago":      45,
        "notes":         "Retail payment authorisation and settlement. PCI DSS Level 1 "
                         "confirmed. Fourth-party chain not documented.",
        "default":       "Yes",
        "by_category":   {},
        "by_question":   {"U02": "Partial", "U04": "No",      "U08": "No",
                          "U11": "Partial", "U12": "No",      "U13": "No",
                          "U14": "Partial", "PP03": "Partial"},
    },
    {
        "name":          "Borealis Analytics",
        "service_type":  "Data Analytics / AI",
        "criticality":   "High",
        "expected_tier": "High",
        "days_ago":      30,
        "notes":         "Customer segmentation models. No breach notification clause "
                         "in the contract and no bias testing evidence for models that "
                         "inform customer decisions.",
        "default":       "Yes",
        "by_category":   {"Governance":               "Partial",
                          "Business Continuity":      "Partial",
                          "Vulnerability Management": "Partial"},
        "by_question":   {"U03": "No",      "U04": "No",      "U07": "Partial",
                          "U08": "No",      "U10": "No",      "U11": "No",
                          "U13": "Partial", "U14": "Partial",
                          "DA01": "Partial", "DA04": "No"},
    },
    {
        "name":          "Rideau Infrastructure Group",
        "service_type":  "IT Infrastructure",
        "criticality":   "High",
        "expected_tier": "Critical",
        "days_ago":      220,
        "notes":         "Branch network and data centre colocation. Assessment was "
                         "never completed at onboarding. No security certification, "
                         "no tested BCP, no right-to-audit clause. Escalated to the "
                         "Operational Risk Committee.",
        "default":       "No",
        "by_category":   {},
        "by_question":   {"U01": "Yes",     "U07": "Yes",     "U10": "Yes",
                          "IT03": "Yes",
                          "U05": "Partial", "U06": "Partial", "U09": "Partial",
                          "IT01": "Partial"},
    },
    {
        "name":          "Cartier Ledger Systems",
        "service_type":  "Software / SaaS",
        "criticality":   "Medium",
        "expected_tier": "Medium",
        "days_ago":      80,
        "notes":         "General ledger reconciliation SaaS. Secure development "
                         "lifecycle documented; no SBOM and no independent pen test.",
        "default":       "Yes",
        "by_category":   {},
        "by_question":   {"U02": "Partial", "U04": "Partial", "U08": "Partial",
                          "U11": "No",      "U12": "Partial", "U13": "No",
                          "SW02": "Partial", "SW04": "No"},
    },
    {
        "name":          "Lakeshore Trust Software",
        "service_type":  "Software / SaaS",
        "criticality":   "High",
        "expected_tier": "Low",
        "days_ago":      120,
        "notes":         "Trust accounting platform. Strong posture. No "
                         "sub-contractors touch bank data, so U13 is scored N/A "
                         "and excluded from the denominator.",
        "default":       "Yes",
        "by_category":   {},
        "by_question":   {"U04": "Partial", "U08": "Partial", "U11": "Partial",
                          "U13": "N/A",     "SW04": "Partial"},
    },
    {
        "name":          "Gastown Data Works",
        "service_type":  "Data Analytics / AI",
        "criticality":   "Medium",
        "expected_tier": "Medium",
        "days_ago":      400,
        "notes":         "Marketing attribution reporting. Overdue for annual "
                         "reassessment. Model explainability and data minimisation "
                         "both only partially evidenced.",
        "default":       "Yes",
        "by_category":   {},
        "by_question":   {"U02": "Partial", "U04": "No",      "U08": "No",
                          "U11": "Partial", "U12": "Partial", "U13": "No",
                          "U14": "Partial", "DA01": "Partial",
                          "DA03": "Partial", "DA04": "No"},
    },
    {
        "name":          "Acadia Payment Networks",
        "service_type":  "Payment Processor",
        "criticality":   "High",
        "expected_tier": "High",
        "days_ago":      140,
        "notes":         "Secondary card acquiring route. Overdue for quarterly "
                         "reassessment. No recognised certification, untested BCP, "
                         "and no documented patching SLA.",
        "default":       "Yes",
        "by_category":   {},
        "by_question":   {"U01": "Partial", "U02": "No",      "U03": "Partial",
                          "U04": "No",      "U06": "Partial", "U08": "No",
                          "U09": "Partial", "U10": "No",      "U11": "No",
                          "U12": "Partial", "U13": "No",      "U14": "Partial",
                          "PP03": "Partial", "PP04": "Partial"},
    },
]


def build_answers(vendor):
    """
    Turns a vendor posture into the answers dict calculate_score() expects.

    Precedence: per-question override, then per-category override, then the
    vendor's default answer. The dict shape matches what the Streamlit app
    builds, so the seeded scores are identical to scores entered by hand.
    """
    questions = UNIVERSAL_QUESTIONS + SERVICE_SPECIFIC_QUESTIONS[vendor["service_type"]]
    answers   = {}
    for q in questions:
        answer = vendor["by_question"].get(
            q["id"],
            vendor["by_category"].get(q["category"], vendor["default"]),
        )
        answers[q["id"]] = {
            "answer":   answer,
            "weight":   q["weight"],
            "question": q["question"],
            "category": q["category"],
        }
    return answers


def seed_vendors():
    """Scores and stores all eight vendors. Returns the scored rows."""
    rows = []
    for vendor in VENDORS:
        answers = build_answers(vendor)
        result  = calculate_score(answers)

        if result["tier"] != vendor["expected_tier"]:
            raise AssertionError(
                f"{vendor['name']}: scored {result['score']} "
                f"({result['tier']}), expected tier {vendor['expected_tier']}. "
                "Questionnaire weights or tier thresholds changed — retune the "
                "posture in VENDORS."
            )

        assessment_date = TODAY - timedelta(days=vendor["days_ago"])
        assessment_id   = save_vendor_assessment(
            vendor_name     = vendor["name"],
            service_type    = vendor["service_type"],
            criticality     = vendor["criticality"],
            assessor        = ASSESSOR,
            assessment_date = assessment_date.isoformat(),
            score           = result["score"],
            risk_tier       = result["tier"],
            gap_count       = result["gap_count"],
            critical_gaps   = len(result["critical_gaps"]),
            notes           = vendor["notes"],
        )
        save_vendor_responses(assessment_id, answers)

        rows.append({
            "vendor":    vendor["name"],
            "type":      vendor["service_type"],
            "criticality": vendor["criticality"],
            "score":     result["score"],
            "tier":      result["tier"],
            "gaps":      result["gap_count"],
            "critical":  len(result["critical_gaps"]),
            "date":      assessment_date.isoformat(),
            "days_ago":  vendor["days_ago"],
        })
    return rows


# ─────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────
def print_summary(gaps, scenario_results, vendor_rows):
    windows = get_reassessment_days()

    print(f"\n{'=' * 78}")
    print(f"  DEMO DATASET SEEDED — {ORG_NAME}")
    print(f"{'=' * 78}")

    # ── CSF ──────────────────────────────────────────────────
    print(f"\n{Fore.CYAN}  NIST CSF 2.0 BASELINE{Style.RESET_ALL}\n")
    csf_table = []
    for func_name in CSF_FUNCTIONS:
        score, _ = CSF_SCORES[func_name]
        csf_table.append([
            func_name,
            f"{score}/5",
            f"{DEFAULT_TARGET_SCORE}/5",
            DEFAULT_TARGET_SCORE - score,
            "⚠️  GAP" if func_name in gaps else "✅ OK",
        ])
    print(tabulate(
        csf_table,
        headers=["Function", "Current", "Target", "Gap", "Status"],
        tablefmt="rounded_outline",
    ))
    overall = sum(s for s, _ in CSF_SCORES.values()) / len(CSF_SCORES)
    print(f"\n  Overall maturity: {overall:.1f} / 5.0   "
          f"Gaps recorded: {len(gaps)}")

    # ── FAIR ─────────────────────────────────────────────────
    print(f"\n{Fore.CYAN}  FAIR RISK SCENARIOS{Style.RESET_ALL}\n")
    fair_table = []
    total_ale = total_residual = total_cost = 0
    for key, scenario in SCENARIOS.items():
        result, econ = scenario_results[key]
        total_ale      += result["ale"]
        total_residual += econ["residual_ale"]
        total_cost     += scenario["control_cost"]
        fair_table.append([
            scenario["name"],
            format_currency(result["ale"]),
            format_currency(result["percentile_90"]),
            format_currency(scenario["control_cost"]),
            f"{scenario['control_effectiveness']:.0%}",
            format_currency(econ["residual_ale"]),
            f"{econ['rosi_pct']:.0f}%",
        ])
    print(tabulate(
        fair_table,
        headers=["Scenario", "ALE", "90th %ile", "Control Cost",
                 "Ctrl Eff.", "Residual ALE", "ROSI"],
        tablefmt="rounded_outline",
    ))
    print(f"\n  Portfolio ALE: {format_currency(total_ale)}   "
          f"Residual: {format_currency(total_residual)}   "
          f"Control spend: {format_currency(total_cost)}/yr")

    # ── Vendors ──────────────────────────────────────────────
    print(f"\n{Fore.CYAN}  VENDOR PORTFOLIO{Style.RESET_ALL}\n")
    vendor_table = []
    for r in vendor_rows:
        window  = windows[r["tier"]]
        overdue = r["days_ago"] > window
        vendor_table.append([
            r["vendor"],
            r["type"],
            r["criticality"],
            r["score"],
            r["tier"],
            r["gaps"],
            r["critical"],
            f"{r['days_ago']}d / {window}d",
            "⚠️  OVERDUE" if overdue else "current",
        ])
    print(tabulate(
        vendor_table,
        headers=["Vendor", "Service Type", "Criticality", "Score", "Tier",
                 "Gaps", "Critical", "Age / Window", "Reassessment"],
        tablefmt="rounded_outline",
    ))

    tiers = {row["risk_tier"]: row["count"] for row in get_vendor_tier_summary()}
    print("\n  Tier distribution: " + "  ".join(
        f"{tier} {tiers.get(tier, 0)}" for tier in ("Critical", "High", "Medium", "Low")
    ))

    overdue_rows = get_overdue_vendors()
    print(f"  Overdue for reassessment: {len(overdue_rows)} — " + ", ".join(
        f"{r['vendor_name']} ({r['risk_tier']}, {r['days_since']}d)"
        for r in overdue_rows
    ))

    print(f"\n{'=' * 78}")
    print("  Next: python3 src/reporting/export_for_powerbi.py")
    print(f"{'=' * 78}\n")


def seed_all():
    """Wipes and rebuilds the whole demo dataset."""
    db_path = get_db_path()
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"  Removed existing database: {os.path.basename(db_path)}")

    initialise_database()

    _, gaps          = seed_csf_assessment()
    scenario_results = seed_risk_scenarios()
    vendor_rows      = seed_vendors()

    print_summary(gaps, scenario_results, vendor_rows)


if __name__ == "__main__":
    seed_all()
