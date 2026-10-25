"""
tests/test_extension_server.py — Unit tests for FastAPI receiver endpoint (Milestone 3.1).
"""

import unittest
import uuid
from fastapi.testclient import TestClient
from extension_server.server import app, get_expected_auth_token
from core.database import init_db, get_connection


class TestExtensionServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.valid_token = get_expected_auth_token()

    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["database"], "connected")

    def test_collect_unauthorized_token(self):
        payload = {
            "text": "This is a test feedback quote.",
            "source_url": "https://reddit.com/r/IndiaInvestments",
            "source": "Reddit",
            "auth_token": "wrong_invalid_secret_token"
        }
        response = self.client.post("/api/collect", json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Unauthorized", response.json()["detail"])

    def test_collect_empty_text_rejection(self):
        payload = {
            "text": "   <b></b>   ",
            "source_url": "https://example.com",
            "source": "Test",
            "auth_token": self.valid_token
        }
        response = self.client.post("/api/collect", json=payload)
        self.assertEqual(response.status_code, 422)

    created_record_ids = []

    def test_collect_valid_submission_and_deduplication(self):
        unique_text = f"User experienced auto-pay delay on Groww {uuid.uuid4()}"
        payload = {
            "text": f"<p>{unique_text}</p>",
            "source_url": "https://play.google.com/store/apps/details?id=com.nextbillion.groww",
            "source": "Google Play Store",
            "auth_token": self.valid_token
        }
        
        # 1. First submission should be unique
        res1 = self.client.post("/api/collect", json=payload)
        self.assertEqual(res1.status_code, 201)
        data1 = res1.json()
        self.assertEqual(data1["duplicate_status"], "unique")
        rec_id = data1["record_id"]
        self.created_record_ids.append(rec_id)

        with get_connection() as conn:
            row = conn.execute("SELECT * FROM records WHERE record_id = ?", (rec_id,)).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["collection_method"], "chrome_extension")
            self.assertEqual(row["record_type"], "browser_collected")
            self.assertNotIn("<p>", row["text"])  # HTML stripped

        # 2. Duplicate submission with exact same text
        res2 = self.client.post("/api/collect", json=payload)
        self.assertEqual(res2.status_code, 201)
        data2 = res2.json()
        self.assertEqual(data2["duplicate_status"], "exact_duplicate")
        self.created_record_ids.append(data2["record_id"])

    @classmethod
    def tearDownClass(cls):
        if cls.created_record_ids:
            with get_connection() as conn:
                placeholders = ','.join('?' * len(cls.created_record_ids))
                conn.execute(f"DELETE FROM records WHERE record_id IN ({placeholders})", cls.created_record_ids)


if __name__ == "__main__":
    unittest.main()
