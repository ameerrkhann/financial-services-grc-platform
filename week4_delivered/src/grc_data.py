# grc_data.py
# Corrected reference data for the Financial Services Cyber Risk Intelligence Platform.
#
# Framework references verified against:
#   - NIST CSF 2.0 Core (NIST CSWP 29, February 2024)
#   - ISO/IEC 27001:2022 Annex A (93 controls, 4 themes)
#   - SOC 2 Trust Services Criteria (2017, with 2022 points of focus)
#   - OSFI B-10 (effective May 1, 2024), B-13 (effective January 1, 2024),
#     E-21 (full adherence September 1, 2026; scenario testing September 1, 2027)
#
# NOTE ON CSF 2.0: the categories PR.AC, RS.RP and RC.IM used in CSF 1.1 do not
# exist in CSF 2.0. They map to PR.AA, RS.MA and ID.IM respectively.

ORG_NAME = "First National Bank (Fictional)"
ASSESSOR = "Ameer Khan"
SEED = 42
N_SIMULATIONS = 100_000

# ──────────────────────────────────────────────────────────────────────
# NIST CSF 2.0 — six functions, current vs target maturity
# ──────────────────────────────────────────────────────────────────────

CSF_FUNCTIONS = {
    "Govern": {
        "code": "GV",
        "order": 1,
        "description": "Establishes cybersecurity strategy, expectations and policy.",
        "score": 2,
        "target": 4,
        "rationale": "No board-approved cybersecurity policy. Risk appetite undocumented.",
    },
    "Identify": {
        "code": "ID",
        "order": 2,
        "description": "Understands assets, risks and the business environment.",
        "score": 2,
        "target": 4,
        "rationale": "Asset inventory incomplete. Risk assessments are informal and ad hoc.",
    },
    "Protect": {
        "code": "PR",
        "order": 3,
        "description": "Implements safeguards to prevent or limit cyber events.",
        "score": 3,
        "target": 4,
        "rationale": "MFA and encryption deployed. Access reviews not yet measured.",
    },
    "Detect": {
        "code": "DE",
        "order": 4,
        "description": "Identifies the occurrence of cybersecurity events.",
        "score": 2,
        "target": 4,
        "rationale": "Logging in place but no active monitoring or alerting thresholds.",
    },
    "Respond": {
        "code": "RS",
        "order": 5,
        "description": "Takes action regarding a detected cybersecurity incident.",
        "score": 1,
        "target": 4,
        "rationale": "No documented incident response plan. OSFI 24-hour reporting path undefined.",
    },
    "Recover": {
        "code": "RC",
        "order": 6,
        "description": "Restores capabilities and maintains resilience after an incident.",
        "score": 3,
        "target": 4,
        "rationale": "Backups tested annually. Recovery time objectives defined for tier-1 systems only.",
    },
}

