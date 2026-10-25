"""
core/scoring.py — 6-factor weighted opportunity scorecard & safety filter.

Weights:
- evidence_strength: 0.25
- sip_relevance: 0.25
- user_severity: 0.15
- product_influence: 0.15
- feasibility: 0.10
- safety_compliance: 0.10 (Hard filter: score <= 2 blocks candidate from ranking)
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from core.database import get_connection

FACTOR_WEIGHTS = {
    "evidence_strength": 0.25,
    "sip_relevance": 0.25,
    "user_severity": 0.15,
    "product_influence": 0.15,
    "feasibility": 0.10,
    "safety_compliance": 0.10
}

FACTOR_DESCRIPTIONS = {
    "evidence_strength": "Grounded in multiple independent, traceable records across diverse sources (1 = weak single anecdote, 5 = robust triangulation).",
    "sip_relevance": "Direct connection to 12-month active SIP continuation rather than generic onboarding complaints.",
    "user_severity": "Emotional frustration, financial uncertainty, or acute barrier experienced by the investor.",
    "product_influence": "Degree to which Groww product/UX can directly address or alleviate this root cause.",
    "feasibility": "Realistic to research, validate, and design interventions within project scope.",
    "safety_compliance": "HARD FILTER: Strictly non-advisory, no stock/fund tips, no FOMO, no dark patterns (<= 2 is blocked)."
}


def calculate_score(scores: Dict[str, Optional[int]]) -> Tuple[float, bool]:
    """
    Compute normalized weighted score across provided factors.
    Returns: (weighted_score, safety_blocked)
    - safety_blocked: True if safety_compliance is <= 2
    """
    safety_val = scores.get("safety_compliance")
    safety_blocked = safety_val is not None and safety_val <= 2

    total_weight = 0.0
    weighted_sum = 0.0

    for factor, weight in FACTOR_WEIGHTS.items():
        val = scores.get(factor)
        if val is not None and 1 <= val <= 5:
            weighted_sum += val * weight
            total_weight += weight

    if total_weight == 0:
        return 0.0, safety_blocked

    # Normalize score on a 1.0 to 5.0 scale
    normalized_score = round(weighted_sum / total_weight, 2)
    return normalized_score, safety_blocked


def save_score(
    problem_id: str,
    scores_dict: Dict[str, int],
    justification: str = "",
    scored_by: str = "human_pm"
) -> str:
    """Save or update score evaluation for a candidate problem statement."""
    weighted, blocked = calculate_score(scores_dict)
    score_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO scores (
                score_id, problem_id, evidence_strength, sip_relevance,
                user_severity, product_influence, feasibility,
                safety_compliance, weighted_score, justification,
                scored_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                score_id,
                problem_id,
                scores_dict.get("evidence_strength"),
                scores_dict.get("sip_relevance"),
                scores_dict.get("user_severity"),
                scores_dict.get("product_influence"),
                scores_dict.get("feasibility"),
                scores_dict.get("safety_compliance"),
                weighted,
                justification,
                scored_by,
                now
            )
        )
    return score_id


def get_scorecard(problem_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve the most recent score for a specific problem statement."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM scores
            WHERE problem_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (problem_id,)
        ).fetchone()
        return dict(row) if row else None


def get_ranked_problems() -> List[Dict[str, Any]]:
    """
    Retrieve all problem statements joined with their latest score.
    Returns sorted list, with safety_blocked items flagged.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT 
                p.problem_id,
                p.title,
                p.user_segment,
                p.journey_stage,
                p.validation_status,
                p.is_ai_generated,
                s.evidence_strength,
                s.sip_relevance,
                s.user_severity,
                s.product_influence,
                s.feasibility,
                s.safety_compliance,
                s.weighted_score,
                s.justification
            FROM problem_statements p
            LEFT JOIN (
                SELECT s1.* FROM scores s1
                INNER JOIN (
                    SELECT problem_id, MAX(created_at) as max_c
                    FROM scores GROUP BY problem_id
                ) s2 ON s1.problem_id = s2.problem_id AND s1.created_at = s2.max_c
            ) s ON p.problem_id = s.problem_id
            """
        ).fetchall()

    results = []
    for r in rows:
        d = dict(r)
        sc = d.get("safety_compliance")
        d["safety_blocked"] = sc is not None and sc <= 2
        d["has_score"] = d.get("weighted_score") is not None
        results.append(d)

    # Sort: unblocked items with scores descending, then unranked items, then blocked items
    def sort_key(item):
        if item["safety_blocked"]:
            return (-1, 0)
        if item["has_score"]:
            return (1, item["weighted_score"])
        return (0, 0)

    results.sort(key=sort_key, reverse=True)
    return results
