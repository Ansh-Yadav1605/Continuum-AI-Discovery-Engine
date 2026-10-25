"""
tests/test_evaluation.py — Unit tests for AI Evidence Log & Benchmark (Milestone 2.3).
"""

import unittest
import uuid
import json
from datetime import datetime, timezone
from core.database import init_db, get_connection
from core.evaluation import (
    create_evaluation_entry,
    calculate_metrics,
    export_evidence_log_csv,
    get_benchmark_candidates
)


class TestEvaluation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.rec_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO records (record_id, source, record_type, text, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self.rec_id, "Trustpilot", "public_review", "My funds deducted twice and SIP was paused.", now)
            )
            conn.execute(
                """
                INSERT INTO analysis_results (
                    analysis_id, record_id, ai_relevance, ai_themes,
                    ai_evidence_excerpt, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    self.rec_id,
                    "directly_relevant",
                    json.dumps(["Payment and mandate friction"]),
                    "funds deducted twice and SIP was paused",
                    now
                )
            )

    def test_create_evaluation_entry_exact_match(self):
        log_id = create_evaluation_entry(
            record_id=self.rec_id,
            human_relevance="directly_relevant",
            human_themes=["Payment and mandate friction"],
            human_evidence="funds deducted twice and SIP was paused",
            error_category="correct",
            reviewer_notes="Accurate AI extraction"
        )
        self.assertIsNotNone(log_id)

        with get_connection() as conn:
            log_row = conn.execute("SELECT * FROM evidence_log WHERE log_id = ?", (log_id,)).fetchone()
            self.assertIsNotNone(log_row)
            self.assertEqual(log_row["agreement"], "exact_match")
            self.assertEqual(log_row["error_category"], "correct")

            # Check analysis_results updated
            res_row = conn.execute("SELECT * FROM analysis_results WHERE record_id = ?", (self.rec_id,)).fetchone()
            self.assertEqual(res_row["review_status"], "reviewed")

    def test_metrics_calculation_and_guards(self):
        metrics = calculate_metrics()
        self.assertGreaterEqual(metrics["total_evaluated"], 1)
        self.assertIn("exact_agreement_rate", metrics)
        self.assertIn("macro_f1", metrics)

        # Check data sufficiency warning triggers when < 10 records evaluated
        if metrics["total_evaluated"] < 10:
            self.assertTrue(metrics["data_sufficiency_warning"])

    def test_csv_export(self):
        create_evaluation_entry(
            record_id=self.rec_id,
            human_relevance="directly_relevant",
            human_themes=["Payment and mandate friction"],
            human_evidence="funds deducted twice",
            error_category="correct",
            reviewer_notes="Export test"
        )
        csv_str = export_evidence_log_csv()
        self.assertIn("log_id", csv_str)
        self.assertIn(self.rec_id, csv_str)

    def tearDown(self):
        with get_connection() as conn:
            conn.execute("DELETE FROM evidence_log WHERE record_id = ?", (self.rec_id,))
            conn.execute("DELETE FROM analysis_results WHERE record_id = ?", (self.rec_id,))
            conn.execute("DELETE FROM records WHERE record_id = ?", (self.rec_id,))


if __name__ == "__main__":
    unittest.main()