# Gaps generated for any function scoring below 3
CONTROL_GAPS = {
    "Govern": {
        "gap": "No board-approved cybersecurity policy or documented risk appetite statement.",
        "priority": "Critical",
        "risk_rank": 1,
        "csf_ref": "GV.PO-01",
        "iso_ref": "A.5.1",
        "soc2_ref": "CC1.1",
        "osfi_ref": "OSFI B-13 — Governance and Risk Management",
        "effort": "Low",
        "effort_weeks": 4,
        "impact": "Without governance, no other function is sustained. B-13 requires documented "
                  "cyber risk governance with board oversight.",
        "quick_win": "Draft a one-page cybersecurity policy and obtain executive sign-off this month.",
        "remediation": "Draft and approve a cybersecurity policy. Document a risk appetite statement. "
                       "Establish quarterly cyber risk reporting to the board.",
    },
    "Identify": {
        "gap": "Incomplete asset inventory; no formal risk assessment process.",
        "priority": "Critical",
        "risk_rank": 2,
        "csf_ref": "ID.AM-01",
        "iso_ref": "A.5.9",
        "soc2_ref": "CC3.2",
        "osfi_ref": "OSFI B-13 — Technology Operations and Resilience",
        "effort": "Medium",
        "effort_weeks": 8,
        "impact": "You cannot protect what you do not know you have. Unknown assets remain the "
                  "most common initial access point in reported breaches.",
        "quick_win": "Run an authenticated network discovery scan to produce a baseline asset list.",
        "remediation": "Deploy asset discovery tooling. Conduct a formal risk assessment and record "
                       "findings in a risk register with named owners.",
    },
    "Detect": {
        "gap": "Logging exists but is not actively monitored; no alerting thresholds defined.",
        "priority": "High",
        "risk_rank": 4,
        "csf_ref": "DE.CM-01",
        "iso_ref": "A.8.15 / A.8.16",
        "soc2_ref": "CC7.2",
        "osfi_ref": "OSFI B-13 — Cyber Security",
        "effort": "Medium",
        "effort_weeks": 10,
        "impact": "Undetected intrusions persist. Breach cost rises sharply with dwell time, and "
                  "OSFI incident reporting cannot start until an incident is detected.",
        "quick_win": "Enable and review authentication logs weekly while SIEM procurement proceeds.",
        "remediation": "Implement a SIEM platform. Define alerting thresholds and assign named "
                       "ownership for daily event review.",
    },
    "Respond": {
        "gap": "No documented or tested incident response plan.",
        "priority": "High",
        "risk_rank": 3,
        "csf_ref": "RS.MA-01",
        "iso_ref": "A.5.24 / A.5.26",
        "soc2_ref": "CC7.4",
        "osfi_ref": "OSFI Technology and Cyber Security Incident Reporting Advisory (24 hours)",
        "effort": "Low",
        "effort_weeks": 6,
        "impact": "Without a plan, response is improvised. OSFI expects notification of a reportable "
                  "technology or cyber incident within 24 hours of determination.",
        "quick_win": "Name an incident response lead and publish a contact escalation tree this week.",
        "remediation": "Create an incident response plan covering roles, containment and the OSFI "
                       "24-hour reporting path. Run a tabletop exercise within 90 days.",
    },
}

# ──────────────────────────────────────────────────────────────────────
# Cross-framework control mapping
# ──────────────────────────────────────────────────────────────────────

