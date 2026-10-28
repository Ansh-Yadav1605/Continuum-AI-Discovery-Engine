/**
 * sip-rescue-mvp/js/app.js
 * 
 * Standalone Application Orchestrator & Router
 * 
 * Implements Desktop 3-Area Fintech Dashboard:
 * - A. Left Sidebar: Dark navy navigation, logo, demo scenario picker, demo mode badge
 * - B. Main Workspace: Top search bar ("Search your SIPs or find guidance"), help icon, primary CTA
 * - C. Right-hand Contextual Panel: Upcoming instalments, notice cutoff summary, continuity checklist
 * 
 * Routes:
 * - 'home': Overview Dashboard (Main Feed + Right Context Panel)
 * - 'sips': Dedicated My SIPs Management Screen (Search, Filters, Data Table)
 * - 'sip-detail': Focused SIP Scheme Breakdown & Factual Lifecycle Timeline
 * - 'navigator': Core "Get SIP Help" Guided Wizard (Situation -> Options -> Guidance)
 * - 'plan-ahead': Flow A — Planned Skip, Cash Shortage & Flexible Contribution
 * - 'missed-payment': Flow B — Missed Payment Recovery, Status & Repeat Debit Check
 * - 'flexible-contribution': Voluntary Smaller One-Time Investment in Same Fund
 * - 'comeback': Supportive Comeback Reflection Plan & Calendar Reminder
 * - 'guidance': Knowledge Base, Platform Rules Comparison, & FAQs
 */

import { SAMPLE_SIPS } from "./data/sampleSips.js?v=3";
import { DEMO_SCENARIOS } from "./data/demoScenarios.js?v=3";
import { renderSidebar } from "./components/Sidebar.js?v=3";
import { renderTopNav } from "./components/TopNav.js?v=3";
import { renderContextPanel } from "./components/ContextPanel.js?v=3";
import { renderHomeScreen } from "./components/HomeScreen.js?v=3";
import { renderMySipsScreen } from "./components/MySipsScreen.js?v=3";
import { renderSipDetailScreen } from "./components/SipDetailScreen.js?v=3";
import { renderRescueNavigator } from "./components/RescueNavigator.js?v=3";
import { renderPlanAheadFlow } from "./components/PlanAheadFlow.js?v=3";
import { renderMissedPaymentFlow } from "./components/MissedPaymentFlow.js?v=3";
import { renderFlexibleContributionView } from "./components/FlexibleContributionView.js?v=3";
import { renderComebackPlan } from "./components/ComebackPlan.js?v=3";
import { renderGuidanceScreen } from "./components/GuidanceScreen.js?v=3";
import { renderFeedbackWidget } from "./components/FeedbackModal.js?v=3";

const VALID_ROUTES = [
  "home",
  "sips",
  "sip-detail",
  "navigator",
  "plan-ahead",
  "missed-payment",
  "flexible-contribution",
  "comeback",
  "guidance"
];

class SipRescueApp {
  constructor() {
    this.rootEl = document.getElementById("app-root");
    this.currentScreen = "home";
    this.selectedSip = SAMPLE_SIPS[0];
    this.activeScenario = null;
    this.feedbackOpen = false;
    this.isMobileSidebarOpen = false;
    this.comebackContext = null;

    // Listen to hash changes
    window.addEventListener("hashchange", () => this.handleHashChange());
  }

  init() {
    const hash = window.location.hash.replace("#", "");
    if (VALID_ROUTES.includes(hash)) {
      this.currentScreen = hash;
    } else {
      this.currentScreen = "home";
    }
    this.render();
  }

  handleHashChange() {
    const hash = window.location.hash.replace("#", "");
    if (VALID_ROUTES.includes(hash)) {
      if (this.currentScreen !== hash) {
        this.currentScreen = hash;
        this.render();
      }
    }
  }

  navigateTo(screen, params = {}) {
    this.currentScreen = screen;
    if (params.sip) this.selectedSip = params.sip;
    if (params.scenario) this.activeScenario = params.scenario;
    if (params.resetScenario) this.activeScenario = null;
    if (params.context) this.comebackContext = params.context;

    this.isMobileSidebarOpen = false;
    window.location.hash = screen;
    window.scrollTo({ top: 0, behavior: "smooth" });
    this.render();
  }

