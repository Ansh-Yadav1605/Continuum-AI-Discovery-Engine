"""
extension_server/server.py — Unified Local Backend API & Chrome Extension Receiver.

Features:
- Binds strictly to 127.0.0.1 (local-first safety).
- Serves the frontend (index.html, assets, data) at http://127.0.0.1:8000
- REST API for research retrieval: /api/records (filtered by all, primary, secondary)
- Live database statistics: /api/stats
- Secondary research collection pipeline: /api/fetch-url (SSRF safe, rate-limit aware)
- Manual secondary entry: /api/manual-secondary
- Chrome Extension receiver: /api/collect (authenticated via EXTENSION_AUTH_TOKEN)
- Preserves all database integrity and deduplication checks.
"""

import os
import re
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from core.database import get_connection, init_db, now_iso
from core.secondary_collection import (
    fetch_secondary_url,
    import_manual_secondary_record,
    collect_from_platform
)
from core.export import (
    export_research_data_csv,
    export_research_data_json,
    export_themes,
    export_problems,
    export_evidence_citations,
    export_contradictions_report,
    generate_methodology,
    export_evidence_log
)

# Load environment configuration
load_dotenv()

app = FastAPI(
    title="Continuum AI — SIP Discovery Engine Server",
    description="Local-first unified backend for Primary & Secondary Research.",
    version="2.4.0"
)

# CORS configuration: Production-ready and environment-aware
allowed_origins_list = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

frontend_url = os.getenv("FRONTEND_URL", "").strip()
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()

for origin_source in [frontend_url, allowed_origins_env]:
    if origin_source:
        for u in origin_source.split(","):
            cleaned = u.strip().rstrip("/")
            if cleaned and cleaned not in allowed_origins_list:
                allowed_origins_list.append(cleaned)

allow_vercel_previews = os.getenv("ALLOW_VERCEL_PREVIEWS", "true").lower() in ("true", "1", "yes")
if allow_vercel_previews:
    cors_origin_regex = r"^(chrome-extension://.*|https://.*\.vercel\.app|http://127\.0\.0\.1:.*|http://localhost:.*)$"
else:
    cors_origin_regex = r"^(chrome-extension://.*|http://127\.0\.0\.1:.*|http://localhost:.*)$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

HTML_TAG_RE = re.compile(r"<[^>]+>")


def sanitize_text(text: str) -> str:
    """Strip HTML tags and normalize excessive internal whitespace."""
    no_html = HTML_TAG_RE.sub(" ", text)
    cleaned = " ".join(no_html.split())
    return cleaned


def compute_text_hash(text: str) -> str:
    """Compute normalized SHA-256 hash for deduplication."""
    norm = " ".join(text.lower().split())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def get_expected_auth_token() -> str:
    return os.getenv("EXTENSION_AUTH_TOKEN", "sip_dev_token_groww_2026").strip()


# Request / Response Schemas
class CollectRequest(BaseModel):
    text: str = Field(..., max_length=10000, description="Selected evidence text")
    source_url: Optional[str] = Field(default="", description="Webpage URL where text was captured")
    source: Optional[str] = Field(default="Browser Research", description="Source label")
    collected_at: Optional[str] = Field(default=None, description="ISO timestamp")
    auth_token: str = Field(..., description="Extension authentication secret")


class CollectResponse(BaseModel):
    record_id: str
    duplicate_status: str
    message: str
    created_at: str


class FetchUrlRequest(BaseModel):
    url: str = Field(..., description="Public permitted URL to fetch")
    source_name: Optional[str] = Field(default=None, description="Custom label for source")


class ManualSecondaryRequest(BaseModel):
    text: str = Field(..., min_length=15, description="Secondary research excerpt or notes")
    title: Optional[str] = Field(default="Manual Secondary Excerpt", description="Document or section title")
    source_name: Optional[str] = Field(default="Manual Secondary Entry", description="Source name")
    source_url: Optional[str] = Field(default=None, description="Optional URL or citation")
    publication_date: Optional[str] = Field(default=None, description="YYYY-MM-DD publication date")


