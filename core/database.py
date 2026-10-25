"""
core/database.py — SQLite schema initializer, connection helper, and CRUD utilities.

All 8 tables are created with CREATE TABLE IF NOT EXISTS (safe for re-runs).
Pre-populates the 14-category provisional taxonomy into the themes table.
Database path: data/sip_discovery.db (relative to project root).
"""

import sqlite3
import os
import uuid
import json
from datetime import datetime, timezone
from contextlib import contextmanager

# Database location (relative to project root)
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "sip_discovery.db")


def _ensure_data_dir():
    """Create the data/ directory if it doesn't exist."""
    os.makedirs(DB_DIR, exist_ok=True)


@contextmanager
def get_connection():
    """
    Context-managed SQLite connection.
    
    Usage:
        with get_connection() as conn:
            conn.execute("SELECT ...")
    
    Automatically commits on success, rolls back on exception.
    """
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ──────────────────────────────────────────────
# Schema Definitions
# ──────────────────────────────────────────────

SCHEMA_SQL = """
-- 1. records: Unified research records from all ingestion channels
CREATE TABLE IF NOT EXISTS records (
    record_id           TEXT PRIMARY KEY,
    source              TEXT,
    record_type         TEXT,
    title               TEXT,
    source_category     TEXT DEFAULT 'secondary',
    text                TEXT NOT NULL,
    text_edited         TEXT,
    source_url          TEXT,
    publication_date    TEXT,
    rating              REAL,
    collection_date     TEXT,
    collection_method   TEXT,
    respondent_id       TEXT,
    duplicate_status    TEXT DEFAULT 'unique',
    processing_status   TEXT DEFAULT 'processed',
    is_demo             INTEGER DEFAULT 0,
    created_at          TEXT
);

-- 2. analysis_results: AI + human labels per record
CREATE TABLE IF NOT EXISTS analysis_results (
    analysis_id             TEXT PRIMARY KEY,
    record_id               TEXT,
    ai_relevance            TEXT,
    ai_relevance_explanation TEXT,
    ai_evidence_excerpt     TEXT,
    ai_themes               TEXT,
    ai_behaviour            TEXT,
    ai_user_need            TEXT,
    ai_workaround           TEXT,
    ai_journey_stage        TEXT,
    ai_continuation_mention TEXT,
    ai_missing_context      TEXT,
    ai_explanation          TEXT,
    human_relevance         TEXT,
    human_themes            TEXT,
    human_evidence          TEXT,
    review_status           TEXT DEFAULT 'pending',
    reviewer_notes          TEXT,
    reviewed_at             TEXT,
    model_used              TEXT,
    created_at              TEXT,
    FOREIGN KEY (record_id) REFERENCES records(record_id)
);

-- 3. themes: Theme taxonomy definition
CREATE TABLE IF NOT EXISTS themes (
    theme_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    theme_name          TEXT UNIQUE,
    theme_definition    TEXT,
    is_active           INTEGER DEFAULT 1,
    created_at          TEXT
);

-- 4. problem_statements: Candidate problem cards
CREATE TABLE IF NOT EXISTS problem_statements (
    problem_id              TEXT PRIMARY KEY,
    title                   TEXT,
    user_segment            TEXT,
    journey_stage           TEXT,
    observation             TEXT,
    interpretation          TEXT,
    hypothesis              TEXT,
    supporting_evidence     TEXT,
    contradictory_evidence  TEXT,
    user_need               TEXT,
    workaround              TEXT,
    consequence             TEXT,
    sip_relationship        TEXT,
    alternative_explanations TEXT,
    limitations             TEXT,
    open_questions          TEXT,
    interview_questions     TEXT,
    validation_status       TEXT DEFAULT 'needs_research',
    is_ai_generated         INTEGER DEFAULT 0,
    created_at              TEXT,
    updated_at              TEXT
);

-- 5. scores: Opportunity prioritization scores
CREATE TABLE IF NOT EXISTS scores (
    score_id            TEXT PRIMARY KEY,
    problem_id          TEXT,
    evidence_strength   INTEGER,
    sip_relevance       INTEGER,
    user_severity       INTEGER,
    product_influence   INTEGER,
    feasibility         INTEGER,
    safety_compliance   INTEGER,
    weighted_score      REAL,
    justification       TEXT,
    scored_by           TEXT,
    created_at          TEXT,
    FOREIGN KEY (problem_id) REFERENCES problem_statements(problem_id)
);

-- 6. evidence_log: AI evaluation audit trail
CREATE TABLE IF NOT EXISTS evidence_log (
    log_id              TEXT PRIMARY KEY,
    record_id           TEXT,
    ai_relevance        TEXT,
    human_relevance     TEXT,
    ai_themes           TEXT,
    human_themes        TEXT,
    ai_evidence         TEXT,
    human_evidence      TEXT,
    agreement           TEXT,
    error_category      TEXT,
    correction          TEXT,
    final_label         TEXT,
    reviewer_notes      TEXT,
    reviewed_at         TEXT,
    FOREIGN KEY (record_id) REFERENCES records(record_id)
);

-- 7. source_register: Collection metadata
CREATE TABLE IF NOT EXISTS source_register (
    source_id           TEXT PRIMARY KEY,
    source_name         TEXT,
    collection_method   TEXT,
    date_collected      TEXT,
    record_count        INTEGER DEFAULT 0,
    known_limitations   TEXT,
    permission_notes    TEXT,
    created_at          TEXT
);

-- 8. settings: Application configuration (key-value)
CREATE TABLE IF NOT EXISTS settings (
    key                 TEXT PRIMARY KEY,
    value               TEXT,
    updated_at          TEXT
);
"""


