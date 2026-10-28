/**
 * sip-rescue-mvp/js/data/rulesConfig.js
 * 
 * Deterministic Rules Repository & Guidance Logic for SIP Rescue Navigator.
 * Separates verified platform rules from general informational guidance and unverified fallbacks.
 * 
 * All official URLs, cutoffs, and verification dates are explicitly declared.
 */

export const VERIFIED_RULES = {
  GROWW: {
    sourceUrl: "https://groww.in/help/mutual-funds/sip",
    name: "Groww Help & Support — SIP Rules"
  },
  ZERODHA: {
    sourceUrl: "https://support.zerodha.com/category/mutual-funds/coin-web/sip-coin/articles/how-to-pause-my-sip-on-coin",
    name: "Zerodha Coin Support — SIP Rules"
  },
  AMC_DIRECT: {
    sourceUrl: "https://www.amfiindia.com/investor-corner/knowledge-center/systematic-investment-plan.html",
    name: "AMFI India Investor Guidelines"
  }
};

export const PLATFORM_RULES = {
  // --- GROWW PLATFORM ---
  groww_skip: {
    ruleId: "groww_skip",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    actionType: "skip",
    supported: true,
    minNoticeDays: 2,
    noticeCutoffDescription: "At least 2 working days before your scheduled SIP debit date.",
    eligibilityConditions: "Available on active Groww AutoPay (e-Mandate / UPI Autopay) SIPs for eligible mutual fund schemes.",
    effectiveDateImplication: "If submitted >= 2 working days before debit date, the upcoming instalment is skipped with ₹0 fee. If submitted within 2 working days, the skip request applies only to the following month.",
    limitations: [
      "Cannot be processed within 2 working days of scheduled debit date.",
      "Maximum 1 instalment skipped per request; consecutive skips typically require a Pause request.",
      "If your bank account has insufficient balance and the cutoff has passed, your bank may charge ECS bounce fees (typically ₹250–₹500 + GST); Groww itself charges ₹0.",
      "This application cannot access your live Groww account or confirm your bank balance."
    ],
    officialSourceName: "Groww Help & Support — Skip SIP Instalment",
    officialSourceUrl: "https://groww.in/help/mutual-funds/sip",
    lastVerifiedDate: "2026-10-25",
    verificationStatus: "VERIFIED",
    plainLanguageSummary: "You can skip your upcoming instalment on Groww with zero platform penalty, provided you submit the request at least 2 working days before your debit date."
  },

  groww_pause: {
    ruleId: "groww_pause",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    actionType: "pause",
    supported: true,
    minNoticeDays: 2,
    noticeCutoffDescription: "At least 2 working days before your next SIP date.",
    eligibilityConditions: "Supported for AMCs that offer the Pause facility on platform mandates. Allows pausing for 1 to 3, or up to 6 months depending on AMC policy.",
    effectiveDateImplication: "If paused >= 2 working days before debit date, auto-debits halt starting with the upcoming instalment. If requested within 2 working days, pause takes effect from the next month.",
    limitations: [
      "Not all AMCs support pause through third-party platforms; if unavailable in app, skipping or editing amount is the alternative.",
      "Maximum consecutive pause limit applies (typically 3 to 6 months).",
      "Units already accumulated remain completely safe in your folio and continue compounding."
    ],
    officialSourceName: "Groww Help & Support — Pause SIP",
    officialSourceUrl: "https://groww.in/blog/how-to-pause-sip-in-groww",
    lastVerifiedDate: "2026-10-25",
    verificationStatus: "VERIFIED",
    plainLanguageSummary: "Pause halts your SIP deductions for 1 to 6 months while keeping your mandate alive and accumulated units intact."
  },

  groww_modify: {
    ruleId: "groww_modify",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    actionType: "modify_amount",
    supported: true,
    minNoticeDays: 2,
    noticeCutoffDescription: "At least 2 working days before your scheduled SIP date.",
    eligibilityConditions: "Subject to the fund's minimum SIP instalment limit (usually ₹100 or ₹500 depending on scheme).",
    effectiveDateImplication: "Reduced amount applies to the upcoming instalment if submitted >= 2 working days prior; otherwise applies from the subsequent month.",
    limitations: [
      "Cannot reduce instalment amount below the fund's regulatory minimum (e.g., ₹100 or ₹500).",
      "May require re-authenticating mandate if modifying payment details."
    ],
    officialSourceName: "Groww Help & Support — Edit SIP",
    officialSourceUrl: "https://groww.in/help/mutual-funds/sip",
    lastVerifiedDate: "2026-10-25",
    verificationStatus: "VERIFIED",
    plainLanguageSummary: "Step down your monthly contribution to the scheme minimum (e.g. ₹100 or ₹500) to keep your investment habit alive without straining your monthly budget."
  },

  groww_cancel: {
    ruleId: "groww_cancel",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    actionType: "cancel",
    supported: true,
    minNoticeDays: 2,
    noticeCutoffDescription: "At least 2 working days before next debit date.",
    eligibilityConditions: "Any active SIP can be cancelled anytime with zero exit penalty from Groww.",
    effectiveDateImplication: "Stops all future debits. If cancelled within 2 working days of debit, the immediate upcoming debit instruction may already be dispatched to your bank.",
    limitations: [
      "All past accumulated units remain safely invested in your folio and continue earning market returns; cancellation only stops future automated debits.",
      "Restarting later requires creating a new SIP or mandate."
    ],
    officialSourceName: "Groww Help & Support — Cancel SIP",
    officialSourceUrl: "https://groww.in/help/mutual-funds/sip",
    lastVerifiedDate: "2026-10-25",
    verificationStatus: "VERIFIED",
    plainLanguageSummary: "Completely stops future debits. Accumulated fund units stay safely invested in your folio with zero cancellation penalties from Groww."
  },

  groww_payment_failure: {
    ruleId: "groww_payment_failure",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    actionType: "payment_failure",
    supported: true,
    minNoticeDays: 0,
    noticeCutoffDescription: "Immediate post-failure grace period.",
    eligibilityConditions: "Applies whenever a scheduled SIP debit does not complete.",
    effectiveDateImplication: "A single missed instalment DOES NOT cancel your SIP. Groww charges ₹0 for failed debits. Mutual fund regulations state that 3 consecutive failed instalments cause the AMC to terminate the SIP automatically.",
    limitations: [
      "Groww charges ₹0, but your bank may charge ECS/NACH bounce fees (typically ₹250–₹500 + GST) if failure was due to insufficient balance.",
      "Units are not allotted for failed instalments.",
      "Manual 1-time UPI payment ('Pay Now') may be available for select schemes to cover the missed month."
    ],
    officialSourceName: "Groww Help & Support — What happens if SIP fails?",
    officialSourceUrl: "https://groww.in/help/mutual-funds/sip",
    lastVerifiedDate: "2026-10-25",
    verificationStatus: "VERIFIED",
    plainLanguageSummary: "One failed instalment will not cancel your SIP. Groww charges no fee, but watch out for bank bounce fees if balance was low. 3 consecutive failures will terminate the SIP."
  },

  // --- ZERODHA COIN ---
  zerodha_coin_pause: {
    ruleId: "zerodha_coin_pause",
    platform: "Zerodha Coin",
    setupType: "Platform-managed SIP",
    actionType: "pause",
    supported: true,
    minNoticeDays: 2,
    noticeCutoffDescription: "At least 2 working days before scheduled date (specifically before 11:00 AM on T-2 days).",
    eligibilityConditions: "Available on Zerodha Coin SIPs executed via BSE StAR MF exchange.",
    effectiveDateImplication: "Pausing halts order creation on BSE StAR MF if paused at least 2 days prior. If within 2 days, order is already sent to the exchange.",
    limitations: [
      "Zerodha Coin pause halts order creation on BSE StAR MF. UPI AutoPay mandate remains active unless paused/modified in UPI app.",
      "If trading account balance or bank account is empty on execution day, the order fails without units allotted.",
      "BSE StAR MF automatically deletes SIPs with 3 consecutive failed orders."
    ],
    officialSourceName: "Zerodha Support Portal — How to pause an SIP on Coin?",
    officialSourceUrl: "https://support.zerodha.com/category/mutual-funds/coin-web/sip-coin/articles/how-to-pause-an-sip-on-coin",
    lastVerifiedDate: "2026-10-25",
    verificationStatus: "VERIFIED",
    plainLanguageSummary: "Zerodha Coin allows pausing an SIP directly in the app up to 2 working days before the scheduled date with zero penalty."
  },

  zerodha_coin_cancel: {
    ruleId: "zerodha_coin_cancel",
    platform: "Zerodha Coin",
    setupType: "Platform-managed SIP",
    actionType: "cancel",
    supported: true,
    minNoticeDays: 2,
    noticeCutoffDescription: "At least 2 working days before scheduled execution.",
    eligibilityConditions: "Can delete or pause Coin SIP anytime.",
    effectiveDateImplication: "Deleting SIP removes scheduled order generation on BSE StAR MF. Existing units in Demat account remain untouched.",
    limitations: [
      "Demat mutual fund units remain safe in your Zerodha Demat account.",
      "Remember to pause or cancel the associated bank mandate/UPI AutoPay if not automatically unlinked."
    ],
    officialSourceName: "Zerodha Support Portal — Delete SIP on Coin",
    officialSourceUrl: "https://support.zerodha.com/category/mutual-funds/coin-web/sip-coin/articles/how-to-delete-an-sip-on-coin",
    lastVerifiedDate: "2026-10-25",
    verificationStatus: "VERIFIED",
    plainLanguageSummary: "Deleting an SIP on Coin halts future orders. Demat units remain safe and liquid in your account."
  },

  // --- AMC DIRECT / CAMS / KFINTECH ---
  amc_direct_pause: {
    ruleId: "amc_direct_pause",
    platform: "AMC Direct",
    setupType: "AMC-registered SIP",
    actionType: "pause",
    supported: true,
    minNoticeDays: 10,
    noticeCutoffDescription: "Typically 10 to 21 calendar days (10–15 business days) prior notice required.",
    eligibilityConditions: "Offered directly through AMC portals or Registrar portals (CAMS / KFintech). Notice window set by individual AMC guidelines.",
    effectiveDateImplication: "Because AMC-registered mandates interface directly with clearing houses (NPCI/NACH) in batches, changes require 10–21 days notice. If submitted with less notice, the upcoming debit cannot be stopped.",
    limitations: [
      "Significantly longer cutoff than fintech platform SIPs (10–21 days vs 2 days).",
      "Maximum 3 to 6 consecutive pauses depending on AMC.",
      "Requires folio number and AMC portal login / CAMS myCAMS portal."
    ],
    officialSourceName: "AMFI India / CAMS Investor Services — SIP Pause Facility",
    officialSourceUrl: "https://www.amfiindia.com/investor-corner/knowledge-center/sip-pause.html",
    lastVerifiedDate: "2026-10-25",
    verificationStatus: "VERIFIED",
    plainLanguageSummary: "Direct AMC mandates require 10–21 days advance notice through CAMS, KFintech, or AMC portals to stop or pause an upcoming debit."
  },

  // --- GENERAL GUIDANCE FALLBACK ---
  general_guidance: {
    ruleId: "general_guidance",
    platform: "General / Other Platforms",
    setupType: "All",
    actionType: "overview",
    supported: false,
    minNoticeDays: 3,
    noticeCutoffDescription: "Industry average is 2 to 5 business days for platform SIPs, and 10 to 21 days for direct AMC mandates.",
    eligibilityConditions: "Varies by broker platform and AMC.",
    effectiveDateImplication: "We cannot confirm the exact cutoff for your specific platform setup. Please verify directly in your platform's help center before taking action.",
    limitations: [
      "Platform rules vary significantly (Groww vs Zerodha Coin vs Paytm Money vs AMC Direct).",
      "Do not assume a same-day or 1-day advance request will stop the debit.",
      "Check with your platform support or AMC customer care before taking action."
    ],
    officialSourceName: "AMFI India Official Guidance on Mutual Fund SIPs",
    officialSourceUrl: "https://www.amfiindia.com/investor-corner/knowledge-center/sip-pause.html",
    lastVerifiedDate: "2026-10-25",
    verificationStatus: "GENERAL_GUIDANCE",
    plainLanguageSummary: "General industry guidance: Most apps need 2 to 5 days advance notice, while direct AMC mandates need 10 to 21 days."
  }
};

