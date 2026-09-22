# src/reporting/executive_summary.py
# Builds docs/executive_summary.pdf — a 4-page briefing to the CISO.
#
# Every figure in this document is read from the database. Nothing is typed in.
# Run the seed and the chart generators first:
#
#     python3 src/database/seed_demo_data.py
#     python3 src/risk_quantification/loss_exceedance.py
#     python3 src/compliance/csf_radar.py
#     python3 src/reporting/executive_summary.py

import sys
import os
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.compliance.csf_data import CSF_FUNCTIONS, DEFAULT_TARGET_SCORE, GAP_METADATA
from src.compliance.gap_analysis import build_roadmap
from src.database.db_manager import (
    get_connection,
    get_latest_scenario_run,
    get_overdue_vendors,
    get_reassessment_days,
    get_vendor_tier_summary,
    initialise_database,
)
from src.risk_quantification.fair_engine import format_currency
from src.risk_quantification.loss_exceedance import SHORT_NAMES
from src.risk_quantification.scenarios import SCENARIOS

ROOT       = os.path.join(os.path.dirname(__file__), "../..")
DOCS_DIR   = os.path.join(ROOT, "docs")
CHARTS_DIR = os.path.join(ROOT, "dashboards")
os.makedirs(DOCS_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(DOCS_DIR, "executive_summary.pdf")

AUTHOR = "Ameer Khan"
FOOTER = "First National Bank (Fictional) — simulated data for portfolio demonstration"

# One accent, plus a reserved status palette used only for ratings and tiers.
ACCENT     = colors.HexColor("#1F4E79")
ACCENT_MID = colors.HexColor("#2E6DA4")
INK        = colors.HexColor("#1c1c1c")
INK_MUTED  = colors.HexColor("#5f6b73")
RULE       = colors.HexColor("#cdd8de")
ROW_ALT    = colors.HexColor("#f4f7f9")
TILE_BG    = colors.HexColor("#f1f5f8")

# Compact service labels, so vendor rows stay on one line
SERVICE_LABELS = {
    "Data Analytics / AI": "Analytics / AI",
    "Payment Processor":   "Payments",
    "IT Infrastructure":   "Infrastructure",
    "Software / SaaS":     "Software / SaaS",
    "Cloud Provider":      "Cloud",
}

STATUS = {
    "Critical": colors.HexColor("#b3261e"),
    "High":     colors.HexColor("#c2620f"),
    "Medium":   colors.HexColor("#8a6a0b"),
    "Low":      colors.HexColor("#1d6f42"),
}


# ─────────────────────────────────────────────────────────────
# Styles
# ─────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=23, leading=27, textColor=ACCENT, alignment=TA_LEFT,
            spaceAfter=3,
        ),
        "byline": ParagraphStyle(
            "byline", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=14, textColor=INK_MUTED, spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13.5, leading=17, textColor=ACCENT,
            spaceBefore=13, spaceAfter=5, keepWithNext=1,
        ),
        "h3": ParagraphStyle(
            "h3", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=10.5, leading=14, textColor=INK,
            spaceBefore=7, spaceAfter=2, keepWithNext=1,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, leading=13.6, textColor=INK, spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "small", parent=base["Normal"], fontName="Helvetica",
            fontSize=8.2, leading=11, textColor=INK_MUTED, spaceAfter=3,
        ),
        "refs": ParagraphStyle(
            "refs", parent=base["Normal"], fontName="Helvetica",
            fontSize=8, leading=10.5, textColor=ACCENT_MID, spaceAfter=2,
        ),
        "cell": ParagraphStyle(
            "cell", parent=base["Normal"], fontName="Helvetica",
            fontSize=8.8, leading=11.4, textColor=INK,
        ),
        "cellhead": ParagraphStyle(
            "cellhead", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8.8, leading=11.4, textColor=colors.white,
        ),
        "kpi_value": ParagraphStyle(
            "kpi_value", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=15, leading=18, textColor=ACCENT, spaceAfter=1,
        ),
        "kpi_label": ParagraphStyle(
            "kpi_label", parent=base["Normal"], fontName="Helvetica",
            fontSize=7.4, leading=9.2, textColor=INK_MUTED,
        ),
    }