# ──────────────────────────────────────────────
# 14-Category Provisional Taxonomy
# ──────────────────────────────────────────────

PROVISIONAL_TAXONOMY = [
    (
        "Expectations vs. actual experience",
        "Covers situations where the investor's expectations about SIP returns, timeline, or experience differ from what actually happened (e.g. volatility shock, short-term negative returns)."
    ),
    (
        "SIP or investment-process understanding",
        "Gaps in the investor's understanding of how SIPs work — instalment frequency, compounding, rupee-cost averaging, fund selection, or how to modify/cancel."
    ),
    (
        "Uncertainty and confidence",
        "Feelings of doubt, worry, or lack of confidence about whether they are making the right investment choice or whether SIPs are suitable for them."
    ),
    (
        "Instalment, payment, or mandate friction",
        "Technical or process difficulties with payments — UPI auto-debit, e-mandate setup, bank limits, deduction failures, or payment gateway issues."
    ),
    (
        "Changing circumstances",
        "Life events explicitly mentioned by the investor — job changes, income reduction, liquidity needs, or other personal/financial changes affecting SIP continuation."
    ),
    (
        "Habits, attention, and routine",
        "Patterns related to checking the app, monitoring returns, maintaining the SIP habit, or attention drift over time."
    ),
    (
        "Trust and transparency",
        "Concerns about the platform's trustworthiness, fee transparency, fund manager reliability, or hidden charges."
    ),
    (
        "Support and issue resolution",
        "Experiences with customer support, complaint resolution, response times, or unresolved issues affecting confidence."
    ),
    (
        "Conflicting information or misunderstanding",
        "Contradictory advice from different sources, misinterpretation of market events, or confusion caused by external information."
    ),
    (
        "Product usability",
        "Difficulty navigating the app, finding information, understanding the dashboard, or performing SIP-related actions within the product."
    ),
    (
        "Explicitly reported reasons for continuing",
        "Specific reasons the investor gives for keeping their SIP active — long-term goals, discipline, positive returns, advisor recommendation, etc."
    ),
    (
        "Explicitly reported reasons for pausing or stopping",
        "Specific reasons the investor gives for pausing, reducing, or stopping their SIP — other than changing circumstances."
    ),
    (
        "Other emerging themes",
        "Evidence that does not fit neatly into the above categories but may represent a new or unexpected pattern."
    ),
    (
        "Unclear or insufficient evidence",
        "Records where the text does not provide enough context to classify confidently. Requires human review."
    ),
]