CONTROL_MAPPING = [
    {"function": "Govern", "csf_ref": "GV.PO-01",
     "csf_desc": "Policy for managing cybersecurity risk is established and communicated.",
     "iso_ref": "A.5.1", "iso_desc": "Policies for information security",
     "soc2_ref": "CC1.1", "soc2_desc": "Commitment to integrity and ethical values",
     "osfi_ref": "B-13 Governance and Risk Management",
     "control": "Board-approved cybersecurity policy reviewed annually.",
     "frequency": "Annual"},
    {"function": "Govern", "csf_ref": "GV.RM-01",
     "csf_desc": "Risk management objectives are established and agreed to by stakeholders.",
     "iso_ref": "Clause 6.1", "iso_desc": "Actions to address risks and opportunities",
     "soc2_ref": "CC3.1", "soc2_desc": "Specifies objectives to enable risk identification",
     "osfi_ref": "B-13 Governance and Risk Management",
     "control": "Documented cyber risk appetite statement approved by executive committee.",
     "frequency": "Annual"},
    {"function": "Govern", "csf_ref": "GV.SC-01",
     "csf_desc": "A supply chain risk management programme is established and agreed to.",
     "iso_ref": "A.5.19", "iso_desc": "Information security in supplier relationships",
     "soc2_ref": "CC9.2", "soc2_desc": "Assesses and manages risks from vendors and partners",
     "osfi_ref": "B-10 Third-Party Risk Management",
     "control": "Third-party risk programme with documented tiering methodology.",
     "frequency": "Annual"},
    {"function": "Identify", "csf_ref": "ID.AM-01",
     "csf_desc": "Inventories of hardware managed by the organisation are maintained.",
     "iso_ref": "A.5.9", "iso_desc": "Inventory of information and other associated assets",
     "soc2_ref": "CC3.2", "soc2_desc": "Identifies and analyses risks to objectives",
     "osfi_ref": "B-13 Technology Operations and Resilience",
     "control": "Automated asset discovery feeding a maintained CMDB.",
     "frequency": "Continuous"},
    {"function": "Identify", "csf_ref": "ID.RA-01",
     "csf_desc": "Vulnerabilities in assets are identified, validated and recorded.",
     "iso_ref": "A.8.8", "iso_desc": "Management of technical vulnerabilities",
     "soc2_ref": "CC7.1", "soc2_desc": "Detects and monitors configuration changes",
     "osfi_ref": "B-13 Cyber Security",
     "control": "Quarterly authenticated vulnerability scans with tracked remediation SLAs.",
     "frequency": "Quarterly"},
    {"function": "Identify", "csf_ref": "ID.IM-04",
     "csf_desc": "Incident response and other cybersecurity plans are established and improved.",
     "iso_ref": "A.5.27", "iso_desc": "Learning from information security incidents",
     "soc2_ref": "CC4.2", "soc2_desc": "Evaluates and communicates deficiencies",
     "osfi_ref": "E-21 Operational Resilience",
     "control": "Post-incident review completed within 14 days; plans updated accordingly.",
     "frequency": "Per incident"},
    {"function": "Protect", "csf_ref": "PR.AA-01",
     "csf_desc": "Identities and credentials for authorised users are managed.",
     "iso_ref": "A.5.15", "iso_desc": "Access control",
     "soc2_ref": "CC6.1", "soc2_desc": "Restricts logical access to information assets",
     "osfi_ref": "B-13 Cyber Security",
     "control": "Centralised identity management with quarterly access recertification.",
     "frequency": "Quarterly"},
    {"function": "Protect", "csf_ref": "PR.AA-03",
     "csf_desc": "Users, services and hardware are authenticated.",
     "iso_ref": "A.8.5", "iso_desc": "Secure authentication",
     "soc2_ref": "CC6.1", "soc2_desc": "Restricts logical access to information assets",
     "osfi_ref": "B-13 Cyber Security",
     "control": "Multi-factor authentication enforced on all internet-facing and privileged access.",
     "frequency": "Continuous"},
    {"function": "Protect", "csf_ref": "PR.DS-01",
     "csf_desc": "The confidentiality, integrity and availability of data-at-rest are protected.",
     "iso_ref": "A.8.24", "iso_desc": "Use of cryptography",
     "soc2_ref": "CC6.7", "soc2_desc": "Restricts transmission and removal of information",
     "osfi_ref": "B-13 Cyber Security",
     "control": "AES-256 encryption on all datastores holding customer information.",
     "frequency": "Continuous"},
    {"function": "Protect", "csf_ref": "PR.AT-01",
     "csf_desc": "Personnel are provided with awareness and training.",
     "iso_ref": "A.6.3", "iso_desc": "Information security awareness, education and training",
     "soc2_ref": "CC1.4", "soc2_desc": "Attracts, develops and retains competent individuals",
     "osfi_ref": "B-13 Governance and Risk Management",
     "control": "Mandatory annual security awareness training with phishing simulations.",
     "frequency": "Annual"},
    {"function": "Detect", "csf_ref": "DE.CM-01",
     "csf_desc": "Networks and network services are monitored to find potentially adverse events.",
     "iso_ref": "A.8.16", "iso_desc": "Monitoring activities",
     "soc2_ref": "CC7.2", "soc2_desc": "Monitors system components for anomalies",
     "osfi_ref": "B-13 Cyber Security",
     "control": "SIEM ingesting network and authentication logs with 24/7 alerting.",
     "frequency": "Continuous"},
    {"function": "Detect", "csf_ref": "DE.AE-02",
     "csf_desc": "Potentially adverse events are analysed to better understand associated activities.",
     "iso_ref": "A.8.15", "iso_desc": "Logging",
     "soc2_ref": "CC7.3", "soc2_desc": "Evaluates security events to determine incidents",
     "osfi_ref": "B-13 Cyber Security",
     "control": "Security events triaged against documented severity criteria within 4 hours.",
     "frequency": "Continuous"},
    {"function": "Respond", "csf_ref": "RS.MA-01",
     "csf_desc": "The incident response plan is executed once an incident is declared.",
     "iso_ref": "A.5.26", "iso_desc": "Response to information security incidents",
     "soc2_ref": "CC7.4", "soc2_desc": "Responds to identified security incidents",
     "osfi_ref": "E-21 Operational Resilience; B-13 Cyber Security",
     "control": "Incident response plan tested annually via tabletop exercise.",
     "frequency": "Annual"},
    {"function": "Respond", "csf_ref": "RS.CO-02",
     "csf_desc": "Internal and external stakeholders are notified of incidents.",
     "iso_ref": "A.6.8", "iso_desc": "Information security event reporting",
     "soc2_ref": "CC2.2", "soc2_desc": "Communicates internally on responsibilities and issues",
     "osfi_ref": "OSFI Technology and Cyber Security Incident Reporting Advisory",
     "control": "Reportable incidents notified to OSFI within 24 hours of determination.",
     "frequency": "Per incident"},
    {"function": "Recover", "csf_ref": "RC.RP-01",
     "csf_desc": "The recovery portion of the incident response plan is executed.",
     "iso_ref": "A.5.30", "iso_desc": "ICT readiness for business continuity",
     "soc2_ref": "A1.2", "soc2_desc": "Environmental protections and data back-up processes",
     "osfi_ref": "E-21 Operational Resilience",
     "control": "Recovery procedures executed against defined tolerances for disruption.",
     "frequency": "Per incident"},
    {"function": "Recover", "csf_ref": "RC.RP-05",
     "csf_desc": "The integrity of restored assets is verified before returning to service.",
     "iso_ref": "A.8.13", "iso_desc": "Information backup",
     "soc2_ref": "A1.2", "soc2_desc": "Environmental protections and data back-up processes",
     "osfi_ref": "E-21 Operational Resilience",
     "control": "Quarterly restore testing with documented integrity verification.",
     "frequency": "Quarterly"},
]

