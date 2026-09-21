# Cyber Risk Assessment Methodology
## Financial Services Cyber Risk Intelligence Platform
**Author:** Ameer Mohammad Khan  
**Organization:** First National Bank (Fictional)  
**Date:** September 2026  

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
   information. "Ransomware carries an expected annual loss of $5.42M" 
   is more useful than "Ransomware risk is HIGH."

2. **Comparability** — Quantified risks can be ranked, compared, and 
   prioritised against each other and against control costs.

3. **ROSI justification** — When control costs and an assumed control
   effectiveness are known, FAIR enables a direct Return on Security
   Investment calculation. This justifies security investment to boards
   and audit committees.

---

## 3. FAIR Implementation

FAIR is implemented using **Monte Carlo simulation** with log-normal 
loss distributions and Poisson frequency distributions — the same 
statistical approach used by Netflix's open-source riskquant library. 
riskquant itself is not a dependency (it does not support Python 3.13); 
the maths is implemented directly with numpy in `fair_engine.py`.

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
3. **100,000 Monte Carlo simulations** are run per scenario — one 
   simulation is one simulated year
4. Each simulated year draws an event count `N ~ Poisson(lambda)`, then 
   draws **N independent** loss magnitudes and sums them. Each loss event 
   is its own draw, which is what FAIR specifies — multiplying a single 
   magnitude by the event count would force every event in a year to cost 
   exactly the same and would materially overstate the tail
5. The distribution of 100,000 annual loss estimates produces the 
   output statistics
6. Each scenario is simulated with a fixed seed (`fair_engine.seed_for`), 
   so the ALE quoted in the README, the Power BI export, the executive PDF 
   and the risk register are all the same number

### 3.3 Output Metrics

| Metric | Definition | Use |
|--------|-----------|-----|
| ALE | Annualised Loss Expectancy — mean annual loss across all simulations | Primary risk metric for budgeting |
| Median | Middle value of the loss distribution | Typical year estimate |
| 90th Percentile | Loss exceeded in 1 of 10 years | Planning for bad years |
| 95th Percentile | Loss exceeded in 1 of 20 years | Stress testing |
| P(>$1M) | Probability annual loss exceeds $1M | Board risk threshold metric |
| P(>$5M) | Probability annual loss exceeds $5M | Catastrophic loss indicator |

### 3.4 Control Economics (ROSI)

Control value is expressed as **Return on Security Investment**, not as a
percentage of ALE avoided:

```
residual_ale   = ale * (1 - control_effectiveness)
risk_reduction = ale - residual_ale
rosi           = (risk_reduction - control_cost) / control_cost
```

`control_effectiveness` is an **assumption** recorded per scenario in
`scenarios.py` (0.60–0.80 across the portfolio). It is a judgement about how
much of the annual expected loss the listed control set removes — it is not
measured, and it is deliberately below 1.0 because controls reduce risk
rather than eliminate it.

---

## 4. Scenario Definitions

### Scenario 1 — Data Breach (Customer PII)
Unauthorised exfiltration of customer PII including names, SINs, and 
account data. Loss range reflects regulatory fines (OSFI, PIPEDA), 
legal costs, customer notification, and reputational damage.

- **Loss range:** $500K – $8M | **Frequency:** 0.5–3.0x/year
- **Regulatory ref:** OSFI *Technology and Cyber Security Incident Reporting* advisory — reportable incidents reported within 24 hours
- **ALE (seeded run):** $4.97M | **90th percentile:** $11.74M | **ROSI:** 894% at $350K/yr (70% assumed effectiveness)

### Scenario 2 — Ransomware Attack
Malware encrypts critical banking systems causing operational shutdown. 
Loss includes ransom consideration, recovery costs, business interruption, 
and regulatory reporting costs.

- **Loss range:** $800K – $12M | **Frequency:** 0.5–2.0x/year
- **Regulatory ref:** OSFI B-13 — Technology Operations and Resilience; reporting per the OSFI incident reporting advisory
- **ALE (seeded run):** $5.42M | **90th percentile:** $13.99M | **ROSI:** 713% at $500K/yr (75% assumed effectiveness)

