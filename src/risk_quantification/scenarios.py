# src/risk_quantification/scenarios.py
# FAIR scenario definitions for First National Bank (Fictional)
# Parameters based on Canadian financial services threat landscape

SCENARIOS = {
    "data_breach": {
        "id":          1,
        "name":        "Data Breach — Customer PII",
        "description": (
            "Unauthorised exfiltration of customer personally identifiable "
            "information (PII). Includes names, SINs, account numbers, and "
            "transaction history. Triggered by phishing, credential stuffing, "
            "or insider access abuse."
        ),
        "loss_low":    500_000,
        "loss_high":   8_000_000,
        "freq_low":    0.5,
        "freq_high":   3.0,
        "osfi_ref":    "OSFI B-13 s.5 — Cyber Incident Notification (24hr rule)",
        "nist_ref":    "DE.CM-01, RS.RP-01",
        "controls": [
            "Data Loss Prevention (DLP) tools",
            "Encryption of all PII at rest and in transit",
            "Privileged Access Management (PAM)",
            "OSFI 24-hour breach notification process",
        ],
        "control_cost": 350_000,
    },

    "ransomware": {
        "id":          2,
        "name":        "Ransomware Attack",
        "description": (
            "Malware encrypts critical banking systems — core banking platform, "
            "payment processing, customer portal. Attacker demands ransom. "
            "Business operations halted. Regulatory reporting triggered."
        ),
        "loss_low":    800_000,
        "loss_high":   12_000_000,
        "freq_low":    0.5,
        "freq_high":   2.0,
        "osfi_ref":    "OSFI B-13 s.5 — Technology Incident Reporting",
        "nist_ref":    "PR.AC-01, DE.CM-01, RC.RP-01",
        "controls": [
            "Immutable offline backups tested quarterly",
            "Network segmentation to limit lateral movement",
            "Endpoint Detection & Response (EDR) on all devices",
            "Incident response plan with ransomware-specific playbook",
        ],
        "control_cost": 500_000,
    },

    "insider_threat": {
        "id":          3,
        "name":        "Insider Threat — Privileged Access Abuse",
        "description": (
            "A malicious or negligent employee or contractor misuses privileged "
            "access to exfiltrate customer data, manipulate transactions, or "
            "sabotage systems. Particularly difficult to detect because the "
            "actor has legitimate credentials. Financial services firms are "
            "prime targets due to high-value data and transaction access."
        ),
        "loss_low":    200_000,     # smaller but more frequent
        "loss_high":   5_000_000,   # large fraud or mass data theft
        "freq_low":    0.5,
        "freq_high":   2.0,
        "osfi_ref":    "OSFI B-13 s.4 — Cyber Risk Governance & Access Controls",
        "nist_ref":    "PR.AC-01, DE.AE-02, RS.RP-01",
        "controls": [
            "User and Entity Behaviour Analytics (UEBA)",
            "Least-privilege access with quarterly access reviews",
            "Separation of duties for high-risk transactions",
            "Offboarding procedure — immediate access revocation",
        ],
        "control_cost": 280_000,
    },

    "vendor_failure": {
        "id":          4,
        "name":        "Third-Party Vendor Security Failure",
        "description": (
            "A critical vendor — cloud provider, payment processor, or software "
            "supplier — suffers a security breach that exposes the bank's data "
            "or disrupts services. The bank is liable even though the breach "
            "occurred externally. OSFI B-10 requires banks to manage and monitor "
            "vendor risk throughout the vendor lifecycle."
        ),
        "loss_low":    400_000,
        "loss_high":   9_000_000,
        "freq_low":    0.3,         # less frequent but high impact
        "freq_high":   1.5,
        "osfi_ref":    "OSFI B-10 — Third-Party Risk Management",
        "nist_ref":    "ID.RA-01, DE.CM-01, RS.CO-02",
        "controls": [
            "Vendor security questionnaires and risk tiering (Critical/High/Medium/Low)",
            "Contractual security requirements in all vendor agreements",
            "Continuous vendor monitoring and annual reassessment",
            "Incident notification clauses requiring vendor to notify within 24 hours",
        ],
        "control_cost": 200_000,
    },

    "cloud_misconfiguration": {
        "id":          5,
        "name":        "Cloud Misconfiguration — Data Exposure",
        "description": (
            "A misconfigured cloud storage bucket, database, or API exposes "
            "sensitive customer or operational data publicly. Common causes: "
            "overly permissive IAM policies, publicly accessible storage, "
            "unencrypted databases, or exposed API keys in code repositories. "
            "Canadian banks accelerating cloud adoption face growing exposure "
            "to this risk category."
        ),
        "loss_low":    150_000,
        "loss_high":   6_000_000,
        "freq_low":    1.0,         # most frequent — happens at nearly every large org
        "freq_high":   4.0,
        "osfi_ref":    "OSFI B-13 s.6 — Cloud and Technology Risk Management",
        "nist_ref":    "PR.DS-01, ID.AM-01, DE.CM-01",
        "controls": [
            "Cloud Security Posture Management (CSPM) tool",
            "Automated misconfiguration scanning on all cloud resources",
            "Infrastructure-as-Code (IaC) security scanning in CI/CD pipeline",
            "No public storage buckets policy enforced via cloud policy engine",
        ],
        "control_cost": 180_000,
    },
}