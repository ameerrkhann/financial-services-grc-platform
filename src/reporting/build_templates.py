# src/reporting/build_templates.py
# Builds the two Excel deliverables in templates/:
#
#   risk_register.xlsx  — a working risk register with live formulas,
#                         dropdowns and conditional formatting. Seeded with
#                         one example row per FAIR scenario, ALE read from
#                         the database.
#   control_matrix.xlsx — one row per control in framework_mapper's
#                         CONTROL_MAPPING, with test tracking and a
#                         formula-driven summary sheet.
#
# Run seed_demo_data.py first so the example rows carry real numbers.

import sys
import os
from datetime import date, timedelta

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.compliance.csf_data import CSF_FUNCTIONS
from src.compliance.framework_mapper import CONTROL_MAPPING
from src.database.db_manager import (
    get_connection,
    get_latest_scenario_run,
    initialise_database,
)
from src.risk_quantification.scenarios import SCENARIOS

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../../templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

BLANK_ROWS = 20

# One accent, matching the executive PDF
ACCENT      = "14607A"
ACCENT_PALE = "E8F1F4"
HEAD_FONT   = Font(color="FFFFFF", bold=True, size=10)
HEAD_FILL   = PatternFill("solid", fgColor=ACCENT)
TITLE_FONT  = Font(color=ACCENT, bold=True, size=14)
NOTE_FONT   = Font(color="5A5A5A", italic=True, size=9)

THIN   = Side(style="thin", color="C9D6DB")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# Rating colours, shared by both workbooks
RATING_FILLS = {
    "Critical": PatternFill("solid", fgColor="F8CBCB"),
    "High":     PatternFill("solid", fgColor="FBDDC4"),
    "Medium":   PatternFill("solid", fgColor="FCF0C0"),
    "Low":      PatternFill("solid", fgColor="D4EDD5"),
}
RESULT_FILLS = {
    "Effective":           PatternFill("solid", fgColor="D4EDD5"),
    "Partially Effective": PatternFill("solid", fgColor="FCF0C0"),
    "Ineffective":         PatternFill("solid", fgColor="F8CBCB"),
    "Not Tested":          PatternFill("solid", fgColor="E4E4E4"),
}


# ─────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────
def write_header(ws, headers, widths, row=1):
    """Writes a styled header row, sets widths, freezes and autofilters."""
    for i, (title, width) in enumerate(zip(headers, widths), start=1):
        cell = ws.cell(row=row, column=i, value=title)
        cell.font      = HEAD_FONT
        cell.fill      = HEAD_FILL
        cell.border    = BORDER
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.row_dimensions[row].height = 30
    ws.freeze_panes = f"A{row + 1}"
    ws.auto_filter.ref = f"A{row}:{get_column_letter(len(headers))}{row}"


