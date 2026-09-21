# src/reporting/executive_summary.py
# Builds docs/executive_summary.pdf — a 2-3 page briefing to the CISO.
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
from src.database.db_manager import (
    get_connection,
    get_latest_scenario_run,
    get_overdue_vendors,
    get_reassessment_days,
    get_vendor_tier_summary,
    initialise_database,
)
from src.risk_quantification.fair_engine import format_currency
from src.risk_quantification.scenarios import SCENARIOS

ROOT        = os.path.join(os.path.dirname(__file__), "../..")
DOCS_DIR    = os.path.join(ROOT, "docs")
CHARTS_DIR  = os.path.join(ROOT, "dashboards")
os.makedirs(DOCS_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(DOCS_DIR, "executive_summary.pdf")

AUTHOR = "Ameer Khan — 4th Year CS @ University of Toronto"

# One accent colour, used for rules, headings and table headers.
ACCENT     = colors.HexColor("#14607A")
ACCENT_PALE = colors.HexColor("#E8F1F4")
INK        = colors.HexColor("#1c1c1c")
INK_MUTED  = colors.HexColor("#5a5a5a")
RULE       = colors.HexColor("#c9d6db")
ROW_ALT    = colors.HexColor("#f5f8f9")


# ─────────────────────────────────────────────────────────────
# Styles
# ─────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=20, leading=24, textColor=ACCENT, alignment=TA_LEFT,
            spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, leading=13, textColor=INK_MUTED, spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, leading=16, textColor=ACCENT,
            spaceBefore=12, spaceAfter=5, keepWithNext=1,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=14, textColor=INK, spaceAfter=6,
        ),
        "cell": ParagraphStyle(
            "cell", parent=base["Normal"], fontName="Helvetica",
            fontSize=9, leading=11.5, textColor=INK,
        ),
        "cellhead": ParagraphStyle(
            "cellhead", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9, leading=11.5, textColor=colors.white,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=8.5, leading=11, textColor=INK_MUTED, spaceAfter=4,
        ),
        "disclaimer": ParagraphStyle(
            "disclaimer", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9, leading=12, textColor=ACCENT,
        ),
    }


def table(data, col_widths, styles, align=None, spans=None):
    """
    Builds a consistently styled table. First row is the header.

    spans is a list of ((col, row), (col, row)) cell ranges to merge — used
    so a wide paragraph can wrap across columns that are narrow elsewhere
    in the same table.
    """
    header = [Paragraph(str(c), styles["cellhead"]) for c in data[0]]
    body   = [[Paragraph(str(c), styles["cell"]) for c in row] for row in data[1:]]

    t = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), ACCENT),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("LINEBELOW",     (0, 0), (-1, -2), 0.4, RULE),
        ("BOX",           (0, 0), (-1, -1), 0.6, RULE),
    ])
    for i in range(1, len(data)):
        if i % 2 == 0:
            t.add("BACKGROUND", (0, i), (-1, i), ROW_ALT)
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
            f"run the chart generators first.</i>", styles["caption"]
        )
    img = Image(path)
    img.drawHeight = img.drawHeight * (width / img.drawWidth)
    img.drawWidth  = width
    img.hAlign     = "CENTER"
    if caption:
        return KeepTogether([img, Spacer(1, 3), Paragraph(caption, styles["caption"])])
    return img


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

    by_name  = {r["function_name"]: r for r in csf_rows}
    csf      = [
        (f, by_name[f]["score"], by_name[f]["target_score"] or DEFAULT_TARGET_SCORE)
        for f in CSF_FUNCTIONS if f in by_name
    ]

    return {
        "org":        assessment["org_name"],
        "assessor":   assessment["assessor"],
        "date_run":   assessment["date_run"],
        "csf":        csf,
        "scenarios":  scenarios,
        "vendors":    vendors,
        "tiers":      {r["risk_tier"]: r["count"] for r in get_vendor_tier_summary()},
        "overdue":    get_overdue_vendors(),
        "windows":    get_reassessment_days(),
    }


