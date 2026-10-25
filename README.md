# 📈 AI-Powered SIP Continuation Discovery Engine (Groww Edition)

> **Product Management Fellowship Research Assistant**  
> Investigating why first-time mutual fund investors pause, stop, or drop off from Systematic Investment Plans (SIPs) within their first 12 months.

---

## 🎯 Project Overview & Scope

- **Business Objective:** Increase the percentage of first-time mutual fund investors on Groww who still maintain an active SIP 12 months after starting their first SIP.
- **Active SIP Definition:** At least one successful instalment deduction within the last 30 calendar days.
- **Discovery First:** This system is a **Product Discovery Research Partner**, not an investor-facing advice bot or chatbot.
- **Compliance & Safety Guardrails:** Strictly non-advisory. Does NOT recommend specific funds or stocks, does not use fear/urgency/FOMO nudges, and never collects sensitive credentials (PAN, Aadhaar, bank credentials).

---

## 🚀 Quick Start Guide (Beginner-Friendly)

### 1. Prerequisites
- Python 3.10+ installed on your computer.
- Google Chrome browser (for the optional browser research extension).

### 2. Environment Setup
```powershell
# 1. Clone or navigate to the project directory
cd "c:\Users\anshy\OneDrive\Desktop\Project 3"

# 2. Install required Python packages
pip install -r requirements.txt

# 3. Configure environment variables
# Copy .env.example to .env (if not already done)
# Update GROQ_API_KEY with your key from console.groq.com
```

### 3. Launching the Streamlit Research App
```powershell
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🌐 Chrome Extension Setup (Optional Browser Capture)

The SIP Discovery Chrome Extension allows PM researchers to capture quotes directly from Reddit, Play Store reviews, and Groww community discussions into the local SQLite database with zero friction.

### Step 1: Start the Local Receiver Server
In a separate terminal, launch the local FastAPI receiver:
```powershell
python extension_server/run_server.py
```
*The receiver will run safely on `http://127.0.0.1:8000`.*

### Step 2: Install Extension in Google Chrome
1. Open Google Chrome and go to `chrome://extensions/`.
2. Toggle on **Developer mode** in the top-right corner.
3. Click the **Load unpacked** button in the top-left corner.
4. Select the `chrome_extension` folder located inside this project directory.
5. The **SIP Discovery Assistant** icon (📈) will appear in your Chrome toolbar!

### Step 3: Capture Evidence
1. Browse to any public review or discussion (e.g., Google Play Store Groww reviews, Reddit `r/IndiaInvestments`).
2. Highlight a quote and click the extension icon.
3. Verify the excerpt, review the auto-detected source, and click **Approve & Save**.
4. The record immediately appears in **Browser Inbox** (`pages/7_Browser_Collection.py`)!

---

## 🧭 System Architecture & Discovery Modules

The application is structured into 8 modular discovery pages:

| Module | Location | Purpose |
| :--- | :--- | :--- |
| **1. Overview Dashboard** | `pages/1_Dashboard.py` | High-level metrics, relevance distribution, top themes, and source coverage. |
| **2. Import Data** | `pages/2_Import_Data.py` | CSV uploader for public reviews and Google Forms surveys with SHA-256 deduplication and column mapping. |
| **3. Research Explorer** | `pages/3_Research_Explorer.py` | Filterable evidence cards, controlled batch analysis with Groq, and manual triage. |
| **4. Theme Analysis** | `pages/4_Theme_Analysis.py` | Synthesizes 14 behavioral taxonomy themes, compares reviews vs. surveys, and isolates contradictory signals. |
| **5. Problem Statements** | `pages/5_Problem_Statements.py` | Formulates falsifiable cards (Observation, Interpretation, Hypothesis), 6-factor scorecard, compliance hard filter, and interview guides. |
| **6. AI Evaluation Log** | `pages/6_AI_Evaluation.py` | Human-in-the-loop benchmark, Agreement Rate, per-theme Precision/Recall/F1 with data sufficiency guards. |
| **7. Browser Inbox** | `pages/7_Browser_Collection.py` | Monitors FastAPI receiver health, reviews Chrome extension submissions, and approves quotes for analysis. |
| **8. Export Hub** | `pages/8_Export.py` | One-click downloads for Unified Research CSV, AI Evidence Log, Problem Statements (JSON/MD), and automated Methodology Report. |

---

## ☁️ Production Cloud Deployment (Vercel + Railway)

Continuum AI is architected for seamless separation between static frontend presentation and secure backend execution:

- **Frontend (Vercel):** Serves `index.html` as a high-performance static SPA without build steps. Centralized API routing is managed via `assets/js/config.js`.
- **Backend API (Railway):** Runs FastAPI via Uvicorn (`Procfile`) with environment-configured host, port, and production CORS policies.
- **AI Synthesis (Grok / Groq):** Server-side secret keys are securely injected via Railway's environment dashboard (`GROQ_API_KEY` / `GROK_API_KEY`).
- **Database (PostgreSQL Migration Roadmap):** Local development uses SQLite in `data/sip_discovery.db`. A step-by-step roadmap for migrating to Railway PostgreSQL is documented in [`docs/deployment_guide.md`](docs/deployment_guide.md).

For step-by-step instructions, see the complete [Deployment Guide](docs/deployment_guide.md).

---

## 🧪 Running Unit Tests

Run the full automated test suite covering all discovery modules and deployment configs:
```powershell
python -m unittest discover -s tests
```
*Includes tests for database schema, CSV ingestion, deduplication, Groq client, scoring, evaluation metrics, FastAPI receiver, deployment configuration, and candidate problem audits.*

---

## 🛡️ Research Disclosures & Explicit Non-Goals

1. **No Direct Transaction Access:** We do not possess access to internal Groww transaction ledgers or customer databases.
2. **Signal vs. Causation:** Mention frequencies identify friction signals for qualitative investigation, but do not prove 12-month retention causality.
3. **No Financial Advice:** This tool does not recommend mutual funds or stocks. It is built strictly as a product discovery assistant.
