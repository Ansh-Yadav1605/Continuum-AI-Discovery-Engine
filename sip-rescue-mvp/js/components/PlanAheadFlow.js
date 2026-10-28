/**
 * sip-rescue-mvp/js/components/PlanAheadFlow.js
 * 
 * Flow A: Plan Ahead (Intelligent SIP Assistance)
 * For investors who know in advance that they may not have enough money for their upcoming SIP instalment.
 * 
 * Principles:
 * Understand the situation -> Explain available options -> Let investor choose -> Verify the outcome.
 * 
 * Steps:
 * Step A1: Understand investor need (5 options)
 * Step A2: Understand budget & amount (dynamic presets, percent of SIP, difference, scheme minimum validation)
 * Step A3: Check applicable route (Groww/Zerodha/AMC cutoffs, simulator toggle for deadline passed vs open)
 * Step A4: Present options & evaluate warnings (Case 1: skip confirmed + optional separate investment; Case 2: warning on potential double outflow; Case 3: unverified info notice)
 * Step A5: Summary & Confirmation (independent tracking of regular SIP vs separate investment)
 */

import { SAMPLE_SIPS } from "../data/sampleSips.js?v=3";
import { evaluatePlanAheadRoute, validateOneTimeAmount } from "../data/rulesConfig.js?v=3";

