# build_pbix.py
# Adds two dashboard pages to the existing Power BI report by writing PBIR
# (Power BI Enhanced Report Format) JSON directly into the .pbix archive.
#
# Design constraint: the .pbix carries a binary DataModel that cannot be
# regenerated here, so every new visual references only tables and columns
# that already exist in that model, plus columns added by the refreshed
# Excel export. New tables (VendorResponses, ControlMapping, KPISummary)
# are deliberately NOT used, because they would not exist until a fresh
# import rather than a refresh.

import os
import json
import shutil
import zipfile
import hashlib

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_PBIX = "/mnt/user-data/uploads/GRC_Risk_Dashboard__1_.pbix"
WORK = os.path.join(BASE, "pb")
EX = os.path.join(WORK, "ex")
OUT_PBIX = os.path.join(BASE, "out", "GRC_Risk_Dashboard.pbix")

VIS_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.10.0/schema.json"
PAGE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
PAGES_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"

# Power BI aggregation function codes
SUM, AVG, MIN, MAX, COUNT_DISTINCT, COUNT = 0, 1, 2, 3, 4, 5


def oid(*parts):
    """Deterministic 20-hex-char object id, matching Power BI's id shape."""
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:20]


def col(entity, prop):
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def agg(entity, prop, fn):
    return {"Aggregation": {"Expression": col(entity, prop), "Function": fn}}


def projection(entity, prop, fn=None, display=None, active=False):
    """Builds one field projection for a visual's query state."""
    if fn is None:
        field = col(entity, prop)
        qref = f"{entity}.{prop}"
    else:
        field = agg(entity, prop, fn)
        fname = {SUM: "Sum", AVG: "Avg", MIN: "Min", MAX: "Max",
                 COUNT_DISTINCT: "CountDistinct", COUNT: "CountNonNull"}[fn]
        qref = f"{fname}({entity}.{prop})"
    p = {"field": field, "queryRef": qref,
         "nativeQueryRef": display or prop}
    if display:
        p["displayName"] = display
    if active:
        p["active"] = True
    return p


def visual(name, vtype, x, y, w, h, z, query_state=None, title=None,
           objects=None, sort=None):
    """Assembles a complete visual container document."""
    v = {"visualType": vtype}
    if query_state:
        q = {"queryState": query_state}
        if sort:
            q["sortDefinition"] = {"sort": sort, "isDefaultSort": True}
        v["query"] = q
    if objects:
        v["objects"] = objects
    if title is not None:
        v["visualContainerObjects"] = {
            "title": [{"properties": {"text": {"expr": {"Literal": {"Value": f"'{title}'"}}}}}]
        }
    v["drillFilterOtherVisuals"] = True
    return {
        "$schema": VIS_SCHEMA,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": v,
    }


def textbox(name, x, y, w, h, z, text, size="28pt", align="center"):
    return {
        "$schema": VIS_SCHEMA,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": "textbox",
            "objects": {"general": [{"properties": {"paragraphs": [
                {"textRuns": [{"value": text, "textStyle": {"fontSize": size}}],
                 "horizontalTextAlignment": align}
            ]}}]},
            "drillFilterOtherVisuals": True,
        },
    }


