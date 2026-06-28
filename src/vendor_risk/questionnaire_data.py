# src/vendor_risk/questionnaire_data.py
# Vendor security questionnaire questions organised by service type
# Aligned to OSFI B-10 Third-Party Risk Management requirements

# Questions that apply to every vendor regardless of type
UNIVERSAL_QUESTIONS = [
    {
        "id":       "U01",
        "category": "Governance",
        "question": "Does the vendor have a documented Information Security Policy approved by senior leadership?",
        "osfi_ref": "B-10 s.3 — Third-Party Risk Governance",
        "weight":   3,  # higher weight = more important to the score
    },
    {
        "id":       "U02",
        "category": "Governance",
        "question": "Has the vendor achieved or maintained a recognised security certification (ISO 27001, SOC 2 Type II)?",
        "osfi_ref": "B-10 s.4 — Due Diligence",
        "weight":   3,
    },
    {
        "id":       "U03",
        "category": "Incident Response",
        "question": "Does the vendor have a documented Incident Response Plan that includes notification to clients within 24 hours of a confirmed breach?",
        "osfi_ref": "B-10 s.7 — Incident Notification",
        "weight":   3,
    },
    {
        "id":       "U04",
        "category": "Incident Response",
        "question": "Has the vendor experienced a security incident or data breach in the past 3 years? If yes, was a post-incident report provided to affected clients?",
        "osfi_ref": "B-10 s.7 — Incident History",
        "weight":   2,
    },
    {
        "id":       "U05",
        "category": "Access Control",
        "question": "Does the vendor enforce Multi-Factor Authentication (MFA) on all systems with access to client data?",
        "osfi_ref": "B-13 s.5 — Cyber Controls",
        "weight":   3,
    },
    {
        "id":       "U06",
        "category": "Access Control",
        "question": "Does the vendor apply the principle of least privilege — restricting employee access to only what is necessary for their role?",
        "osfi_ref": "B-13 s.5 — Access Management",
        "weight":   2,
    },
    {
        "id":       "U07",
        "category": "Data Protection",
        "question": "Is all client data encrypted at rest (AES-256 or equivalent) and in transit (TLS 1.2 or higher)?",
        "osfi_ref": "B-10 s.5 — Data Security",
        "weight":   3,
    },
    {
        "id":       "U08",
        "category": "Data Protection",
        "question": "Does the vendor have a documented data retention and secure deletion policy?",
        "osfi_ref": "B-10 s.5 — Data Handling",
        "weight":   2,
    },
    {
        "id":       "U09",
        "category": "Business Continuity",
        "question": "Does the vendor have a tested Business Continuity Plan (BCP) with defined Recovery Time Objectives (RTOs)?",
        "osfi_ref": "E-21 — Operational Resilience",
        "weight":   3,
    },
    {
        "id":       "U10",
        "category": "Business Continuity",
        "question": "Are backups of client data performed regularly and tested for successful restoration?",
        "osfi_ref": "E-21 — Recovery Capability",
        "weight":   2,
    },
    {
        "id":       "U11",
        "category": "Vulnerability Management",
        "question": "Does the vendor conduct regular penetration testing (at least annually) by an independent third party?",
        "osfi_ref": "B-13 s.5 — Security Testing",
        "weight":   2,
    },
    {
        "id":       "U12",
        "category": "Vulnerability Management",
        "question": "Does the vendor have a formal vulnerability management process with defined SLAs for patching critical vulnerabilities?",
        "osfi_ref": "B-13 s.5 — Vulnerability Management",
        "weight":   2,
    },
    {
        "id":       "U13",
        "category": "Subcontracting",
        "question": "Does the vendor use sub-contractors or fourth parties with access to client data? If yes, are they subject to equivalent security requirements?",
        "osfi_ref": "B-10 s.6 — Fourth-Party Risk",
        "weight":   2,
    },
    {
        "id":       "U14",
        "category": "Audit Rights",
        "question": "Does the vendor contractually permit the client to conduct security audits or review independent audit reports (SOC 2, penetration test results)?",
        "osfi_ref": "B-10 s.8 — Right to Audit",
        "weight":   2,
    },
]

