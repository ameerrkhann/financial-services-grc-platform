# OSFI B-10 Compliance Mapping
## Vendor Risk Assessor — Financial Services GRC Platform

**Author:** Ameer Mohammad Khan  
**Tool:** Vendor Risk Assessor (Module 3)  
**Regulation:** OSFI B-10 — Third-Party Risk Management  
**Date:** March 2026  

---

## 1. Purpose of This Document

This document maps each major requirement of OSFI Guideline B-10 
(Third-Party Risk Management) to the specific features of the Vendor 
Risk Assessor built in this portfolio project.

OSFI B-10 applies to all federally regulated financial institutions 
(FRFIs) in Canada — including banks, insurance companies, and trust 
companies. It governs how these institutions identify, assess, monitor, 
and manage the risks introduced by external vendors and service providers.

---

## 2. OSFI B-10 Requirement Mapping

### Requirement 1 — Risk Governance Framework
**What B-10 requires:**  
FRFIs must establish a governance framework for third-party risk that 
includes board oversight, clear accountability, and written policies 
for vendor risk management.

**How this tool addresses it:**  
- Every assessment is recorded with an assessor name and date, 
  creating accountability for who conducted the review
- The risk tier output (Critical/High/Medium/Low) gives the board 
  a clear, consistent classification of the vendor portfolio
- The assessment history table provides a board-ready view of the 
  organisation's overall third-party risk posture

**B-10 Section:** s.3 — Governance

---

### Requirement 2 — Risk-Based Due Diligence
**What B-10 requires:**  
Before onboarding a vendor, FRFIs must conduct due diligence 
proportionate to the risk the vendor represents. Higher-risk vendors 
require more rigorous assessment.

**How this tool addresses it:**  
- Universal questions apply to every vendor regardless of type
- Service-specific questions are added based on vendor category 
  (Cloud Provider, Payment Processor, Software/SaaS, etc.) — 
  more targeted questions for higher-complexity service types
- Business Criticality field (Low/Medium/High/Critical) captures 
  the operational dependency on the vendor
- Weighted scoring ensures high-importance controls (weight 3) 
  have greater influence on the final tier than lower-importance ones

**B-10 Section:** s.4 — Due Diligence

---

### Requirement 3 — Vendor Risk Tiering
**What B-10 requires:**  
Not all vendors carry equal risk. FRFIs must classify vendors by 
risk level and apply controls proportionate to that classification.

**How this tool addresses it:**  
- Every completed assessment automatically assigns a risk tier:
  - **Critical (0–40):** Do not onboard without remediation plan
  - **High (41–60):** Onboard with conditions and quarterly review
  - **Medium (61–80):** Standard onboarding with annual review
  - **Low (81–100):** Approve with biennial reassessment
- Tiering is based on objective scoring, not subjective judgment
- The vendor portfolio dashboard shows tier distribution across 
  all assessed vendors at a glance

**B-10 Section:** s.4 — Risk Classification

---

### Requirement 4 — Contractual Security Requirements
**What B-10 requires:**  
Vendor contracts must include specific security obligations — breach 
notification timelines, audit rights, data handling requirements, 
and sub-contractor restrictions.

**How this tool addresses it:**  
The questionnaire directly assesses whether these contractual 
requirements are in place:
- **U03** — 24-hour breach notification clause
- **U13** — Sub-contractor (fourth-party) security requirements
- **U14** — Right-to-audit clause in vendor contract
- **U07** — Data encryption requirements (at rest and in transit)
- **U08** — Data retention and secure deletion policy

Gaps in these areas are flagged as Critical or High severity in 
the gap report, signalling that the contract must be renegotiated.

**B-10 Section:** s.5 — Contractual Protections

---

### Requirement 5 — Ongoing Monitoring
**What B-10 requires:**  
Vendor risk assessment is not a one-time exercise. FRFIs must 
continuously monitor vendor risk and reassess vendors periodically 
based on their risk tier.

**How this tool addresses it:**  
- Every assessment is saved to the SQLite database with a timestamp, 
  creating a full historical record of vendor assessments over time
