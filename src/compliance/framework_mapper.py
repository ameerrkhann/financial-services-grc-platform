# src/compliance/framework_mapper.py
# Cross-framework control mapping: NIST CSF 2.0 → ISO 27001 → SOC 2

import sys
import os
from tabulate import tabulate
from colorama import Fore, Style, init

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

init(autoreset=True)

# ─────────────────────────────────────────────────────────────
# The core mapping table
# Each entry = one control that satisfies all 3 frameworks
#
# CSF IDs are from the NIST CSF 2.0 Core (NIST CSWP 29, February 2024).
# ISO IDs are from ISO/IEC 27001:2022 Annex A (93 controls, 4 themes) —
# the 2013 numbering does not apply. OSFI references name the guideline and
# domain rather than inventing section numbers.
# ─────────────────────────────────────────────────────────────
CONTROL_MAPPING = [
    # ── GOVERN ──────────────────────────────────────────────
    {
        "csf_function":   "Govern",
        "csf_ref":        "GV.PO-01",
        "csf_description":"Policy for managing cybersecurity risks is established, communicated and enforced.",
        "iso_ref":        "A.5.1",
        "iso_description":"Policies for information security.",
        "soc2_ref":       "CC1.1",
        "soc2_description":"COSO Principle 1: Demonstrates commitment to integrity and ethics.",
        "osfi_ref":       "B-13 — Governance and Risk Management",
        "control_example":"Written cybersecurity policy approved by the board annually.",
        "test_frequency": "Annual",
    },
    {
        "csf_function":   "Govern",
        "csf_ref":        "GV.RM-01",
        "csf_description":"Risk management objectives are established and agreed to by stakeholders.",
        "iso_ref":        "Clause 6.1",
        "iso_description":"Actions to address information security risks and opportunities.",
        "soc2_ref":       "CC3.1",
        "soc2_description":"Specifies suitable objectives as a precondition to risk identification.",
        "osfi_ref":       "B-13 — Governance and Risk Management",
        "control_example":"Documented risk appetite statement reviewed by executive leadership.",
        "test_frequency": "Annual",
    },
    {
        "csf_function":   "Govern",
        "csf_ref":        "GV.SC-04",
        "csf_description":"Suppliers are known and prioritised by criticality.",
        "iso_ref":        "A.5.19",
        "iso_description":"Information security in supplier relationships.",
        "soc2_ref":       "CC9.2",
        "soc2_description":"Assesses and manages risks associated with vendors and business partners.",
        "osfi_ref":       "B-10 — Third-Party Risk Management",
        "control_example":"Vendor register with a risk tier per vendor, refreshed each assessment.",
        "test_frequency": "Quarterly",
    },
    {
        "csf_function":   "Govern",
        "csf_ref":        "GV.SC-07",
        "csf_description":"Risks posed by suppliers and third parties are assessed and monitored across the relationship.",
        "iso_ref":        "A.5.22",
        "iso_description":"Monitoring, review and change management of supplier services.",
        "soc2_ref":       "CC9.2",
        "soc2_description":"Assesses and manages risks associated with vendors and business partners.",
        "osfi_ref":       "B-10 — Third-Party Risk Management",
        "control_example":"Vendor reassessed on its tier's cycle; overdue vendors flagged automatically.",
        "test_frequency": "Quarterly",
    },
    # ── IDENTIFY ────────────────────────────────────────────
    {
        "csf_function":   "Identify",
        "csf_ref":        "ID.AM-01",
        "csf_description":"Inventories of hardware managed by the organisation are maintained.",
        "iso_ref":        "A.5.9",
        "iso_description":"Inventory of information and other associated assets.",
        "soc2_ref":       "CC6.1",
        "soc2_description":"Logical access security software, infrastructure and architectures.",
        "osfi_ref":       "B-13 — Technology Operations and Resilience",
        "control_example":"Real-time asset inventory updated automatically via discovery tools.",
        "test_frequency": "Quarterly",
    },
    {
        "csf_function":   "Identify",
        "csf_ref":        "ID.RA-01",
        "csf_description":"Vulnerabilities in assets are identified, validated and recorded.",
        "iso_ref":        "A.8.8",
        "iso_description":"Management of technical vulnerabilities.",
        "soc2_ref":       "CC7.1",
        "soc2_description":"Detection and monitoring procedures to identify changes to configurations.",
        "osfi_ref":       "B-13 — Cyber Security",
        "control_example":"Quarterly vulnerability scans with findings tracked in a risk register.",
        "test_frequency": "Quarterly",
    },
    {
        "csf_function":   "Identify",
        "csf_ref":        "ID.IM-04",
        "csf_description":"Incident response and other cybersecurity plans are established, maintained and improved.",
        "iso_ref":        "A.5.27",
        "iso_description":"Learning from information security incidents.",
        "soc2_ref":       "CC4.2",
        "soc2_description":"Evaluates and communicates deficiencies in a timely manner.",
        "osfi_ref":       "E-21 — Operational Risk and Resilience Management",
        "control_example":"Post-incident report completed within 2 weeks. IRP updated accordingly.",
        "test_frequency": "Per incident",
    },
    # ── PROTECT ─────────────────────────────────────────────
    {
        "csf_function":   "Protect",
        "csf_ref":        "PR.AA-01",
        "csf_description":"Identities and credentials for authorised users, services and hardware are managed.",
        "iso_ref":        "A.5.15, A.8.5",
        "iso_description":"Access control; secure authentication.",
        "soc2_ref":       "CC6.1",
        "soc2_description":"Restricts logical access to information assets.",
        "osfi_ref":       "B-13 — Cyber Security",
        "control_example":"MFA enforced on all systems. Joiner/mover/leaver process automated.",
        "test_frequency": "Quarterly",
    },
    {
        "csf_function":   "Protect",
        "csf_ref":        "PR.AA-05",
        "csf_description":"Access permissions and authorisations are managed, incorporating least privilege and separation of duties.",
        "iso_ref":        "A.5.18",
        "iso_description":"Access rights.",
        "soc2_ref":       "CC6.3",
        "soc2_description":"Authorises, modifies or removes access based on roles and responsibilities.",
        "osfi_ref":       "B-13 — Cyber Security",
        "control_example":"Quarterly access recertification by system owners. Privileged access via PAM.",
        "test_frequency": "Quarterly",
    },
    {
        "csf_function":   "Protect",
        "csf_ref":        "PR.DS-01",
        "csf_description":"The confidentiality, integrity and availability of data-at-rest are protected.",
        "iso_ref":        "A.8.24",
        "iso_description":"Use of cryptography.",
        "soc2_ref":       "CC6.7",
        "soc2_description":"Restricts the transmission, movement, and removal of information.",
        "osfi_ref":       "B-13 — Cyber Security",
        "control_example":"AES-256 encryption applied to all databases containing customer data.",
        "test_frequency": "Semi-annual",
    },
    {
        "csf_function":   "Protect",
        "csf_ref":        "PR.DS-11",
        "csf_description":"Backups of data are created, protected, maintained and tested.",
        "iso_ref":        "A.8.13",
        "iso_description":"Information backup.",
        "soc2_ref":       "A1.2",
        "soc2_description":"Environmental protections, software, data back-up processes in place.",
        "osfi_ref":       "E-21 — Operational Risk and Resilience Management",
        "control_example":"Immutable offline backups restored successfully each quarter.",
        "test_frequency": "Quarterly",
    },
    {
        "csf_function":   "Protect",
        "csf_ref":        "PR.AT-01",
        "csf_description":"Personnel are provided awareness and training.",
        "iso_ref":        "A.6.3",
        "iso_description":"Information security awareness, education and training.",
        "soc2_ref":       "CC1.4",
        "soc2_description":"Demonstrates commitment to attract, develop and retain competent people.",
        "osfi_ref":       "B-13 — Governance and Risk Management",
        "control_example":"Annual security awareness training mandatory for all staff.",
        "test_frequency": "Annual",
    },
    # ── DETECT ──────────────────────────────────────────────
    {
        "csf_function":   "Detect",
        "csf_ref":        "DE.CM-01",
        "csf_description":"Networks and network services are monitored to find potentially adverse events.",
        "iso_ref":        "A.8.15, A.8.16",
        "iso_description":"Logging; monitoring activities.",
        "soc2_ref":       "CC7.2",
        "soc2_description":"Monitors system components for anomalies that indicate malicious acts.",
        "osfi_ref":       "B-13 — Cyber Security",
        "control_example":"SIEM platform ingesting all network and authentication logs 24/7.",
        "test_frequency": "Monthly",
    },
    {
        "csf_function":   "Detect",
        "csf_ref":        "DE.AE-02",
        "csf_description":"Potentially adverse events are analysed to better understand associated activities.",
        "iso_ref":        "A.8.16",
        "iso_description":"Monitoring activities.",
        "soc2_ref":       "CC7.3",
        "soc2_description":"Evaluates security events to determine if they are security incidents.",
        "osfi_ref":       "B-13 — Cyber Security",
        "control_example":"Security events triaged within 4 hours by the SOC team.",
        "test_frequency": "Monthly",
    },
    # ── RESPOND ─────────────────────────────────────────────
    {
        "csf_function":   "Respond",
        "csf_ref":        "RS.MA-01",
        "csf_description":"The incident response plan is executed in coordination with relevant third parties once an incident is declared.",
        "iso_ref":        "A.5.24, A.5.26",
        "iso_description":"Incident management planning and preparation; response to incidents.",
        "soc2_ref":       "CC7.4",
        "soc2_description":"Responds to identified security incidents by executing a defined programme.",
        "osfi_ref":       "B-13 — Cyber Security",
        "control_example":"IRP tested via tabletop exercise annually, with named incident commander.",
        "test_frequency": "Annual",
    },
    {
        "csf_function":   "Respond",
        "csf_ref":        "RS.CO-02",
        "csf_description":"Internal and external stakeholders are notified of incidents.",
        "iso_ref":        "A.6.8",
        "iso_description":"Information security event reporting.",
        "soc2_ref":       "CC2.2",
        "soc2_description":"Communicates internally about objectives, responsibilities and issues.",
        "osfi_ref":       "Technology and Cyber Security Incident Reporting advisory — 24-hour reporting",
        "control_example":"OSFI's Technology Risk Division and lead supervisor notified within 24 hours of a reportable incident.",
        "test_frequency": "Per incident",
    },
    # ── RECOVER ─────────────────────────────────────────────
    {
        "csf_function":   "Recover",
        "csf_ref":        "RC.RP-01",
        "csf_description":"The recovery portion of the incident response plan is executed once initiated.",
        "iso_ref":        "A.5.29, A.5.30",
        "iso_description":"Information security during disruption; ICT readiness for business continuity.",
        "soc2_ref":       "A1.2",
        "soc2_description":"Environmental protections, software, data back-up processes in place.",
        "osfi_ref":       "E-21 — Operational Risk and Resilience Management",
        "control_example":"Tested BCP with defined RTOs for every critical operation.",
        "test_frequency": "Annual",
    },
]


