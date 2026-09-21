# Cross-Framework Control Mapping
## NIST CSF 2.0 → ISO 27001 → SOC 2

This document maps each NIST CSF 2.0 control to its equivalent
ISO/IEC 27001:2022 Annex A control, SOC 2 Trust Services Criteria,
and the OSFI guideline it supports. One control — four frameworks.
No duplicate work.

CSF IDs are from the NIST CSF 2.0 Core (NIST CSWP 29, February 2024).
ISO IDs are from ISO/IEC 27001:2022 Annex A — not the 2013 numbering.

---


## Govern

| NIST CSF 2.0 | ISO/IEC 27001:2022 | SOC 2 | OSFI | Control Example |
|--------------|--------------------|-------|------|-----------------|
| GV.PO-01 — Policy for managing cybersecurity risks is established, communicated and enforced. | A.5.1 — Policies for information security. | CC1.1 — COSO Principle 1: Demonstrates commitment to integrity and ethics. | B-13 — Governance and Risk Management | Written cybersecurity policy approved by the board annually. |
| GV.RM-01 — Risk management objectives are established and agreed to by stakeholders. | Clause 6.1 — Actions to address information security risks and opportunities. | CC3.1 — Specifies suitable objectives as a precondition to risk identification. | B-13 — Governance and Risk Management | Documented risk appetite statement reviewed by executive leadership. |
| GV.SC-04 — Suppliers are known and prioritised by criticality. | A.5.19 — Information security in supplier relationships. | CC9.2 — Assesses and manages risks associated with vendors and business partners. | B-10 — Third-Party Risk Management | Vendor register with a risk tier per vendor, refreshed each assessment. |
| GV.SC-07 — Risks posed by suppliers and third parties are assessed and monitored across the relationship. | A.5.22 — Monitoring, review and change management of supplier services. | CC9.2 — Assesses and manages risks associated with vendors and business partners. | B-10 — Third-Party Risk Management | Vendor reassessed on its tier's cycle; overdue vendors flagged automatically. |

## Identify

| NIST CSF 2.0 | ISO/IEC 27001:2022 | SOC 2 | OSFI | Control Example |
|--------------|--------------------|-------|------|-----------------|
| ID.AM-01 — Inventories of hardware managed by the organisation are maintained. | A.5.9 — Inventory of information and other associated assets. | CC6.1 — Logical access security software, infrastructure and architectures. | B-13 — Technology Operations and Resilience | Real-time asset inventory updated automatically via discovery tools. |
| ID.RA-01 — Vulnerabilities in assets are identified, validated and recorded. | A.8.8 — Management of technical vulnerabilities. | CC7.1 — Detection and monitoring procedures to identify changes to configurations. | B-13 — Cyber Security | Quarterly vulnerability scans with findings tracked in a risk register. |
| ID.IM-04 — Incident response and other cybersecurity plans are established, maintained and improved. | A.5.27 — Learning from information security incidents. | CC4.2 — Evaluates and communicates deficiencies in a timely manner. | E-21 — Operational Risk and Resilience Management | Post-incident report completed within 2 weeks. IRP updated accordingly. |

## Protect

| NIST CSF 2.0 | ISO/IEC 27001:2022 | SOC 2 | OSFI | Control Example |
|--------------|--------------------|-------|------|-----------------|
| PR.AA-01 — Identities and credentials for authorised users, services and hardware are managed. | A.5.15, A.8.5 — Access control; secure authentication. | CC6.1 — Restricts logical access to information assets. | B-13 — Cyber Security | MFA enforced on all systems. Joiner/mover/leaver process automated. |
| PR.AA-05 — Access permissions and authorisations are managed, incorporating least privilege and separation of duties. | A.5.18 — Access rights. | CC6.3 — Authorises, modifies or removes access based on roles and responsibilities. | B-13 — Cyber Security | Quarterly access recertification by system owners. Privileged access via PAM. |
| PR.DS-01 — The confidentiality, integrity and availability of data-at-rest are protected. | A.8.24 — Use of cryptography. | CC6.7 — Restricts the transmission, movement, and removal of information. | B-13 — Cyber Security | AES-256 encryption applied to all databases containing customer data. |
| PR.DS-11 — Backups of data are created, protected, maintained and tested. | A.8.13 — Information backup. | A1.2 — Environmental protections, software, data back-up processes in place. | E-21 — Operational Risk and Resilience Management | Immutable offline backups restored successfully each quarter. |
| PR.AT-01 — Personnel are provided awareness and training. | A.6.3 — Information security awareness, education and training. | CC1.4 — Demonstrates commitment to attract, develop and retain competent people. | B-13 — Governance and Risk Management | Annual security awareness training mandatory for all staff. |

## Detect

| NIST CSF 2.0 | ISO/IEC 27001:2022 | SOC 2 | OSFI | Control Example |
|--------------|--------------------|-------|------|-----------------|
| DE.CM-01 — Networks and network services are monitored to find potentially adverse events. | A.8.15, A.8.16 — Logging; monitoring activities. | CC7.2 — Monitors system components for anomalies that indicate malicious acts. | B-13 — Cyber Security | SIEM platform ingesting all network and authentication logs 24/7. |
| DE.AE-02 — Potentially adverse events are analysed to better understand associated activities. | A.8.16 — Monitoring activities. | CC7.3 — Evaluates security events to determine if they are security incidents. | B-13 — Cyber Security | Security events triaged within 4 hours by the SOC team. |

## Respond

| NIST CSF 2.0 | ISO/IEC 27001:2022 | SOC 2 | OSFI | Control Example |
|--------------|--------------------|-------|------|-----------------|
| RS.MA-01 — The incident response plan is executed in coordination with relevant third parties once an incident is declared. | A.5.24, A.5.26 — Incident management planning and preparation; response to incidents. | CC7.4 — Responds to identified security incidents by executing a defined programme. | B-13 — Cyber Security | IRP tested via tabletop exercise annually, with named incident commander. |
| RS.CO-02 — Internal and external stakeholders are notified of incidents. | A.6.8 — Information security event reporting. | CC2.2 — Communicates internally about objectives, responsibilities and issues. | Technology and Cyber Security Incident Reporting advisory — 24-hour reporting | OSFI's Technology Risk Division and lead supervisor notified within 24 hours of a reportable incident. |

## Recover

| NIST CSF 2.0 | ISO/IEC 27001:2022 | SOC 2 | OSFI | Control Example |
|--------------|--------------------|-------|------|-----------------|
| RC.RP-01 — The recovery portion of the incident response plan is executed once initiated. | A.5.29, A.5.30 — Information security during disruption; ICT readiness for business continuity. | A1.2 — Environmental protections, software, data back-up processes in place. | E-21 — Operational Risk and Resilience Management | Tested BCP with defined RTOs for every critical operation. |

---
*Total controls mapped: 17*