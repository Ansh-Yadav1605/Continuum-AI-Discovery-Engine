"""
core/themes.py — Theme aggregation, frequency analysis, and taxonomy helpers.

Supports Milestone 2.1:
- get_theme_summary(): per-theme metrics, distinct sources & respondents, record types, top evidence excerpts, contradictory counts
- get_theme_records(theme_name): retrieves all matching records with both AI and human labels
- get_contradictory_evidence(theme_name): separates supporting vs contradictory signals (e.g. continuation vs stopping)
- get_theme_open_questions(theme_name) & save_theme_open_question(theme_name, question): manages exploratory questions per theme
"""

import json
from typing import List, Dict, Any, Optional
from core.database import get_connection, PROVISIONAL_TAXONOMY


def get_all_taxonomy_definitions() -> Dict[str, str]:
    """Return dictionary of theme_name -> theme_definition from DB or PROVISIONAL_TAXONOMY."""
    taxonomy_map = {name: desc for name, desc in PROVISIONAL_TAXONOMY}
    try:
        with get_connection() as conn:
            rows = conn.execute("SELECT theme_name, theme_definition FROM themes WHERE is_active = 1").fetchall()
            for r in rows:
                taxonomy_map[r["theme_name"]] = r["theme_definition"] or taxonomy_map.get(r["theme_name"], "")
    except Exception:
        pass
    return taxonomy_map


def get_theme_distribution() -> List[Dict[str, Any]]:
    """
    Compute aggregate theme frequencies across both AI-tagged and human-tagged results.
    Returns list of dicts: [{"theme": str, "count": int}, ...]
    """
    theme_counts: Dict[str, int] = {}
    
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT a.ai_themes, a.human_themes 
            FROM analysis_results a
            INNER JOIN records r ON a.record_id = r.record_id
            WHERE COALESCE(r.is_quarantined, 0) = 0 
              AND (a.review_status != 'invalidated' OR a.review_status IS NULL)
            """
        ).fetchall()

        for row in rows:
            themes_raw = row["human_themes"] if row["human_themes"] and row["human_themes"] != "[]" else row["ai_themes"]
            if themes_raw:
                try:
                    theme_list = json.loads(themes_raw)
                    if isinstance(theme_list, list):
                        for t in theme_list:
                            theme_counts[t] = theme_counts.get(t, 0) + 1
                except Exception:
                    continue

    sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"theme": k, "count": v} for k, v in sorted_themes]


def get_relevance_distribution() -> Dict[str, int]:
    """
    Compute distribution of relevance ratings across analysis results.
    Returns dict: {'directly_relevant': count, ...}
    """
    counts = {
        "directly_relevant": 0,
        "indirectly_relevant": 0,
        "not_relevant": 0,
        "ambiguous": 0
    }
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT 
                COALESCE(a.human_relevance, a.ai_relevance, 'unassigned') AS rel,
                COUNT(*) as cnt
            FROM analysis_results a
            INNER JOIN records r ON a.record_id = r.record_id
            WHERE COALESCE(r.is_quarantined, 0) = 0
              AND (a.review_status != 'invalidated' OR a.review_status IS NULL)
            GROUP BY rel
            """
        ).fetchall()

        for r in rows:
            rel = r["rel"]
            if rel in counts:
                counts[rel] = r["cnt"]
            elif rel != "unassigned":
                counts[rel] = r["cnt"]

    return counts


