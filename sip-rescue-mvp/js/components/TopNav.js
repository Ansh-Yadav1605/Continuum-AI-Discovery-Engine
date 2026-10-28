/**
 * sip-rescue-mvp/js/components/TopNav.js
 * 
 * Top Header bar for main workspace:
 * - Search bar ("Search your SIPs or find guidance")
 * - Help shortcut icon
 * - Primary CTA: "Get SIP Help"
 * - Mobile sidebar toggle
 */

export function renderTopNav({ onSearch, onStartRescue, onNavigateGuidance, onToggleMobile }) {
  const topNav = document.createElement("div");
  topNav.className = "workspace-top-bar";

  topNav.innerHTML = `
    <div class="top-bar-left">
      <button class="btn-sidebar-toggle" id="btn-toggle-sidebar" aria-label="Toggle navigation menu">
        <span>☰</span>
      </button>

      <div class="workspace-search-wrapper">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          id="top-search-input" 
          class="workspace-search-input" 
          placeholder="Search your SIPs or find guidance..." 
          aria-label="Search your SIPs or find guidance"
        />
      </div>
    </div>

    <div class="top-bar-right">
      <button class="top-bar-icon-btn" id="btn-top-help" title="Help & Guidance documentation">
        <span>❓</span>
        <span class="top-bar-icon-label">Help</span>
      </button>

      <div class="top-bar-divider"></div>

      <button class="btn btn-primary top-cta-btn" id="btn-top-get-help" title="Start guided SIP continuity rescue">
        <span style="font-size: 14px;">🆘</span>
        <span>Get SIP Help</span>
      </button>
    </div>
  `;

  // Attach handlers
  const toggleBtn = topNav.querySelector("#btn-toggle-sidebar");
  if (toggleBtn && onToggleMobile) {
    toggleBtn.addEventListener("click", () => onToggleMobile());
  }

  const searchInput = topNav.querySelector("#top-search-input");
  if (searchInput && onSearch) {
    searchInput.addEventListener("input", (e) => {
      onSearch(e.target.value);
    });
  }

  const btnHelp = topNav.querySelector("#btn-top-help");
  if (btnHelp && onNavigateGuidance) {
    btnHelp.addEventListener("click", () => onNavigateGuidance());
  }

  const btnGetHelp = topNav.querySelector("#btn-top-get-help");
  if (btnGetHelp && onStartRescue) {
    btnGetHelp.addEventListener("click", () => onStartRescue());
  }

  return topNav;
}