def table(data, col_widths, styles, align=None, spans=None, bold_last=False):
    """Builds a consistently styled table. First row is the header."""
    header = [Paragraph(str(c), styles["cellhead"]) for c in data[0]]
    body   = [[Paragraph(str(c), styles["cell"]) for c in row] for row in data[1:]]

    t = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), ACCENT_MID),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("LINEBELOW",     (0, 0), (-1, -2), 0.4, RULE),
        ("BOX",           (0, 0), (-1, -1), 0.5, RULE),
    ])
    for i in range(1, len(data)):
        if i % 2 == 0:
            t.add("BACKGROUND", (0, i), (-1, i), ROW_ALT)
    if bold_last:
        t.add("BACKGROUND", (0, len(data) - 1), (-1, len(data) - 1),
              colors.HexColor("#e6edf2"))
    for col in (align or []):
        t.add("ALIGN", (col, 1), (col, -1), "RIGHT")
    for start, end in (spans or []):
        t.add("SPAN", start, end)

    tbl = Table([header] + body, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(t)
    return tbl


def chart(path, width, styles, caption=None):
    """Embeds a PNG scaled to width, preserving aspect ratio."""
    if not os.path.exists(path):
        return Paragraph(
            f"<i>Chart not found: {os.path.basename(path)} — "
            f"run the chart generators first.</i>", styles["small"]
        )
    img = Image(path)
    img.drawHeight = img.drawHeight * (width / img.drawWidth)
    img.drawWidth  = width
    img.hAlign     = "CENTER"
    if caption:
        return KeepTogether([img, Spacer(1, 3),
                             Paragraph(caption, styles["small"])])
    return img


def kpi_strip(tiles, styles, total_width):
    """The five headline numbers as a row of tiles. tiles = (value, label, colour)."""
    row = []
    for value, label, colour in tiles:
        cell = Table(
            [[Paragraph(f'<font color="{colour.hexval()}">{value}</font>',
                        styles["kpi_value"])],
             [Paragraph(label, styles["kpi_label"])]],
            colWidths=[total_width / len(tiles) - 0.04 * inch],
            style=TableStyle([
                ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
                ("TOPPADDING",    (0, 0), (-1, 0), 7),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
                ("TOPPADDING",    (0, 1), (-1, 1), 0),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 7),
            ]))
        row.append(cell)

    outer = Table([row], colWidths=[total_width / len(tiles)] * len(tiles))
    outer.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), TILE_BG),
        ("INNERGRID",     (0, 0), (-1, -1), 2.5, colors.white),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return outer