# ──────────────────────────────────────────────────────────────────────
# FAIR threat scenarios
#
# Loss ranges are interpreted as the 5th and 95th percentile of a
# log-normal single-event loss distribution. Annual event count is
# Poisson with lambda = mean of the frequency range.
#
# control_effectiveness is an ASSUMPTION representing the proportion of
# expected loss avoided once the recommended controls are fully in place.
# ──────────────────────────────────────────────────────────────────────

SCENARIOS = {
    "data_breach": {
        "id": 1,
        "name": "Data Breach — Customer PII",
        "short": "Data Breach",
        "description": (
            "Unauthorised exfiltration of customer personally identifiable information, "
            "including names, social insurance numbers, account numbers and transaction "
            "history. Initiated through phishing, credential stuffing or misuse of "
            "privileged access."
        ),
        "loss_low": 500_000, "loss_high": 8_000_000,
        "freq_low": 0.5, "freq_high": 3.0,
        "control_cost": 350_000, "control_effectiveness": 0.70,
        "osfi_ref": "OSFI Technology and Cyber Security Incident Reporting Advisory (24-hour notification)",
        "csf_ref": "PR.DS-01, DE.CM-01, RS.MA-01",
        "controls": [
            "Data loss prevention tooling across email and endpoint",
            "AES-256 encryption at rest and TLS 1.2+ in transit for all PII",
            "Privileged access management with session recording",
            "Documented OSFI 24-hour breach notification procedure",
        ],
    },
    "ransomware": {
        "id": 2,
        "name": "Ransomware Attack",
        "short": "Ransomware",
        "description": (
            "Malware encrypts critical banking systems — core banking platform, payment "
            "processing and the customer portal. Operations halt, recovery costs accrue "
            "and regulatory reporting obligations are triggered."
        ),
        "loss_low": 800_000, "loss_high": 12_000_000,
        "freq_low": 0.5, "freq_high": 2.0,
        "control_cost": 500_000, "control_effectiveness": 0.75,
        "osfi_ref": "OSFI E-21 Operational Resilience; B-13 Technology Operations and Resilience",
        "csf_ref": "PR.AA-03, DE.CM-01, RC.RP-01",
        "controls": [
            "Immutable offline backups with quarterly restore testing",
            "Network segmentation limiting lateral movement",
            "Endpoint detection and response deployed fleet-wide",
            "Ransomware-specific incident response playbook",
        ],
    },
    "insider_threat": {
        "id": 3,
        "name": "Insider Threat — Privileged Access Abuse",
        "short": "Insider Threat",
        "description": (
            "A malicious or negligent employee or contractor misuses privileged access to "
            "exfiltrate customer data, manipulate transactions or disrupt systems. Harder "
            "to detect because the actor holds legitimate credentials."
        ),
        "loss_low": 200_000, "loss_high": 5_000_000,
        "freq_low": 0.5, "freq_high": 2.0,
        "control_cost": 280_000, "control_effectiveness": 0.60,
        "osfi_ref": "OSFI B-13 Cyber Security (access management)",
        "csf_ref": "PR.AA-01, DE.AE-02, RS.MA-01",
        "controls": [
            "User and entity behaviour analytics on privileged accounts",
            "Least-privilege access with quarterly recertification",
            "Separation of duties on high-value transactions",
            "Same-day access revocation on offboarding",
        ],
    },
    "vendor_failure": {
        "id": 4,
        "name": "Third-Party Vendor Security Failure",
        "short": "Vendor Failure",
        "description": (
            "A critical vendor — cloud provider, payment processor or software supplier — "
            "suffers a breach that exposes bank data or disrupts service. The bank remains "
            "accountable to its customers and regulator even though the failure was external."
        ),
        "loss_low": 400_000, "loss_high": 9_000_000,
        "freq_low": 0.3, "freq_high": 1.5,
        "control_cost": 200_000, "control_effectiveness": 0.65,
        "osfi_ref": "OSFI B-10 Third-Party Risk Management",
        "csf_ref": "GV.SC-01, ID.RA-01, RS.CO-02",
        "controls": [
            "Risk-tiered vendor security questionnaires before onboarding",
            "Contractual security requirements including 24-hour breach notification",
            "Continuous monitoring with tier-based reassessment cycles",
            "Documented exit strategy for every critical vendor",
        ],
    },
    "cloud_misconfiguration": {
        "id": 5,
        "name": "Cloud Misconfiguration — Data Exposure",
        "short": "Cloud Misconfig",
        "description": (
            "A misconfigured storage bucket, database or API exposes sensitive data "
            "publicly. Driven by overly permissive IAM policies, public storage defaults "
            "or credentials committed to code repositories."
        ),
        "loss_low": 150_000, "loss_high": 6_000_000,
        "freq_low": 1.0, "freq_high": 4.0,
        "control_cost": 180_000, "control_effectiveness": 0.80,
        "osfi_ref": "OSFI B-13 Technology Operations and Resilience (cloud risk)",
        "csf_ref": "PR.DS-01, ID.AM-01, DE.CM-01",
        "controls": [
            "Cloud security posture management with continuous scanning",
            "Infrastructure-as-code security scanning in the CI/CD pipeline",
            "Policy-enforced prohibition on public storage buckets",
            "Automated secret detection across all repositories",
        ],
    },
}

