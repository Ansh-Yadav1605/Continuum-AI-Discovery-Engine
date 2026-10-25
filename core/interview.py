"""
core/interview.py — Evidence gap detection, neutral interview guide generation, and interview note logging.

Supports Milestone 2.4:
- get_evidence_gaps(): identifies themes with sparse data (< 3 records), high contradictions, or missing context.
- generate_interview_questions(): generates neutral, non-leading discovery interview questions covering 10 key research areas.
- add_interview_note(): records primary user interview notes with record_type='interview_note' and collection_method='user_interview'.
"""

import uuid
import json
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import get_connection
from core.groq_client import get_client, get_model_name, get_api_key
from core.themes import get_theme_summary, get_contradictory_evidence
from core.problems import get_all_problems

# 10 core research guide areas for first-time SIP discovery
CORE_INTERVIEW_AREAS = [
    "Initial Motivation (Why start first SIP?)",
    "Pre-Investment Expectations (Returns, timelines, deductions)",
    "First Deduction Experience (Actual reality vs expectations)",
    "Behavioral Triggers (Moments of hesitation, volatility shock)",
    "Information Sources (Where did they seek clarity when stuck?)",
    "Mental Model & Understanding (Compounding, fund mechanics, pauses)",
    "Friction Points (e-mandates, bank limits, deduction failures)",
    "Resolution Attempts (Groww support, friends, YouTube, Reddit)",
    "Continuation Catalysts (What helped or motivated staying invested?)",
    "Workarounds (Manual payments, stopping SIP, withdrawing funds)"
]

LEADING_WORDS_PATTERN = re.compile(r"\b(obviously|frustrated with groww|bad app|confusing ui|ruined|terrible)\b", re.IGNORECASE)


def get_evidence_gaps() -> Dict[str, Any]:
    """
    Scans theme analysis and candidate problem statements to pinpoint:
    - sparse_themes: Themes with < 3 records.
    - contradictory_themes: Themes with active opposing signals (stopping vs continuing).
    - missing_context_areas: Frequently cited missing information in AI logs.
    - unvalidated_hypotheses: Problem statements currently marked as 'needs_research' or 'requires_validation'.
    """
    summaries = get_theme_summary()
    sparse = [s["theme"] for s in summaries if 0 < s["record_count"] < 3]
    contradictory = [s["theme"] for s in summaries if s["contradictory_count"] > 0]
    
    missing_ctx = set()
    for s in summaries:
        for m in s.get("missing_contexts", []):
            if m:
                missing_ctx.add(m)

    problems = get_all_problems()
    unvalidated = [p["title"] for p in problems if p.get("validation_status") in ("needs_research", "requires_validation")]

    return {
        "sparse_themes": sparse,
        "contradictory_themes": contradictory,
        "missing_context_areas": list(missing_ctx)[:5],
        "unvalidated_problems": unvalidated
    }


def generate_interview_questions(
    theme_name: Optional[str] = None,
    problem_title: Optional[str] = None,
    use_ai: bool = False
) -> List[Dict[str, str]]:
    """
    Generates neutral, open-ended interview questions for target user interviews.
    Ensures zero leading questions and covers key discovery objectives.
    Default (use_ai=False) uses instant curated discovery questions.
    Set use_ai=True to formulate dynamic questions via Groq API.
    """
    if use_ai:
        api_key = get_api_key()
        client = get_client() if api_key and api_key != "your_key_here" else None

        context_str = f"Theme: {theme_name or 'General First-Time SIP Continuation'}"
        if problem_title:
            context_str += f" | Problem Context: {problem_title}"

        if client:
            try:
                model = get_model_name()
                prompt = f"""
You are a Senior User Researcher conducting discovery interviews with first-time mutual fund investors on Groww.
Context: {context_str}

Generate 5 neutral, open-ended interview questions to investigate why first-time investors continue or discontinue SIPs within 12 months.
STRICT RULES:
1. Do NOT ask leading questions (e.g. Do not ask 'Was the UI confusing?').
2. Ask about actual behaviors, specific past incidents, and expectations vs reality.
3. Return ONLY a valid JSON list of objects:
[
  {{
    "area": "One of: Initial Motivation, Expectations vs Reality, Friction Points, Information Sources, Continuation Triggers",
    "question": "Neutral open-ended question",
    "rationale": "Why this question tests the hypothesis without bias"
  }}
]
"""
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                raw = response.choices[0].message.content.strip()
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    for v in parsed.values():
                        if isinstance(v, list):
                            parsed = v
                            break
                if isinstance(parsed, list):
                    # Filter out any accidentally leading questions
                    clean_q = []
                    for item in parsed:
                        q_text = item.get("question", "")
                        if not LEADING_WORDS_PATTERN.search(q_text):
                            clean_q.append(item)
                    if clean_q:
                        return clean_q
            except Exception:
                pass

    # High-quality neutral curated fallback questions
    return [
        {
            "area": "Initial Motivation",
            "question": "Thinking back to when you started your very first SIP on Groww, what prompted you to start that specific week or month?",
            "rationale": "Uncovers real-world catalysts (salary hike, peer influence, ad) without assuming motivation."
        },
        {
            "area": "Expectations vs Reality",
            "question": "What did you expect would happen during your first 3 to 6 months of investing, and how did that compare with what you actually saw?",
            "rationale": "Captures volatility shocks or process surprises through the user's own narrative."
        },
        {
            "area": "Friction Points",
            "question": "Can you walk me through the deduction process when your monthly instalment is due? Have you ever had to intervene or check why a payment didn't process?",
            "rationale": "Tests mandate/UPI/bank limit issues through concrete behavioral walkthroughs."
        },
        {
            "area": "Information Sources",
            "question": "When you have questions about how your SIP is performing or how deductions work, where do you typically look for answers?",
            "rationale": "Identifies internal vs external reliance (in-app FAQs vs Reddit vs friends)."
        },
        {
            "area": "Continuation Triggers",
            "question": "Have you ever considered pausing, stopping, or withdrawing from your SIP? If so, what was happening around that time?",
            "rationale": "Identifies life events, liquidity constraints, or sentiment triggers without judgment."
        }
    ]


def add_interview_note(
    text: str,
    respondent_id: str = "",
    source_url: str = "",
    notes_date: Optional[str] = None
) -> str:
    """
    Saves qualitative primary interview notes directly into the unified records table.
    Record is tagged with record_type='interview_note' and collection_method='user_interview'.
    """
    record_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    pub_date = notes_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    clean_text = text.strip()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO records (
                record_id, source, record_type, text, source_url,
                publication_date, collection_date, collection_method,
                respondent_id, duplicate_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'unique', ?)
            """,
            (
                record_id,
                "Primary User Interview",
                "interview_note",
                clean_text,
                source_url or "internal://interview",
                pub_date,
                pub_date,
                "user_interview",
                respondent_id or f"interviewee_{str(uuid.uuid4())[:6]}",
                now
            )
        )
    return record_id
