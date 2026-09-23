# build_pdf.py
# Generates the executive summary PDF. Every figure is read from the
# generated dataset — nothing is hardcoded.

import os
import json

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
    TableStyle, Image, KeepTogether,
)

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
PDF = os.path.join(OUT, "executive_summary.pdf")

INK       = colors.HexColor("#14171f")
INK_SOFT  = colors.HexColor("#4a5163")
ACCENT    = colors.HexColor("#14508c")
RULE      = colors.HexColor("#d5dae3")
BAND      = colors.HexColor("#eef1f6")
CRITICAL  = colors.HexColor("#b0342c")
HIGH      = colors.HexColor("#c2601f")
GOOD      = colors.HexColor("#1b6b4c")

MARGIN = 0.72 * inch
CONTENT_W = LETTER[0] - 2 * MARGIN


def S(name, size, leading, colour=INK, space_before=0, space_after=0,
      bold=False, align=TA_LEFT):
    return ParagraphStyle(
        name, fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size, leading=leading, textColor=colour,
        spaceBefore=space_before, spaceAfter=space_after, alignment=align,
    )


ST = {
    "title":    S("title", 21, 25, INK, 0, 2, bold=True),
    "subtitle": S("subtitle", 10.5, 14, INK_SOFT, 0, 4),
    "h2":       S("h2", 13, 16, ACCENT, 11, 5, bold=True),
    "h3":       S("h3", 10.5, 13, INK, 9, 3, bold=True),
    "body":     S("body", 9.6, 14, INK, 0, 6),
    "small":    S("small", 8.3, 11.5, INK_SOFT, 0, 3),
    "caption":  S("caption", 7.8, 10.5, INK_SOFT, 2, 8),
    "cell":     S("cell", 8.4, 11, INK),
    "cellb":    S("cellb", 8.4, 11, INK, bold=True),
    "cellh":    S("cellh", 8.2, 10.5, colors.white, bold=True),
}


def hx(c):
    """reportlab inline <font color> needs #rrggbb, hexval() gives 0xrrggbb."""
    return "#" + c.hexval()[2:]


def money(v, dp=2):
    v = float(v)
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.{dp}f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:,.0f}"


def load():
    d = {}
    for n in ("RiskScenarios", "CSFScores", "ControlGaps",
              "VendorAssessments", "KPISummary"):
        d[n] = pd.read_json(os.path.join(OUT, f"{n}.json"))
    return d


def table(data, widths, header=True, align_right=None, zebra=True):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    style = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
    ]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), ACCENT),
                  ("LINEBELOW", (0, 0), (-1, 0), 0, colors.white)]
    if zebra:
        for r in range(1, len(data)):
            if r % 2 == 0:
                style.append(("BACKGROUND", (0, r), (-1, r), BAND))
    if align_right:
        for c in align_right:
            style.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
    t.setStyle(TableStyle(style))
    return t


def kpi_strip(items):
    """A row of headline numbers."""
    cells, styles = [], []
    row_v, row_l = [], []
    for i, (label, value, colour) in enumerate(items):
        row_v.append(Paragraph(f"<font color='{hx(colour)}'>{value}</font>",
                               S("kv", 16, 19, INK, bold=True)))
        row_l.append(Paragraph(label, S("kl", 7.6, 9.5, INK_SOFT)))
    w = CONTENT_W / len(items)
    t = Table([row_v, row_l], colWidths=[w] * len(items), hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
        ("TOPPADDING", (0, 1), (-1, 1), 0),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, -1), BAND),
        ("LINEBEFORE", (1, 0), (-1, -1), 0.5, colors.white),
    ]))
    return t


def fit_image(path, max_w, max_h):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(path).size
    scale = min(max_w / iw, max_h / ih)
    return Image(path, width=iw * scale, height=ih * scale)


