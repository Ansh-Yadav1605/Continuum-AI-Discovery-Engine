"""
core/problems.py — Candidate problem statement generation, lifecycle, and management.

Supports Milestone 2.2:
- Structured problem cards separating Observation, Interpretation, and Hypothesis.
- Validation status management (needs_research, supported, challenged, requires_validation).
- AI generation via Groq with structured JSON parsing and robust offline manual template fallback.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import get_connection
from core.groq_client import get_client, get_model_name, get_api_key
from core.themes import get_theme_records, get_contradictory_evidence

VALIDATION_STATUSES = [
    "needs_research",
    "supported",
    "challenged",
    "requires_validation"
]

PROBLEM_SCHEMA_PROMPT = """
You are an expert Product Discovery & AI Research Partner investigating why first-time mutual fund investors stop their SIPs within 12 months on Groww.

Generate 1-2 structured Candidate Problem Statements for the following research theme based on the provided evidence excerpts:
Theme: {theme_name}
Evidence Excerpts:
{evidence_text}

Rules:
1. Strictly separate Observation (what the data factually says), Interpretation (what it suggests about investor psychology/context), and Hypothesis (a testable proposition to validate).
2. Never assume drop-offs are simply due to "lack of financial literacy" or "market drops".
3. Return ONLY a valid JSON array of objects adhering strictly to this schema:
[
  {
    "title": "Short descriptive title (max 10 words)",
    "user_segment": "e.g. First-time salaried investors aged 22-28 using UPI AutoPay",
    "journey_stage": "e.g. Month 1-3 or Initial deduction",
    "observation": "Factual summary of quotes and data observed",
    "interpretation": "What this implies about user mental model or friction",
    "hypothesis": "Testable hypothesis regarding why this causes drop-off",
    "supporting_evidence": "Key supporting quote or data point",
    "contradictory_evidence": "Any contrary or nuance quote (or 'None observed yet')",
    "user_need": "Core underlying unmet need",
    "workaround": "What users do instead (e.g. manual payments, cancelling SIP)",
    "consequence": "Business & user impact if unresolved",
    "sip_relationship": "Direct or indirect link to 12-month retention",
    "alternative_explanations": "Alternative reasons for the same behavior",
    "limitations": "Known data limitations or sampling biases",
    "open_questions": "Key open question to investigate",
    "interview_questions": "Neutral, open-ended question for user interviews"
  }
]
"""


def get_all_problems() -> List[Dict[str, Any]]:
    """Fetch all candidate problem statements with their latest score info."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT 
                p.*,
                s.weighted_score,
                s.safety_compliance,
                s.evidence_strength,
                s.sip_relevance,
                s.user_severity,
                s.product_influence,
                s.feasibility,
                s.justification AS score_justification
            FROM problem_statements p
            LEFT JOIN (
                SELECT s1.* FROM scores s1
                INNER JOIN (
                    SELECT problem_id, MAX(created_at) as max_created
                    FROM scores GROUP BY problem_id
                ) s2 ON s1.problem_id = s2.problem_id AND s1.created_at = s2.max_created
            ) s ON p.problem_id = s.problem_id
            ORDER BY COALESCE(s.weighted_score, 0) DESC, p.created_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]


def get_problem(problem_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single problem statement by ID."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM problem_statements WHERE problem_id = ?
            """,
            (problem_id,)
        ).fetchone()
        return dict(row) if row else None


def save_problem(p: Dict[str, Any]) -> str:
    """Save or update a candidate problem statement."""
    pid = p.get("problem_id") or str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO problem_statements (
                problem_id, title, user_segment, journey_stage, observation,
                interpretation, hypothesis, supporting_evidence, contradictory_evidence,
                user_need, workaround, consequence, sip_relationship,
                alternative_explanations, limitations, open_questions,
                interview_questions, validation_status, is_ai_generated,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(problem_id) DO UPDATE SET
                title = excluded.title,
                user_segment = excluded.user_segment,
                journey_stage = excluded.journey_stage,
                observation = excluded.observation,
                interpretation = excluded.interpretation,
                hypothesis = excluded.hypothesis,
                supporting_evidence = excluded.supporting_evidence,
                contradictory_evidence = excluded.contradictory_evidence,
                user_need = excluded.user_need,
                workaround = excluded.workaround,
                consequence = excluded.consequence,
                sip_relationship = excluded.sip_relationship,
                alternative_explanations = excluded.alternative_explanations,
                limitations = excluded.limitations,
                open_questions = excluded.open_questions,
                interview_questions = excluded.interview_questions,
                validation_status = excluded.validation_status,
                updated_at = excluded.updated_at
            """,
            (
                pid,
                p.get("title", "Untitled Problem"),
                p.get("user_segment", "First-time mutual fund investors"),
                p.get("journey_stage", "Months 1-3"),
                p.get("observation", ""),
                p.get("interpretation", ""),
                p.get("hypothesis", ""),
                p.get("supporting_evidence", ""),
                p.get("contradictory_evidence", ""),
                p.get("user_need", ""),
                p.get("workaround", ""),
                p.get("consequence", ""),
                p.get("sip_relationship", "Unknown direct correlation"),
                p.get("alternative_explanations", ""),
                p.get("limitations", "Public reviews do not establish 12-month retention causality."),
                p.get("open_questions", ""),
                p.get("interview_questions", ""),
                p.get("validation_status", "needs_research"),
                p.get("is_ai_generated", 0),
                p.get("created_at", now),
                now
            )
        )
    return pid


