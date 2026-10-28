/**
 * sip-rescue-mvp/js/components/Header.js
 * 
 * Top Navigation Header with Brand, Navigation Links,
 * Demo Scenario selector dropdown, and Demo Mode indicator.
 */

import { DEMO_SCENARIOS } from "../data/demoScenarios.js";

export function renderHeader(activeScreen, onNavigate, onSelectScenario) {
  const header = document.createElement("header");
  header.className = "app-header";

  header.innerHTML = `
    <div class="header-inner">
      <div class="brand-group" id="btn-brand-home" title="Return to Home">
        <div class="brand-icon" aria-label="SIP Rescue Logo">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="36" height="36" fill="none" aria-hidden="true">
            <rect width="32" height="32" rx="8" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1.2"/>
            <path d="M15.5 6.5C21.5 6.8 24.5 10.5 24.5 16.5C19.2 16.5 16.2 13 15.5 6.5Z" fill="#047857"/>
            <path d="M8.5 16.5C10.5 20.8 14 23.5 18 23.5C22.2 23.5 24.5 20.2 24.5 16.5" stroke="#10B981" stroke-width="2" stroke-linecap="round"/>
            <path d="M9.5 17L13.8 21.2L22.8 10.2" stroke="#047857" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="brand-text">
          <div class="brand-title">
            SIP Rescue
          </div>
          <div class="brand-subtitle">A SIP Continuity Assistant</div>
        </div>
      </div>

      <nav class="nav-links">
        <button class="nav-link ${activeScreen === 'home' ? 'active' : ''}" data-nav="home">Home</button>
        <button class="nav-link ${activeScreen === 'sips' ? 'active' : ''}" data-nav="sips">My SIPs</button>
        <button class="nav-link ${activeScreen === 'navigator' ? 'active' : ''}" data-nav="navigator">Help & Guidance</button>
        <button class="nav-link ${activeScreen === 'comeback' ? 'active' : ''}" data-nav="comeback">Comeback Plan</button>
      </nav>

      <div class="header-actions">
        <div class="demo-dropdown-wrapper">
          <button class="btn-demo-trigger" id="btn-demo-toggle" aria-expanded="false" title="Click to view assessor test scenarios">
            <span>⚡ Try a demo scenario</span>
            <span style="font-size: 10px;">▼</span>
          </button>
          <div class="demo-menu" id="demo-menu">
            <div class="demo-menu-header">Select an Assessor Scenario</div>
            ${DEMO_SCENARIOS.map(s => `
              <button class="demo-scenario-item" data-scenario-id="${s.id}">
                <div class="demo-scenario-title">${s.title}</div>
                <div class="demo-scenario-desc">${s.description}</div>
              </button>
            `).join('')}
          </div>
        </div>
        <div class="demo-badge-pill" title="All mutual fund data shown is for demonstration">
          Demo Mode
        </div>
      </div>
    </div>
  `;

  // Attach event handlers
  const brandHome = header.querySelector("#btn-brand-home");
  brandHome.addEventListener("click", () => onNavigate("home"));

  header.querySelectorAll(".nav-link").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const target = e.currentTarget.getAttribute("data-nav");
      onNavigate(target);
    });
  });

  const demoToggle = header.querySelector("#btn-demo-toggle");
  const demoMenu = header.querySelector("#demo-menu");

  demoToggle.addEventListener("click", (e) => {
    e.stopPropagation();
    const isOpen = demoMenu.classList.toggle("open");
    demoToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });

  // Close demo menu on outside click
  document.addEventListener("click", (e) => {
    if (!demoMenu.contains(e.target) && !demoToggle.contains(e.target)) {
      demoMenu.classList.remove("open");
      demoToggle.setAttribute("aria-expanded", "false");
    }
  });

  header.querySelectorAll(".demo-scenario-item").forEach(item => {
    item.addEventListener("click", (e) => {
      const scenarioId = e.currentTarget.getAttribute("data-scenario-id");
      const scenario = DEMO_SCENARIOS.find(s => s.id === scenarioId);
      demoMenu.classList.remove("open");
      demoToggle.setAttribute("aria-expanded", "false");
      if (scenario && onSelectScenario) {
        onSelectScenario(scenario);
      }
    });
  });

  return header;
}