def get_source_coverage() -> List[Dict[str, Any]]:
    """Retrieve source register entries with counts and dates."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT source_id, source_name, collection_method, date_collected,
                   record_count, known_limitations, permission_notes
            FROM source_register
            ORDER BY date_collected DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]


def get_theme_summary() -> List[Dict[str, Any]]:
    """
    Detailed aggregation per theme for Milestone 2.1:
    - theme: Theme name
    - definition: Taxonomy definition
    - record_count: Total associated records
    - distinct_sources: Count of unique sources (e.g. Play Store, Reddit, Survey)
    - distinct_respondents: Count of unique respondents/users where known
    - record_types: Breakdown dict {'public_review': X, 'survey_response': Y, 'interview_note': Z}
    - top_excerpts: Up to 3 representative evidence quotes
    - contradictory_count: Count of records indicating contrasting/continuation vs stopping signals
    - missing_contexts: Set/List of common unknowns or missing context
    """
    taxonomy_map = get_all_taxonomy_definitions()
    
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT 
                r.record_id,
                r.source,
                r.record_type,
                r.respondent_id,
                r.text,
                a.ai_themes,
                a.human_themes,
                a.ai_evidence_excerpt,
                a.human_evidence,
                a.ai_continuation_mention,
                a.ai_missing_context,
                a.ai_relevance,
                a.human_relevance
            FROM records r
            INNER JOIN analysis_results a ON r.record_id = a.record_id
            WHERE COALESCE(r.is_quarantined, 0) = 0
              AND (a.review_status != 'invalidated' OR a.review_status IS NULL)
            """
        ).fetchall()

    theme_data: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        themes_raw = row["human_themes"] if row["human_themes"] and row["human_themes"] != "[]" else row["ai_themes"]
        if not themes_raw:
            continue
        try:
            t_list = json.loads(themes_raw)
            if not isinstance(t_list, list):
                continue
        except Exception:
            continue

        excerpt = row["human_evidence"] or row["ai_evidence_excerpt"] or (row["text"][:140] + "..." if len(row["text"]) > 140 else row["text"])
        source_name = row["source"] or "Unknown"
        resp_id = row["respondent_id"] or row["record_id"]
        rtype = row["record_type"] or "public_review"
        cont_mention = (row["ai_continuation_mention"] or "").lower()
        missing_ctx = row["ai_missing_context"]

        for t in t_list:
            if t not in theme_data:
                theme_data[t] = {
                    "theme": t,
                    "definition": taxonomy_map.get(t, "Defined theme in provisional taxonomy."),
                    "records": [],
                    "sources": set(),
                    "respondents": set(),
                    "record_types": {"public_review": 0, "survey_response": 0, "interview_note": 0, "browser_collected": 0, "other": 0},
                    "excerpts": [],
                    "stopping_count": 0,
                    "continuing_count": 0,
                    "missing_contexts": []
                }

            td = theme_data[t]
            td["records"].append(row["record_id"])
            td["sources"].add(source_name)
            td["respondents"].add(resp_id)
            
            if rtype in td["record_types"]:
                td["record_types"][rtype] += 1
            else:
                td["record_types"]["other"] += 1

            if excerpt and len(td["excerpts"]) < 3 and excerpt not in td["excerpts"]:
                td["excerpts"].append(excerpt)

            if "stop" in cont_mention or "pause" in cont_mention or "cancel" in cont_mention:
                td["stopping_count"] += 1
            elif "continu" in cont_mention or "active" in cont_mention or "kept" in cont_mention:
                td["continuing_count"] += 1

            if missing_ctx and missing_ctx.lower() not in ["none", "n/a", "not specified", "null"]:
                if missing_ctx not in td["missing_contexts"] and len(td["missing_contexts"]) < 5:
                    td["missing_contexts"].append(missing_ctx)

    summaries = []
    # Include all themes that either have records or are in taxonomy
    for t, td in theme_data.items():
        contradictory = min(td["stopping_count"], td["continuing_count"])
        summaries.append({
            "theme": t,
            "definition": td["definition"],
            "record_count": len(td["records"]),
            "distinct_sources": len(td["sources"]),
            "distinct_respondents": len(td["respondents"]),
            "record_types": td["record_types"],
            "top_excerpts": td["excerpts"],
            "stopping_count": td["stopping_count"],
            "continuing_count": td["continuing_count"],
            "contradictory_count": contradictory,
            "missing_contexts": td["missing_contexts"]
        })

    # Add themes from taxonomy with 0 records if not yet observed
    existing_themes = {s["theme"] for s in summaries}
    for t_name, t_def in taxonomy_map.items():
        if t_name not in existing_themes:
            summaries.append({
                "theme": t_name,
                "definition": t_def,
                "record_count": 0,
                "distinct_sources": 0,
                "distinct_respondents": 0,
                "record_types": {"public_review": 0, "survey_response": 0, "interview_note": 0, "browser_collected": 0, "other": 0},
                "top_excerpts": [],
                "stopping_count": 0,
                "continuing_count": 0,
                "contradictory_count": 0,
                "missing_contexts": []
            })

    # Sort descending by record count, then alphabetical
    summaries.sort(key=lambda x: (x["record_count"], x["theme"]), reverse=True)
    return summaries


