"""
pages/5_Problem_Statements.py — Candidate Problem Statements, Prioritization & Interview Guide (Milestone 2.2 & 2.4).

Formulate, score, and rank candidate problem statements using the 6-factor weighted scorecard.
Enforces compliance as a hard filter (safety_compliance <= 2 blocks the candidate).
Generates neutral discovery interview guides and logs qualitative interview notes.
"""

import streamlit as st
import pandas as pd
from core.database import init_db
from core.ui_helpers import apply_custom_styles, render_sidebar_status
from core.themes import get_theme_summary
from core.problems import (
    get_all_problems,
    save_problem,
    update_validation_status,
    delete_problem,
    generate_problem_statements,
    VALIDATION_STATUSES
)
from core.scoring import (
    calculate_score,
    save_score,
    get_scorecard,
    get_ranked_problems,
    FACTOR_WEIGHTS,
    FACTOR_DESCRIPTIONS
)
from core.interview import (
    get_evidence_gaps,
    generate_interview_questions,
    add_interview_note
)

# 1. Page Configuration
st.set_page_config(
    page_title="Problem Statements & Scoring | SIP Discovery Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()
apply_custom_styles()
render_sidebar_status()

# 2. Header
st.markdown(
    """
    <div class="hero-header">
        <div class="hero-title">🎯 Candidate Problem Statements & Opportunity Prioritization</div>
        <p class="hero-subtitle">
            Structure qualitative observations into rigorous, falsifiable problem statements. Prioritize opportunities using a 6-factor weighted scorecard with compliance as a hard filter, and generate non-leading interview guides to validate data gaps.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.warning(
    "⚠️ **Investigative Rule:** Do **not** select a problem solely because it has the most mentions. "
    "High mention frequency often reflects loud vocal friction rather than the true systemic cause of 12-month drop-off."
)

# 3. Action Bar: Generate AI Candidates, Add Manual Candidate, or Log Interview Note
action_col1, action_col2, action_col3 = st.columns([1, 1, 1])

with action_col1:
    with st.expander("🤖 Generate Problem Candidates", expanded=False):
        theme_summaries = get_theme_summary()
        available_themes = [t["theme"] for t in theme_summaries if t["record_count"] > 0]
        if not available_themes:
            available_themes = [t["theme"] for t in theme_summaries]

        selected_theme = st.selectbox("Select Theme to investigate", available_themes)
        if st.button("Generate Candidate Statement", type="primary", key="btn_gen_prob"):
            with st.spinner(f"Formulating candidate problem from '{selected_theme}'..."):
                generated = generate_problem_statements(selected_theme)
                st.success(f"Generated {len(generated)} candidate problem statement(s)!")
                st.rerun()

with action_col2:
    with st.expander("✍️ Author Manual Problem", expanded=False):
        with st.form("manual_problem_form"):
            m_title = st.text_input("Title (e.g., Volatility Shock in Month 2)")
            m_segment = st.text_input("Target Segment", value="First-time mutual fund investors")
            m_stage = st.text_input("Journey Stage", value="Month 1–3 post initial instalment")
            m_obs = st.text_area("Observation (What the data says)")
            m_interp = st.text_area("Interpretation (What this suggests)")
            m_hyp = st.text_area("Hypothesis (Falsifiable proposition to test)")
            m_need = st.text_input("Core User Need")
            m_workaround = st.text_input("Current Workaround")
            m_limits = st.text_input("Known Limitations", value="Public reviews cannot establish 12-month retention causality.")
            submitted = st.form_submit_button("Save Candidate Problem")

            if submitted:
                if m_title.strip():
                    save_problem({
                        "title": m_title,
                        "user_segment": m_segment,
                        "journey_stage": m_stage,
                        "observation": m_obs,
                        "interpretation": m_interp,
                        "hypothesis": m_hyp,
                        "user_need": m_need,
                        "workaround": m_workaround,
                        "limitations": m_limits,
                        "validation_status": "needs_research",
                        "is_ai_generated": 0
                    })
                    st.success("Manual problem statement added!")
                    st.rerun()
                else:
                    st.error("Title is required.")

with action_col3:
    with st.expander("🎙️ Log Primary Interview Note", expanded=False):
        with st.form("interview_note_form"):
            int_resp = st.text_input("Interviewee ID / Tag (e.g., User_P1_Bangalore)", value="")
            int_date = st.date_input("Interview Date")
            int_notes = st.text_area("Verbatim Notes & Quotes", placeholder="User stated: 'I didn't realize UPI would fail silently if bank daily limit was reached...'")
            save_note = st.form_submit_button("Save Interview Note")

            if save_note:
                if int_notes.strip():
                    add_interview_note(
                        text=int_notes,
                        respondent_id=int_resp,
                        notes_date=str(int_date)
                    )
                    st.success("Primary interview note recorded in unified records!")
                    st.rerun()
                else:
                    st.error("Notes text cannot be empty.")

# 4. Evidence Gaps & Investigation Guidance
with st.expander("🔍 Evidence Gaps & Open Research Blind Spots", expanded=False):
    gaps = get_evidence_gaps()
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.markdown("**Sparse Themes (< 3 records observed):**")
        if gaps["sparse_themes"]:
            for st_theme in gaps["sparse_themes"]:
                st.markdown(f"- ⚠️ *{st_theme}*")
        else:
            st.caption("All active themes have at least 3 records.")

        st.markdown("**Contradictory Signal Themes:**")
        if gaps["contradictory_themes"]:
            for ct in gaps["contradictory_themes"]:
                st.markdown(f"- ⚡ *{ct}*")
        else:
            st.caption("No strong opposing continuation signals detected.")

    with g_col2:
        st.markdown("**Missing Context Areas from AI Audit:**")
        if gaps["missing_context_areas"]:
            for mc in gaps["missing_context_areas"]:
                st.markdown(f"- ❓ *{mc}*")
        else:
            st.caption("No common missing context patterns logged.")

st.markdown("---")

# 5. Ranked Opportunity Overview Table
st.markdown("### 🏆 Prioritized Opportunity Scorecard")

ranked_data = get_ranked_problems()

if ranked_data:
    table_rows = []
    for r in ranked_data:
        score_display = f"{r['weighted_score']:.2f} / 5.0" if r["has_score"] else "Unscored"
        status_label = r["validation_status"].replace("_", " ").title()
        
        flags = []
        if r["safety_blocked"]:
            flags.append("🚨 COMPLIANCE BLOCKED")
        if r["is_ai_generated"]:
            flags.append("🤖 AI-Generated")
        else:
            flags.append("👤 Human-Authored")

        table_rows.append({
            "Title": r["title"],
            "Validation Status": status_label,
            "Weighted Score": score_display,
            "Evidence (25%)": r.get("evidence_strength") or "-",
            "SIP Rel (25%)": r.get("sip_relevance") or "-",
            "Severity (15%)": r.get("user_severity") or "-",
            "Influence (15%)": r.get("product_influence") or "-",
            "Feasibility (10%)": r.get("feasibility") or "-",
            "Safety (10%)": r.get("safety_compliance") or "-",
            "Notes / Flags": " | ".join(flags)
        })

    df_rank = pd.DataFrame(table_rows)
    st.dataframe(df_rank, use_container_width=True, hide_index=True)
else:
    st.info("No problem statements created yet. Generate or author one above.")

st.markdown("---")

# 6. Problem Detail Cards with Interactive Scoring & Interview Guide
st.markdown("### 📋 Candidate Problem Cards & Validation")

all_problems = get_all_problems()

for p in all_problems:
    pid = p["problem_id"]
    status_val = p.get("validation_status", "needs_research")
    score_val = p.get("weighted_score")
    is_blocked = p.get("safety_compliance") is not None and p.get("safety_compliance") <= 2

    card_title = f"{p['title']} [{status_val.replace('_', ' ').upper()}]"
    if score_val:
        card_title += f" — Score: {score_val:.2f}/5.0"
    if is_blocked:
        card_title += " 🚨 [COMPLIANCE BLOCKED]"

    with st.expander(card_title, expanded=False):
        c_meta1, c_meta2, c_meta3 = st.columns(3)
        with c_meta1:
            st.markdown(f"**Segment:** {p.get('user_segment', 'N/A')}")
        with c_meta2:
            st.markdown(f"**Journey Stage:** {p.get('journey_stage', 'N/A')}")
        with c_meta3:
            origin = "🤖 AI Generated" if p.get("is_ai_generated") else "👤 Human Authored"
            st.markdown(f"**Origin:** {origin}")

        tab_obs, tab_interp, tab_hyp, tab_evid, tab_interview, tab_score, tab_manage = st.tabs([
            "🔍 Observation",
            "🧠 Interpretation",
            "🧪 Hypothesis",
            "📌 Evidence & Context",
            "🎙️ Interview Guide",
            "⚖️ Score Opportunity",
            "⚙️ Manage & Status"
        ])

        with tab_obs:
            st.markdown("#### What the data says (Factual Observation):")
            st.info(p.get("observation") or "No observation recorded.")
            if p.get("user_need"):
                st.markdown(f"**Unmet Need:** {p['user_need']}")
            if p.get("workaround"):
                st.markdown(f"**Observed Workaround:** {p['workaround']}")

        with tab_interp:
            st.markdown("#### What this suggests (Interpretation):")
            st.markdown(p.get("interpretation") or "No interpretation recorded.")
            if p.get("consequence"):
                st.markdown(f"**Consequence:** {p['consequence']}")
            if p.get("alternative_explanations"):
                st.markdown(f"**Alternative Explanations:** {p['alternative_explanations']}")

        with tab_hyp:
            st.markdown("#### What requires validation (Hypothesis):")
            st.success(p.get("hypothesis") or "No hypothesis recorded.")
            if p.get("sip_relationship"):
                st.markdown(f"**Relation to SIP Continuation:** {p['sip_relationship']}")

        with tab_evid:
            st.markdown("#### Evidence & Rigor")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.markdown("**Supporting Evidence:**")
                st.markdown(f"<div class='evidence-box'>{p.get('supporting_evidence') or 'None listed.'}</div>", unsafe_allow_html=True)
            with col_e2:
                st.markdown("**Contradictory / Nuance:**")
                st.markdown(f"<div class='evidence-box' style='border-left-color: #EC4899;'>{p.get('contradictory_evidence') or 'None listed.'}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='missing-box'>**Limitations:** {p.get('limitations') or 'None specified.'}</div>", unsafe_allow_html=True)

        with tab_interview:
            st.markdown("#### 🎙️ Non-Leading Discovery Interview Questions")
            st.caption("Neutral, open-ended questions designed to test this hypothesis without priming or biasing respondents.")
            
            if st.button("🤖 Formulate Custom AI Questions with Groq", key=f"btn_ai_q_{pid}"):
                with st.spinner("Formulating neutral questions with Groq AI..."):
                    questions = generate_interview_questions(problem_title=p["title"], use_ai=True)
            else:
                questions = generate_interview_questions(problem_title=p["title"])

            for q_idx, q in enumerate(questions, 1):
                st.markdown(f"**{q_idx}. [{q['area']}]** {q['question']}")
                st.caption(f"*Rationale:* {q['rationale']}")
                st.markdown("<br/>", unsafe_allow_html=True)

        with tab_score:
            st.markdown("#### ⚖️ 6-Factor Prioritization Scoring")
            existing_score = get_scorecard(pid) or {}

            with st.form(f"score_form_{pid}"):
                sc_col1, sc_col2 = st.columns(2)
                
                with sc_col1:
                    ev_s = st.slider("1. Evidence Strength (Weight: 25%)", 1, 5, value=existing_score.get("evidence_strength") or 3, help=FACTOR_DESCRIPTIONS["evidence_strength"])
                    sip_r = st.slider("2. SIP Continuation Relevance (Weight: 25%)", 1, 5, value=existing_score.get("sip_relevance") or 3, help=FACTOR_DESCRIPTIONS["sip_relevance"])
                    sev = st.slider("3. User Difficulty / Severity (Weight: 15%)", 1, 5, value=existing_score.get("user_severity") or 3, help=FACTOR_DESCRIPTIONS["user_severity"])

                with sc_col2:
                    prod_inf = st.slider("4. Product Influence (Weight: 15%)", 1, 5, value=existing_score.get("product_influence") or 3, help=FACTOR_DESCRIPTIONS["product_influence"])
                    feas = st.slider("5. Feasibility (Weight: 10%)", 1, 5, value=existing_score.get("feasibility") or 3, help=FACTOR_DESCRIPTIONS["feasibility"])
                    safe_c = st.slider("6. Safety & Compliance Filter (Weight: 10%)", 1, 5, value=existing_score.get("safety_compliance") or 5, help=FACTOR_DESCRIPTIONS["safety_compliance"])

                if safe_c <= 2:
                    st.error("🚨 Warning: Safety & Compliance score <= 2 triggers a HARD FILTER and blocks this problem from ranking.")

                score_just = st.text_area("Scoring Justification & Rationale", value=existing_score.get("justification") or "")
                submit_score = st.form_submit_button("Save & Update Scorecard")

                if submit_score:
                    score_dict = {
                        "evidence_strength": ev_s,
                        "sip_relevance": sip_r,
                        "user_severity": sev,
                        "product_influence": prod_inf,
                        "feasibility": feas,
                        "safety_compliance": safe_c
                    }
                    save_score(pid, score_dict, score_just)
                    st.success("Score updated successfully!")
                    st.rerun()

        with tab_manage:
            st.markdown("#### ⚙️ Validation Status & Actions")
            col_st, col_del = st.columns([2, 1])
            with col_st:
                current_idx = VALIDATION_STATUSES.index(status_val) if status_val in VALIDATION_STATUSES else 0
                new_status = st.selectbox(
                    "Update Validation Status",
                    VALIDATION_STATUSES,
                    index=current_idx,
                    key=f"status_select_{pid}"
                )
                if new_status != status_val:
                    update_validation_status(pid, new_status)
                    st.success(f"Status updated to '{new_status}'.")
                    st.rerun()

            with col_del:
                st.markdown("<br/>", unsafe_allow_html=True)
                if st.button("🗑️ Delete Statement", key=f"del_btn_{pid}"):
                    delete_problem(pid)
                    st.warning("Statement deleted.")
                    st.rerun()