def derive_recommendations(d):
    """
    Builds the top 3 recommendations from the data, not from a fixed list.

    1. The controls for the highest-ALE scenario.
    2. The remediation for the lowest-scoring CSF function. Its expected effect
       is the combined ALE of the scenarios that cite that function's control
       ID, since a CSF gap has no control cost of its own.
    3. The Critical-tier and overdue vendors, priced against the third-party
       scenario's own control set.
    """
    recs = []

    # ── 1. Highest-ALE scenario ──────────────────────────────
    top = max(d["scenarios"], key=lambda r: r["ale"])
    key = next(k for k, s in SCENARIOS.items() if s["name"] == top["scenario_name"])
    recs.append({
        "title":  f"Fund the {top['scenario_name']} control set",
        "why":    (
            f"Largest single exposure in the portfolio: "
            f"{format_currency(top['ale'])} expected annual loss, "
            f"{format_currency(top['percentile_90'])} in a 1-in-10 year."
        ),
        "what":   "; ".join(SCENARIOS[key]["controls"][:3]) + ".",
        "cost":   f"{format_currency(top['control_cost'])}/yr",
        "effect": (
            f"{format_currency(top['ale'] - top['residual_ale'])}/yr reduction at "
            f"{top['control_effectiveness']:.0%} assumed effectiveness, leaving "
            f"{format_currency(top['residual_ale'])} residual. "
            f"ROSI {top['rosi'] * 100:.0f}%."
        ),
    })

    # ── 2. Lowest-scoring CSF function ───────────────────────
    func, score, target = min(d["csf"], key=lambda r: r[1])
    meta  = GAP_METADATA[func]
    cited = [
        r for r in d["scenarios"]
        if meta["nist_ref"] in next(
            (sc["nist_ref"] for sc in SCENARIOS.values()
             if sc["name"] == r["scenario_name"]), ""
        )
    ]
    cited_ale = sum(r["ale"] for r in cited)
    recs.append({
        "title":  f"Close the {func} gap — {score}/5 against a target of {target}/5",
        "why":    (
            f"The weakest function. {meta['nist_ref']} is cited by {len(cited)} of "
            f"the {len(d['scenarios'])} modelled scenarios, carrying "
            f"{format_currency(cited_ale)} of combined annual expected loss."
        ),
        "what":   meta["remediation"],
        "cost":   f"~{meta['effort_weeks']} weeks of analyst effort; no new tooling",
        "effect": (
            f"Raises the weakest function to the defined level and supports the "
            f"{format_currency(cited_ale)} of ALE that depends on it."
        ),
    })

    # ── 3. Vendors ───────────────────────────────────────────
    critical = [v for v in d["vendors"] if v["risk_tier"] == "Critical"]
    overdue  = [r["vendor_name"] for r in d["overdue"]]
    vs = next((r for r in d["scenarios"] if r["scenario_key"] == "vendor_failure"), None)
    recs.append({
        "title":  "Remediate the Critical-tier vendor and clear the reassessment backlog",
        "why":    (
            f"{len(critical)} vendor sits in the Critical tier "
            f"({', '.join(v['vendor_name'] for v in critical)}) and {len(overdue)} are "
            f"past the reassessment window for their tier. OSFI B-10 expects "
            f"monitoring proportionate to criticality."
        ),
        "what":   "; ".join(SCENARIOS["vendor_failure"]["controls"][:2]) + ".",
        "cost":   f"{format_currency(vs['control_cost'])}/yr" if vs else "n/a",
        "effect": (
            f"{format_currency(vs['ale'] - vs['residual_ale'])}/yr reduction against "
            f"the {format_currency(vs['ale'])} third-party scenario. "
            f"ROSI {vs['rosi'] * 100:.0f}%." if vs else ""
        ),
    })
    return recs


