/**
 * sip-rescue-mvp/js/components/RescueNavigator.js
 * 
 * Screen Three: Core "Get SIP Help" Flow
 * Redesigned into a structured, intuitive fintech workflow:
 * 
 * Step 1: Understand the situation (6 selectable visual cards)
 * Step 2: Understand the SIP (Progressive disclosure: platform, mandate, timing, status)
 * Step 3: Present the guidance with exact hierarchy:
 *         - Your situation (1-sentence summary)
 *         - What you can do next (cards with clear explanations & actions)
 *         - Important timing information (cutoff warning & feasibility)
 *         - What to check before acting (platform, mandate, fee rules)
 *         - Official source (verified documentation link & audit date)
 *         - Your next step (primary CTA + secondary actions)
 * Step 4: Reminder or feedback (explicit status separation)
 */

import { evaluateGuidance } from "../data/rulesConfig.js?v=2";

const SITUATIONS = [
  {
    id: "sit-cash-shortage",
    title: "I do not have enough money right now",
    desc: "Cash flow tightness or temporary shortage before my upcoming debit date.",
    icon: "💰"
  },
  {
    id: "sit-payment-failed",
    title: "My SIP payment failed",
    desc: "A scheduled debit attempt failed; understand penalty risks and how to resume.",
    icon: "⚠️"
  },
  {
    id: "sit-amount-strain",
    title: "My SIP amount is difficult to manage",
    desc: "The monthly contribution feels too high for my current household budget.",
    icon: "📉"
  },
  {
    id: "sit-temporary-break",
    title: "I need a temporary break",
    desc: "Halt deductions for 1 to 6 months while keeping all accumulated units invested.",
    icon: "⏸️"
  },
  {
    id: "sit-cancel",
    title: "I am considering cancelling my SIP",
    desc: "Permanently stop future auto-debits without penalty while preserving units.",
    icon: "🛑"
  },
  {
    id: "sit-not-sure",
    title: "I am not sure what to do",
    desc: "Understand mutual fund SIP flexibility, auto-debits, and how pausing works.",
    icon: "❓"
  }
];

