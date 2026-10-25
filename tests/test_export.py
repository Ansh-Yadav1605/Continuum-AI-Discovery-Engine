"""
tests/test_export.py — Unit tests for Deliverable Export Hub & Methodology Report (Milestone 3.4).
"""

import unittest
from core.database import init_db
from core.export import (
    export_research_data,
    export_evidence_log,
    export_themes,
    export_problems,
    export_source_register,
    generate_methodology
)


class TestExportHub(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_export_research_data(self):
        df = export_research_data()
        self.assertIsNotNone(df)
        self.assertIn("record_id", df.columns)
        self.assertIn("text", df.columns)

    def test_export_evidence_log(self):
        df = export_evidence_log()
        self.assertIsNotNone(df)
        self.assertIn("log_id", df.columns)

    def test_export_themes(self):
        df, md_str = export_themes()
        self.assertIsNotNone(df)
        self.assertIn("Theme Summary", md_str)

    def test_export_problems(self):
        json_str, md_str = export_problems()
        self.assertIn("[", json_str)
        self.assertIn("# Candidate Problem Statements", md_str)

    def test_export_source_register(self):
        df = export_source_register()
        self.assertIsNotNone(df)

    def test_generate_methodology(self):
        report = generate_methodology()
        self.assertIn("Research Methodology & Discovery Disclosure", report)
        self.assertIn("Limitations", report)
        self.assertIn("Groww", report)


if __name__ == "__main__":
    unittest.main()