- The `get_overdue_vendors()` database function flags vendors whose 
  last assessment exceeds the B-10 timeline:
  - Critical/High/Medium vendors: reassess within 365 days
  - Low vendors: reassess within 730 days
- Multiple assessments for the same vendor build a trend — 
  scores improving or declining over time is visible in the history

**B-10 Section:** s.6 — Ongoing Monitoring

---

### Requirement 6 — Fourth-Party Risk
**What B-10 requires:**  
FRFIs must understand and manage the risk introduced by their 
vendors' own sub-contractors — the fourth-party chain.

**How this tool addresses it:**  
- Question **U13** directly addresses fourth-party risk:  
  *"Does the vendor use sub-contractors with access to client data? 
  If yes, are they subject to equivalent security requirements?"*
- This is a high-weight question (weight 2) — a "No" answer 
  results in significant score reduction
- The gap report flags this as a High severity finding requiring 
  contractual remediation

**B-10 Section:** s.6 — Fourth-Party Risk

---

### Requirement 7 — Exit Planning
**What B-10 requires:**  
FRFIs must have documented exit strategies for critical vendor 
relationships — ensuring operations can continue if a vendor 
relationship ends unexpectedly.

**How this tool addresses it:**  
- For Cloud Provider vendors, question **CL03** directly assesses 
  exit planning:  
  *"Does the vendor provide a documented exit strategy enabling 
  the client to migrate data off-platform with minimal disruption?"*
- This is a high-weight question (weight 3) — absence of an exit 
  strategy is flagged as a Critical severity gap
- Exit planning gaps are highlighted in the remediation guidance 
  with specific action steps

**B-10 Section:** s.9 — Exit Planning

---

### Requirement 8 — Audit Trail and Documentation
**What B-10 requires:**  
FRFIs must maintain records demonstrating that third-party risk 
management activities have been conducted and documented.

**How this tool addresses it:**  
The SQLite database stores a complete audit trail including:
- Vendor name, service type, criticality classification
- Assessor name and assessment date
- Final risk score and tier
- Number of gaps identified (total and critical)
- Individual responses to every question
- Notes and additional context from the assessor

This record can be exported and presented to OSFI examiners or 
internal auditors as evidence of B-10 compliance.

**B-10 Section:** s.10 — Record Keeping

---

## 3. Coverage Summary

| B-10 Requirement | Tool Feature | Coverage |
|-----------------|-------------|----------|
| Risk governance framework | Assessor accountability, tier reporting | ✅ Full |
| Risk-based due diligence | Weighted questionnaire, service-specific questions | ✅ Full |
| Vendor risk tiering | Automated Critical/High/Medium/Low assignment | ✅ Full |
| Contractual security requirements | Dedicated contract questions (U03, U13, U14) | ✅ Full |
| Ongoing monitoring | Database audit trail, overdue vendor flagging | ✅ Full |
| Fourth-party risk | Dedicated question U13 | ✅ Full |
| Exit planning | Cloud-specific question CL03 | ✅ Partial |
| Audit trail and documentation | Full SQLite record per assessment | ✅ Full |

---

## 4. Limitations and Future Enhancements

**What this tool does not yet cover:**

1. **Automated vendor monitoring** — B-10 expects continuous 
   monitoring between formal assessments. A production tool would 
   integrate with threat intelligence feeds to flag vendor incidents 
   in real time.

2. **Contract management** — The tool assesses whether contractual 
   protections exist but does not store or manage the contracts 
   themselves.

3. **Concentration risk analysis** — B-10 requires analysis of 
   over-reliance on single vendors. A future enhancement would 
   flag when too many Critical functions rely on one provider.

4. **Automated reassessment reminders** — The overdue vendor 
   database function exists but is not yet surfaced in the UI 
   as automated alerts.

---

## 5. Regulatory Context

This tool is designed specifically for the Canadian financial 
services regulatory environment. The combination of OSFI B-10, 
B-13, and E-21 coverage reflects the real compliance obligations 
of federally regulated financial institutions where I have 
professional experience (Manulife, Scotiabank).

The September 2026 E-21 operational resilience deadline is 
actively driving demand for exactly this kind of structured 
vendor risk tooling at Canadian banks.