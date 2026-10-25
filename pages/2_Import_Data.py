"""
pages/2_Import_Data.py — CSV Ingestion with column mapping, deduplication, and Google Forms support.

Supports:
- Public Reviews CSV ingestion (App Store, Trustpilot, Reddit)
- Google Forms Survey CSV ingestion with question mapping and checkbox preservation
- SHA-256 exact deduplication & SequenceMatcher near-deduplication
- Methodological source register logging
"""

import streamlit as st
import pandas as pd
import io

from core.database import init_db, get_connection
from core.ui_helpers import apply_custom_styles, render_sidebar_status
from core.ingestion import read_csv_safe, import_csv
from core.survey_ingestion import import_survey_csv

st.set_page_config(page_title="Import Data | SIP Discovery Engine", page_icon="📥", layout="wide")
init_db()
apply_custom_styles()
render_sidebar_status()

st.markdown(
    """
    <div class="hero-header">
        <div class="hero-title">📥 Research Data Ingestion</div>
        <p class="hero-subtitle">Import unstructured feedback from public app reviews or structured survey responses with automated deduplication and schema validation.</p>
    </div>
    """,
    unsafe_allow_html=True
)

import_mode = st.radio(
    "Select Ingestion Channel:",
    ["Public Reviews CSV (Play Store, Trustpilot, Discussions)", "Google Forms Survey CSV (Multi-Question Survey)"],
    horizontal=True
)

