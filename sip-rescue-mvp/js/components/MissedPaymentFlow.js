/**
 * sip-rescue-mvp/js/components/MissedPaymentFlow.js
 * 
 * Flow B: Missed Payment Rescue (Intelligent SIP Assistance)
 * For investors whose scheduled SIP payment was not debited or whose payment status is uncertain.
 * 
 * Principles:
 * Understand the situation -> Explain available options -> Let investor choose -> Verify the outcome.
 * 
 * Steps:
 * Step B1: Identify the payment status (5 distinct options: insufficient funds, mandate failed, requested skip, unknown reason, uncertain debit)
 * Step B2: Explain the status (factual, non-judgmental, distinguishes failure from deliberate skip, rule of 3 failures)
 * Step B3: Offer choices (No additional investment, explore smaller one-time purchase, review future SIP settings, contact platform/AMC)
 * Step B4: Check for possible repeat debit (prominently warns about pending debit attempts before any separate investment)
 * Step B5 / Summary: Final outcome & independent statuses
 */

import { SAMPLE_SIPS } from "../data/sampleSips.js?v=3";
import { evaluateMissedPaymentStatus, validateOneTimeAmount } from "../data/rulesConfig.js?v=3";

export function renderMissedPaymentFlow({
  sip = SAMPLE_SIPS[0],
  initialScenario = null,
  onNavigateHome,
  onViewSipDetails,
  onSwitchSip,
  onNavigateComeback
}) {
  const container = document.createElement("div");
  container.className = "wizard-screen-container missed-payment-container";

  // State
  let currentStep = "B1"; // 'B1' | 'B2_CHOICES' | 'B4_REPEAT_CHECK' | 'BUDGET_INPUT' | 'SUMMARY' | 'FUTURE_SETTINGS'
  let selectedReasonKey = initialScenario?.missedReason || "insufficient_funds";
  let selectedChoice = "no_investment"; // 'no_investment' | 'explore_smaller' | 'future_settings' | 'contact_platform'
  let chosenAmount = 1000;
  let isCustomAmount = false;
  let repeatDebitAcknowledged = false;

  // Outcome statuses
  let regularSipStatus = "Payment failed in this demo scenario";
  let separateInvestmentStatus = "Not selected";
  let finalSeparateInvestmentAmount = 0;

  const REASONS = [
    {
      key: "insufficient_funds",
      title: "The debit did not happen because I had insufficient funds.",
      desc: "Bank balance was lower than the scheduled SIP amount on the scheduled date.",
      icon: "💳"
    },
    {
      key: "mandate_failed",
      title: "The payment or mandate failed.",
      desc: "Technical presentation issue, expired mandate, or banking channel failure.",
      icon: "⚠️"
    },
    {
      key: "requested_skip_earlier",
      title: "I requested a skip earlier.",
      desc: "Submitted a skip request on the app and want to verify if it took effect.",
      icon: "⏭️"
    },
    {
      key: "unknown_reason",
      title: "The amount has not been debited, but I do not know why.",
      desc: "Date has passed with no deduction in bank account, reason unclear.",
      icon: "❓"
    },
    {
      key: "uncertain_processing",
      title: "I am not sure whether the payment was processed.",
      desc: "Uncertain if money was debited or if units are awaiting allotment.",
      icon: "🔍"
    }
  ];

  function updateView() {
    container.innerHTML = "";
    
    // Shared SIP Context Card
    renderSharedContext();

    // Progress stepper
    renderStepper();

    if (currentStep === "B1") {
      renderStepB1();
    } else if (currentStep === "B2_CHOICES") {
      renderStepB2AndB3();
    } else if (currentStep === "B4_REPEAT_CHECK") {
      renderStepB4RepeatCheck();
    } else if (currentStep === "BUDGET_INPUT") {
      renderBudgetInput();
    } else if (currentStep === "FUTURE_SETTINGS") {
      renderFutureSettingsGuidance();
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
          <span class="status-badge alert">● Missed / Uncertain Debit</span>
          <span class="demo-badge-pill">Sample Portfolio — Demo Data</span>
        </div>
        <div class="shared-context-right">
          <select id="select-active-sip-missed" class="sip-quick-switcher" title="Switch selected SIP">
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
            ${sip.planOption} • Frequency: <strong>${sip.frequency}</strong> • Mandate: <strong>${sip.mandateMethod} (${sip.platform})</strong>
          </div>
        </div>

        <div class="shared-meta-pills">
          <div class="meta-pill-item">
            <span class="meta-pill-label">Scheduled Amount:</span>
            <span class="meta-pill-val">₹${sip.monthlyAmount.toLocaleString("en-IN")}</span>
          </div>
          <div class="meta-pill-item">
            <span class="meta-pill-label">Scheduled Date:</span>
            <span class="meta-pill-val">${sip.nextDebitDate}</span>
          </div>
          <div class="meta-pill-item">
            <span class="meta-pill-label">Accumulated Units:</span>
            <span class="meta-pill-val" style="color: var(--primary);">100% Safe in Folio</span>
          </div>
        </div>
      </div>

      <div class="shared-context-footer">
        <span class="context-reassurance-note">
          🛡️ <strong>No Live Bank Access:</strong> Statuses shown are for prototype assessment. Check bank statement for actual debits.
        </span>
        <a href="${sip.officialHelpUrl || sip.amcWebsite}" target="_blank" rel="noopener noreferrer" class="context-help-link">
          ${sip.platform} Support Documentation ↗
        </a>
      </div>
    `;

    card.querySelector("#select-active-sip-missed").addEventListener("change", (e) => {
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
      { id: "B1", label: "1. What Happened" },
      { id: "B2_CHOICES", label: "2. Explanation & Choice" },
      { id: "B4_REPEAT_CHECK", label: "3. Repeat Debit Check" },
      { id: "SUMMARY", label: "4. Summary" }
    ];

    const currentIdx = steps.findIndex(s => s.id === currentStep);

    stepperWrapper.innerHTML = `
      <div class="wizard-stepper">
        ${steps.map((st, idx) => `
          <div class="stepper-item ${st.id === currentStep || (st.id === 'B4_REPEAT_CHECK' && currentStep === 'BUDGET_INPUT') ? 'active' : (idx < currentIdx ? 'completed' : '')}">
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
  // STEP B1: Identify Payment Status
  // -------------------------------------------------------------
  function renderStepB1() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    card.innerHTML = `
      <div class="wizard-header-section">
        <div class="wizard-badge-indicator" style="background-color: var(--alert-bg); color: var(--alert-text);">Flow B: Missed Payment Rescue</div>
        <h2 class="wizard-question-title">What happened with your scheduled SIP?</h2>
        <p class="wizard-question-desc">
          Select the situation that best describes the payment status. We handle each situation differently:
        </p>
      </div>

      <div class="selectable-cards-grid">
        ${REASONS.map(r => `
          <div class="select-card ${selectedReasonKey === r.key ? 'selected' : ''}" data-reason-key="${r.key}" tabindex="0" role="button">
            <div class="select-card-icon">${r.icon}</div>
            <div class="select-card-body">
              <div class="select-card-title">${r.title}</div>
              <div class="select-card-sub">${r.desc}</div>
            </div>
          </div>
        `).join('')}
      </div>

      <div class="wizard-actions-bar">
        <button class="btn btn-subtle" id="btn-b1-back">← Back to Overview</button>
        <button class="btn btn-primary" id="btn-b1-continue">
          <span>Understand Status & Options →</span>
        </button>
      </div>
    `;

    card.querySelectorAll(".select-card").forEach(el => {
      const handleSelect = () => {
        card.querySelectorAll(".select-card").forEach(c => c.classList.remove("selected"));
        el.classList.add("selected");
        selectedReasonKey = el.getAttribute("data-reason-key");
      };
      el.addEventListener("click", handleSelect);
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handleSelect();
        }
      });
    });

    card.querySelector("#btn-b1-back").addEventListener("click", () => onNavigateHome());
    card.querySelector("#btn-b1-continue").addEventListener("click", () => {
      currentStep = "B2_CHOICES";
      updateView();
    });

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // STEP B2 & B3: Explain the Status & Offer Investor Choice
  // -------------------------------------------------------------
  function renderStepB2AndB3() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    const evalResult = evaluateMissedPaymentStatus({ sip, reasonKey: selectedReasonKey });

    card.innerHTML = `
      <div class="wizard-header-section">
        <div class="wizard-badge-indicator">Step B2: Understanding Your Status</div>
        <h2 class="wizard-question-title">Payment Status Explanation</h2>
        <p class="wizard-question-desc">
          Factual analysis based on official SEBI mutual fund regulations and ${sip.platform} mandate rules.
        </p>
      </div>

      <!-- Step B2 Explanation Banner -->
      <div class="missed-explanation-banner ${evalResult.statusTone}">
        <div class="banner-icon-col">
          ${evalResult.statusTone === 'alert' ? '⚠️' : (evalResult.statusTone === 'warning' ? '⚙️' : 'ℹ️')}
        </div>
        <div class="banner-content-col">
          <h3 class="banner-title">${evalResult.title}</h3>
          <p class="banner-main-text">
            ${evalResult.explanation}
          </p>
          <div class="banner-rules-checklist">
            <div class="rule-item-line">
              <span class="rule-dot">●</span>
              <span><strong>SIP Continuity:</strong> ${evalResult.ruleOfThree}</span>
            </div>
            <div class="rule-item-line">
              <span class="rule-dot">●</span>
              <span><strong>Fee Transparency:</strong> ${evalResult.bankFeeNotice}</span>
            </div>
            <div class="rule-item-line">
              <span class="rule-dot">●</span>
              <span><strong>Accumulated Wealth:</strong> All existing units remain completely safe in your folio with ${sip.amc}.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Step B3: Offer a Choice (Non-pressuring options) -->
      <div class="investor-choices-section" style="margin-top: 28px;">
        <div class="section-heading-group">
          <div>
            <h3 class="section-title">What would you like to do next?</h3>
            <div class="section-caption">You are under no pressure to make an additional purchase. Choose the option that fits your situation:</div>
          </div>
        </div>

        <div class="choice-cards-stack">
          <!-- Choice 1: No Additional Investment -->
          <div class="choice-option-card ${selectedChoice === 'no_investment' ? 'selected' : ''}" data-choice="no_investment" tabindex="0" role="button">
            <div class="choice-icon">🛡️</div>
            <div class="choice-body">
              <div class="choice-title">No additional investment</div>
              <div class="choice-desc">Review your payment status, ensure your emergency cash remains untouched, and continue with your day. No purchase will be made.</div>
            </div>
            <div class="choice-tag">Recommended for cash crunch</div>
          </div>

          <!-- Choice 2: Explore Smaller Investment -->
          <div class="choice-option-card ${selectedChoice === 'explore_smaller' ? 'selected' : ''}" data-choice="explore_smaller" tabindex="0" role="button">
            <div class="choice-icon">🎯</div>
            <div class="choice-body">
              <div class="choice-title">Explore a smaller one-time investment</div>
              <div class="choice-desc">Voluntarily invest an affordable smaller amount (e.g. ₹500 or ₹1,000) as a separate one-time purchase in ${sip.schemeName}.</div>
            </div>
            <div class="choice-tag">Voluntary</div>
          </div>

          <!-- Choice 3: Review Future SIP Settings -->
          <div class="choice-option-card ${selectedChoice === 'future_settings' ? 'selected' : ''}" data-choice="future_settings" tabindex="0" role="button">
            <div class="choice-icon">⚙️</div>
            <div class="choice-body">
              <div class="choice-title">Review future SIP settings</div>
              <div class="choice-desc">Explore supported platform options to change your monthly recurring amount, adjust the debit date, or take a temporary pause.</div>
            </div>
            <div class="choice-tag">Settings</div>
          </div>

          <!-- Choice 4: Contact Platform or AMC -->
          <div class="choice-option-card ${selectedChoice === 'contact_platform' ? 'selected' : ''}" data-choice="contact_platform" tabindex="0" role="button">
            <div class="choice-icon">📞</div>
            <div class="choice-body">
              <div class="choice-title">Contact ${sip.platform} or ${sip.amcShort}</div>
              <div class="choice-desc">Open the official help desk for mandate inquiries, transaction tracking, or payment reconciliation assistance.</div>
            </div>
            <div class="choice-tag">Support</div>
          </div>
        </div>
      </div>

      <div class="wizard-actions-bar">
        <button class="btn btn-secondary" id="btn-b2-back">← Change Situation</button>
        <button class="btn btn-primary" id="btn-b2-continue">
          <span>Continue With Selected Choice →</span>
        </button>
      </div>
    `;

    card.querySelectorAll(".choice-option-card").forEach(el => {
      const handlePick = () => {
        card.querySelectorAll(".choice-option-card").forEach(c => c.classList.remove("selected"));
        el.classList.add("selected");
        selectedChoice = el.getAttribute("data-choice");
      };
      el.addEventListener("click", handlePick);
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handlePick();
        }
      });
    });

    card.querySelector("#btn-b2-back").addEventListener("click", () => {
      currentStep = "B1";
      updateView();
    });

    card.querySelector("#btn-b2-continue").addEventListener("click", () => {
      if (selectedChoice === "no_investment") {
        regularSipStatus = evalResult.regularSipStatus;
        separateInvestmentStatus = "Not selected";
        finalSeparateInvestmentAmount = 0;
        currentStep = "SUMMARY";
        updateView();
      } else if (selectedChoice === "explore_smaller") {
        // Must check for possible repeat debit first (Step B4)
        currentStep = "B4_REPEAT_CHECK";
        updateView();
      } else if (selectedChoice === "future_settings") {
        currentStep = "FUTURE_SETTINGS";
        updateView();
      } else if (selectedChoice === "contact_platform") {
        window.open(sip.officialHelpUrl || sip.amcWebsite, "_blank");
      }
    });

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // STEP B4: Check for a Possible Repeat Debit
  // -------------------------------------------------------------
  function renderStepB4RepeatCheck() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    const evalResult = evaluateMissedPaymentStatus({ sip, reasonKey: selectedReasonKey });

    card.innerHTML = `
      <div class="wizard-header-section">
        <div class="wizard-badge-indicator" style="background-color: var(--warning-bg); color: var(--warning-text);">Step B4: Repeat Debit Feasibility Check</div>
        <h2 class="wizard-question-title text-warning">Check for a Possible Repeat Debit</h2>
        <p class="wizard-question-desc">
          Before you make a separate investment, we must ensure your regular SIP will not debit your bank account again.
        </p>
      </div>

      <!-- Prominent Repeat Debit Advisory Banner -->
      <div class="prominent-warning-card">
        <div class="warning-header-row">
          <span class="warning-large-icon">⚠️</span>
          <div>
            <h3 class="warning-headline">Your regular SIP payment may still be pending or subject to another debit attempt.</h3>
            <p class="warning-subtext">
              Confirm your bank and platform payment status before making an additional investment. In some payment arrangements (e.g. NACH mandates or banking retry queues), a secondary presentation may be scheduled within 24 to 48 hours.
            </p>
          </div>
        </div>

        <div class="repeat-debit-checks-list">
          <div class="repeat-check-item">
            <span class="repeat-check-icon">🔍</span>
            <div>
              <strong>1. Inspect your Bank Passbook / NetBanking Statement:</strong>
              Check whether the amount of ₹${sip.monthlyAmount.toLocaleString("en-IN")} is shown as 'In Process', 'Hold', or has already been debited.
            </div>
          </div>
          <div class="repeat-check-item">
            <span class="repeat-check-icon">📱</span>
            <div>
              <strong>2. Check ${sip.platform} Order Status:</strong>
              Verify whether the transaction status reads 'Failed' or 'Processing'. If status is uncertain, wait for confirmation.
            </div>
          </div>
        </div>
      </div>

      <!-- Explicit Verification Confirmation -->
      <div class="explicit-confirmation-block" style="margin-top: 20px;">
        <label class="confirmation-checkbox-label">
          <input type="checkbox" id="chk-repeat-debit-ack" ${repeatDebitAcknowledged ? 'checked' : ''} />
          <span>
            I have reviewed my bank statement and understand that if my regular SIP of ₹${sip.monthlyAmount.toLocaleString("en-IN")} undergoes a retry attempt, an additional investment will result in a separate deduction.
          </span>
        </label>
      </div>

      <div class="wizard-actions-bar">
        <button class="btn btn-secondary" id="btn-b4-back">← Back to Options</button>
        <button class="btn btn-primary" id="btn-b4-proceed" ${!repeatDebitAcknowledged ? 'disabled' : ''}>
          <span>Choose Affordable Amount →</span>
        </button>
      </div>
    `;

    const chk = card.querySelector("#chk-repeat-debit-ack");
    const btnProceed = card.querySelector("#btn-b4-proceed");

    chk.addEventListener("change", (e) => {
      repeatDebitAcknowledged = e.target.checked;
      btnProceed.disabled = !repeatDebitAcknowledged;
    });

    card.querySelector("#btn-b4-back").addEventListener("click", () => {
      currentStep = "B2_CHOICES";
      updateView();
    });

    btnProceed.addEventListener("click", () => {
      currentStep = "BUDGET_INPUT";
      updateView();
    });

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // BUDGET INPUT: For Flexible Contribution after Missed Payment
  // -------------------------------------------------------------
  function renderBudgetInput() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    const presets = [500, 1000, 1500, sip.monthlyAmount];
    const validation = validateOneTimeAmount(chosenAmount, sip);

    card.innerHTML = `
      <div class="wizard-header-section">
        <div class="wizard-badge-indicator">Flexible Contribution</div>
        <h2 class="wizard-question-title">Choose an Affordable One-Time Amount</h2>
        <p class="wizard-question-desc">
          Make a separate one-time purchase in <strong>${sip.schemeName}</strong>. This does not replace or modify your recurring SIP.
        </p>
      </div>

      <!-- Calculation Panel -->
      <div class="budget-comparison-panel">
        <div class="budget-comparison-col">
          <span class="budget-col-label">Usual Monthly SIP:</span>
          <span class="budget-col-val">₹${sip.monthlyAmount.toLocaleString("en-IN")}</span>
        </div>
        <div class="budget-comparison-col highlight">
          <span class="budget-col-label">Proposed One-Time Investment:</span>
          <span class="budget-col-val" id="display-b-chosen">₹${Number(chosenAmount).toLocaleString("en-IN")}</span>
          <span class="budget-col-percent" id="display-b-percent">(${validation.percent}% of usual SIP)</span>
        </div>
        <div class="budget-comparison-col">
          <span class="budget-col-label">Cash Preserved:</span>
          <span class="budget-col-val" id="display-b-difference" style="color: var(--primary);">₹${Number(validation.difference).toLocaleString("en-IN")}</span>
        </div>
      </div>

      <!-- Presets -->
      <div class="form-group" style="margin-top: 24px;">
        <label class="form-label">Select amount:</label>
        <div class="budget-chips-row">
          ${presets.map(val => `
            <button type="button" class="budget-chip ${!isCustomAmount && chosenAmount === val ? 'active' : ''}" data-val="${val}">
              <span class="chip-amt">₹${val.toLocaleString("en-IN")}</span>
              <span class="chip-note">${val === sip.monthlyAmount ? 'Full Scheduled' : Math.round((val / sip.monthlyAmount) * 100) + '% of SIP'}</span>
            </button>
          `).join('')}
          <button type="button" class="budget-chip ${isCustomAmount ? 'active' : ''}" id="btn-custom-chip-b">
            <span class="chip-amt">Custom</span>
            <span class="chip-note">Enter amount</span>
          </button>
        </div>
      </div>

      <div class="form-group" id="custom-wrapper-b" style="display: ${isCustomAmount ? 'block' : 'none'};">
        <label class="form-label" for="input-custom-b">Enter custom amount (₹):</label>
        <div class="input-with-prefix">
          <span class="input-prefix">₹</span>
          <input type="number" id="input-custom-b" class="form-input" value="${chosenAmount}" min="${sip.minLumpSumAmount || 100}" step="100" />
        </div>
        <div class="form-help">Minimum additional purchase requirement: ₹${sip.minLumpSumAmount || 100}.</div>
      </div>

      <div id="validation-box-b" class="form-validation-alert" style="display: ${validation.isValid ? 'none' : 'flex'};">
        <span>⚠️</span>
        <span id="validation-text-b">${validation.message || ''}</span>
      </div>

      <div class="wizard-actions-bar">
        <button class="btn btn-secondary" id="btn-budget-back">← Back</button>
        <button class="btn btn-primary" id="btn-budget-confirm" ${!validation.isValid ? 'disabled' : ''}>
          <span>Simulate ₹${Number(chosenAmount).toLocaleString("en-IN")} Investment →</span>
        </button>
      </div>
    `;

    card.querySelectorAll(".budget-chip[data-val]").forEach(btn => {
      btn.addEventListener("click", () => {
        isCustomAmount = false;
        chosenAmount = Number(btn.getAttribute("data-val"));
        card.querySelector("#custom-wrapper-b").style.display = "none";
        updateBMetrics(card);
      });
    });

    const btnCust = card.querySelector("#btn-custom-chip-b");
    const custWrap = card.querySelector("#custom-wrapper-b");
    const custInput = card.querySelector("#input-custom-b");

    btnCust.addEventListener("click", () => {
      isCustomAmount = true;
      custWrap.style.display = "block";
      card.querySelectorAll(".budget-chip").forEach(c => c.classList.remove("active"));
      btnCust.classList.add("active");
      custInput.focus();
    });

    custInput.addEventListener("input", (e) => {
      chosenAmount = Number(e.target.value);
      updateBMetrics(card);
    });

    function updateBMetrics(root) {
      const v = validateOneTimeAmount(chosenAmount, sip);
      root.querySelectorAll(".budget-chip").forEach(c => {
        if (!isCustomAmount && Number(c.getAttribute("data-val")) === chosenAmount) {
          c.classList.add("active");
        } else if (isCustomAmount && c.id === "btn-custom-chip-b") {
          c.classList.add("active");
        } else {
          c.classList.remove("active");
        }
      });

      root.querySelector("#display-b-chosen").textContent = `₹${Number(chosenAmount || 0).toLocaleString("en-IN")}`;
      root.querySelector("#display-b-percent").textContent = `(${v.percent}% of usual SIP)`;
      root.querySelector("#display-b-difference").textContent = `₹${Number(v.difference).toLocaleString("en-IN")}`;

      const vBox = root.querySelector("#validation-box-b");
      const vText = root.querySelector("#validation-text-b");
      const btnConf = root.querySelector("#btn-budget-confirm");

      if (!v.isValid) {
        vBox.style.display = "flex";
        vText.textContent = v.message;
        btnConf.disabled = true;
      } else {
        vBox.style.display = "none";
        btnConf.disabled = false;
        btnConf.querySelector("span").textContent = `Simulate ₹${Number(chosenAmount).toLocaleString("en-IN")} Investment →`;
      }
    }

    card.querySelector("#btn-budget-back").addEventListener("click", () => {
      currentStep = "B4_REPEAT_CHECK";
      updateView();
    });

    card.querySelector("#btn-budget-confirm").addEventListener("click", () => {
      const evalResult = evaluateMissedPaymentStatus({ sip, reasonKey: selectedReasonKey });
      regularSipStatus = evalResult.regularSipStatus;
      separateInvestmentStatus = "Simulated only";
      finalSeparateInvestmentAmount = chosenAmount;
      currentStep = "SUMMARY";
      updateView();
    });

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // FUTURE SETTINGS: Explains Supported Routes (Acceptance Test H)
  // -------------------------------------------------------------
  function renderFutureSettingsGuidance() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    card.innerHTML = `
      <div class="wizard-header-section">
        <div class="wizard-badge-indicator">Future SIP Settings</div>
        <h2 class="wizard-question-title">Supported Options for Your Recurring SIP</h2>
        <p class="wizard-question-desc">
          SIP Rescue explains only supported platform routes and does NOT silently alter your recurring mandate.
        </p>
      </div>

      <div class="guidance-cards-grid">
        <div class="guidance-feature-card">
          <div class="guidance-card-icon">📉</div>
          <h3 class="guidance-card-title">Step Down Monthly Amount</h3>
          <p class="guidance-card-body">
            You can reduce your regular monthly commitment from ₹${sip.monthlyAmount.toLocaleString("en-IN")} to the fund's minimum (₹${sip.minSipAmount || 100}/mo).
          </p>
          <div class="guidance-card-timing">Notice: ≥2 working days on ${sip.platform}</div>
        </div>

        <div class="guidance-feature-card">
          <div class="guidance-card-icon">⏸️</div>
          <h3 class="guidance-card-title">Pause Recurring SIP</h3>
          <p class="guidance-card-body">
            Temporarily pause deductions for 1 to 6 months. All units already purchased remain invested and continue tracking the fund's performance.
          </p>
          <div class="guidance-card-timing">Notice: ≥2 working days on ${sip.platform}</div>
        </div>

        <div class="guidance-feature-card">
          <div class="guidance-card-icon">🗓️</div>
          <h3 class="guidance-card-title">Change Debit Date</h3>
          <p class="guidance-card-body">
            Move your debit date closer to your monthly salary credit day (e.g., from the 10th to the 5th) to avoid cash shortages.
          </p>
          <div class="guidance-card-timing">Notice: ≥2 working days on ${sip.platform}</div>
        </div>
      </div>

      <div class="demo-disclaimer-box" style="margin-top: 24px;">
        <div>ℹ️</div>
        <div>
          <strong>Integrity Safeguard:</strong> This application cannot and will not modify your recurring bank mandate in the background. Modifying recurring settings requires authentication inside your verified ${sip.platform} app.
        </div>
      </div>

      <div class="wizard-actions-bar">
        <button class="btn btn-secondary" id="btn-future-back">← Back to Choices</button>
        <button class="btn btn-primary" id="btn-future-finish">
          <span>Finish Session →</span>
        </button>
      </div>
    `;

    card.querySelector("#btn-future-back").addEventListener("click", () => {
      currentStep = "B2_CHOICES";
      updateView();
    });

    card.querySelector("#btn-future-finish").addEventListener("click", () => {
      const evalResult = evaluateMissedPaymentStatus({ sip, reasonKey: selectedReasonKey });
      regularSipStatus = evalResult.regularSipStatus;
      separateInvestmentStatus = "Not selected";
      finalSeparateInvestmentAmount = 0;
      currentStep = "SUMMARY";
      updateView();
    });

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // SUMMARY: Final Outcome & Independent Statuses
  // -------------------------------------------------------------
  function renderSummary() {
    const card = document.createElement("div");
    card.className = "wizard-main-card summary-card";

    const evalResult = evaluateMissedPaymentStatus({ sip, reasonKey: selectedReasonKey });

    card.innerHTML = `
      <div class="wizard-header-section" style="text-align: center; margin-bottom: 24px;">
        <div style="font-size: 38px; margin-bottom: 8px;">📋</div>
        <h2 class="wizard-question-title" style="font-size: 24px;">Your SIP Rescue Summary</h2>
        <p class="wizard-question-desc">
          Resolution summary for your missed or uncertain debit. Transaction statuses are represented independently.
        </p>
      </div>

      <!-- Independent Statuses -->
      <div class="status-comparison-grid">
        <!-- 1. Regular SIP Instalment Status -->
        <div class="status-box regular-sip-box">
          <div class="status-box-header">
            <span class="status-box-tag">Regular Recurring SIP</span>
            <span class="status-badge ${evalResult.statusTone}">
              ${regularSipStatus}
            </span>
          </div>
          <div class="status-box-fund">${sip.schemeName}</div>
          <div class="status-box-row">
            <span>Usual SIP Amount:</span>
            <strong>₹${sip.monthlyAmount.toLocaleString("en-IN")} / month</strong>
          </div>
          <div class="status-box-row">
            <span>Mandate Health:</span>
            <span>Active mandate (${sip.mandateMethod})</span>
          </div>
          <div class="status-box-desc">
            ${evalResult.ruleOfThree}
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
            <span>Amount:</span>
            <strong>${finalSeparateInvestmentAmount > 0 ? '₹' + finalSeparateInvestmentAmount.toLocaleString('en-IN') : 'No additional investment selected'}</strong>
          </div>
          <div class="status-box-row">
            <span>Execution Type:</span>
            <span>${finalSeparateInvestmentAmount > 0 ? 'Simulated only (Demo)' : 'None'}</span>
          </div>
          <div class="status-box-desc">
            ${finalSeparateInvestmentAmount > 0 
              ? 'Voluntary 1-time purchase simulated in demo mode. This does not replace your recurring SIP.' 
              : 'No additional investment was made. Your regular SIP will follow its next scheduled debit cycle.'}
          </div>
        </div>
      </div>

      <!-- Breakdown Table -->
      <div class="summary-details-card">
        <h3 class="summary-card-subheading">Transaction Details Breakdown</h3>
        <div class="summary-table-rows">
          <div class="summary-table-row">
            <span class="row-label">Mutual Fund:</span>
            <span class="row-val"><strong>${sip.schemeName}</strong> (${sip.amc})</span>
          </div>
          <div class="summary-table-row">
            <span class="row-label">Reported Issue:</span>
            <span class="row-val">${evalResult.shortSummary}</span>
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
            <span class="row-label">Next Regular SIP Run:</span>
            <span class="row-val">${sip.nextDebitDate ? sip.nextDebitDate + ' (Upcoming scheduled cycle)' : 'Schedule pending platform confirmation'}</span>
          </div>
        </div>
      </div>

      <!-- Prototype Disclaimer -->
      <div class="demo-disclaimer-box" style="margin-top: 24px;">
        <div style="font-size: 16px;">ℹ️</div>
        <div>
          <strong>Product Demonstration Disclaimer:</strong>
          This is a product demonstration. No real mutual fund investment, bank debit, SIP skip, cancellation, or mandate modification has occurred.
        </div>
      </div>

      <div class="wizard-actions-bar" style="margin-top: 28px;">
        <button class="btn btn-secondary" id="btn-summary-home">
          ← Back to Overview
        </button>
        <button class="btn btn-secondary" id="btn-summary-details-b">
          View SIP Details
        </button>
        <button class="btn btn-primary" id="btn-summary-restart">
          <span>Explore Another Option</span>
        </button>
      </div>
    `;

    card.querySelector("#btn-summary-home").addEventListener("click", () => onNavigateHome());
    card.querySelector("#btn-summary-details-b").addEventListener("click", () => {
      if (onViewSipDetails) onViewSipDetails(sip);
    });
    card.querySelector("#btn-summary-restart").addEventListener("click", () => {
      currentStep = "B1";
      updateView();
    });

    container.appendChild(card);
  }

  updateView();
  return container;
}