  render() {
    this.rootEl.innerHTML = "";

    // App Layout Container (Sidebar + Main Workspace)
    const appLayout = document.createElement("div");
    appLayout.className = "app-layout";

    // 1. Left Sidebar
    const sidebar = renderSidebar({
      activeScreen: this.currentScreen,
      isMobileOpen: this.isMobileSidebarOpen,
      onNavigate: (targetScreen) => {
        if (targetScreen === "guidance") {
          this.navigateTo("guidance");
        } else {
          this.navigateTo(targetScreen, { resetScenario: true });
        }
      },
      onSelectScenario: (scenario) => {
        const matchSip = SAMPLE_SIPS.find(s => s.id === scenario.sipId) || SAMPLE_SIPS[0];
        const targetScreen = scenario.targetScreen || "navigator";
        this.navigateTo(targetScreen, {
          sip: matchSip,
          scenario: scenario
        });
      },
      onToggleMobile: (isOpen) => {
        this.isMobileSidebarOpen = typeof isOpen === "boolean" ? isOpen : !this.isMobileSidebarOpen;
        this.render();
      }
    });
    appLayout.appendChild(sidebar);

    // Sidebar Mobile Backdrop Overlay
    if (this.isMobileSidebarOpen) {
      const backdrop = document.createElement("div");
      backdrop.className = "sidebar-backdrop";
      backdrop.addEventListener("click", () => {
        this.isMobileSidebarOpen = false;
        this.render();
      });
      appLayout.appendChild(backdrop);
    }

    // 2. Main Workspace Container
    const workspace = document.createElement("div");
    workspace.className = "workspace-container";

    // Top Header Navigation Bar
    const topNav = renderTopNav({
      onSearch: (query) => {
        if (query.trim() && this.currentScreen !== "sips") {
          this.navigateTo("sips");
          setTimeout(() => {
            const localInput = document.getElementById("sips-local-search");
            if (localInput) {
              localInput.value = query;
              localInput.dispatchEvent(new Event("input"));
              localInput.focus();
            }
          }, 80);
        }
      },
      onStartRescue: () => {
        this.navigateTo("navigator", { sip: this.selectedSip || SAMPLE_SIPS[0], resetScenario: true });
      },
      onNavigateGuidance: () => {
        this.navigateTo("guidance");
      },
      onToggleMobile: () => {
        this.isMobileSidebarOpen = !this.isMobileSidebarOpen;
        this.render();
      }
    });
    workspace.appendChild(topNav);

    // Workspace Content Area
    const contentArea = document.createElement("div");
    contentArea.className = "workspace-body";

    // Route Switching
    if (this.currentScreen === "home") {
      // 3-Area Overview Layout: Main Feed (Center) + Context Panel (Right)
      const overviewContainer = document.createElement("div");
      overviewContainer.className = "overview-layout-grid";

      // Center Feed
      const homeScreen = renderHomeScreen({
        onSelectSip: (sip) => this.navigateTo("sip-detail", { sip }),
        onStartRescue: (sip) => this.navigateTo("navigator", { sip, resetScenario: true }),
        onNavigateExplore: () => this.navigateTo("navigator", { sip: SAMPLE_SIPS[0], resetScenario: true }),
        onPlanAhead: (sip) => this.navigateTo("plan-ahead", { sip, resetScenario: true }),
        onMissedPayment: (sip) => this.navigateTo("missed-payment", { sip, resetScenario: true }),
        onFlexibleContribution: (sip) => this.navigateTo("flexible-contribution", { sip, resetScenario: true })
      });
      overviewContainer.appendChild(homeScreen);

      // Right-Hand Contextual Panel
      const contextPanel = renderContextPanel({
        onSelectSip: (sip) => this.navigateTo("sip-detail", { sip }),
        onStartRescue: (sip) => this.navigateTo("navigator", { sip, resetScenario: true })
      });
      overviewContainer.appendChild(contextPanel);

      contentArea.appendChild(overviewContainer);

    } else if (this.currentScreen === "sips") {
      // Dedicated My SIPs Screen
      const mySips = renderMySipsScreen({
        onSelectSip: (sip) => this.navigateTo("sip-detail", { sip }),
        onStartRescue: (sip) => this.navigateTo("navigator", { sip, resetScenario: true })
      });
      contentArea.appendChild(mySips);

    } else if (this.currentScreen === "sip-detail") {
      // Focused SIP Detail Screen
      const detailScreen = renderSipDetailScreen({
        sip: this.selectedSip,
        onBack: () => this.navigateTo("sips"),
        onStartRescue: (sip) => this.navigateTo("navigator", { sip, resetScenario: true }),
        onViewRules: (sip) => this.navigateTo("guidance"),
        onPlanAhead: (sip) => this.navigateTo("plan-ahead", { sip, resetScenario: true }),
        onMissedPayment: (sip) => this.navigateTo("missed-payment", { sip, resetScenario: true }),
        onFlexibleContribution: (sip) => this.navigateTo("flexible-contribution", { sip, resetScenario: true })
      });
      contentArea.appendChild(detailScreen);

    } else if (this.currentScreen === "plan-ahead") {
      // Flow A: Plan Ahead Flow
      const planAheadScreen = renderPlanAheadFlow({
        sip: this.selectedSip,
        initialScenario: this.activeScenario,
        onNavigateHome: () => this.navigateTo("home"),
        onViewSipDetails: (sip) => this.navigateTo("sip-detail", { sip }),
        onStartFlexibleContribution: (sip) => this.navigateTo("flexible-contribution", { sip }),
        onSwitchSip: (newSip) => {
          this.selectedSip = newSip;
          this.render();
        }
      });
      contentArea.appendChild(planAheadScreen);

    } else if (this.currentScreen === "missed-payment") {
      // Flow B: Missed Payment Rescue Flow
      const missedScreen = renderMissedPaymentFlow({
        sip: this.selectedSip,
        initialScenario: this.activeScenario,
        onNavigateHome: () => this.navigateTo("home"),
        onViewSipDetails: (sip) => this.navigateTo("sip-detail", { sip }),
        onSwitchSip: (newSip) => {
          this.selectedSip = newSip;
          this.render();
        },
        onNavigateComeback: (ctx) => this.navigateTo("comeback", { context: ctx })
      });
      contentArea.appendChild(missedScreen);

    } else if (this.currentScreen === "flexible-contribution") {
      // Flexible Contribution Dedicated Screen
      const flexScreen = renderFlexibleContributionView({
        sip: this.selectedSip,
        initialAmount: this.activeScenario?.voluntaryAmount || 1000,
        onNavigateHome: () => this.navigateTo("home"),
        onViewSipDetails: (sip) => this.navigateTo("sip-detail", { sip }),
        onSwitchSip: (newSip) => {
          this.selectedSip = newSip;
          this.render();
        }
      });
      contentArea.appendChild(flexScreen);

    } else if (this.currentScreen === "navigator") {
      // Get SIP Help Core Wizard
      const navScreen = renderRescueNavigator({
        initialSip: this.selectedSip,
        initialScenario: this.activeScenario,
        onNavigateHome: () => this.navigateTo("home"),
        onNavigateComeback: (ctx) => this.navigateTo("comeback", { context: ctx }),
        onPlanAhead: (sip) => this.navigateTo("plan-ahead", { sip, resetScenario: true }),
        onMissedPayment: (sip) => this.navigateTo("missed-payment", { sip, resetScenario: true }),
        onOpenFeedback: (sit) => {
          this.feedbackOpen = true;
          this.render();
        }
      });
      contentArea.appendChild(navScreen);

      if (this.feedbackOpen) {
        const fb = renderFeedbackWidget({
          situation: this.activeScenario ? this.activeScenario.title : "Guided Recovery",
          onClose: () => {
            this.feedbackOpen = false;
            this.render();
          }
        });
        contentArea.appendChild(fb);
      }

    } else if (this.currentScreen === "comeback") {
      // Supportive Comeback Plan Screen
      const comebackScreen = renderComebackPlan({
        contextData: this.comebackContext || { sip: this.selectedSip },
        onNavigateHome: () => this.navigateTo("home")
      });
      contentArea.appendChild(comebackScreen);

    } else if (this.currentScreen === "guidance") {
      // Help & Guidance Knowledge Base Screen
      const guidanceScreen = renderGuidanceScreen({
        onStartRescue: () => this.navigateTo("navigator", { sip: this.selectedSip || SAMPLE_SIPS[0], resetScenario: true }),
        onPlanAhead: () => this.navigateTo("plan-ahead", { sip: this.selectedSip || SAMPLE_SIPS[0], resetScenario: true }),
        onMissedPayment: () => this.navigateTo("missed-payment", { sip: this.selectedSip || SAMPLE_SIPS[0], resetScenario: true }),
        onFlexibleContribution: () => this.navigateTo("flexible-contribution", { sip: this.selectedSip || SAMPLE_SIPS[0], resetScenario: true })
      });
      contentArea.appendChild(guidanceScreen);
    }

    workspace.appendChild(contentArea);

    // Workspace Footer
    const footer = document.createElement("footer");
    footer.className = "workspace-footer";
    footer.innerHTML = `
      <div class="footer-inner">
        <div>
          <strong>SIP Rescue — A SIP Continuity Assistant</strong> &nbsp;|&nbsp; Fintech Product Prototype
        </div>
        <div>
          Built with verified platform rules (Groww, Zerodha Coin, AMC Direct). No bank access or transactional execution.
        </div>
        <div style="font-size: 11px; color: var(--text-dim); margin-top: 4px;">
          Disclaimer: Mutual fund investments are subject to market risks. Read all scheme related documents carefully.
        </div>
      </div>
    `;
    workspace.appendChild(footer);

    appLayout.appendChild(workspace);
    this.rootEl.appendChild(appLayout);
  }
}

// Launch application
document.addEventListener("DOMContentLoaded", () => {
  const app = new SipRescueApp();
  app.init();
});
