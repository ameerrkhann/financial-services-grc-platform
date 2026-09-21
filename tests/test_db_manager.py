# tests/test_db_manager.py
# Round-trip tests against a throwaway database. The temp_db fixture in
# conftest.py points GRC_DB_PATH at a fresh file for every test, so nothing
# here can touch src/database/grc_platform.db.

import os
import sqlite3
from datetime import date, timedelta

import pytest

from src.database.db_manager import (
    DEFAULT_DB_PATH,
    get_all_risk_scenarios,
    get_all_vendor_assessments,
    get_assessment_gaps,
    get_assessment_scores,
    get_connection,
    get_db_path,
    get_high_risk_scenarios,
    get_latest_scenario_run,
    get_overdue_vendors,
    get_reassessment_days,
    get_vendor_tier_summary,
    initialise_database,
    insert_assessment,
    insert_control_gap,
    insert_function_score,
    save_risk_scenario,
    save_vendor_assessment,
    save_vendor_responses,
)


# ─────────────────────────────────────────────────────────────
# The env-var override itself
# ─────────────────────────────────────────────────────────────
def test_grc_db_path_redirects_away_from_the_real_database(temp_db):
    assert get_db_path() == str(temp_db)
    assert get_db_path() != DEFAULT_DB_PATH


def test_initialise_creates_the_file_and_every_table(temp_db):
    initialise_database(verbose=False)
    assert os.path.exists(temp_db)

    conn   = get_connection()
    tables = {
        r["name"] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()
    assert {
        "assessments", "function_scores", "control_gaps", "risk_scenarios",
        "vendor_assessments", "vendor_responses",
    } <= tables


def test_initialise_is_idempotent(temp_db):
    initialise_database(verbose=False)
    insert_assessment("Bank (Fictional)", "Tester", "2026-09-01")
    initialise_database(verbose=False)   # must not wipe or fail

    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) AS n FROM assessments").fetchone()["n"]
    conn.close()
    assert count == 1


def test_stale_schema_is_migrated_rather_than_crashing(temp_db):
    """
    A database built before the ROSI and target_score columns existed must be
    healed in place, not left to fail later with "no such column".
    """
    old_schema = """
        CREATE TABLE assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, org_name TEXT NOT NULL,
            assessor TEXT NOT NULL, date_run TEXT NOT NULL, notes TEXT);
        CREATE TABLE function_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT, assessment_id INTEGER NOT NULL,
            function_name TEXT NOT NULL, score INTEGER NOT NULL, rationale TEXT);
        CREATE TABLE risk_scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, scenario_key TEXT NOT NULL,
            scenario_name TEXT NOT NULL, loss_low REAL NOT NULL,
            loss_high REAL NOT NULL, freq_low REAL NOT NULL, freq_high REAL NOT NULL,
            ale REAL NOT NULL, median REAL NOT NULL, percentile_90 REAL NOT NULL,
            percentile_95 REAL NOT NULL, prob_over_1m REAL NOT NULL,
            prob_over_5m REAL NOT NULL, control_cost REAL, date_run TEXT NOT NULL,
            osfi_ref TEXT);
    """
    conn = sqlite3.connect(temp_db)
    conn.executescript(old_schema)
    conn.commit()
    conn.close()

    initialise_database(verbose=False)

    conn = get_connection()
    scenario_cols = {r["name"] for r in
                     conn.execute("PRAGMA table_info(risk_scenarios)").fetchall()}
    score_cols    = {r["name"] for r in
                     conn.execute("PRAGMA table_info(function_scores)").fetchall()}
    conn.close()

    assert {"control_effectiveness", "residual_ale", "rosi"} <= scenario_cols
    assert "target_score" in score_cols
    assert get_latest_scenario_run() == []   # the query no longer raises


# ─────────────────────────────────────────────────────────────
# Assessments, scores and gaps
# ─────────────────────────────────────────────────────────────
def test_assessment_round_trip(initialised_db):
    assessment_id = insert_assessment(
        org_name="First National Bank (Fictional)",
        assessor="Ameer Khan",
        date_run="2026-09-21",
        notes="round trip",
    )
    assert assessment_id == 1

    conn = get_connection()
    row  = conn.execute("SELECT * FROM assessments WHERE id = ?",
                        (assessment_id,)).fetchone()
    conn.close()
    assert row["org_name"] == "First National Bank (Fictional)"
    assert row["assessor"] == "Ameer Khan"
    assert row["notes"] == "round trip"


