# tests/test_vendor_scoring.py
# The vendor score decides a tier, and the tier decides whether a vendor can
# be onboarded, so the boundaries need to be exact rather than approximately
# right.

import pytest

from src.vendor_risk.questionnaire_data import (
    RISK_TIERS,
    SERVICE_SPECIFIC_QUESTIONS,
    SERVICE_TYPES,
    UNIVERSAL_QUESTIONS,
)
from src.vendor_risk.scoring import calculate_score, get_score_label, get_tier_colour


def answers_from(questions, answer):
    """Builds an answers dict giving the same answer to every question."""
    return {
        q["id"]: {
            "answer":   answer,
            "weight":   q["weight"],
            "question": q["question"],
            "category": q["category"],
        }
        for q in questions
    }


def answers_scoring(target):
    """
    Builds an answers dict that scores exactly `target` out of 100.

    100 questions of weight 1 give a 200-point maximum, and each Yes is worth
    2 points, so answering `target` of them Yes lands on exactly `target`.
    """
    return {
        f"Q{i:03d}": {
            "answer":   "Yes" if i < target else "No",
            "weight":   1,
            "question": f"Question {i}",
            "category": "Test",
        }
        for i in range(100)
    }


# ─────────────────────────────────────────────────────────────
# The two extremes
# ─────────────────────────────────────────────────────────────
@pytest.mark.parametrize("service_type", SERVICE_TYPES)
def test_all_yes_scores_100_and_lands_in_low(service_type):
    questions = UNIVERSAL_QUESTIONS + SERVICE_SPECIFIC_QUESTIONS[service_type]
    result    = calculate_score(answers_from(questions, "Yes"))

    assert result["score"] == 100
    assert result["tier"] == "Low"
    assert result["gaps"] == []
    assert result["gap_count"] == 0
    assert result["critical_gaps"] == []


@pytest.mark.parametrize("service_type", SERVICE_TYPES)
def test_all_no_scores_0_and_lands_in_critical(service_type):
    questions = UNIVERSAL_QUESTIONS + SERVICE_SPECIFIC_QUESTIONS[service_type]
    result    = calculate_score(answers_from(questions, "No"))

    assert result["score"] == 0
    assert result["tier"] == "Critical"
    assert result["gap_count"] == len(questions)
    # Every weight-3 "No" is a Critical severity finding
    expected_critical = sum(1 for q in questions if q["weight"] == 3)
    assert len(result["critical_gaps"]) == expected_critical


def test_all_partial_scores_50():
    """Partial earns half the available points."""
    questions = UNIVERSAL_QUESTIONS + SERVICE_SPECIFIC_QUESTIONS["Cloud Provider"]
    result    = calculate_score(answers_from(questions, "Partial"))
    assert result["score"] == 50
    assert result["tier"] == "High"


# ─────────────────────────────────────────────────────────────
# N/A handling
# ─────────────────────────────────────────────────────────────
def test_na_is_excluded_from_the_denominator():
    """
    An N/A question must not count against the vendor.

    Five Yes answers and five N/A should score 100, not 50.
    """
    answers = {
        f"Q{i}": {
            "answer":   "Yes" if i < 5 else "N/A",
            "weight":   1,
            "question": f"Question {i}",
            "category": "Test",
        }
        for i in range(10)
    }
    result = calculate_score(answers)

    assert result["max_points"] == 10      # 5 scored questions x weight 1 x 2
    assert result["total_points"] == 10
    assert result["score"] == 100
    assert result["tier"] == "Low"


def test_na_does_not_create_a_gap():
    answers = answers_from(UNIVERSAL_QUESTIONS, "N/A")
    result  = calculate_score(answers)
    assert result["gaps"] == []
    assert result["max_points"] == 0
    assert result["score"] == 0            # nothing scored, so no evidence of anything


# ─────────────────────────────────────────────────────────────
# Tier boundaries
# ─────────────────────────────────────────────────────────────
@pytest.mark.parametrize("score,expected_tier", [
    (0,   "Critical"),
    (40,  "Critical"),   # top of Critical
    (41,  "High"),       # bottom of High
    (60,  "High"),       # top of High
    (61,  "Medium"),     # bottom of Medium
    (80,  "Medium"),     # top of Medium
    (81,  "Low"),        # bottom of Low
    (100, "Low"),
])
def test_tier_boundaries(score, expected_tier):
    result = calculate_score(answers_scoring(score))
    assert result["score"] == score
    assert result["tier"] == expected_tier


def test_tier_bands_are_contiguous_and_cover_0_to_100():
    """No score between 0 and 100 can fall between two tiers."""
    bands = sorted(
        ((info["min"], info["max"], tier) for tier, info in RISK_TIERS.items()),
    )
    assert bands[0][0] == 0
    assert bands[-1][1] == 100
    for (_, prev_max, _), (next_min, _, _) in zip(bands, bands[1:]):
        assert next_min == prev_max + 1


def test_every_tier_declares_a_reassessment_cycle():
    """get_overdue_vendors() depends on this field existing for every tier."""
    for tier, info in RISK_TIERS.items():
        assert isinstance(info["reassessment_days"], int), tier
        assert info["reassessment_days"] > 0, tier


# ─────────────────────────────────────────────────────────────
# Gap severity and weighting
# ─────────────────────────────────────────────────────────────
def test_weight_3_no_is_critical_and_weight_2_no_is_high():
    answers = {
        "HIGH_W": {"answer": "No", "weight": 3, "question": "q", "category": "c"},
        "MED_W":  {"answer": "No", "weight": 2, "question": "q", "category": "c"},
    }
    by_id = {g["id"]: g for g in calculate_score(answers)["gaps"]}
    assert by_id["HIGH_W"]["severity"] == "Critical"
    assert by_id["MED_W"]["severity"] == "High"


def test_gaps_are_sorted_worst_first():
    answers = {
        "A": {"answer": "Partial", "weight": 2, "question": "q", "category": "c"},
        "B": {"answer": "No",      "weight": 3, "question": "q", "category": "c"},
        "C": {"answer": "No",      "weight": 2, "question": "q", "category": "c"},
    }
    lost = [g["lost_points"] for g in calculate_score(answers)["gaps"]]
    assert lost == sorted(lost, reverse=True)
    assert lost == [6, 4, 2]


def test_a_weight_3_answer_moves_the_score_more_than_a_weight_2_answer():
    base = {
        "W3": {"answer": "Yes", "weight": 3, "question": "q", "category": "c"},
        "W2": {"answer": "Yes", "weight": 2, "question": "q", "category": "c"},
    }
    drop_w3 = dict(base, W3=dict(base["W3"], answer="No"))
    drop_w2 = dict(base, W2=dict(base["W2"], answer="No"))
    assert calculate_score(drop_w3)["score"] < calculate_score(drop_w2)["score"]


def test_empty_questionnaire_does_not_divide_by_zero():
    result = calculate_score({})
    assert result["score"] == 0
    assert result["max_points"] == 0


# ─────────────────────────────────────────────────────────────
def test_tier_colours_and_labels_exist_for_every_tier():
    for tier in RISK_TIERS:
        assert get_tier_colour(tier).startswith("#")
    for score in (10, 50, 70, 95):
        assert get_score_label(score)
