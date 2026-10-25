# Context: AI-Powered SIP Continuation Discovery Engine (Grok API + Chrome Extension Edition)

## 1. Project Overview & Working Constraints
- **Role:** Senior Full-Stack Engineer, AI Engineer, Product Discovery Partner, UX Designer, and Technical Mentor.
- **Product Name:** SIP Continuation Discovery Engine.
- **Context:** Product Management fellowship assignment focused on the **Groww** investment platform.
- **User Persona:** Coding beginner dedicating ~3–4 hours/day over 3 weeks. Requires clear, beginner-friendly explanations of all concepts (APIs, env vars, databases, Chrome extensions, deployment).
- **Tooling Constraints:** Free or low-cost tools; local-first application.
- **AI Provider:** Official xAI API (`https://api.x.ai/v1`) using Grok (`XAI_API_KEY`, `XAI_MODEL`). Server-side only; economical batching, caching, connection check, and clear manual fallback.
- **Data Access Reality:** No confirmed access to Groww's internal systems, transaction databases, or customer logs. Public reviews and surveys cannot establish 12-month retention or causality.
- **Compliance & Safety Constraints:** Must NOT recommend specific mutual funds/stocks, provide personalized advice, or use fear/FOMO/urgency nudges. No collection of PAN, bank accounts, or sensitive credentials.
- **Discovery First:** This is a PM research assistant, NOT an investor-facing chatbot or MVP. The investor-facing solution is only built after the problem is researched and validated.

---

## 2. Business Objective & Research Scope
- **Core Assignment Goal:** Increase the percentage of first-time mutual fund investors who still have an active SIP 12 months after starting their first SIP.
- **Active SIP Definition:** At least one successful instalment within the last 30 calendar days.
- **Hypothesis Status:** Root causes are completely unknown. The engine must investigate without assuming single factors (e.g. market dips, financial literacy, reminders) cause drop-offs.
- **Potential Investigation Areas:**
  1. Payment and mandate friction (UPI, e-mandates, bank limits, deduction failures).
  2. Expectations vs. actual experience (volatility shock, short-term negative returns).
  3. Uncertainty and investor confidence.
  4. Changing personal/financial circumstances (job changes, liquidity needs).
  5. Trust, transparency, and reporting clarity.
  6. Customer support and issue resolution.
  7. Product usability and navigation within Groww.
  8. Understanding of SIPs, compounding, and fund mechanics.
  9. Habits, routines, and attention drift.
  10. Information needs and external workarounds.

---

## 3. Core System Architecture & Ingestion Flow
1. **Primary Research Database:** Lightweight local SQLite database (`sip_discovery.db`) storing unified records from CSV, Google Forms, and Chrome Extension.
2. **Ingestion Channels:**
   - **CSV Import (Public Reviews & Feedback):** Flexible field mapping, validation, whitespace trimming, exact & near-duplicate detection, source traceability, and unknown-field marking.
   - **Google Forms Import (Primary Survey Data):** Preserves question-to-answer mapping, anonymous respondent IDs, multi-select checkboxes, and filters by self-reported continuation.
   - **Chrome Extension (Browser-Assisted Research):** Manifest V3 popup to capture selected text, current page URL, timestamp, and source label. Requires user review/edit/approval before saving directly to local backend.
3. **Grok AI Analysis Pipeline (xAI API):**
   - **Relevance Classification:** Directly relevant, Indirectly relevant, Not relevant, Ambiguous (human review required). Includes short evidence excerpt and justification.
   - **Multi-Label Taxonomy (14 Categories):** Covers expectations vs experience, process understanding, uncertainty, mandate friction, changing circumstances, habits, trust, support, usability, reasons for continuing/stopping, etc.
   - **Evidence Extraction:** Verbatim quotes, observable behavior, potential user need, workaround, journey stage, continuation status mentions, missing context.
   - **Prompt Injection Defense:** Input sanitation, treating external text as untrusted data, strict JSON schema output parsing.
   - **Manual Fallback:** Fully operational manual labeling and review if Grok API key is absent or credits are exhausted.

---

## 4. Synthesis, Discovery & Problem Formulation
- **Theme Analysis:** Aggregate evidence by theme, distinguishing record count vs. unique respondents, highlighting supporting vs. contradictory evidence, and identifying unanswered questions.
- **Candidate Problem Statements:** Structured cards separating *Observation* (what data says), *Interpretation* (what it suggests), *Hypothesis* (what requires validation), and *Validated Finding*.
- **Scorecard Prioritization:**
  - Evidence Strength (25%)
  - Relevance to SIP Continuation (25%)
  - User Difficulty / Severity (15%)
  - Potential Product Influence (15%)
  - Feasibility within Project (10%)
  - Safety & Compliance Suitability (10% - acts as a hard filter)
- **Primary Research Guide:** Neutral interview question generator for 5–6 target user interviews based on data gaps.

---

## 5. AI Evidence Log & Evaluation
- **Traceable Audit Log:** Compares AI vs. Human labels (relevance, themes, quotes) with agreement metrics, error categorization, human corrections, and reviewer notes.
- **Evaluation Workflow:** Benchmark on ~20 diverse real records (clear, ambiguous, irrelevant, multi-theme, prompt-injection edge cases) with precision, recall, and F1 tracking.
- **Export Capabilities:** Full export of SQLite records, Evidence Log, themes, problem statements, and methodology documentation as CSV/JSON/Markdown.

---

## 6. Implementation Timeline (3 Weeks, 3-4 Hours/Day)
- **Week 1 (Working Foundation):** Setup SQLite, Streamlit UI, CSV & Google Forms ingestion, deduplication, Grok API integration with connection check, small batch analysis, and manual fallback.
- **Week 2 (Discovery & Evaluation):** Theme grouping, candidate problem statements, scorecard prioritization, AI Evidence Log, human evaluation workflow, and interview question generator.
- **Week 3 (Chrome Extension, Testing & Submission):** Chrome Manifest V3 extension with FastAPI ingestion endpoint, end-to-end testing, methodology documentation, and export for fellowship deliverables.
