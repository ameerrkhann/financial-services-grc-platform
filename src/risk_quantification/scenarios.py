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
        "loss_low":    500_000,     # $500K minimum — regulatory fines alone
        "loss_high":   8_000_000,   # $8M maximum — class action + OSFI remediation
        "freq_low":    0.5,         # Once every 2 years at minimum
        "freq_high":   3.0,         # Up to 3 attempts/year
        "osfi_ref":    "OSFI B-13 s.5 — Cyber Incident Notification (24hr rule)",
        "nist_ref":    "DE.CM-01, RS.RP-01",
        "controls":    [
            "Data Loss Prevention (DLP) tools",
            "Encryption of all PII at rest and in transit",
            "Privileged Access Management (PAM)",
            "OSFI 24-hour breach notification process",
        ],
        "control_cost": 350_000,    # estimated annual cost of controls
    },

    "ransomware": {
        "id":          2,
        "name":        "Ransomware Attack",
        "description": (
            "Malware encrypts critical banking systems — core banking platform, "
            "payment processing, customer portal. Attacker demands ransom. "
            "Business operations halted. Regulatory reporting triggered."
        ),
        "loss_low":    800_000,     # $800K — even 'contained' incidents cost this
        "loss_high":   12_000_000,  # $12M — full operational shutdown scenario
        "freq_low":    0.5,
        "freq_high":   2.0,
        "osfi_ref":    "OSFI B-13 s.5 — Technology Incident Reporting",
        "nist_ref":    "PR.AC-01, DE.CM-01, RC.RP-01",
        "controls":    [
            "Immutable offline backups tested quarterly",
            "Network segmentation to limit lateral movement",
            "Endpoint Detection & Response (EDR) on all devices",
            "Incident response plan with ransomware-specific playbook",
        ],
        "control_cost": 500_000,
    },
}