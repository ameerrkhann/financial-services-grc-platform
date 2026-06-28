# src/vendor_risk/app.py
# Vendor Risk Assessor — Streamlit Web App
# OSFI B-10 aligned vendor security questionnaire and scoring

import sys
import os
from datetime import date

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.vendor_risk.questionnaire_data import (
    UNIVERSAL_QUESTIONS,
    SERVICE_SPECIFIC_QUESTIONS,
    RISK_TIERS,
    SERVICE_TYPES,
)
from src.vendor_risk.scoring import (
    calculate_score,
    get_tier_colour,
    get_score_label,
)
from src.database.db_manager import (
    initialise_database,
    save_vendor_assessment,
    save_vendor_responses,
    get_all_vendor_assessments,
    get_vendor_tier_summary,
)

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Vendor Risk Assessor",
    page_icon="🛡️",
    layout="wide",
)

initialise_database()

st.markdown("""
    <style>
    .main { background-color: #0f1117; }
    .stApp { background-color: #0f1117; }
    h1, h2, h3 { color: #00d4ff; }
    </style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────
st.title("🛡️ Vendor Risk Assessor")
st.markdown("**Financial Services GRC Platform** — OSFI B-10 Aligned")
st.markdown("---")


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("📋 Vendor Information")

    vendor_name = st.text_input(
        "Vendor Name",
        placeholder="e.g. Acme Cloud Services"
    )
    service_type = st.selectbox(
        "Service Type",
        options=SERVICE_TYPES,
        help="Select the type of service this vendor provides"
    )
    criticality = st.select_slider(
        "Business Criticality",
        options=["Low", "Medium", "High", "Critical"],
        value="Medium",
        help="How critical is this vendor to your operations?"
    )
    assessor_name = st.text_input(
        "Assessor Name",
        placeholder="e.g. Ameer Khan"
    )
    assessment_date = st.date_input(
        "Assessment Date",
        value=date.today()
    )

    st.markdown("---")
    st.markdown("**Regulatory Framework**")
    st.markdown("🇨🇦 OSFI B-10 — Third-Party Risk")
    st.markdown("🔒 OSFI B-13 — Cyber Risk")
    st.markdown("⚡ OSFI E-21 — Operational Resilience")


# ── Main Content ──────────────────────────────────────────────
if not vendor_name:
    st.info("👈 Enter vendor information in the sidebar to begin the assessment.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Step 1 — Enter Vendor Info**")
        st.markdown("Vendor name, service type, and criticality in the sidebar.")
    with col2:
        st.markdown("**Step 2 — Answer Questions**")
        st.markdown("Yes / Partial / No / N/A for each security control question.")
    with col3:
        st.markdown("**Step 3 — Get Risk Tier**")
        st.markdown("Automated scoring assigns Critical / High / Medium / Low tier.")

    st.markdown("---")
    st.markdown("### Question Coverage")
    st.markdown(f"**Universal questions (all vendors):** {len(UNIVERSAL_QUESTIONS)}")
    for stype, questions in SERVICE_SPECIFIC_QUESTIONS.items():
        st.markdown(f"**{stype} specific:** {len(questions)} additional questions")

else:
    # ── Vendor summary bar ────────────────────────────────────
    st.markdown(f"## Assessment: {vendor_name}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Service Type",  service_type)
    col2.metric("Criticality",   criticality)
    col3.metric("Assessor",      assessor_name or "Not specified")
    col4.metric("Date",          str(assessment_date))
    st.markdown("---")

    # ── Build question list ───────────────────────────────────
    all_questions = UNIVERSAL_QUESTIONS.copy()
    specific      = SERVICE_SPECIFIC_QUESTIONS.get(service_type, [])
    all_questions.extend(specific)

    st.markdown("### Security Questionnaire")
    st.markdown(
        f"**{len(all_questions)} questions** generated for a "
        f"**{service_type}** vendor "
        f"({len(UNIVERSAL_QUESTIONS)} universal + {len(specific)} service-specific)"
    )
    st.markdown("---")

    # ── Group by category ─────────────────────────────────────
    categories = {}
    for q in all_questions:
        cat = q["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(q)

    # ── Render questions ──────────────────────────────────────
    answers = {}
    for category, questions in categories.items():
        with st.expander(f"📂 {category} ({len(questions)} questions)", expanded=True):
            for q in questions:
                col_q, col_a = st.columns([3, 1])
                with col_q:
                    st.markdown(f"**{q['id']}** — {q['question']}")
                    st.caption(
                        f"🏛️ {q['osfi_ref']} | "
                        f"Weight: {'🔴 High' if q['weight'] == 3 else '🟡 Medium'}"
                    )
                with col_a:
                    answer = st.radio(
                        label=q["id"],
                        options=["Yes", "Partial", "No", "N/A"],
                        key=f"q_{q['id']}",
                        label_visibility="collapsed",
                        horizontal=False,
                    )
                    answers[q["id"]] = {
                        "answer":   answer,
                        "weight":   q["weight"],
                        "question": q["question"],
                        "category": q["category"],
                    }
                st.markdown("---")

    # ── Notes + Submit ────────────────────────────────────────
    st.markdown("### Submit Assessment")
    notes = st.text_area(
        "Additional Notes",
        placeholder="Any additional context about this vendor assessment..."
    )

    if st.button("🔍 Calculate Risk Score", type="primary", use_container_width=True):
        result = calculate_score(answers)

        # Save to database
        assessment_id = save_vendor_assessment(
            vendor_name     = vendor_name,
            service_type    = service_type,
            criticality     = criticality,
            assessor        = assessor_name or "Unknown",
            assessment_date = str(assessment_date),
            score           = result["score"],
            risk_tier       = result["tier"],
            gap_count       = result["gap_count"],
            critical_gaps   = len(result["critical_gaps"]),
            notes           = notes,
        )
        save_vendor_responses(assessment_id, answers)

        # Store in session state
        st.session_state["result"]        = result
        st.session_state["assessment_id"] = assessment_id
        st.session_state["vendor_name"]   = vendor_name
        st.session_state["service_type"]  = service_type
        st.session_state["criticality"]   = criticality
        st.session_state["notes"]         = notes
        st.session_state["submitted"]     = True

    # ── Results ───────────────────────────────────────────────
    if st.session_state.get("submitted"):
        result = st.session_state["result"]
        score  = result["score"]
        tier   = result["tier"]

        st.markdown("---")
        st.markdown("## 📊 Assessment Results")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Risk Score",    f"{score} / 100")
        col2.metric("Risk Tier",     tier)
        col3.metric("Critical Gaps", len(result["critical_gaps"]))
        col4.metric("Total Gaps",    result["gap_count"])

        st.markdown(f"**Posture Summary:** {get_score_label(score)}")
        st.info(f"**Recommended Action:** {result['tier_info']['action']}")

        # Answer breakdown
        answered  = list(answers.values())
        yes_c     = sum(1 for a in answered if a["answer"] == "Yes")
        partial_c = sum(1 for a in answered if a["answer"] == "Partial")
        no_c      = sum(1 for a in answered if a["answer"] == "No")
        na_c      = sum(1 for a in answered if a["answer"] == "N/A")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("✅ Yes",     yes_c)
        col2.metric("⚠️ Partial", partial_c)
        col3.metric("❌ No",      no_c)
        col4.metric("➖ N/A",     na_c)

        st.markdown("---")

        # ── Gap report ────────────────────────────────────────
        if result["gaps"]:
            st.markdown("### ⚠️ Gap Report — Ranked by Impact")
            st.markdown("These are the answers that reduced your score, worst first.")

            for gap in result["gaps"]:
                sev_icon = "🔴" if gap["severity"] == "Critical" else "🟡"
                with st.expander(
                    f"{sev_icon} [{gap['severity']}] {gap['id']} — "
                    f"{gap['category']} | Lost {gap['lost_points']} points"
                ):
                    st.markdown(f"**Question:** {gap['question']}")
                    st.markdown(f"**Answer given:** {gap['answer']}")
                    if gap["answer"] == "Partial":
                        st.markdown("**To resolve:** Fully implement this control and provide documentation.")
                    else:
                        st.markdown("**To resolve:** Implement this control and provide evidence to assessor.")

        # ── Strengths ─────────────────────────────────────────
        if result["strengths"]:
            st.markdown("### ✅ Strengths")
            for s in result["strengths"]:
                st.markdown(f"- **{s['id']}** ({s['category']}): {s['question'][:80]}...")

        # ── Save confirmation ─────────────────────────────────
        aid = st.session_state.get("assessment_id", "—")
        st.success(
            f"✅ Assessment saved to database (ID: {aid}) — "
            f"**{st.session_state['vendor_name']}** | "
            f"Tier: {result['tier']} | Score: {result['score']}/100"
        )


# ── Assessment History (always visible) ──────────────────────
st.markdown("---")
st.markdown("## 📁 Assessment History")

all_assessments = get_all_vendor_assessments()

if not all_assessments:
    st.info("No assessments saved yet. Complete an assessment above to see it here.")
else:
    tier_summary = get_vendor_tier_summary()
    if tier_summary:
        st.markdown("### Vendor Portfolio by Risk Tier")
        cols      = st.columns(len(tier_summary))
        tier_icons = {
            "Critical": "🔴",
            "High":     "🟠",
            "Medium":   "🟡",
            "Low":      "🟢",
        }
        for i, row in enumerate(tier_summary):
            icon = tier_icons.get(row["risk_tier"], "⚪")
            cols[i].metric(
                f"{icon} {row['risk_tier']}",
                f"{row['count']} vendor(s)"
            )

    st.markdown("### All Assessments")
    import pandas as pd
    df           = pd.DataFrame([dict(row) for row in all_assessments])
    display_cols = [
        "id", "vendor_name", "service_type", "risk_tier",
        "score", "critical_gaps", "assessor", "assessment_date"
    ]
    existing_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(
        df[existing_cols],
        use_container_width=True,
        hide_index=True,
    )