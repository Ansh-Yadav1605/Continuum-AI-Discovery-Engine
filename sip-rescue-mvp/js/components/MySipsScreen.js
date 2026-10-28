/**
 * sip-rescue-mvp/js/components/MySipsScreen.js
 * 
 * Dedicated SIP Management Screen (#sips):
 * - Page Title: "My SIPs"
 * - Subtitle: "Review your SIPs and find guidance when you need it."
 * - Search field + Status filters (All, Active, Due Soon) + AMC filters
 * - Desktop table / scannable grid view with responsive cards for mobile
 * - Displays: Fund name, monthly amount, next scheduled date, platform & payment method, status, View details & Get help actions
 */

import { SAMPLE_SIPS } from "../data/sampleSips.js?v=2";

export function renderMySipsScreen({ onSelectSip, onStartRescue }) {
  const container = document.createElement("div");
  container.className = "mysips-screen-container";

  // State
  let searchQuery = "";
  let statusFilter = "all"; // 'all' | 'active' | 'warning'
  let amcFilter = "all";    // 'all' | 'HDFC' | 'SBI' | 'ICICI Prudential'

  function getFilteredSips() {
    return SAMPLE_SIPS.filter(sip => {
      // Search text match
      const query = searchQuery.trim().toLowerCase();
      if (query) {
        const matchName = sip.schemeName.toLowerCase().includes(query);
        const matchAmc = sip.amc.toLowerCase().includes(query);
        const matchPlatform = sip.platform.toLowerCase().includes(query);
        const matchMethod = sip.mandateMethod.toLowerCase().includes(query);
        if (!matchName && !matchAmc && !matchPlatform && !matchMethod) return false;
      }

      // Status filter
      if (statusFilter === "active" && sip.statusTone !== "normal") return false;
      if (statusFilter === "warning" && sip.statusTone !== "warning") return false;

      // AMC filter
      if (amcFilter !== "all" && sip.amcShort !== amcFilter) return false;

      return true;
    });
  }

  function render() {
    const filtered = getFilteredSips();

    container.innerHTML = `
      <!-- Header Area -->
      <div class="screen-page-header">
        <div>
          <div class="breadcrumb-nav">
            <span class="breadcrumb-item">Dashboard</span>
            <span class="breadcrumb-sep">/</span>
            <span class="breadcrumb-active">My SIPs</span>
          </div>
          <h1 class="screen-page-title">My SIPs</h1>
          <p class="screen-page-subtitle">Review your SIPs and find guidance when you need it.</p>
        </div>
        <div class="demo-badge-pill">
          Sample Portfolio — Demo Data
        </div>
      </div>

      <!-- Controls Bar: Search & Filter Pills -->
      <div class="sips-controls-card">
        <div class="sips-search-box">
          <span class="search-input-icon">🔍</span>
          <input 
            type="text" 
            id="sips-local-search" 
            class="sips-filter-input" 
            placeholder="Search by fund, AMC, platform, or mandate..." 
            value="${escapeHtml(searchQuery)}"
            aria-label="Filter SIPs"
          />
          ${searchQuery ? `<button class="btn-clear-search" id="btn-clear-sips-search" title="Clear search">✕</button>` : ''}
        </div>

        <div class="sips-filters-row">
          <!-- Status Filters -->
          <div class="filter-group">
            <span class="filter-group-label">Status:</span>
            <div class="filter-pill-stack">
              <button class="filter-pill ${statusFilter === 'all' ? 'active' : ''}" data-filter-type="status" data-filter-val="all">All (${SAMPLE_SIPS.length})</button>
              <button class="filter-pill ${statusFilter === 'active' ? 'active' : ''}" data-filter-type="status" data-filter-val="active">Active</button>
              <button class="filter-pill ${statusFilter === 'warning' ? 'active' : ''}" data-filter-type="status" data-filter-val="warning">Due Soon (Attention)</button>
            </div>
          </div>

          <!-- AMC Filters -->
          <div class="filter-group">
            <span class="filter-group-label">AMC:</span>
            <div class="filter-pill-stack">
              <button class="filter-pill ${amcFilter === 'all' ? 'active' : ''}" data-filter-type="amc" data-filter-val="all">All AMCs</button>
              <button class="filter-pill ${amcFilter === 'HDFC' ? 'active' : ''}" data-filter-type="amc" data-filter-val="HDFC">HDFC</button>
              <button class="filter-pill ${amcFilter === 'SBI' ? 'active' : ''}" data-filter-type="amc" data-filter-val="SBI">SBI</button>
              <button class="filter-pill ${amcFilter === 'ICICI Prudential' ? 'active' : ''}" data-filter-type="amc" data-filter-val="ICICI Prudential">ICICI Pru</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Content Table / Grid -->
      ${filtered.length === 0 ? `
        <div class="sips-empty-state">
          <div style="font-size: 32px; margin-bottom: 8px;">🔍</div>
          <h3 style="font-size: 16px; font-weight: 700; color: var(--text-main); margin-bottom: 4px;">No matching SIPs found</h3>
          <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">Try adjusting your search query or active filters.</p>
          <button class="btn btn-secondary btn-sm" id="btn-reset-filters">Reset All Filters</button>
        </div>
      ` : `
        <!-- Desktop Table View -->
        <div class="sips-table-wrapper">
          <table class="sips-data-table" aria-label="SIP Investments Table">
            <thead>
              <tr>
                <th>Fund / Scheme</th>
                <th>Monthly Amount</th>
                <th>Next Scheduled Date</th>
                <th>Platform & Mandate</th>
                <th>Status</th>
                <th style="text-align: right;">Actions</th>
              </tr>
            </thead>
            <tbody>
              ${filtered.map(sip => `
                <tr class="sip-table-row" data-sip-id="${sip.id}">
                  <td>
                    <div class="table-amc-tag">${sip.amc}</div>
                    <div class="table-fund-title">${sip.schemeName}</div>
                    <div class="table-fund-sub">${sip.planOption} • ISIN: ${sip.isin}</div>
                  </td>
                  <td>
                    <div class="table-amount">₹${sip.monthlyAmount.toLocaleString("en-IN")}</div>
                    <div class="table-frequency">${sip.frequency}</div>
                  </td>
                  <td>
                    <div class="table-date">${sip.nextDebitDate}</div>
                    <div class="table-relative ${sip.statusTone === 'warning' ? 'text-warning' : ''}">${sip.nextDebitRelative}</div>
                  </td>
                  <td>
                    <div class="table-platform">${sip.platform}</div>
                    <div class="table-mandate">${sip.mandateMethod}</div>
                  </td>
                  <td>
                    <span class="status-badge ${sip.statusTone}">
                      ● ${sip.statusTone === 'warning' ? 'Due Soon' : 'Active'}
                    </span>
                    ${sip.needsAttention ? `<div class="table-attention-hint">${sip.attentionReason}</div>` : ''}
                  </td>
                  <td style="text-align: right;">
                    <div class="table-action-buttons">
                      <button class="btn btn-secondary btn-sm btn-table-view" data-sip-id="${sip.id}" title="View detailed breakdown">
                        View
                      </button>
                      <button class="btn btn-primary btn-sm btn-table-help" data-sip-id="${sip.id}" title="Get personalized continuity guidance">
                        Get Help
                      </button>
                    </div>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- Mobile Card View (shown via CSS media queries) -->
        <div class="sips-mobile-cards-list">
          ${filtered.map(sip => `
            <div class="sip-mobile-card" data-sip-id="${sip.id}">
              <div class="sip-mobile-header">
                <div>
                  <div class="sip-amc-tag">${sip.amc}</div>
                  <div class="sip-scheme-name">${sip.schemeName}</div>
                  <div class="sip-plan-option">${sip.planOption}</div>
                </div>
                <span class="status-badge ${sip.statusTone}">
                  ● ${sip.statusTone === 'warning' ? 'Due Soon' : 'Active'}
                </span>
              </div>

              <div class="sip-mobile-meta-grid">
                <div>
                  <div class="meta-field-label">Monthly SIP</div>
                  <div class="meta-field-val">₹${sip.monthlyAmount.toLocaleString("en-IN")}</div>
                  <div class="meta-field-sub">${sip.frequency}</div>
                </div>
                <div>
                  <div class="meta-field-label">Next Scheduled Date</div>
                  <div class="meta-field-val">${sip.nextDebitRelative}</div>
                  <div class="meta-field-sub">${sip.nextDebitDate}</div>
                </div>
                <div>
                  <div class="meta-field-label">Platform</div>
                  <div class="meta-field-val">${sip.platform}</div>
                  <div class="meta-field-sub">${sip.setupType}</div>
                </div>
                <div>
                  <div class="meta-field-label">Payment Method</div>
                  <div class="meta-field-val">${sip.mandateMethod}</div>
                  <div class="meta-field-sub">NPCI Authenticated</div>
                </div>
              </div>

              ${sip.needsAttention ? `
                <div class="mobile-attention-callout">
                  ⚠️ <strong>Notice:</strong> ${sip.attentionReason}. ${sip.nextStepHint}.
                </div>
              ` : ''}

              <div class="sip-card-actions">
                <button class="btn btn-secondary btn-sm btn-mobile-view" data-sip-id="${sip.id}">
                  View Details
                </button>
                <button class="btn btn-primary btn-sm btn-mobile-help" data-sip-id="${sip.id}">
                  Get SIP Help
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      `}

      <!-- Footer Demo Notice -->
      <div class="demo-disclaimer-box" style="margin-top: 24px;">
        <div style="font-size: 15px;">🔒</div>
        <div>
          <strong>Non-Transactional Demo:</strong>
          This management screen displays sample portfolio records for prototype demonstration. It does not initiate broker modifications, bank mandates, or payment instructions.
        </div>
      </div>
    `;

    // Attach listeners
    const searchInput = container.querySelector("#sips-local-search");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        searchQuery = e.target.value;
        render();
      });
    }

    const clearBtn = container.querySelector("#btn-clear-sips-search");
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        searchQuery = "";
        render();
      });
    }

    const resetBtn = container.querySelector("#btn-reset-filters");
    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        searchQuery = "";
        statusFilter = "all";
        amcFilter = "all";
        render();
      });
    }

    container.querySelectorAll(".filter-pill").forEach(pill => {
      pill.addEventListener("click", (e) => {
        const type = e.currentTarget.getAttribute("data-filter-type");
        const val = e.currentTarget.getAttribute("data-filter-val");
        if (type === "status") statusFilter = val;
        if (type === "amc") amcFilter = val;
        render();
      });
    });

    // View & Help button handlers (Table and Mobile)
    container.querySelectorAll(".btn-table-view, .btn-mobile-view").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const sipId = e.currentTarget.getAttribute("data-sip-id");
        const sip = SAMPLE_SIPS.find(s => s.id === sipId);
        if (sip && onSelectSip) onSelectSip(sip);
      });
    });

    container.querySelectorAll(".btn-table-help, .btn-mobile-help").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const sipId = e.currentTarget.getAttribute("data-sip-id");
        const sip = SAMPLE_SIPS.find(s => s.id === sipId);
        if (sip && onStartRescue) onStartRescue(sip);
      });
    });

    // Row click
    container.querySelectorAll(".sip-table-row").forEach(row => {
      row.addEventListener("click", (e) => {
        // Only if not clicking a button
        if (e.target.closest("button")) return;
        const sipId = row.getAttribute("data-sip-id");
        const sip = SAMPLE_SIPS.find(s => s.id === sipId);
        if (sip && onSelectSip) onSelectSip(sip);
      });
    });
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/[&<>'"]/g, 
      tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag));
  }

  render();
  return container;
}
