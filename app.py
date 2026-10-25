"""
app.py — Main Streamlit application entry point and router.

SIP Continuation Discovery Engine — Groq API Edition
Investigating why first-time mutual fund investors stop their SIPs within 12 months on Groww.
"""

import streamlit as st
from core.database import init_db, get_connection
from core.ui_helpers import apply_custom_styles, render_sidebar_status
from core.groq_client import get_api_key, get_model_name

# 1. Page Configuration
st.set_page_config(
    page_title="SIP Continuation Discovery Engine",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Ensure database schema exists on startup
init_db()

# 3. Apply shared modern styles
apply_custom_styles()

# 4. Render common sidebar status
render_sidebar_status()

# 5. Main landing view
st.markdown(
    """
    <div class="hero-header">
        <div class="hero-title">📈 SIP Continuation Discovery Engine</div>
        <p class="hero-subtitle">
            A PM research assistant investigating why first-time mutual fund investors on Groww pause, stop, or drop off from Systematic Investment Plans (SIPs) within their first 12 months.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Fetch current high-level metrics
with get_connection() as conn:
    total_records = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    analysed_records = conn.execute("SELECT COUNT(*) FROM analysis_results").fetchone()[0]
    review_pending = conn.execute("SELECT COUNT(*) FROM analysis_results WHERE review_status = 'pending'").fetchone()[0]
    problems_count = conn.execute("SELECT COUNT(*) FROM problem_statements").fetchone()[0]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val">{total_records}</div>
            <div class="metric-pill-label">Total Records</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val">{analysed_records}</div>
            <div class="metric-pill-label">AI Analysed</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val">{review_pending}</div>
            <div class="metric-pill-label">Pending Review</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col4:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val">{problems_count}</div>
            <div class="metric-pill-label">Problem Cards</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br/>", unsafe_allow_html=True)

# Navigation Quick Cards: Complete 8-Module Suite
st.markdown("### 🧭 Full Discovery Suite Navigation")

r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)

with r1_c1:
    st.markdown(
        """
        <div class="glass-card">
            <h4>📊 1. Dashboard</h4>
            <p style="color: #94A3B8; font-size: 0.82rem;">Relevance distributions, source coverage, and research progress charts.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/1_Dashboard.py", label="Open Dashboard", icon="📊", use_container_width=True)

with r1_c2:
    st.markdown(
        """
        <div class="glass-card">
            <h4>📥 2. Import Data</h4>
            <p style="color: #94A3B8; font-size: 0.82rem;">Upload public reviews CSVs or Google Forms survey CSVs with dedup.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/2_Import_Data.py", label="Open Importer", icon="📥", use_container_width=True)

with r1_c3:
    st.markdown(
        """
        <div class="glass-card">
            <h4>🔬 3. Explorer</h4>
            <p style="color: #94A3B8; font-size: 0.82rem;">Filter evidence, trigger Groq batch analysis, and manual triage.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/3_Research_Explorer.py", label="Open Explorer", icon="🔬", use_container_width=True)

with r1_c4:
    st.markdown(
        """
        <div class="glass-card">
            <h4>🧬 4. Themes</h4>
            <p style="color: #94A3B8; font-size: 0.82rem;">Aggregate taxonomy themes, contrast drop-offs vs continuations.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/4_Theme_Analysis.py", label="Open Themes", icon="🧬", use_container_width=True)

r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)

with r2_c1:
    st.markdown(
        """
        <div class="glass-card">
            <h4>🎯 5. Problems</h4>
            <p style="color: #94A3B8; font-size: 0.82rem;">Falsifiable cards, 6-factor opportunity scorecard, and safety filter.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/5_Problem_Statements.py", label="Open Problems", icon="🎯", use_container_width=True)

with r2_c2:
    st.markdown(
        """
        <div class="glass-card">
            <h4>⚖️ 6. AI Evaluation</h4>
            <p style="color: #94A3B8; font-size: 0.82rem;">Benchmark AI vs human labels, monitor Precision/Recall/F1 audit log.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/6_AI_Evaluation.py", label="Open AI Eval", icon="⚖️", use_container_width=True)

with r2_c3:
    st.markdown(
        """
        <div class="glass-card">
            <h4>🌐 7. Browser Inbox</h4>
            <p style="color: #94A3B8; font-size: 0.82rem;">FastAPI receiver health, review and approve Chrome extension quotes.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/7_Browser_Collection.py", label="Open Inbox", icon="🌐", use_container_width=True)

with r2_c4:
    st.markdown(
        """
        <div class="glass-card">
            <h4>📦 8. Export Hub</h4>
            <p style="color: #94A3B8; font-size: 0.82rem;">Download CSV, JSON, Markdown, and automated methodology report.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/8_Export.py", label="Open Export", icon="📦", use_container_width=True)

st.markdown("---")

# Architectural Guarantee Highlights
st.markdown("### 🛡️ Architectural & Research Integrity Guarantees")
gcol1, gcol2 = st.columns(2)

with gcol1:
    st.markdown(
        """
        - **Local-First & Secure:** All data stays in `data/sip_discovery.db`. API keys remain strictly server-side.
        - **Defensive Deduplication:** SHA-256 exact matching and sequence-matcher fuzzy near-duplicate detection.
        - **Human-in-the-Loop:** AI suggestions never override human judgment; all reviews create an immutable audit trail.
        """
    )

with gcol2:
    st.markdown(
        """
        - **Controlled AI Batching:** Safe default batch sizes (5 records) prevent quota spikes and accidental spend.
        - **Graceful Manual Fallback:** If Groq is unreachable or key is missing, manual analysis mode operates flawlessly.
        - **Compliance as a Hard Filter:** Any candidate problem scoring ≤ 2 on safety/compliance is strictly blocked.
        """
    )