class CollectSecondaryRequest(BaseModel):
    platform: str = Field(default="url", description="url, youtube, reddit, google_play, trustpilot, or manual")
    target: Optional[str] = Field(default=None, description="Target URL, review text, or search query")
    url: Optional[str] = Field(default=None, description="Target URL")
    query: Optional[str] = Field(default=None, description="Optional search query or notes")
    limit: Optional[int] = Field(default=5, ge=1, le=20)
    title: Optional[str] = Field(default=None, description="Optional title")
    source_name: Optional[str] = Field(default=None, description="Custom source label")


@app.on_event("startup")
def startup_event():
    """Ensure database schema exists on server startup."""
    init_db()


# ========================================================
# REST API Endpoints
# ========================================================

@app.get("/api/health")
def health_check():
    """Connectivity diagnostic for extension, UI, and test suites."""
    now = datetime.now(timezone.utc).isoformat()
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1").fetchone()
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "timestamp": now,
        "database": "connected" if db_ok else "disconnected",
        "service": "Continuum AI Unified Research Engine"
    }


@app.get("/api/stats")
def get_stats():
    """
    Returns actual counts and source breakdowns directly from SQLite database.
    Excludes quarantined test records from all active counts.
    """
    with get_connection() as conn:
        total = conn.execute("SELECT count(*) FROM records WHERE COALESCE(is_quarantined, 0) = 0").fetchone()[0]
        primary_cnt = conn.execute("SELECT count(*) FROM records WHERE COALESCE(is_quarantined, 0) = 0 AND source_category = 'primary'").fetchone()[0]
        secondary_cnt = conn.execute("SELECT count(*) FROM records WHERE COALESCE(is_quarantined, 0) = 0 AND source_category = 'secondary'").fetchone()[0]
        quarantined_cnt = conn.execute("SELECT count(*) FROM records WHERE is_quarantined = 1").fetchone()[0]

        primary_vault_cnt = conn.execute("SELECT count(*) FROM records WHERE is_quarantined = 1 AND source_category = 'primary' AND (respondent_id LIKE 'RESP-%' OR respondent_id LIKE 'INT-%')").fetchone()[0]
        synthetic_cnt = conn.execute("SELECT count(*) FROM records WHERE is_quarantined = 1 AND (quarantine_reason = 'synthetic_test_seed' OR source IN ('Primary Survey', 'Primary User Interview'))").fetchone()[0]

        sources_rows = conn.execute("""
            SELECT source, source_category, count(*) as count 
            FROM records 
            WHERE COALESCE(is_quarantined, 0) = 0
            GROUP BY source, source_category
            ORDER BY count DESC
        """).fetchall()

        sources = [
            {"source": r["source"], "category": r["source_category"] or "secondary", "count": r["count"]}
            for r in sources_rows
        ]

    return {
        "total_records": total,
        "primary_records": primary_cnt,
        "secondary_records": secondary_cnt,
        "quarantined_records": quarantined_cnt,
        "primary_quarantined_records": primary_vault_cnt,
        "synthetic_quarantined_records": synthetic_cnt,
        "sources": sources
    }


