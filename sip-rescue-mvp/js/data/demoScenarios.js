/**
 * sip-rescue-mvp/js/data/demoScenarios.js
 * 
 * Interactive Assessor Scenarios for SIP Rescue Navigator:
 * Aligned with Acceptance Tests A through H:
 * 
 * 1. Plan Ahead — Supported Skip Window (T-2 Days, HDFC Flexi Cap ₹3,000) [Tests A & B]
 * 2. Plan Ahead — Deadline Passed (<24h, Warning on Potential Outflow) [Test C]
 * 3. Missed Payment — Insufficient Funds (Recovery & Status) [Test D]
 * 4. Missed Payment — Mandate or Payment Failure (Mandate Attention) [Test E]
 * 5. Missed Payment — Unknown Debit Outcome (Verification First) [Test F]
 * 6. Flexible Contribution — Voluntary Smaller One-Time Investment [Flexible Contribution]
 * 7. Cancellation Consideration — Options & Pause Comparison (Existing flow)
 */

export const DEMO_SCENARIOS = [
  {
    id: "scenario-plan-ahead-skip",
    title: "Plan Ahead — Supported Skip Window",
    tag: "T-2 Days • ₹3,000 SIP",
    description: "Investor has upcoming debit on HDFC Flexi Cap Fund due in 2 days. Platform supports skip with ₹0 fee.",
    sipId: "sip-hdfc-flexi",
    situation: "I want to skip this month's instalment",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    timeRemaining: "Within 1–2 days",
    targetScreen: "plan-ahead",
    scenarioType: "supported_skip",
    cutoffPassed: false,
    initialNeed: "skip",
    suggestedAmount: 1000
  },
  {
    id: "scenario-plan-ahead-deadline",
    title: "Plan Ahead — Deadline Passed (<24h)",
    tag: "Double Outflow Warning",
    description: "Upcoming debit is due tomorrow. Modification cutoff has passed. App warns about potential double outflow before separate investment.",
    sipId: "sip-hdfc-flexi",
    situation: "I cannot afford the full amount this month",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    timeRemaining: "Today",
    targetScreen: "plan-ahead",
    scenarioType: "deadline_passed",
    cutoffPassed: true,
    initialNeed: "smaller_amount",
    suggestedAmount: 1000
  },
  {
    id: "scenario-missed-insufficient",
    title: "Missed Payment — Insufficient Funds",
    tag: "Payment Not Debited",
    description: "Scheduled debit on HDFC Flexi Cap was not debited due to low balance. Explains bounce fees, continuity rule of 3, and next steps.",
    sipId: "sip-hdfc-flexi",
    situation: "The debit did not happen because I had insufficient funds",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    timeRemaining: "Past debit date",
    targetScreen: "missed-payment",
    missedReason: "insufficient_funds"
  },
  {
    id: "scenario-missed-mandate-fail",
    title: "Missed Payment — Mandate / Payment Failed",
    tag: "Mandate Issue",
    description: "Payment or mandate failed on SBI Nifty Index Fund. Explains mandate status and confirms recurring SIP is not automatically cancelled.",
    sipId: "sip-sbi-nifty",
    situation: "The payment or mandate failed",
    platform: "Zerodha Coin",
    setupType: "Platform-managed SIP",
    timeRemaining: "Yesterday",
    targetScreen: "missed-payment",
    missedReason: "mandate_failed"
  },
  {
    id: "scenario-missed-unknown",
    title: "Missed Payment — Status Unknown",
    tag: "Verify Before Acting",
    description: "Instalment was not debited but status is uncertain. Prominently warns user to verify bank/platform records before additional investment.",
    sipId: "sip-hdfc-flexi",
    situation: "The amount has not been debited, but I do not know why",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    timeRemaining: "Unknown",
    targetScreen: "missed-payment",
    missedReason: "unknown_reason"
  },
  {
    id: "scenario-flexible-contribution",
    title: "Flexible Contribution — ₹1,000 One-Time",
    tag: "Voluntary Investment",
    description: "Direct exploration of a smaller ₹1,000 one-time purchase in HDFC Flexi Cap Fund without altering recurring SIP.",
    sipId: "sip-hdfc-flexi",
    situation: "I want to invest a smaller amount in the same fund",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    timeRemaining: "Anytime",
    targetScreen: "flexible-contribution",
    voluntaryAmount: 1000
  },
  {
    id: "scenario-cancel-vs-pause",
    title: "Cancellation Consideration — Options",
    tag: "Pause vs Cancel",
    description: "Investor considering cancelling ₹2,500 SIP on ICICI Prudential Balanced Advantage Fund, comparing pause vs stepping down vs cancelling.",
    sipId: "sip-icici-pru-baf",
    situation: "I am considering cancelling my SIP",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    timeRemaining: "More than 5 days",
    targetScreen: "navigator"
  }
];