def init_db():
    """
    Initialize the database: create all 8 tables and pre-populate the
    provisional taxonomy if the themes table is empty.
    
    Safe to call multiple times (CREATE TABLE IF NOT EXISTS).
    """
    _ensure_data_dir()
    with get_connection() as conn:
        # Create all tables
        conn.executescript(SCHEMA_SQL)

        # Safe auto-migration for newly added columns
        existing_cols = [c[1] for c in conn.execute("PRAGMA table_info(records)").fetchall()]
        if "source_category" not in existing_cols:
            conn.execute("ALTER TABLE records ADD COLUMN source_category TEXT DEFAULT 'secondary'")
        if "title" not in existing_cols:
            conn.execute("ALTER TABLE records ADD COLUMN title TEXT")
        if "processing_status" not in existing_cols:
            conn.execute("ALTER TABLE records ADD COLUMN processing_status TEXT DEFAULT 'processed'")
        if "is_quarantined" not in existing_cols:
            conn.execute("ALTER TABLE records ADD COLUMN is_quarantined INTEGER DEFAULT 0")
        if "quarantine_reason" not in existing_cols:
            conn.execute("ALTER TABLE records ADD COLUMN quarantine_reason TEXT")
        
        # Pre-populate themes if empty
        existing = conn.execute("SELECT COUNT(*) FROM themes").fetchone()[0]
        if existing == 0:
            now = datetime.now(timezone.utc).isoformat()
            conn.executemany(
                "INSERT INTO themes (theme_name, theme_definition, is_active, created_at) VALUES (?, ?, 1, ?)",
                [(name, defn, now) for name, defn in PROVISIONAL_TAXONOMY]
            )

        # Pre-populate candidate problems from candidate_problems.json if empty
        prob_count = conn.execute("SELECT COUNT(*) FROM problem_statements").fetchone()[0]
        if prob_count == 0:
            _seed_candidate_problems(conn)

        # Pre-populate sample records if records table is empty
        rec_count = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        if rec_count == 0:
            _seed_sample_records()


def _seed_candidate_problems(conn):
    """Seed audited candidate problem statements and scores from candidate_problems.json."""
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "candidate_problems.json")
    if not os.path.exists(json_path):
        json_path = "candidate_problems.json"
    if not os.path.exists(json_path):
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        now = datetime.now(timezone.utc).isoformat()
        weights = {
            "evidence_strength": 0.25,
            "sip_relevance": 0.25,
            "user_severity": 0.15,
            "product_influence": 0.15,
            "feasibility": 0.10,
            "safety_compliance": 0.10
        }

        for item in data.get("candidate_problems", []):
            pid = item.get("problem_id")
            title = item.get("title")
            orig = item.get("original_candidate", {})
            rev = item.get("revised_candidate", {})

            obs = orig.get("observation", "")
            interp = orig.get("interpretation", "")
            hyp = orig.get("hypothesis", "")
            limitations = orig.get("limitations", "")
            statement = rev.get("problem_statement", "")

            conn.execute(
                """
                INSERT OR IGNORE INTO problem_statements (
                    problem_id, title, user_segment, journey_stage, observation,
                    interpretation, hypothesis, user_need, workaround, limitations,
                    validation_status, is_ai_generated, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pid,
                    title,
                    "First-time mutual fund investors",
                    "Months 1-3 post initial instalment",
                    obs or statement,
                    interp,
                    hyp,
                    "Predictable expectations & seamless automated investing",
                    "Manual interventions or premature cancellation",
                    limitations or "Observational data; requires 1:1 validation.",
                    "needs_research",
                    0,
                    now,
                    now
                )
            )

            raw_scores = orig.get("scores", {})
            ev_s = min(5, max(1, round(raw_scores.get("evidenceStrength", 80) / 20)))
            sip_r = min(5, max(1, round(raw_scores.get("relevance", 80) / 20)))
            sev = min(5, max(1, round(raw_scores.get("severity", 80) / 20)))
            prod_inf = min(5, max(1, round(raw_scores.get("influence", 80) / 20)))
            feas = min(5, max(1, round(raw_scores.get("feasibility", 80) / 20)))
            safe_c = min(5, max(1, round(raw_scores.get("compliance", 80) / 20)))

            weighted = (
                ev_s * weights["evidence_strength"] +
                sip_r * weights["sip_relevance"] +
                sev * weights["user_severity"] +
                prod_inf * weights["product_influence"] +
                feas * weights["feasibility"] +
                safe_c * weights["safety_compliance"]
            )

            conn.execute(
                """
                INSERT OR IGNORE INTO scores (
                    score_id, problem_id, evidence_strength, sip_relevance,
                    user_severity, product_influence, feasibility, safety_compliance,
                    weighted_score, justification, scored_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"score_{pid}",
                    pid,
                    ev_s,
                    sip_r,
                    sev,
                    prod_inf,
                    feas,
                    safe_c,
                    round(weighted, 2),
                    f"Audited candidate score based on {rev.get('total_verified_records', 10)} verified citations.",
                    "Audited Baseline",
                    now
                )
            )
    except Exception:
        pass


