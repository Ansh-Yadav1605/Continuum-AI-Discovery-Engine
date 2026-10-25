"""
tests/test_themes.py — Unit tests for Theme Analysis Engine (Milestone 2.1).
"""

import unittest
import uuid
import json
from datetime import datetime, timezone
from core.database import init_db, get_connection
from core.themes import (
    get_theme_summary,
    get_theme_records,
    get_contradictory_evidence,
    get_theme_open_questions,
    save_theme_open_question
)


class TestThemeAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        # Insert test records
        self.rec1_id = str(uuid.uuid4())
        self.rec2_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO records (record_id, source, record_type, text, respondent_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (self.rec1_id, "Play Store", "public_review", "My SIP stopped after first month due to mandate failure.", "resp_1", now)
            )
            conn.execute(
                """
                INSERT INTO records (record_id, source, record_type, text, respondent_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (self.rec2_id, "Primary Survey", "survey_response", "I have kept my SIP active for 8 months now, smooth experience.", "resp_2", now)
            )
            conn.execute(
                """
                INSERT INTO analysis_results (
                    analysis_id, record_id, ai_relevance, ai_themes,
                    ai_evidence_excerpt, ai_continuation_mention, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    self.rec1_id,
                    "directly_relevant",
                    json.dumps(["Payment and mandate friction"]),
                    "My SIP stopped after first month",
                    "stopped",
                    now
                )
            )
            conn.execute(
                """
                INSERT INTO analysis_results (
                    analysis_id, record_id, ai_relevance, ai_themes,
                    ai_evidence_excerpt, ai_continuation_mention, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    self.rec2_id,
                    "directly_relevant",
                    json.dumps(["Payment and mandate friction"]),
                    "kept my SIP active for 8 months",
                    "continuing",
                    now
                )
            )

    def test_theme_summary_aggregation(self):
        summaries = get_theme_summary()
        self.assertIsInstance(summaries, list)
        friction = next((s for s in summaries if s["theme"] == "Payment and mandate friction"), None)
        self.assertIsNotNone(friction)
        self.assertGreaterEqual(friction["record_count"], 2)
        self.assertGreaterEqual(friction["distinct_respondents"], 2)
        self.assertGreaterEqual(friction["contradictory_count"], 1)

    def test_get_theme_records(self):
        records = get_theme_records("Payment and mandate friction")
        r_ids = [r["record_id"] for r in records]
        self.assertIn(self.rec1_id, r_ids)
        self.assertIn(self.rec2_id, r_ids)

    def test_contradictory_evidence_partitioning(self):
        partition = get_contradictory_evidence("Payment and mandate friction")
        self.assertIn("stopping_or_friction", partition)
        self.assertIn("continuing_or_positive", partition)
        
        stop_ids = [r["record_id"] for r in partition["stopping_or_friction"]]
        cont_ids = [r["record_id"] for r in partition["continuing_or_positive"]]
        
        self.assertIn(self.rec1_id, stop_ids)
        self.assertIn(self.rec2_id, cont_ids)

    def test_open_questions_lifecycle(self):
        theme_name = "Payment and mandate friction"
        saved = save_theme_open_question(theme_name, "What is the primary bank failure code for auto-debit?")
        self.assertTrue(saved)
        questions = get_theme_open_questions(theme_name)
        self.assertIn("What is the primary bank failure code for auto-debit?", questions)

    def tearDown(self):
        with get_connection() as conn:
            conn.execute("DELETE FROM analysis_results WHERE record_id IN (?, ?)", (self.rec1_id, self.rec2_id))
            conn.execute("DELETE FROM records WHERE record_id IN (?, ?)", (self.rec1_id, self.rec2_id))


if __name__ == "__main__":
    unittest.main()
