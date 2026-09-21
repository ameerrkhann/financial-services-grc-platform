# NIST CSF 2.0 — Quick Reference Cheat Sheet

Control IDs below are from the **NIST CSF 2.0 Core (NIST CSWP 29, February
2024)**. Several CSF 1.1 categories no longer exist in 2.0 — the common traps
are listed at the bottom of this page.

## The 6 Functions

| Function | Core Question | Key Activities | Interview Example |
|----------|--------------|----------------|-------------------|
| **Govern** | Who owns security & what are the rules? | Policies, roles, board reporting, risk appetite | "Our CISO reports to the board quarterly" |
| **Identify** | What do we have & what are the risks? | Asset inventory, risk assessment, threat modelling | "We maintain a real-time inventory of 3,000+ assets" |
| **Protect** | How do we prevent attacks? | MFA, encryption, access controls, training, patching | "All customer data encrypted at rest and in transit" |
| **Detect** | How do we notice attacks? | SIEM monitoring, anomaly detection, log analysis | "Automated alerts fire within 5 minutes of anomaly" |
| **Respond** | What do we do during an attack? | Incident response plan, containment, notifications | "OSFI requires reportable incidents to be reported within 24 hours" |
| **Recover** | How do we get back to normal? | Backups, BCP, lessons learned, customer comms | "Tested recovery procedures with defined RTOs" |

## Maturity Scale

| Score | Meaning | Signals |
|-------|---------|---------|
| 1 | Initial | Ad hoc, undocumented, reactive |
| 2 | Developing | Some processes exist, inconsistent |
| 3 | Defined | Documented, consistently followed |
| 4 | Managed | Measured, tracked with metrics |
| 5 | Optimized | Continuously improved using data |

## Key Terms

- **Control** — A specific action that reduces a risk (e.g. MFA)
- **Gap** — The difference between your current maturity and your target
- **Remediation** — The plan to close a gap
- **Risk Appetite** — How much risk an org is willing to accept
- **CISO** — Chief Information Security Officer (owns the security program)
- **SOC** — Security Operations Centre (the team watching for threats 24/7)
- **SIEM** — Software that collects and analyzes security logs
- **RTO** — Recovery Time Objective (how fast you must recover)

## Categories per Function (CSF 2.0)

| Function | Categories |
|----------|-----------|
| Govern (GV) | GV.OC Organizational Context · GV.RM Risk Management Strategy · GV.RR Roles, Responsibilities and Authorities · GV.PO Policy · GV.OV Oversight · GV.SC Cybersecurity Supply Chain Risk Management |
| Identify (ID) | ID.AM Asset Management · ID.RA Risk Assessment · ID.IM Improvement |
| Protect (PR) | PR.AA Identity Management, Authentication and Access Control · PR.AT Awareness and Training · PR.DS Data Security · PR.PS Platform Security · PR.IR Technology Infrastructure Resilience |
| Detect (DE) | DE.CM Continuous Monitoring · DE.AE Adverse Event Analysis |
| Respond (RS) | RS.MA Incident Management · RS.AN Incident Analysis · RS.CO Incident Response Reporting and Communication · RS.MI Incident Mitigation |
| Recover (RC) | RC.RP Incident Recovery Plan Execution · RC.CO Incident Recovery Communication |

## CSF 1.1 IDs That No Longer Exist in 2.0

These are the ones most often carried over by mistake — this project used four
of them before they were corrected:

| CSF 1.1 ID | What replaced it in 2.0 |
|------------|-------------------------|
| `PR.AC-01` | `PR.AA-01` — identities and credentials. The whole `PR.AC` category became `PR.AA` |
| `RS.RP-01` | `RS.MA-01` — incident response plan executed. `RS.RP` was folded into `RS.MA` |
| `RC.IM-01` | `ID.IM-04` — plans maintained and improved. Improvement moved from Recover to **Identify** |
| `GV.OC-01` used for policy | `GV.PO-01` — cybersecurity policy. `GV.OC-01` is the organisational *mission* |
