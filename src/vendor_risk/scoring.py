# src/vendor_risk/scoring.py
# Vendor risk scoring engine — OSFI B-10 aligned

from src.vendor_risk.questionnaire_data import RISK_TIERS


def calculate_score(answers: dict) -> dict:
    """
    Calculates a vendor risk score from questionnaire answers.

    Parameters
    ----------
    answers : dict
        Keys are question IDs.
        Values are dicts with 'answer' (Yes/Partial/No/N/A) and 'weight'.

    Returns
    -------
    dict with score, tier, points breakdown, and gap list
    """
    total_points = 0
    max_points   = 0
    gaps         = []
    strengths    = []

    for qid, data in answers.items():
        weight = data["weight"]
        ans    = data["answer"]
        label  = data.get("question", qid)
        cat    = data.get("category", "General")

        if ans == "N/A":
            continue  # exclude from scoring

        max_points += weight * 2

        if ans == "Yes":
            total_points += weight * 2
            if weight == 3:  # only track high-weight strengths
                strengths.append({
                    "id":       qid,
                    "category": cat,
                    "question": label,
                    "impact":   "High",
                })
        elif ans == "Partial":
            total_points += weight * 1
            gaps.append({
                "id":         qid,
                "category":   cat,
                "question":   label,
                "answer":     "Partial",
                "lost_points": weight,
                "severity":   "High" if weight == 3 else "Medium",
            })
        elif ans == "No":
            gaps.append({
                "id":         qid,
                "category":   cat,
                "question":   label,
                "answer":     "No",
                "lost_points": weight * 2,
                "severity":   "Critical" if weight == 3 else "High",
            })

    # Calculate final score
    score = int((total_points / max_points) * 100) if max_points > 0 else 0

    # Determine risk tier
    tier      = "Critical"
    tier_info = RISK_TIERS["Critical"]
    for tier_name, info in RISK_TIERS.items():
        if info["min"] <= score <= info["max"]:
            tier      = tier_name
            tier_info = info
            break

    # Sort gaps by lost points descending — worst gaps first
    gaps.sort(key=lambda x: x["lost_points"], reverse=True)

    return {
        "score":        score,
        "tier":         tier,
        "tier_info":    tier_info,
        "total_points": total_points,
        "max_points":   max_points,
        "gaps":         gaps,
        "strengths":    strengths,
        "gap_count":    len(gaps),
        "critical_gaps": [g for g in gaps if g["severity"] == "Critical"],
        "high_gaps":    [g for g in gaps if g["severity"] == "High"],
    }


def get_tier_colour(tier: str) -> str:
    """Returns a hex colour for a given risk tier."""
    colours = {
        "Critical": "#ff2d55",
        "High":     "#ff6b35",
        "Medium":   "#ffdd00",
        "Low":      "#32d74b",
    }
    return colours.get(tier, "#ffffff")


def get_score_label(score: int) -> str:
    """Returns a plain English label for a score range."""
    if score >= 81:
        return "Strong security posture — meets OSFI B-10 baseline requirements."
    elif score >= 61:
        return "Adequate posture with gaps — acceptable with a remediation plan."
    elif score >= 41:
        return "Significant gaps — conditional onboarding with enhanced monitoring."
    else:
        return "Inadequate security posture — do not onboard without remediation."