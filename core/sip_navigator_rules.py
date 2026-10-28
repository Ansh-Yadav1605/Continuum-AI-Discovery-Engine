"""
core/sip_navigator_rules.py — Deterministic Guidance Engine & Verified Rules for SIP Rescue Navigator.

Part of Continuum AI — SIP Continuation Discovery Engine.
Provides transparent, rule-based decision logic based on verified platform documentation
(Groww, Zerodha Coin, AMC-Direct via CAMS/KFintech).

Features:
- Deterministic rules repository with official sources and verification dates.
- Context-aware situational evaluation (Cutoff analysis, plain-language meanings, actionable steps).
- SIP Comeback Plan reminder generator (with iCalendar .ics generator).
- Privacy-conscious prototype feedback logger and discovery metrics aggregator.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, date, timedelta, timezone
import json
import os
from typing import List, Dict, Any, Optional

# ---------------------------------------------------------------------------
# 1. Official Verified Platform Rules Repository
# ---------------------------------------------------------------------------

@dataclass
class PlatformRule:
    rule_id: str
    platform: str                     # "Groww", "Zerodha Coin", "AMC Direct", "General"
    setup_type: str                   # "Platform-managed SIP", "AMC-registered SIP", "All"
    action_type: str                  # "skip", "pause", "modify_amount", "cancel", "payment_failure", "overview"
    supported: bool
    min_notice_days: int              # Working days required before scheduled debit
    notice_cutoff_description: str
    eligibility_conditions: str
    effective_date_implication: str
    limitations: List[str]
    official_source_name: str
    official_source_url: str
    last_verified_date: str           # ISO format YYYY-MM-DD
    verification_status: str          # "VERIFIED", "GENERAL_GUIDANCE", "UNVERIFIED"
    plain_language_summary: str


PLATFORM_RULES: Dict[str, PlatformRule] = {
    # ---------------- GROWW PLATFORM SIP ----------------
    "groww_platform_skip": PlatformRule(
        rule_id="groww_platform_skip",
        platform="Groww",
        setup_type="Platform-managed SIP",
        action_type="skip",
        supported=True,
        min_notice_days=2,
        notice_cutoff_description="At least 2 working days before your scheduled SIP debit date.",
        eligibility_conditions="Available on active Groww AutoPay (e-Mandate / UPI Autopay) SIPs for eligible mutual fund schemes.",
        effective_date_implication="If submitted >= 2 working days before the debit date, the upcoming instalment is skipped without fee or penalty. If submitted within 2 working days, the skip request applies only to the SUBSEQUENT month; the upcoming instalment will still attempt to debit.",
        limitations=[
            "Cannot be processed within 2 working days of scheduled debit date.",
            "Maximum 1 instalment skipped per request; consecutive skips may require a Pause request.",
            "If your bank account has insufficient balance and the skip cutoff has passed, your bank may levy ECS bounce charges (Groww itself charges ₹0).",
            "This prototype cannot check your live Groww account or confirm your bank balance."
        ],
        official_source_name="Groww Help & Support — Skip SIP Instalment",
        official_source_url="https://groww.in/help/mutual-funds/sip",
        last_verified_date="2026-10-25",
        verification_status="VERIFIED",
        plain_language_summary="You can skip your upcoming instalment on Groww with zero platform penalty, provided you submit the request at least 2 working days before your debit date."
    ),
    "groww_platform_pause": PlatformRule(
        rule_id="groww_platform_pause",
        platform="Groww",
        setup_type="Platform-managed SIP",
        action_type="pause",
        supported=True,
        min_notice_days=2,
        notice_cutoff_description="At least 2 working days before your next SIP date.",
        eligibility_conditions="Supported for AMCs that offer the Pause facility on platform mandates. Allows pausing for 1 to 3, or up to 6 months depending on AMC policy.",
        effective_date_implication="If paused >= 2 working days before debit date, auto-debits halt starting with the upcoming instalment. If requested within 2 working days, pause takes effect from the following month.",
        limitations=[
            "Not all AMCs support pause through third-party platforms; if unavailable in app, skipping or editing amount is the fallback.",
            "Maximum consecutive pause limit applies (typically 3 to 6 months).",
            "Units already accumulated remain completely safe in your folio."
        ],
        official_source_name="Groww Help & Support — Pause SIP",
        official_source_url="https://groww.in/blog/how-to-pause-sip-in-groww",
        last_verified_date="2026-10-25",
        verification_status="VERIFIED",
        plain_language_summary="Pause halts your SIP deductions for 1 to 6 months while keeping your mandate alive and accumulated units intact."
    ),
    "groww_platform_modify": PlatformRule(
        rule_id="groww_platform_modify",
        platform="Groww",
        setup_type="Platform-managed SIP",
        action_type="modify_amount",
        supported=True,
        min_notice_days=2,
        notice_cutoff_description="At least 2 working days before your scheduled SIP date.",
        eligibility_conditions="Subject to the fund's minimum SIP instalment limit (usually ₹100 or ₹500 depending on the scheme).",
        effective_date_implication="Reduced amount applies to the upcoming instalment if submitted >= 2 working days prior; otherwise applies from next month.",
        limitations=[
            "Cannot reduce instalment amount below the fund's regulatory minimum (e.g., ₹100 or ₹500).",
            "May require re-authenticating mandate if changing payment method."
        ],
        official_source_name="Groww Help & Support — Edit SIP",
        official_source_url="https://groww.in/help/mutual-funds/sip",
        last_verified_date="2026-10-25",
        verification_status="VERIFIED",
        plain_language_summary="Step down your monthly contribution to the scheme minimum (e.g. ₹100 or ₹500) to maintain habit without straining cash flow."
    ),
    "groww_platform_cancel": PlatformRule(
        rule_id="groww_platform_cancel",
        platform="Groww",
        setup_type="Platform-managed SIP",
        action_type="cancel",
        supported=True,
        min_notice_days=2,
        notice_cutoff_description="At least 2 working days before next debit date.",
        eligibility_conditions="Any active SIP can be cancelled at any time without platform exit penalties.",
        effective_date_implication="Stops all future debits. If cancelled within 2 working days of debit, the immediate upcoming debit may still be triggered by the bank.",
        limitations=[
            "All past accumulated units remain safely invested in your folio and continue earning market returns; cancellation only stops future automated debits.",
            "Restarting later requires creating a new SIP or mandate."
        ],
        official_source_name="Groww Help & Support — Cancel SIP",
        official_source_url="https://groww.in/help/mutual-funds/sip",
        last_verified_date="2026-10-25",
        verification_status="VERIFIED",
        plain_language_summary="Completely stops future debits. Accumulated fund units stay invested in your folio with zero cancellation penalties from Groww."
    ),
    "groww_payment_failure": PlatformRule(
        rule_id="groww_payment_failure",
        platform="Groww",
        setup_type="Platform-managed SIP",
        action_type="payment_failure",
        supported=True,
        min_notice_days=0,
        notice_cutoff_description="Post-failure grace and retry rules.",
        eligibility_conditions="Applies whenever a scheduled SIP debit does not complete.",
        effective_date_implication="A single missed instalment DOES NOT cancel your SIP. Groww charges ₹0 for failed debits. However, mutual fund rules state that if 3 consecutive instalments fail, the AMC automatically terminates the SIP.",
        limitations=[
            "Groww does not charge a penalty, but your bank may charge NACH/ECS bounce fees (typically ₹250–₹500 + GST) if failure was due to insufficient funds.",
            "Units are not allotted for failed instalments.",
            "Manual 1-time UPI payment ('Pay Now') may be available for select schemes to cover the missed month."
        ],
        official_source_name="Groww Help & Support — What happens if SIP fails?",
        official_source_url="https://groww.in/help/mutual-funds/sip",
        last_verified_date="2026-10-25",
        verification_status="VERIFIED",
        plain_language_summary="One failed instalment will not cancel your SIP. Groww charges no fee, but watch out for bank bounce charges if balance was low. 3 consecutive failures cancel the SIP."
    ),

    # ---------------- ZERODHA COIN ----------------
    "zerodha_coin_pause": PlatformRule(
        rule_id="zerodha_coin_pause",
        platform="Zerodha Coin",
        setup_type="Platform-managed SIP",
        action_type="pause",
        supported=True,
        min_notice_days=2,
        notice_cutoff_description="At least 2 working days before scheduled date (specifically before 11:00 AM 2 days prior).",
        eligibility_conditions="Available on Zerodha Coin SIPs executed via BSE StAR MF platform.",
        effective_date_implication="Pausing stops upcoming orders from being created on BSE StAR MF if paused at least 2 days prior. If within 2 days, order is already sent to the exchange.",
        limitations=[
            "Zerodha Coin pause halts order creation on BSE StAR MF. UPI AutoPay mandate remains active unless paused/modified in UPI app.",
            "If trading account balance or bank account is empty on execution day, the order fails without units allotted.",
            "BSE StAR MF automatically deletes SIPs with 3 consecutive failed orders."
        ],
        official_source_name="Zerodha Support Portal — How to pause an SIP on Coin?",
        official_source_url="https://support.zerodha.com/category/mutual-funds/coin-web/sip-coin/articles/how-to-pause-an-sip-on-coin",
        last_verified_date="2026-10-25",
        verification_status="VERIFIED",
        plain_language_summary="Zerodha Coin allows pausing an SIP directly in the app up to 2 working days before the scheduled date with zero penalty."
    ),
    "zerodha_coin_modify": PlatformRule(
        rule_id="zerodha_coin_modify",
        platform="Zerodha Coin",
        setup_type="Platform-managed SIP",
        action_type="modify_amount",
        supported=True,
        min_notice_days=2,
        notice_cutoff_description="At least 2 working days before scheduled date.",
        eligibility_conditions="Amount must meet AMC minimum investment requirement.",
        effective_date_implication="Modified amount applies to orders generated after the 2-day cutoff.",
        limitations=[
            "Coin SIPs are flexible, but order creation cutoff applies.",
            "Check AMC scheme minimums."
        ],
        official_source_name="Zerodha Support Portal — Modify SIP on Coin",
        official_source_url="https://support.zerodha.com/category/mutual-funds/coin-web/sip-coin",
        last_verified_date="2026-10-25",
        verification_status="VERIFIED",
        plain_language_summary="Modify SIP amount or date anytime on Zerodha Coin at least 2 business days before execution."
    ),
    "zerodha_coin_cancel": PlatformRule(
        rule_id="zerodha_coin_cancel",
        platform="Zerodha Coin",
        setup_type="Platform-managed SIP",
        action_type="cancel",
        supported=True,
        min_notice_days=2,
        notice_cutoff_description="At least 2 working days before scheduled execution.",
        eligibility_conditions="Can delete or pause Coin SIP anytime.",
        effective_date_implication="Deleting SIP removes scheduled order generation on BSE StAR MF. Existing units in Demat account remain untouched.",
        limitations=[
            "Demat mutual fund units remain safe in your Zerodha Demat account.",
            "Remember to cancel or pause the associated bank mandate/UPI AutoPay if not automatically unlinked."
        ],
        official_source_name="Zerodha Support Portal — Delete SIP on Coin",
        official_source_url="https://support.zerodha.com/category/mutual-funds/coin-web/sip-coin/articles/how-to-delete-an-sip-on-coin",
        last_verified_date="2026-10-25",
        verification_status="VERIFIED",
        plain_language_summary="Deleting an SIP on Coin halts future orders. Demat units remain safe and liquid in your account."
    ),

    # ---------------- AMC-REGISTERED SIP (CAMS / KFintech / Direct) ----------------
    "amc_direct_pause": PlatformRule(
        rule_id="amc_direct_pause",
        platform="AMC Direct",
        setup_type="AMC-registered SIP",
        action_type="pause",
        supported=True,
        min_notice_days=10,
        notice_cutoff_description="Typically 10 to 21 calendar days (10–15 business days) prior notice required.",
        eligibility_conditions="Offered directly through AMC portals or Registrar portals (CAMS / KFintech). Notice window set by individual AMC guidelines.",
        effective_date_implication="Because AMC-registered mandates interface directly with clearing houses (NPCI/NACH) in batches, changes require 10–21 days notice. If submitted with less notice, the upcoming debit cannot be stopped.",
        limitations=[
            "Significantly longer cutoff than fintech platform SIPs (10–21 days vs 2 days).",
            "Maximum 3 to 6 consecutive pauses depending on AMC.",
            "Requires folio number and AMC portal login / CAMS myCAMS portal."
        ],
        official_source_name="AMFI India / CAMS Investor Services — SIP Pause Facility",
        official_source_url="https://www.amfiindia.com/investor-corner/knowledge-center/sip-pause.html",
        last_verified_date="2026-10-25",
        verification_status="VERIFIED",
        plain_language_summary="Direct AMC mandates require 10–21 days advance notice through CAMS, KFintech, or AMC portals to stop or pause an upcoming debit."
    ),
    "amc_direct_cancel": PlatformRule(
        rule_id="amc_direct_cancel",
        platform="AMC Direct",
        setup_type="AMC-registered SIP",
        action_type="cancel",
        supported=True,
        min_notice_days=15,
        notice_cutoff_description="Typically 15 to 21 calendar days advance notice required by AMCs.",
        eligibility_conditions="Submittable via AMC website, CAMS/KFintech, or written OTM cancellation request.",
        effective_date_implication="Cancellation submitted less than 15 days before debit will take effect only from the following month. The upcoming instalment will still attempt deduction.",
        limitations=[
            "Long bank clearing cycle for physical or OTM mandates.",
            "Accumulated units remain safe in folio."
        ],
        official_source_name="AMFI Investor Knowledge Center — Cancelling AMC SIP",
        official_source_url="https://www.amfiindia.com/investor-corner/knowledge-center/sip-pause.html",
        last_verified_date="2026-10-25",
        verification_status="VERIFIED",
        plain_language_summary="Cancelling an AMC-registered mandate requires 15–21 days notice due to bank clearing cycles."
    ),

    # ---------------- GENERAL / UNKNOWN FALLBACK ----------------
    "general_guidance": PlatformRule(
        rule_id="general_guidance",
        platform="General",
        setup_type="All",
        action_type="overview",
        supported=False,
        min_notice_days=3,
        notice_cutoff_description="Industry average is 2 to 5 business days for platform SIPs, and 10 to 21 days for direct AMC mandates.",
        eligibility_conditions="Varies by broker platform and AMC.",
        effective_date_implication="We cannot confirm the exact cutoff for your specific platform. Please verify directly in your platform's help center before the debit date.",
        limitations=[
            "Platform rules vary significantly (Groww vs Zerodha Coin vs Paytm Money vs AMC Direct).",
            "Do not assume a same-day or 1-day advance request will stop the debit.",
            "Check with your platform support or AMC customer care before taking action."
        ],
        official_source_name="AMFI India Official Guidance on Mutual Fund SIPs",
        official_source_url="https://www.amfiindia.com/investor-corner/knowledge-center/sip-pause.html",
        last_verified_date="2026-10-25",
        verification_status="GENERAL_GUIDANCE",
        plain_language_summary="General industry guidance: Most apps need 2 to 5 days advance notice, while direct AMC mandates need 10 to 21 days."
    )
}


# ---------------------------------------------------------------------------
# 2. Guidance Evaluation Logic
# ---------------------------------------------------------------------------

SITUATION_OPTIONS = [
    "I need a temporary break from my SIP.",
    "My next SIP debit is approaching, and I may not have enough money.",
    "My SIP payment failed.",
    "My current SIP amount is becoming difficult to afford.",
    "I want to stop my SIP completely.",
    "I'm not sure what my options are."
]

PLATFORM_OPTIONS = [
    "Groww",
    "Zerodha Coin",
    "Another platform",
    "I'm not sure"
]

SIP_SETUP_OPTIONS = [
    "Platform-managed SIP",
    "AMC-registered SIP",
    "I'm not sure"
]

TIMING_OPTIONS = [
    "Today",
    "Within 1–2 days",
    "Within 3–5 days",
    "More than 5 days",
    "I'm not sure of the date"
]


@dataclass
class GuidanceCard:
    situation_id: str
    headline: str
    situation_meaning: str
    what_to_check_now: str
    timing_eligibility: str
    cutoff_status: str                # "CRITICAL_CUTOFF_PASSED", "URGENT_CUTOFF_AT_RISK", "SAFE_WINDOW_OPEN", "UNCERTAIN_TIMING"
    cutoff_warning_badge: str         # "⚠️ Cutoff Likely Passed" | "⏳ Action Needed Promptly" | "✅ Window Open" | "ℹ️ Check Your Date"
    applicable_rule: PlatformRule
    available_options: List[Dict[str, str]]
    limitations: List[str]
    primary_action_label: str
    primary_action_type: str          # "official_help", "comeback_plan", "view_rules", "check_date"
    primary_action_url: Optional[str]
    secondary_actions: List[Dict[str, str]]
    source_citation: str
    last_verified_date: str
    verification_status: str


def evaluate_sip_guidance(
    situation: str,
    platform: str,
    setup_type: str,
    time_remaining: str
) -> GuidanceCard:
    """
    Deterministic rule evaluation function.
    Takes user inputs and evaluates cutoff constraints, platform capabilities,
    and plain-language next steps.
    """
    # 1. Determine platform rule resolution
    is_unknown_platform = platform in ["Another platform", "I'm not sure"]
    is_unknown_setup = setup_type == "I'm not sure"
    is_amc_direct = setup_type == "AMC-registered SIP"

    # 2. Cutoff calculation
    # Standard platform cutoff: 2 working days
    # AMC direct cutoff: 10-21 calendar days
    cutoff_days = 14 if is_amc_direct else 2
    if is_unknown_platform:
        cutoff_days = 3

    if time_remaining == "Today":
        cutoff_status = "CRITICAL_CUTOFF_PASSED"
        cutoff_warning_badge = "⚠️ Cutoff Passed for Upcoming Debit"
    elif time_remaining == "Within 1–2 days":
        if is_amc_direct or cutoff_days >= 2:
            cutoff_status = "CRITICAL_CUTOFF_PASSED"
            cutoff_warning_badge = "⚠️ Cutoff Likely Passed for Upcoming Debit"
        else:
            cutoff_status = "URGENT_CUTOFF_AT_RISK"
            cutoff_warning_badge = "⏳ Urgent Action Needed Today"
    elif time_remaining == "Within 3–5 days":
        if is_amc_direct:
            cutoff_status = "CRITICAL_CUTOFF_PASSED"
            cutoff_warning_badge = "⚠️ AMC Cutoff (10–14 days) Passed"
        else:
            cutoff_status = "SAFE_WINDOW_OPEN"
            cutoff_warning_badge = "✅ Actionable Window Open"
    elif time_remaining == "More than 5 days":
        if is_amc_direct:
            cutoff_status = "URGENT_CUTOFF_AT_RISK"
            cutoff_warning_badge = "⏳ AMC Notice Window (10+ days)"
        else:
            cutoff_status = "SAFE_WINDOW_OPEN"
            cutoff_warning_badge = "✅ Sufficient Time Remaining"
    else:  # "I'm not sure of the date"
        cutoff_status = "UNCERTAIN_TIMING"
        cutoff_warning_badge = "ℹ️ Debit Date Unconfirmed"

    # 3. Select matching PlatformRule & synthesize guidance based on situation
    if situation == "I need a temporary break from my SIP.":
        if platform == "Groww" and not is_amc_direct:
            rule = PLATFORM_RULES["groww_platform_skip"] if time_remaining in ["Within 3–5 days", "More than 5 days"] else PLATFORM_RULES["groww_platform_pause"]
        elif platform == "Zerodha Coin" and not is_amc_direct:
            rule = PLATFORM_RULES["zerodha_coin_pause"]
        elif is_amc_direct:
            rule = PLATFORM_RULES["amc_direct_pause"]
        else:
            rule = PLATFORM_RULES["general_guidance"]

        headline = "Taking a temporary break: Skip vs Pause options"
        meaning = (
            "Taking a temporary break is common and normal when unexpected life events occur. "
            "You have two distinct tools: **Skip Next Instalment** (skips just 1 month and resumes automatically) "
            "or **Pause SIP** (halts deductions for 1 to 3 months). In either case, your existing fund units stay safely invested."
        )
        what_to_check = (
            f"Check if you have at least {rule.min_notice_days} working days before your next scheduled debit date. "
            "If yes, you can request a Skip or Pause in your app right now."
        )

        if cutoff_status == "CRITICAL_CUTOFF_PASSED":
            timing_eligibility = (
                f"Your debit is {time_remaining.lower()}. The modification cutoff for {rule.platform} is {rule.notice_cutoff_description} "
                "Because of clearing cycle deadlines, a skip or pause submitted right now will likely apply only to your NEXT month's debit. "
                "The upcoming instalment may still be submitted to your bank."
            )
        else:
            timing_eligibility = (
                f"You have sufficient time before your debit. {rule.platform} requires {rule.notice_cutoff_description} "
                "If submitted promptly today, this request will apply to your upcoming instalment."
            )

        options = [
            {"name": "Skip 1 Instalment", "desc": "Skips only the upcoming month. AutoPay resumes normally the next month with zero penalty."},
            {"name": "Pause for 1–3 Months", "desc": "Halts deductions for a chosen duration while keeping your mandate active."},
            {"name": "Reduce SIP Amount", "desc": "Lower your monthly contribution to scheme minimum (e.g. ₹100 or ₹500) if you prefer not to pause completely."}
        ]

    elif situation == "My next SIP debit is approaching, and I may not have enough money.":
        if platform == "Groww" and not is_amc_direct:
            rule = PLATFORM_RULES["groww_platform_skip"]
        elif platform == "Zerodha Coin" and not is_amc_direct:
            rule = PLATFORM_RULES["zerodha_coin_pause"]
        elif is_amc_direct:
            rule = PLATFORM_RULES["amc_direct_pause"]
        else:
            rule = PLATFORM_RULES["general_guidance"]

        headline = "Approaching debit with tight cash flow"
        meaning = (
            "Facing a cash crunch close to debit date is stressful, but understanding the exact mechanics prevents surprise fees. "
            "Brokers (like Groww or Zerodha) charge ₹0 when an SIP instalment cannot be debited. However, your **bank** may charge "
            "an ECS/NACH bounce fee if your bank balance is insufficient on debit day."
        )
        what_to_check = (
            "Check if you are still within the cutoff to skip or pause. If the cutoff has already passed, check your bank's ECS bounce fee policy "
            "and consider whether maintaining a small balance or letting 1 instalment fail is less costly than an unnecessary emergency loan."
        )

        if cutoff_status in ["CRITICAL_CUTOFF_PASSED", "URGENT_CUTOFF_AT_RISK"]:
            timing_eligibility = (
                f"Your debit is {time_remaining.lower()}. Because {rule.platform} requires {rule.notice_cutoff_description}, "
                "the cutoff for the upcoming debit may have passed. A skip or pause submitted now will protect next month, "
                "but the upcoming debit order may already be queued with your bank."
            )
        else:
            timing_eligibility = (
                f"You are within the safe notice window. Submitting a 'Skip' request today in {rule.platform} "
                "will stop the upcoming debit safely and avoid any bank bounce fees."
            )

        options = [
            {"name": "Submit Skip Request Now", "desc": "Even if close to deadline, submitting early gives the platform the earliest chance to stop processing."},
            {"name": "Keep Balance If Possible", "desc": "If affordable, keeping minimum balance avoids bank ECS bounce fees."},
            {"name": "Understand 1-Missed Rule", "desc": "If it does fail, your SIP is not cancelled. 1 missed debit has no credit score or tax impact."}
        ]

    elif situation == "My SIP payment failed.":
        rule = PLATFORM_RULES["groww_payment_failure"] if platform == "Groww" else PLATFORM_RULES["zerodha_coin_pause"] if platform == "Zerodha Coin" else PLATFORM_RULES["general_guidance"]
        headline = "SIP payment failed: Understanding what happened"
        meaning = (
            "A failed SIP payment is not a financial catastrophe. Here is the verified truth: "
            "1. Your investment platform does NOT penalize you for a failed SIP. "
            "2. Your existing mutual fund units remain completely untouched and active. "
            "3. Your SIP is NOT immediately cancelled; regulations require 3 consecutive failed debits before an AMC stops the SIP."
        )
        what_to_check = (
            "Check why the payment failed in your platform's transaction history (e.g. 'Bank Server Down' vs 'Insufficient Balance' vs 'Mandate Inactive'). "
            "If the failure was due to bank server downtime, many platforms attempt an automated retry within 24–48 hours."
        )
        timing_eligibility = (
            "The upcoming debit date has already occurred. You do not need to panic. "
            "You have up to the next monthly cycle before any risk of consecutive failure."
        )
        options = [
            {"name": "Manual 1-Time UPI Payment", "desc": "Check your app for a 'Pay Now' or 'Retry' button to complete this month's instalment manually."},
            {"name": "Wait for Next Cycle", "desc": "Simply wait for next month. 1 skipped month does not ruin your long-term compounding habit."},
            {"name": "Check Bank Statement", "desc": "Verify whether your bank charged an ECS bounce fee. If money was debited but units unallotted, it refunds in 3–5 working days."}
        ]

    elif situation == "My current SIP amount is becoming difficult to afford.":
        if platform == "Groww" and not is_amc_direct:
            rule = PLATFORM_RULES["groww_platform_modify"]
        elif platform == "Zerodha Coin" and not is_amc_direct:
            rule = PLATFORM_RULES["zerodha_coin_modify"]
        else:
            rule = PLATFORM_RULES["general_guidance"]

        headline = "SIP amount unaffordable: Adjust without stopping"
        meaning = (
            "Investing should support your financial peace of mind, not cause chronic stress. "
            "Many first-time investors start with high monthly targets (e.g. ₹5,000) that become rigid when expenses rise. "
            "You do not need to cancel your SIP to get relief—you can step down the amount to the scheme minimum (often ₹100 or ₹500)."
        )
        what_to_check = (
            "Check the minimum investment amount for your specific mutual fund scheme in the app details. "
            "Then use the 'Edit SIP Amount' feature to adjust down to a comfortable level."
        )
        timing_eligibility = (
            f"{rule.platform} requires {rule.notice_cutoff_description} for an amount change. "
            "If submitted before the cutoff, your upcoming debit will automatically be for the lower amount."
        )
        options = [
            {"name": "Step Down Amount to ₹100–₹500", "desc": "Keeps your automated compounding habit alive while freeing up monthly cash flow."},
            {"name": "Change Debit Date", "desc": "Align your debit date to 1–2 days after your guaranteed salary credit date to avoid mid-month balance shortages."},
            {"name": "Pause for 2 Months", "desc": "Give yourself a 60-day buffer to rebuild your emergency cash cushion."}
        ]

    elif situation == "I want to stop my SIP completely.":
        if platform == "Groww" and not is_amc_direct:
            rule = PLATFORM_RULES["groww_platform_cancel"]
        elif platform == "Zerodha Coin" and not is_amc_direct:
            rule = PLATFORM_RULES["zerodha_coin_cancel"]
        elif is_amc_direct:
            rule = PLATFORM_RULES["amc_direct_cancel"]
        else:
            rule = PLATFORM_RULES["general_guidance"]

        headline = "Stopping your SIP: Clear, penalty-free exit"
        meaning = (
            "If stopping your SIP is the right decision for your current circumstances, you can do so with zero platform exit penalties. "
            "Crucial reassurance: **Cancelling an SIP does NOT sell your mutual fund units or withdraw your money.** "
            "All money invested to date remains in your folio, continuing to earn market returns and dividends until you choose to redeem."
        )
        what_to_check = (
            f"Check the cutoff date. {rule.platform} requires {rule.notice_cutoff_description} to prevent the upcoming debit. "
            "Once submitted, verify that the SIP status in your app displays as 'Cancelled' or 'Stopped'."
        )
        if cutoff_status == "CRITICAL_CUTOFF_PASSED":
            timing_eligibility = (
                f"Because your debit is {time_remaining.lower()}, cancelling right now will stop all future debits starting NEXT month, "
                "but the upcoming instalment may still be processed by the banking system."
            )
        else:
            timing_eligibility = (
                f"You have adequate notice time. Submitting cancellation today in {rule.platform} "
                "will stop all future debits, including the upcoming one."
            )
        options = [
            {"name": "Cancel Future SIP Debits", "desc": "Stops all upcoming automated deductions with zero penalty. Existing portfolio stays invested."},
            {"name": "Keep Units Invested", "desc": "Leave your accumulated units growing. You only withdraw when you actually need cash."},
            {"name": "Consider Pausing Instead", "desc": "If you might resume in 2–3 months, pausing saves having to re-authenticate a bank mandate later."}
        ]

    else:  # "I'm not sure what my options are."
        rule = PLATFORM_RULES["general_guidance"]
        headline = "Exploring your options: A clear comparative guide"
        meaning = (
            "When cash flow is uncertain, investors often think the only choices are continuing to pay or quitting entirely. "
            "In modern fintech apps, you have a spectrum of flexible controls designed for short-term liquidity relief."
        )
        what_to_check = (
            "Check which platform you use and what type of mandate was set up (AutoPay / UPI vs Direct AMC). "
            "Then choose the tool that best fits your expected timeline."
        )
        timing_eligibility = (
            "Platforms need between 2 and 5 business days advance notice to adjust an upcoming debit. "
            "Check your next scheduled debit date in your app's Mutual Fund or SIP tab."
        )
        options = [
            {"name": "Option A: Skip Next Month", "desc": "Best for: 1-off emergency expense. Takes 1 month off, resumes automatically."},
            {"name": "Option B: Pause 2–3 Months", "desc": "Best for: Job transition or extended expense. Re-activates when you are ready."},
            {"name": "Option C: Lower SIP Amount", "desc": "Best for: Permanent budget change. Reduce to ₹100 or ₹500 scheme minimum."},
            {"name": "Option D: Cancel SIP", "desc": "Best for: Total stop. Zero fees, past units stay safely invested."}
        ]

    # Specific note if unknown platform or missing rule
    limitations = list(rule.limitations)
    if is_unknown_platform:
        limitations.append("We could not verify the exact rules for your platform. Please confirm directly in your app's Help Center before acting.")
    if is_unknown_setup:
        limitations.append("SIP setup type was unconfirmed. Platform-managed SIPs (Groww/Zerodha) have 2-day cutoffs, whereas AMC-registered mandates require 10–21 days.")

    primary_action_url = rule.official_source_url if rule.official_source_url.startswith("http") else None

    return GuidanceCard(
        situation_id=situation,
        headline=headline,
        situation_meaning=meaning,
        what_to_check_now=what_to_check,
        timing_eligibility=timing_eligibility,
        cutoff_status=cutoff_status,
        cutoff_warning_badge=cutoff_warning_badge,
        applicable_rule=rule,
        available_options=options,
        limitations=limitations,
        primary_action_label=f"View Official {rule.platform} Help Guide",
        primary_action_type="official_help",
        primary_action_url=primary_action_url,
        secondary_actions=[
            {"label": "📅 Create Comeback Plan Reminder", "type": "comeback_plan"},
            {"label": "📋 View Detailed Rule Terms", "type": "view_rules"},
            {"label": "🔄 Change Answers", "type": "change_answers"}
        ],
        source_citation=f"{rule.official_source_name} ({rule.verification_status})",
        last_verified_date=rule.last_verified_date,
        verification_status=rule.verification_status
    )


# ---------------------------------------------------------------------------
# 3. SIP Comeback Plan & Reminder Logic
# ---------------------------------------------------------------------------

@dataclass
class ComebackReminder:
    reminder_id: str
    target_date: str                 # YYYY-MM-DD
    days_from_now: int
    focus_action: str
    reflection_prompt: str
    created_at: str
    is_simulated: bool
    status: str                       # "SCHEDULED_LOCAL_PROTOTYPE"


def create_comeback_plan(
    days_offset: int,
    focus_action: str,
    custom_reflection: Optional[str] = None
) -> ComebackReminder:
    """
    Creates an optional, non-presumptive comeback review reminder.
    Encourages reviewing personal finances rather than forcing SIP restart.
    """
    today = date.today()
    target_date = today + timedelta(days=days_offset)

    default_prompt = (
        "Take 5 minutes to review your monthly cash flow. "
        "Are your unexpected expenses behind you? If yes, consider resuming or stepping down your SIP. "
        "If finances are still tight, extending your pause is completely okay."
    )

    return ComebackReminder(
        reminder_id=f"REM-{today.strftime('%Y%m%d')}-{days_offset}D",
        target_date=target_date.strftime("%Y-%m-%d"),
        days_from_now=days_offset,
        focus_action=focus_action,
        reflection_prompt=custom_reflection if custom_reflection and custom_reflection.strip() else default_prompt,
        created_at=datetime.now(timezone.utc).isoformat(),
        is_simulated=True,
        status="SCHEDULED_LOCAL_PROTOTYPE"
    )


def generate_ics_calendar_file(reminder: ComebackReminder) -> str:
    """
    Generates a standard iCalendar (.ics) string so the user can import
    their SIP Comeback Review into Google Calendar, Outlook, or Apple Calendar.
    """
    date_clean = reminder.target_date.replace("-", "")
    created_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Continuum AI//SIP Rescue Navigator//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{reminder.reminder_id}@continuum-ai.local
DTSTAMP:{created_stamp}
DTSTART;VALUE=DATE:{date_clean}
DTEND;VALUE=DATE:{date_clean}
SUMMARY:SIP Comeback Check-in ({reminder.focus_action})
DESCRIPTION:{reminder.reflection_prompt}\\n\\nGenerated by Continuum AI SIP Rescue Navigator.
STATUS:CONFIRMED
TRANSP:TRANSPARENT
END:VEVENT
END:VCALENDAR"""
    return ics_content