def get_theme_records(theme_name: str) -> List[Dict[str, Any]]:
    """Retrieve all unified records associated with a specific theme."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT 
                r.record_id,
                r.source,
                r.record_type,
                r.text,
                r.text_edited,
                r.source_url,
                r.publication_date,
                r.rating,
                r.respondent_id,
                a.ai_relevance,
                a.ai_themes,
                a.ai_evidence_excerpt,
                a.ai_behaviour,
                a.ai_user_need,
                a.ai_workaround,
                a.ai_journey_stage,
                a.ai_continuation_mention,
                a.ai_missing_context,
                a.ai_explanation,
                a.human_relevance,
                a.human_themes,
                a.human_evidence,
                a.review_status,
                a.reviewer_notes
            FROM records r
            INNER JOIN analysis_results a ON r.record_id = a.record_id
            WHERE COALESCE(r.is_quarantined, 0) = 0
              AND (a.review_status != 'invalidated' OR a.review_status IS NULL)
            ORDER BY r.publication_date DESC, r.created_at DESC
            """
        ).fetchall()

    matching = []
    for r in rows:
        themes_raw = r["human_themes"] if r["human_themes"] and r["human_themes"] != "[]" else r["ai_themes"]
        if not themes_raw:
            continue
        try:
            t_list = json.loads(themes_raw)
            if isinstance(t_list, list) and theme_name in t_list:
                matching.append(dict(r))
        except Exception:
            continue

    return matching


def get_contradictory_evidence(theme_name: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Partition evidence for a theme into:
    - 'stopping_or_friction': records showing dropped SIPs, failures, confusion, hesitation
    - 'continuing_or_positive': records showing continued SIPs, satisfaction, persistence
    - 'unclear_or_neutral': other records
    """
    records = get_theme_records(theme_name)
    partition = {
        "stopping_or_friction": [],
        "continuing_or_positive": [],
        "unclear_or_neutral": []
    }

    for rec in records:
        cont = (rec.get("ai_continuation_mention") or "").lower()
        rating = rec.get("rating")
        text = (rec.get("text") or "").lower()

        is_stopping = "stop" in cont or "pause" in cont or "cancel" in cont or (rating and rating <= 2) or "stopped" in text or "quit" in text
        is_continuing = "continu" in cont or "active" in cont or "kept" in cont or (rating and rating >= 4) or "still investing" in text

        if is_stopping and not is_continuing:
            partition["stopping_or_friction"].append(rec)
        elif is_continuing and not is_stopping:
            partition["continuing_or_positive"].append(rec)
        else:
            partition["unclear_or_neutral"].append(rec)

    return partition


def get_theme_open_questions(theme_name: str) -> List[str]:
    """Retrieve saved open questions for a given theme from settings table."""
    key = f"theme_questions_{theme_name}"
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if row and row["value"]:
            try:
                questions = json.loads(row["value"])
                if isinstance(questions, list):
                    return questions
            except Exception:
                pass
    return []


def save_theme_open_question(theme_name: str, question_text: str) -> bool:
    """Add an open question to the theme's list of research questions."""
    if not question_text or not question_text.strip():
        return False
    question_text = question_text.strip()
    questions = get_theme_open_questions(theme_name)
    if question_text not in questions:
        questions.append(question_text)
        key = f"theme_questions_{theme_name}"
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO settings (key, value, updated_at) 
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                (key, json.dumps(questions))
            )
    return True
