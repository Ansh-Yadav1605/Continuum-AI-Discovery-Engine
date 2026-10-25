"""
pages/4_Theme_Analysis.py — Theme Analysis Engine (Milestone 2.1).

Aggregates evidence across provisional taxonomy, identifies supporting vs. contradictory
evidence signals, highlights missing context/limitations, and logs open research questions.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.database import init_db
from core.ui_helpers import apply_custom_styles, render_sidebar_status
from core.themes import (
    get_theme_summary,
    get_theme_records,
    get_contradictory_evidence,
    get_theme_open_questions,
    save_theme_open_question
)

# 1. Page Configuration
st.set_page_config(
    page_title="Theme Analysis | SIP Discovery Engine",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()
apply_custom_styles()
render_sidebar_status()

# 2. Header & Integrity Guidance
st.markdown(
    """
    <div class="hero-header">
        <div class="hero-title">🧬 Theme Analysis & Evidence Synthesis</div>
        <p class="hero-subtitle">
            Aggregate qualitative and survey signals across the 14-category provisional taxonomy. Compare reviews vs. surveys, scrutinise contradictory signals, and identify critical evidence gaps.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.warning(
    "⚠️ **Methodology Notice:** Theme frequency represents an investigative signal, **NOT proof of causation**. "
    "A frequent complaint does not guarantee that it is the primary driver of 12-month SIP termination. "
    "Always separate observed frequency from causal impact."
)

# 3. Data Retrieval
theme_summaries = get_theme_summary()
active_themes = [t for t in theme_summaries if t["record_count"] > 0]

if not active_themes:
    st.info("ℹ️ No records have been analysed yet. Go to **Import Data** and **Research Explorer** to ingest and analyse records first.")
    st.stop()

# 4. Top-level Theme Distribution & Comparative Overview
st.markdown("### 📊 Distribution Overview")

col_mode, col_sort = st.columns([2, 1])
with col_mode:
    view_mode = st.radio(
        "Display Mode",
        ["Consolidated Theme Cards", "Compare Reviews vs Surveys Side-by-Side"],
        horizontal=True
    )

if view_mode == "Compare Reviews vs Surveys Side-by-Side":
    st.markdown("#### ⚖️ Public Reviews vs. Primary Surveys by Theme")
    
    comp_data = []
    for t in active_themes:
        comp_data.append({
            "Theme": t["theme"][:26] + "..." if len(t["theme"]) > 28 else t["theme"],
            "Public Reviews": t["record_types"]["public_review"],
            "Survey Responses": t["record_types"]["survey_response"],
            "Interview Notes": t["record_types"]["interview_note"],
            "Browser Captured": t["record_types"]["browser_collected"]
        })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=[d["Theme"] for d in comp_data],
        x=[d["Public Reviews"] for d in comp_data],
        name="Public Reviews",
        orientation="h",
        marker_color="#6366F1"
    ))
    fig.add_trace(go.Bar(
        y=[d["Theme"] for d in comp_data],
        x=[d["Survey Responses"] for d in comp_data],
        name="Survey Responses",
        orientation="h",
        marker_color="#EC4899"
    ))
    fig.add_trace(go.Bar(
        y=[d["Theme"] for d in comp_data],
        x=[d["Interview Notes"] for d in comp_data],
        name="Interview Notes",
        orientation="h",
        marker_color="#10B981"
    ))
    fig.update_layout(
        barmode="group",
        height=550,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0")
    )
    st.plotly_chart(fig, use_container_width=True)

# 5. Theme Drill-Down Cards
st.markdown("### 🗂️ Theme Detail Cards")