### Scenario 3 — Insider Threat
Privileged access abuse by employee or contractor. Harder to detect 
than external attacks. Loss includes fraud, data theft, and 
investigation costs.

- **Loss range:** $200K – $5M | **Frequency:** 0.5–2.0x/year
- **Regulatory ref:** OSFI B-13 — Cyber Security domain (identity and access management)
- **ALE (seeded run):** $2.02M | **90th percentile:** $5.27M | **ROSI:** 368% at $280K/yr (65% assumed effectiveness)

### Scenario 4 — Third-Party Vendor Failure
Security failure at a critical vendor exposes bank data or disrupts 
services. Bank bears liability even for externally-originated breaches. 
OSFI B-10 governs vendor risk management.

- **Loss range:** $400K – $9M | **Frequency:** 0.3–1.5x/year
- **Regulatory ref:** OSFI B-10 — Third-Party Risk Management
- **ALE (seeded run):** $2.70M | **90th percentile:** $7.63M | **ROSI:** 711% at $200K/yr (60% assumed effectiveness)

### Scenario 5 — Cloud Misconfiguration
Misconfigured cloud storage or IAM policies expose sensitive data 
publicly. Most frequent scenario due to rapid cloud adoption and 
configuration complexity.

- **Loss range:** $150K – $6M | **Frequency:** 1.0–4.0x/year
- **Regulatory ref:** OSFI B-13 — Technology Operations and Resilience (cloud and technology risk), with B-10 third-party expectations
- **ALE (seeded run):** $4.46M | **90th percentile:** $10.24M | **ROSI:** 1,884% at $180K/yr (80% assumed effectiveness)

---

### Portfolio Totals (seeded run, 100,000 simulations per scenario)

| Metric | Value |
|--------|-------|
| Combined portfolio ALE | **$19.58M** |
| Combined residual ALE after controls | $5.53M |
| Total annual control investment | $1.51M |
| Portfolio risk reduction | $14.05M/yr (72% of ALE) |
| Portfolio ROSI | 830% |

Every figure above is produced by `run_scenarios.py` and read back from the
database — none of them are typed in by hand.

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

3. **Control effectiveness is an assumption** — the 0.60–0.80 values 
   driving residual ALE and ROSI are judgements, not measurements. They 
   assume the listed controls are fully implemented and operating. A real 
   programme would derive them from control testing results, and a lower 
   effectiveness assumption reduces ROSI proportionately.

4. **Static parameters** — the threat landscape evolves. Parameters 
   should be reviewed annually or after significant incidents.

5. **Frequency midpoint** — lambda is the midpoint of the freq_low/freq_high 
   range. The range is treated as a plausible band for the annual event rate, 
   not as distribution percentiles.

---

## 7. Regulatory Context

This assessment is designed with Canadian federally regulated financial 
institutions in mind. Key regulatory obligations addressed:

| Guideline / advisory | Requirement addressed | Key date |
|----------------------|-----------------------|----------|
| OSFI B-13 — Technology and Cyber Risk Management | Technology and cyber risk governance, operations and resilience | Effective January 1, 2024 |
| OSFI B-10 — Third-Party Risk Management | Third-party risk assessment and ongoing monitoring | Revised 2023, effective May 1, 2024 |
| OSFI E-21 — Operational Risk and Resilience Management | Operational resilience, recovery planning, scenario testing | Full adherence expected September 1, 2026; scenario testing of all critical operations expected September 1, 2027 |
| OSFI Technology and Cyber Security Incident Reporting advisory | Reporting a reportable incident to OSFI within 24 hours | In effect |
| PIPEDA | Customer data breach notification obligations | In effect |

---

## 8. How to Use This Report

**For risk and GRC teams:** Use ALE figures to populate the risk 
register. Use 90th percentile figures for insurance coverage decisions.

**For the CISO:** Use the portfolio ALE and P(>$1M) metrics for 
board reporting. Frame control investments against ALE reduction.

**For executive and board audiences:** Focus on ALE and the ROSI figures.
"Ransomware carries a $5.42M expected annual loss. A $500K/year control
programme, assumed 75% effective, leaves $1.35M of residual expected loss —
a 713% return on that investment" is the business case. State the
effectiveness assumption out loud every time; it is the number a sceptical
audit committee will push back on.