def _seed_sample_records():
    """Load sample datasets into records table if database is completely empty."""
    try:
        from tests.sample_data import load_sample_dataset
        load_sample_dataset()
    except Exception:
        pass


# ──────────────────────────────────────────────
# CRUD Utilities
# ──────────────────────────────────────────────

def generate_id():
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def now_iso():
    """Current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def insert_record(conn, record_dict):
    """
    Insert a single record into the records table.
    
    Args:
        conn: SQLite connection (from get_connection context)
        record_dict: dict with keys matching records table columns.
                     record_id and created_at are auto-generated if missing.
    """
    record_dict.setdefault("record_id", generate_id())
    record_dict.setdefault("created_at", now_iso())
    record_dict.setdefault("collection_date", now_iso())
    record_dict.setdefault("duplicate_status", "unique")
    record_dict.setdefault("is_demo", 0)
    
    columns = list(record_dict.keys())
    placeholders = ", ".join(["?"] * len(columns))
    col_names = ", ".join(columns)
    
    conn.execute(
        f"INSERT INTO records ({col_names}) VALUES ({placeholders})",
        [record_dict[col] for col in columns]
    )
    return record_dict["record_id"]


def get_record(conn, record_id):
    """Fetch a single record by ID."""
    row = conn.execute(
        "SELECT * FROM records WHERE record_id = ?", (record_id,)
    ).fetchone()
    return dict(row) if row else None


def get_records(conn, filters=None, limit=100, offset=0, include_quarantined=False):
    """
    Fetch records with optional filtering.
    
    Args:
        filters: dict of {column: value} for WHERE clauses
        limit: max records to return
        offset: pagination offset
        include_quarantined: whether to include quarantined test records (default False)
    
    Returns:
        List of record dicts
    """
    query = "SELECT * FROM records"
    params = []
    conditions = []
    
    if not include_quarantined:
        conditions.append("COALESCE(is_quarantined, 0) = 0")
    
    if filters:
        for col, val in filters.items():
            if val is not None:
                conditions.append(f"{col} = ?")
                params.append(val)
                
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def count_records(conn, filters=None, include_quarantined=False):
    """Count records with optional filtering."""
    query = "SELECT COUNT(*) FROM records"
    params = []
    conditions = []
    
    if not include_quarantined:
        conditions.append("COALESCE(is_quarantined, 0) = 0")
    
    if filters:
        for col, val in filters.items():
            if val is not None:
                conditions.append(f"{col} = ?")
                params.append(val)
                
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    return conn.execute(query, params).fetchone()[0]


def get_all_themes(conn, active_only=True):
    """Fetch all themes from the taxonomy."""
    query = "SELECT * FROM themes"
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY theme_id"
    rows = conn.execute(query).fetchall()
    return [dict(row) for row in rows]


def get_setting(conn, key, default=None):
    """Get a setting value by key."""
    row = conn.execute(
        "SELECT value FROM settings WHERE key = ?", (key,)
    ).fetchone()
    return row[0] if row else default


def set_setting(conn, key, value):
    """Set or update a setting."""
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
        (key, value, now_iso())
    )


def search_records(conn, search_text, limit=50, include_quarantined=False):
    """Search records by text content (case-insensitive substring match)."""
    quarantine_clause = "" if include_quarantined else "AND COALESCE(is_quarantined, 0) = 0"
    rows = conn.execute(
        f"SELECT * FROM records WHERE text LIKE ? {quarantine_clause} ORDER BY created_at DESC LIMIT ?",
        (f"%{search_text}%", limit)
    ).fetchall()
    return [dict(row) for row in rows]


def get_records_with_analysis(conn, filters=None, limit=100, offset=0, include_quarantined=False):
    """
    Fetch records joined with their analysis results.
    Returns records with all analysis columns (NULL if not yet analysed).
    Excludes quarantined records by default.
    """
    query = """
        SELECT r.*, a.analysis_id, a.ai_relevance, a.ai_relevance_explanation,
               a.ai_evidence_excerpt, a.ai_themes, a.ai_behaviour, a.ai_user_need,
               a.ai_workaround, a.ai_journey_stage, a.ai_continuation_mention,
               a.ai_missing_context, a.ai_explanation,
               a.human_relevance, a.human_themes, a.human_evidence,
               a.review_status AS analysis_review_status, a.reviewer_notes,
               a.reviewed_at, a.model_used
        FROM records r
        LEFT JOIN analysis_results a ON r.record_id = a.record_id
    """
    params = []
    conditions = []
    
    if not include_quarantined:
        conditions.append("COALESCE(r.is_quarantined, 0) = 0")
    
    if filters:
        for col, val in filters.items():
            if val is not None:
                # Prefix with table alias for ambiguous columns
                if col in ("review_status",):
                    conditions.append(f"a.{col} = ?")
                elif col == "ai_relevance":
                    conditions.append(f"a.ai_relevance = ?")
                elif col == "record_type":
                    conditions.append(f"r.record_type = ?")
                elif col == "source":
                    conditions.append(f"r.source = ?")
                else:
                    conditions.append(f"r.{col} = ?")
                params.append(val)
                
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY r.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def quarantine_record(conn, record_id: str, reason: str = "synthetic_test_seed"):
    """
    Quarantine a record, isolating it from all active discovery, queries, and reports.
    Invalidates any attached analysis results without permanent deletion.
    """
    conn.execute(
        "UPDATE records SET is_quarantined = 1, quarantine_reason = ? WHERE record_id = ?",
        (reason, record_id)
    )
    conn.execute(
        "UPDATE analysis_results SET review_status = 'invalidated', reviewer_notes = ? WHERE record_id = ?",
        (f"Auto-invalidated: record quarantined ({reason})", record_id)
    )


def unquarantine_record(conn, record_id: str):
    """Restore a quarantined record back to active research."""
    conn.execute(
        "UPDATE records SET is_quarantined = 0, quarantine_reason = NULL WHERE record_id = ?",
        (record_id,)
    )


def get_quarantined_records(conn):
    """Retrieve all quarantined records for audit and compliance inspection."""
    rows = conn.execute(
        "SELECT * FROM records WHERE is_quarantined = 1 ORDER BY created_at DESC"
    ).fetchall()
    return [dict(row) for row in rows]
