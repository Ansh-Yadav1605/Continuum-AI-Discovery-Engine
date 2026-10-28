/**
 * sip-rescue-mvp/js/components/FlexibleContributionView.js
 * 
 * Standalone & Dedicated View: Flexible Contribution
 * Voluntary Smaller One-Time Investment in the Same Mutual Fund.
 * 
 * Features:
 * 1. Shows selected fund & AMC with current recurring SIP context.
 * 2. Clearly labels proposed investment as a separate one-time investment.
 * 3. Checks known scheme minimums (e.g. ₹100 or ₹500) and eligibility.
 * 4. Explains regular SIP remains scheduled unless separately confirmed.
 * 5. Obtains explicit user confirmation before simulated purchase.
 * 6. Shows transaction status separately from regular SIP status.
 */

import { SAMPLE_SIPS } from "../data/sampleSips.js?v=3";
import { validateOneTimeAmount } from "../data/rulesConfig.js?v=3";

export function renderFlexibleContributionView({
  sip = SAMPLE_SIPS[0],
  initialAmount = 1000,
  onNavigateHome,
  onViewSipDetails,
  onSwitchSip
}) {
  const container = document.createElement("div");
  container.className = "wizard-screen-container flexible-contribution-screen";

  let chosenAmount = initialAmount || 1000;
  let isCustom = false;
  let hasConfirmedExplicitly = false;
  let isSimulated = false;

  function render() {
    container.innerHTML = "";

    // Header & Context
    const headerCard = document.createElement("div");
    headerCard.className = "screen-page-header";
    headerCard.innerHTML = `
      <div>
        <div class="breadcrumb-nav">
          <span class="breadcrumb-item"><a href="#home" id="btn-fc-bc-home">Dashboard</a></span>
          <span class="breadcrumb-sep">/</span>
          <span class="breadcrumb-active">Flexible Contribution</span>
        </div>
        <h1 class="screen-page-title">Flexible Contribution</h1>
        <p class="screen-page-subtitle">
          Make a voluntary, affordable one-time investment in the same fund without altering your recurring SIP.
        </p>
      </div>
      <div class="demo-badge-pill">
        Voluntary Feature — Demo Mode
      </div>
    `;

    headerCard.querySelector("#btn-fc-bc-home").addEventListener("click", (e) => {
      e.preventDefault();
      onNavigateHome();
    });

    container.appendChild(headerCard);

    if (!isSimulated) {
      renderForm();
    } else {
      renderOutcome();
    }
  }

  function renderForm() {
    const card = document.createElement("div");
    card.className = "wizard-main-card";

    const presets = [500, 1000, 1500, sip.monthlyAmount];
    const validation = validateOneTimeAmount(chosenAmount, sip);

    card.innerHTML = `
      <!-- Scheme Selector -->
      <div class="shared-context-header" style="background: var(--bg-subtle); padding: 14px 18px; border-radius: var(--radius-md); margin-bottom: 24px;">
        <div>
          <span class="amc-badge">${sip.amc}</span>
          <h2 style="font-size: 18px; font-weight: 700; color: var(--text-main); margin-top: 4px;">${sip.schemeName}</h2>
          <div style="font-size: 13px; color: var(--text-muted);">
            Regular Recurring SIP: <strong>₹${sip.monthlyAmount.toLocaleString("en-IN")}/mo</strong> on ${sip.frequency} (${sip.platform})
          </div>
        </div>
        <div>
          <select id="select-fc-sip" class="sip-quick-switcher" title="Switch mutual fund">
            ${SAMPLE_SIPS.map(s => `
              <option value="${s.id}" ${s.id === sip.id ? 'selected' : ''}>
                ${s.schemeName}
              </option>
            `).join('')}
          </select>
        </div>
      </div>

      <!-- Clear Non-Replacement Notice -->
      <div class="guidance-feature-card" style="border-left: 4px solid var(--primary); margin-bottom: 24px;">
        <div style="font-size: 14px; color: var(--text-main); line-height: 1.5;">
          📌 <strong>Separate One-Time Investment:</strong>
          This feature allows you to place a separate, one-time lump-sum purchase in <strong>${sip.schemeName}</strong>. 
          It does <strong>NOT</strong> automatically cancel or replace your recurring monthly SIP instalment.
        </div>
      </div>

      <!-- Calculation Breakdown -->
      <div class="budget-comparison-panel">
        <div class="budget-comparison-col">
          <span class="budget-col-label">Scheduled Recurring SIP:</span>
          <span class="budget-col-val">₹${sip.monthlyAmount.toLocaleString("en-IN")}</span>
        </div>
        <div class="budget-comparison-col highlight">
          <span class="budget-col-label">Proposed One-Time Investment:</span>
          <span class="budget-col-val" id="fc-display-amt">₹${Number(chosenAmount).toLocaleString("en-IN")}</span>
          <span class="budget-col-percent" id="fc-display-pct">(${validation.percent}% of regular SIP)</span>
        </div>
        <div class="budget-comparison-col">
          <span class="budget-col-label">Difference Preserved:</span>
          <span class="budget-col-val" id="fc-display-diff" style="color: var(--primary);">₹${Number(validation.difference).toLocaleString("en-IN")}</span>
        </div>
      </div>

      <!-- Amount Selector -->
      <div class="form-group" style="margin-top: 24px;">
        <label class="form-label">How much would you like to invest this time?</label>
        <div class="budget-chips-row">
          ${presets.map(val => `
            <button type="button" class="budget-chip ${!isCustom && chosenAmount === val ? 'active' : ''}" data-val="${val}">
              <span class="chip-amt">₹${val.toLocaleString("en-IN")}</span>
              <span class="chip-note">${val === sip.monthlyAmount ? 'Full Amount' : Math.round((val / sip.monthlyAmount) * 100) + '% of SIP'}</span>
            </button>
          `).join('')}
          <button type="button" class="budget-chip ${isCustom ? 'active' : ''}" id="btn-fc-custom">
            <span class="chip-amt">Custom</span>
            <span class="chip-note">Enter amount</span>
          </button>
        </div>
      </div>

      <!-- Custom Amount Input -->
      <div class="form-group" id="fc-custom-wrap" style="display: ${isCustom ? 'block' : 'none'};">
        <label class="form-label" for="input-fc-custom">Enter custom amount (₹):</label>
        <div class="input-with-prefix">
          <span class="input-prefix">₹</span>
          <input type="number" id="input-fc-custom" class="form-input" value="${chosenAmount}" min="${sip.minLumpSumAmount || 100}" step="100" />
        </div>
        <div class="form-help">
          Known scheme minimum for additional purchase: ₹${(sip.minLumpSumAmount || 100).toLocaleString("en-IN")}.
        </div>
      </div>

      <!-- Validation Error -->
      <div id="fc-validation-box" class="form-validation-alert" style="display: ${validation.isValid ? 'none' : 'flex'};">
        <span>⚠️</span>
        <span id="fc-validation-text">${validation.message || ''}</span>
      </div>

      <!-- Explicit User Confirmation Checkbox -->
      <div class="explicit-confirmation-block" style="margin-top: 24px;">
        <label class="confirmation-checkbox-label">
          <input type="checkbox" id="chk-fc-confirm" ${hasConfirmedExplicitly ? 'checked' : ''} />
          <span>
            I understand that this is a <strong>separate one-time investment</strong> of ₹${Number(chosenAmount).toLocaleString("en-IN")} in ${sip.schemeName}, and my recurring monthly SIP of ₹${sip.monthlyAmount.toLocaleString("en-IN")} remains scheduled unless separately modified or skipped.
          </span>
        </label>
      </div>

      <div class="wizard-actions-bar">
        <button class="btn btn-secondary" id="btn-fc-back">← Back to Overview</button>
        <button class="btn btn-primary" id="btn-fc-submit" ${!validation.isValid || !hasConfirmedExplicitly ? 'disabled' : ''}>
          <span>Simulate ₹${Number(chosenAmount).toLocaleString("en-IN")} Investment →</span>
        </button>
      </div>
    `;

    // SIP switcher
    card.querySelector("#select-fc-sip").addEventListener("change", (e) => {
      const match = SAMPLE_SIPS.find(s => s.id === e.target.value);
      if (match && onSwitchSip) onSwitchSip(match);
    });

    // Chips
    card.querySelectorAll(".budget-chip[data-val]").forEach(btn => {
      btn.addEventListener("click", () => {
        isCustom = false;
        chosenAmount = Number(btn.getAttribute("data-val"));
        card.querySelector("#fc-custom-wrap").style.display = "none";
        updateFcMetrics(card);
      });
    });

    const btnCustom = card.querySelector("#btn-fc-custom");
    const customWrap = card.querySelector("#fc-custom-wrap");
    const customInput = card.querySelector("#input-fc-custom");

    btnCustom.addEventListener("click", () => {
      isCustom = true;
      customWrap.style.display = "block";
      card.querySelectorAll(".budget-chip").forEach(c => c.classList.remove("active"));
      btnCustom.classList.add("active");
      customInput.focus();
    });

    customInput.addEventListener("input", (e) => {
      chosenAmount = Number(e.target.value);
      updateFcMetrics(card);
    });

    const chk = card.querySelector("#chk-fc-confirm");
    const btnSubmit = card.querySelector("#btn-fc-submit");

    chk.addEventListener("change", (e) => {
      hasConfirmedExplicitly = e.target.checked;
      const v = validateOneTimeAmount(chosenAmount, sip);
      btnSubmit.disabled = !v.isValid || !hasConfirmedExplicitly;
    });

    function updateFcMetrics(root) {
      const v = validateOneTimeAmount(chosenAmount, sip);
      root.querySelectorAll(".budget-chip").forEach(c => {
        if (!isCustom && Number(c.getAttribute("data-val")) === chosenAmount) {
          c.classList.add("active");
        } else if (isCustom && c.id === "btn-fc-custom") {
          c.classList.add("active");
        } else {
          c.classList.remove("active");
        }
      });

      root.querySelector("#fc-display-amt").textContent = `₹${Number(chosenAmount || 0).toLocaleString("en-IN")}`;
      root.querySelector("#fc-display-pct").textContent = `(${v.percent}% of regular SIP)`;
      root.querySelector("#fc-display-diff").textContent = `₹${Number(v.difference).toLocaleString("en-IN")}`;

      const vBox = root.querySelector("#fc-validation-box");
      const vText = root.querySelector("#fc-validation-text");

      if (!v.isValid) {
        vBox.style.display = "flex";
        vText.textContent = v.message;
        btnSubmit.disabled = true;
      } else {
        vBox.style.display = "none";
        btnSubmit.disabled = !hasConfirmedExplicitly;
        btnSubmit.querySelector("span").textContent = `Simulate ₹${Number(chosenAmount).toLocaleString("en-IN")} Investment →`;
      }
    }

    card.querySelector("#btn-fc-back").addEventListener("click", () => onNavigateHome());
    btnSubmit.addEventListener("click", () => {
      isSimulated = true;
      render();
    });

    container.appendChild(card);
  }

  function renderOutcome() {
    const card = document.createElement("div");
    card.className = "wizard-main-card summary-card";

    card.innerHTML = `
      <div class="wizard-header-section" style="text-align: center; margin-bottom: 24px;">
        <div style="font-size: 38px; margin-bottom: 8px;">✅</div>
        <h2 class="wizard-question-title" style="font-size: 24px;">Flexible Contribution Simulated</h2>
        <p class="wizard-question-desc">
          Your voluntary one-time investment in ${sip.schemeName} has been simulated. Transaction statuses are represented independently:
        </p>
      </div>

      <!-- Independent Statuses -->
      <div class="status-comparison-grid">
        <div class="status-box regular-sip-box">
          <div class="status-box-header">
            <span class="status-box-tag">Regular Recurring SIP</span>
            <span class="status-badge normal">Scheduled</span>
          </div>
          <div class="status-box-fund">${sip.schemeName}</div>
          <div class="status-box-row">
            <span>Amount:</span>
            <strong>₹${sip.monthlyAmount.toLocaleString("en-IN")} / month</strong>
          </div>
          <div class="status-box-row">
            <span>Next Debit:</span>
            <span>${sip.nextDebitRelative} (${sip.nextDebitDate})</span>
          </div>
          <div class="status-box-desc">
            Recurring mandate remains active and scheduled as usual. No recurring change was made.
          </div>
        </div>

        <div class="status-box separate-inv-box">
          <div class="status-box-header">
            <span class="status-box-tag">Separate One-Time Investment</span>
            <span class="status-badge normal">Simulated only</span>
          </div>
          <div class="status-box-fund">${sip.schemeName} (One-Time)</div>
          <div class="status-box-row">
            <span>Amount:</span>
            <strong>₹${Number(chosenAmount).toLocaleString("en-IN")}</strong>
          </div>
          <div class="status-box-row">
            <span>Execution Type:</span>
            <span>Simulated Purchase</span>
          </div>
          <div class="status-box-desc">
            One-time purchase order simulated in demo mode. Units are calculated based on latest indicative NAV.
          </div>
        </div>
      </div>

      <!-- Prototype Disclaimer -->
      <div class="demo-disclaimer-box" style="margin-top: 24px;">
        <div>ℹ️</div>
        <div>
          <strong>Product Demonstration Disclaimer:</strong>
          This is a product demonstration. No real mutual fund investment, bank debit, SIP skip, cancellation, or mandate modification has occurred.
        </div>
      </div>

      <div class="wizard-actions-bar" style="margin-top: 28px;">
        <button class="btn btn-secondary" id="btn-fc-out-home">
          ← Back to Overview
        </button>
        <button class="btn btn-secondary" id="btn-fc-out-details">
          View SIP Details
        </button>
        <button class="btn btn-primary" id="btn-fc-out-again">
          <span>Make Another Contribution</span>
        </button>
      </div>
    `;

    card.querySelector("#btn-fc-out-home").addEventListener("click", () => onNavigateHome());
    card.querySelector("#btn-fc-out-details").addEventListener("click", () => {
      if (onViewSipDetails) onViewSipDetails(sip);
    });
    card.querySelector("#btn-fc-out-again").addEventListener("click", () => {
      isSimulated = false;
      hasConfirmedExplicitly = false;
      render();
    });

    container.appendChild(card);
  }

  render();
  return container;
}
