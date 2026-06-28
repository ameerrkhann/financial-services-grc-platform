# src/vendor_risk/app.py
# Vendor Risk Assessor — Streamlit Web App
# OSFI B-10 aligned vendor security questionnaire generator

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

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Vendor Risk Assessor",
    page_icon="🛡️",
    layout="wide",
)

# ── Custom styling ────────────────────────────────────────────
st.markdown("""
    <style>
    .main { background-color: #0f1117; }
    .stApp { background-color: #0f1117; }
    h1, h2, h3 { color: #00d4ff; }
    .metric-box {
        background-color: #1a1d2e;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #00d4ff;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────
st.title("🛡️ Vendor Risk Assessor")
st.markdown("**Financial Services GRC Platform** — OSFI B-10 Aligned")
st.markdown("---")


# ── Sidebar — Vendor Info ─────────────────────────────────────
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

    st.markdown("### How This Tool Works")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Step 1 — Enter Vendor Info**")
        st.markdown("Provide vendor name, service type, and criticality in the sidebar.")
    with col2:
        st.markdown("**Step 2 — Answer Questions**")
        st.markdown("Answer Yes/No/Partial for each security question generated for this vendor type.")
    with col3:
        st.markdown("**Step 3 — Get Risk Tier**")
        st.markdown("Your answers produce a score that assigns the vendor to Critical/High/Medium/Low risk tier.")

    st.markdown("---")
    st.markdown("### Question Coverage")
    st.markdown(f"**Universal questions (all vendors):** {len(UNIVERSAL_QUESTIONS)}")
    for stype, questions in SERVICE_SPECIFIC_QUESTIONS.items():
        st.markdown(f"**{stype} specific:** {len(questions)} additional questions")

else:
    # ── Show vendor summary ───────────────────────────────────
    st.markdown(f"## Assessment: {vendor_name}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Service Type", service_type)
    col2.metric("Criticality", criticality)
    col3.metric("Assessor", assessor_name or "Not specified")
    col4.metric("Date", str(assessment_date))

    st.markdown("---")

    # ── Build question list ───────────────────────────────────
    all_questions = UNIVERSAL_QUESTIONS.copy()
    specific      = SERVICE_SPECIFIC_QUESTIONS.get(service_type, [])
    all_questions.extend(specific)

    st.markdown(f"### Security Questionnaire")
    st.markdown(
        f"**{len(all_questions)} questions** generated for a "
        f"**{service_type}** vendor "
        f"({len(UNIVERSAL_QUESTIONS)} universal + {len(specific)} service-specific)"
    )
    st.markdown("---")

    # ── Group questions by category ───────────────────────────
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
                    st.caption(f"🏛️ {q['osfi_ref']}")
                with col_a:
                    answer = st.radio(
                        label=q["id"],
                        options=["Yes", "Partial", "No", "N/A"],
                        key=f"q_{q['id']}",
                        label_visibility="collapsed",
                        horizontal=False,
                    )
                    answers[q["id"]] = {
                        "answer": answer,
                        "weight": q["weight"],
                    }
                st.markdown("---")

    # ── Submit button ─────────────────────────────────────────
    st.markdown("### Submit Assessment")
    notes = st.text_area(
        "Additional Notes",
        placeholder="Any additional context about this vendor assessment..."
    )

    if st.button("🔍 Calculate Risk Score", type="primary", use_container_width=True):
        st.session_state["submitted"]    = True
        st.session_state["answers"]      = answers
        st.session_state["vendor_name"]  = vendor_name
        st.session_state["service_type"] = service_type
        st.session_state["criticality"]  = criticality
        st.session_state["notes"]        = notes
        st.rerun()

    # ── Show results if submitted ─────────────────────────────
    if st.session_state.get("submitted"):
        saved_answers = st.session_state.get("answers", {})

        # Calculate score
        total_points  = 0
        max_points    = 0
        for qid, data in saved_answers.items():
            weight = data["weight"]
            ans    = data["answer"]
            max_points += weight * 2  # max 2 points per weight unit

            if ans == "Yes":
                total_points += weight * 2
            elif ans == "Partial":
                total_points += weight * 1
            elif ans == "N/A":
                max_points -= weight * 2  # excluded from scoring

        score = int((total_points / max_points) * 100) if max_points > 0 else 0

        # Determine tier
        tier       = "Critical"
        tier_info  = RISK_TIERS["Critical"]
        for tier_name, info in RISK_TIERS.items():
            if info["min"] <= score <= info["max"]:
                tier      = tier_name
                tier_info = info
                break

        # Display results
        st.markdown("---")
        st.markdown("## 📊 Assessment Results")

        col1, col2, col3 = st.columns(3)
        col1.metric("Risk Score", f"{score}/100")
        col2.metric("Risk Tier", tier)
        col3.metric("Questions Answered", len(saved_answers))

        st.markdown(f"### Recommended Action")
        st.info(f"**{tier} Risk:** {tier_info['action']}")

        # Answer breakdown
        yes_count     = sum(1 for d in saved_answers.values() if d["answer"] == "Yes")
        partial_count = sum(1 for d in saved_answers.values() if d["answer"] == "Partial")
        no_count      = sum(1 for d in saved_answers.values() if d["answer"] == "No")

        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Yes", yes_count)
        col2.metric("⚠️ Partial", partial_count)
        col3.metric("❌ No", no_count)

        st.success(f"✅ Assessment complete for {st.session_state['vendor_name']}. "
                   f"Scoring logic and database saving coming in Day 18.")