def data_label_on():
    return {"labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]}


# ──────────────────────────────────────────────────────────────────────
# Page 2 — NIST CSF 2.0 Maturity
# ──────────────────────────────────────────────────────────────────────

def page_csf():
    pid = oid("page", "csf-maturity")
    CSF, GAPS = "CSFScores_tbl", "ControlGaps_tbl"
    vis = []

    vis.append(textbox(oid("csf", "title"), 20, 8, 1238, 62, 1000,
                       "NIST CSF 2.0 Maturity Assessment", "28pt"))

    # Current vs target by function
    vis.append(visual(
        oid("csf", "bars"), "clusteredBarChart", 0, 78, 700, 400, 10,
        query_state={
            "Category": {"projections": [projection(CSF, "function_name", active=True)]},
            "Y": {"projections": [
                projection(CSF, "score", MAX, "Current maturity"),
                projection(CSF, "target_score", MAX, "Target maturity"),
            ]},
        },
        sort=[{"field": col(CSF, "function_name"), "direction": "Ascending"}],
        title="Maturity by Function — Current vs Target (1–5)",
        objects=data_label_on(),
    ))

    # Headline numbers
    vis.append(visual(
        oid("csf", "card-overall"), "cardVisual", 710, 78, 275, 128, 20,
        query_state={"Data": {"projections": [
            projection(CSF, "score", AVG, "Overall Maturity")]}},
        title="Overall Maturity (of 5.0)",
    ))
    vis.append(visual(
        oid("csf", "card-gaps"), "cardVisual", 995, 78, 275, 128, 21,
        query_state={"Data": {"projections": [
            projection(GAPS, "function_name", COUNT, "Open Gaps")]}},
        title="Open Control Gaps",
    ))
    vis.append(visual(
        oid("csf", "card-weeks"), "cardVisual", 710, 214, 275, 128, 22,
        query_state={"Data": {"projections": [
            projection(GAPS, "effort_weeks", SUM, "Remediation Weeks")]}},
        title="Total Remediation Effort (weeks)",
    ))
    vis.append(visual(
        oid("csf", "card-togo"), "cardVisual", 995, 214, 275, 128, 23,
        query_state={"Data": {"projections": [
            projection(CSF, "gap_to_target", SUM, "Maturity Points to Target")]}},
        title="Maturity Points to Target",
    ))

    # Gaps by priority
    vis.append(visual(
        oid("csf", "donut"), "donutChart", 710, 350, 560, 128, 24,
        query_state={
            "Category": {"projections": [projection(GAPS, "priority", active=True)]},
            "Y": {"projections": [projection(GAPS, "function_name", COUNT, "Gaps")]},
        },
        title="Gaps by Priority",
    ))

    # Cross-framework gap register
    vis.append(visual(
        oid("csf", "table"), "tableEx", 0, 486, 1270, 228, 30,
        query_state={"Values": {"projections": [
            projection(GAPS, "function_name", active=True),
            projection(GAPS, "priority"),
            projection(GAPS, "csf_ref", display="NIST CSF 2.0"),
            projection(GAPS, "iso27001_ref", display="ISO 27001:2022"),
            projection(GAPS, "soc2_ref", display="SOC 2"),
            projection(GAPS, "osfi_ref", display="OSFI"),
            projection(GAPS, "effort_weeks", SUM, "Weeks"),
        ]}},
        sort=[{"field": col(GAPS, "function_name"), "direction": "Ascending"}],
        title="Control Gaps — Cross-Framework Mapping and Remediation Effort",
    ))

    page = {"$schema": PAGE_SCHEMA, "name": pid,
            "displayName": "CSF Maturity", "displayOption": "FitToPage",
            "height": 720, "width": 1280}
    return pid, page, vis


# ──────────────────────────────────────────────────────────────────────
# Page 3 — Vendor Risk Portfolio
# ──────────────────────────────────────────────────────────────────────

def page_vendor():
    pid = oid("page", "vendor-risk")
    V, T = "VendorAssessments_tbl", "VendorTierSummary_tbl"
    vis = []

    vis.append(textbox(oid("v", "title"), 20, 8, 1238, 62, 1000,
                       "Third-Party Vendor Risk — OSFI B-10", "28pt"))

    # KPI row
    kpis = [
        (oid("v", "k1"), V, "vendor_name", COUNT, "Vendors Assessed", 0),
        (oid("v", "k2"), V, "is_critical_flag", SUM, "Critical-Tier Vendors", 254),
        (oid("v", "k3"), V, "is_overdue_flag", SUM, "Overdue for Reassessment", 508),
        (oid("v", "k4"), V, "score", AVG, "Average Vendor Score", 762),
        (oid("v", "k5"), V, "critical_gaps", SUM, "Critical Gaps Open", 1016),
    ]
    for name, ent, prop, fn, label, x in kpis:
        vis.append(visual(name, "cardVisual", x, 78, 250, 120, 20,
                          query_state={"Data": {"projections":
                                                [projection(ent, prop, fn, label)]}},
                          title=label))

    # Tier distribution
    vis.append(visual(
        oid("v", "tiers"), "clusteredColumnChart", 0, 206, 500, 290, 30,
        query_state={
            "Category": {"projections": [projection(T, "risk_tier", active=True)]},
            "Y": {"projections": [projection(T, "vendor_count", SUM, "Vendors")]},
        },
        title="Portfolio by Risk Tier",
        objects=data_label_on(),
    ))

    # Score by vendor
    vis.append(visual(
        oid("v", "scores"), "clusteredBarChart", 508, 206, 762, 290, 31,
        query_state={
            "Category": {"projections": [projection(V, "vendor_name", active=True)]},
            "Y": {"projections": [projection(V, "score", MAX, "Risk Score")]},
        },
        sort=[{"field": agg(V, "score", MAX), "direction": "Descending"}],
        title="Vendor Risk Score (0–100, higher is better)",
        objects=data_label_on(),
    ))

    # Filter by service type
    vis.append(visual(
        oid("v", "slicer"), "slicer", 0, 504, 250, 210, 40,
        query_state={"Values": {"projections": [projection(V, "service_type", active=True)]}},
        title="Filter — Service Type",
    ))

    # Vendor register
    vis.append(visual(
        oid("v", "table"), "tableEx", 258, 504, 1012, 210, 41,
        query_state={"Values": {"projections": [
            projection(V, "vendor_name", active=True),
            projection(V, "service_type"),
            projection(V, "risk_tier", display="Tier"),
            projection(V, "score", MAX, "Score"),
            projection(V, "critical_gaps", SUM, "Critical Gaps"),
            projection(V, "assessment_date", display="Last Assessed"),
            projection(V, "reassessment_due", display="Reassessment Due"),
            projection(V, "is_overdue", display="Overdue"),
        ]}},
        sort=[{"field": agg(V, "score", MAX), "direction": "Ascending"}],
        title="Vendor Register — Assessment History and Reassessment Status",
    ))

    page = {"$schema": PAGE_SCHEMA, "name": pid,
            "displayName": "Vendor Risk", "displayOption": "FitToPage",
            "height": 720, "width": 1280}
    return pid, page, vis


# ──────────────────────────────────────────────────────────────────────

def main():
    if os.path.exists(EX):
        shutil.rmtree(EX)
    os.makedirs(EX, exist_ok=True)
    with zipfile.ZipFile(SRC_PBIX) as z:
        z.extractall(EX)

    pages_dir = os.path.join(EX, "Report", "definition", "pages")
    meta_path = os.path.join(pages_dir, "pages.json")
    meta = json.load(open(meta_path))

    # Rename the existing page so the three read as a set
    existing = meta["pageOrder"][0]
    p1_path = os.path.join(pages_dir, existing, "page.json")
    p1 = json.load(open(p1_path))
    p1["displayName"] = "Risk Overview"
    json.dump(p1, open(p1_path, "w"), indent=2)

    new_order = [existing]
    for builder in (page_csf, page_vendor):
        pid, page, visuals = builder()
        vdir = os.path.join(pages_dir, pid, "visuals")
        os.makedirs(vdir, exist_ok=True)
        json.dump(page, open(os.path.join(pages_dir, pid, "page.json"), "w"), indent=2)
        for v in visuals:
            d = os.path.join(vdir, v["name"])
            os.makedirs(d, exist_ok=True)
            json.dump(v, open(os.path.join(d, "visual.json"), "w"), indent=2)
        new_order.append(pid)
        print(f"  page '{page['displayName']}' — {len(visuals)} visuals")

    meta["pageOrder"] = new_order
    meta["activePageName"] = existing
    meta["$schema"] = PAGES_SCHEMA
    json.dump(meta, open(meta_path, "w"), indent=2)

    # Repack. [Content_Types].xml must be the first entry in the archive.
    os.makedirs(os.path.dirname(OUT_PBIX), exist_ok=True)
    if os.path.exists(OUT_PBIX):
        os.remove(OUT_PBIX)

    # Preserve each original entry's compression method. Power BI stores the
    # DataModel uncompressed (ZIP_STORED) and can reject it if re-deflated.
    with zipfile.ZipFile(SRC_PBIX) as z:
        original_method = {i.filename: i.compress_type for i in z.infolist()}

    all_files = []
    for root, _, files in os.walk(EX):
        for f in files:
            full = os.path.join(root, f)
            all_files.append((full, os.path.relpath(full, EX).replace(os.sep, "/")))
    all_files.sort(key=lambda t: (t[1] != "[Content_Types].xml", t[1]))

    with zipfile.ZipFile(OUT_PBIX, "w", zipfile.ZIP_DEFLATED) as z:
        for full, arc in all_files:
            z.write(full, arc,
                    compress_type=original_method.get(arc, zipfile.ZIP_DEFLATED))

    size = os.path.getsize(OUT_PBIX) / 1024 / 1024
    print(f"\n  wrote {OUT_PBIX} ({size:.1f} MB, {len(all_files)} entries)")


if __name__ == "__main__":
    main()