def print_full_mapping():
    """Prints the complete cross-framework mapping table."""
    print(f"\n{'=' * 70}")
    print("   CROSS-FRAMEWORK CONTROL MAPPING")
    print("   NIST CSF 2.0  →  ISO 27001 Annex A  →  SOC 2 Trust Services")
    print(f"{'=' * 70}\n")

    current_function = None

    for control in CONTROL_MAPPING:
        # Print a section header when the function changes
        if control["csf_function"] != current_function:
            current_function = control["csf_function"]
            print(f"\n{Fore.CYAN}── {current_function.upper()} {'─' * (55 - len(current_function))}{Style.RESET_ALL}")

        print(f"\n  {Fore.YELLOW}{control['csf_ref']}{Style.RESET_ALL} — {control['csf_description']}")
        print(f"  ISO 27001 : {control['iso_ref']} — {control['iso_description']}")
        print(f"  SOC 2     : {control['soc2_ref']} — {control['soc2_description']}")
        print(f"  OSFI      : {control['osfi_ref']}")
        print(f"  {Fore.GREEN}Example   : {control['control_example']}{Style.RESET_ALL}")

    print(f"\n{'=' * 70}")
    print(f"  Total controls mapped: {len(CONTROL_MAPPING)}")
    print(f"  Frameworks covered: NIST CSF 2.0 | ISO/IEC 27001:2022 | SOC 2 TSC | OSFI")
    print(f"{'=' * 70}\n")


