"""
core/evaluation.py — AI Evidence Log, human evaluation benchmark, and agreement metrics.

Supports Milestone 2.3:
- create_evaluation_entry(): logs human vs. AI comparison, categorizes discrepancies.
- calculate_metrics(): computes agreement rates, per-theme Precision/Recall/F1 with data sufficiency guards (<5 instances marked insufficient, <10 total flags sample warning).
- export_evidence_log_csv(): exports full traceable audit log.
- get_benchmark_candidates(): selects diverse records for structured human evaluation.
"""

import json
import uuid
import io
import csv
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from core.database import get_connection

ERROR_CATEGORIES = [
    "correct",
    "over_interpretation",
    "missed_theme",
    "wrong_relevance",
    "hallucination",
    "other"
]

TARGET_THRESHOLDS = {
    "relevance_agreement": 75.0,  # Target: >= 75%
    "theme_macro_f1": 0.60,       # Target: >= 0.60
    "max_hallucination_rate": 5.0 # Target: < 5%
}


def get_benchmark_candidates(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Curates a diverse set of ~20 records for human evaluation benchmark:
    Mix of directly relevant, indirectly relevant, ambiguous, not relevant, and multi-theme cases.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT 
                r.record_id,
                r.source,
                r.record_type,
                r.text,
                r.rating,
                a.ai_relevance,
                a.ai_relevance_explanation,
                a.ai_evidence_excerpt,
                a.ai_themes,
                a.ai_behaviour,
                a.ai_user_need,
                a.ai_missing_context,
                a.review_status,
                a.human_relevance,
                a.human_themes
            FROM records r
            INNER JOIN analysis_results a ON r.record_id = a.record_id
            WHERE COALESCE(r.is_quarantined, 0) = 0
              AND (a.review_status != 'invalidated' OR a.review_status IS NULL)
            ORDER BY 
                CASE 
                    WHEN a.ai_relevance = 'ambiguous' THEN 1
                    WHEN a.ai_relevance = 'directly_relevant' THEN 2
                    WHEN a.ai_relevance = 'not_relevant' THEN 3
                    ELSE 4
                END,
                r.created_at DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def create_evaluation_entry(
    record_id: str,
    human_relevance: str,
    human_themes: List[str],
    human_evidence: str,
    error_category: str = "correct",
    reviewer_notes: str = ""
) -> str:
    """
    Compares AI labels with human ground truth, categorizes errors,
    records in evidence_log, and updates analysis_results.
    """
    now = datetime.now(timezone.utc).isoformat()
    log_id = str(uuid.uuid4())

    with get_connection() as conn:
        ai_row = conn.execute(
            "SELECT * FROM analysis_results WHERE record_id = ?",
            (record_id,)
        ).fetchone()

        if not ai_row:
            raise ValueError(f"No analysis record found for record_id {record_id}")

        ai_rel = ai_row["ai_relevance"] or "unassigned"
        ai_themes_raw = ai_row["ai_themes"] or "[]"
        ai_evidence = ai_row["ai_evidence_excerpt"] or ""

        # Determine agreement
        rel_match = (ai_rel.lower() == human_relevance.lower())
        
        try:
            ai_themes_list = json.loads(ai_themes_raw)
            if not isinstance(ai_themes_list, list):
                ai_themes_list = []
        except Exception:
            ai_themes_list = []

        # Jaccard / set comparison
        ai_set = set(ai_themes_list)
        human_set = set(human_themes)
        theme_match = (ai_set == human_set)

        if rel_match and theme_match and error_category == "correct":
            agreement = "exact_match"
        elif rel_match:
            agreement = "partial_relevance_only"
        else:
            agreement = "disagree"

        # Auto-adjust error category if human marked disagree but category is correct
        if agreement == "disagree" and error_category == "correct":
            error_category = "wrong_relevance"

        final_label = f"Relevance: {human_relevance} | Themes: {', '.join(human_themes)}"

        # 1. Insert into evidence_log
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
                ai_themes_raw,
                json.dumps(human_themes),
                ai_evidence,
                human_evidence,
                agreement,
                error_category,
                "Human correction applied" if agreement != "exact_match" else "Verified correct",
                final_label,
                reviewer_notes,
                now
            )
        )

        # 2. Update analysis_results table
        conn.execute(
            """
            UPDATE analysis_results
            SET 
                human_relevance = ?,
                human_themes = ?,
                human_evidence = ?,
                review_status = 'reviewed',
                reviewer_notes = ?,
                reviewed_at = ?
            WHERE record_id = ?
            """,
            (
                human_relevance,
                json.dumps(human_themes),
                human_evidence,
                reviewer_notes,
                now,
                record_id
            )
        )

    return log_id