for t in active_themes:
    t_name = t["theme"]
    count = t["record_count"]
    sources_cnt = t["distinct_sources"]
    respondents_cnt = t["distinct_respondents"]
    contradictory_cnt = t["contradictory_count"]

    header_label = f"**{t_name}** — {count} records | {respondents_cnt} distinct respondents | {sources_cnt} sources"
    if contradictory_cnt > 0:
        header_label += f" ⚠️ ({contradictory_cnt} contradictory signals)"

    with st.expander(header_label, expanded=False):
        st.markdown(f"**Definition:** *{t['definition']}*")
        
        # Metric Pills
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Records", count)
        with m2:
            st.metric("Unique Respondents", respondents_cnt, help="Count of unique user/respondent IDs where known.")
        with m3:
            st.metric("Distinct Sources", sources_cnt)
        with m4:
            st.metric("Contradictory Signals", contradictory_cnt, help="Records showing contrasting outcomes, e.g. continuation vs drop-off.")

        # Source breakdown pills
        st.markdown(
            f"""
            <div style="margin-bottom: 12px;">
                <span class="badge badge-source">Reviews: {t['record_types']['public_review']}</span>
                <span class="badge badge-survey">Surveys: {t['record_types']['survey_response']}</span>
                <span class="badge badge-relevant">Interviews: {t['record_types']['interview_note']}</span>
                <span class="badge badge-indirect">Browser Ext: {t['record_types']['browser_collected']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        tab_support, tab_contra, tab_limits, tab_questions = st.tabs([
            "📌 Supporting Evidence",
            f"⚡ Contradictory Evidence ({contradictory_cnt})",
            "🛡️ Evidence Limitations",
            "❓ Open Questions"
        ])

        with tab_support:
            partition = get_contradictory_evidence(t_name)
            stopping_records = partition["stopping_or_friction"]
            if stopping_records:
                st.markdown(f"**Drop-off / Friction Signals ({len(stopping_records)} records):**")
                for r in stopping_records[:5]:
                    quote = r["human_evidence"] or r["ai_evidence_excerpt"] or r["text"][:200]
                    st.markdown(f"<div class='evidence-box'>“{quote}”<br/><small style='color:#94A3B8;'>Source: {r['source']} | ID: {r['record_id'][:8]}</small></div>", unsafe_allow_html=True)
            else:
                st.info("No explicit stopping or friction signals isolated for this theme yet.")

        with tab_contra:
            partition = get_contradictory_evidence(t_name)
            continuing_records = partition["continuing_or_positive"]
            if continuing_records:
                st.markdown(f"**Continuation / Positive Signals ({len(continuing_records)} records):**")
                for r in continuing_records[:5]:
                    quote = r["human_evidence"] or r["ai_evidence_excerpt"] or r["text"][:200]
                    st.markdown(f"<div class='evidence-box' style='border-left-color: #10B981; background: rgba(16,185,129,0.08);'>“{quote}”<br/><small style='color:#94A3B8;'>Source: {r['source']} | ID: {r['record_id'][:8]}</small></div>", unsafe_allow_html=True)
            else:
                st.caption("No contrasting continuation signals found for this theme.")

        with tab_limits:
            st.markdown("#### 🔍 What this evidence does NOT establish")
            st.markdown(
                """
                - **Causal linkage to 12-month retention:** Public reviews reflect point-in-time frustration rather than verified longitudinal continuation.
                - **Unbiased population sampling:** Disgruntled users or vocal respondents are over-represented compared to quiet successful investors.
                """
            )
            if t["missing_contexts"]:
                st.markdown("**Specific context gaps flagged by AI / Reviewers:**")
                for ctx in t["missing_contexts"]:
                    st.markdown(f"<div class='missing-box'>⚠️ {ctx}</div>", unsafe_allow_html=True)

        with tab_questions:
            st.markdown("#### ❓ Open Research Questions")
            existing_questions = get_theme_open_questions(t_name)
            if existing_questions:
                for idx, q in enumerate(existing_questions, 1):
                    st.markdown(f"**{idx}.** {q}")
            else:
                st.caption("No open questions added for this theme yet.")

            new_q = st.text_input(f"Add an exploratory question for {t_name}", key=f"new_q_{t_name}")
            if st.button("Save Question", key=f"btn_q_{t_name}"):
                if new_q.strip():
                    save_theme_open_question(t_name, new_q)
                    st.success("Question logged to theme audit.")
                    st.rerun()

        st.markdown("<br/>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            if st.button("Explore in Research Explorer ↗", key=f"nav_exp_{t_name}"):
                st.switch_page("pages/3_Research_Explorer.py")
