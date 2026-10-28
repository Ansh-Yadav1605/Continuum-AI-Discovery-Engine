/**
 * sip-rescue-mvp/js/components/HomeScreen.js
 * 
 * Screen One: Overview Dashboard
 * Inspired by modern Indian fintech investment dashboards.
 * 
 * Answers 3 questions immediately:
 * 1. What is the current status of my SIPs?
 * 2. Is there anything I need to pay attention to?
 * 3. What should I do next if I am having difficulty continuing a SIP?
 * 
 * Sections:
 * 1. Welcome header: "Your SIPs, made easier to manage" + CTA "Get SIP Help"
 * 2. 4 Summary cards: Active SIPs, Monthly SIP commitment, Next instalment, Needs attention
 * 3. SIP Portfolio Overview: Scannable rows/cards with status badges, hints, and actions
 * 4. Recommended Next Step: "Need help with an upcoming SIP? Explore my options"
 * 5. Honest demo mode disclaimer
 */

import { SAMPLE_SIPS, PORTFOLIO_SUMMARY } from "../data/sampleSips.js?v=2";

export function renderHomeScreen({
  onSelectSip,
  onStartRescue,
  onNavigateExplore,
  onPlanAhead,
  onMissedPayment,
  onFlexibleContribution
}) {
  const container = document.createElement("div");
  container.className = "overview-dashboard-container";

  container.innerHTML = `
    <!-- Section 1: Welcome Header -->
    <div class="overview-welcome-header">
      <div class="welcome-header-content">
        <div class="welcome-badge-row">
          <span class="welcome-pill">Investment Continuity Assistant</span>
          <span class="demo-badge-pill">${PORTFOLIO_SUMMARY.modeLabel}</span>
        </div>
        <h1 class="welcome-title">Your SIPs, made easier to manage</h1>
        <p class="welcome-subtitle">
          Understand your options when your financial circumstances change.
        </p>
      </div>

      <div class="welcome-header-action">
        <button class="btn btn-primary welcome-cta-btn" id="btn-overview-get-help" title="Start guided SIP continuity rescue">
          <span style="font-size: 15px;">🆘</span>
          <span>Get SIP Help</span>
        </button>
      </div>
    </div>

    <!-- Section 2: Summary Cards (4 Horizontally Aligned Cards on Desktop) -->
    <div class="summary-cards-row">
      <!-- Card 1: Active SIPs -->
      <div class="dashboard-stat-card card-active-sips">
        <div class="stat-card-header">
          <span class="stat-card-label">Active SIPs</span>
          <span class="stat-card-icon">💼</span>
        </div>
        <div class="stat-card-main-val">
          ${PORTFOLIO_SUMMARY.activeCount}
          <span class="stat-card-sublabel">Currently active</span>
        </div>
        <div class="stat-card-footer">
          <span>3 verified mutual funds</span>
        </div>
      </div>

      <!-- Card 2: Monthly SIP Commitment -->
      <div class="dashboard-stat-card card-commitment">
        <div class="stat-card-header">
          <span class="stat-card-label">Monthly SIP Commitment</span>
          <span class="stat-card-icon">📊</span>
        </div>
        <div class="stat-card-main-val">
          ₹${PORTFOLIO_SUMMARY.plannedCommitment.toLocaleString("en-IN")}
          <span class="stat-card-sublabel">Planned monthly amount</span>
        </div>
        <div class="stat-card-footer">
          <span class="stat-note-highlight">₹0 paid so far this month (demo)</span>
        </div>
      </div>

      <!-- Card 3: Next Instalment -->
      <div class="dashboard-stat-card card-next-debit">
        <div class="stat-card-header">
          <span class="stat-card-label">Next Instalment</span>
          <span class="stat-card-icon">🗓️</span>
        </div>
        <div class="stat-card-main-val stat-val-warning">
          ₹${PORTFOLIO_SUMMARY.nextInstalmentAmount.toLocaleString("en-IN")}
          <span class="stat-card-sublabel">Due in 2 days (Oct 29)</span>
        </div>
        <div class="stat-card-footer">
          <span>${PORTFOLIO_SUMMARY.nextInstalmentFund}</span>
        </div>
      </div>

      <!-- Card 4: Needs Attention -->
      <div class="dashboard-stat-card card-attention ${PORTFOLIO_SUMMARY.needsAttentionCount > 0 ? 'attention-active' : ''}">
        <div class="stat-card-header">
          <span class="stat-card-label">Needs Attention</span>
          <span class="stat-card-icon">⚠️</span>
        </div>
        <div class="stat-card-main-val stat-val-attention">
          ${PORTFOLIO_SUMMARY.needsAttentionCount} SIP
          <span class="stat-card-sublabel">Approaching notice cutoff</span>
        </div>
        <div class="stat-card-footer">
          <span style="color: var(--warning-text); font-weight: 500;">Action needed within 48h</span>
        </div>
      </div>
    </div>

    <!-- Section: Two Main Assistance Entry Points (Plan Ahead & Missed Payment Rescue) -->
    <div class="assistance-entry-cards-grid">
      <!-- Entry Point A: Plan Ahead -->
      <div class="entry-card plan-ahead-entry-card">
        <div class="entry-card-badge">Upcoming Debit Assistance</div>
        <div class="entry-card-header">
          <div class="entry-card-icon plan-ahead-icon">🗓️</div>
          <h2 class="entry-card-title">Know you cannot afford your next SIP?</h2>
        </div>
        <p class="entry-card-desc">
          Explore your options before your next scheduled payment. Skip, pause, or step down without losing your investment habit.
        </p>
        <div class="entry-card-meta">
          <span>Upcoming: <strong>HDFC Flexi Cap Fund</strong> (₹3,000 due in 2 days)</span>
        </div>
        <div class="entry-card-action">
          <button class="btn btn-primary entry-cta-btn" id="btn-dashboard-plan-ahead">
            <span>Plan My SIP →</span>
          </button>
        </div>
      </div>

      <!-- Entry Point B: Missed Payment Rescue -->
      <div class="entry-card missed-payment-entry-card">
        <div class="entry-card-badge badge-alert">Payment Recovery & Status</div>
        <div class="entry-card-header">
          <div class="entry-card-icon missed-payment-icon">⚠️</div>
          <h2 class="entry-card-title">Your SIP payment was not debited?</h2>
        </div>
        <p class="entry-card-desc">
          Understand what happened and explore your next steps. Check mandate health, bounce fees, and continuity rules.
        </p>
        <div class="entry-card-meta">
          <span>Supported: <strong>Groww & Zerodha Coin</strong> mandate recovery guidance</span>
        </div>
        <div class="entry-card-action">
          <button class="btn btn-secondary entry-cta-btn" id="btn-dashboard-missed-payment" style="background: var(--bg-surface); border: 1.5px solid var(--border-medium); color: var(--text-main);">
            <span>Resolve Payment Issue →</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Flexible Contribution Notification Strip -->
    <div class="flexible-contrib-strip">
      <div class="strip-left">
        <span class="strip-icon">🎯</span>
        <div>
          <strong>Flexible Contribution:</strong>
          <span>Want to make an affordable smaller one-time investment in your fund without modifying your recurring SIP?</span>
        </div>
      </div>
      <button class="btn btn-subtle btn-sm strip-btn" id="btn-strip-flexible-contrib">
        Explore Flexible Contribution →
      </button>
    </div>

    <!-- Section 3: SIP Portfolio Overview -->
    <div class="portfolio-section">
      <div class="section-heading-group">
        <div>
          <h2 class="section-title">SIP Portfolio Overview</h2>
          <div class="section-caption">Current status, upcoming debits, and recommended next steps for your investments.</div>
        </div>
        <a href="#sips" class="section-link-more" id="link-view-all-sips">
          <span>View all in My SIPs</span>
          <span>→</span>
        </a>
      </div>

      <div class="portfolio-list">
        ${SAMPLE_SIPS.map(sip => `
          <div class="portfolio-row-card" data-sip-id="${sip.id}">
            <!-- Left Info -->
            <div class="row-card-primary">
              <div class="row-fund-meta">
                <span class="row-amc-pill">${sip.amc}</span>
                <span class="status-badge ${sip.statusTone}">
                  ● ${sip.statusTone === 'warning' ? 'Due Soon (Attention)' : 'Active'}
                </span>
              </div>
              <h3 class="row-fund-name">${sip.schemeName}</h3>
              <div class="row-fund-sub">${sip.planOption} • Mandate: ${sip.mandateMethod} (${sip.platform})</div>
            </div>

            <!-- Middle Columns -->
            <div class="row-card-meta-columns">
              <div class="row-meta-col">
                <div class="meta-field-label">SIP Amount</div>
                <div class="meta-field-val">₹${sip.monthlyAmount.toLocaleString("en-IN")}</div>
                <div class="meta-field-sub">${sip.frequency}</div>
              </div>

              <div class="row-meta-col">
                <div class="meta-field-label">Scheduled Date</div>
                <div class="meta-field-val ${sip.statusTone === 'warning' ? 'text-warning' : ''}">${sip.nextDebitRelative}</div>
                <div class="meta-field-sub">${sip.nextDebitDate}</div>
              </div>

              <div class="row-meta-col row-step-col">
                <div class="meta-field-label">Next Step</div>
                <div class="row-step-text ${sip.needsAttention ? 'text-attention' : ''}">${sip.nextStepHint}</div>
              </div>
            </div>

            <!-- Right Actions -->
            <div class="row-card-actions">
              <button class="btn btn-secondary btn-sm btn-row-view" data-sip-id="${sip.id}">
                View details
              </button>
              <button class="btn btn-primary btn-sm btn-row-help" data-sip-id="${sip.id}">
                Get help
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- Section 5: Honest Demo Notice -->
    <div class="demo-disclaimer-box" style="margin-top: 28px;">
      <div style="font-size: 16px;">ℹ️</div>
      <div>
        <strong>Sample Portfolio Mode:</strong>
        Scheme names shown (HDFC Flexi Cap Fund, SBI Nifty Index Fund, ICICI Prudential Balanced Advantage Fund) are verified Indian mutual funds. All portfolio balances, account numbers, and debit schedules shown are fictional demo data for prototype evaluation. This application does not connect to actual bank accounts, initiate financial transactions, or offer investment recommendations.
      </div>
    </div>
  `;

  // Attach event listeners
  const btnPlanAhead = container.querySelector("#btn-dashboard-plan-ahead");
  if (btnPlanAhead) {
    btnPlanAhead.addEventListener("click", () => {
      if (onPlanAhead) onPlanAhead(SAMPLE_SIPS[0]);
    });
  }

  const btnMissedPayment = container.querySelector("#btn-dashboard-missed-payment");
  if (btnMissedPayment) {
    btnMissedPayment.addEventListener("click", () => {
      if (onMissedPayment) onMissedPayment(SAMPLE_SIPS[0]);
    });
  }

  const btnStripFlex = container.querySelector("#btn-strip-flexible-contrib");
  if (btnStripFlex) {
    btnStripFlex.addEventListener("click", () => {
      if (onFlexibleContribution) onFlexibleContribution(SAMPLE_SIPS[0]);
    });
  }

  const btnHeroHelp = container.querySelector("#btn-overview-get-help");
  if (btnHeroHelp) {
    btnHeroHelp.addEventListener("click", () => {
      if (onStartRescue) onStartRescue(SAMPLE_SIPS[0]);
    });
  }

  const btnExplore = container.querySelector("#btn-explore-options");
  if (btnExplore) {
    btnExplore.addEventListener("click", () => {
      if (onNavigateExplore) {
        onNavigateExplore();
      } else if (onStartRescue) {
        onStartRescue(SAMPLE_SIPS[0]);
      }
    });
  }

  const linkViewAll = container.querySelector("#link-view-all-sips");
  if (linkViewAll) {
    linkViewAll.addEventListener("click", (e) => {
      e.preventDefault();
      window.location.hash = "sips";
    });
  }

  // Row buttons
  container.querySelectorAll(".btn-row-view").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const sipId = e.currentTarget.getAttribute("data-sip-id");
      const sip = SAMPLE_SIPS.find(s => s.id === sipId);
      if (sip && onSelectSip) onSelectSip(sip);
    });
  });

  container.querySelectorAll(".btn-row-help").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const sipId = e.currentTarget.getAttribute("data-sip-id");
      const sip = SAMPLE_SIPS.find(s => s.id === sipId);
      if (sip && onStartRescue) onStartRescue(sip);
    });
  });

  // Clicking row opens detail
  container.querySelectorAll(".portfolio-row-card").forEach(row => {
    row.addEventListener("click", (e) => {
      if (e.target.closest("button")) return;
      const sipId = row.getAttribute("data-sip-id");
      const sip = SAMPLE_SIPS.find(s => s.id === sipId);
      if (sip && onSelectSip) onSelectSip(sip);
    });
  });

  return container;
}
