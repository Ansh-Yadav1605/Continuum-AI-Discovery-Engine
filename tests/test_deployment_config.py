"""
tests/test_deployment_config.py — Validation tests for deployment readiness,
secret exclusion, CORS policy, and environment-aware API configuration.
"""

import os
import re
import unittest
from fastapi.testclient import TestClient
from extension_server.server import app


class TestDeploymentConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.client = TestClient(app)

    def test_env_example_contains_no_secrets(self):
        env_ex_path = os.path.join(self.root_dir, ".env.example")
        self.assertTrue(os.path.exists(env_ex_path), ".env.example must exist")

        with open(env_ex_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Must not contain real Groq API key pattern
        self.assertIsNone(
            re.search(r'gsk_[a-zA-Z0-9]{20,}', content),
            "Found real API key in .env.example! It must only contain safe placeholder values."
        )
        self.assertIn("your_groq_or_grok_api_key_here", content)

    def test_gitignore_protects_critical_files(self):
        gitignore_path = os.path.join(self.root_dir, ".gitignore")
        self.assertTrue(os.path.exists(gitignore_path), ".gitignore must exist")

        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()

        required_patterns = [
            ".env",
            "data/",
            "scratch/",
            "_backup_pre_deployment/",
            "*.db",
            "__pycache__/",
            ".pytest_cache/"
        ]
        for pat in required_patterns:
            self.assertIn(pat, content, f"Missing critical exclusion '{pat}' in .gitignore")

    def test_anonymized_research_data(self):
        js_path = os.path.join(self.root_dir, "assets", "js", "research_data.js")
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
        self.assertEqual(
            len(emails), 0,
            f"Found raw email addresses in assets/js/research_data.js: {emails}. Must be anonymized."
        )

    def test_index_html_has_no_hardcoded_localhost_api_urls(self):
        index_path = os.path.join(self.root_dir, "index.html")
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = re.findall(r'http://127\.0\.0\.1:8000', content)
        self.assertEqual(
            len(matches), 0,
            f"Found hardcoded 'http://127.0.0.1:8000' in index.html: {len(matches)} occurrences. Must use APP_CONFIG.apiUrl."
        )
        self.assertIn("assets/js/config.js", content, "index.html must include assets/js/config.js")

    def test_health_check_endpoint(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("status", data)
        self.assertIn("database", data)
        self.assertIn("timestamp", data)
        self.assertEqual(data["status"], "ok")

    def test_procfile_exists_and_valid(self):
        procfile_path = os.path.join(self.root_dir, "Procfile")
        self.assertTrue(os.path.exists(procfile_path), "Procfile must exist for Railway")

        with open(procfile_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("uvicorn extension_server.server:app", content)
        self.assertIn("0.0.0.0", content)


if __name__ == '__main__':
    unittest.main()
