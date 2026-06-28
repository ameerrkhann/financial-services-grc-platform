# Financial Services Cyber Risk Intelligence Platform

**Author:** Ameer Mohammad Khan  
**Background:** 3rd Year CS @ University of Toronto | Data Analyst I @ Manulife | Part-time @ Scotiabank  
**Target Role:** GRC Cybersecurity Analyst — Canadian Financial Services  
**Status:** 🔨 Week 3 Complete — Vendor Risk Assessor

---

## What This Project Is

A Python-based GRC portfolio project simulating a real cybersecurity 
risk program for a fictional Canadian financial institution. Built to 
demonstrate practical GRC engineering skills — not just framework 
knowledge, but working tools that produce real outputs aligned to 
Canadian regulatory requirements.

---

## Three Modules

| Module | Description | Frameworks | Status |
|--------|-------------|------------|--------|
| **NIST CSF 2.0 Assessment** | Maturity scoring engine with gap analysis and cross-framework mapping | NIST CSF 2.0, ISO 27001, SOC 2 | ✅ Complete |
| **Quantitative Risk Engine** | Dollar-value risk modelling across 5 threat scenarios using FAIR | FAIR Methodology | ✅ Complete |
| **Vendor Risk Assessor** | OSFI-aligned questionnaire generator with automated risk tiering | OSFI B-10, B-13, E-21 | ✅ Complete |

---

## Module 1 — NIST CSF 2.0 Assessment Engine

### What it does
- Scores a fictional Canadian bank across all 6 NIST CSF 2.0 functions
- Generates a prioritised gap analysis ranked by risk score and effort
- Maps every control to equivalent ISO 27001 and SOC 2 references
- Saves all assessment data to SQLite with full audit trail

### The 6 Functions Scored

| Function | What It Checks |
|----------|---------------|
| Govern | Cybersecurity policy, board reporting, risk ownership |
| Identify | Asset inventory, risk assessments, threat modelling |
| Protect | MFA, encryption, access controls, security training |
| Detect | SIEM monitoring, alerting, anomaly detection |
| Respond | Incident response plan, OSFI notification requirements |
| Recover | Backup testing, RTOs, business continuity planning |

### Maturity Scale

| Score | Meaning |
|-------|---------|
| 1 | Ad hoc — undocumented and reactive |
| 2 | Developing — inconsistent processes |
| 3 | Defined — documented and followed |
| 4 | Managed — measured with metrics |
| 5 | Optimised — continuously improved |

### Sample Assessment Output

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
| GV.OC-01 | A.5.1 | CC1.1 | Cybersecurity policy |
| PR.AC-01 | A.9.1 | CC6.1 | MFA and access control |
| DE.CM-01 | A.12.4 | CC7.2 | SIEM monitoring |
| RS.RP-01 | A.16.1 | CC7.3 | Incident response plan |
| RC.RP-01 | A.17.1 | A1.2 | Backup and recovery |

### Gap Analysis Output

```
REMEDIATION ROADMAP — FIRST NATIONAL BANK

# | Function  | Score | Priority | Effort | Est. Fix Time | Risk Score
1 | Govern    | 2/5   | Critical | Low    | 4 weeks       | 6
2 | Identify  | 2/5   | Critical | Medium | 8 weeks       | 5
3 | Respond   | 1/5   | High     | Low    | 6 weeks       | 4
4 | Detect    | 2/5   | High     | Medium | 10 weeks      | 3

90-Day Action Plan:
Month 1 → Fix Govern gap (Low effort, ~4 weeks)
Month 2 → Fix Respond gap (Low effort, ~6 weeks)
Month 3 → Fix Identify and Detect gaps (Medium effort)
```

---

## Module 2 — Quantitative Risk Engine (FAIR)

### What it does
- Models 5 realistic threat scenarios for a Canadian financial institution
- Implements FAIR methodology using Monte Carlo simulation (100,000 runs per scenario)
- Produces Annualised Loss Expectancy (ALE) and Loss Exceedance Curves
- Calculates ROI of security controls against expected annual losses
- Stores all results in SQLite for trend analysis and Power BI connection

### Why FAIR over High/Medium/Low

A board member cannot act on "ransomware risk is HIGH."  
They can act on "ransomware carries an expected annual loss of $2.8M,  
with a 10% chance of exceeding $6.8M — versus $500K to implement controls."  
That is the business case FAIR enables.

### The 5 Scenarios

| Scenario | Loss Range | Frequency/Year | ALE (approx) | 90th Percentile | Control Cost |
|----------|-----------|----------------|-------------|-----------------|--------------|
| Data Breach — Customer PII | $500K – $8M | 0.5 – 3.0x | ~$2.1M | ~$5.2M | $350K |
| Ransomware Attack | $800K – $12M | 0.5 – 2.0x | ~$2.8M | ~$6.8M | $500K |
| Insider Threat | $200K – $5M | 0.5 – 2.0x | ~$1.2M | ~$3.1M | $280K |
| Third-Party Vendor Failure | $400K – $9M | 0.3 – 1.5x | ~$1.5M | ~$4.0M | $200K |
| Cloud Misconfiguration | $150K – $6M | 1.0 – 4.0x | ~$1.8M | ~$4.5M | $180K |

