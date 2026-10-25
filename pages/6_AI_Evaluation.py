"""
pages/6_AI_Evaluation.py — AI Evidence Log & Human Benchmark (Milestone 2.3).

Perform structured human evaluation benchmark against AI extraction, track agreement rates,
categorize errors, and export the complete traceable audit log.
"""

import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.database import init_db, PROVISIONAL_TAXONOMY
from core.ui_helpers import apply_custom_styles, render_sidebar_status
from core.evaluation import (
    get_benchmark_candidates,
    create_evaluation_entry,
    calculate_metrics,
    export_evidence_log_csv,
    ERROR_CATEGORIES,
    TARGET_THRESHOLDS
)

# 1. Page Configuration
st.set_page_config(
    page_title="AI Evaluation & Audit Log | SIP Discovery Engine",
    page_icon="⚖️",
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
        <div class="hero-title">⚖️ AI Evidence Log & Evaluation Benchmark</div>
        <p class="hero-subtitle">
            Rigorous human-in-the-loop audit trail comparing AI extraction vs. human ground truth. Monitor precision, recall, and error taxonomy with strict data sufficiency guards.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.warning(
    "⚠️ **Audit Integrity Guarantee:** Do **not** fabricate evaluations or auto-approve records. "
    "Metrics reflect only genuinely reviewed records. When evaluation sample size is below 10, metrics display data sufficiency warnings."
)

tab_metrics, tab_benchmark, tab_audit = st.tabs([
    "📊 Evaluation Dashboard & Metrics",
    "🔬 Benchmark Review Workspace",
    "📜 Full Audit Log & Export"
])

metrics = calculate_metrics()
TAXONOMY_OPTIONS = [name for name, _ in PROVISIONAL_TAXONOMY]
RELEVANCE_OPTIONS = ["directly_relevant", "indirectly_relevant", "not_relevant", "ambiguous"]

# ──────────────────────────────────────────────
# TAB 1: Metrics Dashboard
# ──────────────────────────────────────────────
with tab_metrics:
    total_eval = metrics["total_evaluated"]

    if metrics.get("data_sufficiency_warning"):
        st.info(f"ℹ️ **Sample Size Notice:** {metrics['warning_message']}")

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total Evaluated Records", total_eval)
    with col_m2:
        rel_rate = metrics["relevance_agreement_rate"]
        st.metric("Relevance Agreement", f"{rel_rate}%", delta=f"{rel_rate - TARGET_THRESHOLDS['relevance_agreement']:.1f}% vs Target (75%)")
    with col_m3:
        macro_f1 = metrics["macro_f1"]
        st.metric("Theme Macro F1", f"{macro_f1}", delta=f"{macro_f1 - TARGET_THRESHOLDS['theme_macro_f1']:.2f} vs Target (0.60)")
    with col_m4:
        hal_rate = metrics["hallucination_rate"]
        st.metric("Hallucination Rate", f"{hal_rate}%", delta=f"{TARGET_THRESHOLDS['max_hallucination_rate'] - hal_rate:.1f}% headroom (<5%)")

    st.markdown("<br/>", unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("#### 🎯 Error Category Distribution")
        err_dist = metrics["error_distribution"]
        if any(err_dist.values()):
            df_err = pd.DataFrame([{"Category": k.replace("_", " ").title(), "Count": v} for k, v in err_dist.items() if v > 0])
            fig_pie = px.pie(
                df_err,
                names="Category",
                values="Count",
                color_discrete_sequence=["#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#6B7280"]
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=320, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.caption("No error categories logged yet.")

    with col_chart2:
        st.markdown("#### 📐 Target Benchmark Comparison")
        st.markdown(
            f"""
            - **Relevance Agreement:** Current: **{metrics['relevance_agreement_rate']}%** | Minimum Target: **75.0%**
            - **Theme Extraction Macro F1:** Current: **{metrics['macro_f1']}** | Target: **≥ 0.60**
            - **Hallucination / Fabrication Rate:** Current: **{metrics['hallucination_rate']}%** | Maximum Allowed: **< 5.0%**
            - **Human Corrections Applied:** **{metrics['corrections_count']}** record(s)
            """
        )

    st.markdown("---")
    st.markdown("#### 📋 Per-Theme Precision, Recall & F1")
    theme_mets = metrics["per_theme_metrics"]
    if theme_mets:
        theme_rows = []
        for t, m in theme_mets.items():
            if m["insufficient_data"]:
                theme_rows.append({
                    "Theme": t,
                    "Evaluated Instances": m["instances"],
                    "Precision": "Insufficient Data",
                    "Recall": "Insufficient Data",
                    "F1 Score": "Insufficient Data",
                    "Data Status": "⚠️ Needs ≥ 5 instances"
                })
            else:
                theme_rows.append({
                    "Theme": t,
                    "Evaluated Instances": m["instances"],
                    "Precision": f"{m['precision']:.2f}",
                    "Recall": f"{m['recall']:.2f}",
                    "F1 Score": f"{m['f1']:.2f}",
                    "Data Status": "✅ Statistically Valid"
                })
        st.dataframe(pd.DataFrame(theme_rows), use_container_width=True, hide_index=True)
    else:
        st.caption("No theme evaluation instances recorded yet.")

# ──────────────────────────────────────────────
# TAB 2: Benchmark Review Workspace
# ──────────────────────────────────────────────
with tab_benchmark:
    st.markdown("### 🔬 Evaluate Curated Benchmark Records")
    candidates = get_benchmark_candidates(limit=20)

    if not candidates:
        st.info("No analysed records available for evaluation. Run batch analysis in Research Explorer first.")
    else:
        record_options = {
            f"Record {r['record_id'][:8]} | Source: {r['source']} | AI: {r['ai_relevance']}": r["record_id"]
            for r in candidates
        }
        selected_display = st.selectbox("Select Record to Evaluate", list(record_options.keys()))
        selected_rid = record_options[selected_display]
        rec = next(r for r in candidates if r["record_id"] == selected_rid)

        bcol1, bcol2 = st.columns([1, 1])

        with bcol1:
            st.markdown("#### 📄 Original Text & AI Extraction")
            st.markdown(f"<div class='glass-card'><strong>Source:</strong> {rec['source']} | <strong>Type:</strong> {rec['record_type']}<br/><br/>{rec['text']}</div>", unsafe_allow_html=True)
            
            st.markdown("**AI Proposed Labels:**")
            st.markdown(f"- **Relevance:** `{rec['ai_relevance']}`")
            st.markdown(f"- **Themes:** `{rec['ai_themes']}`")
            st.markdown(f"- **Evidence Excerpt:** *“{rec['ai_evidence_excerpt']}”*")
            st.markdown(f"- **Explanation:** {rec['ai_relevance_explanation']}")
            if rec.get("ai_missing_context"):
                st.markdown(f"- **Missing Context:** *{rec['ai_missing_context']}*")

        with bcol2:
            st.markdown("#### 👤 Human Benchmark Ground Truth")
            with st.form(f"eval_form_{selected_rid}"):
                # Default selection
                default_rel = rec.get("human_relevance") or rec.get("ai_relevance") or "directly_relevant"
                if default_rel not in RELEVANCE_OPTIONS:
                    default_rel = "directly_relevant"

                h_rel = st.selectbox("Human Relevance Label", RELEVANCE_OPTIONS, index=RELEVANCE_OPTIONS.index(default_rel))

                # Default themes
                curr_themes = []
                try:
                    raw_th = rec.get("human_themes") or rec.get("ai_themes") or "[]"
                    curr_themes = [t for t in json.loads(raw_th) if t in TAXONOMY_OPTIONS]
                except Exception:
                    pass

                h_themes = st.multiselect("Human Taxonomy Themes", TAXONOMY_OPTIONS, default=curr_themes)
                h_evid = st.text_area("Human Evidence Excerpt (Verbatim quote)", value=rec.get("human_evidence") or rec.get("ai_evidence_excerpt") or "")
                
                err_cat = st.selectbox(
                    "Error Categorization (if AI had discrepancy)",
                    ERROR_CATEGORIES,
                    index=0,
                    help="Select 'correct' if AI was accurate. If AI over-indexed, missed a theme, or hallucinated, categorize it here."
                )
                
                notes = st.text_input("Reviewer Notes / Justification", value="")
                submit_eval = st.form_submit_button("Submit Evaluation Entry", type="primary")

                if submit_eval:
                    create_evaluation_entry(
                        record_id=selected_rid,
                        human_relevance=h_rel,
                        human_themes=h_themes,
                        human_evidence=h_evid,
                        error_category=err_cat,
                        reviewer_notes=notes
                    )
                    st.success("Evaluation submitted and saved to immutable Evidence Log!")
                    st.rerun()

# ──────────────────────────────────────────────
# TAB 3: Full Audit Log & Export
# ──────────────────────────────────────────────
with tab_audit:
    st.markdown("### 📜 Traceable Evidence Log")

    csv_data = export_evidence_log_csv()
    st.download_button(
        label="📥 Download Evidence Log CSV",
        data=csv_data,
        file_name="sip_ai_evidence_log.csv",
        mime="text/csv",
        use_container_width=False
    )

    logs = metrics.get("logs", [])
    if logs:
        st.markdown(f"**Total Logged Evaluations:** {len(logs)}")
        log_rows = []
        for l in logs:
            log_rows.append({
                "Date": l["reviewed_at"][:19].replace("T", " ") if l["reviewed_at"] else "-",
                "Record ID": l["record_id"][:8],
                "AI Rel": l["ai_relevance"],
                "Human Rel": l["human_relevance"],
                "Agreement": l["agreement"],
                "Error Category": l["error_category"],
                "Notes": l["reviewer_notes"] or "-"
            })
        st.dataframe(pd.DataFrame(log_rows), use_container_width=True, hide_index=True)
    else:
        st.caption("No evaluation records logged in the database yet.")