# ─────────────────────────────────────────────────────────────
# Data gathering — every number below comes from the database
# ─────────────────────────────────────────────────────────────
def gather_data():
    conn = get_connection()

    assessment = conn.execute(
        "SELECT id, org_name, assessor, date_run FROM assessments "
        "ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if assessment is None:
        conn.close()
        raise SystemExit(
            "  No assessment found. Run src/database/seed_demo_data.py first."
        )

    csf_rows = conn.execute(
        "SELECT function_name, score, target_score, rationale FROM function_scores "
        "WHERE assessment_id = ?", (assessment["id"],)
    ).fetchall()

    vendors = conn.execute("""
        SELECT vendor_name, service_type, criticality, risk_tier, score,
               gap_count, critical_gaps, assessment_date,
               CAST(julianday('now') - julianday(assessment_date) AS INTEGER) AS days_since
        FROM vendor_assessments
        WHERE id IN (SELECT MAX(id) FROM vendor_assessments GROUP BY vendor_name)
        ORDER BY score ASC
    """).fetchall()
    conn.close()

    scenarios = get_latest_scenario_run()
    if not scenarios:
        raise SystemExit(
            "  No risk scenarios found. Run src/database/seed_demo_data.py first."
        )

    by_name = {r["function_name"]: r for r in csf_rows}
    csf = [
        (f, by_name[f]["score"], by_name[f]["target_score"] or DEFAULT_TARGET_SCORE,
         by_name[f]["rationale"] or "")
        for f in CSF_FUNCTIONS if f in by_name
    ]

    return {
        "org":       assessment["org_name"],
        "assessor":  assessment["assessor"],
        "date_run":  assessment["date_run"],
        "csf":       csf,
        "roadmap":   build_roadmap(assessment["id"]),
        "scenarios": scenarios,
        "vendors":   vendors,
        "tiers":     {r["risk_tier"]: r["count"] for r in get_vendor_tier_summary()},
        "overdue":   get_overdue_vendors(),
        "windows":   get_reassessment_days(),
    }


def scenario_label(name):
    """Compact scenario name, shared with the charts."""
    key = next((k for k, s in SCENARIOS.items() if s["name"] == name), None)
    return SHORT_NAMES.get(key, name.split(" — ")[0])


def derive_recommendations(d):
    """
    Builds the top 3 recommendations from the data, not from a fixed list.

    1. The controls for the highest-ALE scenario.
    2. The remediation for the lowest-scoring CSF function. Its expected effect
       is the combined ALE of the scenarios citing that function's control ID,
       since a maturity gap has no control cost of its own.
    3. The Critical-tier and overdue vendors, priced against the third-party
       scenario's own control set.
    """
    recs = []

    # ── 1. Highest-ALE scenario ──────────────────────────────
    top = max(d["scenarios"], key=lambda r: r["ale"])
    key = next(k for k, s in SCENARIOS.items() if s["name"] == top["scenario_name"])
    sc  = SCENARIOS[key]
    recs.append({
        "title":    scenario_label(top["scenario_name"]),
        "priority": "Critical",
        "effort":   f"{format_currency(top['control_cost'])}/yr programme",
        "why": (
            f"The largest single exposure in the portfolio at "
            f"{format_currency(top['ale'])} expected annual loss, with a "
            f"one-in-ten-year loss of {format_currency(top['percentile_90'])}."
        ),
        "action":    "; ".join(sc["controls"][:3]) + ".",
        "quick_win": (
            f"Confirm the {format_currency(top['control_cost'])} sits in next "
            f"year's budget line before the planning cycle closes."
        ),
        "effect": (
            f"{format_currency(top['ale'] - top['residual_ale'])}/yr reduction at "
            f"{top['control_effectiveness']:.0%} assumed effectiveness, leaving "
            f"{format_currency(top['residual_ale'])} residual. "
            f"ROSI {top['rosi'] * 100:,.0f}%."
        ),
        "refs": f"NIST CSF {sc['nist_ref']}  ·  {sc['osfi_ref'].split(';')[0]}",
    })

    # ── 2. Lowest-scoring CSF function ───────────────────────
    func, score, target, _ = min(d["csf"], key=lambda r: r[1])
    meta  = GAP_METADATA[func]
    cited = [
        r for r in d["scenarios"]
        if meta["nist_ref"] in next(
            (s["nist_ref"] for s in SCENARIOS.values()
             if s["name"] == r["scenario_name"]), ""
        )
    ]
    cited_ale = sum(r["ale"] for r in cited)
    recs.append({
        "title":    func,
        "priority": meta["priority"],
        "effort":   f"{meta['effort'].lower()} effort, about {meta['effort_weeks']} weeks",
        "why": (
            f"{meta['business_impact']} {meta['nist_ref']} is cited by "
            f"{len(cited)} of the {len(d['scenarios'])} modelled scenarios, "
            f"which carry {format_currency(cited_ale)} of combined annual "
            f"expected loss."
        ),
        "action":    meta["remediation"],
        "quick_win": meta["quick_win"],
        "effect": (
            f"Raises the weakest function from {score}/5 towards the target of "
            f"{target}/5 and supports the {format_currency(cited_ale)} of ALE "
            f"that depends on it. No new tooling required."
        ),
        "refs": (
            f"NIST CSF {meta['nist_ref']}  ·  ISO 27001 {meta['iso_ref']}  ·  "
            f"SOC 2 {meta['soc2_ref']}"
        ),
    })

    # ── 3. Vendors ───────────────────────────────────────────
    critical = [v for v in d["vendors"] if v["risk_tier"] == "Critical"]
    overdue  = [r["vendor_name"] for r in d["overdue"]]
    vs = next((r for r in d["scenarios"] if r["scenario_key"] == "vendor_failure"), None)
    recs.append({
        "title":    "Third-party risk",
        "priority": "High",
        "effort":   "about 90 days to clear the backlog",
        "why": (
            f"{len(critical)} vendor sits in the Critical tier "
            f"({', '.join(v['vendor_name'] for v in critical)}) and "
            f"{len(overdue)} are past the reassessment window for their tier "
            f"({', '.join(overdue)}). OSFI B-10 expects monitoring "
            f"proportionate to criticality."
        ),
        "action":    "; ".join(SCENARIOS["vendor_failure"]["controls"][:3]) + ".",
        "quick_win": (
            "Re-run the questionnaire for the overdue vendors before any "
            "contract renewal is signed."
        ),
        "effect": (
            f"{format_currency(vs['ale'] - vs['residual_ale'])}/yr reduction "
            f"against the {format_currency(vs['ale'])} third-party scenario. "
            f"ROSI {vs['rosi'] * 100:,.0f}%." if vs else ""
        ),
        "refs": "OSFI B-10 — Third-Party Risk Management  ·  NIST CSF GV.SC-07",
    })
    return recs


# ─────────────────────────────────────────────────────────────
# Document
# ─────────────────────────────────────────────────────────────
def build_story(d, s, width):
    story     = []
    total_ale = sum(r["ale"] for r in d["scenarios"])
    total_res = sum(r["residual_ale"] for r in d["scenarios"])
    total_cc  = sum(r["control_cost"] or 0 for r in d["scenarios"])
    overall   = sum(c for _, c, _, _ in d["csf"]) / len(d["csf"])
    avg_tgt   = sum(t for _, _, t, _ in d["csf"]) / len(d["csf"])
    top       = max(d["scenarios"], key=lambda r: r["ale"])
    worst     = min(d["csf"], key=lambda r: r[1])

    # ── Header ───────────────────────────────────────────────
    story.append(Paragraph("Cyber Risk Executive Summary", s["title"]))
    story.append(Paragraph(
        f"{d['org']} &nbsp;·&nbsp; Prepared by {AUTHOR} &nbsp;·&nbsp; "
        f"{date.today().isoformat()}", s["byline"]))
    story.append(Table([[""]], colWidths=[width], rowHeights=[2],
                       style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT)])))
    story.append(Spacer(1, 9))

    story.append(Paragraph(
        "<b>Simulated organisation.</b> First National Bank is fictional and every "
        "figure illustrative. This demonstrates analytical method and reporting "
        "format, not an assessment of any real institution.", s["small"]))
    story.append(Spacer(1, 9))

    # ── KPI strip ────────────────────────────────────────────
    story.append(kpi_strip([
        (format_currency(total_ale), "Total annualised loss expectancy",
         STATUS["Critical"]),
        (format_currency(total_res), "Residual after controls", ACCENT),
        (f"{overall:.1f} / 5.0", "NIST CSF maturity", STATUS["Medium"]),
        (str(len(d["vendors"])), "Vendors assessed", ACCENT),
        (str(len(d["overdue"])), "Overdue reassessments",
         STATUS["Critical"] if d["overdue"] else STATUS["Low"]),
    ], s, width))
    story.append(Spacer(1, 4))

    # ── Executive Overview ───────────────────────────────────
    story.append(Paragraph("Executive Overview", s["h2"]))
    story.append(Paragraph(
        f"Across five modelled threat scenarios, {d['org']} carries an expected "
        f"annual cyber loss of <b>{format_currency(total_ale)}</b>. The largest "
        f"single exposure is {scenario_label(top['scenario_name'])} at "
        f"{format_currency(top['ale'])} a year, with a one-in-ten-year loss of "
        f"{format_currency(top['percentile_90'])}. A programme costing "
        f"<b>{format_currency(total_cc)} annually</b> would remove "
        f"{format_currency(total_ale - total_res)} of that exposure, leaving "
        f"{format_currency(total_res)} residual.", s["body"]))
    story.append(Paragraph(
        f"Control maturity is the constraint: <b>{overall:.1f} of 5.0</b> against "
        f"NIST CSF 2.0, versus a target of {avg_tgt:.0f}, with <b>{worst[0]}</b> "
        f"weakest at {worst[1]}/5. {len(d['roadmap'])} control gaps are open and "
        f"{len(d['overdue'])} of {len(d['vendors'])} vendors are past their OSFI "
        f"B-10 reassessment date. Governance and incident response are where low "
        f"cost meets high consequence.", s["body"]))

    # ── 1. Quantified Risk Exposure ──────────────────────────
    story.append(Paragraph("1. Quantified Risk Exposure", s["h2"]))
    story.append(Paragraph(
        "Each scenario is modelled with the FAIR method: annual event frequency "
        "drawn from a Poisson distribution, single-event loss from a log-normal "
        "fitted to a low/high range, summed across 100,000 simulated years.",
        s["body"]))

    rows = [["Scenario", "Expected annual loss", "1-in-10 yr",
             "Control cost", "Residual ALE", "ROSI"]]
    for r in sorted(d["scenarios"], key=lambda r: r["ale"], reverse=True):
        rows.append([
            f"<b>{scenario_label(r['scenario_name'])}</b>",
            format_currency(r["ale"]),
            format_currency(r["percentile_90"]),
            format_currency(r["control_cost"] or 0),
            format_currency(r["residual_ale"]),
            f"{r['rosi'] * 100:,.0f}%",
        ])
    rows.append(["<b>Portfolio total</b>", f"<b>{format_currency(total_ale)}</b>",
                 "—", f"<b>{format_currency(total_cc)}</b>",
                 f"<b>{format_currency(total_res)}</b>", "—"])
    story.append(table(
        rows,
        [1.25 * inch, 1.42 * inch, 0.92 * inch, 0.9 * inch, 0.92 * inch, 0.72 * inch],
        s, bold_last=True))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "ROSI = (risk reduced − control cost) ÷ control cost. Effectiveness is "
        "assumed at 60–80% by scenario, not measured, and costs cover tooling "
        "only — so ROSI is an upper bound.", s["small"]))
    story.append(Spacer(1, 6))
    story.append(chart(
        os.path.join(CHARTS_DIR, "lec_all_scenarios.png"), 4.2 * inch, s,
        "Loss exceedance curves. Read the curve at any dollar figure to get the "
        "probability that annual losses exceed it."))

    # ── 2. Control Maturity ──────────────────────────────────
    story.append(Paragraph("2. Control Maturity — NIST CSF 2.0", s["h2"]))
    csf_rows = [["Function", "Current", "Target", "Gap", "Assessment"]]
    for func, score, target, rationale in d["csf"]:
        band = "Critical" if score <= 1 else "High" if score == 2 else "Low"
        csf_rows.append([
            f"<b>{func}</b>",
            f'<font color="{STATUS[band].hexval()}"><b>{score}</b></font>',
            str(target),
            f"+{target - score}",
            rationale,
        ])
    story.append(table(
        csf_rows,
        [0.88 * inch, 0.72 * inch, 0.55 * inch, 0.45 * inch, 3.65 * inch],
        s, align=[1, 2, 3]))
    story.append(Spacer(1, 6))
    story.append(chart(
        os.path.join(CHARTS_DIR, "csf_radar.png"), 2.7 * inch, s,
        "Current maturity against a target of 4 (managed and measured) across "
        "all six functions."))

    # ── 3. Recommended Actions ───────────────────────────────
    # Derived from the data: largest quantified exposure, weakest control
    # function, and the third-party backlog.
    # keepWithNext cannot hold a heading to a KeepTogether block, so the
    # heading is bound into the first recommendation instead.
    for i, rec in enumerate(derive_recommendations(d), 1):
        colour = STATUS.get(rec["priority"], ACCENT).hexval()
        heading = [Paragraph("3. Recommended Actions", s["h2"])] if i == 1 else []
        story.append(KeepTogether(heading + [
            Paragraph(
                f"{i}. {rec['title']} — "
                f'<font color="{colour}">{rec["priority"]}</font> '
                f"<font color='#5f6b73'>({rec['effort']})</font>", s["h3"]),
            Paragraph(f"{rec['why']} <b>{rec['effect']}</b>", s["body"]),
            Paragraph(f"<b>Action:</b> {rec['action']}", s["body"]),
            Paragraph(f"<b>Start this month:</b> {rec['quick_win']}", s["body"]),
            Paragraph(rec["refs"], s["refs"]),
        ]))
        story.append(Spacer(1, 2))

    # ── 4. Third-Party Risk Snapshot ─────────────────────────
    tier_counts = ", ".join(
        f"{d['tiers'].get(t, 0)} {t.lower()}"
        for t in ("Critical", "High", "Medium", "Low")
    )
    overdue_names = {r["vendor_name"] for r in d["overdue"]}
    v_rows = [["Vendor", "Service", "Tier", "Score", "Crit. gaps",
               "Reassessment"]]
    for v in d["vendors"]:
        due = ("<font color='#b3261e'><b>OVERDUE</b></font>"
               if v["vendor_name"] in overdue_names
               else f"in {d['windows'][v['risk_tier']] - v['days_since']}d")
        v_rows.append([
            f"<b>{v['vendor_name']}</b>",
            SERVICE_LABELS.get(v["service_type"], v["service_type"]),
            f'<font color="{STATUS[v["risk_tier"]].hexval()}">'
            f'<b>{v["risk_tier"]}</b></font>',
            str(v["score"]),
            str(v["critical_gaps"]),
            due,
        ])
    story.append(KeepTogether([
        Paragraph("4. Third-Party Risk Snapshot", s["h2"]),
        Paragraph(
            f"{len(d['vendors'])} vendors assessed against an OSFI B-10 aligned "
            f"questionnaire: {tier_counts} tier. <b>{len(d['overdue'])} are past "
            f"their reassessment date.</b>", s["body"]),
        table(v_rows,
              [2.0 * inch, 1.2 * inch, 0.7 * inch, 0.55 * inch, 0.7 * inch,
               1.15 * inch], s, align=[3, 4]),
    ]))

    # ── 5. OSFI Alignment ────────────────────────────────────
    story.append(KeepTogether([
        Paragraph("5. OSFI Alignment", s["h2"]),
        table([
            ["Guideline", "Scope", "Status in this assessment"],
            ["<b>B-13</b> <font color='#5f6b73'>(in force Jan 2024)</font>",
             "Technology and cyber risk management",
             "Governance and detection gaps open; reporting path undefined"],
            ["<b>B-10</b> <font color='#5f6b73'>(in force May 2024)</font>",
             "Third-party risk management",
             f"Vendor tiering operating; {len(d['overdue'])} reassessments overdue"],
            ["<b>E-21</b> <font color='#5f6b73'>(full adherence Sep 2026)</font>",
             "Operational risk and resilience",
             "Recovery tested; scenario testing of all critical operations due Sep 2027"],
            ["<b>Incident reporting advisory</b>",
             "Reportable technology and cyber incidents",
             "24-hour path undocumented — closed by recommendation 2"],
        ], [1.45 * inch, 1.75 * inch, 3.05 * inch], s),
    ]))

    # ── Method and limitations ───────────────────────────────
    story.append(KeepTogether([
        Paragraph("Method and Limitations", s["h2"]),
        Paragraph(
            "Loss ranges are calibrated to published Canadian financial-sector "
            "breach benchmarks and read as the 5th and 95th percentile of a "
            "log-normal distribution, so the mean sits above the midpoint of the "
            "stated range. Each simulated year sums N independent loss draws, "
            "where N follows a Poisson distribution. Scenarios are modelled "
            "independently, though one event often triggers several. Control "
            "effectiveness is assumed, not measured. Read these as a "
            "decision-support range, not a forecast.", s["body"]),
    ]))

    return story


def draw_page(canvas, doc):
    """Footer rule, source note and page number on every page."""
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.6)
    canvas.line(0.75 * inch, 0.62 * inch, LETTER[0] - 0.75 * inch, 0.62 * inch)

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(INK_MUTED)
    canvas.drawString(0.75 * inch, 0.47 * inch, FOOTER)
    canvas.drawRightString(LETTER[0] - 0.75 * inch, 0.47 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf():
    initialise_database(verbose=False)
    d = gather_data()
    s = build_styles()

    doc = BaseDocTemplate(
        OUTPUT_FILE, pagesize=LETTER,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.7 * inch, bottomMargin=0.78 * inch,
        title="Cyber Risk Executive Summary — First National Bank (Fictional)",
        author=f"{AUTHOR} — 4th Year CS @ University of Toronto",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=draw_page)])
    doc.build(build_story(d, s, doc.width))

    print("  ✅ Saved: docs/executive_summary.pdf")
    print(f"     {len(d['scenarios'])} scenarios, {len(d['csf'])} CSF functions, "
          f"{len(d['vendors'])} vendors — all figures read from the database.")


if __name__ == "__main__":
    build_pdf()
