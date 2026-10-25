"""
tests/test_ingestion.py — Acceptance and unit tests for CSV ingestion, validation, and deduplication.
"""

import os
import unittest
import pandas as pd
from core.database import init_db, get_connection
from core.ingestion import import_csv, compute_text_hash, check_near_duplicate
from core.survey_ingestion import import_survey_csv

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


class TestIngestion(unittest.TestCase):
    def setUp(self):
        init_db()
        with get_connection() as conn:
            conn.execute("DELETE FROM records WHERE source LIKE 'Test%'")
            conn.execute("DELETE FROM source_register WHERE source_name LIKE 'Test%'")

    def test_text_hashing(self):
        """Verify normalized hashing produces consistent SHA-256 digests."""
        h1 = compute_text_hash("Great mutual fund app   ")
        h2 = compute_text_hash("great   mutual  fund APP")
        self.assertEqual(h1, h2)

    def test_near_duplicate_detection(self):
        """Verify SequenceMatcher flags similar strings with minor variations."""
        t1 = "My bank mandate auto-debit failed on 5th March, and my bank charged 295 rupees ECS bounce penalty."
        t2 = "My bank mandate auto-debit failed on 5th March and my bank charged 295 Rs ECS penalty."
        is_near, ratio, match = check_near_duplicate(t2, [t1], threshold=0.85)
        self.assertTrue(is_near)
        self.assertGreater(ratio, 0.85)

    def test_csv_acceptance_test(self):
        """
        Acceptance test per implementation-plan.md Milestone 1.2:
        - Upload a CSV with 10+ rows, 2 exact duplicates, 1 empty-text row
        - Verify records imported, exact duplicates skipped, empty text rejected
        """
        csv_path = os.path.join(FIXTURES_DIR, "sample_reviews.csv")
        self.assertTrue(os.path.exists(csv_path), "Fixture sample_reviews.csv missing")

        summary = import_csv(
            file_or_path=csv_path,
            column_mapping={
                "text": "Review_Text",
                "rating": "Rating",
                "publication_date": "Review_Date",
                "source_url": "URL"
            },
            source_name="Test Play Store Batch",
            record_type="public_review"
        )

        self.assertGreaterEqual(summary["total"], 10, "Total rows in fixture should be at least 10")
        self.assertGreaterEqual(summary["imported"], 7, "Should import at least 7 unique records")
        self.assertGreaterEqual(summary["exact_duplicates"], 1, "Should detect at least 1 exact duplicate")
        self.assertGreaterEqual(summary["near_duplicates"], 1, "Should flag near duplicate")
        self.assertGreaterEqual(summary["rejected"], 1, "Should reject empty whitespace-only row")

        # Verify records exist in database
        with get_connection() as conn:
            row_count = conn.execute("SELECT COUNT(*) FROM records WHERE source = 'Test Play Store Batch'").fetchone()[0]
            self.assertEqual(row_count, summary["imported"])

    def test_survey_ingestion(self):
        """Verify Google Forms survey ingestion creates survey_response records with context headers."""
        survey_path = os.path.join(FIXTURES_DIR, "sample_survey.csv")
        self.assertTrue(os.path.exists(survey_path), "Fixture sample_survey.csv missing")

        summary = import_survey_csv(
            file_or_path=survey_path,
            open_text_col="Detailed_Experience_Feedback",
            respondent_id_col="Respondent_Email",
            context_cols=[
                ("SIP_Continuation_Status", "Status"),
                ("Primary_Dropoff_Reasons", "Reasons")
            ],
            source_name="Test Survey Batch"
        )

        self.assertGreaterEqual(summary["imported"], 5)
        
        with get_connection() as conn:
            rec = conn.execute(
                "SELECT * FROM records WHERE source = 'Test Survey Batch' LIMIT 1"
            ).fetchone()
            self.assertIsNotNone(rec)
            self.assertEqual(rec["record_type"], "survey_response")
            self.assertEqual(rec["collection_method"], "google_forms_csv")
            self.assertIn("[Status:", rec["text"])


if __name__ == "__main__":
    unittest.main()
