/**
 * sip-rescue-mvp/js/components/ContextPanel.js
 * 
 * Right-Hand Contextual Panel for SIP Rescue Dashboard:
 * - Upcoming SIP instalments (next 2-3 with dates & amounts)
 * - Concise portfolio status breakdown
 * - Important notice cutoff rules at a glance
 * - Quick continuity checklist
 */

import { SAMPLE_SIPS, PORTFOLIO_SUMMARY } from "../data/sampleSips.js?v=2";

export function renderContextPanel({ onSelectSip, onStartRescue }) {
  const panel = document.createElement("aside");
  panel.className = "dashboard-context-panel";

  panel.innerHTML = `
    <!-- Card 1: Upcoming Instalment Calendar -->
    <div class="context-card">
      <div class="context-card-header">
        <h3 class="context-card-title">Upcoming Instalments</h3>
        <span class="context-badge-info">Next 30 Days</span>
      </div>

      <div class="context-instalments-list">
        ${SAMPLE_SIPS.map(sip => `
          <div class="context-instalment-item" data-sip-id="${sip.id}" role="button" tabindex="0">
            <div class="context-item-left">
              <div class="context-item-dot ${sip.statusTone}"></div>
              <div>
                <div class="context-item-name">${sip.schemeName}</div>
                <div class="context-item-date">${sip.nextDebitRelative} • ${sip.frequency}</div>
              </div>
            </div>
            <div class="context-item-right">
              <div class="context-item-amount">₹${sip.monthlyAmount.toLocaleString("en-IN")}</div>
              <span class="context-item-link">View →</span>
            </div>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- Card 2: Notice Cutoff Summary -->
    <div class="context-card">
      <div class="context-card-header">
        <h3 class="context-card-title">Notice Cutoffs at a Glance</h3>
      </div>
      <div class="context-rule-item">
        <div class="context-rule-platform">Groww AutoPay</div>
        <div class="context-rule-cutoff">At least 2 working days prior</div>
        <div class="context-rule-note">Cutoff missed? Request applies from next month.</div>
      </div>
      <div class="context-rule-item">
        <div class="context-rule-platform">Zerodha Coin (BSE StAR MF)</div>
        <div class="context-rule-cutoff">2 working days prior (before 11:00 AM)</div>
        <div class="context-rule-note">Orders sent 2 days prior to exchange.</div>
      </div>
      <div class="context-rule-item">
        <div class="context-rule-platform">AMC Direct (CAMS / KFintech)</div>
        <div class="context-rule-cutoff">10 to 21 calendar days notice</div>
        <div class="context-rule-note">Operates on clearing batch schedules.</div>
      </div>
    </div>

    <!-- Card 3: Quick Continuity Checklist -->
    <div class="context-card context-card-highlight">
      <div class="context-card-header">
        <h3 class="context-card-title" style="color: var(--primary);">Quick Pre-Debit Checklist</h3>
      </div>
      <ul class="context-checklist">
        <li>✓ Confirm account balance ≥ instalment amount</li>
        <li>✓ Submit pause or skip ≥ 2 business days prior</li>
        <li>✓ Remember: 1 missed debit does not cancel an active SIP</li>
      </ul>
      <button class="btn btn-secondary btn-sm" id="btn-context-help-flow" style="width: 100%; margin-top: 12px;">
        Need Help With an Upcoming Debit?
      </button>
    </div>
  `;

  // Attach event handlers
  panel.querySelectorAll(".context-instalment-item").forEach(item => {
    const sipId = item.getAttribute("data-sip-id");
    const sip = SAMPLE_SIPS.find(s => s.id === sipId);
    item.addEventListener("click", () => {
      if (onSelectSip && sip) onSelectSip(sip);
    });
    item.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        if (onSelectSip && sip) onSelectSip(sip);
      }
    });
  });

  const btnHelp = panel.querySelector("#btn-context-help-flow");
  if (btnHelp && onStartRescue) {
    btnHelp.addEventListener("click", () => onStartRescue(SAMPLE_SIPS[0]));
  }

  return panel;
}