# ──────────────────────────────────────────────
# Channel 1: Public Reviews CSV
# ──────────────────────────────────────────────
if import_mode.startswith("Public Reviews"):
    st.markdown("### 📱 Public Reviews Ingestion")
    
    uploaded_file = st.file_uploader("Upload CSV File:", type=["csv"], key="public_csv_uploader")
    
    if uploaded_file:
        try:
            df_preview = read_csv_safe(uploaded_file)
            st.success(f"CSV file loaded successfully: **{len(df_preview)} rows**, **{len(df_preview.columns)} columns** detected.")
            
            with st.expander("👀 View Raw CSV Headers and First 3 Rows", expanded=False):
                st.dataframe(df_preview.head(3), use_container_width=True)

            st.markdown("#### 🗺️ Column Mapping")
            st.caption("Map the columns in your CSV to the unified research schema. Columns with matched names are auto-selected.")

            col_opts = ["(None / Skip)"] + list(df_preview.columns)

            # Auto-detection helper
            def find_best_col(keywords, cols):
                for kw in keywords:
                    for c in cols:
                        if kw in c.lower():
                            return c
                return "(None / Skip)"

            cmap1, cmap2 = st.columns(2)
            with cmap1:
                default_text = find_best_col(["review", "text", "body", "content", "comment", "feedback"], df_preview.columns)
                text_col = st.selectbox(
                    "Feedback Text (Required) *",
                    col_opts,
                    index=col_opts.index(default_text) if default_text in col_opts else 0,
                    help="The verbatim review text content"
                )

                default_rating = find_best_col(["rating", "score", "stars"], df_preview.columns)
                rating_col = st.selectbox(
                    "Numeric Rating (Optional)",
                    col_opts,
                    index=col_opts.index(default_rating) if default_rating in col_opts else 0,
                    help="Star rating or review score (e.g. 1-5)"
                )

            with cmap2:
                default_date = find_best_col(["date", "time", "created", "published"], df_preview.columns)
                date_col = st.selectbox(
                    "Publication Date (Optional)",
                    col_opts,
                    index=col_opts.index(default_date) if default_date in col_opts else 0,
                    help="Review submission or publication date"
                )

                default_url = find_best_col(["url", "link", "permalink"], df_preview.columns)
                url_col = st.selectbox(
                    "Source URL (Optional)",
                    col_opts,
                    index=col_opts.index(default_url) if default_url in col_opts else 0,
                    help="Original post or review URL"
                )

            st.markdown("#### 📝 Metadata & Source Register")
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                source_name = st.text_input("Source Platform Name:", value="Google Play Store", help="e.g. Google Play Store, iOS App Store, Trustpilot, Reddit")
                source_url_default = st.text_input("Default Source URL (if not in CSV):", value="https://play.google.com/store/apps/details?id=com.nextbillion.groww")
            with mcol2:
                known_limitations = st.text_area(
                    "Known Limitations & Biases:",
                    value="Public app store reviews exhibit negative response bias; users experiencing unaddressed friction are more likely to complain than satisfied retainers.",
                    height=70
                )
                permission_notes = st.text_input("Permissions / Legal Notes:", value="Publicly accessible app store user reviews.")

            # Live preview of mapped data
            if text_col != "(None / Skip)":
                st.markdown("#### 🔎 Preview of Mapped Records (Top 3)")
                preview_data = []
                for _, r in df_preview.head(3).iterrows():
                    preview_data.append({
                        "Source": source_name,
                        "Text": str(r.get(text_col, ""))[:140] + ("..." if len(str(r.get(text_col, ""))) > 140 else ""),
                        "Rating": r.get(rating_col) if rating_col != "(None / Skip)" else None,
                        "Date": r.get(date_col) if date_col != "(None / Skip)" else None
                    })
                st.dataframe(pd.DataFrame(preview_data), use_container_width=True)

                if st.button("🚀 Start Ingestion & Validation", type="primary", use_container_width=True):
                    col_mapping = {"text": text_col}
                    if rating_col != "(None / Skip)":
                        col_mapping["rating"] = rating_col
                    if date_col != "(None / Skip)":
                        col_mapping["publication_date"] = date_col
                    if url_col != "(None / Skip)":
                        col_mapping["source_url"] = url_col

                    prog_bar = st.progress(0)
                    prog_status = st.empty()

                    def update_prog(cur, tot):
                        prog_bar.progress(cur / tot)
                        prog_status.caption(f"Validating and deduplicating record {cur} of {tot}...")

                    # Rewind file pointer
                    uploaded_file.seek(0)
                    summary = import_csv(
                        file_or_path=uploaded_file,
                        column_mapping=col_mapping,
                        source_name=source_name,
                        source_url=source_url_default,
                        collection_method="csv_import",
                        record_type="public_review",
                        known_limitations=known_limitations,
                        permission_notes=permission_notes,
                        progress_callback=update_prog
                    )
                    prog_bar.progress(1.0)
                    prog_status.empty()

                    st.success("🎉 Ingestion complete!")
                    
                    # Summary metrics
                    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                    with sc1:
                        st.metric("Total Rows", summary["total"])
                    with sc2:
                        st.metric("Imported", summary["imported"], delta=f"{summary['imported']} added")
                    with sc3:
                        st.metric("Exact Dups Skipped", summary["exact_duplicates"], delta="SHA-256 match", delta_color="inverse")
                    with sc4:
                        st.metric("Near Dups Flagged", summary["near_duplicates"], delta="Flagged >85%", delta_color="off")
                    with sc5:
                        st.metric("Rejected (Blank)", summary["rejected"], delta_color="inverse")

                    if summary["rejection_reasons"]:
                        with st.expander(f"⚠️ View {len(summary['rejection_reasons'])} Rejected Rows"):
                            st.write(summary["rejection_reasons"])
            else:
                st.warning("Please map the 'Feedback Text' column to proceed.")

        except Exception as e:
            st.error(f"Error parsing CSV: {str(e)}")

