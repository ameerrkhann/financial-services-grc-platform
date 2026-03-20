-- Financial Services GRC Platform
-- SQLite Database Schema
-- Week 1: NIST CSF Assessment Tables

-- Stores each time someone runs a full assessment
CREATE TABLE IF NOT EXISTS assessments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    org_name    TEXT NOT NULL,          -- e.g. "First National Bank (Fictional)"
    assessor    TEXT NOT NULL,          -- e.g. "Ameer Khan"
    date_run    TEXT NOT NULL,          -- e.g. "2026-03-20"
    notes       TEXT                    -- any free-text context
);

-- Stores the score for each of the 6 CSF functions
CREATE TABLE IF NOT EXISTS function_scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id   INTEGER NOT NULL,
    function_name   TEXT NOT NULL,      -- e.g. "Govern", "Identify"
    score           INTEGER NOT NULL,   -- 1 to 5
    rationale       TEXT,               -- why this score was given
    FOREIGN KEY (assessment_id) REFERENCES assessments(id)
);

-- Stores each gap identified (any function scoring below 3)
CREATE TABLE IF NOT EXISTS control_gaps (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id   INTEGER NOT NULL,
    function_name   TEXT NOT NULL,
    gap_description TEXT NOT NULL,      -- what is missing
    priority        TEXT NOT NULL,      -- "Critical", "High", "Medium"
    nist_ref        TEXT,               -- e.g. "GV.OC-01"
    iso27001_ref    TEXT,               -- e.g. "A.5.1"
    soc2_ref        TEXT,               -- e.g. "CC1.1"
    remediation     TEXT,               -- what to do to fix it
    FOREIGN KEY (assessment_id) REFERENCES assessments(id)
);