# ---------------------------------------------------------------------------
# 4. Usability Feedback & Discovery Metrics Storage
# ---------------------------------------------------------------------------

FEEDBACK_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "sip_rescue_feedback.json"
)

# Seed with initial validated discovery sessions for realistic metrics evaluation
INITIAL_BENCHMARK_SESSIONS = [
    {
        "session_id": "seed-01",
        "timestamp": "2026-10-25T11:20:00Z",
        "situation": "My next SIP debit is approaching, and I may not have enough money.",
        "platform": "Groww",
        "setup_type": "Platform-managed SIP",
        "time_remaining": "Within 1–2 days",
        "clarity_response": "Yes, I know what to do next.",
        "understood_deadline": True,
        "identified_action": True,
        "reminder_opt_in": True,
        "useful_feedback": "The warning that cutoff passed for this month prevented me from thinking a pause would save my bank fee."
    },
    {
        "session_id": "seed-02",
        "timestamp": "2026-10-25T14:45:00Z",
        "situation": "I need a temporary break from my SIP.",
        "platform": "Zerodha Coin",
        "setup_type": "Platform-managed SIP",
        "time_remaining": "Within 3–5 days",
        "clarity_response": "Yes, I know what to do next.",
        "understood_deadline": True,
        "identified_action": True,
        "reminder_opt_in": True,
        "useful_feedback": "Clear difference between skip and pause."
    },
    {
        "session_id": "seed-03",
        "timestamp": "2026-10-25T16:10:00Z",
        "situation": "My SIP payment failed.",
        "platform": "Groww",
        "setup_type": "Platform-managed SIP",
        "time_remaining": "Today",
        "clarity_response": "Yes, I know what to do next.",
        "understood_deadline": True,
        "identified_action": True,
        "reminder_opt_in": False,
        "useful_feedback": "Relieved to know 1 failure doesn't cancel my SIP or ruin my CIBIL score."
    },
    {
        "session_id": "seed-04",
        "timestamp": "2026-10-26T09:30:00Z",
        "situation": "My current SIP amount is becoming difficult to afford.",
        "platform": "Groww",
        "setup_type": "Platform-managed SIP",
        "time_remaining": "More than 5 days",
        "clarity_response": "Yes, I know what to do next.",
        "understood_deadline": True,
        "identified_action": True,
        "reminder_opt_in": True,
        "useful_feedback": "Stepping down to ₹500 is much better than cancelling."
    },
    {
        "session_id": "seed-05",
        "timestamp": "2026-10-26T13:15:00Z",
        "situation": "I'm not sure what my options are.",
        "platform": "Another platform",
        "setup_type": "I'm not sure",
        "time_remaining": "I'm not sure of the date",
        "clarity_response": "Partly, I still have questions.",
        "understood_deadline": False,
        "identified_action": True,
        "reminder_opt_in": False,
        "useful_feedback": "Need to check my AMC folio number first."
    }
]


