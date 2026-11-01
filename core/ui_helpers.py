"""
core/ui_helpers.py — Shared design system, CSS styling, and visual components.

Provides:
- WCAG AA compliant dual-theme typography and styling (Light & Dark mode)
- Standardized title casing helper (format_display_name)
- Status pills, badges, metric cards
- Reusable UI headers and Groq connection status widgets
"""

import streamlit as st
from core.groq_client import test_connection, get_api_key, get_model_name
from core.database import get_connection

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

/* Typography & Base */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* ==========================================================================
   WCAG AA Dual Theme Tokens (Light & Dark Mode)
   ========================================================================== */

/* Default Light Theme Tokens */
:root {
    --ct-text-primary: #0F172A;
    --ct-text-secondary: #334155;
    --ct-text-muted: #64748B;
    --ct-card-bg: #FFFFFF;
    --ct-card-border: #E2E8F0;
    --ct-card-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
    --ct-hero-bg: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
    --ct-hero-border: #C7D2FE;
    --ct-hero-title: #0F172A;
    --ct-hero-sub: #475569;
    --ct-pill-bg: #F8FAFC;
    --ct-pill-border: #E2E8F0;
    --ct-evidence-bg: #F1F5F9;
    --ct-evidence-text: #0F172A;
    --ct-badge-green-bg: #ECFDF5;
    --ct-badge-green-text: #065F46;
    --ct-badge-green-border: #A7F3D0;
    --ct-badge-amber-bg: #FFFBEB;
    --ct-badge-amber-text: #92400E;
    --ct-badge-amber-border: #FDE68A;
    --ct-badge-purple-bg: #FAF5FF;
    --ct-badge-purple-text: #581C87;
    --ct-badge-purple-border: #DDD6FE;
    --ct-badge-blue-bg: #EFF6FF;
    --ct-badge-blue-text: #1E40AF;
    --ct-badge-blue-border: #BFDBFE;
}

/* Dark Theme Tokens Override */
@media (prefers-color-scheme: dark) {
    :root {
        --ct-text-primary: #F8FAFC;
        --ct-text-secondary: #CBD5E1;
        --ct-text-muted: #94A3B8;
        --ct-card-bg: rgba(255, 255, 255, 0.04);
        --ct-card-border: rgba(255, 255, 255, 0.08);
        --ct-card-shadow: none;
        --ct-hero-bg: linear-gradient(135deg, rgba(99, 102, 241, 0.18) 0%, rgba(168, 85, 247, 0.12) 100%);
        --ct-hero-border: rgba(99, 102, 241, 0.35);
        --ct-hero-title: #FFFFFF;
        --ct-hero-sub: #94A3B8;
        --ct-pill-bg: rgba(255, 255, 255, 0.03);
        --ct-pill-border: rgba(255, 255, 255, 0.08);
        --ct-evidence-bg: rgba(99, 102, 241, 0.08);
        --ct-evidence-text: #F1F5F9;
        --ct-badge-green-bg: rgba(16, 185, 129, 0.18);
        --ct-badge-green-text: #34D399;
        --ct-badge-green-border: rgba(16, 185, 129, 0.35);
        --ct-badge-amber-bg: rgba(245, 158, 11, 0.18);
        --ct-badge-amber-text: #FBBF24;
        --ct-badge-amber-border: rgba(245, 158, 11, 0.35);
        --ct-badge-purple-bg: rgba(139, 92, 246, 0.16);
        --ct-badge-purple-text: #A78BFA;
        --ct-badge-purple-border: rgba(139, 92, 246, 0.3);
        --ct-badge-blue-bg: rgba(59, 130, 246, 0.18);
        --ct-badge-blue-text: #60A5FA;
        --ct-badge-blue-border: rgba(59, 130, 246, 0.35);
    }
}

/* Streamlit Theme Overrides (when user toggles in Settings) */
[data-theme="light"], .stApp[data-theme="light"] {
    --ct-text-primary: #0F172A;
    --ct-text-secondary: #334155;
    --ct-text-muted: #64748B;
    --ct-card-bg: #FFFFFF;
    --ct-card-border: #E2E8F0;
    --ct-card-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    --ct-hero-bg: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
    --ct-hero-border: #C7D2FE;
    --ct-hero-title: #0F172A;
    --ct-hero-sub: #475569;
    --ct-pill-bg: #F8FAFC;
    --ct-pill-border: #E2E8F0;
    --ct-evidence-bg: #F1F5F9;
    --ct-evidence-text: #0F172A;
    --ct-badge-green-bg: #ECFDF5;
    --ct-badge-green-text: #065F46;
    --ct-badge-green-border: #A7F3D0;
    --ct-badge-amber-bg: #FFFBEB;
    --ct-badge-amber-text: #92400E;
    --ct-badge-amber-border: #FDE68A;
    --ct-badge-purple-bg: #FAF5FF;
    --ct-badge-purple-text: #581C87;
    --ct-badge-purple-border: #DDD6FE;
    --ct-badge-blue-bg: #EFF6FF;
    --ct-badge-blue-text: #1E40AF;
    --ct-badge-blue-border: #BFDBFE;
}

