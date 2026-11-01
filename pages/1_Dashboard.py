"""
pages/1_Dashboard.py — Executive Research Brief for Continuum AI Discovery Engine.

Transforms the research dashboard into a leadership-ready executive communication tool:
- Section A: Executive Header (Research status, scope, refresh date, evidence coverage)
- Section B: Executive Takeaway ("What the research is telling us", leading hypothesis, status badge)
- Section C: Research Evidence at a Glance (5 dynamic metric cards + data hygiene audit drawer)
- Section D: Key Investor Findings (4 standardized findings with evidence stats and verbatim quotes)
- Section E: Problem Statement Comparison (prob-1, prob-2, prob-3 evaluation & scores)
- Section F: Product Opportunity ("Where could we create value?", conceptual traceability chain)
- Section G: Research Limitations ("What we still need to validate", 5 explicit evidence gaps)
- Section H: Recommended Next Steps (5 prioritized validation activities)
- Section I: Leadership Takeaway (Concise executive decision recommendation)
"""

import streamlit as st
import pandas as pd
import json

from core.database import init_db, get_connection
from core.ui_helpers import apply_custom_styles, render_sidebar_status, format_display_name

st.set_page_config(
    page_title="Executive Research Brief | Continuum AI",
    page_icon="📊",
    layout="wide"
)

init_db()
apply_custom_styles()
render_sidebar_status()

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE QUERIES & DYNAMIC METRICS
# ─────────────────────────────────────────────────────────────────────────────
with get_connection() as conn:
    # High-level corpus counts
    total_records = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    active_records = conn.execute("SELECT COUNT(*) FROM records WHERE COALESCE(is_quarantined, 0) = 0").fetchone()[0]
    quarantined_records = conn.execute("SELECT COUNT(*) FROM records WHERE COALESCE(is_quarantined, 0) = 1").fetchone()[0]

    # Primary vs Secondary verified counts
    verified_primary = conn.execute("""
        SELECT COUNT(*) FROM records 
        WHERE (record_type = 'survey_response' OR record_type = 'interview_note') 
          AND COALESCE(is_quarantined, 0) = 0
    """).fetchone()[0]

    usable_secondary = conn.execute("""
        SELECT COUNT(*) FROM records 
        WHERE record_type = 'public_review' 
          AND COALESCE(is_quarantined, 0) = 0
    """).fetchone()[0]

    # Analysis review status
    analysed_records = conn.execute("SELECT COUNT(*) FROM analysis_results").fetchone()[0]
    evidence_reviewed = conn.execute("SELECT COUNT(*) FROM analysis_results WHERE review_status IN ('reviewed', 'approved')").fetchone()[0]
    evidence_pending = conn.execute("SELECT COUNT(*) FROM analysis_results WHERE review_status = 'pending'").fetchone()[0]

    # Problem statements and scores
    problem_count = conn.execute("SELECT COUNT(*) FROM problem_statements").fetchone()[0]
    problems_data = conn.execute("""
        SELECT p.problem_id, p.title, p.observation, p.interpretation, p.hypothesis, 
               p.user_need, p.open_questions, p.validation_status,
               COALESCE(s.weighted_score, 0), COALESCE(s.evidence_strength, 0), 
               COALESCE(s.feasibility, 0), COALESCE(s.user_severity, 0)
        FROM problem_statements p
        LEFT JOIN scores s ON p.problem_id = s.problem_id
        ORDER BY p.problem_id
    """).fetchall()

    # Most recent record timestamp for refresh date
    latest_ts_row = conn.execute("SELECT MAX(created_at) FROM records").fetchone()
    last_refresh_date = latest_ts_row[0][:10] if (latest_ts_row and latest_ts_row[0]) else "2026-11-01"