/**
 * Deterministic Guidance Engine
 */
export function evaluateGuidance({ situation, platform, setupType, timeRemaining }) {
  const isUnknownPlatform = platform === "Another platform" || platform === "I'm not sure";
  const isUnknownSetup = setupType === "I'm not sure";
  const isAmcDirect = setupType === "AMC-registered SIP";

  let rule = PLATFORM_RULES.general_guidance;
  let isVerified = false;

  // Resolve rule only if both platform and setup type are verified and supported
  if (!isUnknownPlatform && !isUnknownSetup) {
    if (platform === "Groww" && !isAmcDirect) {
      if (situation === "My payment failed") {
        rule = PLATFORM_RULES.groww_payment_failure;
        isVerified = true;
      } else if (situation === "I want to cancel my SIP") {
        rule = PLATFORM_RULES.groww_cancel;
        isVerified = true;
      } else if (situation === "I may not have enough money for my next SIP") {
        rule = (timeRemaining === "Within 3–5 days" || timeRemaining === "More than 5 days")
          ? PLATFORM_RULES.groww_skip
          : PLATFORM_RULES.groww_pause;
        isVerified = true;
      } else if (situation === "I need to take a temporary break") {
        rule = PLATFORM_RULES.groww_pause;
        isVerified = true;
      } else if (situation === "My current SIP amount is difficult to manage") {
        rule = PLATFORM_RULES.groww_modify;
        isVerified = true;
      } else {
        rule = PLATFORM_RULES.groww_pause;
        isVerified = true;
      }
    } else if (platform === "Zerodha Coin" && !isAmcDirect) {
      if (situation === "I want to cancel my SIP") {
        rule = PLATFORM_RULES.zerodha_coin_cancel;
        isVerified = true;
      } else {
        rule = PLATFORM_RULES.zerodha_coin_pause;
        isVerified = true;
      }
    } else if (isAmcDirect) {
      rule = PLATFORM_RULES.amc_direct_pause;
      isVerified = true;
    }
  } else {
    rule = PLATFORM_RULES.general_guidance;
    isVerified = false;
  }

  // Evaluate Timing Cutoff Status conditionally
  let cutoffStatus = "SAFE_WINDOW_OPEN";
  let cutoffBadge = "✅ Window Open";
  let cutoffAlertText = "You appear to be outside the cutoff notice window for this setup. Requests made now should reliably apply before the upcoming debit.";

  if (situation === "My payment failed") {
    cutoffStatus = "POST_FAILURE";
    cutoffBadge = "ℹ️ Post-Debit Review";
    cutoffAlertText = "Your debit attempt has already concluded. No further automated retries will occur for this calendar month.";
  } else if (timeRemaining === "Today" || timeRemaining === "Within 1–2 days") {
    cutoffStatus = "CRITICAL_CUTOFF_PASSED";
    if (isAmcDirect) {
      cutoffBadge = "⚠️ Cutoff Passed for AMC Direct";
      cutoffAlertText = `Your debit is due in ${timeRemaining}. Direct AMC-registered mandates require 10–21 calendar days advance notice due to bank clearing batch cycles. A request submitted now cannot stop this upcoming debit.`;
    } else if (platform === "Groww" && !isUnknownSetup) {
      cutoffBadge = "⚠️ Cutoff Likely Passed on Groww";
      cutoffAlertText = `Your debit is due in ${timeRemaining}. Groww AutoPay mandates require at least 2 working days prior notice. Requests submitted within 2 working days typically apply only to the subsequent month.`;
    } else if (platform === "Zerodha Coin" && !isUnknownSetup) {
      cutoffBadge = "⚠️ Cutoff Likely Passed on Coin";
      cutoffAlertText = `Your debit is due in ${timeRemaining}. Zerodha Coin requires requests at least 2 working days prior (before 11:00 AM on T-2 days) before orders are sent to BSE StAR MF.`;
    } else {
      cutoffBadge = "⚠️ Cutoff May Be Passed";
      cutoffAlertText = `Your debit is due in ${timeRemaining}. Most mandates require at least 2 working days (and up to 10–21 days for direct AMC mandates). With 1–2 days remaining, your request may not take effect before this debit.`;
    }
  } else if (timeRemaining === "Within 3–5 days") {
    if (isAmcDirect) {
      cutoffStatus = "CRITICAL_CUTOFF_PASSED";
      cutoffBadge = "⚠️ Cutoff Passed for AMC Direct";
      cutoffAlertText = "AMC-registered mandates require 10–21 days notice. A 3–5 day window is insufficient to stop this upcoming debit.";
    } else if (platform === "Groww" && !isUnknownSetup) {
      cutoffStatus = "ACTION_NEEDED_PROMPTLY";
      cutoffBadge = "⏳ Action Needed Promptly";
      cutoffAlertText = "You have 3 to 5 days remaining. Since Groww requires at least 2 working days notice, submit your request promptly before the cutoff window closes.";
    } else if (platform === "Zerodha Coin" && !isUnknownSetup) {
      cutoffStatus = "ACTION_NEEDED_PROMPTLY";
      cutoffBadge = "⏳ Action Needed Promptly";
      cutoffAlertText = "You have 3 to 5 days remaining. Since Zerodha Coin requires requests at least 2 working days prior (before 11:00 AM on T-2 days), submit promptly.";
    } else {
      cutoffStatus = "ACTION_NEEDED_PROMPTLY";
      cutoffBadge = "⏳ Action Needed Promptly";
      cutoffAlertText = "You have 3 to 5 days remaining. Check your platform's specific cutoff (commonly 2 to 5 business days for apps, 10–21 days for direct AMCs) to ensure timely submission.";
    }
  } else if (timeRemaining === "I'm not sure of the date") {
    cutoffStatus = "UNCERTAIN_TIMING";
    cutoffBadge = "ℹ️ Date Unconfirmed";
    cutoffAlertText = "Please check your next scheduled debit date in your mutual fund app to confirm if you are within the safe notice window.";
  }

  // Construct Plain Language Guidance
  let whatThisMeans = "";
  let whatYouCanDoNow = [];
  let whatToBeCarefulAbout = [];

  if (situation === "I may not have enough money for my next SIP") {
    if (cutoffStatus === "CRITICAL_CUTOFF_PASSED") {
      if (platform === "Groww" && !isUnknownSetup) {
        whatThisMeans = "For Groww AutoPay SIPs, changes require at least 2 working days advance notice. Because your debit is due within 1–2 days, the bank debit instruction may already be in process, so a skip or pause submitted now will likely take effect only from the following month.";
      } else if (platform === "Zerodha Coin" && !isUnknownSetup) {
        whatThisMeans = "For Zerodha Coin SIPs, orders are generated on BSE StAR MF 2 working days in advance (by 11:00 AM on T-2 days). Requests submitted after this cutoff cannot stop order generation for the current cycle.";
      } else if (isAmcDirect) {
        whatThisMeans = "Direct AMC-registered mandates interface with bank clearing cycles in batches and require 10 to 21 calendar days notice. With only 1–2 days remaining, the upcoming debit cannot be stopped through CAMS, KFintech, or AMC portals.";
      } else {
        whatThisMeans = "Notice cutoffs depend on your specific broker and mandate arrangement. While app-based platforms commonly require ~2 working days, direct AMC mandates require 10–21 days. With only 1–2 days remaining, requests submitted now are unlikely to stop the upcoming debit.";
      }
      whatYouCanDoNow = [
        {
          title: "Maintain Sufficient Balance (If feasible)",
          description: "If possible, keep sufficient balance in your bank account on debit day to avoid bank ECS/NACH bounce fees."
        },
        {
          title: "Understand Bank vs Platform Charges",
          description: "If your account has insufficient funds, your bank may levy a bounce charge (typically ₹250–₹500 + GST). Platforms like Groww and Zerodha charge ₹0."
        },
        {
          title: "Submit Skip for Subsequent Month",
          description: "Submit a Skip or Pause request now in your app so that future debits do not attempt until you are ready."
        }
      ];
      whatToBeCarefulAbout = [
        "Do not assume submitting a skip or pause today will stop tomorrow's scheduled payment attempt.",
        "Advance cutoffs are mandate-specific (typically 2 working days for platform AutoPay, 10–21 days for direct AMC mandates).",
        "Your accumulated mutual fund units remain completely safe and untouched in your folio.",
        "A single missed debit does not cancel your SIP or liquidate your investment."
      ];
    } else {
      whatThisMeans = `You have sufficient time before your debit. On ${rule.platform}, you can safely skip this single instalment or pause deductions without penalty.`;
      whatYouCanDoNow = [
        {
          title: "Option 1: Skip Upcoming Instalment (Recommended)",
          description: "Skips only the upcoming month's debit. The SIP resumes automatically the following month without any re-setup."
        },
        {
          title: "Option 2: Pause SIP for 1 to 3 Months",
          description: "Halt deductions for multiple months while keeping your mandate alive. You can unpause whenever ready."
        },
        {
          title: "Option 3: Step Down Amount to Minimum",
          description: "Reduce your monthly contribution to ₹100 or ₹500 to keep the discipline going without stretching cash flow."
        }
      ];
      whatToBeCarefulAbout = [
        `Submit your request at least ${rule.minNoticeDays} working days before debit date.`,
        "Do not cancel the SIP if you only need temporary relief—cancellation requires creating a new mandate later."
      ];
    }
  } else if (situation === "My payment failed") {
    whatThisMeans = "Your scheduled SIP debit could not be processed (usually due to low balance, bank server downtime, or mandate expiry). A single failed payment does NOT cancel your mutual fund SIP.";
    whatYouCanDoNow = [
      {
        title: "Check Bank Passbook / Statement",
        description: "Check if your bank deducted an ECS/NACH bounce fee (typically ₹250–₹500 + GST). Platforms like Groww/Zerodha charge ₹0."
      },
      {
        title: "No Immediate Action Required for SIP Continuity",
        description: "Your SIP remains active. The next debit will automatically be attempted on the next scheduled monthly date."
      },
      {
        title: "Optional: Make a 1-Time UPI Lumpsum",
        description: "If you still want to invest this month's amount once cash arrives, you can place a 1-time purchase in the same fund folio."
      }
    ];
    whatToBeCarefulAbout = [
      "Rule of 3 Failures: Mutual fund regulations specify that if 3 consecutive monthly debits fail, the AMC will terminate the SIP.",
      "Units are not allotted for failed months, but your existing past units continue compounding normally."
    ];
  } else if (situation === "My current SIP amount is difficult to manage") {
    whatThisMeans = "You do not have to stop investing completely. Most mutual fund schemes allow stepping down your monthly instalment to their regulatory minimum (often ₹100 or ₹500).";
    whatYouCanDoNow = [
      {
        title: "Edit SIP Amount in Your App",
        description: "Navigate to your SIP details in Groww / Zerodha and select 'Edit SIP'. Lower the monthly amount to a manageable figure."
      },
      {
        title: "Keep the Compounding Habit",
        description: "Even ₹500/month maintains the psychological habit of investing without causing month-end anxiety."
      }
    ];
    whatToBeCarefulAbout = [
      "Editing the amount must be done at least 2 working days before your next debit date.",
      "Check scheme-specific minimum instalment requirements (some index funds allow ₹100, while others require ₹500)."
    ];
  } else if (situation === "I need to take a temporary break") {
    whatThisMeans = "You can take a temporary pause of 1 to 6 months without liquidating or affecting any past units you have already bought.";
    whatYouCanDoNow = [
      {
        title: "Use In-App Pause Feature",
        description: "Select 1, 2, 3, or up to 6 months pause in your platform app. Your mandate remains connected."
      },
      {
        title: "Set a Comeback Reminder",
        description: "Plan a date to review your budget and resume your SIP when cash flow normalizes."
      }
    ];
    whatToBeCarefulAbout = [
      `Pause requests must be submitted at least ${rule.minNoticeDays} working days before the scheduled debit date.`,
      "Your units remain invested and continue tracking the market."
    ];
  } else if (situation === "I want to cancel my SIP") {
    whatThisMeans = "Cancelling an SIP only stops FUTURE automated bank debits. It DOES NOT sell your existing mutual fund units or close your folio.";
    whatYouCanDoNow = [
      {
        title: "Cancel Future Automated Debits",
        description: "Go to SIP details > Cancel SIP. Future debits will stop permanently with zero platform exit charge."
      },
      {
        title: "Leave Units Invested",
        description: "Your accumulated wealth remains in the scheme, earning market returns and dividends until you decide to redeem."
      }
    ];
    whatToBeCarefulAbout = [
      "Cancelling within 2 days of debit date may not stop the immediate upcoming deduction.",
      "If you wish to redeem existing units, that requires a separate 'Redeem / Sell' order."
    ];
  } else {
    // General overview
    whatThisMeans = "Mutual fund SIPs are flexible contracts. You are never locked in or forced to continue debits if your financial situation changes.";
    whatYouCanDoNow = [
      {
        title: "Identify Your Immediate Need",
        description: "Decide whether you need relief for just 1 month (Skip), multiple months (Pause), a lower amount (Edit), or permanent stop (Cancel)."
      },
      {
        title: "Check Your Advance Notice Window",
        description: "Ensure your request is submitted with at least 2–3 business days buffer before debit day."
      }
    ];
    whatToBeCarefulAbout = [
      "Accumulated units are always safe in your folio with the AMC, registered under your PAN.",
      "Check with your platform or AMC before taking irreversible actions."
    ];
  }

  return {
    situation,
    platform,
    setupType,
    timeRemaining,
    isVerified,
    cutoffStatus,
    cutoffBadge,
    cutoffAlertText,
    rule,
    whatThisMeans,
    whatYouCanDoNow,
    whatToBeCarefulAbout,
    uncertaintyNotice: !isVerified
      ? "We couldn't verify the rule for this specific SIP setup. Please check the relevant platform or AMC before taking action."
      : null
  };
}

