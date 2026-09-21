# tests/conftest.py
# Shared fixtures.
#
# The autouse temp_db fixture points GRC_DB_PATH at a fresh file per test, so
# no test can reach src/database/grc_platform.db even by accident.

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.database.db_manager import (  # noqa: E402
    get_db_path,
    initialise_database,
    insert_assessment,
    insert_function_score,
)


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Redirects the database to a throwaway file for the duration of a test."""
    db_path = tmp_path / "test_grc_platform.db"
    monkeypatch.setenv("GRC_DB_PATH", str(db_path))
    assert get_db_path() == str(db_path)
    yield db_path


@pytest.fixture
def initialised_db(temp_db):
    """A temp database with the schema applied."""
    initialise_database(verbose=False)
    return temp_db


@pytest.fixture
def assessment_with_scores(initialised_db):
    """
    An assessment carrying the demo baseline scores.

    Govern 2, Identify 2, Protect 3, Detect 2, Respond 1, Recover 3 — four
    functions below the gap threshold and two above it.
    """
    scores = {
        "Govern": 2, "Identify": 2, "Protect": 3,
        "Detect": 2, "Respond": 1, "Recover": 3,
    }
    assessment_id = insert_assessment(
        org_name="Test Bank (Fictional)",
        assessor="Test Assessor",
        date_run="2026-09-01",
        notes="pytest fixture",
    )
    for function_name, score in scores.items():
        insert_function_score(
            assessment_id, function_name, score,
            rationale=f"{function_name} rationale", target_score=4,
        )
    return assessment_id, scores