[data-theme="dark"], .stApp[data-theme="dark"] {
    --ct-text-primary: #F8FAFC;
    --ct-text-secondary: #CBD5E1;
    --ct-text-muted: #94A3B8;
    --ct-card-bg: rgba(255, 255, 255, 0.04);
    --ct-card-border: rgba(255, 255, 255, 0.08);
    --ct-card-shadow: none;
    --ct-hero-bg: linear-gradient(135deg, rgba(99, 102, 241, 0.18) 0%, rgba(168, 85, 247, 0.12) 100%);
    --ct-hero-border: rgba(99, 102, 241, 0.35);
    --ct-hero-title: #FFFFFF;
    --ct-hero-sub: #94A3B8;
    --ct-pill-bg: rgba(255, 255, 255, 0.03);
    --ct-pill-border: rgba(255, 255, 255, 0.08);
    --ct-evidence-bg: rgba(99, 102, 241, 0.08);
    --ct-evidence-text: #F1F5F9;
    --ct-badge-green-bg: rgba(16, 185, 129, 0.18);
    --ct-badge-green-text: #34D399;
    --ct-badge-green-border: rgba(16, 185, 129, 0.35);
    --ct-badge-amber-bg: rgba(245, 158, 11, 0.18);
    --ct-badge-amber-text: #FBBF24;
    --ct-badge-amber-border: rgba(245, 158, 11, 0.35);
    --ct-badge-purple-bg: rgba(139, 92, 246, 0.16);
    --ct-badge-purple-text: #A78BFA;
    --ct-badge-purple-border: rgba(139, 92, 246, 0.3);
    --ct-badge-blue-bg: rgba(59, 130, 246, 0.18);
    --ct-badge-blue-text: #60A5FA;
    --ct-badge-blue-border: rgba(59, 130, 246, 0.35);
}

/* Card Style */
.glass-card {
    background: var(--ct-card-bg);
    border: 1px solid var(--ct-card-border);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 16px;
    box-shadow: var(--ct-card-shadow);
    color: var(--ct-text-primary);
    transition: all 0.2s ease-in-out;
}

.glass-card:hover {
    border-color: #6366F1;
}

/* Hero Section */
.hero-header {
    background: var(--ct-hero-bg);
    border: 1px solid var(--ct-hero-border);
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: var(--ct-card-shadow);
}

.hero-title {
    font-size: 1.85rem;
    font-weight: 800;
    margin-bottom: 6px;
    color: var(--ct-hero-title);
    letter-spacing: -0.02em;
}

.hero-subtitle {
    color: var(--ct-hero-sub);
    font-size: 0.95rem;
    line-height: 1.5;
    margin: 0;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-right: 6px;
}

.badge-relevant {
    background: var(--ct-badge-green-bg);
    color: var(--ct-badge-green-text);
    border: 1px solid var(--ct-badge-green-border);
}

.badge-indirect {
    background: var(--ct-badge-blue-bg);
    color: var(--ct-badge-blue-text);
    border: 1px solid var(--ct-badge-blue-border);
}

.badge-not-relevant {
    background: rgba(107, 114, 128, 0.14);
    color: var(--ct-text-muted);
    border: 1px solid rgba(107, 114, 128, 0.25);
}

.badge-ambiguous {
    background: var(--ct-badge-amber-bg);
    color: var(--ct-badge-amber-text);
    border: 1px solid var(--ct-badge-amber-border);
}

.badge-source {
    background: var(--ct-badge-purple-bg);
    color: var(--ct-badge-purple-text);
    border: 1px solid var(--ct-badge-purple-border);
}

.badge-survey {
    background: rgba(236, 72, 153, 0.12);
    color: #BE185D;
    border: 1px solid rgba(236, 72, 153, 0.25);
}

.badge-flagged {
    background: rgba(239, 68, 68, 0.12);
    color: #B91C1C;
    border: 1px solid rgba(239, 68, 68, 0.25);
}

/* Metric Pill */
.metric-pill {
    background: var(--ct-pill-bg);
    border: 1px solid var(--ct-pill-border);
    border-radius: 10px;
    padding: 14px 18px;
    text-align: center;
    box-shadow: var(--ct-card-shadow);
}

.metric-pill-val {
    font-family: 'Outfit', sans-serif;
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--ct-text-primary);
    line-height: 1.1;
}

.metric-pill-label {
    font-size: 0.78rem;
    color: var(--ct-text-muted);
    font-weight: 600;
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
    background: var(--ct-evidence-bg);
    padding: 10px 16px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
    font-style: italic;
    color: var(--ct-evidence-text);
    font-size: 0.92rem;
    line-height: 1.5;
}

