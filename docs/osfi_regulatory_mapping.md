# OSFI Regulatory Mapping
## Financial Services Cyber Risk Intelligence Platform

This document maps each major OSFI requirement to the specific 
feature in this platform that addresses it.

---

## OSFI B-10 — Third-Party Risk Management

Final revised guideline issued 2023, effective **May 1, 2024**.

| B-10 Requirement | Platform Feature |
|-----------------|-----------------|
| Vendor risk tiering (Critical/High/Medium/Low) | Automated scoring → risk tier assignment in Module 3 |
| Pre-onboarding due diligence | Vendor security questionnaire generator |
| Ongoing monitoring with audit trail | SQLite database storing assessment date, score, tier per vendor |
| Security requirements documentation | Questionnaire covers encryption, access control, incident response, BC/DR |
| Concentration risk awareness | Vendor tier distribution dashboard |
| Board-level risk reporting | Executive KPI summary in Power BI and the executive PDF |

---

## OSFI B-13 — Technology and Cyber Risk Management

Effective **January 1, 2024**. Organised into three domains: Governance and
Risk Management; Technology Operations and Resilience; Cyber Security.

| B-13 Requirement | Platform Feature |
|-----------------|-----------------|
| Board ownership of cyber risk | Loss Exceedance Curves designed for board-level consumption |
| Written risk appetite | NIST CSF Govern function scoring + gap analysis |
| Continuous risk assessment | FAIR engine produces quantified, repeatable risk assessments |
| Critical systems identification | NIST CSF Identify function scoring |
| Control validation and testing | NIST CSF maturity scoring tests existence AND effectiveness |
| Incident reporting readiness | Respond function gap analysis and IRP remediation. The 24-hour clock itself comes from OSFI's *Technology and Cyber Security Incident Reporting* advisory, not from B-13 |
| Third-party risk management | Module 3 vendor risk assessor |
| Cloud risk management | Cloud misconfiguration FAIR scenario |
| Continuous improvement | Remediation roadmap with 90-day action plan |

---

## OSFI E-21 — Operational Risk and Resilience Management

Full adherence was expected by **September 1, 2026**. Scenario testing across
all critical operations is expected by **September 1, 2027**.

| E-21 Requirement | Platform Feature |
|-----------------|-----------------|
| Critical operations identification | NIST CSF Identify function — asset and system inventory |
| Impact tolerance definition | NIST CSF Recover function — RTO documentation gap analysis |
| Resilience testing | NIST CSF Recover maturity scoring — tests whether BCP is validated |
| Severe scenario testing | FAIR scenarios include ransomware, vendor failure, cloud outage |
| Post-incident lessons applied | NIST CSF Recover — lessons learned remediation action |

---

## Compliance Date Reference

| Guideline / advisory | Status | Key date |
|----------------------|--------|----------|
| OSFI B-13 — Technology and Cyber Risk Management | In effect | Effective January 1, 2024 |
| OSFI B-10 — Third-Party Risk Management | In effect | Revised 2023, effective May 1, 2024 |
| OSFI E-21 — Operational Risk and Resilience Management | In effect | Full adherence expected September 1, 2026; scenario testing of all critical operations expected September 1, 2027 |
| Technology and Cyber Security Incident Reporting advisory | In effect | Reportable incidents reported to OSFI within 24 hours |

---

## Interview Talking Points

- "B-10 requires vendor risk tiering — my tool automates this with a 
  scored questionnaire that assigns Critical/High/Medium/Low tiers"
  
- "The 24-hour incident report goes to OSFI's Technology Risk Division and
  the lead supervisor, and it comes from the Technology and Cyber Security
  Incident Reporting advisory rather than B-13 itself — a distinction worth
  getting right. I built that step into the Respond function remediation
  guidance in Module 1"

- "E-21 full adherence was due September 1, 2026, and scenario testing across
  all critical operations is expected by September 1, 2027 — Canadian FRFIs are
  actively building out that testing capability now. I built my project around
  the operational resilience requirements it specifies"