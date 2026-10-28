/**
 * sip-rescue-mvp/js/components/SipDetailScreen.js
 * 
 * Screen Two: Focused SIP Details
 * 
 * Top Section:
 * - Fund name, AMC name, SIP amount & frequency, next scheduled date, status badge, primary CTA "Get SIP Help"
 * 
 * Information Cards:
 * - SIP schedule & mandate method
 * - Platform details & applicable cutoff rules
 * - Bank mandate status & clearing note
 * 
 * Factual Timeline:
 * - Stage 1: Check the applicable modification deadline
 * - Stage 2: Review scheduled payment and mandate status
 * - Stage 3: Check transaction processing and unit-allotment status
 */

export function renderSipDetailScreen({
  sip,
  onBack,
  onStartRescue,
  onViewRules,
  onPlanAhead,
  onMissedPayment,
  onFlexibleContribution
}) {
  const container = document.createElement("div");
  container.className = "sip-detail-screen-container";

  // Stage 1: Conditional on platform & setupType
  let stage1Label = "1. Check Applicable Modification Deadline";
  let stage1Desc = "Notice cutoffs depend on your platform and mandate type. App-managed SIPs typically require ~2 working days advance notice, while direct AMC mandates require 10–21 calendar days notice.";

  if (sip.platform === "Groww" && sip.setupType === "Platform-managed SIP") {
    stage1Label = "1. Modification Deadline (≥2 Working Days on Groww)";
    stage1Desc = "Groww AutoPay requires at least 2 working days advance notice to skip or pause before debit generation. Mandates registered directly with the AMC require longer notice.";
  } else if (sip.platform === "Zerodha Coin" && sip.setupType === "Platform-managed SIP") {
    stage1Label = "1. Modification Deadline (≥2 Working Days on Coin)";
    stage1Desc = "Zerodha Coin requires modification or pause requests at least 2 working days prior (before 11:00 AM on T-2 days) before orders are sent to BSE StAR MF.";
  } else if (sip.setupType === "AMC-registered SIP") {
    stage1Label = "1. Mandate Notice Window (10–21 Calendar Days)";
    stage1Desc = "Direct AMC/NACH mandates require 10 to 21 calendar days prior notice to clear bank clearing house batch cycles.";
  }

  // Stage 2: Scheduled payment attempt
  const stage2Label = "2. Scheduled Payment & Mandate Execution";
  const stage2Desc = `A scheduled payment attempt is triggered on your debit date. Execution depends on your payment arrangement (${sip.mandateMethod}) and bank clearing processing.`;

  // Stage 3: Allotment & NAV realization
  const stage3Label = "3. Transaction Processing & Unit Allotment";
  const stage3Desc = "Applicable NAV and allotment timing depend on regulatory cut-off timings and actual realization of funds by the AMC. Allotment typically reflects 1–2 business days after fund realization; fixed dates are not guaranteed.";

  container.innerHTML = `
    <!-- Top Breadcrumb & Back Action -->
    <div class="screen-page-header" style="margin-bottom: 20px;">
      <div>
        <div class="breadcrumb-nav">
          <span class="breadcrumb-item"><a href="#sips" id="btn-back-breadcrumb">My SIPs</a></span>
          <span class="breadcrumb-sep">/</span>
          <span class="breadcrumb-active">${sip.schemeName}</span>
        </div>
        <div class="detail-amc-badge">${sip.amc}</div>
        <h1 class="screen-page-title" style="margin-top: 4px;">${sip.schemeName}</h1>
        <div class="scheme-subtext-meta">
          <span>${sip.planOption}</span>
          <span>•</span>
          <span>ISIN: ${sip.isin} (Verified Scheme)</span>
          <span>•</span>
          <a href="${sip.amcWebsite}" target="_blank" rel="noopener noreferrer" class="external-link">
            <span>AMC Website</span> ↗
          </a>
        </div>
      </div>

      <div class="detail-header-cta-group">
        <button class="btn btn-secondary btn-sm" id="btn-back-sips-list">
          ← Back to My SIPs
        </button>
        <button class="btn btn-secondary btn-sm" id="btn-detail-flex-contrib" title="Make an affordable one-time investment">
          <span>🎯 Flexible Contribution</span>
        </button>
        <button class="btn btn-primary btn-sm" id="btn-detail-get-help">
          <span style="font-size: 15px;">🆘</span>
          <span>Get SIP Help</span>
        </button>
      </div>
    </div>

    <!-- Top Key Metric Cards Grid -->
    <div class="detail-overview-grid">
      <div class="detail-stat-card">
        <div class="meta-field-label">Monthly SIP Commitment</div>
        <div class="detail-stat-val">₹${sip.monthlyAmount.toLocaleString("en-IN")}</div>
        <div class="detail-stat-sub">${sip.frequency}</div>
      </div>

      <div class="detail-stat-card">
        <div class="meta-field-label">Next Scheduled Date</div>
        <div class="detail-stat-val ${sip.statusTone === 'warning' ? 'text-warning' : ''}">${sip.nextDebitRelative}</div>
        <div class="detail-stat-sub">${sip.nextDebitDate}</div>
      </div>

      <div class="detail-stat-card">
        <div class="meta-field-label">Platform & Setup Type</div>
        <div class="detail-stat-val">${sip.platform}</div>
        <div class="detail-stat-sub">${sip.setupType}</div>
      </div>

      <div class="detail-stat-card">
        <div class="meta-field-label">Status & Mandate Method</div>
        <div class="detail-stat-val">
          <span class="status-badge ${sip.statusTone}">
            ● ${sip.statusTone === 'warning' ? 'Due Soon (Attention)' : 'Active'}
          </span>
        </div>
        <div class="detail-stat-sub">${sip.mandateMethod}</div>
      </div>
    </div>

    <!-- Factual Neutral 3-Stage Timeline -->
    <div class="detail-section-card">
      <div class="section-heading-group">
        <div>
          <h2 class="section-title">Instalment Lifecycle & Notice Stages</h2>
          <div class="section-caption">Factual lifecycle stages for your upcoming payment attempt. Universal deadlines are not assumed.</div>
        </div>
        <span class="badge-verified">Verified Process</span>
      </div>

      <div class="timeline-stepper-grid">
        <div class="timeline-step-card ${sip.statusTone === 'warning' ? 'step-warning' : ''}">
          <div class="step-num-badge">STAGE 1</div>
          <div class="step-card-title">${stage1Label}</div>
          <div class="step-card-desc">${stage1Desc}</div>
        </div>

        <div class="timeline-step-card">
          <div class="step-num-badge">STAGE 2</div>
          <div class="step-card-title">${stage2Label}</div>
          <div class="step-card-desc">${stage2Desc}</div>
        </div>

        <div class="timeline-step-card">
          <div class="step-num-badge">STAGE 3</div>
          <div class="step-card-title">${stage3Label}</div>
          <div class="step-card-desc">${stage3Desc}</div>
        </div>
      </div>
    </div>

    <!-- Information Cards: Schedule & Rules Accordion -->
    <div class="detail-two-col-grid">
      <!-- Card A: SIP Schedule & Mandate Details -->
      <div class="detail-info-card">
        <h3 class="info-card-heading">📅 SIP Schedule Details</h3>
        <div class="info-detail-rows">
          <div class="info-row">
            <span class="info-row-label">Scheduled Amount:</span>
            <span class="info-row-val">₹${sip.monthlyAmount.toLocaleString("en-IN")} on ${sip.frequency}</span>
          </div>
          <div class="info-row">
            <span class="info-row-label">Next Scheduled Run:</span>
            <span class="info-row-val">${sip.nextDebitDate} (${sip.nextDebitRelative})</span>
          </div>
          <div class="info-row">
            <span class="info-row-label">Bank Mandate Reference:</span>
            <span class="info-row-val">${sip.folioNumber}-NPCI-DEMO</span>
          </div>
          <div class="info-row">
            <span class="info-row-label">Payment Authentication:</span>
            <span class="info-row-val">${sip.mandateMethod}</span>
          </div>
        </div>
      </div>

      <!-- Card B: Applicable Rules & Fees -->
      <div class="detail-info-card">
        <h3 class="info-card-heading">📋 Applicable Rules & Cutoffs</h3>
        <div class="info-detail-rows">
          <div class="info-row">
            <span class="info-row-label">Platform Modification Fee:</span>
            <span class="info-row-val" style="color: var(--primary); font-weight: 700;">₹0 (Free)</span>
          </div>
          <div class="info-row">
            <span class="info-row-label">Bank Mandate Bounce Fee:</span>
            <span class="info-row-val" style="color: var(--warning-text);">₹250–₹500 + GST (Bank only)</span>
          </div>
          <div class="info-row">
            <span class="info-row-label">Accumulated Units Safety:</span>
            <span class="info-row-val" style="color: var(--primary);">100% Intact in Folio</span>
          </div>
          <div class="info-row">
            <span class="info-row-label">Auto-Cancellation Rule:</span>
            <span class="info-row-val">Only after 3 consecutive failures</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Illustrative Demo Disclaimer -->
    <div class="demo-disclaimer-box" style="margin-top: 24px;">
      <div style="font-size: 15px;">🔒</div>
      <div>
        <strong>Demonstration Protocol:</strong>
        This screen presents an illustrative demo view of an Indian mutual fund SIP. SIP Rescue does not link to live broker accounts or initiate debit authorizations.
      </div>
    </div>
  `;

  // Attach handlers
  const handleBack = () => {
    if (onBack) onBack();
  };

  const btnBreadcrumb = container.querySelector("#btn-back-breadcrumb");
  if (btnBreadcrumb) btnBreadcrumb.addEventListener("click", (e) => { e.preventDefault(); handleBack(); });

  const btnBackList = container.querySelector("#btn-back-sips-list");
  if (btnBackList) btnBackList.addEventListener("click", handleBack);

  const btnGetHelp = container.querySelector("#btn-detail-get-help");
  if (btnGetHelp) btnGetHelp.addEventListener("click", () => {
    if (onStartRescue) onStartRescue(sip);
  });

  const btnFlexContrib = container.querySelector("#btn-detail-flex-contrib");
  if (btnFlexContrib) btnFlexContrib.addEventListener("click", () => {
    if (onFlexibleContribution) onFlexibleContribution(sip);
  });

  return container;
}
