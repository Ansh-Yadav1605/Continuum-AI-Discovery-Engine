/**
 * sip-rescue-mvp/js/components/Sidebar.js
 * 
 * Dark Navy Left Navigation Sidebar for SIP Rescue Dashboard.
 * 
 * Navigation Items:
 * - Overview
 * - My SIPs
 * - Get SIP Help
 * - Comeback Plan
 * - Help & Guidance
 */

import { DEMO_SCENARIOS } from "../data/demoScenarios.js?v=2";

export function renderSidebar({ activeScreen, onNavigate, onSelectScenario, isMobileOpen = false, onToggleMobile }) {
  const sidebar = document.createElement("aside");
  sidebar.className = `app-sidebar ${isMobileOpen ? 'mobile-open' : ''}`;
  sidebar.id = "app-sidebar";

  sidebar.innerHTML = `
    <!-- Top Branding -->
    <div class="sidebar-brand-group" id="sidebar-brand-home" role="button" tabindex="0" title="Return to Overview">
      <div class="sidebar-brand-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="34" height="34" fill="none" aria-hidden="true">
          <rect width="32" height="32" rx="8" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1.2"/>
          <path d="M15.5 6.5C21.5 6.8 24.5 10.5 24.5 16.5C19.2 16.5 16.2 13 15.5 6.5Z" fill="#047857"/>
          <path d="M8.5 16.5C10.5 20.8 14 23.5 18 23.5C22.2 23.5 24.5 20.2 24.5 16.5" stroke="#10B981" stroke-width="2" stroke-linecap="round"/>
          <path d="M9.5 17L13.8 21.2L22.8 10.2" stroke="#047857" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="sidebar-brand-text">
        <div class="sidebar-brand-title">SIP Rescue</div>
        <div class="sidebar-brand-subtitle">SIP Continuity Assistant</div>
      </div>
    </div>

    <!-- Navigation Links -->
    <nav class="sidebar-nav">
      <div class="sidebar-nav-section-label">MAIN NAVIGATION</div>

      <button class="sidebar-nav-item ${activeScreen === 'home' ? 'active' : ''}" data-nav="home">
        <span class="sidebar-nav-icon">📊</span>
        <span class="sidebar-nav-label">Overview</span>
      </button>

      <button class="sidebar-nav-item ${activeScreen === 'sips' ? 'active' : ''}" data-nav="sips">
        <span class="sidebar-nav-icon">💼</span>
        <span class="sidebar-nav-label">My SIPs</span>
      </button>

      <button class="sidebar-nav-item ${activeScreen === 'navigator' ? 'active' : ''}" data-nav="navigator">
        <span class="sidebar-nav-icon">🆘</span>
        <span class="sidebar-nav-label">Get SIP Help</span>
        <span class="sidebar-nav-pill">Core</span>
      </button>

      <button class="sidebar-nav-item ${activeScreen === 'comeback' ? 'active' : ''}" data-nav="comeback">
        <span class="sidebar-nav-icon">🗓️</span>
        <span class="sidebar-nav-label">Comeback Plan</span>
      </button>

      <button class="sidebar-nav-item ${activeScreen === 'guidance' ? 'active' : ''}" data-nav="guidance">
        <span class="sidebar-nav-icon">📖</span>
        <span class="sidebar-nav-label">Help & Guidance</span>
      </button>

      <div class="sidebar-nav-section-label" style="margin-top: 14px;">ASSISTANCE FLOWS</div>

      <button class="sidebar-nav-item ${activeScreen === 'plan-ahead' ? 'active' : ''}" data-nav="plan-ahead">
        <span class="sidebar-nav-icon">🗓️</span>
        <span class="sidebar-nav-label">Plan Ahead</span>
        <span class="sidebar-nav-pill" style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7;">New</span>
      </button>

      <button class="sidebar-nav-item ${activeScreen === 'missed-payment' ? 'active' : ''}" data-nav="missed-payment">
        <span class="sidebar-nav-icon">⚠️</span>
        <span class="sidebar-nav-label">Missed Payment</span>
        <span class="sidebar-nav-pill" style="background: rgba(239, 68, 68, 0.2); color: #fca5a5;">Rescue</span>
      </button>

      <button class="sidebar-nav-item ${activeScreen === 'flexible-contribution' ? 'active' : ''}" data-nav="flexible-contribution">
        <span class="sidebar-nav-icon">🎯</span>
        <span class="sidebar-nav-label">Flexible Contribution</span>
      </button>
    </nav>

    <!-- Sidebar Bottom Utilities & Assessor Scenarios -->
    <div class="sidebar-footer">
      <div class="sidebar-demo-box">
        <div class="sidebar-demo-header">
          <span>⚡ Try a demo scenario</span>
        </div>
        <div class="sidebar-scenarios-list">
          ${DEMO_SCENARIOS.map(s => `
            <button class="sidebar-scenario-btn" data-scenario-id="${s.id}">
              <div class="sidebar-scenario-title">${s.title}</div>
              <div class="sidebar-scenario-desc">${s.tag}</div>
            </button>
          `).join('')}
        </div>
      </div>

      <div class="sidebar-mode-indicator">
        <span class="sidebar-mode-dot"></span>
        <span>Sample Portfolio — Demo Mode</span>
      </div>
    </div>
  `;

  // Attach event handlers
  const brandHome = sidebar.querySelector("#sidebar-brand-home");
  brandHome.addEventListener("click", () => onNavigate("home"));
  brandHome.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onNavigate("home");
    }
  });

  sidebar.querySelectorAll(".sidebar-nav-item").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const target = e.currentTarget.getAttribute("data-nav");
      if (onToggleMobile) onToggleMobile(false);
      onNavigate(target);
    });
  });

  sidebar.querySelectorAll(".sidebar-scenario-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const scenarioId = e.currentTarget.getAttribute("data-scenario-id");
      const scenario = DEMO_SCENARIOS.find(s => s.id === scenarioId);
      if (onToggleMobile) onToggleMobile(false);
      if (scenario && onSelectScenario) {
        onSelectScenario(scenario);
      }
    });
  });

  return sidebar;
}