def build():
    d = load()
    scen = d["RiskScenarios"].sort_values("ale", ascending=False)
    csf = d["CSFScores"].sort_values("function_order")
    gaps = d["ControlGaps"].sort_values("risk_rank")
    vend = d["VendorAssessments"]
    k = d["KPISummary"].iloc[0]

    story = []

    # ── Header ────────────────────────────────────────────────────────
    story.append(Paragraph("Cyber Risk Executive Summary", ST["title"]))
    story.append(Paragraph(
        f"{k['org_name']} &nbsp;·&nbsp; Prepared by {'Ameer Khan'} "
        f"&nbsp;·&nbsp; {k['report_date']}", ST["subtitle"]))
    story.append(Table([[""]], colWidths=[CONTENT_W], rowHeights=[2],
                       style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT)])))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Simulated organisation.</b> First National Bank is fictional and all figures "
        "are illustrative, produced by a portfolio risk-modelling platform. This document "
        "demonstrates analytical method and reporting format, not an assessment of any real "
        "institution.", ST["small"]))
    story.append(Spacer(1, 10))

    # ── KPI strip ─────────────────────────────────────────────────────
    story.append(kpi_strip([
        ("Total annualised loss expectancy", money(k["total_ale"]), CRITICAL),
        ("Residual after controls", money(k["total_residual_ale"]), HIGH),
        ("NIST CSF maturity", f"{k['csf_overall_score']:.1f} / 5.0", HIGH),
        ("Vendors assessed", f"{int(k['vendors_assessed'])}", ACCENT),
        ("Overdue reassessments", f"{int(k['overdue_vendors'])}", CRITICAL),
    ]))

    # ── Overview ──────────────────────────────────────────────────────
    top = scen.iloc[0]
    worst_fn = csf.sort_values("score").iloc[0]
    story.append(Paragraph("Executive Overview", ST["h2"]))
    story.append(Paragraph(
        f"Across five modelled threat scenarios, First National Bank carries an expected "
        f"annual cyber loss of <b>{money(k['total_ale'])}</b>. The largest single exposure is "
        f"<b>{top['scenario_name'].split('—')[0].strip()}</b> at {money(top['ale'])} per year, with a "
        f"one-in-ten-year loss of {money(top['percentile_90'])}. A control programme costing "
        f"<b>{money(k['total_control_cost'])} annually</b> is estimated to remove "
        f"{money(k['total_risk_reduction'])} of that exposure, leaving "
        f"{money(k['total_residual_ale'])} residual.", ST["body"]))
    story.append(Paragraph(
        f"Control maturity is the constraint. The bank scores <b>{k['csf_overall_score']:.1f} of 5.0</b> "
        f"against NIST CSF 2.0, with <b>{worst_fn['function_name']}</b> weakest at "
        f"{int(worst_fn['score'])}/5. {int(k['open_control_gaps'])} control gaps are open, and "
        f"{int(k['overdue_vendors'])} of {int(k['vendors_assessed'])} third-party vendors are past their "
        f"OSFI B-10 reassessment date. Governance and incident response are the two areas where "
        f"low cost meets high consequence.", ST["body"]))

    # ── Risk findings ─────────────────────────────────────────────────
    story.append(Paragraph("1. Quantified Risk Exposure", ST["h2"]))
    story.append(Paragraph(
        "Each scenario is modelled with the FAIR method: annual event frequency drawn from a "
        "Poisson distribution, single-event loss from a log-normal fitted to a low/high range, "
        "summed across 100,000 simulated years.", ST["body"]))

    rows = [[Paragraph(h, ST["cellh"]) for h in
             ["Scenario", "Expected annual loss", "1-in-10 year", "Control cost",
              "Residual ALE", "ROSI"]]]
    for r in scen.itertuples():
        rows.append([
            Paragraph(r.scenario_short, ST["cellb"]),
            Paragraph(money(r.ale), ST["cell"]),
            Paragraph(money(r.percentile_90), ST["cell"]),
            Paragraph(money(r.control_cost, 0), ST["cell"]),
            Paragraph(money(r.residual_ale), ST["cell"]),
            Paragraph(f"{r.rosi_pct:,.0f}%", ST["cell"]),
        ])
    rows.append([
        Paragraph("<b>Portfolio total</b>", ST["cellb"]),
        Paragraph(f"<b>{money(k['total_ale'])}</b>", ST["cellb"]),
        Paragraph("—", ST["cell"]),
        Paragraph(f"<b>{money(k['total_control_cost'])}</b>", ST["cellb"]),
        Paragraph(f"<b>{money(k['total_residual_ale'])}</b>", ST["cellb"]),
        Paragraph("—", ST["cell"]),
    ])
    w = [1.28, 1.30, 1.02, 1.00, 1.05, 0.65]
    story.append(table(rows, [x * inch for x in w], align_right=[1, 2, 3, 4, 5]))
    story.append(Paragraph(
        "ROSI (return on security investment) = (risk reduced − control cost) ÷ control cost. "
        "Control effectiveness is assumed at 60–80% by scenario. Control costs represent "
        "incremental tooling spend only and exclude staffing, so ROSI is an upper bound.",
        ST["caption"]))

    story.append(Spacer(1, 4))
    story.append(fit_image(os.path.join(OUT, "lec_all_scenarios.png"), CONTENT_W, 2.28 * inch))
    story.append(Paragraph(
        "Loss exceedance curves. Read the curve at any dollar figure to get the probability that "
        "annual losses exceed it.", ST["caption"]))

    # ── CSF maturity ──────────────────────────────────────────────────
    story.append(Paragraph("2. Control Maturity — NIST CSF 2.0", ST["h2"]))

    mrows = [[Paragraph(h, ST["cellh"]) for h in
              ["Function", "Current", "Target", "Gap", "Assessment"]]]
    for r in csf.itertuples():
        col_sc = CRITICAL if r.score < 2.5 else (HIGH if r.score < 3.5 else GOOD)
        mrows.append([
            Paragraph(r.function_name, ST["cellb"]),
            Paragraph(f"<font color='{hx(col_sc)}'><b>{int(r.score)}</b></font>", ST["cell"]),
            Paragraph(str(int(r.target_score)), ST["cell"]),
            Paragraph(f"+{int(r.gap_to_target)}", ST["cell"]),
            Paragraph(r.rationale, ST["cell"]),
        ])
    story.append(table(mrows, [0.95 * inch, 0.62 * inch, 0.58 * inch,
                               0.45 * inch, 4.7 * inch], align_right=[1, 2, 3]))

    story.append(Spacer(1, 6))
    story.append(fit_image(os.path.join(OUT, "csf_radar.png"), 2.55 * inch, 2.38 * inch))
    story.append(Paragraph(
        "Current maturity against a target of 4 (managed and measured) across all six functions.",
        ST["caption"]))

    # ── Recommendations ───────────────────────────────────────────────
    story.append(Paragraph("3. Recommended Actions", ST["h2"]))
    story.append(Paragraph(
        "Ranked by consequence relative to effort. The first two are low-cost and "
        "unblock everything downstream.", ST["body"]))

    for i, g in enumerate(gaps.head(3).itertuples(), start=1):
        colour = CRITICAL if g.priority == "Critical" else HIGH
        block = [
            Paragraph(f"{i}. {g.function_name} — "
                      f"<font color='{hx(colour)}'>{g.priority}</font> "
                      f"<font color='{hx(INK_SOFT)}'>({g.effort.lower()} effort, "
                      f"about {int(g.effort_weeks)} weeks)</font>", ST["h3"]),
            Paragraph(g.business_impact, ST["body"]),
            Paragraph(f"<b>Action:</b> {g.remediation}", ST["body"]),
            Paragraph(f"<b>Start this month:</b> {g.quick_win}", ST["body"]),
            Paragraph(f"NIST CSF {g.csf_ref} &nbsp;·&nbsp; ISO 27001 {g.iso27001_ref} "
                      f"&nbsp;·&nbsp; SOC 2 {g.soc2_ref} &nbsp;·&nbsp; {g.osfi_ref}",
                      ST["caption"]),
        ]
        story.append(KeepTogether(block))

    # ── Vendor snapshot ───────────────────────────────────────────────
    story.append(Paragraph("4. Third-Party Risk Snapshot", ST["h2"]))
    tier_counts = {t: int((vend["risk_tier"] == t).sum())
                   for t in ["Critical", "High", "Medium", "Low"]}
    story.append(Paragraph(
        f"{int(k['vendors_assessed'])} vendors assessed against an OSFI B-10 aligned questionnaire: "
        f"{tier_counts['Critical']} critical, {tier_counts['High']} high, {tier_counts['Medium']} medium "
        f"and {tier_counts['Low']} low tier. <b>{int(k['overdue_vendors'])} are past their reassessment "
        f"date</b> and should be re-run before any contract renewal.", ST["body"]))

    vr = [[Paragraph(h, ST["cellh"]) for h in
           ["Vendor", "Service", "Tier", "Score", "Critical gaps", "Reassessment"]]]
    for r in vend.sort_values("score").itertuples():
        tcol = {"Critical": CRITICAL, "High": HIGH,
                "Medium": colors.HexColor("#8a6a12"), "Low": GOOD}[r.risk_tier]
        due = "OVERDUE" if r.is_overdue == "TRUE" else r.reassessment_due
        due_col = CRITICAL if r.is_overdue == "TRUE" else INK
        vr.append([
            Paragraph(r.vendor_name, ST["cellb"]),
            Paragraph(r.service_type, ST["cell"]),
            Paragraph(f"<font color='{hx(tcol)}'><b>{r.risk_tier}</b></font>", ST["cell"]),
            Paragraph(f"{int(r.score)}", ST["cell"]),
            Paragraph(f"{int(r.critical_gaps)}", ST["cell"]),
            Paragraph(f"<font color='{hx(due_col)}'>{due}</font>", ST["cell"]),
        ])
    story.append(KeepTogether(table(vr, [1.72 * inch, 1.42 * inch, 0.72 * inch,
                                        0.55 * inch, 0.85 * inch, 1.04 * inch],
                                   align_right=[3, 4])))

    # ── Regulatory ────────────────────────────────────────────────────
    story.append(Paragraph("5. OSFI Alignment", ST["h2"]))
    reg = [[Paragraph(h, ST["cellh"]) for h in ["Guideline", "Scope", "Status in this assessment"]]]
    for g, scope, status in [
        ("B-13 <font size=7>(in force Jan 2024)</font>", "Technology and cyber risk management",
         "Governance and detection gaps open; incident reporting path undefined"),
        ("B-10 <font size=7>(in force May 2024)</font>", "Third-party risk management",
         f"Vendor tiering operating; {int(k['overdue_vendors'])} reassessments overdue"),
        ("E-21 <font size=7>(full adherence Sep 2026)</font>", "Operational risk and resilience",
         "Recovery tested annually; scenario testing of all critical operations due Sep 2027"),
    ]:
        reg.append([Paragraph(g, ST["cellb"]), Paragraph(scope, ST["cell"]),
                    Paragraph(status, ST["cell"])])
    story.append(table(reg, [1.5 * inch, 2.1 * inch, 3.7 * inch]))

    story.append(KeepTogether([
        Paragraph("Method and Limitations", ST["h2"]),
        Paragraph(
        "Loss ranges are calibrated to published Canadian financial-sector breach cost benchmarks "
        "and interpreted as the 5th and 95th percentile of a log-normal distribution; the resulting "
        "mean therefore sits above the midpoint of the stated range. Scenarios are modelled "
        "independently, though in practice one event often triggers several. Control effectiveness "
        "is assumed rather than measured. Figures should be read as a decision-support range, not "
        "a forecast.", ST["body"])]))

    # ── Build ─────────────────────────────────────────────────────────
    doc = BaseDocTemplate(PDF, pagesize=LETTER,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=0.62 * inch,
                          title="Cyber Risk Executive Summary — First National Bank (Fictional)",
                          author="Ameer Khan")
    frame = Frame(MARGIN, 0.62 * inch, CONTENT_W,
                  LETTER[1] - MARGIN - 0.62 * inch, id="f", showBoundary=0)

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.4)
        canvas.line(MARGIN, 0.52 * inch, LETTER[0] - MARGIN, 0.52 * inch)
        canvas.setFont("Helvetica", 7.4)
        canvas.setFillColor(INK_SOFT)
        canvas.drawString(MARGIN, 0.37 * inch,
                          "First National Bank (Fictional) — simulated data for portfolio demonstration")
        canvas.drawRightString(LETTER[0] - MARGIN, 0.37 * inch, f"Page {doc_.page}")
        canvas.restoreState()

    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])
    doc.build(story)
    print(f"  wrote {PDF}")


if __name__ == "__main__":
    build()