@app.get("/api/records")
def get_records_endpoint(
    source_type: str = Query(default="all", pattern="^(all|primary|secondary|interviews|quarantined|full)$"),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=2000),
    offset: int = Query(default=0, ge=0)
):
    """
    Returns research records filtered by source_type (all, primary, secondary, interviews, quarantined, full),
    with free-text search support and non-identifying fields.
    """
    where_clauses = []
    params = []

    if source_type == "quarantined":
        where_clauses.append("is_quarantined = 1")
    elif source_type == "primary":
        # All 34 Primary 1:1 records (27 Survey + 7 Interview Notes)
        where_clauses.append("source_category = 'primary' AND (respondent_id LIKE 'RESP-%' OR respondent_id LIKE 'INT-%')")
    elif source_type == "interviews":
        # Specifically the 7 genuine 1:1 qualitative interview responses
        where_clauses.append("respondent_id LIKE 'INT-%'")
    elif source_type == "secondary":
        where_clauses.append("COALESCE(is_quarantined, 0) = 0 AND source_category = 'secondary'")
    elif source_type == "full":
        # All records in DB including vault
        pass
    else: # "all" - active records
        where_clauses.append("COALESCE(is_quarantined, 0) = 0")

    if search and search.strip():
        q = f"%{search.strip()}%"
        where_clauses.append("(text LIKE ? OR title LIKE ? OR source LIKE ? OR respondent_id LIKE ?)")
        params.extend([q, q, q, q])

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    with get_connection() as conn:
        # Total matching
        count_sql = f"SELECT count(*) FROM records {where_sql}"
        total_matching = conn.execute(count_sql, params).fetchone()[0]

        # Fetch records
        query_sql = f"""
            SELECT record_id, source, record_type, title, source_category,
                   text, source_url, publication_date, rating, collection_date,
                   collection_method, respondent_id, duplicate_status, processing_status,
                   is_quarantined, quarantine_reason, created_at
            FROM records
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(query_sql, params + [limit, offset]).fetchall()

    items = []
    for r in rows:
        items.append({
            "record_id": r["record_id"],
            "source": r["source"] or "Unknown Source",
            "record_type": r["record_type"],
            "title": r["title"] or f"{r['source']} Excerpt",
            "source_category": r["source_category"] or "secondary",
            "text": r["text"],
            "source_url": r["source_url"],
            "publication_date": r["publication_date"],
            "rating": r["rating"],
            "collection_date": r["collection_date"],
            "collection_method": r["collection_method"],
            "respondent_id": r["respondent_id"],
            "duplicate_status": r["duplicate_status"],
            "processing_status": r["processing_status"] or "processed",
            "created_at": r["created_at"]
        })

    return {
        "total": total_matching,
        "source_type": source_type,
        "limit": limit,
        "offset": offset,
        "records": items
    }


@app.post("/api/fetch-url")
def fetch_url_endpoint(payload: FetchUrlRequest):
    """
    Fetches, parses, and persists secondary research from a permitted public URL.
    Enforces SSRF prevention, paywall detection, and returns structured errors on failure.
    """
    if not payload.url or not payload.url.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="URL is required."
        )

    result = fetch_secondary_url(payload.url.strip(), payload.source_name)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to fetch secondary URL.")
        )

    return result


@app.post("/api/collect-secondary")
def collect_secondary_endpoint(payload: CollectSecondaryRequest):
    """
    Unified multi-platform collection endpoint (URL, YouTube, Reddit, Play Store, Trustpilot, Manual).
    Strict veracity: Never invents synthetic records on failure; returns clear errors.
    """
    target_str = (payload.target or payload.url or payload.query or "").strip()
    if not target_str and payload.platform != "manual":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A target URL, review text, or search query is required."
        )

    result = collect_from_platform(
        platform=payload.platform,
        target=target_str,
        query=payload.query,
        limit=payload.limit or 5,
        custom_title=payload.title,
        custom_source=payload.source_name
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to collect from platform.")
        )
    return result


# ========================================================
# Research Reports & Dataset Export Endpoints
# ========================================================

@app.get("/api/reports/export")
def export_dataset_endpoint(
    scope: str = Query(default="all", pattern="^(all|primary|secondary|quarantine)$"),
    format: str = Query(default="csv", pattern="^(csv|json)$")
):
    """
    Export active research dataset in CSV or JSON format.
    Excludes quarantined test records.
    """
    if format == "csv":
        csv_content = export_research_data_csv(scope=scope)
        filename = f"continuum_ai_research_{scope}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
        )
    else:
        json_content = export_research_data_json(scope=scope)
        filename = f"continuum_ai_research_{scope}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
        )


@app.get("/api/reports/analysis")
def export_analysis_report_endpoint(
    report_type: str = Query(default="methodology", pattern="^(methodology|themes|citations|contradictions|problems|audit)$"),
    format: str = Query(default="markdown", pattern="^(markdown|json)$")
):
    """
    Generate readable analysis reports based solely on active research records:
    - methodology: Full research disclosure narrative
    - themes: 14-category taxonomy summary table
    - citations: Key direct user quotes mapped to themes
    - contradictions: Catalyst vs friction behavioral signals
    - problems: Ranked candidate problem cards
    - audit: Human-in-the-loop AI evidence agreement log
    """
    if report_type == "methodology":
        md_text = generate_methodology()
        return PlainTextResponse(content=md_text, media_type="text/markdown")

    elif report_type == "themes":
        df, md_text = export_themes()
        if format == "json":
            return JSONResponse(content=df.to_dict(orient="records"))
        return PlainTextResponse(content=md_text, media_type="text/markdown")

    elif report_type == "citations":
        df, md_text = export_evidence_citations()
        if format == "json":
            return JSONResponse(content=df.to_dict(orient="records"))
        return PlainTextResponse(content=md_text, media_type="text/markdown")

    elif report_type == "contradictions":
        df, md_text = export_contradictions_report()
        if format == "json":
            return JSONResponse(content=df.to_dict(orient="records"))
        return PlainTextResponse(content=md_text, media_type="text/markdown")

    elif report_type == "problems":
        json_str, md_text = export_problems()
        if format == "json":
            return Response(content=json_str, media_type="application/json")
        return PlainTextResponse(content=md_text, media_type="text/markdown")

    elif report_type == "audit":
        df = export_evidence_log(include_quarantined=False)
        if format == "json":
            return JSONResponse(content=df.to_dict(orient="records"))
        return Response(
            content=df.to_csv(index=False),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=\"continuum_ai_audit_log.csv\""}
        )


@app.get("/api/reports/quarantine")
def get_quarantine_report():
    """
    Audit log of quarantined records excluded from active research.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT record_id, source, record_type, respondent_id, text, 
                   quarantine_reason, created_at
            FROM records 
            WHERE is_quarantined = 1
            ORDER BY created_at DESC
            """
        ).fetchall()
        return {
            "quarantined_count": len(rows),
            "status": "isolated_from_active_dataset",
            "records": [dict(r) for r in rows]
        }


@app.post("/api/manual-secondary")
def manual_secondary_endpoint(payload: ManualSecondaryRequest):
    """
    Manually save secondary research notes, excerpts, or report citations.
    """
    result = import_manual_secondary_record(
        text=payload.text,
        title=payload.title,
        source_name=payload.source_name,
        source_url=payload.source_url,
        publication_date=payload.publication_date
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result.get("error", "Failed to save manual secondary research.")
        )
    return result


@app.post("/api/collect", response_model=CollectResponse, status_code=status.HTTP_201_CREATED)
def collect_submission(payload: CollectRequest):
    """
    Accepts verified user-approved selection from Chrome Extension as Secondary Research.
    """
    expected_token = get_expected_auth_token()
    if not payload.auth_token or payload.auth_token.strip() != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing EXTENSION_AUTH_TOKEN"
        )

    clean_text = sanitize_text(payload.text)
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Text cannot be empty or solely whitespace/HTML."
        )

    text_hash = compute_text_hash(clean_text)
    now = datetime.now(timezone.utc).isoformat()
    pub_date = payload.collected_at or now[:10]
    coll_date = payload.collected_at or now

    with get_connection() as conn:
        existing_rows = conn.execute(
            "SELECT record_id, text FROM records WHERE length(text) > 0"
        ).fetchall()

        duplicate_status = "unique"
        existing_id = None
        for r in existing_rows:
            if compute_text_hash(r["text"]) == text_hash:
                duplicate_status = "exact_duplicate"
                existing_id = r["record_id"]
                break

        record_id = str(uuid.uuid4())
        source_label = (payload.source or "Browser Research").strip()
        source_url = (payload.source_url or "").strip()

        conn.execute(
            """
            INSERT INTO records (
                record_id, source, record_type, title, source_category,
                text, source_url, publication_date, collection_date,
                collection_method, duplicate_status, processing_status,
                is_demo, created_at
            ) VALUES (?, ?, 'browser_collected', ?, 'secondary', ?, ?, ?, ?, 'chrome_extension', ?, 'processed', 0, ?)
            """,
            (
                record_id,
                source_label,
                f"Web Capture from {source_label}",
                clean_text,
                source_url,
                pub_date[:10],
                coll_date,
                duplicate_status,
                now
            )
        )

    msg = "Record saved successfully."
    if duplicate_status == "exact_duplicate":
        msg = f"Saved, but flagged as exact duplicate of record {existing_id[:8]}."

    return CollectResponse(
        record_id=record_id,
        duplicate_status=duplicate_status,
        message=msg,
        created_at=now
    )


# ========================================================
# Frontend Static Files & Index Route
# ========================================================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mount static asset folders
assets_dir = os.path.join(ROOT_DIR, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

data_dir = os.path.join(ROOT_DIR, "data")
if os.path.exists(data_dir):
    app.mount("/data", StaticFiles(directory=data_dir), name="data")


@app.get("/")
def serve_index():
    """Serve the desktop-first Continuum AI frontend."""
    index_path = os.path.join(ROOT_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Continuum AI Server running. index.html not found in project root."}