export function renderPlanAheadFlow({
  sip = SAMPLE_SIPS[0],
  initialScenario = null,
  onNavigateHome,
  onViewSipDetails,
  onStartFlexibleContribution,
  onSwitchSip
}) {
  const container = document.createElement("div");
  container.className = "wizard-screen-container plan-ahead-container";

  // State
  let currentStep = "A1"; // 'A1' | 'A2' | 'A3' | 'A4' | 'SUMMARY'
  let selectedNeed = initialScenario?.initialNeed || "cannot_afford";
  let chosenAmount = initialScenario?.suggestedAmount || 1000;
  let customAmountInput = "";
  let isCustomAmount = false;
  
  // Scenario simulation toggle: 'supported_skip' | 'deadline_passed' | 'unverified'
  let scenarioState = initialScenario?.cutoffPassed ? "deadline_passed" : (initialScenario?.scenarioType || "supported_skip");
  
  // Explicit confirmation state for double debit warning
  let doubleDebitAcknowledged = false;

  // Outcome statuses
  let regularSipStatus = "Scheduled"; // 'Confirmed skipped in this demo scenario' | 'Debit may still occur' | 'Scheduled'
  let separateInvestmentStatus = "Not selected"; // 'Not selected' | 'Proposed' | 'Simulated only' | 'Awaiting investor confirmation'
  let finalSeparateInvestmentAmount = 0;

  const NEEDS = [
    {
      id: "cannot_afford",
      title: "I cannot afford the full amount this month",
      desc: "Cash flow tightness; explore temporary skip, pausing, or stepping down.",
      icon: "💰"
    },
    {
      id: "skip",
      title: "I want to skip this month's instalment",
      desc: "Skip only this upcoming instalment while keeping future recurring debits active.",
      icon: "⏭️"
    },
    {
      id: "smaller_amount",
      title: "I want to invest a smaller amount in the same fund",
      desc: "Explore an affordable one-time contribution without altering recurring SIP mandate.",
      icon: "🎯"
    },
    {
      id: "change_future",
      title: "I want to explore changing my future SIP amount",
      desc: "Step down or revise recurring monthly SIP commitment to better fit budget.",
      icon: "📉"
    },
    {
      id: "unsure",
      title: "I am unsure what to do",
      desc: "Compare skip vs pause vs modify options and check applicable deadlines.",
      icon: "❓"
    }
  ];

  function updateView() {
    container.innerHTML = "";
    
    // Top Shared SIP Context Card
    renderSharedContext();

    // Progress stepper
    renderStepper();

    if (currentStep === "A1") {
      renderStepA1();
    } else if (currentStep === "A2") {
      renderStepA2();
    } else if (currentStep === "A3") {
      renderStepA3();
    } else if (currentStep === "A4") {
      renderStepA4();
    } else if (currentStep === "SUMMARY") {
      renderSummary();
    }
  }

  // -------------------------------------------------------------
  // Shared SIP Context
  // -------------------------------------------------------------
  function renderSharedContext() {
    const card = document.createElement("div");
    card.className = "shared-sip-context-card";
    card.innerHTML = `
      <div class="shared-context-header">
        <div class="shared-context-left">
          <span class="amc-badge">${sip.amc}</span>
          <span class="status-badge ${sip.statusTone}">● ${sip.statusTone === 'warning' ? 'Due Soon (Attention)' : 'Active'}</span>
          <span class="demo-badge-pill">Sample Portfolio — Demo Data</span>
        </div>
        <div class="shared-context-right">
          <select id="select-active-sip" class="sip-quick-switcher" title="Switch selected SIP">
            ${SAMPLE_SIPS.map(s => `
              <option value="${s.id}" ${s.id === sip.id ? 'selected' : ''}>
                ${s.schemeName} (₹${s.monthlyAmount.toLocaleString("en-IN")}/mo)
              </option>
            `).join('')}
          </select>
        </div>
      </div>

      <div class="shared-context-body">
        <div>
          <h2 class="shared-scheme-name">${sip.schemeName}</h2>
          <div class="shared-scheme-meta">
            ${sip.planOption} • Frequency: <strong>${sip.frequency}</strong> • Next Debit: <strong class="${sip.statusTone === 'warning' ? 'text-warning' : ''}">${sip.nextDebitRelative} (${sip.nextDebitDate})</strong>
          </div>
        </div>

        <div class="shared-meta-pills">
          <div class="meta-pill-item">
            <span class="meta-pill-label">Regular SIP:</span>
            <span class="meta-pill-val">₹${sip.monthlyAmount.toLocaleString("en-IN")}</span>
          </div>
          <div class="meta-pill-item">
            <span class="meta-pill-label">Platform:</span>
            <span class="meta-pill-val">${sip.platform} (${sip.mandateMethod})</span>
          </div>
          <div class="meta-pill-item">
            <span class="meta-pill-label">Scheme Min:</span>
            <span class="meta-pill-val">₹${sip.minLumpSumAmount || 100} lump-sum</span>
          </div>
        </div>
      </div>

      <div class="shared-context-footer">
        <span class="context-reassurance-note">
          🔒 <strong>Simulated Context:</strong> This prototype does not access your bank account, alter mandates, or place real transactions.
        </span>
        <a href="${sip.officialHelpUrl || sip.amcWebsite}" target="_blank" rel="noopener noreferrer" class="context-help-link">
          Official ${sip.platform} Rule Source ↗
        </a>
      </div>
    `;

    card.querySelector("#select-active-sip").addEventListener("change", (e) => {
      const selectedId = e.target.value;
      const newSip = SAMPLE_SIPS.find(s => s.id === selectedId);
      if (newSip && onSwitchSip) {
        onSwitchSip(newSip);
      }
    });

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // Stepper Header
  // -------------------------------------------------------------
  function renderStepper() {
    const stepperWrapper = document.createElement("div");
    stepperWrapper.className = "wizard-progress-bar";
    const steps = [
      { id: "A1", label: "1. Need" },
      { id: "A2", label: "2. Budget" },
      { id: "A3", label: "3. Route Check" },
      { id: "A4", label: "4. Options & Action" },
      { id: "SUMMARY", label: "5. Outcome" }
    ];

    const currentIdx = steps.findIndex(s => s.id === currentStep);

    stepperWrapper.innerHTML = `
      <div class="wizard-stepper">
        ${steps.map((st, idx) => `
          <div class="stepper-item ${st.id === currentStep ? 'active' : (idx < currentIdx ? 'completed' : '')}">
            <span class="stepper-number">${idx + 1}</span>
            <span class="stepper-label">${st.label}</span>
          </div>
          ${idx < steps.length - 1 ? '<div class="stepper-arrow">→</div>' : ''}
        `).join('')}
      </div>
    `;
    container.appendChild(stepperWrapper);
  }

  // -------------------------------------------------------------
  // STEP A1: Understand Investor Need
  // -------------------------------------------------------------
  function renderStepA1() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    card.innerHTML = `
      <div class="wizard-header-section">
        <div class="wizard-badge-indicator">Flow A: Plan Ahead</div>
        <h2 class="wizard-question-title">What would you like to do about your upcoming SIP?</h2>
        <p class="wizard-question-desc">
          Plan ahead before your scheduled debit date (${sip.nextDebitRelative}). Choose the option that fits best:
        </p>
      </div>

      <div class="selectable-cards-grid">
        ${NEEDS.map(n => `
          <div class="select-card ${selectedNeed === n.id ? 'selected' : ''}" data-need-id="${n.id}" tabindex="0" role="button">
            <div class="select-card-icon">${n.icon}</div>
            <div class="select-card-body">
              <div class="select-card-title">${n.title}</div>
              <div class="select-card-sub">${n.desc}</div>
            </div>
          </div>
        `).join('')}
      </div>

      <div class="wizard-actions-bar">
        <button class="btn btn-subtle" id="btn-a1-back">← Back to Overview</button>
        <button class="btn btn-primary" id="btn-a1-continue">
          <span>Continue →</span>
        </button>
      </div>
    `;

    card.querySelectorAll(".select-card").forEach(el => {
      const handleSelect = () => {
        card.querySelectorAll(".select-card").forEach(c => c.classList.remove("selected"));
        el.classList.add("selected");
        selectedNeed = el.getAttribute("data-need-id");
      };
      el.addEventListener("click", handleSelect);
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handleSelect();
        }
      });
    });

    card.querySelector("#btn-a1-back").addEventListener("click", () => onNavigateHome());
    card.querySelector("#btn-a1-continue").addEventListener("click", () => {
      // If investor wants smaller amount or budget planning, go to Step A2
      // If investor selected change future, we explain future settings
      currentStep = "A2";
      updateView();
    });

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // STEP A2: Understand Their Budget
  // -------------------------------------------------------------
  function renderStepA2() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    const regAmount = sip.monthlyAmount;
    const presets = [500, 1000, 1500, regAmount];
    const validation = validateOneTimeAmount(chosenAmount, sip);

    card.innerHTML = `
      <div class="wizard-header-section">
        <div class="wizard-badge-indicator">Step A2: Budget & Affordability</div>
        <h2 class="wizard-question-title">How much can you comfortably invest this month?</h2>
        <p class="wizard-question-desc">
          Choose an amount that fits your current financial situation. You do not need to stretch your budget.
        </p>
      </div>

      <!-- Comparison Metrics Card -->
      <div class="budget-comparison-panel">
        <div class="budget-comparison-col">
          <span class="budget-col-label">Regular Monthly SIP:</span>
          <span class="budget-col-val">₹${regAmount.toLocaleString("en-IN")}</span>
        </div>
        <div class="budget-comparison-col highlight">
          <span class="budget-col-label">Preferred One-Time Investment:</span>
          <span class="budget-col-val" id="display-chosen-amount">₹${Number(chosenAmount).toLocaleString("en-IN")}</span>
          <span class="budget-col-percent" id="display-chosen-percent">(${validation.percent}% of regular SIP)</span>
        </div>
        <div class="budget-comparison-col">
          <span class="budget-col-label">Difference from usual amount:</span>
          <span class="budget-col-val" id="display-difference" style="color: var(--primary);">₹${Number(validation.difference).toLocaleString("en-IN")} saved</span>
        </div>
      </div>

      <!-- Quick Preset Chips -->
      <div class="form-group" style="margin-top: 24px;">
        <label class="form-label">Select an affordable one-time amount:</label>
        <div class="budget-chips-row">
          ${presets.map(val => `
            <button type="button" class="budget-chip ${!isCustomAmount && chosenAmount === val ? 'active' : ''}" data-val="${val}">
              <span class="chip-amt">₹${val.toLocaleString("en-IN")}</span>
              <span class="chip-note">${val === regAmount ? 'Full Scheduled' : Math.round((val / regAmount) * 100) + '% of SIP'}</span>
            </button>
          `).join('')}
          <button type="button" class="budget-chip ${isCustomAmount ? 'active' : ''}" id="btn-custom-chip">
            <span class="chip-amt">Custom</span>
            <span class="chip-note">Enter amount</span>
          </button>
        </div>
      </div>

      <!-- Custom Amount Input if Selected -->
      <div class="form-group" id="custom-amount-wrapper" style="display: ${isCustomAmount ? 'block' : 'none'};">
        <label class="form-label" for="input-custom-amount">Enter custom one-time amount (₹):</label>
        <div class="input-with-prefix">
          <span class="input-prefix">₹</span>
          <input 
            type="number" 
            id="input-custom-amount" 
            class="form-input" 
            value="${chosenAmount}" 
            min="${sip.minLumpSumAmount || 100}" 
            step="100" 
            placeholder="e.g. 750" 
          />
        </div>
        <div class="form-help">
          Official scheme minimum for additional purchase: ₹${(sip.minLumpSumAmount || 100).toLocaleString("en-IN")}.
        </div>
      </div>

      <!-- Validation Error / Notice -->
      <div id="validation-notice-box" class="form-validation-alert" style="display: ${validation.isValid ? 'none' : 'flex'};">
        <span>⚠️</span>
        <span id="validation-notice-text">${validation.message || ''}</span>
      </div>

      <!-- Reassurance Banner -->
      <div class="guidance-feature-card" style="margin-top: 20px; border-left: 4px solid var(--primary);">
        <div style="font-size: 13px; color: var(--text-body); line-height: 1.5;">
          💡 <strong>Flexible Contribution Principle:</strong> Exploring a smaller one-time contribution is completely voluntary. It gives you flexibility without cancelling your mutual fund SIP or breaking investment discipline.
        </div>
      </div>

      <div class="wizard-actions-bar">
        <button class="btn btn-secondary" id="btn-a2-back">← Change Need</button>
        <button class="btn btn-primary" id="btn-a2-continue" ${!validation.isValid ? 'disabled' : ''}>
          <span>Check Applicable Route →</span>
        </button>
      </div>
    `;

    // Chip click handlers
    card.querySelectorAll(".budget-chip[data-val]").forEach(btn => {
      btn.addEventListener("click", () => {
        isCustomAmount = false;
        chosenAmount = Number(btn.getAttribute("data-val"));
        updateA2Metrics(card);
      });
    });

    const btnCustomChip = card.querySelector("#btn-custom-chip");
    const customWrapper = card.querySelector("#custom-amount-wrapper");
    const customInput = card.querySelector("#input-custom-amount");

    btnCustomChip.addEventListener("click", () => {
      isCustomAmount = true;
      customWrapper.style.display = "block";
      card.querySelectorAll(".budget-chip").forEach(c => c.classList.remove("active"));
      btnCustomChip.classList.add("active");
      customInput.focus();
    });

    customInput.addEventListener("input", (e) => {
      const val = Number(e.target.value);
      chosenAmount = val;
      updateA2Metrics(card);
    });

    function updateA2Metrics(root) {
      const v = validateOneTimeAmount(chosenAmount, sip);
      root.querySelectorAll(".budget-chip").forEach(c => {
        if (!isCustomAmount && Number(c.getAttribute("data-val")) === chosenAmount) {
          c.classList.add("active");
        } else if (isCustomAmount && c.id === "btn-custom-chip") {
          c.classList.add("active");
        } else {
          c.classList.remove("active");
        }
      });

      root.querySelector("#display-chosen-amount").textContent = `₹${Number(chosenAmount || 0).toLocaleString("en-IN")}`;
      root.querySelector("#display-chosen-percent").textContent = `(${v.percent}% of regular SIP)`;
      root.querySelector("#display-difference").textContent = `₹${Number(v.difference).toLocaleString("en-IN")} saved`;

      const noticeBox = root.querySelector("#validation-notice-box");
      const noticeText = root.querySelector("#validation-notice-text");
      const btnCont = root.querySelector("#btn-a2-continue");

      if (!v.isValid) {
        noticeBox.style.display = "flex";
        noticeText.textContent = v.message;
        btnCont.disabled = true;
      } else {
        noticeBox.style.display = "none";
        btnCont.disabled = false;
      }
    }

    card.querySelector("#btn-a2-back").addEventListener("click", () => {
      currentStep = "A1";
      updateView();
    });

    card.querySelector("#btn-a2-continue").addEventListener("click", () => {
      currentStep = "A3";
      updateView();
    });

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // STEP A3: Check Applicable Route & Deadline
  // -------------------------------------------------------------
  function renderStepA3() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    const routeEvaluation = evaluatePlanAheadRoute({
      sip,
      action: selectedNeed,
      scenarioState,
      chosenAmount
    });

    card.innerHTML = `
      <div class="wizard-header-section">
        <div class="wizard-badge-indicator">Step A3: Route & Deadline Verification</div>
        <h2 class="wizard-question-title">Checking the applicable platform rules for this change</h2>
        <p class="wizard-question-desc">
          We check whether your platform, mandate type, and debit timing allow skipping or modifying this upcoming instalment.
        </p>
      </div>

      <!-- Assessor Simulation Toggle (Explicitly supports Acceptance Tests A, B, C) -->
      <div class="assessor-scenario-simulator-box">
        <div class="simulator-header">
          <span>⚙️ Prototype Scenario Controller (Test Different Outcomes):</span>
        </div>
        <div class="simulator-options-row">
          <label class="simulator-option ${scenarioState === 'supported_skip' ? 'active' : ''}">
            <input type="radio" name="sim-scenario" value="supported_skip" ${scenarioState === 'supported_skip' ? 'checked' : ''} />
            <span><strong>Supported Skip Window</strong> (≥2 days notice, skip supported with ₹0 fee)</span>
          </label>
          <label class="simulator-option ${scenarioState === 'deadline_passed' ? 'active' : ''}">
            <input type="radio" name="sim-scenario" value="deadline_passed" ${scenarioState === 'deadline_passed' ? 'checked' : ''} />
            <span><strong>Deadline Passed (&lt;24h)</strong> (Regular debit may still be processed — Warning)</span>
          </label>
          <label class="simulator-option ${scenarioState === 'unverified' ? 'active' : ''}">
            <input type="radio" name="sim-scenario" value="unverified" ${scenarioState === 'unverified' ? 'checked' : ''} />
            <span><strong>Unverified Platform Policy</strong> (Missing rules; verify with AMC)</span>
          </label>
        </div>
      </div>

      <!-- Dynamic Verification Checklist -->
      <div class="route-verification-grid">
        <div class="route-check-card ${routeEvaluation.isScheduled ? 'pass' : 'fail'}">
          <div class="check-icon">${routeEvaluation.isScheduled ? '✓' : '✗'}</div>
          <div>
            <div class="check-title">Upcoming Debit Scheduled</div>
            <div class="check-sub">${sip.nextDebitDate} (${sip.nextDebitRelative})</div>
          </div>
        </div>

        <div class="route-check-card ${routeEvaluation.deadlineStatus === 'WINDOW_OPEN' ? 'pass' : (routeEvaluation.deadlineStatus === 'DEADLINE_PASSED' ? 'warning' : 'unknown')}">
          <div class="check-icon">${routeEvaluation.deadlineStatus === 'WINDOW_OPEN' ? '✓' : (routeEvaluation.deadlineStatus === 'DEADLINE_PASSED' ? '⚠️' : '?')}</div>
          <div>
            <div class="check-title">Modification / Skip Cutoff</div>
            <div class="check-sub">${routeEvaluation.deadlineStatus === 'WINDOW_OPEN' ? 'Open (≥ 2 working days)' : (routeEvaluation.deadlineStatus === 'DEADLINE_PASSED' ? 'Cutoff may have passed' : 'Cutoff unconfirmed')}</div>
          </div>
        </div>

        <div class="route-check-card ${sip.platform === 'Groww' || sip.platform === 'Zerodha Coin' ? 'pass' : 'unknown'}">
          <div class="check-icon">${sip.platform === 'Groww' || sip.platform === 'Zerodha Coin' ? '✓' : '?'}</div>
          <div>
            <div class="check-title">Platform Support Verified</div>
            <div class="check-sub">${sip.platform} official documentation checked</div>
          </div>
        </div>

        <div class="route-check-card pass">
          <div class="check-icon">✓</div>
          <div>
            <div class="check-title">Mandate & Scheme Compatibility</div>
            <div class="check-sub">${sip.mandateMethod} (${sip.setupType})</div>
          </div>
        </div>
      </div>

      <!-- Real-time Rule Finding Box -->
      <div class="rule-evaluation-summary-box ${routeEvaluation.routeCase === 'CASE_DEADLINE_PASSED' ? 'warning-box' : (routeEvaluation.routeCase === 'CASE_UNVERIFIED' ? 'info-box' : 'safe-box')}">
        <div class="eval-box-icon">
          ${routeEvaluation.routeCase === 'CASE_DEADLINE_PASSED' ? '⚠️' : (routeEvaluation.routeCase === 'CASE_UNVERIFIED' ? 'ℹ️' : '✅')}
        </div>
        <div class="eval-box-content">
          <div class="eval-box-title">
            ${routeEvaluation.routeCase === 'CASE_DEADLINE_PASSED' 
              ? 'Notice Window Advisory: Regular debit may still be attempted' 
              : (routeEvaluation.routeCase === 'CASE_UNVERIFIED' 
                  ? 'We could not confirm whether this change can affect your upcoming instalment' 
                  : 'Skip Route Supported on ' + sip.platform)}
          </div>
          <p class="eval-box-desc">
            ${routeEvaluation.routeCase === 'CASE_DEADLINE_PASSED'
              ? 'Groww AutoPay and BSE StAR MF mandates require at least 2 working days prior notice. Because the debit is approaching, your bank may still present the scheduled amount.'
              : (routeEvaluation.routeCase === 'CASE_UNVERIFIED'
                  ? 'Please check the applicable platform or AMC instructions before proceeding. We do not assume automated skips are processed without verified rules.'
                  : 'You may request an instalment skip with ₹0 platform charges. Your SIP mandate will remain active for future months.')}
          </p>
        </div>
      </div>

      <div class="wizard-actions-bar">
        <button class="btn btn-secondary" id="btn-a3-back">← Adjust Budget</button>
        <button class="btn btn-primary" id="btn-a3-continue">
          <span>See Available Options →</span>
        </button>
      </div>
    `;

    card.querySelectorAll("input[name='sim-scenario']").forEach(radio => {
      radio.addEventListener("change", (e) => {
        scenarioState = e.target.value;
        renderStepA3();
      });
    });

    card.querySelector("#btn-a3-back").addEventListener("click", () => {
      currentStep = "A2";
      updateView();
    });

    card.querySelector("#btn-a3-continue").addEventListener("click", () => {
      currentStep = "A4";
      updateView();
    });

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // STEP A4: Present Appropriate Options & Warnings
  // -------------------------------------------------------------
  function renderStepA4() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    const routeEvaluation = evaluatePlanAheadRoute({
      sip,
      action: selectedNeed,
      scenarioState,
      chosenAmount
    });

    if (routeEvaluation.routeCase === "CASE_SUPPORTED_SKIP") {
      // ---------------------------------------------------------
      // CASE 1: Supported Skip Route is Available
      // ---------------------------------------------------------
      card.innerHTML = `
        <div class="wizard-header-section">
          <div class="wizard-badge-indicator" style="background-color: var(--primary-light); color: var(--primary);">Case 1: Supported Skip Route Available</div>
          <h2 class="wizard-question-title">Your SIP Skip Route is Supported</h2>
          <p class="wizard-question-desc">
            You can request an instalment skip on ${sip.platform} before the debit cut-off. Your recurring mandate stays active with ₹0 platform fees.
          </p>
        </div>

        <!-- Simulated Confirmed Skip Banner -->
        <div class="demo-scenario-action-card">
          <div class="demo-action-icon">⏭️</div>
          <div>
            <div class="demo-action-heading">Instalment Skip Simulated in Demo Scenario</div>
            <div class="demo-action-sub">
              Your upcoming SIP instalment of ₹${sip.monthlyAmount.toLocaleString("en-IN")} on ${sip.nextDebitDate} has been skipped in this demo scenario.
            </div>
          </div>
        </div>

        <!-- Voluntary Flexible Contribution Offer -->
        <div class="voluntary-contribution-box">
          <div class="vol-box-header">
            <span class="vol-badge">Flexible Contribution (Optional)</span>
            <h3 class="vol-title">Would you like to explore a separate investment of ₹${Number(chosenAmount).toLocaleString("en-IN")} in the same fund?</h3>
          </div>
          <p class="vol-desc">
            This would be a completely separate one-time purchase in <strong>${sip.schemeName}</strong>. It does not replace or alter your recurring SIP schedule.
          </p>

          <div class="vol-breakdown-row">
            <div>
              <span class="vol-meta-label">Selected Amount:</span>
              <span class="vol-meta-val">₹${Number(chosenAmount).toLocaleString("en-IN")}</span>
            </div>
            <div>
              <span class="vol-meta-label">Investment Type:</span>
              <span class="vol-meta-val">1-Time Purchase (Direct Plan)</span>
            </div>
            <div>
              <span class="vol-meta-label">Recurring SIP:</span>
              <span class="vol-meta-val" style="color: var(--primary);">Remains Skipped</span>
            </div>
          </div>

          <div class="vol-cta-buttons">
            <button class="btn btn-primary" id="btn-explore-separate-inv">
              <span>Explore ₹${Number(chosenAmount).toLocaleString("en-IN")} investment →</span>
            </button>
            <button class="btn btn-secondary" id="btn-no-additional-inv">
              <span>No additional investment</span>
            </button>
            <button class="btn btn-subtle" id="btn-view-sip-details-a4">
              <span>View SIP details</span>
            </button>
          </div>
        </div>
      `;

      card.querySelector("#btn-explore-separate-inv").addEventListener("click", () => {
        regularSipStatus = "Confirmed skipped in this demo scenario";
        separateInvestmentStatus = "Simulated only";
        finalSeparateInvestmentAmount = chosenAmount;
        currentStep = "SUMMARY";
        updateView();
      });

      card.querySelector("#btn-no-additional-inv").addEventListener("click", () => {
        regularSipStatus = "Confirmed skipped in this demo scenario";
        separateInvestmentStatus = "Not selected";
        finalSeparateInvestmentAmount = 0;
        currentStep = "SUMMARY";
        updateView();
      });

      card.querySelector("#btn-view-sip-details-a4").addEventListener("click", () => {
        if (onViewSipDetails) onViewSipDetails(sip);
      });

    } else if (routeEvaluation.routeCase === "CASE_DEADLINE_PASSED") {
      // ---------------------------------------------------------
      // CASE 2: The Skip or Modification Deadline May Have Passed
      // ---------------------------------------------------------
      const scheduledAmt = sip.monthlyAmount;
      const proposedAmt = chosenAmount;
      const potentialTotal = scheduledAmt + proposedAmt;

      card.innerHTML = `
        <div class="wizard-header-section">
          <div class="wizard-badge-indicator" style="background-color: var(--warning-bg); color: var(--warning-text);">Case 2: Notice Window Passed</div>
          <h2 class="wizard-question-title text-warning">Notice: Modification Deadline May Have Passed</h2>
          <p class="wizard-question-desc">
            Your upcoming instalment is scheduled in less than 48 hours. Please review the potential total outflow before deciding on any separate investment.
          </p>
        </div>

        <!-- Prominent Warning Banner -->
        <div class="prominent-warning-card">
          <div class="warning-header-row">
            <span class="warning-large-icon">⚠️</span>
            <div>
              <h3 class="warning-headline">Your regular SIP debit may still be processed.</h3>
              <p class="warning-subtext">
                Because bank presentation batches run 2 working days in advance, a skip or pause submitted right now may only take effect for the following month.
              </p>
            </div>
          </div>

          <!-- Outflow Calculation Table -->
          <div class="outflow-calculation-box">
            <div class="outflow-calc-header">
              <span>Potential Outflow Analysis (If you make an additional investment):</span>
            </div>
            <div class="outflow-calc-row">
              <span class="calc-label">Scheduled Regular SIP (May still debit):</span>
              <span class="calc-val">₹${scheduledAmt.toLocaleString("en-IN")}</span>
            </div>
            <div class="outflow-calc-row">
              <span class="calc-label">Proposed Additional Investment:</span>
              <span class="calc-val">+ ₹${proposedAmt.toLocaleString("en-IN")}</span>
            </div>
            <div class="outflow-divider"></div>
            <div class="outflow-calc-row total-row">
              <span class="calc-label"><strong>Potential Total Outflow:</strong></span>
              <span class="calc-val total-amt">₹${potentialTotal.toLocaleString("en-IN")}</span>
            </div>
            <div class="outflow-disclaimer-tag">
              * Note: Labelled as a potential total outflow, not a confirmed debit.
            </div>
          </div>
        </div>

        <!-- Explicit Confirmation Checkbox Required Before Proceeding -->
        <div class="explicit-confirmation-block">
          <label class="confirmation-checkbox-label">
            <input type="checkbox" id="chk-acknowledge-double-debit" ${doubleDebitAcknowledged ? 'checked' : ''} />
            <span>
              I understand that my scheduled SIP of ₹${scheduledAmt.toLocaleString("en-IN")} may still be debited, and any separate investment could increase my total monthly outflow up to ₹${potentialTotal.toLocaleString("en-IN")}.
            </span>
          </label>
        </div>

        <div class="wizard-actions-bar" style="flex-wrap: wrap; gap: 12px;">
          <button class="btn btn-secondary" id="btn-review-platform-rules">
            Review Platform Rules ↗
          </button>
          <button class="btn btn-secondary" id="btn-contact-amc">
            Contact AMC (${sip.amcShort})
          </button>
          <button class="btn btn-primary" id="btn-proceed-with-warning" ${!doubleDebitAcknowledged ? 'disabled' : ''}>
            <span>Confirm & Continue With ₹${proposedAmt.toLocaleString("en-IN")} →</span>
          </button>
          <button class="btn btn-subtle" id="btn-return-no-investment">
            No Additional Investment (Return to Details)
          </button>
        </div>
      `;

      const chk = card.querySelector("#chk-acknowledge-double-debit");
      const btnProceed = card.querySelector("#btn-proceed-with-warning");

      chk.addEventListener("change", (e) => {
        doubleDebitAcknowledged = e.target.checked;
        btnProceed.disabled = !doubleDebitAcknowledged;
      });

      card.querySelector("#btn-review-platform-rules").addEventListener("click", () => {
        window.open(sip.officialHelpUrl || "https://groww.in/help/mutual-funds/sip", "_blank");
      });

      card.querySelector("#btn-contact-amc").addEventListener("click", () => {
        window.open(sip.amcWebsite, "_blank");
      });

      btnProceed.addEventListener("click", () => {
        regularSipStatus = "Debit may still occur";
        separateInvestmentStatus = "Simulated only";
        finalSeparateInvestmentAmount = chosenAmount;
        currentStep = "SUMMARY";
        updateView();
      });

      card.querySelector("#btn-return-no-investment").addEventListener("click", () => {
        regularSipStatus = "Debit may still occur";
        separateInvestmentStatus = "Not selected";
        finalSeparateInvestmentAmount = 0;
        currentStep = "SUMMARY";
        updateView();
      });

    } else {
      // ---------------------------------------------------------
      // CASE 3: Route Cannot Be Verified
      // ---------------------------------------------------------
      card.innerHTML = `
        <div class="wizard-header-section">
          <div class="wizard-badge-indicator" style="background-color: var(--info-bg); color: var(--info-text);">Case 3: Unverified Route</div>
          <h2 class="wizard-question-title">We Could Not Confirm This Route</h2>
          <p class="wizard-question-desc">
            We could not confirm whether this change can affect your upcoming instalment. Please check the applicable platform or AMC instructions before proceeding.
          </p>
        </div>

        <div class="unverified-guidance-card">
          <div class="unverified-icon">❓</div>
          <div>
            <h3 class="unverified-title">What Information is Missing:</h3>
            <ul class="unverified-list">
              <li>Platform-specific cutoff timeline for ${sip.platform} with ${sip.mandateMethod}.</li>
              <li>Whether a skip facility is enabled by ${sip.amc} for this folio.</li>
            </ul>
            <div style="margin-top: 14px;">
              <strong>Where you can check:</strong> Visit your ${sip.platform} account under SIP Details &gt; Manage SIP, or check directly on the official ${sip.amc} portal.
            </div>
          </div>
        </div>

        <div class="demo-disclaimer-box" style="margin-top: 20px;">
          <div>🔒</div>
          <div>
            <strong>Transparent Principle:</strong> SIP Rescue Navigator never displays a guaranteed skip, cancellation, or investment outcome when rules cannot be verified.
          </div>
        </div>

        <div class="wizard-actions-bar">
          <button class="btn btn-secondary" id="btn-back-to-a3">← Change Scenario</button>
          <button class="btn btn-secondary" id="btn-visit-amc">Visit AMC Portal ↗</button>
          <button class="btn btn-primary" id="btn-finish-unverified">
            <span>View Summary →</span>
          </button>
        </div>
      `;

      card.querySelector("#btn-back-to-a3").addEventListener("click", () => {
        currentStep = "A3";
        updateView();
      });

      card.querySelector("#btn-visit-amc").addEventListener("click", () => {
        window.open(sip.amcWebsite, "_blank");
      });

      card.querySelector("#btn-finish-unverified").addEventListener("click", () => {
        regularSipStatus = "Payment status unknown";
        separateInvestmentStatus = "Not selected";
        finalSeparateInvestmentAmount = 0;
        currentStep = "SUMMARY";
        updateView();
      });
    }

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // STEP A5 / SUMMARY: Final Outcome & Independent Statuses
  // -------------------------------------------------------------
  function renderSummary() {
    const card = document.createElement("div");
    card.className = "wizard-main-card summary-card";

    card.innerHTML = `
      <div class="wizard-header-section" style="text-align: center; margin-bottom: 24px;">
        <div style="font-size: 38px; margin-bottom: 8px;">📋</div>
        <h2 class="wizard-question-title" style="font-size: 24px;">Your SIP Rescue Summary</h2>
        <p class="wizard-question-desc">
          Summary of your planned assistance session. Transaction statuses are tracked independently.
        </p>
      </div>

      <!-- Two Independent Transaction Statuses Display -->
      <div class="status-comparison-grid">
        <!-- 1. Regular SIP Instalment Status -->
        <div class="status-box regular-sip-box">
          <div class="status-box-header">
            <span class="status-box-tag">Regular Recurring SIP</span>
            <span class="status-badge ${regularSipStatus.includes('skipped') ? 'normal' : (regularSipStatus.includes('may still occur') ? 'warning' : 'info')}">
              ${regularSipStatus}
            </span>
          </div>
          <div class="status-box-fund">${sip.schemeName}</div>
          <div class="status-box-row">
            <span>Usual SIP Amount:</span>
            <strong>₹${sip.monthlyAmount.toLocaleString("en-IN")} / month</strong>
          </div>
          <div class="status-box-row">
            <span>Upcoming Debit Date:</span>
            <span>${sip.nextDebitDate} (${sip.nextDebitRelative})</span>
          </div>
          <div class="status-box-desc">
            ${regularSipStatus.includes('skipped') 
              ? 'Confirmed skipped in this demo scenario. Your recurring mandate remains active for subsequent months.' 
              : (regularSipStatus.includes('may still occur')
                  ? 'Cutoff window was passed. The regular debit of ₹' + sip.monthlyAmount.toLocaleString('en-IN') + ' may still occur on debit day.'
                  : 'Recurring mandate status remains under review.')}
          </div>
        </div>

        <!-- 2. Separate Investment Status -->
        <div class="status-box separate-inv-box">
          <div class="status-box-header">
            <span class="status-box-tag">Separate One-Time Investment</span>
            <span class="status-badge ${separateInvestmentStatus === 'Simulated only' ? 'normal' : 'info'}">
              ${separateInvestmentStatus}
            </span>
          </div>
          <div class="status-box-fund">${sip.schemeName} (One-Time)</div>
          <div class="status-box-row">
            <span>One-Time Contribution:</span>
            <strong>${finalSeparateInvestmentAmount > 0 ? '₹' + finalSeparateInvestmentAmount.toLocaleString('en-IN') : 'No additional investment selected'}</strong>
          </div>
          <div class="status-box-row">
            <span>Execution Type:</span>
            <span>${finalSeparateInvestmentAmount > 0 ? 'Simulated only (Demo)' : 'None'}</span>
          </div>
          <div class="status-box-desc">
            ${finalSeparateInvestmentAmount > 0 
              ? 'Voluntary 1-time purchase simulated in demo mode. This does not replace your recurring SIP.'
              : 'No separate lump-sum purchase was made. You can review your budget anytime.'}
          </div>
        </div>
      </div>

      <!-- Schedule & Details Summary Table -->
      <div class="summary-details-card">
        <h3 class="summary-card-subheading">Portfolio & Commitment Details</h3>
        <div class="summary-table-rows">
          <div class="summary-table-row">
            <span class="row-label">Mutual Fund:</span>
            <span class="row-val"><strong>${sip.schemeName}</strong> (${sip.amc})</span>
          </div>
          <div class="summary-table-row">
            <span class="row-label">Usual Monthly SIP:</span>
            <span class="row-val">₹${sip.monthlyAmount.toLocaleString("en-IN")} per month</span>
          </div>
          <div class="summary-table-row">
            <span class="row-label">Preferred One-Time Investment:</span>
            <span class="row-val">${finalSeparateInvestmentAmount > 0 ? '₹' + finalSeparateInvestmentAmount.toLocaleString('en-IN') : 'No additional investment selected'}</span>
          </div>
          <div class="summary-table-row">
            <span class="row-label">Regular SIP Status:</span>
            <span class="row-val">${regularSipStatus}</span>
          </div>
          <div class="summary-table-row">
            <span class="row-label">Separate Investment Status:</span>
            <span class="row-val">${separateInvestmentStatus}</span>
          </div>
          <div class="summary-table-row">
            <span class="row-label">Next Regular SIP Scheduled:</span>
            <span class="row-val">${sip.nextDebitDate ? sip.nextDebitDate + ' (Subject to platform schedule)' : 'Schedule not available'}</span>
          </div>
        </div>
      </div>

      <!-- Mandatory Prototype Disclaimer -->
      <div class="demo-disclaimer-box" style="margin-top: 24px;">
        <div style="font-size: 16px;">ℹ️</div>
        <div>
          <strong>Product Demonstration Disclaimer:</strong>
          This is a product demonstration. No real mutual fund investment, bank debit, SIP skip, cancellation, or mandate modification has occurred.
        </div>
      </div>

      <!-- Summary Actions Bar -->
      <div class="wizard-actions-bar" style="margin-top: 28px;">
        <button class="btn btn-secondary" id="btn-summary-overview">
          ← Back to Overview
        </button>
        <button class="btn btn-secondary" id="btn-summary-details">
          View SIP Details
        </button>
        <button class="btn btn-primary" id="btn-summary-another">
          <span>Explore Another Option</span>
        </button>
      </div>
    `;

    card.querySelector("#btn-summary-overview").addEventListener("click", () => onNavigateHome());
    card.querySelector("#btn-summary-details").addEventListener("click", () => {
      if (onViewSipDetails) onViewSipDetails(sip);
    });
    card.querySelector("#btn-summary-another").addEventListener("click", () => {
      currentStep = "A1";
      updateView();
    });

    container.appendChild(card);
  }

  updateView();
  return container;
}
