"""
core/ui_helpers.py — Shared design system, CSS styling, and visual components.

Provides:
- Modern glassmorphism dark-mode aesthetics
- Custom typography via Google Fonts (Outfit & Inter)
- Status pills, badges, metric cards
- Reusable UI headers and Groq connection status widgets
"""

import streamlit as st
from core.groq_client import test_connection, get_api_key, get_model_name
from core.database import get_connection

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

/* Typography & Base */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* Glassmorphism Card Style */
.glass-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 16px;
    backdrop-filter: blur(8px);
    transition: all 0.2s ease-in-out;
}

.glass-card:hover {
    border-color: rgba(99, 102, 241, 0.35);
    background: rgba(255, 255, 255, 0.06);
}

/* Hero Section */
.hero-header {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.12) 100%);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 24px;
}

.hero-title {
    font-size: 1.8rem;
    font-weight: 800;
    margin-bottom: 6px;
    background: linear-gradient(90deg, #FFFFFF 0%, #CBD5E1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #94A3B8;
    font-size: 0.95rem;
    margin: 0;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-right: 6px;
}

.badge-relevant {
    background: rgba(16, 185, 129, 0.18);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.35);
}

.badge-indirect {
    background: rgba(59, 130, 246, 0.18);
    color: #60A5FA;
    border: 1px solid rgba(59, 130, 246, 0.35);
}

.badge-not-relevant {
    background: rgba(107, 114, 128, 0.18);
    color: #9CA3AF;
    border: 1px solid rgba(107, 114, 128, 0.35);
}

.badge-ambiguous {
    background: rgba(245, 158, 11, 0.18);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.35);
}

.badge-source {
    background: rgba(139, 92, 246, 0.16);
    color: #A78BFA;
    border: 1px solid rgba(139, 92, 246, 0.3);
}

.badge-survey {
    background: rgba(236, 72, 153, 0.16);
    color: #F472B6;
    border: 1px solid rgba(236, 72, 153, 0.3);
}

.badge-flagged {
    background: rgba(239, 68, 68, 0.18);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
}

/* Metric Pill */
.metric-pill {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 14px 18px;
    text-align: center;
}

.metric-pill-val {
    font-family: 'Outfit', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1.1;
}

.metric-pill-label {
    font-size: 0.78rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 4px;
}

/* Status indicator pulse */
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}

.status-dot-green {
    background: #10B981;
    box-shadow: 0 0 8px #10B981;
}

.status-dot-yellow {
    background: #F59E0B;
    box-shadow: 0 0 8px #F59E0B;
}

.status-dot-red {
    background: #EF4444;
    box-shadow: 0 0 8px #EF4444;
}

/* Evidence Highlight Box */
.evidence-box {
    border-left: 3px solid #6366F1;
    background: rgba(99, 102, 241, 0.08);
    padding: 8px 14px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
    font-style: italic;
    color: #E2E8F0;
    font-size: 0.92rem;
}

.missing-box {
    border-left: 3px solid #F59E0B;
    background: rgba(245, 158, 11, 0.08);
    padding: 8px 14px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
    color: #FDE68A;
    font-size: 0.88rem;
}

/* Journey Stage Cards & Timeline */
.journey-stage-header {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.18) 0%, rgba(14, 165, 233, 0.12) 100%);
    border: 1px solid rgba(99, 102, 241, 0.35);
    border-radius: 12px;
    padding: 16px 22px;
    margin-bottom: 20px;
}

.stage-badge {
    display: inline-block;
    padding: 4px 10px;
    background: #4F46E5;
    color: #FFFFFF;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-radius: 6px;
    margin-bottom: 8px;
}

.trace-step-node {
    background: rgba(255, 255, 255, 0.03);
    border-left: 4px solid #10B981;
    border-radius: 0 10px 10px 0;
    padding: 12px 18px;
    margin-bottom: 12px;
}

.assessor-highlight-box {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(59, 130, 246, 0.10) 100%);
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
</style>
"""


def apply_custom_styles():
    """Inject custom modern CSS into the current Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_sidebar_status():
    """Render Groq API status and quick project stats in the sidebar."""
    st.sidebar.markdown("### ⚡ AI Pipeline Status")

    key = get_api_key()
    model = get_model_name()

    if not key or key == "your_key_here":
        st.sidebar.markdown(
            """
            <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 10px 12px; margin-bottom: 12px;">
                <span class="status-dot status-dot-yellow"></span>
                <strong style="color: #FBBF24;">Manual Mode</strong>
                <div style="font-size: 0.8rem; color: #D1D5DB; margin-top: 4px;">GROQ_API_KEY not configured in .env. Analysis runs in manual label mode.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.sidebar.markdown(
            f"""
            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 10px 12px; margin-bottom: 12px;">
                <span class="status-dot status-dot-green"></span>
                <strong style="color: #34D399;">Groq Connected</strong>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 4px;">Model: <code>{model}</code></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Connection Test expander / trigger
    with st.sidebar.expander("🔍 Run Connection Diagnostic"):
        if st.button("Test Groq Connection", use_container_width=True, key="side_test_conn_btn"):
            with st.spinner("Testing API connection..."):
                diag = test_connection()
                if diag["all_passed"]:
                    st.success("All 5 diagnostic steps passed!")
                else:
                    st.error("Diagnostic encountered issues:")
                for s in diag["steps"]:
                    icon = "✅" if s["success"] else "❌"
                    st.markdown(f"**Step {s['step']}: {s['name']}** {icon}")
                    st.caption(s["message"])

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Research Stats")

    # Fetch live stats from DB
    try:
        with get_connection() as conn:
            total_recs = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
            analysed_recs = conn.execute("SELECT COUNT(*) FROM analysis_results").fetchone()[0]
            pending_review = conn.execute("SELECT COUNT(*) FROM analysis_results WHERE review_status = 'pending'").fetchone()[0]
            sources_count = conn.execute("SELECT COUNT(*) FROM source_register").fetchone()[0]

        st.sidebar.markdown(
            f"""
            <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.8;">
                📁 <strong>Total Records:</strong> {total_recs}<br/>
                🤖 <strong>Analysed:</strong> {analysed_recs}<br/>
                ⏳ <strong>Pending Review:</strong> {pending_review}<br/>
                📚 <strong>Sources Registered:</strong> {sources_count}
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        st.sidebar.caption("Database not initialized yet.")