def update_validation_status(problem_id: str, status: str) -> bool:
    """Update human validation status (needs_research, supported, challenged, requires_validation)."""
    if status not in VALIDATION_STATUSES:
        return False
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE problem_statements 
            SET validation_status = ?, updated_at = ?
            WHERE problem_id = ?
            """,
            (status, now, problem_id)
        )
    return True


def delete_problem(problem_id: str) -> bool:
    """Delete a problem statement and associated scores."""
    with get_connection() as conn:
        conn.execute("DELETE FROM scores WHERE problem_id = ?", (problem_id,))
        conn.execute("DELETE FROM problem_statements WHERE problem_id = ?", (problem_id,))
    return True


def generate_problem_statements(theme_name: str) -> List[Dict[str, Any]]:
    """
    Generate candidate problem statements for a theme.
    Calls Groq if configured, else creates rich grounded candidate templates.
    """
    records = get_theme_records(theme_name)
    partition = get_contradictory_evidence(theme_name)
    
    excerpts = []
    for r in records[:6]:
        quote = r.get("human_evidence") or r.get("ai_evidence_excerpt") or r.get("text", "")[:180]
        excerpts.append(f"- {quote} (Source: {r.get('source')})")
    
    evidence_text = "\n".join(excerpts) if excerpts else "No direct quotes recorded yet."
    
    api_key = get_api_key()
    client = get_client() if api_key and api_key != "your_key_here" else None

    if client:
        try:
            model = get_model_name()
            prompt = PROBLEM_SCHEMA_PROMPT.format(theme_name=theme_name, evidence_text=evidence_text)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a specialized discovery assistant. Always output strict JSON array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content.strip()
            parsed = json.loads(raw)
            # Normalize if wrapped in a dict key like {"problems": [...]}
            if isinstance(parsed, dict):
                for val in parsed.values():
                    if isinstance(val, list):
                        parsed = val
                        break
            if isinstance(parsed, list):
                candidates = []
                for item in parsed:
                    item["is_ai_generated"] = 1
                    item["validation_status"] = "needs_research"
                    pid = save_problem(item)
                    item["problem_id"] = pid
                    candidates.append(item)
                return candidates
        except Exception:
            # Fall back to template-based generation below
            pass

    # Heuristic grounded fallback candidate
    sample_stopping = partition["stopping_or_friction"]
    sample_contra = partition["continuing_or_positive"]
    
    sup_quote = sample_stopping[0]["text"][:200] if sample_stopping else (records[0]["text"][:200] if records else "Uncertainty observed in exploratory reviews.")
    contra_quote = sample_contra[0]["text"][:200] if sample_contra else "No contradictory continuation signals recorded."

    candidate = {
        "title": f"Friction in {theme_name[:36]}",
        "user_segment": "First-time mutual fund investors (Months 1–6)",
        "journey_stage": "Early instalment and post-onboarding period",
        "observation": f"Multiple records in '{theme_name}' indicate hesitation or friction: {sup_quote}",
        "interpretation": "Users experience unexpected mental effort or system feedback gaps, eroding investment confidence.",
        "hypothesis": f"If users experience unresolved friction in {theme_name.lower()}, they are significantly more likely to stop SIPs before month 12.",
        "supporting_evidence": sup_quote,
        "contradictory_evidence": contra_quote,
        "user_need": "Clear, reassuring system feedback and predictable instalment execution.",
        "workaround": "Users pause SIP, cancel mandates, or switch to manual ad-hoc payments.",
        "consequence": "Permanent loss of compounding habit and customer churn from mutual fund category.",
        "sip_relationship": "Directly correlates with continuation decisions during the critical first 3-6 months.",
        "alternative_explanations": "Drop-offs could also stem from broader macroeconomic inflation or salary timing mismatches.",
        "limitations": "Observational evidence from reviews cannot prove 12-month causality without cohort transaction logs.",
        "open_questions": f"Does this friction peak after the 1st, 3rd, or 6th instalment?",
        "interview_questions": "Can you walk me through what happened the last time your SIP deduction was processed?",
        "validation_status": "needs_research",
        "is_ai_generated": 1 if client else 0
    }
    pid = save_problem(candidate)
    candidate["problem_id"] = pid
    return [candidate]
