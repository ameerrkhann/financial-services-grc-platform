# OSFI Regulatory Mapping
## Financial Services Cyber Risk Intelligence Platform

This document maps each major OSFI requirement to the specific 
feature in this platform that addresses it.

---

## OSFI B-10 — Third-Party Risk Management

| B-10 Requirement | Platform Feature |
|-----------------|-----------------|
| Vendor risk tiering (Critical/High/Medium/Low) | Automated scoring → risk tier assignment in Module 3 |
| Pre-onboarding due diligence | Vendor security questionnaire generator |
| Ongoing monitoring with audit trail | SQLite database storing assessment date, score, tier per vendor |
| Security requirements documentation | Questionnaire covers encryption, access control, incident response, BC/DR |
| Concentration risk awareness | Vendor tier distribution dashboard (Week 4) |
| Board-level risk reporting | Executive KPI summary in Power BI (Week 4) |

---

## OSFI B-13 — Technology and Cyber Risk Management

| B-13 Requirement | Platform Feature |
|-----------------|-----------------|
| Board ownership of cyber risk | Loss Exceedance Curves designed for board-level consumption |
| Written risk appetite | NIST CSF Govern function scoring + gap analysis |
| Continuous risk assessment | FAIR engine produces quantified, repeatable risk assessments |
| Critical systems identification | NIST CSF Identify function scoring |
| Control validation and testing | NIST CSF maturity scoring tests existence AND effectiveness |
| 24-hour incident notification | Referenced in Respond function gap analysis and IRP remediation |
| Third-party risk management | Module 3 vendor risk assessor |
| Cloud risk management | Cloud misconfiguration FAIR scenario |
| Continuous improvement | Remediation roadmap with 90-day action plan |

---

## OSFI E-21 — Operational Resilience

| E-21 Requirement | Platform Feature |
|-----------------|-----------------|
| Critical operations identification | NIST CSF Identify function — asset and system inventory |
| Impact tolerance definition | NIST CSF Recover function — RTO documentation gap analysis |
| Resilience testing | NIST CSF Recover maturity scoring — tests whether BCP is validated |
| Severe scenario testing | FAIR scenarios include ransomware, vendor failure, cloud outage |
| Post-incident lessons applied | NIST CSF Recover — lessons learned remediation action |

---

## Compliance Deadline Reference

| Regulation | Status | Key Date |
|-----------|--------|----------|
| OSFI B-13 | In effect | January 2024 |
| OSFI B-10 | In effect | Updated 2023 |
| OSFI E-21 | In effect — full compliance required | September 1, 2026 |

---

## Interview Talking Points

- "B-10 requires vendor risk tiering — my tool automates this with a 
  scored questionnaire that assigns Critical/High/Medium/Low tiers"
  
- "B-13 requires the 24-hour incident notification — I built this into 
  the Respond function remediation guidance in Module 1"
  
- "E-21's September 2026 deadline is actively creating hiring demand 
  at Canadian banks right now — I built my project around the 
  operational resilience requirements it specifies"