# Additional questions for specific vendor service types
SERVICE_SPECIFIC_QUESTIONS = {
    "Cloud Provider": [
        {
            "id":       "CL01",
            "category": "Cloud Security",
            "question": "Does the vendor provide data residency guarantees ensuring Canadian customer data remains within Canada?",
            "osfi_ref": "B-13 s.6 — Cloud Data Residency",
            "weight":   3,
        },
        {
            "id":       "CL02",
            "category": "Cloud Security",
            "question": "Does the vendor have a Cloud Security Posture Management (CSPM) tool that continuously monitors for misconfigurations?",
            "osfi_ref": "B-13 s.6 — Cloud Risk Management",
            "weight":   2,
        },
        {
            "id":       "CL03",
            "category": "Cloud Security",
            "question": "Does the vendor provide a documented exit strategy enabling the client to migrate data off-platform with minimal disruption?",
            "osfi_ref": "B-10 s.9 — Exit Planning",
            "weight":   3,
        },
        {
            "id":       "CL04",
            "category": "Cloud Security",
            "question": "Is there logical separation (multi-tenancy isolation) between this client's data and other clients' data?",
            "osfi_ref": "B-13 s.6 — Data Segregation",
            "weight":   3,
        },
    ],
    "Payment Processor": [
        {
            "id":       "PP01",
            "category": "Payment Security",
            "question": "Is the vendor compliant with PCI DSS Level 1 and can they provide a current Report on Compliance (ROC)?",
            "osfi_ref": "B-10 s.4 — Compliance Verification",
            "weight":   3,
        },
        {
            "id":       "PP02",
            "category": "Payment Security",
            "question": "Does the vendor use tokenisation or encryption to protect payment card data during processing?",
            "osfi_ref": "B-13 s.5 — Payment Data Protection",
            "weight":   3,
        },
        {
            "id":       "PP03",
            "category": "Payment Security",
            "question": "Does the vendor have real-time fraud detection and transaction monitoring in place?",
            "osfi_ref": "B-13 s.4 — Threat Monitoring",
            "weight":   2,
        },
        {
            "id":       "PP04",
            "category": "Payment Security",
            "question": "What is the vendor's maximum transaction processing downtime per year (availability SLA)?",
            "osfi_ref": "E-21 — Service Continuity",
            "weight":   3,
        },
    ],
    "Software / SaaS": [
        {
            "id":       "SW01",
            "category": "Software Security",
            "question": "Does the vendor follow a Secure Software Development Lifecycle (SSDLC) with security testing at each development stage?",
            "osfi_ref": "B-13 s.5 — Secure Development",
            "weight":   2,
        },
        {
            "id":       "SW02",
            "category": "Software Security",
            "question": "Does the vendor conduct Static Application Security Testing (SAST) and Dynamic Application Security Testing (DAST) on all releases?",
            "osfi_ref": "B-13 s.5 — Application Security",
            "weight":   2,
        },
        {
            "id":       "SW03",
            "category": "Software Security",
            "question": "How frequently does the vendor release security patches and what is the SLA for critical vulnerability remediation?",
            "osfi_ref": "B-13 s.5 — Patch Management",
            "weight":   2,
        },
        {
            "id":       "SW04",
            "category": "Software Security",
            "question": "Does the vendor provide a Software Bill of Materials (SBOM) identifying all third-party components and open-source libraries?",
            "osfi_ref": "B-10 s.6 — Supply Chain Risk",
            "weight":   2,
        },
    ],
    "Data Analytics / AI": [
        {
            "id":       "DA01",
            "category": "Data Governance",
            "question": "Is client data used to train AI or machine learning models? If yes, is explicit consent obtained and documented?",
            "osfi_ref": "B-10 s.5 — Data Use Restrictions",
            "weight":   3,
        },
        {
            "id":       "DA02",
            "category": "Data Governance",
            "question": "Does the vendor have a documented data minimisation policy — only collecting data necessary for the contracted service?",
            "osfi_ref": "B-10 s.5 — Data Minimisation",
            "weight":   2,
        },
        {
            "id":       "DA03",
            "category": "Data Governance",
            "question": "Are analytical outputs and AI model decisions explainable and auditable by the client?",
            "osfi_ref": "B-13 s.4 — Model Risk",
            "weight":   2,
        },
        {
            "id":       "DA04",
            "category": "Data Governance",
            "question": "Does the vendor conduct bias testing and fairness audits on AI models that inform decisions about customers?",
            "osfi_ref": "B-13 s.4 — AI Governance",
            "weight":   2,
        },
    ],
    "IT Infrastructure": [
        {
            "id":       "IT01",
            "category": "Network Security",
            "question": "Does the vendor use network segmentation to isolate client environments from other clients and internal systems?",
            "osfi_ref": "B-13 s.5 — Network Controls",
            "weight":   2,
        },
        {
            "id":       "IT02",
            "category": "Network Security",
            "question": "Are all remote access connections to client systems made via encrypted VPN or Zero Trust Network Access (ZTNA)?",
            "osfi_ref": "B-13 s.5 — Remote Access",
            "weight":   3,
        },
        {
            "id":       "IT03",
            "category": "Physical Security",
            "question": "Are data centres where client data is processed certified to SOC 2 Type II or ISO 27001 and subject to physical access controls?",
            "osfi_ref": "B-10 s.4 — Physical Security",
            "weight":   2,
        },
        {
            "id":       "IT04",
            "category": "Network Security",
            "question": "Does the vendor have 24/7 Security Operations Centre (SOC) monitoring with defined escalation procedures?",
            "osfi_ref": "B-13 s.5 — Continuous Monitoring",
            "weight":   2,
        },
    ],
}

# Risk tier thresholds (used in Day 18 scoring)
RISK_TIERS = {
    "Critical": {"min": 0,  "max": 40,  "colour": "#ff2d55", "action": "Do not onboard without remediation plan. Executive approval required."},
    "High":     {"min": 41, "max": 60,  "colour": "#ff6b35", "action": "Onboard with conditions. Quarterly reassessment required."},
    "Medium":   {"min": 61, "max": 80,  "colour": "#ffdd00", "action": "Standard onboarding. Annual reassessment required."},
    "Low":      {"min": 81, "max": 100, "colour": "#32d74b", "action": "Approve for onboarding. Biennial reassessment required."},
}

SERVICE_TYPES = list(SERVICE_SPECIFIC_QUESTIONS.keys())