def test_function_score_round_trip_including_target(initialised_db):
    assessment_id = insert_assessment("Bank (Fictional)", "Tester", "2026-09-21")
    insert_function_score(assessment_id, "Respond", 1,
                          rationale="No IRP", target_score=4)

    rows = get_assessment_scores(assessment_id)
    assert len(rows) == 1
    assert rows[0]["function_name"] == "Respond"
    assert rows[0]["score"] == 1
    assert rows[0]["target_score"] == 4
    assert rows[0]["rationale"] == "No IRP"


def test_function_score_target_defaults_to_null(initialised_db):
    assessment_id = insert_assessment("Bank (Fictional)", "Tester", "2026-09-21")
    insert_function_score(assessment_id, "Detect", 2)
    assert get_assessment_scores(assessment_id)[0]["target_score"] is None


def test_control_gap_round_trip(initialised_db):
    assessment_id = insert_assessment("Bank (Fictional)", "Tester", "2026-09-21")
    insert_control_gap(
        assessment_id, "Respond", "No documented IRP", "High",
        nist_ref="RS.MA-01", iso27001_ref="A.5.24, A.5.26",
        soc2_ref="CC7.3", remediation="Write one",
    )
    rows = get_assessment_gaps(assessment_id)
    assert len(rows) == 1
    assert rows[0]["nist_ref"] == "RS.MA-01"
    assert rows[0]["iso27001_ref"] == "A.5.24, A.5.26"


def test_scores_are_scoped_to_their_assessment(initialised_db):
    first  = insert_assessment("Bank A (Fictional)", "Tester", "2026-09-01")
    second = insert_assessment("Bank B (Fictional)", "Tester", "2026-09-02")
    insert_function_score(first, "Govern", 2)
    insert_function_score(second, "Govern", 4)

    assert get_assessment_scores(first)[0]["score"] == 2
    assert get_assessment_scores(second)[0]["score"] == 4


# ─────────────────────────────────────────────────────────────
# Risk scenarios
# ─────────────────────────────────────────────────────────────
def save_scenario(key="ransomware", ale=5_419_843, **overrides):
    payload = dict(
        scenario_key=key, scenario_name="Ransomware Attack",
        loss_low=800_000, loss_high=12_000_000, freq_low=0.5, freq_high=2.0,
        ale=ale, median=3_271_517, percentile_90=13_988_206,
        percentile_95=18_699_724, prob_over_1m=68.0, prob_over_5m=38.7,
        control_cost=500_000, osfi_ref="OSFI B-13",
        control_effectiveness=0.75, residual_ale=1_354_961, rosi=7.13,
    )
    payload.update(overrides)
    save_risk_scenario(**payload)


def test_risk_scenario_round_trip(initialised_db):
    save_scenario()
    rows = get_all_risk_scenarios()
    assert len(rows) == 1
    assert rows[0]["ale"] == pytest.approx(5_419_843)
    assert rows[0]["control_effectiveness"] == pytest.approx(0.75)
    assert rows[0]["residual_ale"] == pytest.approx(1_354_961)
    assert rows[0]["rosi"] == pytest.approx(7.13)
    assert rows[0]["date_run"]          # defaulted to today by the insert


def test_latest_scenario_run_returns_one_row_per_key(initialised_db):
    save_scenario(ale=1_000_000)
    save_scenario(ale=2_000_000)        # a re-run of the same scenario
    save_scenario(key="data_breach", scenario_name="Data Breach", ale=4_970_939)

    latest = get_latest_scenario_run()
    assert len(latest) == 2
    by_key = {r["scenario_key"]: r for r in latest}
    assert by_key["ransomware"]["ale"] == pytest.approx(2_000_000)


def test_latest_scenario_run_is_ordered_by_ale_descending(initialised_db):
    save_scenario(key="small", scenario_name="Small", ale=1_000_000)
    save_scenario(key="large", scenario_name="Large", ale=9_000_000)
    ales = [r["ale"] for r in get_latest_scenario_run()]
    assert ales == sorted(ales, reverse=True)


def test_high_risk_scenarios_respects_the_threshold(initialised_db):
    save_scenario(key="small", scenario_name="Small", ale=500_000)
    save_scenario(key="large", scenario_name="Large", ale=5_000_000)

    assert len(get_high_risk_scenarios(ale_threshold=1_000_000)) == 1
    assert len(get_high_risk_scenarios(ale_threshold=10_000_000)) == 0


