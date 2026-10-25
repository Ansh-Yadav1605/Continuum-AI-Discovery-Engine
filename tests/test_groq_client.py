"""
tests/test_groq_client.py — Tests for Groq API client, connection diagnostics, schema validation, and prompts.
"""

import unittest
from unittest.mock import patch
from core.groq_client import test_connection, validate_schema, analyse_record, get_api_key
from core.prompts import build_user_prompt, TAXONOMY_THEMES


class TestGroqClient(unittest.TestCase):
    def test_schema_validation(self):
        """Verify schema validation strictly enforces required taxonomy and structure."""
        valid_payload = {
            "relevance": "directly_relevant",
            "relevance_explanation": "Valid test reason",
            "evidence_excerpt": "Direct quote",
            "themes": ["Expectations vs. actual experience"],
            "behaviour": "Stopped SIP",
            "user_need": "Clear return expectations",
            "workaround": None,
            "journey_stage": "3-6_months",
            "continuation_mention": "stopping",
            "missing_context": "None",
            "explanation": "Valid summary"
        }
        is_valid, errors = validate_schema(valid_payload)
        self.assertTrue(is_valid, f"Validation failed on valid payload: {errors}")

        # Invalid relevance enum
        invalid_payload = dict(valid_payload, relevance="unsupported_rel")
        is_valid, errors = validate_schema(invalid_payload)
        self.assertFalse(is_valid)

    def test_prompt_truncation(self):
        """Verify text exceeding 8,000 characters is safely truncated with a system notice."""
        long_text = "A" * 10000
        prompt = build_user_prompt({"text": long_text, "record_id": "test-uuid"})
        self.assertIn("truncated for analysis", prompt)
        self.assertLess(len(prompt), 10000)

    def test_connection_diagnostic_missing_key(self):
        """Verify diagnostic gracefully catches unconfigured API key."""
        with patch("core.groq_client.get_api_key", return_value=None):
            result = test_connection()
            self.assertFalse(result["all_passed"])
            self.assertEqual(result["steps"][0]["step"], 1)
            self.assertFalse(result["steps"][0]["success"])
            self.assertIn("GROQ_API_KEY", result["steps"][0]["message"])

    def test_live_connection_diagnostic(self):
        """Verify live connection check passes with configured key."""
        key = get_api_key()
        if not key or key == "your_key_here":
            self.skipTest("No live GROQ_API_KEY available in .env")

        result = test_connection()
        self.assertTrue(result["all_passed"], f"Diagnostic steps failed: {result['steps']}")
        self.assertEqual(len(result["steps"]), 5)


if __name__ == "__main__":
    unittest.main()