def print_mapping_by_function(function_name):
    """Prints controls for a single CSF function only."""
    filtered = [c for c in CONTROL_MAPPING if c["csf_function"] == function_name]

    if not filtered:
        print(f"  No mappings found for function: {function_name}")
        return

    print(f"\n{Fore.CYAN}Controls for: {function_name}{Style.RESET_ALL}\n")
    table_data = []
    for c in filtered:
        table_data.append([
            c["csf_ref"],
            c["iso_ref"],
            c["soc2_ref"],
            c["osfi_ref"],
            c["control_example"][:55] + "..." if len(c["control_example"]) > 55 else c["control_example"],
        ])

    print(tabulate(
        table_data,
        headers=["NIST CSF", "ISO 27001", "SOC 2", "OSFI", "Control Example"],
        tablefmt="rounded_outline"
    ))


def save_mapping_to_file():
    """Saves the full mapping to a markdown file in /docs."""
    output_path = os.path.join(
        os.path.dirname(__file__), "../../docs/control_framework_mapping.md"
    )

    lines = []
    lines.append("# Cross-Framework Control Mapping")
    lines.append("## NIST CSF 2.0 → ISO 27001 → SOC 2\n")
    lines.append("This document maps each NIST CSF 2.0 control to its equivalent")
    lines.append("ISO/IEC 27001:2022 Annex A control, SOC 2 Trust Services Criteria,")
    lines.append("and the OSFI guideline it supports. One control — four frameworks.")
    lines.append("No duplicate work.\n")
    lines.append("CSF IDs are from the NIST CSF 2.0 Core (NIST CSWP 29, February 2024).")
    lines.append("ISO IDs are from ISO/IEC 27001:2022 Annex A — not the 2013 numbering.\n")
    lines.append("---\n")

    current_function = None
    for c in CONTROL_MAPPING:
        if c["csf_function"] != current_function:
            current_function = c["csf_function"]
            lines.append(f"\n## {current_function}\n")
            lines.append("| NIST CSF 2.0 | ISO/IEC 27001:2022 | SOC 2 | OSFI | Control Example |")
            lines.append("|--------------|--------------------|-------|------|-----------------|")

        lines.append(
            f"| {c['csf_ref']} — {c['csf_description']} "
            f"| {c['iso_ref']} — {c['iso_description']} "
            f"| {c['soc2_ref']} — {c['soc2_description']} "
            f"| {c['osfi_ref']} "
            f"| {c['control_example']} |"
        )

    lines.append(f"\n---")
    lines.append(f"*Total controls mapped: {len(CONTROL_MAPPING)}*")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"  ✅ Mapping saved to docs/control_framework_mapping.md")


def run_mapper():
    """Interactive menu for the framework mapper."""
    print("\n" + "=" * 65)
    print("   NIST CSF 2.0 — Cross-Framework Control Mapper")
    print("=" * 65)
    print("\n  1. View full mapping (all 6 functions)")
    print("  2. View mapping for one function")
    print("  3. Save mapping to docs folder")
    print("  4. All of the above\n")

    choice = input("  Choose an option (1–4): ").strip()

    if choice == "1":
        print_full_mapping()
    elif choice == "2":
        print("\n  Functions: Govern, Identify, Protect, Detect, Respond, Recover")
        func = input("  Enter function name: ").strip().capitalize()
        print_mapping_by_function(func)
    elif choice == "3":
        save_mapping_to_file()
    elif choice == "4":
        print_full_mapping()
        save_mapping_to_file()
    else:
        print("  Invalid choice.")


if __name__ == "__main__":
    run_mapper()