.missing-box {
    border-left: 3px solid #F59E0B;
    background: var(--ct-badge-amber-bg);
    padding: 10px 16px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
    color: var(--ct-badge-amber-text);
    font-size: 0.88rem;
    line-height: 1.5;
}

/* Executive Brief Component Styles */
.exec-takeaway-card {
    background: var(--ct-card-bg);
    border: 1.5px solid #10B981;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 22px;
    box-shadow: var(--ct-card-shadow);
}

.exec-hypothesis-banner {
    background: var(--ct-badge-green-bg);
    border: 1px solid var(--ct-badge-green-border);
    border-radius: 8px;
    padding: 14px 18px;
    margin: 12px 0 16px 0;
}

.exec-hypothesis-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--ct-badge-green-text);
    margin-bottom: 4px;
}

.exec-hypothesis-body {
    font-size: 0.95rem;
    color: var(--ct-text-secondary);
    line-height: 1.55;
    margin: 0;
}

.exec-status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    background: var(--ct-badge-amber-bg);
    border: 1px solid var(--ct-badge-amber-border);
    color: var(--ct-badge-amber-text);
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-radius: 9999px;
    margin-bottom: 12px;
}

.exec-finding-card {
    background: var(--ct-card-bg);
    border: 1px solid var(--ct-card-border);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: var(--ct-card-shadow);
    color: var(--ct-text-primary);
}

.exec-finding-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 6px;
}

.exec-finding-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--ct-text-primary);
}

.exec-finding-desc {
    font-size: 0.92rem;
    color: var(--ct-text-secondary);
    line-height: 1.5;
    margin-bottom: 10px;
}

.exec-finding-meta {
    font-size: 0.8rem;
    color: var(--ct-text-muted);
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 8px;
}

.exec-quote-box {
    background: var(--ct-evidence-bg);
    border-left: 3px solid #6366F1;
    border-radius: 0 8px 8px 0;
    padding: 8px 14px;
    margin: 8px 0;
    font-size: 0.88rem;
    font-style: italic;
    color: var(--ct-evidence-text);
}

.exec-problem-card {
    background: var(--ct-card-bg);
    border: 1px solid var(--ct-card-border);
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 16px;
    box-shadow: var(--ct-card-shadow);
    color: var(--ct-text-primary);
}

.exec-problem-card.leading-problem {
    border: 2px solid #10B981;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
}

.exec-action-box {
    background: var(--ct-hero-bg);
    border: 1px solid var(--ct-hero-border);
    border-radius: 12px;
    padding: 18px 22px;
    margin-top: 14px;
}
</style>
"""

# Acronyms to keep uppercase
ACRONYMS = {
    "SIP", "SIPS", "AI", "SEBI", "NAV", "AMC", "AMCS", "UPI", "KYC", 
    "ECS", "OTP", "API", "PM", "KPI", "KPIS", "BSE", "CAMS", "KFINTECH", 
    "ID", "UI", "UX", "FAQ", "FAQS", "NACH", "NPCI"
}

# Words to keep lowercase unless at start
LOWERCASE_WORDS = {
    "and", "or", "the", "a", "an", "in", "on", "of", "to", "for", 
    "with", "at", "by", "vs", "vs."
}


def format_display_name(text: str) -> str:
    """Standardize display titles and labels to clean Title Case while preserving acronyms."""
    if not text:
        return ""
    words = str(text).strip().split()
    formatted = []
    for i, w in enumerate(words):
        w_clean = w.strip(".,;:()[]{}'\"")
        upper = w_clean.upper()
        if upper in {"SIP", "SIPS"}:
            formatted.append(w.replace(w_clean, "SIPs" if upper == "SIPS" else "SIP"))
        elif upper in ACRONYMS:
            formatted.append(w.replace(w_clean, upper))
        elif i > 0 and w.lower() in LOWERCASE_WORDS:
            formatted.append(w.lower())
        else:
            if "-" in w:
                sub_parts = [p.capitalize() for p in w.split("-")]
                formatted.append("-".join(sub_parts))
            else:
                formatted.append(w.capitalize())
    return " ".join(formatted)


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
            <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px; padding: 10px 12px; margin-bottom: 12px;">
                <span class="status-dot status-dot-yellow"></span>
                <strong style="color: var(--ct-badge-amber-text, #FBBF24);">Manual Mode</strong>
                <div style="font-size: 0.8rem; color: var(--ct-text-muted, #94A3B8); margin-top: 4px;">GROQ_API_KEY not configured in .env. Analysis runs in manual label mode.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.sidebar.markdown(
            f"""
            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 10px 12px; margin-bottom: 12px;">
                <span class="status-dot status-dot-green"></span>
                <strong style="color: var(--ct-badge-green-text, #34D399);">Groq Connected</strong>
                <div style="font-size: 0.78rem; color: var(--ct-text-muted, #94A3B8); margin-top: 4px;">Model: <code>{model}</code></div>
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
            <div style="font-size: 0.85rem; color: var(--ct-text-secondary, #CBD5E1); line-height: 1.8;">
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
