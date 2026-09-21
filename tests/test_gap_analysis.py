# tests/test_gap_analysis.py
# Gaps drive the remediation roadmap and the executive PDF's second
# recommendation, so both the threshold and the ordering matter.

import pytest

from src.compliance.csf_data import (
    CSF_FUNCTIONS,
    GAP_METADATA,
    REMEDIATION_PRIORITY,
)
from src.compliance.gap_analysis import build_roadmap, calculate_risk_score
from src.compliance.scoring_engine import GAP_THRESHOLD, generate_gaps
from src.database.db_manager import get_assessment_gaps


# ─────────────────────────────────────────────────────────────
# Only scores below the threshold produce a gap
# ─────────────────────────────────────────────────────────────
@pytest.mark.parametrize("score", [1, 2])
def test_scores_below_threshold_produce_a_gap(score):
    for function_name in CSF_FUNCTIONS:
        gap = generate_gaps(function_name, score)
        assert gap is not None, f"{function_name} at {score} should be a gap"
        assert gap["gap"]
        assert gap["nist_ref"]


@pytest.mark.parametrize("score", [3, 4, 5])
def test_scores_at_or_above_threshold_produce_no_gap(score):
    for function_name in CSF_FUNCTIONS:
        assert generate_gaps(function_name, score) is None


def test_gap_threshold_is_the_defined_level():
    assert GAP_THRESHOLD == 3


def test_generate_gaps_reads_from_the_single_source():
    """The gap text comes from GAP_METADATA, not from a copy inside the scorer."""
    for function_name in CSF_FUNCTIONS:
        assert generate_gaps(function_name, 1) is GAP_METADATA[function_name]


def test_generate_gaps_persists_when_given_an_assessment_id(assessment_with_scores):
    assessment_id, _ = assessment_with_scores
    generate_gaps("Respond", 1, assessment_id)

    rows = get_assessment_gaps(assessment_id)
    assert len(rows) == 1
    assert rows[0]["function_name"] == "Respond"
    assert rows[0]["nist_ref"] == GAP_METADATA["Respond"]["nist_ref"]


def test_generate_gaps_does_not_persist_without_an_assessment_id(assessment_with_scores):
    assessment_id, _ = assessment_with_scores
    generate_gaps("Respond", 1)
    assert get_assessment_gaps(assessment_id) == []


# ─────────────────────────────────────────────────────────────
# Risk scoring and ordering
# ─────────────────────────────────────────────────────────────
def test_risk_score_formula():
    """(3 - score) * (7 - priority_rank): bigger gap and higher priority rank higher."""
    assert calculate_risk_score(2, REMEDIATION_PRIORITY["Govern"]) == 6    # 1 * 6
    assert calculate_risk_score(2, REMEDIATION_PRIORITY["Identify"]) == 5  # 1 * 5
    assert calculate_risk_score(1, REMEDIATION_PRIORITY["Respond"]) == 4   # 2 * 2
    assert calculate_risk_score(2, REMEDIATION_PRIORITY["Detect"]) == 3    # 1 * 3


def test_a_lower_score_outranks_a_higher_one_in_the_same_function():
    rank = REMEDIATION_PRIORITY["Detect"]
    assert calculate_risk_score(1, rank) > calculate_risk_score(2, rank)


def test_roadmap_only_contains_functions_below_the_threshold(assessment_with_scores):
    assessment_id, scores = assessment_with_scores
    roadmap = build_roadmap(assessment_id)

    found    = {g["function"] for g in roadmap}
    expected = {f for f, s in scores.items() if s < GAP_THRESHOLD}
    assert found == expected
    assert "Protect" not in found   # scored 3
    assert "Recover" not in found   # scored 3


def test_roadmap_is_ordered_by_risk_score_descending(assessment_with_scores):
    assessment_id, _ = assessment_with_scores
    roadmap = build_roadmap(assessment_id)

    risk_scores = [g["risk_score"] for g in roadmap]
    assert risk_scores == sorted(risk_scores, reverse=True)
    # With the demo baseline this is the published fix order
    assert [g["function"] for g in roadmap] == [
        "Govern", "Identify", "Respond", "Detect",
    ]


def test_roadmap_carries_the_framework_references(assessment_with_scores):
    assessment_id, _ = assessment_with_scores
    for gap in build_roadmap(assessment_id):
        meta = GAP_METADATA[gap["function"]]
        assert gap["nist_ref"] == meta["nist_ref"]
        assert gap["iso_ref"] == meta["iso_ref"]
        assert gap["soc2_ref"] == meta["soc2_ref"]
        assert gap["effort_weeks"] > 0


def test_a_clean_assessment_produces_an_empty_roadmap(initialised_db):
    from src.database.db_manager import insert_assessment, insert_function_score

    assessment_id = insert_assessment("Clean Bank (Fictional)", "Tester",
                                      "2026-09-01")
    for function_name in CSF_FUNCTIONS:
        insert_function_score(assessment_id, function_name, 4, target_score=4)

    assert build_roadmap(assessment_id) == []


# ─────────────────────────────────────────────────────────────
# Reference data integrity
# ─────────────────────────────────────────────────────────────
def test_every_function_has_gap_metadata_and_a_priority():
    for function_name in CSF_FUNCTIONS:
        assert function_name in GAP_METADATA
        assert function_name in REMEDIATION_PRIORITY
        meta = GAP_METADATA[function_name]
        for field in ("gap", "priority", "nist_ref", "iso_ref", "soc2_ref",
                      "remediation", "effort", "effort_weeks", "quick_win",
                      "business_impact"):
            assert meta[field], f"{function_name}.{field} is empty"


def test_no_csf_1_1_identifiers_remain():
    """
    PR.AC, RS.RP and RC.IM were removed in CSF 2.0, and GV.OC-01 is the
    organisational mission rather than the policy subcategory.
    """
    retired = ("PR.AC-", "RS.RP-", "RC.IM-")
    for function_name, meta in GAP_METADATA.items():
        assert not meta["nist_ref"].startswith(retired), (
            f"{function_name} still uses the CSF 1.1 id {meta['nist_ref']}"
        )
    assert GAP_METADATA["Govern"]["nist_ref"] == "GV.PO-01"


def test_no_iso_27001_2013_numbering_remains():
    """The project claims ISO/IEC 27001:2022, so the 2013 clauses must be gone."""
    retired = {"A.9.1", "A.12.4", "A.16.1", "A.17.1", "A.8.1", "A.5.8"}
    for function_name, meta in GAP_METADATA.items():
        refs = {r.strip() for r in meta["iso_ref"].split(",")}
        assert not (refs & retired), (
            f"{function_name} still uses 2013 numbering: {meta['iso_ref']}"
        )