def style_body(ws, first_row, last_row, n_cols, wrap_cols=()):
    """Applies borders, alignment and banding to the data range."""
    band = PatternFill("solid", fgColor="F5F8F9")
    for r in range(first_row, last_row + 1):
        for c in range(1, n_cols + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BORDER
            cell.font   = Font(size=10)
            cell.alignment = Alignment(
                vertical="top",
                wrap_text=c in wrap_cols,
            )
            if (r - first_row) % 2 == 1:
                cell.fill = band


def add_list_validation(ws, col, options, first_row, last_row, prompt=""):
    """Adds a dropdown to a whole column range."""
    dv = DataValidation(
        type="list",
        formula1='"' + ",".join(options) + '"',
        allow_blank=True,
        showDropDown=False,          # False = show the dropdown arrow in Excel
        promptTitle=col,
        prompt=prompt,
    )
    ws.add_data_validation(dv)
    dv.add(f"{col}{first_row}:{col}{last_row}")
    return dv


def add_rating_formatting(ws, col, first_row, last_row, fills):
    """Colours a rating/result column by its text value."""
    rng = f"{col}{first_row}:{col}{last_row}"
    for value, fill in fills.items():
        ws.conditional_formatting.add(rng, CellIsRule(
            operator="equal", formula=[f'"{value}"'], fill=fill, stopIfTrue=False,
        ))


def rating_formula(score_cell):
    """Shared 1-25 rating thresholds: >=15 Critical, >=10 High, >=5 Medium."""
    return (
        f'=IF({score_cell}="","",'
        f'IF({score_cell}>=15,"Critical",'
        f'IF({score_cell}>=10,"High",'
        f'IF({score_cell}>=5,"Medium","Low"))))'
    )


# ─────────────────────────────────────────────────────────────
# Risk register
# ─────────────────────────────────────────────────────────────
REGISTER_HEADERS = [
    "Risk ID", "Risk Title", "Threat Source", "Asset / Process",
    "Likelihood (1-5)", "Impact (1-5)", "Inherent Risk", "Inherent Rating",
    "Existing Controls", "Control Effectiveness (%)", "Residual Risk",
    "Residual Rating", "Risk Owner", "Treatment", "Treatment Plan",
    "Target Date", "Status", "ALE (FAIR, $)", "NIST CSF 2.0 Ref", "OSFI Ref",
]
REGISTER_WIDTHS = [
    10, 30, 20, 24, 10, 9, 11, 14, 42, 13, 11, 14, 24, 12, 42, 12, 13, 15, 24, 42,
]

TREATMENTS = ["Accept", "Mitigate", "Transfer", "Avoid"]
STATUSES   = ["Open", "In Progress", "Monitoring", "Closed"]

# Scenario detail the register needs but the FAIR model does not carry
SCENARIO_REGISTER_DETAIL = {
    "data_breach": {
        "threat_source": "External attacker / insider",
        "asset":         "Customer PII store, core banking database",
        "owner":         "Head of Data Protection",
    },
    "ransomware": {
        "threat_source": "Organised cybercrime",
        "asset":         "Core banking platform, payment processing",
        "owner":         "Head of Security Engineering",
    },
    "insider_threat": {
        "threat_source": "Employee or contractor",
        "asset":         "Privileged access to transaction systems",
        "owner":         "Head of Identity and Access Management",
    },
    "vendor_failure": {
        "threat_source": "Third-party service provider",
        "asset":         "Outsourced services and shared data",
        "owner":         "Head of Third-Party Risk",
    },
    "cloud_misconfiguration": {
        "threat_source": "Internal misconfiguration",
        "asset":         "Cloud storage, IAM policies, public APIs",
        "owner":         "Head of Cloud Platform",
    },
}


def likelihood_band(avg_freq):
    """Maps the FAIR annual event rate onto the register's 1-5 scale."""
    for threshold, score in ((0.5, 1), (1.0, 2), (2.0, 3), (3.0, 4)):
        if avg_freq < threshold:
            return score
    return 5


def impact_band(loss_high):
    """Maps the FAIR worst-case single-event loss onto the register's 1-5 scale."""
    for threshold, score in ((1_000_000, 1), (3_000_000, 2),
                             (6_000_000, 3), (10_000_000, 4)):
        if loss_high < threshold:
            return score
    return 5


def build_register_rows():
    """One example row per FAIR scenario, with ALE read from the database."""
    ale_by_name = {r["scenario_name"]: r for r in get_latest_scenario_run()}
    target      = date.today() + timedelta(days=180)

    rows = []
    for i, (key, sc) in enumerate(SCENARIOS.items(), start=1):
        detail   = SCENARIO_REGISTER_DETAIL[key]
        avg_freq = (sc["freq_low"] + sc["freq_high"]) / 2
        stored   = ale_by_name.get(sc["name"])
        rows.append({
            "id":            f"R-{i:03d}",
            "title":         sc["name"],
            "threat":        detail["threat_source"],
            "asset":         detail["asset"],
            "likelihood":    likelihood_band(avg_freq),
            "impact":        impact_band(sc["loss_high"]),
            "controls":      "; ".join(sc["controls"]),
            "effectiveness": sc["control_effectiveness"],
            "owner":         detail["owner"],
            "treatment":     "Mitigate",
            "plan":          f"Fund the control set at "
                             f"${sc['control_cost']:,.0f}/year. Reassess after "
                             f"implementation.",
            "target":        target.isoformat(),
            "status":        "In Progress",
            "ale":           round(stored["ale"], 0) if stored else None,
            "nist":          sc["nist_ref"],
            "osfi":          sc["osfi_ref"],
        })
    return rows


def build_risk_register():
    wb = Workbook()
    ws = wb.active
    ws.title = "Risk Register"

    write_header(ws, REGISTER_HEADERS, REGISTER_WIDTHS)

    rows       = build_register_rows()
    first_row  = 2
    last_filled = first_row + len(rows) - 1
    last_row   = last_filled + BLANK_ROWS

    for offset, r in enumerate(rows):
        row = first_row + offset
        ws.cell(row=row, column=1,  value=r["id"])
        ws.cell(row=row, column=2,  value=r["title"])
        ws.cell(row=row, column=3,  value=r["threat"])
        ws.cell(row=row, column=4,  value=r["asset"])
        ws.cell(row=row, column=5,  value=r["likelihood"])
        ws.cell(row=row, column=6,  value=r["impact"])
        ws.cell(row=row, column=9,  value=r["controls"])
        ws.cell(row=row, column=10, value=r["effectiveness"])
        ws.cell(row=row, column=13, value=r["owner"])
        ws.cell(row=row, column=14, value=r["treatment"])
        ws.cell(row=row, column=15, value=r["plan"])
        ws.cell(row=row, column=16, value=r["target"])
        ws.cell(row=row, column=17, value=r["status"])
        ws.cell(row=row, column=18, value=r["ale"])
        ws.cell(row=row, column=19, value=r["nist"])
        ws.cell(row=row, column=20, value=r["osfi"])

    # Formulas go in every row, filled and blank alike, so a new entry scores
    # itself as soon as likelihood and impact are typed in.
    for row in range(first_row, last_row + 1):
        ws.cell(row=row, column=7,
                value=f'=IF(OR(E{row}="",F{row}=""),"",E{row}*F{row})')
        ws.cell(row=row, column=8,  value=rating_formula(f"G{row}"))
        ws.cell(row=row, column=11,
                value=f'=IF(OR(G{row}="",J{row}=""),"",ROUND(G{row}*(1-J{row}),1))')
        ws.cell(row=row, column=12, value=rating_formula(f"K{row}"))

    style_body(ws, first_row, last_row, len(REGISTER_HEADERS),
               wrap_cols={2, 3, 4, 9, 15, 19, 20})

    # Number formats
    for row in range(first_row, last_row + 1):
        ws.cell(row=row, column=10).number_format = "0%"
        ws.cell(row=row, column=18).number_format = '"$"#,##0'
        ws.cell(row=row, column=7).number_format  = "0"
        ws.cell(row=row, column=11).number_format = "0.0"
        for col in (5, 6, 7, 8, 10, 11, 12, 16, 17):
            ws.cell(row=row, column=col).alignment = Alignment(
                horizontal="center", vertical="top")

    # Dropdowns and bounded inputs
    for col in ("E", "F"):
        dv = DataValidation(type="whole", operator="between",
                            formula1="1", formula2="5", allow_blank=True,
                            errorTitle="1 to 5 only",
                            error="Enter a whole number between 1 and 5.")
        ws.add_data_validation(dv)
        dv.add(f"{col}{first_row}:{col}{last_row}")

    dv_pct = DataValidation(type="decimal", operator="between",
                            formula1="0", formula2="1", allow_blank=True,
                            errorTitle="0% to 100%",
                            error="Enter a percentage between 0% and 100%.")
    ws.add_data_validation(dv_pct)
    dv_pct.add(f"J{first_row}:J{last_row}")

    add_list_validation(ws, "N", TREATMENTS, first_row, last_row,
                        "Accept, Mitigate, Transfer or Avoid")
    add_list_validation(ws, "Q", STATUSES, first_row, last_row,
                        "Open, In Progress, Monitoring or Closed")

    add_rating_formatting(ws, "H", first_row, last_row, RATING_FILLS)
    add_rating_formatting(ws, "L", first_row, last_row, RATING_FILLS)

    build_register_instructions(wb)
    path = os.path.join(TEMPLATES_DIR, "risk_register.xlsx")
    wb.save(path)
    return path, len(rows), last_row - last_filled


def build_register_instructions(wb):
    ws = wb.create_sheet("Instructions")
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 96

    ws["A1"] = "Risk Register — how to use it"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = ("First National Bank (Fictional). The five filled rows are the FAIR "
                "scenarios from this project; their ALE figures are read from the "
                "database, not typed in. Overwrite them with your own risks.")
    ws["A2"].font = NOTE_FONT
    ws.merge_cells("A2:B2")

    row = 4
    ws.cell(row=row, column=1, value="Column").font = HEAD_FONT
    ws.cell(row=row, column=1).fill = HEAD_FILL
    ws.cell(row=row, column=2, value="What goes in it").font = HEAD_FONT
    ws.cell(row=row, column=2).fill = HEAD_FILL

    guide = [
        ("Risk ID", "Unique identifier, e.g. R-001. Never reuse an ID after a risk closes."),
        ("Risk Title", "One line naming the risk event, not the control gap."),
        ("Threat Source", "Who or what causes it: external attacker, insider, third party, process failure."),
        ("Asset / Process", "The business asset or process exposed. Ties the risk to something the business recognises."),
        ("Likelihood (1-5)", "How often you expect the event. 1 = rare (less than once in 5 years), 3 = annual, 5 = several times a year."),
        ("Impact (1-5)", "Worst plausible single-event loss. 1 = under $1M, 3 = $3-6M, 5 = over $10M."),
        ("Inherent Risk", "FORMULA: Likelihood x Impact, 1 to 25. Risk before controls. Do not overwrite."),
        ("Inherent Rating", "FORMULA: 15+ Critical, 10-14 High, 5-9 Medium, under 5 Low. Do not overwrite."),
        ("Existing Controls", "Controls already operating, not planned ones. Planned controls belong in the Treatment Plan."),
        ("Control Effectiveness (%)", "Share of the risk the existing controls remove. An assumption — justify it from control testing results where you have them."),
        ("Residual Risk", "FORMULA: Inherent Risk x (1 - Control Effectiveness). Risk remaining after controls. Do not overwrite."),
        ("Residual Rating", "FORMULA: same thresholds as Inherent Rating, applied to Residual Risk. This is the number that drives escalation. Note that a 60-80% effectiveness assumption pulls almost any inherent score below 5, so every example row rates Low residual. If that looks too comfortable, the effectiveness assumption is the number to challenge, not the formula."),
        ("Risk Owner", "A named accountable role. A risk without an owner does not get treated."),
        ("Treatment", "Accept, Mitigate, Transfer or Avoid. Accept requires sign-off at the level matching the residual rating."),
        ("Treatment Plan", "What will be done, by whom. Specific enough to track."),
        ("Target Date", "When the treatment completes. Blank means nobody is accountable for a date."),
        ("Status", "Open, In Progress, Monitoring or Closed."),
        ("ALE (FAIR, $)", "Annualised Loss Expectancy from the FAIR model, where one exists. Gives the board a dollar figure next to the 1-5 score."),
        ("NIST CSF 2.0 Ref", "The CSF 2.0 subcategory the treating controls map to, e.g. PR.AA-01."),
        ("OSFI Ref", "The OSFI guideline and topic the risk touches, e.g. B-13 Cyber Security."),
    ]
    for i, (col_name, description) in enumerate(guide, start=row + 1):
        ws.cell(row=i, column=1, value=col_name).font = Font(bold=True, size=10)
        ws.cell(row=i, column=2, value=description).font = Font(size=10)
        ws.cell(row=i, column=1).border = BORDER
        ws.cell(row=i, column=2).border = BORDER
        ws.cell(row=i, column=2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(row=i, column=1).alignment = Alignment(vertical="top")

    scale_row = row + len(guide) + 3
    ws.cell(row=scale_row, column=1, value="Rating scale").font = TITLE_FONT
    scale = [
        ("Critical (15-25)", "Escalate to the Operational Risk Committee. Treatment plan required within 30 days."),
        ("High (10-14)",     "Executive owner required. Treatment plan required within 90 days."),
        ("Medium (5-9)",     "Managed within the business line. Reviewed quarterly."),
        ("Low (1-4)",        "Accept and monitor. Reviewed annually."),
    ]
    for i, (band, action) in enumerate(scale, start=scale_row + 1):
        ws.cell(row=i, column=1, value=band).font = Font(bold=True, size=10)
        ws.cell(row=i, column=2, value=action).font = Font(size=10)
        ws.cell(row=i, column=1).fill = RATING_FILLS[band.split(" (")[0]]
        ws.cell(row=i, column=1).border = BORDER
        ws.cell(row=i, column=2).border = BORDER


# ─────────────────────────────────────────────────────────────
# Control matrix
# ─────────────────────────────────────────────────────────────
MATRIX_HEADERS = [
    "Control ID", "Control Description", "NIST CSF 2.0 Function",
    "NIST CSF 2.0 ID", "ISO 27001:2022 Control", "SOC 2 TSC",
    "OSFI Guideline", "Control Owner", "Test Frequency", "Last Tested",
    "Test Result", "Evidence Link",
]
MATRIX_WIDTHS = [11, 52, 18, 15, 20, 11, 40, 30, 14, 12, 19, 26]

TEST_RESULTS = ["Effective", "Partially Effective", "Ineffective", "Not Tested"]

FUNCTION_OWNERS = {
    "Govern":   "Chief Information Security Officer",
    "Identify": "Head of IT Asset Management",
    "Protect":  "Head of Security Engineering",
    "Detect":   "Security Operations Centre Manager",
    "Respond":  "Incident Response Lead",
    "Recover":  "Head of Business Continuity",
}


def result_from_maturity(score):
    """
    Seeds Test Result from the CSF maturity score for that function.

    A function scoring 3 or above is documented and followed, so its controls
    are recorded as tested and effective. A 2 is inconsistent — partially
    effective. A 1 has nothing to test yet.
    """
    if score is None:
        return "Not Tested"
    if score >= 3:
        return "Effective"
    if score == 2:
        return "Partially Effective"
    return "Not Tested"


def get_function_scores():
    """Latest CSF score per function, used to seed the test results."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT function_name, score FROM function_scores
        WHERE assessment_id = (SELECT MAX(id) FROM assessments)
    """).fetchall()
    conn.close()
    return {r["function_name"]: r["score"] for r in rows}


def build_control_matrix():
    wb = Workbook()
    ws = wb.active
    ws.title = "Control Matrix"

    write_header(ws, MATRIX_HEADERS, MATRIX_WIDTHS)

    scores     = get_function_scores()
    first_row  = 2
    last_row   = first_row + len(CONTROL_MAPPING) - 1
    tested_on  = date.today().replace(day=1).isoformat()

    for offset, c in enumerate(CONTROL_MAPPING):
        row    = first_row + offset
        result = result_from_maturity(scores.get(c["csf_function"]))
        ws.cell(row=row, column=1,  value=f"FNB-C-{offset + 1:02d}")
        ws.cell(row=row, column=2,  value=c["csf_description"])
        ws.cell(row=row, column=3,  value=c["csf_function"])
        ws.cell(row=row, column=4,  value=c["csf_ref"])
        ws.cell(row=row, column=5,  value=c["iso_ref"])
        ws.cell(row=row, column=6,  value=c["soc2_ref"])
        ws.cell(row=row, column=7,  value=c["osfi_ref"])
        ws.cell(row=row, column=8,  value=FUNCTION_OWNERS[c["csf_function"]])
        ws.cell(row=row, column=9,  value=c["test_frequency"])
        ws.cell(row=row, column=10, value="" if result == "Not Tested" else tested_on)
        ws.cell(row=row, column=11, value=result)
        ws.cell(row=row, column=12, value="")

    style_body(ws, first_row, last_row, len(MATRIX_HEADERS),
               wrap_cols={2, 5, 7, 8})
    for row in range(first_row, last_row + 1):
        for col in (3, 4, 6, 9, 10, 11):
            ws.cell(row=row, column=col).alignment = Alignment(
                horizontal="center", vertical="top")

    add_list_validation(ws, "K", TEST_RESULTS, first_row, last_row,
                        "Effective, Partially Effective, Ineffective or Not Tested")
    add_rating_formatting(ws, "K", first_row, last_row, RESULT_FILLS)

    build_matrix_summary(wb, first_row, last_row)
    path = os.path.join(TEMPLATES_DIR, "control_matrix.xlsx")
    wb.save(path)
    return path, len(CONTROL_MAPPING)


def build_matrix_summary(wb, first_row, last_row):
    """Summary counts, driven by COUNTIF against the Control Matrix sheet."""
    ws = wb.create_sheet("Summary", 0)
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 14
    ws.column_dimensions["E"].width = 14
    ws.column_dimensions["F"].width = 14

    fn_range     = f"'Control Matrix'!$C${first_row}:$C${last_row}"
    result_range = f"'Control Matrix'!$K${first_row}:$K${last_row}"

    ws["A1"] = "Control Matrix — Summary"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = ("Counts recalculate from the Control Matrix sheet. Test results are "
                "seeded from the NIST CSF maturity score for each function and are "
                "illustrative — replace them as controls are actually tested.")
    ws["A2"].font = NOTE_FONT
    ws.merge_cells("A2:F2")

    # ── Controls by function and test result ─────────────────
    head_row = 4
    headers  = ["NIST CSF 2.0 Function", "Controls"] + TEST_RESULTS
    for i, title in enumerate(headers, start=1):
        cell = ws.cell(row=head_row, column=i, value=title)
        cell.font = HEAD_FONT
        cell.fill = HEAD_FILL
        cell.border = BORDER
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
    ws.row_dimensions[head_row].height = 28

    for i, func in enumerate(CSF_FUNCTIONS, start=head_row + 1):
        ws.cell(row=i, column=1, value=func).font = Font(size=10, bold=True)
        ws.cell(row=i, column=2,
                value=f'=COUNTIF({fn_range},A{i})')
        for j, result in enumerate(TEST_RESULTS, start=3):
            ws.cell(row=i, column=j, value=(
                f'=COUNTIFS({fn_range},$A{i},{result_range},'
                f'{get_column_letter(j)}${head_row})'
            ))
        for col in range(1, len(headers) + 1):
            ws.cell(row=i, column=col).border = BORDER
            if col > 1:
                ws.cell(row=i, column=col).alignment = Alignment(horizontal="center")

    total_row = head_row + len(CSF_FUNCTIONS) + 1
    ws.cell(row=total_row, column=1, value="Total").font = Font(size=10, bold=True)
    for col in range(2, len(headers) + 1):
        letter = get_column_letter(col)
        cell = ws.cell(row=total_row, column=col, value=(
            f'=SUM({letter}{head_row + 1}:{letter}{total_row - 1})'
        ))
        cell.font = Font(size=10, bold=True)
        cell.alignment = Alignment(horizontal="center")
    for col in range(1, len(headers) + 1):
        ws.cell(row=total_row, column=col).border = BORDER
        ws.cell(row=total_row, column=col).fill = PatternFill(
            "solid", fgColor=ACCENT_PALE)

    # ── Coverage by test result, with a percentage ───────────
    cov_row = total_row + 3
    ws.cell(row=cov_row, column=1, value="Test result").font = HEAD_FONT
    ws.cell(row=cov_row, column=1).fill = HEAD_FILL
    ws.cell(row=cov_row, column=2, value="Controls").font = HEAD_FONT
    ws.cell(row=cov_row, column=2).fill = HEAD_FILL
    ws.cell(row=cov_row, column=3, value="% of total").font = HEAD_FONT
    ws.cell(row=cov_row, column=3).fill = HEAD_FILL

    for i, result in enumerate(TEST_RESULTS, start=cov_row + 1):
        ws.cell(row=i, column=1, value=result).font = Font(size=10)
        ws.cell(row=i, column=1).fill = RESULT_FILLS[result]
        ws.cell(row=i, column=2, value=f'=COUNTIF({result_range},A{i})')
        ws.cell(row=i, column=3,
                value=f'=IF($B${total_row}=0,0,B{i}/$B${total_row})')
        ws.cell(row=i, column=3).number_format = "0%"
        for col in (1, 2, 3):
            ws.cell(row=i, column=col).border = BORDER
            if col > 1:
                ws.cell(row=i, column=col).alignment = Alignment(horizontal="center")


# ─────────────────────────────────────────────────────────────
def build_all():
    initialise_database(verbose=False)

    print("\n" + "=" * 62)
    print("  BUILDING EXCEL TEMPLATES")
    print("=" * 62 + "\n")

    reg_path, filled, blanks = build_risk_register()
    print(f"  ✅ templates/risk_register.xlsx")
    print(f"     {filled} example rows from the FAIR scenarios "
          f"(ALE read from the database) + {blanks} blank formatted rows")
    print(f"     Formulas: Inherent Risk, Inherent Rating, Residual Risk, "
          f"Residual Rating")

    mat_path, n_controls = build_control_matrix()
    print(f"\n  ✅ templates/control_matrix.xlsx")
    print(f"     {n_controls} controls from framework_mapper.CONTROL_MAPPING")
    print(f"     Summary sheet counts per function and per test result")

    print(f"\n{'=' * 62}\n")
    return reg_path, mat_path


if __name__ == "__main__":
    build_all()
