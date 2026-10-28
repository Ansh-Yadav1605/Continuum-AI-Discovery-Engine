/**
 * sip-rescue-mvp/js/data/sampleSips.js
 * 
 * Verified Indian Mutual Fund Schemes (Illustrative Demo Data).
 * 
 * Schemes:
 * 1. HDFC Mutual Fund — HDFC Flexi Cap Fund (Direct Plan – Growth)
 * 2. SBI Mutual Fund — SBI Nifty Index Fund [Nifty 50 Index Fund] (Direct Plan – Growth)
 * 3. ICICI Prudential Mutual Fund — ICICI Prudential Balanced Advantage Fund (Direct Plan – Growth)
 * 
 * Note: All figures, dates, and account identifiers are strictly for demonstration
 * and do not represent actual live accounts or investment advice.
 */

export const SAMPLE_SIPS = [
  {
    id: "sip-hdfc-flexi",
    amc: "HDFC Mutual Fund",
    amcShort: "HDFC",
    schemeName: "HDFC Flexi Cap Fund",
    planOption: "Direct Plan – Growth",
    isin: "INF179K01UT0",
    monthlyAmount: 3000,
    frequency: "Monthly (10th)",
    nextDebitDate: "2026-10-29",
    nextDebitRelative: "In 2 days",
    status: "Upcoming",
    statusDetail: "Debit due in 2 days",
    statusTone: "warning", // 'normal' | 'warning' | 'alert'
    needsAttention: true,
    attentionReason: "Debit approaching within 48h notice window",
    nextStepHint: "Review bank balance or skip if funds are tight",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    folioNumber: "FOLIO-DEMO-9481",
    amcWebsite: "https://www.hdfcfund.com",
    mandateMethod: "UPI AutoPay (NPCI)",
    minSipAmount: 100,
    minLumpSumAmount: 100,
    minLumpSumLabel: "₹100 (Official AMC minimum for additional purchase)",
    officialHelpUrl: "https://groww.in/help/mutual-funds/sip",
    notes: "Demonstration SIP: scheduled debit is approaching within 48 hours."
  },
  {
    id: "sip-sbi-nifty",
    amc: "SBI Mutual Fund",
    amcShort: "SBI",
    schemeName: "SBI Nifty Index Fund",
    schemeSubtitle: "SBI Nifty 50 Index Fund",
    planOption: "Direct Plan – Growth",
    isin: "INF200K01131",
    monthlyAmount: 2000,
    frequency: "Monthly (5th)",
    nextDebitDate: "2026-11-05",
    nextDebitRelative: "In 9 days",
    status: "Active",
    statusDetail: "Mandate active",
    statusTone: "normal",
    needsAttention: false,
    nextStepHint: "Normal schedule; no immediate action needed",
    platform: "Zerodha Coin",
    setupType: "Platform-managed SIP",
    folioNumber: "FOLIO-DEMO-3109",
    amcWebsite: "https://www.sbimf.com",
    mandateMethod: "e-NACH Mandate",
    minSipAmount: 500,
    minLumpSumAmount: 500,
    minLumpSumLabel: "₹500 (Official AMC minimum for additional purchase)",
    officialHelpUrl: "https://support.zerodha.com/category/mutual-funds/coin-web/sip-coin",
    notes: "Demonstration SIP: comfortable 9-day buffer before scheduled execution."
  },
  {
    id: "sip-icici-pru-baf",
    amc: "ICICI Prudential Mutual Fund",
    amcShort: "ICICI Prudential",
    schemeName: "ICICI Prudential Balanced Advantage Fund",
    planOption: "Direct Plan – Growth",
    isin: "INF109K019R0",
    monthlyAmount: 2500,
    frequency: "Monthly (15th)",
    nextDebitDate: "2026-11-15",
    nextDebitRelative: "In 18 days",
    status: "Active",
    statusDetail: "Mandate active",
    statusTone: "normal",
    needsAttention: false,
    nextStepHint: "Normal schedule; next debit in 18 days",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    folioNumber: "FOLIO-DEMO-7725",
    amcWebsite: "https://www.icicipruamc.com",
    mandateMethod: "NetBanking AutoPay",
    minSipAmount: 100,
    minLumpSumAmount: 100,
    minLumpSumLabel: "₹100 (Official AMC minimum for additional purchase)",
    officialHelpUrl: "https://groww.in/help/mutual-funds/sip",
    notes: "Demonstration SIP: 18 days remaining until upcoming instalment."
  }
];

export const PORTFOLIO_SUMMARY = {
  activeCount: 3,
  totalMonthlyCommitment: 7500, // 3000 + 2000 + 2500
  plannedCommitment: 7500,
  paidSoFarThisMonth: 0,
  nextInstalmentAmount: 3000,
  nextInstalmentText: "₹3,000 due in 2 days",
  nextInstalmentDate: "2026-10-29",
  nextInstalmentFund: "HDFC Flexi Cap Fund",
  needsAttentionCount: 1,
  needsAttentionLabel: "1 SIP due soon",
  modeLabel: "Sample Portfolio — Demo Mode"
};
