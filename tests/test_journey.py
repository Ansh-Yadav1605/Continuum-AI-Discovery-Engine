"""
tests/test_journey.py — Unit tests for the Explainable Research-to-Problem Journey.
"""

import unittest
from core.database import init_db
from core.journey import (
    get_sources_census,
    get_data_quality_breakdown,
    get_theme_evidence_tree,
    get_evidence_synthesis_cards,
    get_problem_statement_builder_data,
    get_backward_provenance_trace
)


class TestResearchJourney(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_sources_census_non_overlapping_and_complete(self):
        """Verify census returns exactly 570 records and components sum correctly."""
        census = get_sources_census()
        self.assertEqual(census["total_records"], 570)
        self.assertEqual(census["primary_surveys"], 27)
        self.assertEqual(census["primary_interviews"], 7)
        self.assertEqual(census["synthetic_seed"], 25)
        self.assertEqual(census["quarantined_total"], 59)
        self.assertEqual(census["active_secondary"], 511)
        
        # Verify non-overlapping sum
        non_overlapping_sum = (
            census["primary_surveys"] +
            census["primary_interviews"] +
            census["synthetic_seed"] +
            census["play_store_reviews"] +
            census["reddit_reviews"] +
            census["regulatory_studies"]
        )
        self.assertEqual(non_overlapping_sum, 570, "Census categories must be strictly non-overlapping and sum to 570")

    def test_data_quality_provenance(self):
        """Verify data quality inspector returns records with provenance details."""
        records = get_data_quality_breakdown(limit=10)
        self.assertGreaterEqual(len(records), 1)
        first = records[0]
        self.assertIn("record_id", first)
        self.assertIn("source", first)
        self.assertIn("is_quarantined", first)
        self.assertIn("text", first)

    def test_theme_evidence_tree(self):
        """Verify theme evidence tree extracts active grounded themes."""
        tree = get_theme_evidence_tree()
        self.assertIsInstance(tree, list)
        if tree:
            first_theme = tree[0]
            self.assertIn("theme", first_theme)
            self.assertIn("definition", first_theme)
            self.assertIn("record_count", first_theme)
            self.assertIn("sufficiency", first_theme)
            self.assertIn("sample_citations", first_theme)

    def test_evidence_synthesis_cards(self):
        """Verify 6-part synthesis strictly separates observation from interpretation."""
        cards = get_evidence_synthesis_cards()
        self.assertEqual(len(cards), 3)
        for c in cards:
            self.assertIn("problem_id", c)
            self.assertIn("observation", c)
            self.assertIn("interpretation", c)
            self.assertIn("alternative_explanations", c)
            self.assertIn("contradictory_evidence", c)
            self.assertIn("evidence_gaps", c)
            self.assertIn("follow_up_questions", c)

    def test_problem_statement_builder_syntax(self):
        """Verify candidate problem statements adhere to standard PM syntax."""
        probs = get_problem_statement_builder_data()
        self.assertEqual(len(probs), 3)
        for p in probs:
            self.assertTrue(p["formatted_statement"].startswith("For "), "Must start with 'For [segment]'")
            self.assertIn("occurs", p["formatted_statement"])
            self.assertIn("potentially leading to", p["formatted_statement"])
            self.assertIn("opportunity_score", p)
            self.assertIn("score_factors", p)
            self.assertGreater(p["score_factors"]["safety_compliance"], 2, "Safety compliance must be > 2 to pass hard filter")

    def test_reverse_traceability_prob_2(self):
        """Verify reverse traceability resolves 100% of citations in prob-2 directly to database records."""
        trace = get_backward_provenance_trace("prob-2")
        self.assertIsNotNone(trace)
        self.assertEqual(trace["citations_count"], 12)
        self.assertEqual(trace["citations_resolved_in_db"], 12, "All 12 citations in prob-2 must resolve in database")
        
        # Verify INT-0003 is present in trace
        int_0003 = next((s for s in trace["trace_steps"] if s["research_id"] == "INT-0003" or s["respondent_id"] == "INT-0003"), None)
        self.assertIsNotNone(int_0003, "INT-0003 must be resolved in trace")
        self.assertIn("manual", int_0003["citation_quote"].lower())


if __name__ == "__main__":
    unittest.main()