export function renderRescueNavigator({
  initialSip = null,
  initialScenario = null,
  onNavigateHome,
  onNavigateComeback,
  onOpenFeedback,
  onPlanAhead,
  onMissedPayment
}) {
  const container = document.createElement("div");
  container.className = "wizard-screen-container";

  // State
  let currentStep = "1"; // '1' | '2' | '3'
  let selectedSituation = initialScenario ? initialScenario.situation : SITUATIONS[0].title;
  let selectedPlatform = initialScenario ? initialScenario.platform : (initialSip ? initialSip.platform : "Groww");
  let selectedSetup = initialScenario ? initialScenario.setupType : (initialSip ? initialSip.setupType : "Platform-managed SIP");
  let selectedTiming = initialScenario ? initialScenario.timeRemaining : (initialSip ? "Within 1–2 days" : "Within 3–5 days");
  let selectedPaymentStatus = "Scheduled"; // 'Scheduled' | 'Pending' | 'Failed'
  let guidanceResult = null;

  function updateView() {
    container.innerHTML = "";

    // Stepper header
    const stepperWrapper = document.createElement("div");
    stepperWrapper.className = "wizard-progress-bar";
    stepperWrapper.innerHTML = `
      <div class="wizard-stepper">
        <div class="stepper-item ${currentStep === '1' ? 'active' : 'completed'}">
          <span class="stepper-number">1</span>
          <span class="stepper-label">Situation</span>
        </div>
        <div class="stepper-arrow">→</div>
        <div class="stepper-item ${currentStep === '2' ? 'active' : (currentStep === '3' ? 'completed' : '')}">
          <span class="stepper-number">2</span>
          <span class="stepper-label">SIP Details</span>
        </div>
        <div class="stepper-arrow">→</div>
        <div class="stepper-item ${currentStep === '3' ? 'active' : ''}">
          <span class="stepper-number">3</span>
          <span class="stepper-label">Guidance & Action</span>
        </div>
      </div>
    `;
    container.appendChild(stepperWrapper);

    if (currentStep === "1") {
      renderStep1();
    } else if (currentStep === "2") {
      renderStep2();
    } else if (currentStep === "3") {
      renderStep3();
    }
  }

  // -------------------------------------------------------------
  // STEP 1: Understand the Situation
  // -------------------------------------------------------------
  function renderStep1() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    card.innerHTML = `
      <div class="wizard-header-section">
        ${initialSip ? `
          <div class="prefilled-pill">
            <span>Selected SIP: <strong>${initialSip.schemeName}</strong> (${initialSip.amc})</span>
          </div>
        ` : ''}
        <h2 class="wizard-question-title">What is your current situation?</h2>
        <p class="wizard-question-desc">Select one of our specialized assistance flows or choose your situation below:</p>
      </div>

      <!-- Prominent 2-Path Assistance Cards (Section 4 Requirement) -->
      <div class="assistance-entry-cards-grid" style="margin-bottom: 24px;">
        <div class="entry-card plan-ahead-entry-card" style="padding: 18px;">
          <div class="entry-card-badge">Plan Ahead</div>
          <div class="entry-card-header">
            <div class="entry-card-icon plan-ahead-icon" style="font-size: 20px;">🗓️</div>
            <h3 class="entry-card-title" style="font-size: 15px;">Know you cannot afford your next SIP?</h3>
          </div>
          <p class="entry-card-desc" style="font-size: 12.5px;">
            Explore your options before your next scheduled payment. Skip, pause, or step down without penalties.
          </p>
          <button class="btn btn-primary btn-sm entry-cta-btn" id="btn-nav-plan-ahead" style="margin-top: 10px;">
            <span>Plan My SIP →</span>
          </button>
        </div>

        <div class="entry-card missed-payment-entry-card" style="padding: 18px;">
          <div class="entry-card-badge badge-alert">Missed Payment</div>
          <div class="entry-card-header">
            <div class="entry-card-icon missed-payment-icon" style="font-size: 20px;">⚠️</div>
            <h3 class="entry-card-title" style="font-size: 15px;">Your SIP payment was not debited?</h3>
          </div>
          <p class="entry-card-desc" style="font-size: 12.5px;">
            Understand what happened and explore your next steps. Mandate recovery & penalty guidelines.
          </p>
          <button class="btn btn-secondary btn-sm entry-cta-btn" id="btn-nav-missed-payment" style="margin-top: 10px; background: white; border: 1.5px solid var(--border-medium);">
            <span>Resolve Payment Issue →</span>
          </button>
        </div>
      </div>

      <div style="font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">
        OR EXPLORE GENERAL CONTINUITY GUIDANCE
      </div>

      <div class="selectable-cards-grid">
        ${SITUATIONS.map(s => `
          <div class="select-card ${selectedSituation === s.title ? 'selected' : ''}" data-situation-title="${s.title}" tabindex="0" role="button">
            <div class="select-card-icon">${s.icon}</div>
            <div class="select-card-body">
              <div class="select-card-title">${s.title}</div>
              <div class="select-card-sub">${s.desc}</div>
            </div>
          </div>
        `).join('')}
      </div>

      <div class="wizard-actions-bar">
        <button class="btn btn-subtle" id="btn-cancel-to-overview">← Back to Overview</button>
        <button class="btn btn-primary" id="btn-step-1-continue">
          <span>Continue to SIP Details →</span>
        </button>
      </div>
    `;

    const btnNavPlanAhead = card.querySelector("#btn-nav-plan-ahead");
    if (btnNavPlanAhead && onPlanAhead) {
      btnNavPlanAhead.addEventListener("click", () => onPlanAhead(initialSip));
    }

    const btnNavMissed = card.querySelector("#btn-nav-missed-payment");
    if (btnNavMissed && onMissedPayment) {
      btnNavMissed.addEventListener("click", () => onMissedPayment(initialSip));
    }

    // Click & keyboard handlers
    card.querySelectorAll(".select-card").forEach(el => {
      const handleSelect = () => {
        card.querySelectorAll(".select-card").forEach(c => c.classList.remove("selected"));
        el.classList.add("selected");
        selectedSituation = el.getAttribute("data-situation-title");
      };
      el.addEventListener("click", handleSelect);
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handleSelect();
        }
      });
    });

    card.querySelector("#btn-cancel-to-overview").addEventListener("click", () => onNavigateHome());
    card.querySelector("#btn-step-1-continue").addEventListener("click", () => {
      currentStep = "2";
      updateView();
    });

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // STEP 2: Understand the SIP
  // -------------------------------------------------------------
  function renderStep2() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    card.innerHTML = `
      <div class="wizard-header-section">
        <h2 class="wizard-question-title">A few details about this SIP</h2>
        <p class="wizard-question-desc">
          We only ask what is necessary to evaluate the exact notice cutoffs and platform rules.
        </p>
      </div>

      ${initialSip ? `
        <div class="prefilled-pill" style="margin-bottom: 24px;">
          <span>✓ Pre-filled from your demo portfolio: <strong>${initialSip.schemeName}</strong> (₹${initialSip.monthlyAmount.toLocaleString("en-IN")}/mo on ${initialSip.platform})</span>
        </div>
      ` : ''}

      <!-- Question 1: Platform -->
      <div class="form-group">
        <label class="form-label" for="select-platform">Which platform or AMC manages the SIP?</label>
        <div class="form-help">Verified official rules are available for Groww, Zerodha Coin, and direct AMCs.</div>
        <select class="form-select" id="select-platform">
          <option value="Groww" ${selectedPlatform === 'Groww' ? 'selected' : ''}>Groww (AutoPay / BSE)</option>
          <option value="Zerodha Coin" ${selectedPlatform === 'Zerodha Coin' ? 'selected' : ''}>Zerodha Coin (BSE StAR MF)</option>
          <option value="Another platform" ${selectedPlatform === 'Another platform' ? 'selected' : ''}>Another platform (General SEBI / AMFI guidance)</option>
          <option value="I'm not sure" ${selectedPlatform === "I'm not sure" ? 'selected' : ''}>I'm not sure</option>
        </select>
      </div>

      <!-- Question 2: Payment Method / Mandate -->
      <div class="form-group">
        <label class="form-label" for="select-setup">What payment method or mandate is used?</label>
        <div class="form-help">Platform-managed SIPs typically use UPI AutoPay or e-Mandate with ~2 business days cutoff.</div>
        <select class="form-select" id="select-setup">
          <option value="Platform-managed SIP" ${selectedSetup === 'Platform-managed SIP' ? 'selected' : ''}>Platform AutoPay / e-Mandate (UPI / NetBanking via App)</option>
          <option value="AMC-registered SIP" ${selectedSetup === 'AMC-registered SIP' ? 'selected' : ''}>Direct AMC Mandate (OTM / CAMS / KFintech NACH - 10-21 days notice)</option>
          <option value="I'm not sure" ${selectedSetup === "I'm not sure" ? 'selected' : ''}>I'm not sure (Show safe fallback guidance)</option>
        </select>
      </div>

      <!-- Question 3: Scheduled Timing -->
      <div class="form-group">
        <label class="form-label" for="select-timing">When is the next instalment scheduled?</label>
        <div class="form-help">Timelines determine whether a skip/pause can take effect before debit generation.</div>
        <select class="form-select" id="select-timing">
          <option value="Within 1–2 days" ${selectedTiming === 'Within 1–2 days' ? 'selected' : ''}>Within 1–2 days (Critical cutoff zone)</option>
          <option value="Within 3–5 days" ${selectedTiming === 'Within 3–5 days' ? 'selected' : ''}>Within 3–5 days (Action recommended promptly)</option>
          <option value="More than 5 days" ${selectedTiming === 'More than 5 days' ? 'selected' : ''}>More than 5 days (Comfortable notice buffer)</option>
          <option value="Today" ${selectedTiming === 'Today' ? 'selected' : ''}>Today (Instalment due today)</option>
          <option value="I'm not sure of the date" ${selectedTiming === "I'm not sure of the date" ? 'selected' : ''}>I'm not sure of the exact date</option>
        </select>
      </div>

      <!-- Question 4: Current Payment Status -->
      <div class="form-group">
        <label class="form-label" for="select-payment-status">Is the payment scheduled, pending, or has it already failed?</label>
        <select class="form-select" id="select-payment-status">
          <option value="Scheduled" ${selectedPaymentStatus === 'Scheduled' ? 'selected' : ''}>Scheduled for future date</option>
          <option value="Pending" ${selectedPaymentStatus === 'Pending' ? 'selected' : ''}>Pending processing at bank</option>
          <option value="Failed" ${selectedPaymentStatus === 'Failed' ? 'selected' : ''}>Already failed / rejected by bank</option>
        </select>
      </div>

      <div class="wizard-actions-bar">
        <button class="btn btn-secondary" id="btn-back-to-step-1">← Change Situation</button>
        <button class="btn btn-primary" id="btn-evaluate-guidance">
          <span>See Tailored Guidance →</span>
        </button>
      </div>
    `;

    card.querySelector("#btn-back-to-step-1").addEventListener("click", () => {
      currentStep = "1";
      updateView();
    });

    card.querySelector("#btn-evaluate-guidance").addEventListener("click", () => {
      selectedPlatform = card.querySelector("#select-platform").value;
      selectedSetup = card.querySelector("#select-setup").value;
      selectedTiming = card.querySelector("#select-timing").value;
      selectedPaymentStatus = card.querySelector("#select-payment-status").value;

      guidanceResult = evaluateGuidance({
        situation: selectedSituation,
        platform: selectedPlatform,
        setupType: selectedSetup,
        timeRemaining: selectedTiming
      });

      currentStep = "3";
      updateView();
    });

    container.appendChild(card);
  }

  // -------------------------------------------------------------
  // STEP 3: Present the Guidance (Exact Required Hierarchy)
  // -------------------------------------------------------------
  function renderStep3() {
    if (!guidanceResult) {
      guidanceResult = evaluateGuidance({
        situation: selectedSituation,
        platform: selectedPlatform,
        setupType: selectedSetup,
        timeRemaining: selectedTiming
      });
    }

    const res = guidanceResult;
    const card = document.createElement("div");
    card.className = "wizard-main-card guidance-result-view";

    // Timing tone
    const bannerTone = res.cutoffStatus === "CRITICAL_CUTOFF_PASSED"
      ? "warning"
      : (res.cutoffStatus === "SAFE_WINDOW_OPEN" ? "safe" : "info");

    const bannerIcon = res.cutoffStatus === "CRITICAL_CUTOFF_PASSED" ? "⚠️" : (res.cutoffStatus === "SAFE_WINDOW_OPEN" ? "✅" : "ℹ️");

    card.innerHTML = `
      <!-- 1. Your Situation -->
      <div class="guidance-hierarchy-block">
        <div class="guidance-block-label">YOUR SITUATION</div>
        <div class="situation-summary-card">
          <div class="situation-summary-icon">💬</div>
          <div>
            <div class="situation-summary-text">
              You selected: <strong>"${selectedSituation}"</strong>
            </div>
            <div class="situation-summary-sub">
              Platform: <strong>${selectedPlatform}</strong> • Mandate: <strong>${selectedSetup}</strong> • Timing: <strong>${selectedTiming}</strong> (${selectedPaymentStatus})
            </div>
          </div>
        </div>
      </div>

      <!-- 2. What you can do next -->
      <div class="guidance-hierarchy-block">
        <div class="guidance-block-label">WHAT YOU CAN DO NEXT</div>
        <div class="options-cards-stack">
          ${res.whatYouCanDoNow.map((opt, idx) => `
            <div class="guidance-option-card">
              <div class="option-header-row">
                <span class="option-index-badge">Option ${idx + 1}</span>
                <h3 class="option-title-text">${opt.title}</h3>
              </div>
              <p class="option-desc-text">${opt.description}</p>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- 3. Important timing information -->
      <div class="guidance-hierarchy-block">
        <div class="guidance-block-label">IMPORTANT TIMING INFORMATION</div>
        <div class="result-status-banner ${bannerTone}">
          <div class="result-banner-icon">${bannerIcon}</div>
          <div class="result-banner-text">
            <strong>Cutoff Window Feasibility Analysis</strong>
            ${res.cutoffAlertText}
          </div>
        </div>
        <div class="timing-detail-note">
          Notice Requirement: Most apps require at least 2 working days advance notice. If your debit is within 48 hours, submitting a pause or skip now may only take effect for the following month's instalment.
        </div>
      </div>

      <!-- 4. What to check before acting -->
      <div class="guidance-hierarchy-block">
        <div class="guidance-block-label">WHAT TO CHECK BEFORE ACTING</div>
        <div class="checklist-card">
          <ul class="careful-list">
            ${res.whatToBeCarefulAbout.map(item => `
              <li>${item}</li>
            `).join('')}
            <li>Check if your bank charges a mandate bounce fee (₹250–₹500 + GST) if funds are insufficient on debit day.</li>
            <li>Confirm your accumulated mutual fund units remain safe and invested in your folio regardless of whether this debit completes.</li>
          </ul>
        </div>
      </div>

      <!-- Uncertainty State Warning if unverified -->
      ${res.uncertaintyNotice ? `
        <div class="result-status-banner warning" style="margin-top: 12px;">
          <div class="result-banner-icon">❓</div>
          <div class="result-banner-text">
            <strong>Unverified Platform Policy:</strong>
            ${res.uncertaintyNotice}
          </div>
        </div>
      ` : ''}

      <!-- 5. Official Source -->
      <div class="guidance-hierarchy-block">
        <div class="guidance-block-label">OFFICIAL SOURCE</div>
        <div class="rule-transparency-card">
          <div class="rule-transparency-meta">
            <span>Official Policy Reference: <strong>${res.rule.officialSourceName}</strong></span>
            <span class="${res.rule.verificationStatus === 'VERIFIED' ? 'badge-verified' : (res.rule.verificationStatus === 'GENERAL_GUIDANCE' ? 'badge-general' : 'badge-unverified')}">
              ${res.rule.verificationStatus}
            </span>
            <span style="color: var(--text-muted);">Verified on: ${res.rule.lastVerifiedDate}</span>
          </div>
          <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 10px; line-height: 1.45;">
            ${res.rule.plainLanguageSummary}
          </p>
          <div>
            <a href="${res.rule.officialSourceUrl}" target="_blank" rel="noopener noreferrer" class="external-official-link">
              <span>View exact official documentation on ${res.rule.platform}</span>
              <span style="font-size: 11px;">↗</span>
            </a>
          </div>
        </div>
      </div>

      <!-- 6. Your next step -->
      <div class="guidance-hierarchy-block">
        <div class="guidance-block-label">YOUR NEXT STEP</div>
        <div class="next-step-action-panel">
          <div class="action-panel-cta-group">
            <button class="btn btn-primary" id="btn-create-comeback" style="background-color: #047857;">
              <span>🗓️ Set a Comeback Review Reminder</span>
            </button>
            <button class="btn btn-secondary" id="btn-give-feedback">
              <span>💬 Was this guidance clear?</span>
            </button>
          </div>
          <div class="action-panel-secondary-links">
            <button class="btn btn-subtle btn-sm" id="btn-review-another">
              🔄 Try another situation
            </button>
            <button class="btn btn-subtle btn-sm" id="btn-return-overview">
              ← Return to Overview
            </button>
          </div>
        </div>
      </div>

      <!-- Safety Disclaimer -->
      <div class="reassurance-callout">
        🛡️ <strong>Safety Reassurance:</strong> SIP Rescue is an informational assistant. We never initiate financial debits, alter your bank mandates, or modify your broker account.
      </div>
    `;

    card.querySelector("#btn-review-another").addEventListener("click", () => {
      currentStep = "1";
      updateView();
    });

    card.querySelector("#btn-return-overview").addEventListener("click", () => onNavigateHome());

    card.querySelector("#btn-create-comeback").addEventListener("click", () => {
      if (onNavigateComeback) {
        onNavigateComeback({
          situation: selectedSituation,
          sip: initialSip,
          recommendedDate: new Date(Date.now() + 30 * 24 * 3600 * 1000).toISOString().split('T')[0]
        });
      }
    });

    card.querySelector("#btn-give-feedback").addEventListener("click", () => {
      if (onOpenFeedback) {
        onOpenFeedback(selectedSituation);
      }
    });

    container.appendChild(card);
  }

  updateView();
  return container;
}