### Key Output Metrics

| Metric | Definition |
|--------|-----------|
| ALE | Annualised Loss Expectancy — mean annual loss across 100,000 simulations |
| Median | Typical year estimate |
| 90th Percentile | Loss exceeded in 1 of every 10 years |
| 95th Percentile | Loss exceeded in 1 of every 20 years |
| P(>$1M) | Probability annual loss exceeds $1M |
| P(>$5M) | Probability annual loss exceeds $5M — catastrophic loss indicator |

### Loss Exceedance Curves

![Loss Exceedance Curves — All Scenarios](dashboards/lec_all_scenarios.png)

### Sample Risk Report Output

```
RISK PORTFOLIO REPORT — First National Bank (Fictional)

Scenario                    | ALE      | 90th %ile | P(>$1M) | Control Cost | ROI
Data Breach — Customer PII  | $2.1M    | $5.2M     | 68%     | $350K        | 83%
Ransomware Attack           | $2.8M    | $6.8M     | 74%     | $500K        | 82%
Insider Threat              | $1.2M    | $3.1M     | 52%     | $280K        | 77%
Third-Party Vendor Failure  | $1.5M    | $4.0M     | 58%     | $200K        | 87%
Cloud Misconfiguration      | $1.8M    | $4.5M     | 63%     | $180K        | 90%

Combined Portfolio ALE: ~$9.4M
Total Control Investment:   $1.51M
Estimated Risk Reduction:   60–80%
```

---

## Module 3 — Vendor Risk Assessor (OSFI B-10)

### What it does
- Web app built with Streamlit — runs in the browser, no setup for end users
- Generates tailored security questionnaires based on vendor service type
- Scores responses using a weighted engine (High-weight controls matter more)
- Automatically assigns vendors to risk tiers (Critical / High / Medium / Low)
- Produces a gap report ranked by impact showing exactly what needs fixing
- Saves every assessment to SQLite — full audit trail required by OSFI B-10
- Displays vendor portfolio history with tier distribution dashboard

### Question Coverage

| Vendor Type | Universal Questions | Service-Specific | Total |
|-------------|-------------------|------------------|-------|
| Cloud Provider | 14 | 4 | 18 |
| Payment Processor | 14 | 4 | 18 |
| Software / SaaS | 14 | 4 | 18 |
| Data Analytics / AI | 14 | 4 | 18 |
| IT Infrastructure | 14 | 4 | 18 |

### Question Categories Covered

| Category | Example Question |
|----------|-----------------|
| Governance | Does the vendor have a security policy approved by leadership? |
| Incident Response | Does the vendor notify clients within 24 hours of a confirmed breach? |
| Access Control | Is MFA enforced on all systems with access to client data? |
| Data Protection | Is all client data encrypted at rest (AES-256) and in transit (TLS 1.2+)? |
| Business Continuity | Does the vendor have a tested BCP with defined RTOs? |
| Vulnerability Management | Is penetration testing conducted annually by an independent party? |
| Subcontracting | Are fourth parties subject to equivalent security requirements? |
| Audit Rights | Does the vendor permit client security audits? |

### Risk Tier Thresholds

| Score | Tier | Action Required |
|-------|------|----------------|
| 0–40 | 🔴 Critical | Do not onboard without remediation plan. Executive approval required. |
| 41–60 | 🟠 High | Onboard with conditions. Quarterly reassessment required. |
| 61–80 | 🟡 Medium | Standard onboarding. Annual reassessment required. |
| 81–100 | 🟢 Low | Approve for onboarding. Biennial reassessment required. |

### OSFI B-10 Coverage

| B-10 Requirement | Tool Feature | Coverage |
|-----------------|-------------|----------|
| Risk governance framework | Assessor accountability, tier reporting | ✅ Full |
| Risk-based due diligence | Weighted questionnaire by service type | ✅ Full |
| Vendor risk tiering | Automated Critical/High/Medium/Low assignment | ✅ Full |
| Contractual security requirements | Questions U03, U13, U14 | ✅ Full |
| Ongoing monitoring | Database audit trail, overdue vendor flagging | ✅ Full |
| Fourth-party risk | Dedicated question U13 | ✅ Full |
| Exit planning | Cloud-specific question CL03 | ✅ Partial |
| Audit trail and documentation | Full SQLite record per assessment | ✅ Full |

---

## Regulatory Framework

This project is built specifically for the Canadian financial services 
regulatory environment. All three modules map directly to OSFI requirements.

| Regulation | What It Governs | How This Project Addresses It |
|-----------|----------------|-------------------------------|
| OSFI B-13 (Jan 2024) | Technology and cyber risk management | NIST CSF scorer, FAIR engine, Loss Exceedance Curves |
| OSFI B-10 (Updated 2023) | Third-party vendor risk management | Module 3 vendor risk assessor |
| OSFI E-21 (Deadline Sep 2026) | Operational resilience | Recover function scoring, BCP gap analysis |
| ISO 27001 | International security standard | Cross-framework control mapping in Module 1 |
| SOC 2 | Technology trust and compliance | Cross-framework control mapping in Module 1 |

