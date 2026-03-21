# Cross-Framework Control Mapping
## NIST CSF 2.0 → ISO 27001 → SOC 2

This document maps each NIST CSF 2.0 control to its equivalent
ISO 27001 Annex A clause and SOC 2 Trust Services Criteria.
One control — three frameworks. No duplicate work.

---


## Govern

| NIST CSF | ISO 27001 | SOC 2 | Control Example |
|----------|-----------|-------|-----------------|
| GV.OC-01 — Organisational cybersecurity policy is established. | A.5.1 — Policies for information security. | CC1.1 — COSO Principle 1: Demonstrates commitment to integrity and ethics. | Written cybersecurity policy approved by the board annually. |
| GV.RM-01 — Risk management objectives are established and agreed to. | A.5.8 — Information security in project management. | CC3.1 — Specifies suitable objectives as a precondition to risk identification. | Documented risk appetite statement reviewed by executive leadership. |

## Identify

| NIST CSF | ISO 27001 | SOC 2 | Control Example |
|----------|-----------|-------|-----------------|
| ID.AM-01 — Assets (hardware/software) are inventoried. | A.8.1 — Inventory of assets. | CC6.1 — Logical access security software, infrastructure and architectures. | Real-time asset inventory updated automatically via discovery tools. |
| ID.RA-01 — Vulnerabilities in assets are identified and documented. | A.8.8 — Management of technical vulnerabilities. | CC7.1 — Detection and monitoring procedures to identify changes to configurations. | Quarterly vulnerability scans with findings tracked in a risk register. |

## Protect

| NIST CSF | ISO 27001 | SOC 2 | Control Example |
|----------|-----------|-------|-----------------|
| PR.AC-01 — Identities and credentials are managed for authorised users. | A.9.1 — Access control policy. | CC6.1 — Restricts logical access to information assets. | MFA enforced on all systems. Access reviewed quarterly. |
| PR.DS-01 — Data-at-rest is protected. | A.8.24 — Use of cryptography. | CC6.7 — Restricts the transmission, movement, and removal of information. | AES-256 encryption applied to all databases containing customer data. |
| PR.AT-01 — Personnel are provided awareness and training. | A.6.3 — Information security awareness, education and training. | CC1.4 — Demonstrates commitment to attract, develop and retain competent people. | Annual security awareness training mandatory for all staff. |

## Detect

| NIST CSF | ISO 27001 | SOC 2 | Control Example |
|----------|-----------|-------|-----------------|
| DE.CM-01 — Networks and network services are monitored. | A.12.4 — Logging and monitoring. | CC7.2 — Monitors system components for anomalies that indicate malicious acts. | SIEM platform ingesting all network and authentication logs 24/7. |
| DE.AE-02 — Potentially adverse events are analysed. | A.12.4 — Logging and monitoring. | CC7.3 — Evaluates security events to determine if they are security incidents. | Security events triaged within 4 hours by the SOC team. |

## Respond

| NIST CSF | ISO 27001 | SOC 2 | Control Example |
|----------|-----------|-------|-----------------|
| RS.RP-01 — Incident response plan is established and communicated. | A.16.1 — Management of information security incidents. | CC7.3 — Responds to identified security incidents by executing a defined plan. | IRP tested via tabletop exercise annually. OSFI 24-hr notification included. |
| RS.CO-02 — Incidents are reported to appropriate authorities. | A.16.1 — Reporting information security events. | CC2.2 — Communicates internally about objectives, responsibilities and issues. | OSFI notified within 24 hours of a significant cyber incident. |

## Recover

| NIST CSF | ISO 27001 | SOC 2 | Control Example |
|----------|-----------|-------|-----------------|
| RC.RP-01 — Recovery plan is executed during or after a cybersecurity incident. | A.17.1 — Information security continuity. | A1.2 — Environmental protections, software, data back-up processes in place. | Tested BCP with defined RTOs. Backups restored successfully each quarter. |
| RC.IM-01 — Recovery plans incorporate lessons learned. | A.16.1 — Post-incident reviews conducted. | CC4.2 — Evaluates and communicates deficiencies in a timely manner. | Post-incident report completed within 2 weeks. IRP updated accordingly. |

---
*Total controls mapped: 13*