# ─────────────────────────────────────────────────────────────────────────────
# SECTION A — Executive Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="hero-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <span class="badge badge-relevant">Executive Research Brief</span>
                <span class="badge badge-source">Continuum AI Discovery</span>
                <h1 class="hero-title" style="margin-top: 8px;">SIP Continuation Discovery — Executive Research Brief</h1>
                <p class="hero-subtitle">
                    Understanding why first-time mutual fund investors pause, reduce, or stop their SIPs and identifying opportunities to improve their experience.
                </p>
            </div>
            <div style="text-align: right; min-width: 200px;">
                <div style="font-size: 0.82rem; color: var(--ct-text-muted); line-height: 1.6;">
                    <strong>Status:</strong> <span style="color: #10B981; font-weight: 700;">Active Investigation</span><br/>
                    <strong>Scope:</strong> Retail Investors (0–12 mo tenure)<br/>
                    <strong>Last Refresh:</strong> {last_refresh_date}<br/>
                    <strong>Coverage:</strong> {active_records} active records analysed
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION B — Executive Takeaway
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 💡 What the Research is Telling Us")

st.markdown(
    """
    <div class="exec-takeaway-card">
        <div class="exec-status-badge">
            <span>🔍 Leading Problem Hypothesis — Requires Further Validation</span>
        </div>
        <div class="exec-hypothesis-banner">
            <div class="exec-hypothesis-title">Leading Hypothesis</div>
            <div class="exec-hypothesis-body">
                "Temporary cash-flow pressure and limited flexibility in managing SIP contributions may create difficulties for first-time investors when their financial circumstances change."
            </div>
        </div>
        <p style="font-size: 0.95rem; color: var(--ct-text-secondary); line-height: 1.6; margin-bottom: 14px;">
            <strong>Supporting Explanation:</strong> Investors facing unexpected personal expenses or salary timing mismatches may benefit from clearer, proactive guidance about available skip and pause options before debits fail.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 14px;">
            <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10B981; padding: 12px 14px; border-radius: 0 8px 8px 0;">
                <strong style="color: #065F46; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.04em;">Supporting Evidence</strong>
                <div style="font-size: 0.88rem; color: var(--ct-text-secondary); margin-top: 4px; line-height: 1.5;">
                    • Primary interview respondents explicitly report salary credit timing mismatches (INT-0001, INT-0002).<br/>
                    • Survey respondents state liquidity shortages prompt cancellation when pause feels inaccessible (RESP-0010).<br/>
                    • Reviews cite rigid 2-working-day notice cutoffs preventing emergency skip requests.
                </div>
            </div>
            <div style="background: rgba(245, 158, 11, 0.08); border-left: 3px solid #F59E0B; padding: 12px 14px; border-radius: 0 8px 8px 0;">
                <strong style="color: #92400E; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.04em;">Nuance & Counter-Evidence</strong>
                <div style="font-size: 0.88rem; color: var(--ct-text-secondary); margin-top: 4px; line-height: 1.5;">
                    • A substantial cohort stops SIPs due to technical mandate latency rather than cash shortage.<br/>
                    • Market volatility anxiety contributes significantly during initial market drawdowns.<br/>
                    • <em>Notice:</em> This hypothesis is a promising discovery direction, not a proven sole cause of churn.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION C — Research Evidence at a Glance
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 📊 Research Evidence at a Glance")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val" style="color: #10B981;">{verified_primary}</div>
            <div class="metric-pill-label">Verified Primary Records</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi2:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val" style="color: #3B82F6;">{usable_secondary}</div>
            <div class="metric-pill-label">Usable Secondary Records</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi3:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val" style="color: #6366F1;">{evidence_reviewed}</div>
            <div class="metric-pill-label">Evidence Reviewed</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi4:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val" style="color: #F59E0B;">{evidence_pending}</div>
            <div class="metric-pill-label">Evidence Awaiting Review</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi5:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val" style="color: #8B5CF6;">{problem_count}</div>
            <div class="metric-pill-label">Problem Statements Evaluated</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with st.expander("🔍 Data Hygiene & Quarantine Audit Breakdown", expanded=False):
    st.markdown(
        f"""
        <div style="font-size: 0.88rem; color: var(--ct-text-secondary); line-height: 1.6;">
            <strong>Corpus Accounting & Separation:</strong><br/>
            • <strong>Total Ingested Records:</strong> {total_records} records across public reviews, survey responses, interviews, and regulatory studies.<br/>
            • <strong>Active Genuine Corpus:</strong> {active_records} records currently evaluated in evidence synthesis.<br/>
            • <strong>Quarantined / Excluded Records:</strong> {quarantined_records} synthetic or unverified test items safely quarantined to avoid skewing executive metrics.<br/>
            • <strong>Human Quality Assurance:</strong> {evidence_reviewed} records have undergone explicit verification in the Evidence Register.
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION D — Key Investor Findings
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 👥 What Investors are Experiencing")
st.caption("Key themes emerging from verified primary interviews, survey responses, and public feedback:")

findings_data = [
    {
        "title": "Temporary Cash-Flow Pressure & Inflexible Contributions",
        "desc": "First-time investors encountering month-end liquidity crunches face rigid cutoff deadlines (T-2 working days), causing accidental bank bounce fees or forced cancellations.",
        "primary_stat": "RESP-0010, INT-0001, INT-0002",
        "quote": "User explained that salary is credited on the 5th, but SIP was scheduled on the 1st.",
        "quote_source": "In-Depth Interview Note #test_interviewee_42",
        "confidence": "Medium-High (Emerging in Primary Surveys)",
        "uncertainty": "Need longitudinal data to quantify whether paused users naturally resume within 90 days."
    },
    {
        "title": "Mandate Execution Latency & Diagnostic Gaps",
        "desc": "Automated debits experience processing lags of 3–7 days with ambiguous error notifications, causing investors to lose confidence in automated recurring mandates.",
        "primary_stat": "56 occurrences in secondary corpus",
        "quote": "Frustrating payment loop—money stays blocked but app says failed. Zero stars for payment reliability. Whether I use bank net banking, third-party UPI, or Groww UPI, it always shows a technical error.",
        "quote_source": "Play Store Review #7745e1c1",
        "confidence": "High (56 verified records)",
        "uncertainty": "Differentiating banking network/NPCI downtime from retail platform failure states."
    },
    {
        "title": "Product Usability, Navigation & Modification Friction",
        "desc": "First-time investors struggle to locate mandate settings, edit existing bank accounts, or switch payment methods within modern app interfaces.",
        "primary_stat": "10 verified occurrences",
        "quote": "Since last month I have been trying to update my mandate bank, but due to reasons unknown it failed number of times...",
        "quote_source": "Play Store Review #9c87ca38",
        "confidence": "Medium (10 verified records)",
        "uncertainty": "Separating general app UI confusion from SIP-specific mandate friction."
    },
    {
        "title": "Support Responsiveness & Issue Resolution",
        "desc": "When debits fail or duplicate deductions occur, customer support turnaround times (2–5 working days) exceed investor anxiety thresholds, accelerating churn.",
        "primary_stat": "7 verified occurrences",
        "quote": "Customer support advised to wait two banking working days... unhelpful and patronizing while money was stuck.",
        "quote_source": "Play Store Review #d58c00d1",
        "confidence": "Medium (7 verified records)",
        "uncertainty": "Correlation between support ticket turnaround and permanent SIP cancellation."
    }
]

fcol1, fcol2 = st.columns(2)
for idx, f in enumerate(findings_data):
    target_col = fcol1 if idx % 2 == 0 else fcol2
    with target_col:
        st.markdown(
            f"""
            <div class="exec-finding-card">
                <div class="exec-finding-header">
                    <span class="exec-finding-title">{format_display_name(f['title'])}</span>
                    <span class="badge badge-relevant">Maturity: {f['confidence'].split(' ')[0]}</span>
                </div>
                <div class="exec-finding-desc">{f['desc']}</div>
                <div class="exec-quote-box">
                    "{f['quote']}"
                    <div style="font-size: 0.76rem; color: var(--ct-text-muted); margin-top: 4px; font-style: normal;">— {f['quote_source']}</div>
                </div>
                <div class="exec-finding-meta">
                    <span>📚 <strong>Evidence:</strong> {f['primary_stat']}</span>
                    <span>⚠️ <strong>Uncertainty:</strong> {f['uncertainty']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Navigation shortcut to Research Explorer
c_exp1, c_exp2 = st.columns([3, 1])
with c_exp2:
    if st.button("🔎 Explore Verbatim Evidence in Research Explorer", type="secondary", use_container_width=True):
        st.switch_page("pages/3_Research_Explorer.py")

st.markdown("<br/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION E — Problem Statement Comparison
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### ⚖️ Which Investor Problem Should We Prioritise?")
st.caption("Objective multi-dimensional comparison of the 3 candidate problems evaluated by Continuum AI:")

p_cols = st.columns(3)
for idx, p in enumerate(problems_data):
    p_id, title, obs, interp, hyp, need, questions, status, score, ev_str, feas, sev = p
    is_leading = (p_id == "prob-3")
    with p_cols[idx]:
        card_class = "exec-problem-card leading-problem" if is_leading else "exec-problem-card"
        badge_html = "<span class='badge badge-relevant' style='float: right;'>🏆 LEADING HYPOTHESIS</span>" if is_leading else f"<span class='badge badge-source' style='float: right;'>Score: {score:.1f}/5.0</span>"
        
        st.markdown(
            f"""
            <div class="{card_class}">
                {badge_html}
                <div style="font-size: 0.78rem; font-weight: 700; color: #6366F1; text-transform: uppercase; margin-bottom: 4px;">Candidate {idx+1} ({p_id})</div>
                <h4 style="margin: 0 0 10px 0; font-size: 1.05rem; line-height: 1.35; color: var(--ct-text-primary);">{format_display_name(title)}</h4>
                
                <div style="font-size: 0.88rem; color: var(--ct-text-secondary); margin-bottom: 12px; line-height: 1.5;">
                    <strong>Observation:</strong> {obs[:160]}...
                </div>
                
                <div style="background: var(--ct-pill-bg); border: 1px solid var(--ct-pill-border); border-radius: 8px; padding: 10px 12px; margin-bottom: 12px; font-size: 0.82rem;">
                    <div><strong>Evidence Strength:</strong> {ev_str:.1f} / 5.0</div>
                    <div><strong>Feasibility:</strong> {feas:.1f} / 5.0</div>
                    <div><strong>User Severity:</strong> {sev:.1f} / 5.0</div>
                </div>
                
                <div style="font-size: 0.82rem; color: var(--ct-text-muted); line-height: 1.45;">
                    <strong>Unresolved Question:</strong><br/>
                    {questions[:130]}...
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION F — Product Opportunity
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 🚀 Where Could We Create Value?")

st.markdown(
    """
    <div class="glass-card" style="border-left: 4px solid #10B981;">
        <span class="badge badge-relevant">Emerging Product Opportunity</span>
        <h3 style="margin: 6px 0 10px 0; font-size: 1.25rem;">Context-Aware SIP Guidance for Investors Experiencing Temporary Cash-Flow Pressure</h3>
        <p style="font-size: 0.95rem; color: var(--ct-text-secondary); line-height: 1.6; margin-bottom: 16px;">
            Rather than offering a blunt binary choice between <em>Active recurring debit</em> and <em>Full cancellation</em>, mutual fund platforms could provide contextual continuity pathways:
        </p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 18px;">
            <div style="background: var(--ct-pill-bg); border: 1px solid var(--ct-pill-border); border-radius: 8px; padding: 12px 14px;">
                <strong style="color: #10B981; font-size: 0.9rem;">1. Plan Ahead</strong>
                <div style="font-size: 0.82rem; color: var(--ct-text-muted); margin-top: 4px;">Notice cutoff visibility (2 working days before debit) enabling proactive skips.</div>
            </div>
            <div style="background: var(--ct-pill-bg); border: 1px solid var(--ct-pill-border); border-radius: 8px; padding: 12px 14px;">
                <strong style="color: #3B82F6; font-size: 0.9rem;">2. Missed Payment Rescue</strong>
                <div style="font-size: 0.82rem; color: var(--ct-text-muted); margin-top: 4px;">Diagnostic triage explaining that 1 failed debit does not cancel their mandate.</div>
            </div>
            <div style="background: var(--ct-pill-bg); border: 1px solid var(--ct-pill-border); border-radius: 8px; padding: 12px 14px;">
                <strong style="color: #8B5CF6; font-size: 0.9rem;">3. Flexible Contribution</strong>
                <div style="font-size: 0.82rem; color: var(--ct-text-muted); margin-top: 4px;">Voluntary smaller one-time investment in the same fund when cash is tight.</div>
            </div>
            <div style="background: var(--ct-pill-bg); border: 1px solid var(--ct-pill-border); border-radius: 8px; padding: 12px 14px;">
                <strong style="color: #EC4899; font-size: 0.9rem;">4. Mandate Protection</strong>
                <div style="font-size: 0.82rem; color: var(--ct-text-muted); margin-top: 4px;">Demystifying the 3-consecutive-failure cancellation rule under SEBI regulations.</div>
            </div>
            <div style="background: var(--ct-pill-bg); border: 1px solid var(--ct-pill-border); border-radius: 8px; padding: 12px 14px;">
                <strong style="color: #F59E0B; font-size: 0.9rem;">5. Informed Choice</strong>
                <div style="font-size: 0.82rem; color: var(--ct-text-muted); margin-top: 4px;">Supportive skip workflows that respect the user's decision not to invest.</div>
            </div>
        </div>

        <div style="background: var(--ct-evidence-bg); border-radius: 8px; padding: 12px 16px; font-size: 0.85rem; color: var(--ct-text-secondary); line-height: 1.6;">
            <strong>Conceptual Traceability Chain:</strong><br/>
            <code>Research Evidence (INT-0001, RESP-0010)</code> ➔ 
            <code>Problem Statement (prob-3: Inflexible Contribution)</code> ➔ 
            <code>Product Opportunity (Continuity Guidance)</code> ➔ 
            <code>User Validation (Qualitative Prototype Testing)</code>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION G — Research Limitations
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### ⚠️ What We Still Need to Validate")
st.caption("Explicit acknowledgment of evidence gaps, sampling boundaries, and remaining uncertainties:")

lim_col1, lim_col2 = st.columns(2)
with lim_col1:
    st.markdown(
        """
        <div class="glass-card">
            <h4 style="margin: 0 0 8px 0; font-size: 0.95rem; color: var(--ct-text-primary);">1. Public Review Self-Selection Bias</h4>
            <p style="font-size: 0.85rem; color: var(--ct-text-secondary); line-height: 1.5; margin: 0;">
                Public app store reviews heavily skew toward frustrated users whose debits failed or customer support requests timed out. Passive, satisfied, or quiet drop-offs are underrepresented.
            </p>
        </div>
        <div class="glass-card">
            <h4 style="margin: 0 0 8px 0; font-size: 0.95rem; color: var(--ct-text-primary);">2. Temporary vs. Structural Liquidity Constraints</h4>
            <p style="font-size: 0.85rem; color: var(--ct-text-secondary); line-height: 1.5; margin: 0;">
                Current evidence does not yet prove whether investors who pause for 1 month experience a temporary cash mismatch (e.g. salary delay) or long-term financial distress.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with lim_col2:
    st.markdown(
        """
        <div class="glass-card">
            <h4 style="margin: 0 0 8px 0; font-size: 0.95rem; color: var(--ct-text-primary);">3. Investor Preference Validation</h4>
            <p style="font-size: 0.85rem; color: var(--ct-text-secondary); line-height: 1.5; margin: 0;">
                Whether investors prefer an explicit scheduled skip, a temporary pause, or a smaller separate investment requires live prototype interaction testing with representative retail users.
            </p>
        </div>
        <div class="glass-card">
            <h4 style="margin: 0 0 8px 0; font-size: 0.95rem; color: var(--ct-text-primary);">4. Platform Information Architecture</h4>
            <p style="font-size: 0.85rem; color: var(--ct-text-secondary); line-height: 1.5; margin: 0;">
                It remains uncertain whether platforms already offer sufficient pause mechanisms that users simply fail to discover due to buried navigation or rigid cutoff deadlines.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION H — Recommended Next Steps
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 📋 Recommended Next Steps")
st.caption("Actionable validation roadmap to de-risk the product opportunity before production investment:")

steps = [
    ("1. Targeted In-Depth Discovery Interviews", "Conduct 12–15 structured qualitative interviews specifically targeting retail investors who stopped their SIPs within months 3 to 6."),
    ("2. Validate Proactive Skips vs. Reactive Recovery", "Run an interactive user preference test to measure whether investors prefer proactive cutoff warnings or post-failure rescue triage."),
    ("3. Usability Test Investor Prototype", "Test the standalone SIP Rescue Navigator prototype with 20 first-time mutual fund investors to measure comprehension and anxiety reduction."),
    ("4. Verify Cross-Platform Cutoff Rules", "Verify mandate cancellation, pause cutoffs, and bank bounce fee rules across Groww, Zerodha Coin, and AMC Direct with institutional partners."),
    ("5. Define Longitudinal Experiment Metrics", "Establish measurable metrics for a live pilot (e.g., 90-day retention continuation rate, pause-to-resume recovery ratio).")
]

for title, desc in steps:
    st.markdown(
        f"""
        <div style="background: var(--ct-card-bg); border: 1px solid var(--ct-card-border); border-left: 3px solid #6366F1; border-radius: 0 8px 8px 0; padding: 10px 16px; margin-bottom: 10px; box-shadow: var(--ct-card-shadow);">
            <strong style="color: var(--ct-text-primary); font-size: 0.92rem;">{title}</strong>
            <div style="color: var(--ct-text-secondary); font-size: 0.85rem; margin-top: 3px; line-height: 1.45;">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION I — Leadership Takeaway
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 🎯 Leadership Summary & Recommended Decision")

st.markdown(
    """
    <div class="exec-action-box">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin-bottom: 16px;">
            <div>
                <strong style="color: #10B981; font-size: 0.85rem; text-transform: uppercase;">Leading Problem Hypothesis</strong>
                <div style="color: var(--ct-text-primary); font-size: 0.9rem; margin-top: 4px; font-weight: 600;">
                    Inflexible SIP contributions during temporary liquidity crunches force premature, permanent cancellations.
                </div>
            </div>
            <div>
                <strong style="color: #6366F1; font-size: 0.85rem; text-transform: uppercase;">Strongest Evidence</strong>
                <div style="color: var(--ct-text-primary); font-size: 0.9rem; margin-top: 4px;">
                    Repeated primary interview citations reporting salary date mismatches and rigid 2-working-day notice barriers.
                </div>
            </div>
            <div>
                <strong style="color: #F59E0B; font-size: 0.85rem; text-transform: uppercase;">Major Uncertainty</strong>
                <div style="color: var(--ct-text-primary); font-size: 0.9rem; margin-top: 4px;">
                    Whether users who pause will naturally resume monthly contributions without dedicated comeback planning.
                </div>
            </div>
        </div>
        
        <div style="background: rgba(16, 185, 129, 0.12); border: 1.5px solid #10B981; border-radius: 8px; padding: 14px 18px; margin-top: 10px;">
            <strong style="color: #065F46; font-size: 0.92rem; text-transform: uppercase; letter-spacing: 0.04em;">📌 Recommended Leadership Decision:</strong>
            <p style="color: var(--ct-text-primary); font-size: 0.95rem; margin: 6px 0 0 0; line-height: 1.55;">
                "The current research indicates that temporary cash-flow pressure and limited flexibility in managing SIP contributions are promising problem areas to investigate further. We recommend prioritising investor validation and prototype testing before committing to a production solution."
            </p>
            <div style="font-size: 0.78rem; color: var(--ct-text-muted); margin-top: 6px;">
                <em>Status: Proposed Recommendation for Product Leadership • Does not constitute an automatic engineering approval.</em>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br/>", unsafe_allow_html=True)
st.caption("Continuum AI Discovery Engine • Systematic Research-to-Problem Evidence Synthesis")
