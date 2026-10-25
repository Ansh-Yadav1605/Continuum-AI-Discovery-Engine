# Research Methodology & Acceptance Criteria Verification

> **Project:** AI-Powered SIP Continuation Discovery Engine  
> **Fellowship Context:** Product Management Assignment (Groww Mutual Funds)  
> **Target Outcome:** Understand why first-time investors stop SIPs within 12 months.

---

## 1. Research Protocol & Ethical Boundaries

### 1.1 Scope & Objective
The central objective is investigating why first-time mutual fund investors on Groww pause, stop, or drop off from Systematic Investment Plans (SIPs) within their first 12 months. An **active SIP** is strictly defined as an investment where at least one instalment deduction was successfully executed within the last 30 calendar days.

### 1.2 Data Source Reality & Limitations
- **No Internal Ledger Access:** As external researchers, we have no access to Groww's internal transaction databases, customer logs, or KYC records.
- **Observational Signals vs. Causality:** Public reviews (Google Play Store, Trustpilot, App Store) and survey responses cannot independently establish 12-month retention causality.
- **Sampling Asymmetry:** Vocal dissatisfied investors are disproportionately represented in public app store reviews relative to satisfied passive investors.

### 1.3 Compliance & Safety Hard Constraints
- **Zero Investment Advice:** The engine explicitly does NOT recommend specific funds, asset classes, or stocks.
- **Zero Dark Patterns:** No manufactured urgency, countdown timers, FOMO triggers, or guilt-tripping nudges.
- **PII Quarantine:** No collection or persistence of PAN, bank account numbers, IFSC codes, Aadhaar, or passwords.

---

## 2. 14-Category Behavioral Taxonomy

1. **Expectations vs. Actual Experience:** Short-term volatility shock, negative returns in early months.
2. **Process & Mechanics Understanding:** Confusion regarding NAV dates, compounding timeframes, or fund allocations.
3. **Uncertainty & Confidence:** Hesitation when markets dip; anxiety about market timing.
4. **Payment & Mandate Friction:** UPI AutoPay failures, bank debit limits, deduction retry glitches.
5. **Changing Personal / Financial Circumstances:** Job changes, salary delays, sudden liquidity emergencies.
6. **Habits, Routines & Drift:** Lack of investment routine, forgetting to fund bank account on SIP date.
7. **Trust, Transparency & Reporting:** Unclear P&L reporting, confusion over fund expense ratios or exit loads.
8. **Customer Support & Issue Resolution:** Delayed resolution of deduction disputes or mandate cancellations.
9. **Product Usability & Navigation:** In-app difficulty finding SIP pause/cancel buttons or viewing transaction status.
10. **Information Needs & External Workarounds:** Relying on Reddit/YouTube for advice due to lack of in-app clarity.
11. **Continuation Drivers:** Positive experiences, auto-deduction convenience, long-term discipline.
12. **Reasons for Stopping:** Intentional cancellation reasons (financial strain, switching platforms).
13. **Reasons for Pausing:** Temporary cash constraints, expectation of better market entry point.
14. **General Feedback & App Experience:** Platform performance, general UI comments unrelated to SIP mechanics.

---

## 3. 6-Factor Opportunity Prioritization Scorecard

Problem statements are evaluated on a 1–5 scale across 6 weighted factors:
1. **Evidence Strength (25%):** Triangulation across multiple sources and respondents.
2. **SIP Continuation Relevance (25%):** Direct link to 12-month retention vs. generic onboarding complaints.
3. **User Severity (15%):** Emotional anxiety or acute financial friction caused to the user.
4. **Product Influence (15%):** Feasibility of addressing via Groww product/UX interventions.
5. **Project Feasibility (10%):** Realistic to research, validate, and test within constraints.
6. **Safety & Compliance (10% — Hard Filter):** Any candidate scoring $\le 2$ is **strictly blocked** from ranking.

---

## 4. Verification Against All 22 Acceptance Criteria

| # | Acceptance Criterion | Verification Method | Status |
| :---: | :--- | :--- | :---: |
| **1** | CSV import works for public reviews | Tested via `pages/2_Import_Data.py` and `tests/test_ingestion.py` | ✅ PASS |
| **2** | Invalid / incomplete records handled | Empty rows rejected; malformed fields reported cleanly | ✅ PASS |
| **3** | Source references preserved | Logged in `source_register` table with provenance | ✅ PASS |
| **4** | Google Forms import preserves respondent context | `survey_ingestion.py` maps respondent IDs and checkboxes | ✅ PASS |
| **5** | Groq auth and connection test work | 5-step diagnostic in `core/groq_client.py` verified | ✅ PASS |
| **6** | Missing credentials show clear manual fallback | App defaults to manual labeling mode without crashing | ✅ PASS |
| **7** | Model outputs validated against JSON schema | Pydantic / schema validator verifies all required taxonomy keys | ✅ PASS |
| **8** | Ambiguous records can be flagged | Human reviewers can categorize records as "ambiguous" | ✅ PASS |
| **9** | Themes link to supporting evidence | Drill-down cards in `pages/4_Theme_Analysis.py` display quotes | ✅ PASS |
| **10** | Contradictory evidence preserved | Separates drop-off friction vs. continuation signals | ✅ PASS |
| **11** | Problem statements include limitations | Observation, Interpretation, Hypothesis, and Limitations explicitly separated | ✅ PASS |
| **12** | Humans can correct AI labels | Research Explorer and AI Evaluation benchmark save human corrections | ✅ PASS |
| **13** | AI and human labels comparable | Side-by-side comparison with Precision/Recall/F1 metrics | ✅ PASS |
| **14** | Evidence Log exports correctly | One-click CSV download in `pages/8_Export.py` | ✅ PASS |
| **15** | API failures don't destroy data | Database transactions ensure partial progress is committed | ✅ PASS |
| **16** | Imported text cannot override system prompts | Strict prompt injection defense quarantines external text as data | ✅ PASS |
| **17** | Privacy and safety restrictions followed | No PII collected; safety compliance hard filter enforced | ✅ PASS |
| **18** | Beginner can follow setup instructions | Comprehensive, step-by-step `README.md` created | ✅ PASS |
| **19** | Chrome extension cannot send unapproved records | Approve & Save button requires active user confirmation | ✅ PASS |
| **20** | Extension saves approved records to SQLite | FastAPI `/api/collect` endpoint inserts into unified records | ✅ PASS |
| **21** | CSV import works without extension running | CSV and survey imports operate completely independently | ✅ PASS |
| **22** | No deployment URL claimed without live testing | Local-first architecture explicitly documented | ✅ PASS |
