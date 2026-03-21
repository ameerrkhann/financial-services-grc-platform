# src/compliance/gap_analysis.py
# Generates a prioritised remediation roadmap from assessment results

import sys
import os
from datetime import date
from tabulate import tabulate
from colorama import Fore, Style, init

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.compliance.csf_data import GAP_METADATA, REMEDIATION_PRIORITY
from src.database.db_manager import (
    get_connection,
    get_assessment_scores,
    get_assessment_gaps,
)

init(autoreset=True)


def get_all_assessments():
    """Returns a list of all assessments in the database."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, org_name, assessor, date_run FROM assessments ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows


def calculate_risk_score(score, priority_rank):
    """
    Calculates a simple risk score to rank what to fix first.
    Lower maturity + higher priority function = higher risk score.
    """
    gap_severity = (3 - score)          # 0 to 2 (bigger gap = higher severity)
    priority_weight = (7 - priority_rank)  # 6 to 1 (Govern is most critical)
    return gap_severity * priority_weight


def build_roadmap(assessment_id):
    """
    Pulls scores from the database and builds a prioritised
    remediation roadmap for all functions scoring below 3.
    """
    scores = get_assessment_scores(assessment_id)
    
    gaps_found = []
    for row in scores:
        func_name = row["function_name"]
        score     = row["score"]
        
        if score < 3:
            priority_rank = REMEDIATION_PRIORITY[func_name]
            risk_score    = calculate_risk_score(score, priority_rank)
            metadata      = GAP_METADATA[func_name]
            
            gaps_found.append({
                "function":        func_name,
                "score":           score,
                "priority":        metadata["priority"],
                "risk_score":      risk_score,
                "effort":          metadata["effort"],
                "effort_weeks":    metadata["effort_weeks"],
                "business_impact": metadata["business_impact"],
                "quick_win":       metadata["quick_win"],
                "remediation":     metadata["remediation"],
                "nist_ref":        metadata["nist_ref"],
                "iso_ref":         metadata["iso_ref"],
                "soc2_ref":        metadata["soc2_ref"],
            })
    
    # Sort by risk score descending — highest risk first
    gaps_found.sort(key=lambda x: x["risk_score"], reverse=True)
    return gaps_found


def print_roadmap(org_name, gaps, assessment_id):
    """Prints the full remediation roadmap to the terminal."""
    print(f"\n{'=' * 65}")
    print(f"  REMEDIATION ROADMAP — {org_name.upper()}")
    print(f"  Generated: {date.today().isoformat()}")
    print(f"{'=' * 65}")

    if not gaps:
        print(f"\n{Fore.GREEN}  ✅ No gaps found. All functions score 3 or above.{Style.RESET_ALL}")
        return

    print(f"\n  {len(gaps)} gap(s) identified. Ranked by risk score (fix highest first).\n")

    # Summary table
    table_data = []
    for i, gap in enumerate(gaps, 1):
        table_data.append([
            i,
            gap["function"],
            f"{gap['score']}/5",
            gap["priority"],
            gap["effort"],
            f"{gap['effort_weeks']} weeks",
            gap["risk_score"],
        ])

    print(tabulate(
        table_data,
        headers=["#", "Function", "Score", "Priority", "Effort", "Est. Fix Time", "Risk Score"],
        tablefmt="rounded_outline"
    ))

    # Detailed breakdown per gap
    print(f"\n{Fore.YELLOW}  DETAILED REMEDIATION PLAN{Style.RESET_ALL}")
    for i, gap in enumerate(gaps, 1):
        colour = Fore.RED if gap["priority"] == "Critical" else Fore.YELLOW
        print(f"\n  {colour}#{i} — {gap['function']} | {gap['priority']} | Score: {gap['score']}/5{Style.RESET_ALL}")
        print(f"  Framework refs: NIST {gap['nist_ref']} | ISO 27001 {gap['iso_ref']} | SOC 2 {gap['soc2_ref']}")
        print(f"\n  Why it matters:")
        print(f"  {gap['business_impact']}")
        print(f"\n  ⚡ Quick win:")
        print(f"  {gap['quick_win']}")
        print(f"\n  Full remediation:")
        print(f"  {gap['remediation']}")
        print(f"  {'─' * 55}")

    # 90-day action plan
    print(f"\n{Fore.CYAN}  90-DAY ACTION PLAN{Style.RESET_ALL}")
    print(f"  Based on effort estimates and risk priority:\n")

    sprints = {
        "Month 1 (Days 1–30)":  [g for g in gaps if g["effort_weeks"] <= 4],
        "Month 2 (Days 31–60)": [g for g in gaps if 4 < g["effort_weeks"] <= 8],
        "Month 3 (Days 61–90)": [g for g in gaps if g["effort_weeks"] > 8],
    }

    for period, items in sprints.items():
        if items:
            print(f"  {Fore.CYAN}{period}{Style.RESET_ALL}")
            for item in items:
                print(f"    → Fix {item['function']} gap ({item['effort']} effort, ~{item['effort_weeks']} weeks)")
    
    print(f"\n{'=' * 65}\n")


def save_roadmap_to_file(org_name, gaps, assessment_id):
    """Saves a plain-text version of the roadmap to /docs."""
    output_path = os.path.join(
        os.path.dirname(__file__), "../../docs/nist_csf_gap_analysis.md"
    )

    lines = []
    lines.append(f"# NIST CSF 2.0 Gap Analysis — {org_name}")
    lines.append(f"**Assessment ID:** {assessment_id}")
    lines.append(f"**Generated:** {date.today().isoformat()}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total gaps identified: {len(gaps)}")
    lines.append(f"- Critical gaps: {sum(1 for g in gaps if g['priority'] == 'Critical')}")
    lines.append(f"- High gaps: {sum(1 for g in gaps if g['priority'] == 'High')}")
    lines.append(f"- Medium gaps: {sum(1 for g in gaps if g['priority'] == 'Medium')}")
    lines.append("")
    lines.append("## Prioritised Gaps")
    lines.append("")

    for i, gap in enumerate(gaps, 1):
        lines.append(f"### #{i} — {gap['function']} ({gap['priority']})")
        lines.append(f"- **Score:** {gap['score']}/5")
        lines.append(f"- **NIST CSF:** {gap['nist_ref']}")
        lines.append(f"- **ISO 27001:** {gap['iso_ref']}")
        lines.append(f"- **SOC 2:** {gap['soc2_ref']}")
        lines.append(f"- **Effort:** {gap['effort']} (~{gap['effort_weeks']} weeks)")
        lines.append(f"- **Business Impact:** {gap['business_impact']}")
        lines.append(f"- **Quick Win:** {gap['quick_win']}")
        lines.append(f"- **Remediation:** {gap['remediation']}")
        lines.append("")

    lines.append("## 90-Day Action Plan")
    lines.append("")
    sprints = {
        "Month 1 (Days 1–30)":  [g for g in gaps if g["effort_weeks"] <= 4],
        "Month 2 (Days 31–60)": [g for g in gaps if 4 < g["effort_weeks"] <= 8],
        "Month 3 (Days 61–90)": [g for g in gaps if g["effort_weeks"] > 8],
    }
    for period, items in sprints.items():
        if items:
            lines.append(f"### {period}")
            for item in items:
                lines.append(f"- Fix **{item['function']}** gap (~{item['effort_weeks']} weeks)")
            lines.append("")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"  ✅ Gap analysis saved to docs/nist_csf_gap_analysis.md")


def run_gap_analysis():
    """Main function — lets you pick an assessment and view its roadmap."""
    print("\n" + "=" * 65)
    print("   NIST CSF 2.0 — Gap Analysis & Remediation Roadmap")
    print("=" * 65)

    # Show all past assessments
    assessments = get_all_assessments()
    if not assessments:
        print("\n  No assessments found. Run the scoring engine first.")
        return

    print("\n  Available assessments:\n")
    for a in assessments:
        print(f"  [{a['id']}] {a['org_name']} — {a['date_run']} (assessed by {a['assessor']})")

    while True:
        try:
            choice = int(input("\n  Enter assessment ID to analyse: "))
            selected = next((a for a in assessments if a["id"] == choice), None)
            if selected:
                break
            print("  ID not found. Try again.")
        except ValueError:
            print("  Please enter a number.")

    org_name = selected["org_name"]
    gaps     = build_roadmap(choice)

    print_roadmap(org_name, gaps, choice)
    save_roadmap_to_file(org_name, gaps, choice)


if __name__ == "__main__":
    run_gap_analysis()