# SIP Rescue — A SIP Continuity Assistant
*Standalone Indian Mutual Fund Investor Continuity MVP*

---

## 1. Overview & Purpose

**SIP Rescue** is a standalone, investor-facing fintech product prototype designed to help retail mutual fund investors navigate temporary cash crunches, upcoming debits, and payment failures without dropping off or incurring avoidable bank penalty charges.

Unlike generic research tools or raw data dashboards, **SIP Rescue** is structured around an actual retail investor journey:
1. **Understand Portfolio Commitments**: See active SIP commitments across recognized Indian AMCs.
2. **Context-Aware Rescue Navigator**: 3-step progressive disclosure flow (*Situation → Options → Next Steps*) powered by deterministic, verified platform rules (Groww, Zerodha Coin, and AMC Direct).
3. **No-Pressure Comeback Plan**: A reflection reminder and standard `.ics` calendar generator so investors can pause without fear of losing investment discipline.
4. **Privacy-First Feedback**: Quick, unobtrusive user feedback stored locally with zero collection of sensitive financial credentials.

---

## 2. Directory Structure

The standalone application is completely self-contained in `sip-rescue-mvp/` and runs with zero external npm dependencies or complex build steps:

```
sip-rescue-mvp/
├── index.html                  # HTML5 entry point with responsive meta tags & fonts
├── css/
│   └── styles.css              # Fintech design system (emerald green, subtle borders, mobile grid)
├── js/
│   ├── app.js                  # Application orchestrator, URL hash router, and view manager
│   ├── components/
│   │   ├── Header.js           # Top navigation, brand icon, demo scenario menu, demo badge
│   │   ├── HomeScreen.js       # Screen 1: Welcome hero, portfolio metrics, 3 AMC scheme cards
│   │   ├── SipDetailScreen.js  # Screen 2: Focused scheme details, upcoming debit timeline, rules overview
│   │   ├── RescueNavigator.js  # Screen 3: Guided 3-step wizard (Situation -> Options -> Next Steps)
│   │   ├── ComebackPlan.js     # Screen 4: Review later date picker, limitation disclaimer, .ics export
│   │   └── FeedbackModal.js    # Screen 5: Lightweight feedback widget (localStorage persistence)
│   └── data/
│       ├── sampleSips.js       # Verified Indian mutual fund schemes with illustrative demo data
│       ├── rulesConfig.js      # Deterministic platform rules (Groww, Zerodha Coin, AMC Direct)
│       └── demoScenarios.js    # 3 ready-to-run assessor test scenarios
├── run.py                      # Standalone zero-dependency Python local server (port 5173)
├── package.json                # Project descriptor & npm launch scripts (`npm run dev`)
└── README.md                   # Complete architectural and evaluation documentation
```

---

## 3. How to Launch the Standalone Application

### Option A: Using Python (Recommended on Windows)
From the project root or inside `sip-rescue-mvp/`:

```bash
cd "c:\Users\anshy\OneDrive\Desktop\Project 3 -MVP\sip-rescue-mvp"
python run.py
```