---

## How to Run

```bash
# 1. Clone and set up environment
git clone https://github.com/YOUR_USERNAME/financial-services-grc-platform.git
cd financial-services-grc-platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Module 1 — NIST CSF Assessment Engine
python3 src/compliance/scoring_engine.py     # Run an assessment
python3 src/compliance/gap_analysis.py       # View gap analysis + roadmap
python3 src/compliance/framework_mapper.py   # View cross-framework mapping

# 3. Module 2 — Quantitative Risk Engine
python3 src/risk_quantification/run_scenarios.py     # Run all 5 scenarios
python3 src/risk_quantification/loss_exceedance.py   # Generate LEC charts
python3 src/risk_quantification/risk_report.py       # View portfolio report

# 4. Module 3 — Vendor Risk Assessor (web app)
streamlit run src/vendor_risk/app.py         # Opens in browser at localhost:8501
```

---

## Tech Stack

| Category | Tools |
|----------|-------|
| Language | Python 3.13 |
| Web Framework | Streamlit |
| Statistical Modelling | numpy, scipy (Monte Carlo simulation) |
| Visualisation | matplotlib |
| Database | SQLite |
| Data Handling | pandas, tabulate |
| Terminal Output | colorama |
| Frameworks | NIST CSF 2.0, ISO 27001, SOC 2, FAIR, OSFI B-10, B-13, E-21 |

---

## Repository Structure

```
financial-services-grc-platform/
├── README.md
├── requirements.txt
├── .gitignore
├── docs/
│   ├── nist_csf_cheatsheet.md
│   ├── nist_csf_gap_analysis.md
│   ├── control_framework_mapping.md
│   ├── risk_assessment_methodology.md
│   ├── osfi_b13_summary.md
│   ├── osfi_b10_mapping.md
│   └── osfi_regulatory_mapping.md
├── src/
│   ├── compliance/
│   │   ├── scoring_engine.py
│   │   ├── gap_analysis.py
│   │   ├── framework_mapper.py
│   │   └── csf_data.py
│   ├── risk_quantification/
│   │   ├── fair_engine.py
│   │   ├── scenarios.py
│   │   ├── run_scenarios.py
│   │   ├── loss_exceedance.py
│   │   └── risk_report.py
│   ├── vendor_risk/
│   │   ├── app.py
│   │   ├── scoring.py
│   │   └── questionnaire_data.py
│   └── database/
│       ├── schema.sql
│       └── db_manager.py
├── dashboards/
│   ├── lec_all_scenarios.png
│   └── lec_[scenario_name].png  (x5 individual charts)
└── tests/
```

---

## Documentation

| Document | Description |
|----------|-------------|
| `docs/nist_csf_cheatsheet.md` | NIST CSF 2.0 quick reference — all 6 functions and maturity descriptors |
| `docs/nist_csf_gap_analysis.md` | Auto-generated gap analysis report from assessment run |
| `docs/control_framework_mapping.md` | Full NIST CSF → ISO 27001 → SOC 2 control mapping table |
| `docs/risk_assessment_methodology.md` | FAIR methodology explanation, scenario parameters, calibration rationale |
| `docs/osfi_b13_summary.md` | OSFI B-13 key requirements and project mapping |
| `docs/osfi_b10_mapping.md` | Full B-10 compliance mapping for Module 3 |
| `docs/osfi_regulatory_mapping.md` | Cross-regulation reference table (B-10, B-13, E-21) |

---

## Interview Preparation

This project directly answers the most common GRC interview questions:

| Interview Question | How This Project Answers It |
|-------------------|----------------------------|
| What is NIST CSF and how have you applied it? | Built a scoring engine across all 6 functions with gap analysis and remediation roadmap |
| How do you quantify risk? | FAIR engine with 100,000 Monte Carlo simulations producing ALE and Loss Exceedance Curves |
| How do you approach third-party vendor risk? | OSFI B-10 aligned Streamlit web app with questionnaire, scoring, tiering, and audit trail |
| What do you know about Canadian financial regulations? | B-13 (Jan 2024), B-10 (2023 update), E-21 (Sep 2026 deadline) — all mapped in project |
| Can you communicate risk to non-technical stakeholders? | Loss Exceedance Curves and executive risk report designed for board-level consumption |
| Why GRC over other cybersecurity paths? | GRC Engineering — automating compliance with Python and SQL is the emerging discipline |

---

## Why Financial Services?

I work as a Data Analyst at Manulife and part-time at Scotiabank. Both 
operate under OSFI regulation. I built this project to demonstrate GRC 
skills in the exact regulatory environment Canadian financial institutions 
operate in — not generic theory, but applied practice.

The OSFI E-21 operational resilience deadline of September 1, 2026 is 
actively creating hiring demand at Canadian banks right now. This 
project directly addresses the frameworks driving that demand.

---

## Coming in Week 4

- Power BI dashboards connecting to the SQLite database
- 2–3 page executive PDF summary
- Excel risk register and control matrix templates
- Loom video walkthrough
- Resume update with project bullets
- LinkedIn project launch post and job applications