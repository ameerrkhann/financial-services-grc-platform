# src/compliance/csf_data.py
# Reference data for NIST CSF 2.0 functions

CSF_FUNCTIONS = {
    "Govern": {
        "code": "GV",
        "description": "Establishes cybersecurity strategy, expectations, and policy.",
        "questions": [
            "Is there a formal cybersecurity policy approved by leadership?",
            "Does the board or executive team receive regular cyber risk updates?",
            "Are cybersecurity roles and responsibilities clearly defined?",
            "Is there a documented risk appetite statement?",
        ],
        "maturity_descriptors": {
            1: "No formal policy. Security decisions are made ad hoc.",
            2: "Some policies exist but are inconsistent or outdated.",
            3: "Documented policies exist and are consistently followed.",
            4: "Policies are reviewed regularly and tracked with metrics.",
            5: "Continuously improved governance with board-level integration.",
        }
    },
    "Identify": {
        "code": "ID",
        "description": "Understands assets, risks, and the business environment.",
        "questions": [
            "Is there a complete and up-to-date inventory of hardware and software assets?",
            "Are data classification policies in place?",
            "Is there a formal risk assessment process?",
            "Are third-party vendor risks documented?",
        ],
        "maturity_descriptors": {
            1: "No asset inventory. Risks are unknown.",
            2: "Partial inventory exists. Risk assessment is informal.",
            3: "Full asset inventory maintained. Formal risk assessments conducted.",
            4: "Assets tracked in real time. Risk assessments tied to business impact.",
            5: "Continuous asset discovery and automated risk scoring.",
        }
    },
    "Protect": {
        "code": "PR",
        "description": "Implements safeguards to prevent or limit cyber events.",
        "questions": [
            "Is multi-factor authentication (MFA) enforced across all systems?",
            "Is sensitive data encrypted at rest and in transit?",
            "Is the principle of least privilege applied to user access?",
            "Is security awareness training conducted regularly?",
        ],
        "maturity_descriptors": {
            1: "Minimal controls. No MFA. Data unencrypted.",
            2: "Some controls exist but inconsistently applied.",
            3: "Core controls (MFA, encryption, access control) fully implemented.",
            4: "Controls are monitored and exceptions tracked.",
            5: "Zero-trust architecture. Automated access reviews.",
        }
    },
    "Detect": {
        "code": "DE",
        "description": "Identifies the occurrence of cybersecurity events.",
        "questions": [
            "Is there a SIEM or log monitoring tool in place?",
            "Are there automated alerts for anomalous activity?",
            "Is there a defined process for reviewing security events?",
            "What is the average time to detect a security incident?",
        ],
        "maturity_descriptors": {
            1: "No monitoring. Incidents discovered by accident.",
            2: "Some logging exists but no active monitoring.",
            3: "SIEM in place with defined alerting thresholds.",
            4: "Mean time to detect is measured and improving.",
            5: "24/7 SOC with automated detection and response.",
        }
    },
    "Respond": {
        "code": "RS",
        "description": "Takes action regarding a detected cybersecurity incident.",
        "questions": [
            "Is there a documented Incident Response Plan (IRP)?",
            "Has the IRP been tested in the last 12 months?",
            "Are regulatory notification requirements understood (e.g. OSFI 24-hr rule)?",
            "Are roles and responsibilities during an incident clearly assigned?",
        ],
        "maturity_descriptors": {
            1: "No incident response plan. Reactive and chaotic.",
            2: "Basic plan exists but has never been tested.",
            3: "Documented IRP tested at least annually.",
            4: "IRP metrics tracked. Lessons learned applied.",
            5: "Regular tabletop exercises. IRP updated after every incident.",
        }
    },
    "Recover": {
        "code": "RC",
        "description": "Maintains resilience and restores capabilities after an incident.",
        "questions": [
            "Are backups tested regularly and stored offsite or in the cloud?",
            "Is there a Business Continuity Plan (BCP)?",
            "Are Recovery Time Objectives (RTOs) defined for critical systems?",
            "Is there a post-incident review process?",
        ],
        "maturity_descriptors": {
            1: "No backups tested. No recovery plan.",
            2: "Backups exist but recovery process is untested.",
            3: "Tested backups and defined RTOs for critical systems.",
            4: "Recovery time is measured against targets.",
            5: "Automated failover. Recovery continuously validated.",
        }
    },
}

# Priority order for remediation (lower number = fix first)
REMEDIATION_PRIORITY = {
    "Govern": 1,
    "Identify": 2,
    "Protect": 3,
    "Detect": 4,
    "Respond": 5,
    "Recover": 6,
}