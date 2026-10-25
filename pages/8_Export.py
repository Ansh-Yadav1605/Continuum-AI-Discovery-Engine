"""
pages/8_Export.py — Research Export Hub & Methodology Disclosure (Milestone 3.4).

Generate downloadable fellowship deliverables, full data exports (CSV/JSON/Markdown),
and automated research methodology documentation with explicit limitations disclosures.
"""

import streamlit as st
from core.database import init_db
from core.ui_helpers import apply_custom_styles, render_sidebar_status
from core.export import (
    export_research_data,
    export_evidence_log,
    export_themes,
    export_problems,
    export_source_register,
    generate_methodology
)

# 1. Page Configuration
st.set_page_config(
    page_title="Export & Methodology | SIP Discovery Engine",
    page_icon="📦",
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
        <div class="hero-title">📦 Deliverable Export Hub & Methodology Disclosure</div>
        <p class="hero-subtitle">
            Export unified research findings, candidate problem scorecards, AI audit logs, and automated methodology documentation for fellowship submission.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# 3. Limitations Disclosure (Always Visible)
st.warning(
    """
    🛡️ **Mandatory Research Disclosure & Scope Boundaries:**
    1. **Absence of Internal Logs:** We do not possess access to Groww's internal transactional ledgers or customer databases.
    2. **Investigative Signal vs. Causation:** Mention frequencies identify friction signals for qualitative investigation, but do not prove 12-month retention causality.
    3. **Compliance Assurance:** This system acts purely as a PM discovery partner. It never offers investment recommendations, stock picks, or manipulative urgency patterns.
    """
)

# 4. Download Deliverables Section
st.markdown("### 📥 Download Fellowship Deliverables")

col_d1, col_d2, col_d3 = st.columns(3)

# Data prep
df_research = export_research_data()
df_evidence = export_evidence_log()
df_themes, md_themes = export_themes()
json_problems, md_problems = export_problems()
df_sources = export_source_register()
methodology_md = generate_methodology()

with col_d1:
    st.markdown(
        """
        <div class="glass-card">
            <h4>📊 Unified Research Dataset</h4>
            <p style="color: #94A3B8; font-size: 0.85rem;">All records with source provenance, ratings, and AI/Human labels.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.download_button(
        "Download Full Research (CSV)",
        data=df_research.to_csv(index=False),
        file_name="sip_discovery_unified_research.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_d2:
    st.markdown(
        """
        <div class="glass-card">
            <h4>⚖️ AI Evaluation Evidence Log</h4>
            <p style="color: #94A3B8; font-size: 0.85rem;">Full audit trail of AI vs. human labels, agreement, and error categories.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.download_button(
        "Download Evidence Log (CSV)",
        data=df_evidence.to_csv(index=False),
        file_name="sip_ai_evidence_log.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_d3:
    st.markdown(
        """
        <div class="glass-card">
            <h4>🎯 Prioritized Problem Cards</h4>
            <p style="color: #94A3B8; font-size: 0.85rem;">Falsifiable problem statements, hypotheses, and 6-factor scores.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        st.download_button(
            "JSON",
            data=json_problems,
            file_name="candidate_problems.json",
            mime="application/json",
            use_container_width=True
        )
    with col_sub2:
        st.download_button(
            "Markdown",
            data=md_problems,
            file_name="candidate_problems.md",
            mime="text/markdown",
            use_container_width=True
        )

col_d4, col_d5, col_d6 = st.columns(3)

with col_d4:
    st.markdown(
        """
        <div class="glass-card">
            <h4>🧬 Theme Taxonomy Summary</h4>
            <p style="color: #94A3B8; font-size: 0.85rem;">Aggregate frequencies, contradictory counts, and respondent metrics.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.download_button(
        "Download Theme Summary (CSV)",
        data=df_themes.to_csv(index=False),
        file_name="sip_theme_summary.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_d5:
    st.markdown(
        """
        <div class="glass-card">
            <h4>📋 Source Register</h4>
            <p style="color: #94A3B8; font-size: 0.85rem;">Traceable catalog of review platforms, surveys, and limitation notes.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.download_button(
        "Download Source Register (CSV)",
        data=df_sources.to_csv(index=False),
        file_name="sip_source_register.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_d6:
    st.markdown(
        """
        <div class="glass-card">
            <h4>📝 Research Methodology Report</h4>
            <p style="color: #94A3B8; font-size: 0.85rem;">Complete fellowship narrative with quantitative metrics and boundaries.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.download_button(
        "Download Methodology (Markdown)",
        data=methodology_md,
        file_name="sip_discovery_methodology.md",
        mime="text/markdown",
        use_container_width=True
    )

st.markdown("---")

# 5. Interactive Methodology Report Preview
st.markdown("### 📄 Methodology Narrative Preview")

with st.expander("Expand Methodology Report Document", expanded=True):
    st.markdown(methodology_md)