# ──────────────────────────────────────────────────────────────────────
# Vendor risk — questionnaire weights and tiers
# ──────────────────────────────────────────────────────────────────────

RISK_TIERS = {
    "Critical": {"min": 0,  "max": 40,
                 "action": "Do not onboard without a remediation plan. Executive approval required.",
                 "reassess_days": 180},
    "High":     {"min": 41, "max": 60,
                 "action": "Onboard with conditions. Quarterly reassessment required.",
                 "reassess_days": 365},
    "Medium":   {"min": 61, "max": 80,
                 "action": "Standard onboarding. Annual reassessment required.",
                 "reassess_days": 365},
    "Low":      {"min": 81, "max": 100,
                 "action": "Approve for onboarding. Biennial reassessment required.",
                 "reassess_days": 730},
}

# 8 fictional vendors. answers = (yes_count, partial_count, no_count) shape
# is derived from a target score so the spread covers every tier.
DEMO_VENDORS = [
    {"name": "NorthPeak Cloud Services",   "service": "Cloud Provider",      "criticality": "Critical", "target": 88, "days_ago": 120},
    {"name": "MapleLedger Payments",       "service": "Payment Processor",   "criticality": "Critical", "target": 74, "days_ago": 200},
    {"name": "Borealis Analytics",         "service": "Data Analytics / AI", "criticality": "High",     "target": 52, "days_ago": 410},
    {"name": "Rideau Infrastructure Group","service": "IT Infrastructure",   "criticality": "High",     "target": 67, "days_ago": 95},
    {"name": "Cartier Software Labs",      "service": "Software / SaaS",     "criticality": "Medium",   "target": 83, "days_ago": 60},
    {"name": "Lakeshore Data Systems",     "service": "IT Infrastructure",   "criticality": "Medium",   "target": 36, "days_ago": 440},
    {"name": "Acadia Payment Solutions",   "service": "Payment Processor",   "criticality": "High",     "target": 58, "days_ago": 390},
    {"name": "Sable Ridge SaaS",           "service": "Software / SaaS",     "criticality": "Low",      "target": 79, "days_ago": 30},
]

VENDOR_CATEGORIES = [
    "Governance", "Incident Response", "Access Control", "Data Protection",
    "Business Continuity", "Vulnerability Management", "Subcontracting", "Audit Rights",
]
