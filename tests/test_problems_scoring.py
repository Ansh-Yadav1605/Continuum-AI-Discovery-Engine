"""
tests/test_problems_scoring.py — Unit tests for Candidate Problem Statements and Scoring (Milestone 2.2).
"""

import unittest
import uuid
from core.database import init_db
from core.problems import (
    save_problem,
    get_problem,
    get_all_problems,
    update_validation_status,
    delete_problem,
    generate_problem_statements
)
from core.scoring import (
    calculate_score,
    save_score,
    get_scorecard,
    get_ranked_problems
)


class TestProblemsAndScoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_problem_statement_crud(self):
        p_data = {
            "title": "Mandate Confusion during First SIP Instalment",
            "user_segment": "First-time mutual fund investors",
            "journey_stage": "Month 1",
            "observation": "Users are unaware of separate e-mandate registration delay.",
            "interpretation": "Generates perception of failed transaction.",
            "hypothesis": "Clear status tracking will prevent premature SIP cancellations.",
            "validation_status": "needs_research"
        }
        pid = save_problem(p_data)
        self.assertIsNotNone(pid)

        fetched = get_problem(pid)
        self.assertEqual(fetched["title"], p_data["title"])
        self.assertEqual(fetched["validation_status"], "needs_research")

        # Test validation status update
        updated = update_validation_status(pid, "supported")
        self.assertTrue(updated)
        self.assertEqual(get_problem(pid)["validation_status"], "supported")

        # Test delete
        deleted = delete_problem(pid)
        self.assertTrue(deleted)
        self.assertIsNone(get_problem(pid))

    def test_weighted_scoring_calculation(self):
        # Weights: ev: 0.25, sip: 0.25, sev: 0.15, prod: 0.15, feas: 0.10, safe: 0.10
        scores = {
            "evidence_strength": 4,   # 4 * 0.25 = 1.00
            "sip_relevance": 4,       # 4 * 0.25 = 1.00
            "user_severity": 3,       # 3 * 0.15 = 0.45
            "product_influence": 3,   # 3 * 0.15 = 0.45
            "feasibility": 5,         # 5 * 0.10 = 0.50
            "safety_compliance": 5    # 5 * 0.10 = 0.50
        }
        # Expected: 1.00 + 1.00 + 0.45 + 0.45 + 0.50 + 0.50 = 3.90
        weighted, blocked = calculate_score(scores)
        self.assertAlmostEqual(weighted, 3.90, places=2)
        self.assertFalse(blocked)

    def test_safety_compliance_hard_filter(self):
        # Safety score of 2 must trigger hard filter
        scores = {
            "evidence_strength": 5,
            "sip_relevance": 5,
            "user_severity": 5,
            "product_influence": 5,
            "feasibility": 5,
            "safety_compliance": 2  # Disqualifying compliance rating
        }
        weighted, blocked = calculate_score(scores)
        self.assertTrue(blocked)

    def test_scorecard_persistence_and_ranking(self):
        pid = save_problem({"title": "Test Prioritization Candidate"})
        try:
            score_dict = {
                "evidence_strength": 4,
                "sip_relevance": 5,
                "user_severity": 4,
                "product_influence": 4,
                "feasibility": 4,
                "safety_compliance": 5
            }
            score_id = save_score(pid, score_dict, justification="High triangulation from survey data.")
            self.assertIsNotNone(score_id)

            card = get_scorecard(pid)
            self.assertEqual(card["evidence_strength"], 4)
            self.assertEqual(card["sip_relevance"], 5)
            self.assertGreater(card["weighted_score"], 4.0)

            ranked = get_ranked_problems()
            candidate = next((r for r in ranked if r["problem_id"] == pid), None)
            self.assertIsNotNone(candidate)
            self.assertFalse(candidate["safety_blocked"])
            self.assertTrue(candidate["has_score"])
        finally:
            delete_problem(pid)


if __name__ == "__main__":
    unittest.main()