def calculate_metrics() -> Dict[str, Any]:
    """
    Computes rigorous AI evaluation benchmark metrics from evidence_log:
    - total_evaluated
    - exact_agreement_rate
    - relevance_agreement_rate
    - error_distribution
    - per_theme_metrics (with guard: requires >= 5 examples, else marks insufficient data)
    - data_sufficiency_warning (flags if total < 10)
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT 
                l.*,
                r.text
            FROM evidence_log l
            LEFT JOIN records r ON l.record_id = r.record_id
            ORDER BY l.reviewed_at DESC
            """
        ).fetchall()

    logs = [dict(r) for r in rows]
    total = len(logs)

    if total == 0:
        return {
            "total_evaluated": 0,
            "data_sufficiency_warning": True,
            "warning_message": "No human evaluations recorded yet. Review benchmark records to generate metrics.",
            "exact_agreement_rate": 0.0,
            "relevance_agreement_rate": 0.0,
            "error_distribution": {},
            "corrections_count": 0,
            "hallucination_rate": 0.0,
            "per_theme_metrics": {},
            "logs": []
        }

    exact_matches = sum(1 for l in logs if l["agreement"] == "exact_match")
    rel_matches = sum(1 for l in logs if (l["ai_relevance"] or "").lower() == (l["human_relevance"] or "").lower())
    
    error_counts: Dict[str, int] = {cat: 0 for cat in ERROR_CATEGORIES}
    for l in logs:
        cat = l["error_category"] or "other"
        error_counts[cat] = error_counts.get(cat, 0) + 1

    corrections_cnt = sum(1 for l in logs if l["agreement"] != "exact_match")
    hallucinations = error_counts.get("hallucination", 0)

    # Per-Theme Precision, Recall, F1
    theme_stats: Dict[str, Dict[str, int]] = {}
    
    for l in logs:
        try:
            ai_t = set(json.loads(l["ai_themes"] or "[]"))
        except Exception:
            ai_t = set()
        try:
            hu_t = set(json.loads(l["human_themes"] or "[]"))
        except Exception:
            hu_t = set()

        all_t = ai_t.union(hu_t)
        for t in all_t:
            if t not in theme_stats:
                theme_stats[t] = {"tp": 0, "fp": 0, "fn": 0, "total_human": 0}
            
            in_ai = t in ai_t
            in_hu = t in hu_t

            if in_ai and in_hu:
                theme_stats[t]["tp"] += 1
            elif in_ai and not in_hu:
                theme_stats[t]["fp"] += 1
            elif in_hu and not in_ai:
                theme_stats[t]["fn"] += 1

            if in_hu:
                theme_stats[t]["total_human"] += 1

    per_theme_metrics = {}
    f1_scores = []

    for t, s in theme_stats.items():
        total_instances = s["tp"] + s["fn"]
        if total_instances < 5:
            per_theme_metrics[t] = {
                "instances": total_instances,
                "insufficient_data": True,
                "precision": None,
                "recall": None,
                "f1": None,
                "note": "Insufficient human ground truth (< 5 instances)"
            }
        else:
            tp, fp, fn = s["tp"], s["fp"], s["fn"]
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
            f1_scores.append(f1)
            per_theme_metrics[t] = {
                "instances": total_instances,
                "insufficient_data": False,
                "precision": round(prec, 2),
                "recall": round(rec, 2),
                "f1": round(f1, 2)
            }

    macro_f1 = round(sum(f1_scores) / len(f1_scores), 2) if f1_scores else 0.0
    exact_rate = round((exact_matches / total) * 100, 1)
    rel_rate = round((rel_matches / total) * 100, 1)
    hallucination_rate = round((hallucinations / total) * 100, 1)

    return {
        "total_evaluated": total,
        "data_sufficiency_warning": total < 10,
        "warning_message": "Evaluation dataset too small for reliable metrics. Minimum recommended: 20 diverse examples." if total < 10 else None,
        "exact_agreement_rate": exact_rate,
        "relevance_agreement_rate": rel_rate,
        "macro_f1": macro_f1,
        "hallucination_rate": hallucination_rate,
        "error_distribution": error_counts,
        "corrections_count": corrections_cnt,
        "per_theme_metrics": per_theme_metrics,
        "logs": logs
    }


def export_evidence_log_csv() -> str:
    """Exports full AI Evidence Log as a CSV string."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT 
                l.log_id,
                l.record_id,
                r.source,
                r.record_type,
                r.text,
                l.ai_relevance,
                l.human_relevance,
                l.ai_themes,
                l.human_themes,
                l.ai_evidence,
                l.human_evidence,
                l.agreement,
                l.error_category,
                l.correction,
                l.final_label,
                l.reviewer_notes,
                l.reviewed_at
            FROM evidence_log l
            LEFT JOIN records r ON l.record_id = r.record_id
            ORDER BY l.reviewed_at DESC
            """
        ).fetchall()

    output = io.StringIO()
    if not rows:
        return "log_id,record_id,status\nNo evaluation logs found."

    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    for r in rows:
        writer.writerow(dict(r))

    return output.getvalue()
