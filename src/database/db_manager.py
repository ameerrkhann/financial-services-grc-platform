# src/database/db_manager.py
# Handles all database operations for the GRC platform

import sqlite3
import os

# The database file lives in the same folder as this script
DB_PATH = os.path.join(os.path.dirname(__file__), "grc_platform.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn


def initialise_database():
    """Creates all tables if they don't exist yet."""
    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
    conn = get_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("✅ Database initialised successfully.")


def insert_assessment(org_name, assessor, date_run, notes=""):
    """Saves a new assessment run. Returns the new assessment ID."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO assessments (org_name, assessor, date_run, notes) VALUES (?, ?, ?, ?)",
        (org_name, assessor, date_run, notes)
    )
    conn.commit()
    assessment_id = cursor.lastrowid
    conn.close()
    return assessment_id


def insert_function_score(assessment_id, function_name, score, rationale=""):
    """Saves a score for one CSF function."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO function_scores 
           (assessment_id, function_name, score, rationale) 
           VALUES (?, ?, ?, ?)""",
        (assessment_id, function_name, score, rationale)
    )
    conn.commit()
    conn.close()


def insert_control_gap(assessment_id, function_name, gap_description,
                        priority, nist_ref="", iso27001_ref="",
                        soc2_ref="", remediation=""):
    """Saves a control gap identified during assessment."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO control_gaps 
           (assessment_id, function_name, gap_description, priority,
            nist_ref, iso27001_ref, soc2_ref, remediation)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (assessment_id, function_name, gap_description, priority,
         nist_ref, iso27001_ref, soc2_ref, remediation)
    )
    conn.commit()
    conn.close()


def get_assessment_scores(assessment_id):
    """Returns all function scores for a given assessment."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM function_scores WHERE assessment_id = ?",
        (assessment_id,)
    ).fetchall()
    conn.close()
    return rows


def get_assessment_gaps(assessment_id):
    """Returns all control gaps for a given assessment."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM control_gaps WHERE assessment_id = ?",
        (assessment_id,)
    ).fetchall()
    conn.close()
    return rows


# Quick test — run this file directly to confirm everything works
if __name__ == "__main__":
    initialise_database()
    
    # Insert a test assessment
    aid = insert_assessment(
        org_name="First National Bank (Fictional)",
        assessor="Ameer Khan",
        date_run="2026-03-20",
        notes="Initial baseline assessment"
    )
    print(f"✅ Test assessment created with ID: {aid}")

    # Insert a test score
    insert_function_score(aid, "Govern", 2, "No formal cybersecurity policy exists")
    print("✅ Test score inserted.")

    # Read it back
    scores = get_assessment_scores(aid)
    for row in scores:
        print(f"   → {row['function_name']}: {row['score']}/5")