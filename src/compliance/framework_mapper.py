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
# ─────────────────────────────────────────────────────────────
CONTROL_MAPPING = [
    # ── GOVERN ──────────────────────────────────────────────
    {
        "csf_function":   "Govern",
        "csf_ref":        "GV.OC-01",
        "csf_description":"Organisational cybersecurity policy is established.",
        "iso_ref":        "A.5.1",
        "iso_description":"Policies for information security.",
        "soc2_ref":       "CC1.1",
        "soc2_description":"COSO Principle 1: Demonstrates commitment to integrity and ethics.",
        "control_example":"Written cybersecurity policy approved by the board annually.",
    },
    {
        "csf_function":   "Govern",
        "csf_ref":        "GV.RM-01",
        "csf_description":"Risk management objectives are established and agreed to.",
        "iso_ref":        "A.5.8",
        "iso_description":"Information security in project management.",
        "soc2_ref":       "CC3.1",
        "soc2_description":"Specifies suitable objectives as a precondition to risk identification.",
        "control_example":"Documented risk appetite statement reviewed by executive leadership.",
    },
    # ── IDENTIFY ────────────────────────────────────────────
    {
        "csf_function":   "Identify",
        "csf_ref":        "ID.AM-01",
        "csf_description":"Assets (hardware/software) are inventoried.",
        "iso_ref":        "A.8.1",
        "iso_description":"Inventory of assets.",
        "soc2_ref":       "CC6.1",
        "soc2_description":"Logical access security software, infrastructure and architectures.",
        "control_example":"Real-time asset inventory updated automatically via discovery tools.",
    },
    {
        "csf_function":   "Identify",
        "csf_ref":        "ID.RA-01",
        "csf_description":"Vulnerabilities in assets are identified and documented.",
        "iso_ref":        "A.8.8",
        "iso_description":"Management of technical vulnerabilities.",
        "soc2_ref":       "CC7.1",
        "soc2_description":"Detection and monitoring procedures to identify changes to configurations.",
        "control_example":"Quarterly vulnerability scans with findings tracked in a risk register.",
    },
    # ── PROTECT ─────────────────────────────────────────────
    {
        "csf_function":   "Protect",
        "csf_ref":        "PR.AC-01",
        "csf_description":"Identities and credentials are managed for authorised users.",
        "iso_ref":        "A.9.1",
        "iso_description":"Access control policy.",
        "soc2_ref":       "CC6.1",
        "soc2_description":"Restricts logical access to information assets.",
        "control_example":"MFA enforced on all systems. Access reviewed quarterly.",
    },
    {
        "csf_function":   "Protect",
        "csf_ref":        "PR.DS-01",
        "csf_description":"Data-at-rest is protected.",
        "iso_ref":        "A.8.24",
        "iso_description":"Use of cryptography.",
        "soc2_ref":       "CC6.7",
        "soc2_description":"Restricts the transmission, movement, and removal of information.",
        "control_example":"AES-256 encryption applied to all databases containing customer data.",
    },
    {
        "csf_function":   "Protect",
        "csf_ref":        "PR.AT-01",
        "csf_description":"Personnel are provided awareness and training.",
        "iso_ref":        "A.6.3",
        "iso_description":"Information security awareness, education and training.",
        "soc2_ref":       "CC1.4",
        "soc2_description":"Demonstrates commitment to attract, develop and retain competent people.",
        "control_example":"Annual security awareness training mandatory for all staff.",
    },
    # ── DETECT ──────────────────────────────────────────────
    {
        "csf_function":   "Detect",
        "csf_ref":        "DE.CM-01",
        "csf_description":"Networks and network services are monitored.",
        "iso_ref":        "A.12.4",
        "iso_description":"Logging and monitoring.",
        "soc2_ref":       "CC7.2",
        "soc2_description":"Monitors system components for anomalies that indicate malicious acts.",
        "control_example":"SIEM platform ingesting all network and authentication logs 24/7.",
    },
    {
        "csf_function":   "Detect",
        "csf_ref":        "DE.AE-02",
        "csf_description":"Potentially adverse events are analysed.",
        "iso_ref":        "A.12.4",
        "iso_description":"Logging and monitoring.",
        "soc2_ref":       "CC7.3",
        "soc2_description":"Evaluates security events to determine if they are security incidents.",
        "control_example":"Security events triaged within 4 hours by the SOC team.",
    },
    # ── RESPOND ─────────────────────────────────────────────
    {
        "csf_function":   "Respond",
        "csf_ref":        "RS.RP-01",
        "csf_description":"Incident response plan is established and communicated.",
        "iso_ref":        "A.16.1",
        "iso_description":"Management of information security incidents.",
        "soc2_ref":       "CC7.3",
        "soc2_description":"Responds to identified security incidents by executing a defined plan.",
        "control_example":"IRP tested via tabletop exercise annually. OSFI 24-hr notification included.",
    },
    {
        "csf_function":   "Respond",
        "csf_ref":        "RS.CO-02",
        "csf_description":"Incidents are reported to appropriate authorities.",
        "iso_ref":        "A.16.1",
        "iso_description":"Reporting information security events.",
        "soc2_ref":       "CC2.2",
        "soc2_description":"Communicates internally about objectives, responsibilities and issues.",
        "control_example":"OSFI notified within 24 hours of a significant cyber incident.",
    },
    # ── RECOVER ─────────────────────────────────────────────
    {
        "csf_function":   "Recover",
        "csf_ref":        "RC.RP-01",
        "csf_description":"Recovery plan is executed during or after a cybersecurity incident.",
        "iso_ref":        "A.17.1",
        "iso_description":"Information security continuity.",
        "soc2_ref":       "A1.2",
        "soc2_description":"Environmental protections, software, data back-up processes in place.",
        "control_example":"Tested BCP with defined RTOs. Backups restored successfully each quarter.",
    },
    {
        "csf_function":   "Recover",
        "csf_ref":        "RC.IM-01",
        "csf_description":"Recovery plans incorporate lessons learned.",
        "iso_ref":        "A.16.1",
        "iso_description":"Post-incident reviews conducted.",
        "soc2_ref":       "CC4.2",
        "soc2_description":"Evaluates and communicates deficiencies in a timely manner.",
        "control_example":"Post-incident report completed within 2 weeks. IRP updated accordingly.",
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
        print(f"  {Fore.GREEN}Example   : {control['control_example']}{Style.RESET_ALL}")

    print(f"\n{'=' * 70}")
    print(f"  Total controls mapped: {len(CONTROL_MAPPING)}")
    print(f"  Frameworks covered: NIST CSF 2.0 | ISO 27001:2022 | SOC 2 TSC")
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
            c["control_example"][:55] + "..." if len(c["control_example"]) > 55 else c["control_example"],
        ])

    print(tabulate(
        table_data,
        headers=["NIST CSF", "ISO 27001", "SOC 2", "Control Example"],
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
    lines.append("ISO 27001 Annex A clause and SOC 2 Trust Services Criteria.")
    lines.append("One control — three frameworks. No duplicate work.\n")
    lines.append("---\n")

    current_function = None
    for c in CONTROL_MAPPING:
        if c["csf_function"] != current_function:
            current_function = c["csf_function"]
            lines.append(f"\n## {current_function}\n")
            lines.append("| NIST CSF | ISO 27001 | SOC 2 | Control Example |")
            lines.append("|----------|-----------|-------|-----------------|")

        lines.append(
            f"| {c['csf_ref']} — {c['csf_description']} "
            f"| {c['iso_ref']} — {c['iso_description']} "
            f"| {c['soc2_ref']} — {c['soc2_description']} "
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