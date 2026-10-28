"""
tests/test_sip_rescue_navigator.py — Unit tests for SIP Rescue Navigator rules engine and guidance logic.

Validates:
- Deterministic guidance evaluation for all core situations.
- Timing cutoff rules (T-0, T-1/2, T-3/5, T-5+ days) across Groww, Zerodha Coin, and AMC Direct.
- Graceful handling of unknown platforms and unconfirmed dates.
- Comeback Plan creation and RFC 5545 iCalendar (.ics) generation.
- Privacy-conscious discovery feedback metrics calculation.
"""

import unittest
import os
import json
from core.sip_navigator_rules import (
    evaluate_sip_guidance,
    create_comeback_plan,
    generate_ics_calendar_file,
    get_discovery_metrics,
    save_feedback_record,
    load_feedback_records,
    PLATFORM_RULES,
    SITUATION_OPTIONS,
    PLATFORM_OPTIONS,
    SIP_SETUP_OPTIONS,
    TIMING_OPTIONS
)


class TestSIPRescueNavigatorRules(unittest.TestCase):

    def test_scenario_1_temporary_cash_flow_pressure_known_date(self):
        """Scenario 1: Temporary cash-flow break with adequate notice (3-5 days on Groww)."""
        card = evaluate_sip_guidance(
            situation="I need a temporary break from my SIP.",
            platform="Groww",
            setup_type="Platform-managed SIP",
            time_remaining="Within 3–5 days"
        )
        self.assertEqual(card.cutoff_status, "SAFE_WINDOW_OPEN")
        self.assertIn("Skip", card.available_options[0]["name"])
        self.assertIn("Groww", card.applicable_rule.platform)
        self.assertEqual(card.verification_status, "VERIFIED")
        self.assertTrue(card.primary_action_url.startswith("https://"))
        self.assertIn("Pause", card.headline)

    def test_scenario_2_upcoming_debit_too_close_to_cutoff(self):
        """Scenario 2: Debit approaching within 1-2 days (cutoff passed for Groww 2-day rule)."""
        card = evaluate_sip_guidance(
            situation="My next SIP debit is approaching, and I may not have enough money.",
            platform="Groww",
            setup_type="Platform-managed SIP",
            time_remaining="Within 1–2 days"
        )
        self.assertIn("CRITICAL_CUTOFF_PASSED", card.cutoff_status)
        self.assertIn("Cutoff Likely Passed", card.cutoff_warning_badge)
        # Guidance must warn user that upcoming debit may still be attempted
        self.assertIn("next month", card.timing_eligibility.lower())
        self.assertIn("ECS", card.situation_meaning)

    def test_scenario_3_failed_instalment_diagnostics(self):
        """Scenario 3: Failed instalment with calm, non-alarmist diagnostics."""
        card = evaluate_sip_guidance(
            situation="My SIP payment failed.",
            platform="Groww",
            setup_type="Platform-managed SIP",
            time_remaining="Today"
        )
        self.assertIn("failed", card.headline.lower())
        self.assertIn("NOT immediately cancelled", card.situation_meaning)
        self.assertIn("3 consecutive", card.situation_meaning)
        self.assertEqual(card.applicable_rule.rule_id, "groww_payment_failure")
        self.assertTrue(any("Pay Now" in opt["desc"] or "UPI" in opt["name"] for opt in card.available_options))

    def test_scenario_4_unaffordable_ongoing_sip_amount(self):
        """Scenario 4: SIP amount becoming unaffordable — step down to scheme minimum."""
        card = evaluate_sip_guidance(
            situation="My current SIP amount is becoming difficult to afford.",
            platform="Groww",
            setup_type="Platform-managed SIP",
            time_remaining="More than 5 days"
        )
        self.assertIn("Adjust without stopping", card.headline)
        self.assertIn("Step Down Amount", card.available_options[0]["name"])
        self.assertEqual(card.applicable_rule.action_type, "modify_amount")
        self.assertEqual(card.cutoff_status, "SAFE_WINDOW_OPEN")

    def test_scenario_5_user_wants_to_cancel_completely(self):
        """Scenario 5: Complete cancellation with explicit confirmation of unit safety."""
        card = evaluate_sip_guidance(
            situation="I want to stop my SIP completely.",
            platform="Zerodha Coin",
            setup_type="Platform-managed SIP",
            time_remaining="More than 5 days"
        )
        self.assertIn("penalty-free exit", card.headline.lower())
        self.assertIn("does NOT sell your mutual fund units", card.situation_meaning)
        self.assertIn("Zerodha Coin", card.applicable_rule.platform)
        self.assertEqual(card.applicable_rule.action_type, "cancel")
        self.assertEqual(card.verification_status, "VERIFIED")

    def test_scenario_6_unknown_platform_fallback(self):
        """Scenario 6: Unknown platform directs user to official support channel without inventing rules."""
        card = evaluate_sip_guidance(
            situation="I'm not sure what my options are.",
            platform="Another platform",
            setup_type="I'm not sure",
            time_remaining="I'm not sure of the date"
        )
        self.assertEqual(card.verification_status, "GENERAL_GUIDANCE")
        self.assertIn("General", card.applicable_rule.platform)
        self.assertTrue(any("could not verify" in lim.lower() for lim in card.limitations))
        self.assertEqual(card.cutoff_status, "UNCERTAIN_TIMING")

    def test_scenario_7_amc_registered_mandate_longer_cutoff(self):
        """Scenario 7: AMC-registered mandate requires 10-21 days notice, so 3-5 days is cutoff passed."""
        card = evaluate_sip_guidance(
            situation="I need a temporary break from my SIP.",
            platform="Groww",
            setup_type="AMC-registered SIP",
            time_remaining="Within 3–5 days"
        )
        self.assertEqual(card.cutoff_status, "CRITICAL_CUTOFF_PASSED")
        self.assertIn("AMC Cutoff", card.cutoff_warning_badge)
        self.assertIn("AMFI India", card.applicable_rule.official_source_name)

    def test_comeback_plan_creation_and_ics(self):
        """Verify Comeback Plan creates simulated reminder and valid .ics file."""
        plan = create_comeback_plan(
            days_offset=30,
            focus_action="Review emergency fund and decide whether to resume ₹1,000 SIP",
            custom_reflection="Check if medical expenses have stabilized."
        )
        self.assertEqual(plan.days_from_now, 30)
        self.assertTrue(plan.is_simulated)
        self.assertEqual(plan.status, "SCHEDULED_LOCAL_PROTOTYPE")

        ics_text = generate_ics_calendar_file(plan)
        self.assertIn("BEGIN:VCALENDAR", ics_text)
        self.assertIn("END:VCALENDAR", ics_text)
        self.assertIn("SUMMARY:SIP Comeback Check-in", ics_text)
        self.assertIn(plan.reminder_id, ics_text)

    def test_discovery_metrics_calculation(self):
        """Verify discovery usability metrics include explicit numerators and denominators."""
        metrics = get_discovery_metrics()
        self.assertGreater(metrics["total_sessions"], 0)
        self.assertIn("clarity_rate", metrics)
        self.assertEqual(metrics["clarity_denominator"], metrics["total_sessions"])
        self.assertEqual(metrics["deadline_denominator"], metrics["total_sessions"])
        self.assertEqual(metrics["action_denominator"], metrics["total_sessions"])
        self.assertEqual(metrics["reminder_denominator"], metrics["total_sessions"])
        self.assertIsInstance(metrics["clarity_rate"], float)


if __name__ == "__main__":
    unittest.main()