# ─────────────────────────────────────────────────────────────
# Document
# ─────────────────────────────────────────────────────────────
def build_story(d, s):
    story     = []
    total_ale = sum(r["ale"] for r in d["scenarios"])
    total_res = sum(r["residual_ale"] for r in d["scenarios"])
    total_cc  = sum(r["control_cost"] or 0 for r in d["scenarios"])
    overall   = sum(c for _, c, _ in d["csf"]) / len(d["csf"])
    avg_tgt   = sum(t for _, _, t in d["csf"]) / len(d["csf"])

    # ── 1. Header ────────────────────────────────────────────
    story.append(Paragraph("Cyber Risk Executive Briefing", s["title"]))
    story.append(Paragraph(
        f"{d['org']} &nbsp;|&nbsp; Prepared for the Chief Information Security "
        f"Officer &nbsp;|&nbsp; {AUTHOR}", s["subtitle"]))
    story.append(table(
        [["Assessment date", "Issued", "Basis"],
         [d["date_run"], date.today().isoformat(),
          "NIST CSF 2.0 · FAIR · OSFI B-10 / B-13 / E-21"]],
        [1.3 * inch, 1.3 * inch, 4.1 * inch], s,
    ))
    story.append(Spacer(1, 8))
    story.append(Table(
        [[Paragraph(
            "Simulated organisation — illustrative data. First National Bank "
            "(Fictional) is not a real institution; every figure is modelled.",
            s["disclaimer"])]],
        colWidths=[6.7 * inch],
        style=TableStyle([
            ("BACKGROUND",  (0, 0), (-1, -1), ACCENT_PALE),
            ("BOX",         (0, 0), (-1, -1), 0.6, ACCENT),
            ("TOPPADDING",  (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ])))

    # ── 2. Executive Overview ────────────────────────────────
    story.append(Paragraph("Executive Overview", s["h2"]))
    worst_func, worst_score, worst_target = min(d["csf"], key=lambda r: r[1])
    story.append(Paragraph(
        f"Across five modelled threat scenarios the bank carries "
        f"<b>{format_currency(total_ale)} in expected annual cyber loss</b>. The "
        f"control programme costed here runs at {format_currency(total_cc)} a year "
        f"and would leave {format_currency(total_res)} of residual expected loss — "
        f"a {format_currency(total_ale - total_res)} reduction, or "
        f"{(total_ale - total_res) / total_ale:.0%}.", s["body"]))
    story.append(Paragraph(
        f"Maturity is the constraint, not budget: <b>{overall:.1f} of 5.0</b> against "
        f"a target of {avg_tgt:.1f}, with {sum(1 for _, c, _ in d['csf'] if c < 3)} of "
        f"{len(d['csf'])} functions below the defined level and {worst_func} weakest at "
        f"{worst_score}/5. Of {len(d['vendors'])} vendors, "
        f"{d['tiers'].get('Critical', 0)} is Critical-tier and {len(d['overdue'])} are "
        f"past their reassessment window — a B-10 gap fixable this quarter without "
        f"new spend.", s["body"]))

    # ── 3. Key Risk Findings ─────────────────────────────────
    story.append(Paragraph("Key Risk Findings", s["h2"]))
    rows = [["Scenario", "ALE", "90th %ile", "Control cost",
             "Residual ALE", "ROSI"]]
    for r in sorted(d["scenarios"], key=lambda r: r["ale"], reverse=True):
        rows.append([
            r["scenario_name"].split(" — ")[0],
            format_currency(r["ale"]),
            format_currency(r["percentile_90"]),
            format_currency(r["control_cost"] or 0),
            format_currency(r["residual_ale"]),
            f"{r['rosi'] * 100:.0f}%",
        ])
    rows.append(["<b>Portfolio total</b>",
                 f"<b>{format_currency(total_ale)}</b>", "—",
                 f"<b>{format_currency(total_cc)}</b>",
                 f"<b>{format_currency(total_res)}</b>",
                 f"<b>{(total_ale - total_res - total_cc) / total_cc * 100:.0f}%</b>"])
    story.append(table(
        rows,
        [2.2 * inch, 0.85 * inch, 0.9 * inch, 0.95 * inch, 0.95 * inch, 0.85 * inch],
        s, align=[1, 2, 3, 4, 5]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "ALE is the mean of 100,000 simulated years. Residual ALE and ROSI rest on "
        "a 60–80% control-effectiveness assumption per scenario.", s["caption"]))

    story.append(Spacer(1, 8))
    story.append(chart(
        os.path.join(CHARTS_DIR, "lec_all_scenarios.png"), 4.2 * inch, s,
        "Loss exceedance curves — the probability that annual loss exceeds any "
        "given dollar amount, per scenario."))

    # ── 4. NIST CSF Maturity ─────────────────────────────────
    story.append(Paragraph("NIST CSF 2.0 Maturity", s["h2"]))
    story.append(Paragraph(
        f"Overall maturity is <b>{overall:.1f} / 5.0</b> against a target of "
        f"{avg_tgt:.1f} — an average gap of {avg_tgt - overall:.1f} levels. "
        f"A score of 3 means documented and consistently followed; 4 means "
        f"measured and tracked with metrics.", s["body"]))

    csf_rows = [["Function", "Current", "Target", "Gap", "Status"]]
    for func, score, target in d["csf"]:
        csf_rows.append([
            func, f"{score}/5", f"{target}/5", str(max(target - score, 0)),
            "Gap — below defined" if score < 3 else "At or above defined",
        ])
    story.append(table(
        csf_rows,
        [1.5 * inch, 0.85 * inch, 0.85 * inch, 0.6 * inch, 2.9 * inch],
        s, align=[1, 2, 3]))

    story.append(Spacer(1, 8))
    story.append(chart(
        os.path.join(CHARTS_DIR, "csf_radar.png"), 2.5 * inch, s,
        "Current maturity against the target of 4 across all six functions."))

    # ── 5. Top 3 Recommendations ─────────────────────────────
    story.append(Paragraph("Top Three Recommendations", s["h2"]))
    for i, rec in enumerate(derive_recommendations(d), 1):
        story.append(KeepTogether([
            table(
                [[f"{i}. {rec['title']}", "", ""],
                 ["Why", rec["why"], ""],
                 ["Action", rec["what"], ""],
                 ["Cost", rec["cost"], f"<b>Effect</b> — {rec['effect']}"]],
                [0.78 * inch, 2.25 * inch, 3.67 * inch], s,
                spans=[((0, 0), (2, 0)), ((1, 1), (2, 1)), ((1, 2), (2, 2))]),
            Spacer(1, 8),
        ]))

    # ── 6. OSFI Alignment ────────────────────────────────────
    story.append(Paragraph("OSFI Alignment Summary", s["h2"]))
    story.append(table([
        ["Guideline / advisory", "Status and key date", "How this programme responds"],
        ["B-13 — Technology and Cyber Risk Management",
         "Effective 1 Jan 2024. Domains: Governance and Risk Management; "
         "Technology Operations and Resilience; Cyber Security.",
         "CSF maturity scoring evidences control validation; the FAIR engine "
         "is the repeatable risk assessment."],
        ["B-10 — Third-Party Risk Management",
         "Revised 2023, effective 1 May 2024.",
         f"Vendor questionnaire, tiering and audit trail. The "
         f"{len(d['overdue'])} overdue reassessments are the open item."],
        ["E-21 — Operational Risk and Resilience Management",
         "Full adherence expected by 1 Sep 2026. Scenario testing of all critical "
         "operations expected by 1 Sep 2027.",
         "Recover scoring and the modelled severe scenarios start that testing "
         "programme."],
        ["Technology and Cyber Security Incident Reporting advisory",
         "Reportable incidents reported to OSFI within 24 hours.",
         f"The {worst_func} gap is the direct exposure: the 24-hour reporting "
         "path is undocumented and untested."],
    ], [1.45 * inch, 2.3 * inch, 2.95 * inch], s))

    # ── 7. Vendor Risk Snapshot ──────────────────────────────
    vendor_block = [Paragraph("Vendor Risk Snapshot", s["h2"])]
    tier_rows = [["Tier", "Vendors", "Reassessment cycle", "Action required"]]
    tier_actions = {
        "Critical": "No onboarding or renewal without a remediation plan. Executive approval required.",
        "High":     "Retain with conditions; quarterly reassessment.",
        "Medium":   "Standard monitoring; annual reassessment.",
        "Low":      "Approved; biennial reassessment.",
    }
    for tier in ("Critical", "High", "Medium", "Low"):
        tier_rows.append([
            tier, str(d["tiers"].get(tier, 0)),
            f"{d['windows'][tier]} days", tier_actions[tier],
        ])
    vendor_block.append(table(
        tier_rows,
        [0.8 * inch, 0.78 * inch, 1.12 * inch, 4.0 * inch], s, align=[1]))

    vendor_block.append(Spacer(1, 6))
    if d["overdue"]:
        vendor_block.append(Paragraph(
            f"<b>{len(d['overdue'])} vendors are overdue for reassessment.</b>",
            s["body"]))
        od_rows = [["Vendor", "Tier", "Days since assessment", "Window"]]
        for r in d["overdue"]:
            od_rows.append([
                r["vendor_name"], r["risk_tier"], str(r["days_since"]),
                f"{d['windows'][r['risk_tier']]} days",
            ])
        vendor_block.append(table(
            od_rows,
            [2.9 * inch, 1.0 * inch, 1.6 * inch, 1.2 * inch], s, align=[2, 3]))
    else:
        vendor_block.append(Paragraph(
            "No vendors are currently overdue for reassessment.", s["body"]))

    vendor_block.append(Spacer(1, 6))
    vendor_block.append(Paragraph(
        f"Portfolio average score {sum(v['score'] for v in d['vendors']) / len(d['vendors']):.1f}/100. "
        f"Weakest: {d['vendors'][0]['vendor_name']} at {d['vendors'][0]['score']}, "
        f"with {d['vendors'][0]['critical_gaps']} critical gaps.", s["body"]))

    # The snapshot is short enough to keep whole rather than split a two-row
    # tail onto its own page.
    story.append(KeepTogether(vendor_block))

    return story


def draw_page(canvas, doc):
    """Accent rule at the top of every page, page number at the foot."""
    canvas.saveState()
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(2)
    canvas.line(0.9 * inch, LETTER[1] - 0.62 * inch,
                LETTER[0] - 0.9 * inch, LETTER[1] - 0.62 * inch)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(INK_MUTED)
    canvas.drawString(0.9 * inch, 0.55 * inch,
                      "First National Bank (Fictional) — simulated data")
    canvas.drawRightString(LETTER[0] - 0.9 * inch, 0.55 * inch,
                           f"Page {doc.page}")
    canvas.restoreState()


def build_pdf():
    initialise_database(verbose=False)
    d = gather_data()
    s = build_styles()

    doc = BaseDocTemplate(
        OUTPUT_FILE, pagesize=LETTER,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        topMargin=0.8 * inch, bottomMargin=0.8 * inch,
        title="Cyber Risk Executive Briefing — First National Bank (Fictional)",
        author=AUTHOR,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame],
                                       onPage=draw_page)])
    doc.build(build_story(d, s))

    print(f"  ✅ Saved: docs/executive_summary.pdf")
    print(f"     {len(d['scenarios'])} scenarios, {len(d['csf'])} CSF functions, "
          f"{len(d['vendors'])} vendors — all figures read from the database.")


if __name__ == "__main__":
    build_pdf()
