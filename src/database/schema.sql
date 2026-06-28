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

-- Week 2: Quantitative Risk Scenarios Table
CREATE TABLE IF NOT EXISTS risk_scenarios (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_key    TEXT NOT NULL,
    scenario_name   TEXT NOT NULL,
    loss_low        REAL NOT NULL,
    loss_high       REAL NOT NULL,
    freq_low        REAL NOT NULL,
    freq_high       REAL NOT NULL,
    ale             REAL NOT NULL,       -- Annualised Loss Expectancy
    median          REAL NOT NULL,
    percentile_90   REAL NOT NULL,
    percentile_95   REAL NOT NULL,
    prob_over_1m    REAL NOT NULL,       -- % chance of exceeding $1M
    prob_over_5m    REAL NOT NULL,       -- % chance of exceeding $5M
    control_cost    REAL,                -- estimated annual control cost
    date_run        TEXT NOT NULL,
    osfi_ref        TEXT
);

-- Week 3: Vendor Risk Assessment Tables

-- One row per vendor assessment run
CREATE TABLE IF NOT EXISTS vendor_assessments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_name     TEXT NOT NULL,
    service_type    TEXT NOT NULL,
    criticality     TEXT NOT NULL,
    assessor        TEXT,
    assessment_date TEXT NOT NULL,
    score           INTEGER NOT NULL,
    risk_tier       TEXT NOT NULL,
    gap_count       INTEGER,
    critical_gaps   INTEGER,
    notes           TEXT,
    date_created    TEXT DEFAULT (date('now'))
);

-- One row per question response per assessment
CREATE TABLE IF NOT EXISTS vendor_responses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id   INTEGER NOT NULL,
    question_id     TEXT NOT NULL,
    category        TEXT NOT NULL,
    question_text   TEXT NOT NULL,
    answer          TEXT NOT NULL,       -- Yes/Partial/No/N/A
    weight          INTEGER NOT NULL,
    points_earned   INTEGER NOT NULL,
    points_possible INTEGER NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES vendor_assessments(id)
);