# ──────────────────────────────────────────────
# Channel 2: Google Forms Survey CSV
# ──────────────────────────────────────────────
else:
    st.markdown("### 📋 Google Forms Survey Ingestion")
    st.info("💡 Google Forms surveys typically contain multiple-choice options, multi-select checkboxes, and open-ended text fields. Comma-separated checkbox values are preserved verbatim.")

    uploaded_survey = st.file_uploader("Upload Google Forms CSV Export:", type=["csv"], key="survey_csv_uploader")
    
    if uploaded_survey:
        try:
            df_survey = read_csv_safe(uploaded_survey)
            st.success(f"Survey CSV loaded: **{len(df_survey)} respondent rows**, **{len(df_survey.columns)} question columns**.")
            
            with st.expander("👀 View Survey Questions (Columns)", expanded=False):
                st.write(list(df_survey.columns))

            st.markdown("#### 🗺️ Survey Question Mapping")
            
            # Primary open text
            col_opts = list(df_survey.columns)
            open_text_default = next((c for c in col_opts if any(k in c.lower() for k in ["why", "reason", "feedback", "describe", "experience", "explain"])), col_opts[-1])
            
            open_col = st.selectbox(
                "Primary Open-Text Feedback Question (Required) *",
                col_opts,
                index=col_opts.index(open_text_default) if open_text_default in col_opts else 0,
                help="The main qualitative answer describing user experience or continuation hurdles"
            )

            # Respondent ID
            id_opts = ["(Auto-generate sequential IDs RESP-0001...)"] + col_opts
            resp_default = next((c for c in col_opts if any(k in c.lower() for k in ["timestamp", "id", "email", "respondent"])), "(Auto-generate sequential IDs RESP-0001...)")
            resp_col = st.selectbox(
                "Respondent ID Question / Timestamp",
                id_opts,
                index=id_opts.index(resp_default) if resp_default in id_opts else 0,
                help="Column identifying individual respondents"
            )

            # Context questions
            remaining_cols = [c for c in col_opts if c != open_col and c != resp_col]
            context_cols_selected = st.multiselect(
                "Additional Structured Context Questions (Included in header):",
                remaining_cols,
                default=remaining_cols[:2] if len(remaining_cols) >= 2 else remaining_cols,
                help="Multi-select checkboxes or multiple-choice questions whose answers will be included as structured context"
            )

            survey_name = st.text_input("Survey Study Name:", value="SIP Investor Drop-off Survey Wave 1")
            survey_limitations = st.text_area(
                "Survey Methodology Limitations:",
                value="Self-selected survey cohort; responses reflect self-reported behavior and may suffer from recall bias regarding specific drop-off triggers.",
                height=65
            )

            # Live preview of composed record
            st.markdown("#### 🔎 Preview of Unified Survey Record (Respondent 1)")
            sample_parts = []
            for c in context_cols_selected:
                val = df_survey.iloc[0].get(c)
                if pd.notna(val):
                    sample_parts.append(f"[{c[:25]}: {str(val).strip()}]")
            sample_open = df_survey.iloc[0].get(open_col)
            preview_text = f"{' '.join(sample_parts)}\n{sample_open}"
            st.code(preview_text, language="markdown")

            if st.button("🚀 Import Survey Responses", type="primary", use_container_width=True):
                prog_bar = st.progress(0)
                prog_status = st.empty()

                def update_prog_survey(cur, tot):
                    prog_bar.progress(cur / tot)
                    prog_status.caption(f"Processing respondent {cur} of {tot}...")

                uploaded_survey.seek(0)
                mapped_context = [(c, c[:30]) for c in context_cols_selected]
                actual_resp_col = None if resp_col.startswith("(Auto-generate") else resp_col

                summary = import_survey_csv(
                    file_or_path=uploaded_survey,
                    open_text_col=open_col,
                    respondent_id_col=actual_resp_col,
                    context_cols=mapped_context,
                    source_name=survey_name,
                    known_limitations=survey_limitations,
                    progress_callback=update_prog_survey
                )
                prog_bar.progress(1.0)
                prog_status.empty()

                st.success("🎉 Survey responses imported!")
                
                sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                with sc1:
                    st.metric("Total Responses", summary["total"])
                with sc2:
                    st.metric("Imported", summary["imported"], delta=f"{summary['imported']} responses")
                with sc3:
                    st.metric("Exact Duplicates", summary["exact_duplicates"], delta_color="inverse")
                with sc4:
                    st.metric("Near Duplicates", summary["near_duplicates"], delta="Flagged", delta_color="off")
                with sc5:
                    st.metric("Blank Responses", summary["rejected"], delta_color="inverse")

        except Exception as e:
            st.error(f"Error importing survey CSV: {str(e)}")
