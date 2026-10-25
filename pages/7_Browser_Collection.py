"""
pages/7_Browser_Collection.py — Browser Collection Management (Milestone 3.3).

Monitor the local FastAPI receiver endpoint, review incoming quotes captured via the Chrome extension,
approve/discard submissions, and send approved evidence to the AI analysis pipeline.
"""

import streamlit as st
import pandas as pd
import httpx
from core.database import init_db, get_connection
from core.ui_helpers import apply_custom_styles, render_sidebar_status
from core.analysis import run_analysis

# 1. Page Configuration
st.set_page_config(
    page_title="Browser Collection | SIP Discovery Engine",
    page_icon="🌐",
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
        <div class="hero-title">🌐 Browser-Assisted Research & Extension Inbox</div>
        <p class="hero-subtitle">
            Collect verified excerpts, Reddit posts, and Play Store reviews using the SIP Discovery Chrome extension. Review, approve, and send captured evidence directly to the synthesis engine.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.info(
    "💡 **Architecture Reminder:** The Chrome Extension and FastAPI receiver operate strictly locally (`127.0.0.1`). "
    "CSV and survey imports remain 100% operational regardless of whether the extension server is running."
)

# 3. Server Health & Setup Diagnostics
def check_server_health():
    try:
        r = httpx.get("http://127.0.0.1:8000/api/health", timeout=0.6)
        if r.status_code == 200:
            return True, r.json()
    except Exception:
        pass
    return False, None

server_online, health_data = check_server_health()

col_status, col_install = st.columns([1, 1])

with col_status:
    if server_online:
        st.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 8px; padding: 12px 16px;">
                <span class="status-dot status-dot-green"></span>
                <strong style="color: #34D399;">Receiver Server Online</strong> &bull; <code>http://127.0.0.1:8000</code>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 8px; padding: 12px 16px;">
                <span class="status-dot status-dot-red"></span>
                <strong style="color: #F87171;">Receiver Server Offline</strong> &bull; Start via <code>python extension_server/run_server.py</code>
            </div>
            """,
            unsafe_allow_html=True
        )

with col_install:
    with st.expander("🛠️ How to Launch Server & Install Extension"):
        st.markdown(
            """
            **Step 1: Start Receiver Server**
            ```powershell
            python extension_server/run_server.py
            ```

            **Step 2: Load Chrome Extension**
            1. Open Google Chrome and navigate to `chrome://extensions/`
            2. Enable **Developer mode** (top-right toggle switch)
            3. Click **Load unpacked** (top-left button)
            4. Select the `chrome_extension` folder in this project directory
            5. Highlight any text on any page and click the extension icon to save!
            """
        )

st.markdown("---")

# 4. Fetch Browser Collected Submissions
with get_connection() as conn:
    rows = conn.execute(
        """
        SELECT 
            r.record_id,
            r.source,
            r.text,
            r.source_url,
            r.collection_date,
            r.duplicate_status,
            a.review_status,
            a.ai_relevance,
            a.ai_themes
        FROM records r
        LEFT JOIN analysis_results a ON r.record_id = a.record_id
        WHERE r.collection_method = 'chrome_extension'
        ORDER BY r.created_at DESC
        LIMIT 50
        """
    ).fetchall()

browser_records = [dict(r) for r in rows]

# Metric Overview
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Total Captured Quotes", len(browser_records))
with m2:
    duplicates_cnt = sum(1 for r in browser_records if r["duplicate_status"] == "exact_duplicate")
    st.metric("Duplicate Flagged", duplicates_cnt)
with m3:
    analysed_cnt = sum(1 for r in browser_records if r["ai_relevance"] is not None)
    st.metric("Analysed by AI", analysed_cnt)

st.markdown("<br/>", unsafe_allow_html=True)

# Action Row: Batch Analyse Approved Browser Records
col_act1, col_act2 = st.columns([2, 1])
with col_act1:
    st.markdown("### 📥 Captured Evidence Submissions")
with col_act2:
    unanalysed_ids = [r["record_id"] for r in browser_records if r["ai_relevance"] is None]
    if unanalysed_ids:
        if st.button(f"⚡ Analyse {len(unanalysed_ids)} Unanalysed Quotes", type="primary"):
            with st.spinner("Processing browser evidence with Groq pipeline..."):
                res = run_analysis(record_ids=unanalysed_ids)
                st.success(f"Analysed {res['analysed']} records! (Errors: {res['errors']})")
                st.rerun()

if not browser_records:
    st.info("ℹ️ No quotes captured via the Chrome extension yet. Highlight text on a webpage and click the extension icon to capture quotes directly.")
else:
    for rec in browser_records:
        rid = rec["record_id"]
        dup_tag = "⚠️ [EXACT DUPLICATE]" if rec["duplicate_status"] == "exact_duplicate" else "✅ [UNIQUE]"
        rev_tag = f"Review: {rec.get('review_status', 'pending').upper()}"
        
        card_header = f"{rec['source']} &bull; {rec['text'][:90]}... &bull; {dup_tag} &bull; {rev_tag}"
        
        with st.expander(card_header, expanded=False):
            st.markdown(f"<div class='glass-card'><strong>Full Evidence Text:</strong><br/>{rec['text']}</div>", unsafe_allow_html=True)
            
            c_meta1, c_meta2 = st.columns(2)
            with c_meta1:
                st.markdown(f"**Source URL:** [{rec['source_url'] or 'N/A'}]({rec['source_url']})")
                st.markdown(f"**Collected Date:** {rec['collection_date']}")
            with c_meta2:
                st.markdown(f"**Duplicate Status:** `{rec['duplicate_status']}`")
                ai_info = f"Relevance: {rec['ai_relevance']} | Themes: {rec['ai_themes']}" if rec['ai_relevance'] else "Pending analysis"
                st.markdown(f"**AI Extraction:** {ai_info}")

            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                if st.button("🗑️ Remove Quote", key=f"del_rec_{rid}"):
                    with get_connection() as conn:
                        conn.execute("DELETE FROM analysis_results WHERE record_id = ?", (rid,))
                        conn.execute("DELETE FROM records WHERE record_id = ?", (rid,))
                    st.success("Removed from research records.")
                    st.rerun()