# ─────────────────────────────────────────────────────────────
# Vendors
# ─────────────────────────────────────────────────────────────
def save_vendor(name, tier, score, assessment_date, **overrides):
    payload = dict(
        vendor_name=name, service_type="Cloud Provider", criticality="High",
        assessor="Ameer Khan", assessment_date=assessment_date, score=score,
        risk_tier=tier, gap_count=4, critical_gaps=1, notes="",
    )
    payload.update(overrides)
    return save_vendor_assessment(**payload)


def test_vendor_assessment_round_trip(initialised_db):
    assessment_id = save_vendor("NorthPeak Cloud Services", "Low", 88,
                                "2026-09-01")
    rows = get_all_vendor_assessments()
    assert len(rows) == 1
    assert rows[0]["id"] == assessment_id
    assert rows[0]["vendor_name"] == "NorthPeak Cloud Services"
    assert rows[0]["risk_tier"] == "Low"
    assert rows[0]["score"] == 88


def test_vendor_responses_round_trip_and_point_maths(initialised_db):
    assessment_id = save_vendor("MapleLedger Payments", "Medium", 72,
                                "2026-09-01")
    save_vendor_responses(assessment_id, {
        "U01": {"answer": "Yes",     "weight": 3, "question": "q", "category": "Governance"},
        "U04": {"answer": "Partial", "weight": 2, "question": "q", "category": "Incident Response"},
        "U08": {"answer": "No",      "weight": 2, "question": "q", "category": "Data Protection"},
        "U13": {"answer": "N/A",     "weight": 2, "question": "q", "category": "Subcontracting"},
    })

    conn = get_connection()
    rows = {r["question_id"]: r for r in conn.execute(
        "SELECT * FROM vendor_responses WHERE assessment_id = ?",
        (assessment_id,)).fetchall()}
    conn.close()

    assert rows["U01"]["points_earned"] == 6 and rows["U01"]["points_possible"] == 6
    assert rows["U04"]["points_earned"] == 2 and rows["U04"]["points_possible"] == 4
    assert rows["U08"]["points_earned"] == 0 and rows["U08"]["points_possible"] == 4
    # N/A contributes nothing to either side of the ratio
    assert rows["U13"]["points_earned"] == 0 and rows["U13"]["points_possible"] == 0


def test_tier_summary_counts_the_latest_assessment_per_vendor(initialised_db):
    save_vendor("Vendor A", "Low", 90, "2026-01-01")
    save_vendor("Vendor A", "Medium", 70, "2026-09-01")   # reassessed, dropped a tier
    save_vendor("Vendor B", "Critical", 30, "2026-09-01")

    summary = {r["risk_tier"]: r["count"] for r in get_vendor_tier_summary()}
    assert summary == {"Critical": 1, "Medium": 1}


def days_ago(n):
    """An ISO date n days before today, so these tests never go stale."""
    return (date.today() - timedelta(days=n)).isoformat()


def test_overdue_uses_the_window_for_each_tier(initialised_db):
    """Critical and High reassess at 90 days, Medium at 365, Low at 730."""
    assert get_reassessment_days() == {
        "Critical": 90, "High": 90, "Medium": 365, "Low": 730,
    }

    save_vendor("Fresh Critical", "Critical", 30, days_ago(30))
    save_vendor("Stale Critical", "Critical", 30, days_ago(200))
    save_vendor("Stale High",     "High",     50, days_ago(120))
    save_vendor("Stale Medium",   "Medium",   70, days_ago(400))
    save_vendor("Fresh Medium",   "Medium",   70, days_ago(100))
    save_vendor("Fresh Low",      "Low",      90, days_ago(400))

    overdue = {r["vendor_name"] for r in get_overdue_vendors()}
    assert overdue == {"Stale Critical", "Stale High", "Stale Medium"}
    # 400 days is well inside the Low tier's 730-day window
    assert "Fresh Low" not in overdue


def test_overdue_is_ordered_oldest_first(initialised_db):
    save_vendor("Older", "Critical", 30, days_ago(500))
    save_vendor("Newer", "Critical", 30, days_ago(100))
    assert [r["vendor_name"] for r in get_overdue_vendors()] == ["Older", "Newer"]


def test_empty_database_returns_empty_results_not_errors(initialised_db):
    assert get_all_risk_scenarios() == []
    assert get_latest_scenario_run() == []
    assert get_all_vendor_assessments() == []
    assert get_vendor_tier_summary() == []
    assert get_overdue_vendors() == []
