"""
tests/test_database.py — Unit tests for SQLite database schema and CRUD operations.
"""

import os
import unittest
from core.database import init_db, get_connection, insert_record, get_records, count_records

class TestDatabase(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_schema_tables_exist(self):
        """Verify all 8 tables defined in architecture.md exist in the database."""
        expected_tables = {
            "records",
            "analysis_results",
            "themes",
            "problem_statements",
            "scores",
            "evidence_log",
            "source_register",
            "settings"
        }
        with get_connection() as conn:
            rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            existing_tables = {r["name"] for r in rows}

        for tbl in expected_tables:
            self.assertIn(tbl, existing_tables, f"Table '{tbl}' is missing from database schema")

    def test_taxonomy_prepopulated(self):
        """Verify that the 14-category provisional taxonomy is populated in themes table."""
        with get_connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM themes").fetchone()[0]
        self.assertGreaterEqual(count, 14, "Expected at least 14 taxonomy themes")

    def test_record_crud(self):
        """Verify inserting and querying a unified research record."""
        with get_connection() as conn:
            rec_id = insert_record(conn, {
                "source": "test_suite",
                "record_type": "public_review",
                "text": "Automated test record for database verification.",
                "rating": 4.5
            })
            self.assertIsNotNone(rec_id)

            fetched = conn.execute("SELECT * FROM records WHERE record_id = ?", (rec_id,)).fetchone()
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched["source"], "test_suite")
            self.assertEqual(fetched["rating"], 4.5)

    @classmethod
    def tearDownClass(cls):
        with get_connection() as conn:
            conn.execute("DELETE FROM records WHERE source = 'test_suite'")


if __name__ == "__main__":
    unittest.main()
