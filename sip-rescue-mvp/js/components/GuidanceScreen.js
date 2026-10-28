/**
 * sip-rescue-mvp/js/components/GuidanceScreen.js
 * 
 * Help & Guidance Screen (#guidance):
 * - Clear platform rules reference (Groww, Zerodha Coin, AMC Direct)
 * - Notice cutoffs and timing breakdown
 * - Bank bounce fee clarifications vs. mutual fund platform rules
 * - Quick continuity options glossary (Skip vs. Pause vs. Cancel)
 * - Primary CTA to start "Get SIP Help" flow
 */

import { VERIFIED_RULES } from "../data/rulesConfig.js?v=2";

export function renderGuidanceScreen({
  onStartRescue,
  onPlanAhead,
  onMissedPayment,
  onFlexibleContribution
}) {
  const container = document.createElement("div");
  container.className = "guidance-screen-container";

  container.innerHTML = `
    <!-- Screen Header -->
    <div class="screen-page-header">
      <div>
        <div class="breadcrumb-nav">
          <span class="breadcrumb-item">Dashboard</span>
          <span class="breadcrumb-sep">/</span>
          <span class="breadcrumb-active">Help & Guidance</span>
        </div>
        <h1 class="screen-page-title">SIP Continuity Knowledge Base</h1>
        <p class="screen-page-subtitle">Verified rules, timing cutoffs, and regulatory guidelines for Indian mutual fund investors.</p>
      </div>
      <button class="btn btn-primary" id="btn-guidance-start-help">
        <span>🆘 Get SIP Help</span>
      </button>
    </div>

    <!-- Intelligent Assistance Entry Points in Help -->
    <div class="assistance-entry-cards-grid" style="margin-bottom: 24px;">
      <div class="entry-card plan-ahead-entry-card" style="padding: 20px;">
        <div class="entry-card-badge">Plan Ahead</div>
        <div class="entry-card-header">
          <div class="entry-card-icon plan-ahead-icon" style="font-size: 20px;">🗓️</div>
          <h3 class="entry-card-title" style="font-size: 16px;">Know you cannot afford your next SIP?</h3>
        </div>
        <p class="entry-card-desc" style="font-size: 13px;">
          Explore your options before your next scheduled payment. Skip or pause without penalties.
        </p>
        <button class="btn btn-primary btn-sm entry-cta-btn" id="btn-guidance-plan-ahead" style="margin-top: 12px;">
          <span>Plan My SIP →</span>
        </button>
      </div>

      <div class="entry-card missed-payment-entry-card" style="padding: 20px;">
        <div class="entry-card-badge badge-alert">Missed Payment</div>
        <div class="entry-card-header">
          <div class="entry-card-icon missed-payment-icon" style="font-size: 20px;">⚠️</div>
          <h3 class="entry-card-title" style="font-size: 16px;">Your SIP payment was not debited?</h3>
        </div>
        <p class="entry-card-desc" style="font-size: 13px;">
          Understand what happened and explore your next steps. Mandate recovery & penalty guidelines.
        </p>
        <button class="btn btn-secondary btn-sm entry-cta-btn" id="btn-guidance-missed-payment" style="margin-top: 12px; background: white; border: 1.5px solid var(--border-medium);">
          <span>Resolve Payment Issue →</span>
        </button>
      </div>

      <div class="entry-card" style="padding: 20px; background: #f0fdf4; border: 1.5px solid var(--primary-border);">
        <div class="entry-card-badge" style="background: var(--primary-light); color: var(--primary);">Flexible Contribution</div>
        <div class="entry-card-header">
          <div class="entry-card-icon" style="font-size: 20px;">🎯</div>
          <h3 class="entry-card-title" style="font-size: 16px;">Voluntary Smaller Investment</h3>
        </div>
        <p class="entry-card-desc" style="font-size: 13px;">
          Explore a smaller one-time investment in the same fund without modifying your recurring SIP.
        </p>
        <button class="btn btn-primary btn-sm entry-cta-btn" id="btn-guidance-flex-contrib" style="margin-top: 12px;">
          <span>Flexible Contribution →</span>
        </button>
      </div>
    </div>

    <!-- Quick Options Summary Grid -->
    <div class="guidance-cards-grid">
      <div class="guidance-feature-card">
        <div class="guidance-card-icon">⏭️</div>
        <h3 class="guidance-card-title">Skip Next Instalment</h3>
        <p class="guidance-card-body">
          Temporarily skips just one upcoming monthly debit without cancelling your recurring mandate. Your SIP automatically resumes the following month.
        </p>
        <div class="guidance-card-timing">Notice: ≥2 business days prior</div>
      </div>

      <div class="guidance-feature-card">
        <div class="guidance-card-icon">⏸️</div>
        <h3 class="guidance-card-title">Pause SIP</h3>
        <p class="guidance-card-body">
          Temporarily halts deductions for a specified period (1 to 6 months depending on AMC policy). All existing accumulated units remain invested.
        </p>
        <div class="guidance-card-timing">Notice: ≥2 business days prior</div>
      </div>

      <div class="guidance-feature-card">
        <div class="guidance-card-icon">🛑</div>
        <h3 class="guidance-card-title">Cancel SIP</h3>
        <p class="guidance-card-body">
          Permanently terminates future auto-debits on that specific scheme. Zero exit penalty from mutual fund platforms; accumulated units remain intact in your folio.
        </p>
        <div class="guidance-card-timing">Notice: ≥2 business days prior</div>
      </div>
    </div>

    <!-- Platform Cutoff Comparison Table -->
    <div class="rules-table-container">
      <div class="section-heading-group" style="margin-bottom: 12px;">
        <div>
          <h2 class="section-title">Verified Platform Rules Comparison</h2>
          <div class="section-caption">Factual advance notice and execution rules verified against official documentation.</div>
        </div>
        <span class="badge-verified">Verified Rules</span>
      </div>

      <div class="sips-table-wrapper">
        <table class="sips-data-table">
          <thead>
            <tr>
              <th>Platform</th>
              <th>Advance Notice Cutoff</th>
              <th>Platform Fees</th>
              <th>Bank Bounce Impact</th>
              <th>Official Source Link</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <strong>Groww</strong><br>
                <span style="font-size: 11px; color: var(--text-muted);">AutoPay / Mandate</span>
              </td>
              <td>
                <span class="timing-badge">≥ 2 working days</span><br>
                <span style="font-size: 12px; color: var(--text-muted);">Request submitted later applies to subsequent instalment</span>
              </td>
              <td><strong>₹0</strong> (Free)</td>
              <td>Bank may charge ₹250–₹500 + GST if balance insufficient on debit day</td>
              <td>
                <a href="${VERIFIED_RULES.GROWW.sourceUrl}" target="_blank" rel="noopener noreferrer" class="external-link">
                  <span>Groww Help Centre</span> ↗
                </a>
              </td>
            </tr>

            <tr>
              <td>
                <strong>Zerodha Coin</strong><br>
                <span style="font-size: 11px; color: var(--text-muted);">BSE StAR MF Integration</span>
              </td>
              <td>
                <span class="timing-badge">≥ 2 working days (before 11 AM)</span><br>
                <span style="font-size: 12px; color: var(--text-muted);">Orders sent to exchange 2 days prior</span>
              </td>
              <td><strong>₹0</strong> (Free)</td>
              <td>Orders simply fail on exchange if trading balance/mandate is unfunded</td>
              <td>
                <a href="${VERIFIED_RULES.ZERODHA.sourceUrl}" target="_blank" rel="noopener noreferrer" class="external-link">
                  <span>Zerodha Support</span> ↗
                </a>
              </td>
            </tr>

            <tr>
              <td>
                <strong>AMC Direct</strong><br>
                <span style="font-size: 11px; color: var(--text-muted);">CAMS / KFintech / NACH</span>
              </td>
              <td>
                <span class="timing-badge">10 to 21 calendar days</span><br>
                <span style="font-size: 12px; color: var(--text-muted);">Clearing batch schedules require physical/electronic lead time</span>
              </td>
              <td><strong>₹0</strong> (Free)</td>
              <td>Bank clearing bounce charges apply on failed ECS/NACH presentation</td>
              <td>
                <a href="${VERIFIED_RULES.AMC_DIRECT.sourceUrl}" target="_blank" rel="noopener noreferrer" class="external-link">
                  <span>AMFI India Investor Guidelines</span> ↗
                </a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Critical Truths / FAQs -->
    <div class="faq-accordion-group">
      <h2 class="section-title" style="margin-bottom: 16px;">Important Things Every SIP Investor Should Know</h2>

      <div class="faq-item">
        <div class="faq-question">1. Does 1 missed SIP payment cancel my mutual fund investment?</div>
        <div class="faq-answer">
          <strong>No.</strong> A single missed payment or bank debit failure will never cancel your mutual fund SIP or forfeit your accumulated units. Under SEBI regulations and standard AMC policies, an automated SIP is only cancelled if <strong>3 consecutive monthly instalments fail</strong> due to insufficient balance.
        </div>
      </div>

      <div class="faq-item">
        <div class="faq-question">2. Does Groww or Zerodha charge a penalty for pausing or skipping?</div>
        <div class="faq-answer">
          <strong>No platform penalty is charged.</strong> Neither Groww, Zerodha, nor AMCs charge any fee to skip, pause, modify, or cancel a SIP. However, your own bank may levy an auto-debit bounce charge (typically ₹250 to ₹500 plus GST) if an auto-debit mandate is presented to your bank when your account has insufficient balance.
        </div>
      </div>

      <div class="faq-item">
        <div class="faq-question">3. What happens to my already accumulated mutual fund units?</div>
        <div class="faq-answer">
          Your accumulated units remain safely in your folio with the AMC or in your demat account, continuing to participate in the market. Pausing, skipping, or cancelling future SIP debits has zero impact on units you have already purchased.
        </div>
      </div>

      <div class="faq-item">
        <div class="faq-question">4. Can I restart my SIP at a lower monthly amount?</div>
        <div class="faq-answer">
          Yes. Most schemes allow minimum SIP amounts of ₹100 or ₹500. If your current monthly amount is causing cash-flow strain, you can create a new SIP at a lower amount once your current one is paused or cancelled, provided it meets the scheme's minimum instalment threshold.
        </div>
      </div>
    </div>
  `;

  const btnHelp = container.querySelector("#btn-guidance-start-help");
  if (btnHelp && onStartRescue) {
    btnHelp.addEventListener("click", () => onStartRescue());
  }

  const btnPlanAhead = container.querySelector("#btn-guidance-plan-ahead");
  if (btnPlanAhead && onPlanAhead) {
    btnPlanAhead.addEventListener("click", () => onPlanAhead());
  }

  const btnMissed = container.querySelector("#btn-guidance-missed-payment");
  if (btnMissed && onMissedPayment) {
    btnMissed.addEventListener("click", () => onMissedPayment());
  }

  const btnFlex = container.querySelector("#btn-guidance-flex-contrib");
  if (btnFlex && onFlexibleContribution) {
    btnFlex.addEventListener("click", () => onFlexibleContribution());
  }

  return container;
}
