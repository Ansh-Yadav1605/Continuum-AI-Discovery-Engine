"""
tests/test_quarantine_and_reports.py — Verification suite for Data Integrity, Quarantine,
Secondary Collection Veracity, and Research Reports.
"""

import io
import json
import csv
import unittest
from fastapi.testclient import TestClient

from extension_server.server import app
from core.database import (
    get_connection,
    get_records,
    count_records,
    search_records,
    get_records_with_analysis
)
from core.export import (
    export_research_data,
    export_research_data_csv,
    export_research_data_json,
    generate_methodology,
    export_themes,
    export_evidence_citations,
    export_contradictions_report
)
from core.themes import get_theme_summary, get_theme_distribution
from core.secondary_collection import is_safe_public_url, collect_from_platform


class TestQuarantineAndReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_verified_counts_and_quarantine_isolation(self):
        """Verify exact expected counts: 511 active secondary, 59 quarantined in vault (34 primary 1:1 + 25 synthetic) = 570 total."""
        with get_connection() as conn:
            total_active = count_records(conn, include_quarantined=False)
            primary_active = count_records(conn, filters={"source_category": "primary"}, include_quarantined=False)
            secondary_active = count_records(conn, filters={"source_category": "secondary"}, include_quarantined=False)
            quarantined_total = count_records(conn, filters={"is_quarantined": 1}, include_quarantined=True)
            all_in_db = count_records(conn, include_quarantined=True)
            sec_with_url = conn.execute("SELECT count(*) FROM records WHERE source_category = 'secondary' AND COALESCE(is_quarantined, 0) = 0 AND source_url IS NOT NULL AND length(source_url) > 15").fetchone()[0]

        self.assertEqual(primary_active, 0, f"Expected 0 active primary records (all in quarantine vault), got {primary_active}")
        self.assertGreaterEqual(secondary_active, 500, f"Expected at least 500 active secondary records, got {secondary_active}")
        self.assertEqual(secondary_active, 511, f"Expected 511 active secondary records, got {secondary_active}")
        self.assertEqual(total_active, 511, f"Expected 511 total active records, got {total_active}")
        self.assertEqual(quarantined_total, 59, f"Expected 59 quarantined records, got {quarantined_total}")
        self.assertEqual(all_in_db, 570, f"Expected 570 total records in database, got {all_in_db}")
        self.assertEqual(sec_with_url, secondary_active, "100% of secondary records must have a real, valid URL")

    def test_genuine_survey_records_intact(self):
        """Verify that all 27 genuine survey responses (RESP-0001 to RESP-0027) and 7 interview notes (INT-0001 to INT-0007) are preserved."""
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT respondent_id, source, source_category, is_quarantined, quarantine_reason 
                FROM records 
                WHERE source_category = 'primary' AND is_quarantined = 1 AND (respondent_id LIKE 'RESP-%' OR respondent_id LIKE 'INT-%')
                ORDER BY respondent_id
            """).fetchall()

        self.assertEqual(len(rows), 34)
        resp_ids = {r["respondent_id"] for r in rows}
        for i in range(1, 28):
            self.assertIn(f"RESP-{i:04d}", resp_ids)
        for i in range(1, 8):
            self.assertIn(f"INT-{i:04d}", resp_ids)
            
    def test_quarantined_synthetic_records_excluded_from_queries(self):
        """Verify that get_records and search_records exclude quarantined items by default."""
        with get_connection() as conn:
            active_records = get_records(conn, limit=1000, include_quarantined=False)
            active_ids = {r["record_id"] for r in active_records}
            
            quarantined_rows = conn.execute("SELECT record_id FROM records WHERE is_quarantined = 1").fetchall()
            quarantined_ids = {r["record_id"] for r in quarantined_rows}

            # Intersect must be empty
            self.assertEqual(len(active_ids.intersection(quarantined_ids)), 0)

            # Search also excludes quarantined
            search_results = search_records(conn, "SIP", limit=100)
            for r in search_results:
                self.assertNotIn(r["record_id"], quarantined_ids)

    def test_api_stats_endpoint_reflects_active_counts(self):
        """Verify GET /api/stats reports 511 total, 0 primary, 511 secondary, 59 quarantined."""
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["total_records"], 511)
        self.assertEqual(data["primary_records"], 0)
        self.assertEqual(data["secondary_records"], 511)
        self.assertEqual(data["quarantined_records"], 59)

    def test_api_records_filtering(self):
        """Verify GET /api/records filters by source_type (all, primary, secondary, quarantined)."""
        # All
        r_all = self.client.get("/api/records?source_type=all&limit=1000").json()
        self.assertEqual(r_all["total"], 511)
        self.assertEqual(len(r_all["records"]), 511)

        # Primary (returns all 34 primary 1:1 records from vault)
        r_pri = self.client.get("/api/records?source_type=primary&limit=1000").json()
        self.assertEqual(r_pri["total"], 34)
        self.assertEqual(len(r_pri["records"]), 34)

        # Interviews (7 qualitative responses)
        r_int = self.client.get("/api/records?source_type=interviews&limit=1000").json()
        self.assertEqual(r_int["total"], 7)
        self.assertEqual(len(r_int["records"]), 7)

        # Secondary
        r_sec = self.client.get("/api/records?source_type=secondary&limit=1000").json()
        self.assertEqual(r_sec["total"], 511)
        self.assertEqual(len(r_sec["records"]), 511)
        for r in r_sec["records"]:
            self.assertEqual(r["source_category"], "secondary")
            self.assertTrue(r["source_url"] and r["source_url"].startswith("http"), "Secondary records must have real URL")

        # Quarantined
        r_qua = self.client.get("/api/records?source_type=quarantined&limit=1000").json()
        self.assertEqual(r_qua["total"], 59)
        self.assertEqual(len(r_qua["records"]), 59)

        # Full
        r_ful = self.client.get("/api/records?source_type=full&limit=1000").json()
        self.assertEqual(r_ful["total"], 570)
        self.assertEqual(len(r_ful["records"]), 570)

    def test_dataset_export_csv_and_json(self):
        """Verify /api/reports/export outputs valid CSV and JSON with correct record counts."""
        # 1. Combined CSV (Active 511)
        res_csv = self.client.get("/api/reports/export?scope=all&format=csv")
        self.assertEqual(res_csv.status_code, 200)
        self.assertEqual(res_csv.headers["content-type"], "text/csv; charset=utf-8")
        reader = list(csv.DictReader(io.StringIO(res_csv.text)))
        self.assertEqual(len(reader), 511, "CSV export must contain exactly 511 active records")

        # 2. Combined JSON (Active 511)
        res_json = self.client.get("/api/reports/export?scope=all&format=json")
        self.assertEqual(res_json.status_code, 200)
        data = res_json.json()
        self.assertEqual(data["count"], 511)
        self.assertEqual(len(data["records"]), 511)

        # 3. Primary CSV (34 records from vault: 27 survey + 7 interview)
        res_pri_csv = self.client.get("/api/reports/export?scope=primary&format=csv")
        self.assertEqual(res_pri_csv.status_code, 200)
        reader_pri = list(csv.DictReader(io.StringIO(res_pri_csv.text)))
        self.assertEqual(len(reader_pri), 34, "Primary CSV must contain exactly 34 records")

        # 4. Secondary CSV (511 records)
        res_sec_csv = self.client.get("/api/reports/export?scope=secondary&format=csv")
        self.assertEqual(res_sec_csv.status_code, 200)
        reader_sec = list(csv.DictReader(io.StringIO(res_sec_csv.text)))
        self.assertEqual(len(reader_sec), 511, "Secondary CSV must contain exactly 511 records")

        # 5. Quarantine CSV (59 records)
        res_qua_csv = self.client.get("/api/reports/export?scope=quarantine&format=csv")
        self.assertEqual(res_qua_csv.status_code, 200)
        reader_qua = list(csv.DictReader(io.StringIO(res_qua_csv.text)))
        self.assertEqual(len(reader_qua), 59, "Quarantine CSV must contain exactly 59 records")

    def test_analysis_reports_endpoints(self):
        """Verify readable analysis reports (methodology, themes, citations, contradictions, problems)."""
        # Methodology
        res_meth = self.client.get("/api/reports/analysis?report_type=methodology")
        self.assertEqual(res_meth.status_code, 200)
        self.assertIn("- **Active Ingested Records:** 511", res_meth.text)
        self.assertIn("Secondary Research (Public Reviews, App Store, & Studies): 511", res_meth.text)
        self.assertIn("Safety Quarantine Vault Records:** 59", res_meth.text)

        # Themes
        res_thm = self.client.get("/api/reports/analysis?report_type=themes&format=markdown")
        self.assertEqual(res_thm.status_code, 200)
        self.assertIn("# SIP Discovery Engine: Theme Summary", res_thm.text)

        # Citations
        res_cit = self.client.get("/api/reports/analysis?report_type=citations&format=markdown")
        self.assertEqual(res_cit.status_code, 200)
        self.assertIn("# SIP Discovery: Evidence Citations", res_cit.text)

        # Contradictions
        res_con = self.client.get("/api/reports/analysis?report_type=contradictions&format=markdown")
        self.assertEqual(res_con.status_code, 200)
        self.assertIn("# SIP Discovery: Contradictions & Behavioral Signals Analysis", res_con.text)

        # Problems
        res_prb = self.client.get("/api/reports/analysis?report_type=problems&format=markdown")
        self.assertEqual(res_prb.status_code, 200)
        self.assertIn("# Candidate Problem Statements", res_prb.text)

    def test_secondary_collector_ssrf_and_error_handling(self):
        """Verify SSRF protection and non-fabrication error reporting for unavailable sources."""
        # SSRF checks
        safe, err = is_safe_public_url("http://127.0.0.1:8000/secret")
        self.assertFalse(safe)
        self.assertIn("Access to localhost/internal addresses is strictly prohibited", err)

        safe, err = is_safe_public_url("http://192.168.1.1/router")
        self.assertFalse(safe)
        self.assertIn("prohibited", err)

        # Unavailable source returns structured error without inventing synthetic data
        res = collect_from_platform(
            platform="reddit",
            target="https://reddit.com/r/IndiaInvestments/comments/nonexistent_test"
        )
        self.assertFalse(res["success"])
        self.assertTrue(len(res.get("error", "")) > 10)


if __name__ == "__main__":
    unittest.main()