/**
 * Validates a proposed voluntary one-time investment amount against fund rules.
 */
export function validateOneTimeAmount(amount, sip) {
  const num = Number(amount);
  if (isNaN(num) || num <= 0) {
    return {
      isValid: false,
      amount: 0,
      percent: 0,
      difference: sip.monthlyAmount,
      message: "Please enter a valid investment amount greater than ₹0."
    };
  }

  const minRequired = sip.minLumpSumAmount || 100;
  if (num < minRequired) {
    return {
      isValid: false,
      amount: num,
      percent: Math.round((num / sip.monthlyAmount) * 100),
      difference: sip.monthlyAmount - num,
      minRequired,
      message: `The selected amount (₹${num.toLocaleString("en-IN")}) is below the fund's known minimum additional investment requirement of ₹${minRequired.toLocaleString("en-IN")}.`
    };
  }

  const percent = Math.round((num / sip.monthlyAmount) * 100);
  const difference = sip.monthlyAmount - num;

  return {
    isValid: true,
    amount: num,
    percent,
    difference,
    minRequired,
    message: null
  };
}

/**
 * Evaluates the Plan Ahead route deterministically.
 */
export function evaluatePlanAheadRoute({ sip, action, scenarioState = "supported_skip", chosenAmount = 1000 }) {
  const isScheduled = !!sip.nextDebitDate;
  const isGrowwOrCoin = sip.platform === "Groww" || sip.platform === "Zerodha Coin";
  
  if (scenarioState === "deadline_passed") {
    const potentialOutflow = sip.monthlyAmount + (chosenAmount || 0);
    return {
      routeCase: "CASE_DEADLINE_PASSED",
      isScheduled,
      deadlineKnown: true,
      deadlineStatus: "DEADLINE_PASSED",
      regularDebitMayOccur: true,
      warningTitle: "Your regular SIP debit may still be processed",
      warningBody: `Because your next debit is scheduled within less than 2 working days (${sip.nextDebitRelative}), platform presentation files may have already been generated. Submitting a skip or pause now may not halt this immediate debit.`,
      scheduledSipAmount: sip.monthlyAmount,
      proposedInvestmentAmount: chosenAmount,
      potentialTotalOutflow: potentialOutflow,
      outflowLabel: "Potential total outflow, not a confirmed debit",
      advice: "Do not proceed directly to an additional investment without obtaining explicit confirmation of this potential double outflow.",
      officialSource: sip.officialHelpUrl || "https://groww.in/help/mutual-funds/sip",
      platform: sip.platform
    };
  }

  if (scenarioState === "unverified" || !isGrowwOrCoin) {
    return {
      routeCase: "CASE_UNVERIFIED",
      isScheduled,
      deadlineKnown: false,
      deadlineStatus: "UNVERIFIED",
      regularDebitMayOccur: true,
      warningTitle: "Platform Rule Verification Required",
      warningBody: "We could not confirm whether this change can affect your upcoming instalment. Please check the applicable platform or AMC instructions before proceeding.",
      scheduledSipAmount: sip.monthlyAmount,
      proposedInvestmentAmount: chosenAmount,
      missingInformation: [
        "Broker/Bank presentation cut-off timing for this specific mandate type",
        "AMC direct clearing schedule requirements"
      ],
      whereToCheck: `${sip.amc} official portal (${sip.amcWebsite}) or your banking mandate portal.`,
      platform: sip.platform
    };
  }

  // Default: Supported Skip Route
  return {
    routeCase: "CASE_SUPPORTED_SKIP",
    isScheduled,
    deadlineKnown: true,
    deadlineStatus: "WINDOW_OPEN",
    regularDebitMayOccur: false,
    skipSupported: true,
    platform: sip.platform,
    scheduledSipAmount: sip.monthlyAmount,
    proposedInvestmentAmount: chosenAmount,
    message: `You can request an instalment skip directly on ${sip.platform} with ₹0 platform penalty before debit day.`,
    demoSkipSuccessMessage: `Your upcoming SIP instalment has been skipped in this demo scenario. Would you like to explore a separate investment of ₹${(chosenAmount || 1000).toLocaleString("en-IN")} in the same fund?`,
    officialSource: sip.officialHelpUrl || "https://groww.in/help/mutual-funds/sip"
  };
}