*Output:*
```text
================================================================
  [*] SIP Rescue -- A SIP Continuity Assistant
  Standalone MVP Application
================================================================
  Running locally at: http://localhost:5173
  Serving directory : .../sip-rescue-mvp
  Press Ctrl+C to stop the server.
================================================================
```
Open **[http://localhost:5173](http://localhost:5173)** in any modern browser (Chrome, Edge, Firefox, Safari).

### Option B: Using Node / NPM
If Node.js is installed in your environment:

```bash
cd "c:\Users\anshy\OneDrive\Desktop\Project 3 -MVP\sip-rescue-mvp"
npm run dev
```

---

## 4. Realistic Indian Mutual Fund Context

All mutual fund schemes were verified against official AMC product registries:

| AMC Name | Official Scheme Name | Verified Plan / Option | Demo Amount | Frequency | Next Debit Timing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HDFC Mutual Fund** | HDFC Flexi Cap Fund | Direct Plan – Growth | ₹3,000 / mo | Monthly (10th) | Due in 2 days (Cutoff approaching) |
| **SBI Mutual Fund** | SBI Nifty Index Fund *(Nifty 50 Index)* | Direct Plan – Growth | ₹2,000 / mo | Monthly (5th) | Due in 9 days (Active) |
| **ICICI Prudential Mutual Fund** | ICICI Prudential Balanced Advantage Fund | Direct Plan – Growth | ₹2,500 / mo | Monthly (15th) | Due in 18 days (Active) |

*Total Illustrative Monthly Commitment:* **₹7,500** across 3 active funds.

*Disclaimer:* All portfolio amounts, account numbers, and debit schedules shown are fictional demo data for prototype evaluation. This application does not connect to actual bank accounts, initiate financial transactions, or offer investment recommendations.

---

## 5. Verified Platform Rules & Source Citations

The guidance engine in `js/data/rulesConfig.js` enforces strict transparency:

1. **Groww AutoPay / Platform-Managed SIPs** (Verified: 2026-10-25)
   - *Skip Instalment*: Requires at least **2 working days** notice before scheduled debit date. ₹0 platform fee. Maximum 1 instalment skipped per request.
   - *Pause SIP*: Requires at least **2 working days** notice. Allows 1–6 months halt. Folio units remain untouched.
   - *Modify Amount*: Requires at least **2 working days** notice. Subject to scheme minimum (e.g. ₹100 or ₹500).
   - *Payment Failure*: Single failure does NOT cancel SIP. Groww charges ₹0, but banks charge ECS bounce fees (typically ₹250–₹500 + GST). 3 consecutive failures terminate the SIP at the AMC.
   - *Official Source*: [Groww Help & Support — Mutual Funds](https://groww.in/help/mutual-funds/sip)

2. **Zerodha Coin / BSE StAR MF SIPs** (Verified: 2026-10-25)
   - *Pause / Delete*: Requires at least **2 working days** notice before 11:00 AM 2 days prior to debit. Demat units remain completely safe. 3 failed orders delete the SIP on BSE StAR MF.
   - *Official Source*: [Zerodha Support Portal — Coin SIP](https://support.zerodha.com/category/mutual-funds/coin-web/sip-coin)

3. **AMC-Registered Direct Mandates (CAMS / KFintech)** (Verified: 2026-10-25)
   - *Notice Cutoff*: Requires **10 to 21 calendar days** advance notice due to NPCI/NACH bank clearing cycles. Changes requested within 10 days apply only to subsequent months.
   - *Official Source*: [AMFI India / CAMS Investor Services](https://www.amfiindia.com/investor-corner/knowledge-center/sip-pause.html)

4. **Safe Uncertainty Fallback**
   - If an unknown platform or unverified mandate type is selected, the application displays:
     > *"We couldn't verify the rule for this SIP setup. Please check the relevant platform or AMC before taking action."*

---

## 6. Three Complete Assessor Demo Journeys

Click the **⚡ Try a demo scenario** dropdown at the top right of the navigation header:

### Journey 1: Upcoming Cash Shortage (T-2 Days)
- **Scenario**: Investor has ₹3,000 debit due on HDFC Flexi Cap Fund in 2 days and anticipates a bank balance shortfall.
- **Navigator Flow**:
  1. Step A: Selects *"I may not have enough money for my next SIP"*.
  2. Step B: Prepopulates HDFC Flexi Cap Fund (Groww, T-2 days).
  3. Step C: Shows warning banner **"⚠️ Cutoff Likely Passed"**. Explains that the bank debit file is already in processing; advises maintaining balance if feasible to avoid bank ECS bounce fees, or submitting Skip for next month. Cites official Groww documentation.
  4. Actions: Investor clicks *"Create a Review Reminder"*, picks 30 days ("Review my monthly budget"), and downloads an `.ics` calendar file.

### Journey 2: Payment Failure & Recovery
- **Scenario**: ₹2,000 debit on SBI Nifty Index Fund failed yesterday. Investor is worried about penalties or cancellation.
- **Navigator Flow**:
  1. Step A: Selects *"My payment failed"*.
  2. Step B: Prepopulates SBI Nifty Index Fund on Zerodha Coin.
  3. Step C: Reassures investor that 1 missed debit **does not terminate the SIP**. Explains bank bounce fees vs ₹0 platform fee. Warns about the 3-consecutive-failure AMC rule.

### Journey 3: Cancellation Consideration
- **Scenario**: Investor wants to stop ₹2,500 SIP on ICICI Prudential Balanced Advantage Fund to cut expenses.
- **Navigator Flow**:
  1. Step A: Selects *"I want to cancel my SIP"*.
  2. Step B: Evaluates Groww platform cancellation rules (> 5 days notice).
  3. Step C: Explains that cancellation only stops *future* automated debits. Accumulated mutual fund units stay safe in the folio earning market returns. Highlights alternative options: Pause for 3 months or step down monthly amount to ₹500.

---

## 7. Limitations & Honest Design Disclosures

1. **Non-Transactional**: This application provides decision guidance and reflection tools. It does not initiate bank debits, execute trades, or modify broker mandates.
2. **Comeback Plan**: Stored in local browser storage (`localStorage`). No SMS or email alerts are sent unless exported to desktop/mobile calendar via `.ics`.
3. **Feedback**: Privacy-conscious, stored in browser local storage for prototype testing. No PAN, bank account numbers, or passwords are ever requested or logged.
