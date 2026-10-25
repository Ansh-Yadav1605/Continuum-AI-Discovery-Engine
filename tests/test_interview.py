"""
tests/test_interview.py — Unit tests for Interview Question Generator and Interview Notes (Milestone 2.4).
"""

import unittest
from core.database import init_db, get_connection
from core.interview import (
    get_evidence_gaps,
    generate_interview_questions,
    add_interview_note,
    LEADING_WORDS_PATTERN
)


class TestInterviewGuide(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_evidence_gaps_detection(self):
        gaps = get_evidence_gaps()
        self.assertIn("sparse_themes", gaps)
        self.assertIn("contradictory_themes", gaps)
        self.assertIn("missing_context_areas", gaps)

    def test_generate_neutral_interview_questions(self):
        questions = generate_interview_questions(theme_name="Payment and mandate friction")
        self.assertIsInstance(questions, list)
        self.assertGreaterEqual(len(questions), 3)

        for q in questions:
            self.assertIn("question", q)
            self.assertIn("area", q)
            # Ensure no leading words
            self.assertIsNone(LEADING_WORDS_PATTERN.search(q["question"]))

    def test_add_interview_note(self):
        test_note = "User explained that salary is credited on the 5th, but SIP was scheduled on the 1st."
        rid = add_interview_note(
            text=test_note,
            respondent_id="test_runner_interview_temp"
        )
        self.assertIsNotNone(rid)

        with get_connection() as conn:
            row = conn.execute("SELECT * FROM records WHERE record_id = ?", (rid,)).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["record_type"], "interview_note")
            self.assertEqual(row["collection_method"], "user_interview")
            self.assertEqual(row["source"], "Primary User Interview")
            self.assertEqual(row["respondent_id"], "test_runner_interview_temp")

    @classmethod
    def tearDownClass(cls):
        with get_connection() as conn:
            conn.execute("DELETE FROM records WHERE respondent_id = 'test_runner_interview_temp'")


if __name__ == "__main__":
    unittest.main()
