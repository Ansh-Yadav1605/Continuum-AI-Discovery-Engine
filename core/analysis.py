"""
core/analysis.py — Orchestrator for AI analysis and manual review.

Handles:
- Validation of AI responses against the taxonomy and schema
- Persistence to analysis_results table
- Audit logging to evidence_log table for human reviews
- Batch execution of unanalysed records
- Full manual fallback mode
"""

import json
from typing import Optional, List, Dict, Any
from core.database import get_connection, generate_id, now_iso
from core.groq_client import analyse_batch, get_model_name, validate_schema


def get_unanalysed_records(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch active records that do not yet have an entry in analysis_results."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT r.* FROM records r
            LEFT JOIN analysis_results a ON r.record_id = a.record_id
            WHERE a.analysis_id IS NULL AND COALESCE(r.is_quarantined, 0) = 0
            ORDER BY r.created_at ASC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        return [dict(row) for row in rows]


def save_analysis(
    record_id: str,
    ai_data: Dict[str, Any],
    model_used: Optional[str] = None,
    is_manual: bool = False
) -> str:
    """
    Save an AI or manual analysis result to the analysis_results table.
    """
    now = now_iso()
    analysis_id = generate_id()
    model = model_used or ("manual" if is_manual else get_model_name())

    themes_json = json.dumps(ai_data.get("themes", [])) if isinstance(ai_data.get("themes"), list) else "[]"

    with get_connection() as conn:
        # Check if an analysis already exists for this record
        existing = conn.execute(
            "SELECT analysis_id FROM analysis_results WHERE record_id = ?",
            (record_id,)
        ).fetchone()

        if existing:
            # Update existing
            analysis_id = existing["analysis_id"]
            if is_manual:
                conn.execute(
                    """
                    UPDATE analysis_results
                    SET human_relevance = ?, human_themes = ?, human_evidence = ?,
                        review_status = 'reviewed', reviewer_notes = ?, reviewed_at = ?
                    WHERE analysis_id = ?
                    """,
                    (
                        ai_data.get("human_relevance"),
                        themes_json,
                        ai_data.get("human_evidence"),
                        ai_data.get("reviewer_notes"),
                        now,
                        analysis_id
                    )
                )
            else:
                conn.execute(
                    """
                    UPDATE analysis_results
                    SET ai_relevance = ?, ai_relevance_explanation = ?, ai_evidence_excerpt = ?,
                        ai_themes = ?, ai_behaviour = ?, ai_user_need = ?, ai_workaround = ?,
                        ai_journey_stage = ?, ai_continuation_mention = ?, ai_missing_context = ?,
                        ai_explanation = ?, model_used = ?, created_at = ?
                    WHERE analysis_id = ?
                    """,
                    (
                        ai_data.get("relevance"),
                        ai_data.get("relevance_explanation"),
                        ai_data.get("evidence_excerpt"),
                        themes_json,
                        ai_data.get("behaviour"),
                        ai_data.get("user_need"),
                        ai_data.get("workaround"),
                        ai_data.get("journey_stage"),
                        ai_data.get("continuation_mention"),
                        ai_data.get("missing_context"),
                        ai_data.get("explanation"),
                        model,
                        now,
                        analysis_id
                    )
                )
        else:
            # Insert new
            if is_manual:
                conn.execute(
                    """
                    INSERT INTO analysis_results (
                        analysis_id, record_id, human_relevance, human_themes, human_evidence,
                        review_status, reviewer_notes, reviewed_at, model_used, created_at
                    ) VALUES (?, ?, ?, ?, ?, 'reviewed', ?, ?, 'manual', ?)
                    """,
                    (
                        analysis_id,
                        record_id,
                        ai_data.get("human_relevance"),
                        themes_json,
                        ai_data.get("human_evidence"),
                        ai_data.get("reviewer_notes"),
                        now,
                        now
                    )
                )
            else:
                conn.execute(
                    """
                    INSERT INTO analysis_results (
                        analysis_id, record_id, ai_relevance, ai_relevance_explanation,
                        ai_evidence_excerpt, ai_themes, ai_behaviour, ai_user_need,
                        ai_workaround, ai_journey_stage, ai_continuation_mention,
                        ai_missing_context, ai_explanation, review_status, model_used, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
                    """,
                    (
                        analysis_id,
                        record_id,
                        ai_data.get("relevance"),
                        ai_data.get("relevance_explanation"),
                        ai_data.get("evidence_excerpt"),
                        themes_json,
                        ai_data.get("behaviour"),
                        ai_data.get("user_need"),
                        ai_data.get("workaround"),
                        ai_data.get("journey_stage"),
                        ai_data.get("continuation_mention"),
                        ai_data.get("missing_context"),
                        ai_data.get("explanation"),
                        model,
                        now
                    )
                )

    return analysis_id


def save_manual_review(
    record_id: str,
    human_relevance: str,
    human_themes: List[str],
    human_evidence: Optional[str] = None,
    reviewer_notes: Optional[str] = None,
    review_status: str = "reviewed",
    error_category: Optional[str] = None
) -> str:
    """
    Save human reviewer annotations and record audit trail in evidence_log.
    """
    now = now_iso()
    themes_json = json.dumps(human_themes or [])

    with get_connection() as conn:
        # 1. Fetch current AI analysis to log agreement
        existing = conn.execute(
            "SELECT * FROM analysis_results WHERE record_id = ?",
            (record_id,)
        ).fetchone()

        ai_rel = existing["ai_relevance"] if existing else None
        ai_themes = existing["ai_themes"] if existing else "[]"
        ai_ev = existing["ai_evidence_excerpt"] if existing else None

        agreement = "agree" if (ai_rel and ai_rel == human_relevance) else "disagree"
        err_cat = error_category or ("correct" if agreement == "agree" else "wrong_relevance")

        if existing:
            conn.execute(
                """
                UPDATE analysis_results
                SET human_relevance = ?, human_themes = ?, human_evidence = ?,
                    review_status = ?, reviewer_notes = ?, reviewed_at = ?
                WHERE record_id = ?
                """,
                (
                    human_relevance,
                    themes_json,
                    human_evidence,
                    review_status,
                    reviewer_notes,
                    now,
                    record_id
                )
            )
        else:
            # Record reviewed directly without prior AI analysis
            analysis_id = generate_id()
            conn.execute(
                """
                INSERT INTO analysis_results (
                    analysis_id, record_id, human_relevance, human_themes, human_evidence,
                    review_status, reviewer_notes, reviewed_at, model_used, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'manual', ?)
                """,
                (
                    analysis_id,
                    record_id,
                    human_relevance,
                    themes_json,
                    human_evidence,
                    review_status,
                    reviewer_notes,
                    now,
                    now
                )
            )

        # 2. Append entry to evidence_log audit trail
        log_id = generate_id()
        conn.execute(
            """
            INSERT INTO evidence_log (
                log_id, record_id, ai_relevance, human_relevance,
                ai_themes, human_themes, ai_evidence, human_evidence,
                agreement, error_category, correction, final_label,
                reviewer_notes, reviewed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                log_id,
                record_id,
                ai_rel,
                human_relevance,
                ai_themes,
                themes_json,
                ai_ev,
                human_evidence,
                agreement,
                err_cat,
                f"Relevance: {human_relevance}; Themes: {themes_json}",
                human_relevance,
                reviewer_notes,
                now
            )
        )

    return record_id


def run_analysis(
    record_ids: Optional[List[str]] = None,
    batch_size: int = 5,
    progress_callback = None
) -> Dict[str, Any]:
    """
    Orchestrate AI batch analysis for specified or unanalysed records.

    Args:
        record_ids: Optional list of record UUIDs to analyse. If None, picks next batch of unanalysed records.
        batch_size: Max number of records to process in this run.
        progress_callback: Optional callable(current, total, record_id)

    Returns:
        Summary dict:
        {
          "requested": int,
          "analysed": int,
          "errors": int,
          "skipped": int,
          "error_details": list
        }
    """
    if record_ids:
        with get_connection() as conn:
            placeholders = ", ".join(["?"] * len(record_ids[:batch_size]))
            records = conn.execute(
                f"SELECT * FROM records WHERE record_id IN ({placeholders})",
                record_ids[:batch_size]
            ).fetchall()
            records_to_process = [dict(r) for r in records]
    else:
        records_to_process = get_unanalysed_records(limit=batch_size)

    if not records_to_process:
        return {
            "requested": 0,
            "analysed": 0,
            "errors": 0,
            "skipped": 0,
            "error_details": []
        }

    batch_res = analyse_batch(
        records_to_process,
        batch_size=batch_size,
        progress_callback=progress_callback
    )

    analysed_count = 0
    errors_count = 0
    error_details = []

    for item in batch_res["results"]:
        rec_id = item["record_id"]
        if item["success"] and item["data"]:
            save_analysis(rec_id, item["data"], model_used=item["data"].get("model_used"))
            analysed_count += 1
        else:
            errors_count += 1
            error_details.append({
                "record_id": rec_id,
                "error": item["error"]
            })
            # Log ai_error in analysis_results so it's transparent to the PM
            save_analysis(
                rec_id,
                {
                    "relevance": "ambiguous",
                    "relevance_explanation": f"AI analysis error: {item['error']}",
                    "evidence_excerpt": None,
                    "themes": ["Unclear or insufficient evidence"],
                    "behaviour": None,
                    "user_need": None,
                    "workaround": None,
                    "journey_stage": "unknown",
                    "continuation_mention": "none",
                    "missing_context": "Automatic analysis failed. Requires manual review.",
                    "explanation": f"Error during Groq completion: {item['error']}"
                },
                model_used="ai_error"
            )

    return {
        "requested": len(records_to_process),
        "analysed": analysed_count,
        "errors": errors_count,
        "skipped": 0,
        "error_details": error_details
    }
