"""
pages/3_Research_Explorer.py — Record browsing, search, filtering, Groq batch analysis, and manual review.

Features:
- Free-text search & multidimensional filtering (Source, Record Type, Relevance, Theme, Review Status)
- Controlled Groq AI batch analysis (1, 5, 10, 20 records) with progress reporting
- Manual fallback mode with primary human labeling when API is disconnected
- Verbatim evidence quote highlights, missing context warnings, and journey stage tags
- Human review audit logging into evidence_log
"""

import streamlit as st
import json
import math

from core.database import init_db, get_connection
from core.ui_helpers import apply_custom_styles, render_sidebar_status
from core.analysis import run_analysis, save_manual_review, get_unanalysed_records
from core.groq_client import get_api_key, test_connection
from core.prompts import TAXONOMY_THEMES

st.set_page_config(page_title="Research Explorer | SIP Discovery Engine", page_icon="🔬", layout="wide")
init_db()
apply_custom_styles()
render_sidebar_status()

st.markdown(
    """
    <div class="hero-header">
        <div class="hero-title">🔬 Research Explorer & Evidence Lab</div>
        <p class="hero-subtitle">Inspect qualitative records, execute controlled Groq AI batch analysis, and verify evidence with human review audit logging.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Check Groq API connectivity
api_key = get_api_key()
is_api_available = bool(api_key and api_key != "your_key_here")

# ──────────────────────────────────────────────
# Top Batch Action Bar
# ──────────────────────────────────────────────
unanalysed_records = get_unanalysed_records(limit=100)
unanalysed_count = len(unanalysed_records)

bar_col1, bar_col2, bar_col3 = st.columns([2, 1, 1])

with bar_col1:
    if not is_api_available:
        st.warning("⚠️ **Manual Mode Active:** Groq API is not configured in `.env`. Human labeling fields are primary inputs.")
    elif unanalysed_count > 0:
        st.info(f"⚡ **{unanalysed_count} records awaiting AI analysis.** Run a controlled batch below.")
    else:
        st.success("✅ **All imported records have been analysed!** Review and verify the classifications below.")

with bar_col2:
    batch_size = st.selectbox(
        "Batch Size",
        [1, 5, 10, 20],
        index=1,
        disabled=not is_api_available,
        help="Number of records to analyse in a single batch (default: 5)"
    )

with bar_col3:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🤖 Analyse Next Batch", type="primary", disabled=not is_api_available or unanalysed_count == 0, use_container_width=True):
        prog_bar = st.progress(0)
        prog_status = st.empty()

        def batch_prog(cur, tot, rec_id):
            prog_bar.progress(cur / tot)
            prog_status.caption(f"Analysing record {cur} of {tot} via Groq...")

        with st.spinner("Processing batch with Groq..."):
            summary = run_analysis(batch_size=batch_size, progress_callback=batch_prog)
            prog_bar.progress(1.0)
            prog_status.empty()

        if summary["analysed"] > 0:
            st.success(f"Analysed {summary['analysed']} records successfully!")
        if summary["errors"] > 0:
            st.error(f"Encountered {summary['errors']} errors during batch.")
        st.rerun()

st.markdown("---")

# ──────────────────────────────────────────────
# Sidebar Filters
# ──────────────────────────────────────────────
st.sidebar.markdown("### 🔍 Filters & Search")

# Free text search
search_query = st.sidebar.text_input("Text Search:", placeholder="e.g. cancelled, mandate, negative", key="exp_search")

# Get existing sources from DB
with get_connection() as conn:
    src_rows = conn.execute("SELECT DISTINCT source FROM records WHERE source IS NOT NULL").fetchall()
    all_sources = ["All"] + [r["source"] for r in src_rows]

filter_source = st.sidebar.selectbox("Source Platform:", all_sources)
filter_type = st.sidebar.selectbox("Record Type:", ["All", "public_review", "survey_response"])
filter_relevance = st.sidebar.selectbox(
    "Relevance:",
    ["All", "directly_relevant", "indirectly_relevant", "not_relevant", "ambiguous", "Unanalysed"]
)
filter_theme = st.sidebar.selectbox("Taxonomy Theme:", ["All"] + TAXONOMY_THEMES)
filter_review = st.sidebar.selectbox("Review Status:", ["All", "pending", "reviewed", "corrected", "rejected"])

# ──────────────────────────────────────────────
# Database Query Construction
# ──────────────────────────────────────────────
where_clauses = []
params = []

if search_query.strip():
    where_clauses.append("r.text LIKE ?")
    params.append(f"%{search_query.strip()}%")

if filter_source != "All":
    where_clauses.append("r.source = ?")
    params.append(filter_source)

if filter_type != "All":
    where_clauses.append("r.record_type = ?")
    params.append(filter_type)

if filter_relevance == "Unanalysed":
    where_clauses.append("a.analysis_id IS NULL")
elif filter_relevance != "All":
    where_clauses.append("COALESCE(a.human_relevance, a.ai_relevance) = ?")
    params.append(filter_relevance)

if filter_theme != "All":
    where_clauses.append("(a.ai_themes LIKE ? OR a.human_themes LIKE ?)")
    params.append(f"%{filter_theme}%")
    params.append(f"%{filter_theme}%")

if filter_review != "All":
    where_clauses.append("a.review_status = ?")
    params.append(filter_review)

where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

# Count total matching records
with get_connection() as conn:
    count_sql = f"""
        SELECT COUNT(*) FROM records r
        LEFT JOIN analysis_results a ON r.record_id = a.record_id
        {where_sql}
    """
    total_matching = conn.execute(count_sql, params).fetchone()[0]

# Pagination
PAGE_SIZE = 8
total_pages = max(1, math.ceil(total_matching / PAGE_SIZE))

pcol1, pcol2 = st.columns([3, 1])
with pcol1:
    st.markdown(f"Showing **{total_matching}** records matching active criteria")
with pcol2:
    current_page = st.number_input(f"Page (of {total_pages})", min_value=1, max_value=total_pages, value=1, step=1)

offset = (current_page - 1) * PAGE_SIZE

# Fetch paginated rows
with get_connection() as conn:
    fetch_sql = f"""
        SELECT r.*, 
               a.analysis_id, a.ai_relevance, a.ai_relevance_explanation,
               a.ai_evidence_excerpt, a.ai_themes, a.ai_behaviour, a.ai_user_need,
               a.ai_workaround, a.ai_journey_stage, a.ai_continuation_mention,
               a.ai_missing_context, a.ai_explanation,
               a.human_relevance, a.human_themes, a.human_evidence,
               a.review_status AS analysis_review_status, a.reviewer_notes,
               a.model_used
        FROM records r
        LEFT JOIN analysis_results a ON r.record_id = a.record_id
        {where_sql}
        ORDER BY r.created_at DESC
        LIMIT ? OFFSET ?
    """
    query_params = list(params) + [PAGE_SIZE, offset]
    records = conn.execute(fetch_sql, query_params).fetchall()

# ──────────────────────────────────────────────
# Render Record Cards
# ──────────────────────────────────────────────
if not records:
    st.info("No records found matching your filters. Try adjusting your search query or reset filters.")
else:
    for rec in records:
        rec_id = rec["record_id"]
        source = rec["source"] or "Unknown Source"
        rec_type = rec["record_type"] or "public_review"
        text = rec["text"] or ""
        rating = rec["rating"]
        pub_date = rec["publication_date"]
        resp_id = rec["respondent_id"]
        dup_status = rec["duplicate_status"]

        # Analysis data
        is_analysed = rec["analysis_id"] is not None
        ai_rel = rec["ai_relevance"]
        ai_rel_exp = rec["ai_relevance_explanation"]
        ai_excerpt = rec["ai_evidence_excerpt"]
        ai_themes_raw = rec["ai_themes"]
        ai_journey = rec["ai_journey_stage"]
        ai_cont = rec["ai_continuation_mention"]
        ai_need = rec["ai_user_need"]
        ai_missing = rec["ai_missing_context"]
        model_used = rec["model_used"]

        # Human review data
        human_rel = rec["human_relevance"]
        human_themes_raw = rec["human_themes"]
        human_ev = rec["human_evidence"]
        rev_status = rec["analysis_review_status"] or "unreviewed"
        rev_notes = rec["reviewer_notes"] or ""

        # Badges HTML
        badges_html = []
        if rec_type == "survey_response":
            badges_html.append(f'<span class="badge badge-survey">📋 Survey ({resp_id or "Anonymous"})</span>')
        else:
            badges_html.append(f'<span class="badge badge-source">📱 {source}</span>')

        if rating:
            badges_html.append(f'<span class="badge" style="background: rgba(255,255,255,0.08); color: #F1F5F9;">⭐ {rating}/5</span>')

        if dup_status == "near_duplicate_flagged":
            badges_html.append('<span class="badge badge-flagged">⚠️ Near Duplicate</span>')

        # Relevance badge
        effective_rel = human_rel or ai_rel
        if effective_rel == "directly_relevant":
            badges_html.append('<span class="badge badge-relevant">Directly Relevant</span>')
        elif effective_rel == "indirectly_relevant":
            badges_html.append('<span class="badge badge-indirect">Indirectly Relevant</span>')
        elif effective_rel == "not_relevant":
            badges_html.append('<span class="badge badge-not-relevant">Not Relevant</span>')
        elif effective_rel == "ambiguous":
            badges_html.append('<span class="badge badge-ambiguous">Ambiguous</span>')
        else:
            badges_html.append('<span class="badge" style="background: rgba(100,116,139,0.2); color: #94A3B8;">Unanalysed</span>')

        if rev_status in ("reviewed", "corrected"):
            badges_html.append(f'<span class="badge badge-relevant">✓ {rev_status.capitalize()}</span>')
        elif rev_status == "rejected":
            badges_html.append('<span class="badge badge-flagged">✗ Rejected</span>')

        with st.container():
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div>{' '.join(badges_html)}</div>
                        <div style="font-size: 0.75rem; color: #64748B;">ID: <code>{rec_id[:8]}...</code></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Text display with truncation guardrail
            if len(text) > 400:
                short_text = text[:400]
                st.markdown(f"**Verbatim Feedback:**\n> {short_text}...")
                with st.expander("📖 Show Full Text"):
                    st.write(text)
            else:
                st.markdown(f"**Verbatim Feedback:**\n> {text}")

            # AI Insights Section
            if is_analysed:
                st.markdown("##### 🤖 Groq AI Classification")
                if ai_excerpt:
                    st.markdown(f'<div class="evidence-box"><strong>Evidence Excerpt:</strong> "{ai_excerpt}"</div>', unsafe_allow_html=True)

                c_info1, c_info2 = st.columns([1, 1])
                with c_info1:
                    if ai_rel_exp:
                        st.caption(f"**Relevance Rationale:** {ai_rel_exp}")
                    
                    themes_parsed = []
                    if ai_themes_raw:
                        try:
                            themes_parsed = json.loads(ai_themes_raw)
                        except Exception:
                            themes_parsed = []
                    if themes_parsed:
                        st.markdown(f"**Identified Themes:** `{'`, `'.join(themes_parsed)}`")

                with c_info2:
                    if ai_journey:
                        st.caption(f"**Journey Stage:** `{ai_journey}` | **Continuation:** `{ai_cont or 'none'}`")
                    if ai_need:
                        st.caption(f"**Latent Need:** {ai_need}")

                if ai_missing:
                    st.markdown(f'<div class="missing-box"><strong>⚠️ Missing Context / Limitations:</strong> {ai_missing}</div>', unsafe_allow_html=True)
            else:
                st.caption("ℹ️ *This record has not been analysed yet.*")

            # ──────────────────────────────────────────
            # Human Review & Verification Drawer
            # ──────────────────────────────────────────
            with st.expander(f"✍️ Human Review & Audit Controls (Status: {rev_status.upper()})"):
                rf_col1, rf_col2 = st.columns(2)
                
                with rf_col1:
                    default_h_rel = human_rel or ai_rel or "directly_relevant"
                    valid_rels = ["directly_relevant", "indirectly_relevant", "not_relevant", "ambiguous"]
                    h_rel_choice = st.selectbox(
                        "Verified Relevance:",
                        valid_rels,
                        index=valid_rels.index(default_h_rel) if default_h_rel in valid_rels else 0,
                        key=f"h_rel_{rec_id}"
                    )

                    # Prepopulate themes
                    current_themes = []
                    theme_source = human_themes_raw or ai_themes_raw
                    if theme_source:
                        try:
                            parsed_th = json.loads(theme_source)
                            current_themes = [t for t in parsed_th if t in TAXONOMY_THEMES]
                        except Exception:
                            pass

                    h_themes_choice = st.multiselect(
                        "Verified Themes (Taxonomy):",
                        TAXONOMY_THEMES,
                        default=current_themes,
                        key=f"h_themes_{rec_id}"
                    )

                with rf_col2:
                    h_excerpt = st.text_input(
                        "Evidence Excerpt (Substring):",
                        value=human_ev or ai_excerpt or "",
                        key=f"h_ev_{rec_id}",
                        help="Exact verbatim quote supporting this classification"
                    )

                    h_notes = st.text_area(
                        "Reviewer Notes / Commentary:",
                        value=rev_notes,
                        key=f"h_notes_{rec_id}",
                        height=68,
                        placeholder="e.g. User stopped due to market dip rather than UI friction..."
                    )

                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("✅ Approve & Save Review", key=f"btn_save_{rec_id}", type="primary", use_container_width=True):
                        save_manual_review(
                            record_id=rec_id,
                            human_relevance=h_rel_choice,
                            human_themes=h_themes_choice,
                            human_evidence=h_excerpt,
                            reviewer_notes=h_notes,
                            review_status="reviewed",
                            error_category="correct" if (ai_rel and ai_rel == h_rel_choice) else "wrong_relevance"
                        )
                        st.success("Review saved and logged to audit trail!")
                        st.rerun()

                with btn_col2:
                    if is_analysed and st.button("⚡ Quick Approve AI", key=f"btn_quick_{rec_id}", use_container_width=True):
                        # Quick approve accepts AI classifications directly
                        parsed_th = []
                        if ai_themes_raw:
                            try:
                                parsed_th = json.loads(ai_themes_raw)
                            except Exception:
                                pass
                        save_manual_review(
                            record_id=rec_id,
                            human_relevance=ai_rel or "directly_relevant",
                            human_themes=parsed_th,
                            human_evidence=ai_excerpt,
                            reviewer_notes="Quick approved AI analysis.",
                            review_status="reviewed",
                            error_category="correct"
                        )
                        st.success("AI analysis approved!")
                        st.rerun()

                with btn_col3:
                    if st.button("❌ Reject Record", key=f"btn_rej_{rec_id}", use_container_width=True):
                        save_manual_review(
                            record_id=rec_id,
                            human_relevance="not_relevant",
                            human_themes=[],
                            human_evidence=None,
                            reviewer_notes="Rejected by reviewer as non-relevant noise.",
                            review_status="rejected",
                            error_category="wrong_relevance"
                        )
                        st.warning("Record marked as rejected.")
                        st.rerun()

            st.markdown("<hr style='margin: 16px 0; border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