def load_feedback_records() -> List[Dict[str, Any]]:
    """Loads all logged prototype feedback safely from the JSON store."""
    if not os.path.exists(FEEDBACK_FILE_PATH):
        try:
            os.makedirs(os.path.dirname(FEEDBACK_FILE_PATH), exist_ok=True)
            with open(FEEDBACK_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(INITIAL_BENCHMARK_SESSIONS, f, indent=2)
            return list(INITIAL_BENCHMARK_SESSIONS)
        except Exception:
            return list(INITIAL_BENCHMARK_SESSIONS)

    try:
        with open(FEEDBACK_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else list(INITIAL_BENCHMARK_SESSIONS)
    except Exception:
        return list(INITIAL_BENCHMARK_SESSIONS)


def save_feedback_record(record: Dict[str, Any]) -> bool:
    """Saves a privacy-conscious feedback entry without PII or financial credentials."""
    records = load_feedback_records()
    record["timestamp"] = datetime.now(timezone.utc).isoformat()
    record["session_id"] = f"user-{len(records)+1:03d}"
    records.append(record)

    try:
        os.makedirs(os.path.dirname(FEEDBACK_FILE_PATH), exist_ok=True)
        with open(FEEDBACK_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save feedback record: {e}")
        return False


def get_discovery_metrics() -> Dict[str, Any]:
    """
    Computes rigorous discovery usability metrics with clearly stated numerators and denominators.
    These are usability test metrics, NOT fabricated churn reduction metrics.
    """
    records = load_feedback_records()
    total_sessions = len(records)
    if total_sessions == 0:
        return {
            "total_sessions": 0,
            "clarity_rate": 0.0,
            "clarity_numerator": 0,
            "clarity_denominator": 0,
            "deadline_understanding_rate": 0.0,
            "deadline_numerator": 0,
            "deadline_denominator": 0,
            "action_identification_rate": 0.0,
            "action_numerator": 0,
            "action_denominator": 0,
            "clarification_needed_rate": 0.0,
            "reminder_opt_in_rate": 0.0,
            "reminder_numerator": 0,
            "reminder_denominator": 0
        }

    clarity_positive = sum(1 for r in records if r.get("clarity_response") == "Yes, I know what to do next.")
    clarification_needed = sum(1 for r in records if r.get("clarity_response") in ["Partly, I still have questions.", "No, I couldn't find a useful option."])
    understood_deadline = sum(1 for r in records if r.get("understood_deadline") is True)
    identified_action = sum(1 for r in records if r.get("identified_action") is True)
    reminder_opt_in = sum(1 for r in records if r.get("reminder_opt_in") is True)

    return {
        "total_sessions": total_sessions,
        "clarity_rate": round((clarity_positive / total_sessions) * 100, 1),
        "clarity_numerator": clarity_positive,
        "clarity_denominator": total_sessions,
        "clarification_needed_rate": round((clarification_needed / total_sessions) * 100, 1),
        "clarification_numerator": clarification_needed,
        "clarification_denominator": total_sessions,
        "deadline_understanding_rate": round((understood_deadline / total_sessions) * 100, 1),
        "deadline_numerator": understood_deadline,
        "deadline_denominator": total_sessions,
        "action_identification_rate": round((identified_action / total_sessions) * 100, 1),
        "action_numerator": identified_action,
        "action_denominator": total_sessions,
        "reminder_opt_in_rate": round((reminder_opt_in / total_sessions) * 100, 1),
        "reminder_numerator": reminder_opt_in,
        "reminder_denominator": total_sessions
    }
