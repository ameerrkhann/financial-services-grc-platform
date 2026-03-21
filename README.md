# Financial Services Cyber Risk Intelligence Platform

**Author:** Ameer Mohammad Khan  
**Background:** 4rd Year CS @ University of Toronto | Data Analyst I @ Manulife | Part-time @ Scotiabank  
**Target Role:** GRC Cybersecurity Analyst — Canadian Financial Services  
**Status:** 🔨 Week 1 Complete — NIST CSF 2.0 Assessment Engine

---

## What This Project Is

A Python-based GRC portfolio project that simulates a real cybersecurity 
risk program for a fictional Canadian financial institution. Built to 
demonstrate practical GRC engineering skills to hiring managers — not 
just framework knowledge, but working tools.

---

## Three Modules

| Module | Description | Frameworks | Status |
|--------|-------------|------------|--------|
| **NIST CSF 2.0 Assessment** | Maturity scoring engine with gap analysis and remediation roadmap | NIST CSF 2.0, ISO 27001, SOC 2 | ✅ Complete |
| **Quantitative Risk Engine** | Dollar-value risk modelling across 5 threat scenarios | FAIR, Netflix riskquant | 🔨 Week 2 |
| **Vendor Risk Assessor** | Questionnaire generator with OSFI-aligned risk tiering | OSFI B-10, B-13 | 📅 Week 3 |

---

## Module 1 — NIST CSF 2.0 Assessment Engine

### What it does
- Scores a fictional Canadian bank across all 6 NIST CSF 2.0 functions
- Generates a prioritised gap analysis ranked by risk score
- Maps every control to equivalent ISO 27001 and SOC 2 references
- Saves all assessment data to a SQLite database with full audit trail

### The 6 Functions Scored
| Function | What It Checks |
|----------|---------------|
| Govern | Cybersecurity policy, board reporting, risk ownership |
| Identify | Asset inventory, risk assessments, threat modelling |
| Protect | MFA, encryption, access controls, security training |
| Detect | SIEM monitoring, alerting, anomaly detection |
| Respond | Incident response plan, OSFI notification requirements |
| Recover | Backup testing, RTOs, business continuity planning |

### Sample Output — Assessment Results
```
╭───────────┬───────┬────────────┬──────────╮
│ Function  │ Score │ Visual     │ Status   │
├───────────┼───────┼────────────┼──────────┤
│ Govern    │ 2/5   │ ██░░░      │ ⚠️  GAP  │
│ Identify  │ 2/5   │ ██░░░      │ ⚠️  GAP  │
│ Protect   │ 3/5   │ ███░░      │ ✅ OK    │
│ Detect    │ 2/5   │ ██░░░      │ ⚠️  GAP  │
│ Respond   │ 1/5   │ █░░░░      │ ⚠️  GAP  │
│ Recover   │ 3/5   │ ███░░      │ ✅ OK    │
╰───────────┴───────┴────────────┴──────────╯
Overall Maturity Score: 2.2 / 5.0
```

### Cross-Framework Mapping
One control satisfying three frameworks simultaneously — no duplicate compliance work:

| NIST CSF | ISO 27001 | SOC 2 | What It Does |
|----------|-----------|-------|--------------|
| PR.AC-01 | A.9.1 | CC6.1 | MFA + access control |
| DE.CM-01 | A.12.4 | CC7.2 | SIEM monitoring |
| RS.RP-01 | A.16.1 | CC7.3 | Incident response plan |

---

## How to Run
```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/financial-services-grc-platform.git
cd financial-services-grc-platform

# Set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the scoring engine
python3 src/compliance/scoring_engine.py

# Run the gap analysis
python3 src/compliance/gap_analysis.py

# Run the framework mapper
python3 src/compliance/framework_mapper.py
```

---

## Tech Stack
- **Python 3.13** — scoring engine, gap analysis, framework mapping
- **SQLite** — assessment data storage with audit trail
- **pandas** — data manipulation
- **tabulate** — formatted terminal output
- **colorama** — colour-coded results

---

## Repository Structure
```
financial-services-grc-platform/
├── README.md
├── requirements.txt
├── docs/
│   ├── nist_csf_cheatsheet.md
│   ├── nist_csf_gap_analysis.md
│   └── control_framework_mapping.md
├── src/
│   ├── compliance/
│   │   ├── scoring_engine.py
│   │   ├── gap_analysis.py
│   │   ├── framework_mapper.py
│   │   └── csf_data.py
│   └── database/
│       ├── schema.sql
│       └── db_manager.py
└── tests/
```

---

## Why Financial Services?

I work as a Data Analyst at Manulife and part-time at Scotiabank. Both 
operate under OSFI regulation. I built this project to demonstrate GRC 
skills in the exact regulatory environment Canadian financial institutions 
operate in — not generic theory, but applied practice.

---

## Coming in Weeks 2–4
- **Week 2:** Quantitative risk engine using Netflix's riskquant + FAIR methodology
- **Week 3:** Streamlit vendor risk assessor aligned to OSFI B-10 and B-13
- **Week 4:** Power BI dashboards, executive PDF summary, Excel risk register