/**
 * Evaluates Missed Payment status deterministically.
 */
export function evaluateMissedPaymentStatus({ sip, reasonKey }) {
  const configs = {
    insufficient_funds: {
      key: "insufficient_funds",
      title: "Insufficient Funds in Bank Account",
      shortSummary: "The debit did not happen because I had insufficient funds",
      explanation: "Your scheduled instalment may not have been completed. Check the payment status and applicable platform instructions before taking another action.",
      statusTone: "alert",
      regularSipStatus: "Payment failed in this demo scenario",
      regularDebitStatus: "Payment not debited",
      bankFeeNotice: "Your bank may levy an ECS/NACH return fee (typically ₹250–₹500 + GST). Platforms charge ₹0.",
      ruleOfThree: "SEBI / AMFI guidelines mandate that your SIP remains active after a single missed debit. Only 3 consecutive monthly failures trigger automatic cancellation.",
      repeatDebitWarning: "Your regular SIP payment may still be pending or subject to another debit attempt. Confirm the payment status before making an additional investment.",
      unitsSafe: true
    },
    mandate_failed: {
      key: "mandate_failed",
      title: "Payment or Bank Mandate Presentation Failed",
      shortSummary: "The payment or mandate failed",
      explanation: "Your payment may require attention. Check the mandate or payment status to understand whether another debit attempt is possible.",
      statusTone: "warning",
      regularSipStatus: "Payment or mandate failed in this demo scenario",
      regularDebitStatus: "Mandate requires verification",
      bankFeeNotice: "Technical or mandate presentation rejections do not always incur bank penalty charges.",
      ruleOfThree: "A technical failure does not terminate your SIP contract. Inspect your mandate status in your broker app.",
      repeatDebitWarning: "Your regular SIP payment may still be pending or subject to another debit attempt. Confirm the payment status before making an additional investment.",
      unitsSafe: true
    },
    requested_skip_earlier: {
      key: "requested_skip_earlier",
      title: "Instalment Skip Requested Earlier",
      shortSummary: "I requested a skip earlier",
      explanation: "Check whether the skip request was accepted. A submitted request does not necessarily mean the instalment was successfully skipped.",
      statusTone: "info",
      regularSipStatus: "Skip request submitted earlier (under review)",
      regularDebitStatus: "Pending confirmation of skip",
      bankFeeNotice: "If the skip was accepted in time, ₹0 bank fee applies.",
      ruleOfThree: "An accepted skip does not count towards the 3-failure cancellation counter.",
      repeatDebitWarning: "If the skip request was submitted too close to debit day, a presentation attempt may still have occurred. Verify with your bank first.",
      unitsSafe: true
    },
    unknown_reason: {
      key: "unknown_reason",
      title: "Amount Not Debited (Reason Unknown)",
      shortSummary: "The amount has not been debited, but I do not know why",
      explanation: "We cannot confirm the payment outcome yet. Verify the transaction status before making another investment.",
      statusTone: "warning",
      regularSipStatus: "Payment status unknown",
      regularDebitStatus: "Awaiting bank / platform confirmation",
      bankFeeNotice: "Do not make assumptions about bank charges until your bank statement is inspected.",
      ruleOfThree: "Clearing house delays (NPCI / BSE / CAMS) can delay debit notifications by up to 24–48 hours on bank holidays.",
      repeatDebitWarning: "Crucial: Check your bank and platform records before proceeding. The app cannot confirm a missed payment from the absence of a status alone.",
      unitsSafe: true
    },
    uncertain_processing: {
      key: "uncertain_processing",
      title: "Uncertain if Payment was Processed",
      shortSummary: "I am not sure whether the payment was processed",
      explanation: "Check your bank and platform records before proceeding. The app cannot confirm a missed payment from the absence of a status alone.",
      statusTone: "info",
      regularSipStatus: "Payment status unknown",
      regularDebitStatus: "Awaiting user bank statement check",
      bankFeeNotice: "Always inspect your NetBanking transaction log before initiating any secondary payment.",
      ruleOfThree: "Mutual fund units are allotted on NAV date only after funds are realized by the AMC.",
      repeatDebitWarning: "Confirm your payment status before making an additional investment. Do not risk a double debit.",
      unitsSafe: true
    }
  };

  return configs[reasonKey] || configs.unknown_reason;
}

