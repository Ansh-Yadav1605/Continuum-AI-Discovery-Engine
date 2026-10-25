"""
tests/test_candidate_problems_audit.py — Verification test ensuring all research IDs
cited in candidate_problems.json exist in data/sip_discovery.db, no mock citations remain,
and all 3 problems contain transparent scorecard schemas and distinct user needs vs interventions.
"""

import json
import os
import sqlite3
import unittest


class TestCandidateProblemsAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "candidate_problems.json")
        cls.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sip_discovery.db")
        
        self_conn = sqlite3.connect(cls.db_path)
        self_conn.row_factory = sqlite3.Row
        cls.conn = self_conn

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_candidate_problems_file_exists(self):
        self.assertTrue(os.path.exists(self.json_path), "candidate_problems.json must exist in root directory")

    def test_json_structure_and_disclaimer(self):
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertIn("metadata", data)
        self.assertIn("score_methodology_disclaimer", data["metadata"])
        self.assertIn("audit_summary", data)
        self.assertIn("candidate_problems", data)
        self.assertEqual(len(data["candidate_problems"]), 3)

    def test_zero_mock_citations_in_revised_candidates(self):
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        mock_patterns = ["REV-001", "REV-002", "REV-004", "REV-006", "REV-007", "REV-011", "REV-012", "Trustpilot"]
        
        for p in data["candidate_problems"]:
            rev = p["revised_candidate"]
            rev_str = json.dumps(rev)
            for pat in mock_patterns:
                self.assertNotIn(pat, rev_str, f"Found mock pattern {pat} in revised candidate for {p['problem_id']}")

    def test_all_cited_research_ids_exist_in_db(self):
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        c = self.conn.cursor()
        for p in data["candidate_problems"]:
            pid = p["problem_id"]
            ev_list = p["revised_candidate"]["verified_supporting_evidence"]
            self.assertGreaterEqual(len(ev_list), 5, f"Candidate {pid} must have at least 5 verified records")

            for ev in ev_list:
                rid = ev["research_id"]
                c.execute("SELECT record_id, source FROM records WHERE record_id = ? OR respondent_id = ?", (rid, rid))
                row = c.fetchone()
                self.assertIsNotNone(row, f"Research ID '{rid}' cited in problem '{pid}' not found in SQLite database!")

    def test_no_arbitrary_churn_percentage_claims_in_hypotheses(self):
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for p in data["candidate_problems"]:
            hyp = p["revised_candidate"]["testable_hypothesis"].lower()
            self.assertNotIn("decrease by 25%", hyp)
            self.assertNotIn("fall by 40%", hyp)
            self.assertNotIn("drop by 40%", hyp)

    def test_separation_of_user_need_and_intervention(self):
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for p in data["candidate_problems"]:
            rev = p["revised_candidate"]
            self.assertTrue(len(rev["validated_user_need"]) > 20)
            self.assertTrue(len(rev["proposed_intervention"]) > 20)
            self.assertNotEqual(rev["validated_user_need"], rev["proposed_intervention"])

    def test_success_metrics_defined(self):
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for p in data["candidate_problems"]:
            metrics = p["revised_candidate"]["proposed_success_metrics"]
            self.assertGreaterEqual(len(metrics), 2)
            for m in metrics:
                self.assertIn("metric_name", m)
                self.assertIn("type", m)
                self.assertIn("definition", m)


if __name__ == '__main__':
    unittest.main()
