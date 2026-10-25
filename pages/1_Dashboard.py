"""
pages/1_Dashboard.py — Executive overview dashboard for PM research.

Features:
- Dynamic empty state with guided setup checklist and sample data loader
- High-level KPIs: Total Records, Analysed %, Awaiting Review, Reviews vs Survey breakdown
- Plotly interactive charts: Relevance breakdown & Top themes distribution
- Source coverage table from source_register
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from core.database import init_db, get_connection, now_iso
from core.ui_helpers import apply_custom_styles, render_sidebar_status
from core.themes import get_theme_distribution, get_relevance_distribution, get_source_coverage
from core.groq_client import get_api_key

st.set_page_config(page_title="Dashboard | SIP Discovery Engine", page_icon="📊", layout="wide")
init_db()
apply_custom_styles()
render_sidebar_status()

st.markdown(
    """
    <div class="hero-header">
        <div class="hero-title">📊 Executive Research Dashboard</div>
        <p class="hero-subtitle">High-level synthesis of mutual fund SIP retention evidence, taxonomy coverage, and review status.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Fetch current counts
with get_connection() as conn:
    total_records = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    analysed_records = conn.execute("SELECT COUNT(*) FROM analysis_results").fetchone()[0]
    pending_review = conn.execute("SELECT COUNT(*) FROM analysis_results WHERE review_status = 'pending'").fetchone()[0]
    reviewed_count = conn.execute("SELECT COUNT(*) FROM analysis_results WHERE review_status = 'reviewed'").fetchone()[0]
    public_reviews = conn.execute("SELECT COUNT(*) FROM records WHERE record_type = 'public_review'").fetchone()[0]
    survey_responses = conn.execute("SELECT COUNT(*) FROM records WHERE record_type = 'survey_response'").fetchone()[0]

# ──────────────────────────────────────────────
# Empty State View
# ──────────────────────────────────────────────
if total_records == 0:
    st.info("👋 Welcome! The research database is currently empty. Follow the quick setup steps below to start discovering insights.")
    
    scol1, scol2 = st.columns([2, 1])
    with scol1:
        st.markdown(
            """
            <div class="glass-card">
                <h3>🚀 Quick Setup Checklist</h3>
                <ol style="line-height: 2.2; color: #E2E8F0; font-size: 0.95rem;">
                    <li><strong>Step 1: Import Data</strong> — Upload public app store reviews or Google Forms survey CSVs via the Data Importer.</li>
                    <li><strong>Step 2: Check Groq API</strong> — Verify connection in the sidebar diagnostic (or proceed with Manual Mode).</li>
                    <li><strong>Step 3: Run Batch Analysis</strong> — Let AI extract themes, evidence excerpts, and user needs in Research Explorer.</li>
                    <li><strong>Step 4: Human Verification</strong> — Review, correct, and audit classifications to build the Evidence Log.</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True
        )
    with scol2:
        st.markdown(
            """
            <div class="glass-card">
                <h4>🧪 Instant Demo Mode</h4>
                <p style="font-size: 0.88rem; color: #94A3B8;">
                    Want to test the full pipeline immediately? Load a sample dataset of realistic first-time SIP investor feedback (Play Store reviews + Survey responses).
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("📥 Load Sample SIP Feedback Dataset", use_container_width=True, type="primary"):
            from tests.sample_data import load_sample_dataset
            with st.spinner("Loading realistic sample dataset..."):
                count = load_sample_dataset()
                st.success(f"Successfully loaded {count} realistic SIP research records!")
                st.rerun()

    st.stop()

# ──────────────────────────────────────────────
# Populated State View
# ──────────────────────────────────────────────

# Top Metric Pills
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val">{total_records}</div>
            <div class="metric-pill-label">Total Records</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi2:
    pct = round(analysed_records / total_records * 100, 1) if total_records > 0 else 0
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val">{analysed_records} <span style="font-size: 0.9rem; color: #60A5FA;">({pct}%)</span></div>
            <div class="metric-pill-label">Analysed</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi3:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val" style="color: #FBBF24;">{pending_review}</div>
            <div class="metric-pill-label">Awaiting Review</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi4:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val" style="color: #A78BFA;">{public_reviews}</div>
            <div class="metric-pill-label">Public Reviews</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi5:
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-pill-val" style="color: #F472B6;">{survey_responses}</div>
            <div class="metric-pill-label">Survey Responses</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br/>", unsafe_allow_html=True)

# Awaiting Review Banner if there are pending reviews
if pending_review > 0:
    st.markdown(
        f"""
        <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 10px; padding: 12px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong style="color: #FBBF24;">⚡ Action Required:</strong> 
                <span style="color: #E2E8F0; margin-left: 6px;">You have <strong>{pending_review}</strong> records analysed by AI that require human review and verification.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Visualizations Row
chart_col1, chart_col2 = st.columns([1, 1])

# 1. Relevance Distribution Donut
with chart_col1:
    st.markdown("#### 🎯 Relevance Distribution")
    rel_data = get_relevance_distribution()
    unanalysed_count = max(0, total_records - analysed_records)
    
    chart_labels = ["Directly Relevant", "Indirectly Relevant", "Not Relevant", "Ambiguous", "Unanalysed"]
    chart_values = [
        rel_data.get("directly_relevant", 0),
        rel_data.get("indirectly_relevant", 0),
        rel_data.get("not_relevant", 0),
        rel_data.get("ambiguous", 0),
        unanalysed_count
    ]
    color_map = ["#10B981", "#3B82F6", "#6B7280", "#F59E0B", "#374151"]

    fig_pie = go.Figure(
        data=[
            go.Pie(
                labels=chart_labels,
                values=chart_values,
                hole=0.55,
                marker=dict(colors=color_map),
                textinfo="label+percent",
                insidetextorientation="radial"
            )
        ]
    )
    fig_pie.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1", family="Inter")
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 2. Top Themes Bar Chart
with chart_col2:
    st.markdown("#### 🏷️ Top Identified Themes")
    themes_list = get_theme_distribution()
    if themes_list:
        top_themes = themes_list[:7]
        df_themes = pd.DataFrame(top_themes)
        fig_bar = px.bar(
            df_themes,
            x="count",
            y="theme",
            orientation="h",
            labels={"count": "Records", "theme": "Theme"},
            color="count",
            color_continuous_scale="Purples"
        )
        fig_bar.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            yaxis=dict(autorange="reversed", color="#CBD5E1"),
            xaxis=dict(color="#CBD5E1"),
            font=dict(color="#CBD5E1", family="Inter")
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No themes extracted yet. Run batch analysis in Research Explorer to populate themes.")

st.markdown("---")

# Source Coverage Section
st.markdown("### 📚 Source Register & Data Hygiene")
sources = get_source_coverage()
if sources:
    df_src = pd.DataFrame(sources)
    df_src = df_src.rename(columns={
        "source_name": "Source",
        "collection_method": "Method",
        "record_count": "Count",
        "date_collected": "Collected At",
        "known_limitations": "Known Limitations & Biases"
    })
    st.dataframe(
        df_src[["Source", "Method", "Count", "Collected At", "Known Limitations & Biases"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.caption("No registered sources yet.")
