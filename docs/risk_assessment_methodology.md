# Cyber Risk Assessment Methodology
## Financial Services Cyber Risk Intelligence Platform
**Author:** Ameer Mohammad Khan  
**Organization:** First National Bank (Fictional)  
**Date:** March 2026  

---

## 1. Purpose

This document describes the quantitative risk assessment methodology 
used in the Financial Services Cyber Risk Intelligence Platform. It 
explains how threat scenarios are defined, how financial losses are 
modelled, and how results should be interpreted by risk and executive 
stakeholders.

---

## 2. Methodology: FAIR

This platform uses the **FAIR (Factor Analysis of Information Risk)** 
methodology to express cybersecurity risk in financial terms.

FAIR was chosen over qualitative methods (High/Medium/Low ratings) for 
three reasons:

1. **Decision quality** — Dollar values give executives actionable 
   information. "Ransomware carries an expected annual loss of $2.1M" 
   is more useful than "Ransomware risk is HIGH."

2. **Comparability** — Quantified risks can be ranked, compared, and 
   prioritised against each other and against control costs.

3. **ROI justification** — When control costs are known, FAIR enables 
   a direct cost-benefit calculation. This justifies security investment 
   to boards and audit committees.

---

## 3. FAIR Implementation

FAIR is implemented using **Monte Carlo simulation** with log-normal 
loss distributions and Poisson frequency distributions — the same 
statistical approach used by Netflix's open-source riskquant library.

### 3.1 Key Inputs

| Input | Definition | How Estimated |
|-------|-----------|---------------|
| Loss Low | Minimum plausible single-event loss | Conservative industry benchmark |
| Loss High | Maximum plausible single-event loss | Tail-risk industry benchmark |
| Freq Low | Minimum attack attempts per year | Threat intelligence baseline |
| Freq High | Maximum attack attempts per year | Threat intelligence baseline |

### 3.2 Simulation Process

1. Loss magnitude is modelled as a **log-normal distribution** between 
   Loss Low (5th percentile) and Loss High (95th percentile)
2. Annual frequency is modelled as a **Poisson distribution** with mean 
   equal to the average of Freq Low and Freq High
3. **100,000 Monte Carlo simulations** are run per scenario
4. Each simulation draws a random frequency and random loss magnitude, 
   producing one annual loss estimate
5. The distribution of 100,000 annual loss estimates produces the 
   output statistics

### 3.3 Output Metrics

| Metric | Definition | Use |
|--------|-----------|-----|
| ALE | Annualised Loss Expectancy — mean annual loss across all simulations | Primary risk metric for budgeting |
| Median | Middle value of the loss distribution | Typical year estimate |
| 90th Percentile | Loss exceeded in 1 of 10 years | Planning for bad years |
| 95th Percentile | Loss exceeded in 1 of 20 years | Stress testing |
| P(>$1M) | Probability annual loss exceeds $1M | Board risk threshold metric |
| P(>$5M) | Probability annual loss exceeds $5M | Catastrophic loss indicator |

---

## 4. Scenario Definitions

### Scenario 1 — Data Breach (Customer PII)
Unauthorised exfiltration of customer PII including names, SINs, and 
account data. Loss range reflects regulatory fines (OSFI, PIPEDA), 
legal costs, customer notification, and reputational damage.

- **Loss range:** $500K – $8M | **Frequency:** 0.5–3.0x/year
- **Regulatory ref:** OSFI B-13 s.5 — 24-hour incident notification
- **ALE benchmark:** ~$2.1M (varies per simulation run)

### Scenario 2 — Ransomware Attack
Malware encrypts critical banking systems causing operational shutdown. 
Loss includes ransom consideration, recovery costs, business interruption, 
and regulatory reporting costs.

- **Loss range:** $800K – $12M | **Frequency:** 0.5–2.0x/year
- **Regulatory ref:** OSFI B-13 s.5 — Technology Incident Reporting
- **ALE benchmark:** ~$2.8M (varies per simulation run)

### Scenario 3 — Insider Threat
Privileged access abuse by employee or contractor. Harder to detect 
than external attacks. Loss includes fraud, data theft, and 
investigation costs.

- **Loss range:** $200K – $5M | **Frequency:** 0.5–2.0x/year
- **Regulatory ref:** OSFI B-13 s.4 — Cyber Risk Governance
- **ALE benchmark:** ~$1.2M (varies per simulation run)

### Scenario 4 — Third-Party Vendor Failure
Security failure at a critical vendor exposes bank data or disrupts 
services. Bank bears liability even for externally-originated breaches. 
OSFI B-10 governs vendor risk management.

- **Loss range:** $400K – $9M | **Frequency:** 0.3–1.5x/year
- **Regulatory ref:** OSFI B-10 — Third-Party Risk Management
- **ALE benchmark:** ~$1.5M (varies per simulation run)

### Scenario 5 — Cloud Misconfiguration
Misconfigured cloud storage or IAM policies expose sensitive data 
publicly. Most frequent scenario due to rapid cloud adoption and 
configuration complexity.

- **Loss range:** $150K – $6M | **Frequency:** 1.0–4.0x/year
- **Regulatory ref:** OSFI B-13 s.6 — Cloud Risk Management
- **ALE benchmark:** ~$1.8M (varies per simulation run)

---

## 5. Parameter Calibration

Loss ranges are calibrated to the Canadian financial services context 
using the following sources:

- IBM Cost of a Data Breach Report — Canada financial sector benchmarks
- Ponemon Institute financial services cyber loss studies
- OSFI publicly disclosed incident summaries
- Verizon Data Breach Investigations Report (DBIR) — financial sector

Frequency estimates reflect the threat landscape for a mid-size 
federally regulated financial institution (assets $5B–$50B).

---

## 6. Limitations

1. **Fictional organisation** — all parameters are illustrative. Real 
   assessments require organisation-specific threat intelligence and 
   historical loss data.

2. **Independence assumption** — scenarios are modelled independently. 
   In practice, a single attack may trigger multiple scenarios 
   simultaneously (e.g. ransomware causing both operational disruption 
   and data breach).

3. **Control effectiveness** — control cost estimates assume full 
   implementation. Partial implementations will produce lower risk 
   reduction.

4. **Static parameters** — the threat landscape evolves. Parameters 
   should be reviewed annually or after significant incidents.

---

## 7. Regulatory Context

This assessment is designed with Canadian federally regulated financial 
institutions in mind. Key regulatory obligations addressed:

| Regulation | Requirement Addressed |
|-----------|----------------------|
| OSFI B-13 | Technology and cyber risk governance, incident reporting |
| OSFI B-10 | Third-party vendor risk assessment and monitoring |
| OSFI E-21 | Operational resilience and recovery planning |
| PIPEDA | Customer data breach notification obligations |

---

## 8. How to Use This Report

**For risk and GRC teams:** Use ALE figures to populate the risk 
register. Use 90th percentile figures for insurance coverage decisions.

**For the CISO:** Use the portfolio ALE and P(>$1M) metrics for 
board reporting. Frame control investments against ALE reduction.

**For executive and board audiences:** Focus on ALE and the 
cost-benefit analysis. "We can reduce a $2.8M expected annual loss 
to under $500K with a $500K control investment" is the business case.