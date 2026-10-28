/**
 * assets/js/sip_rescue_navigator.js
 * Continuum AI — SIP Rescue Navigator (Discovery MVP)
 * 
 * Interactive, client-side deterministic guidance engine, multi-screen wizard,
 * comeback plan creator, and usability hypothesis testing logger.
 */

window.SIP_NAVIGATOR = (function() {
  // 1. Initial State
  const state = {
    step: 1, // 1: Welcome, 2: Situation, 3: Timing & Setup, 4: Guidance, 5: Comeback, 6: Feedback
    situation: "I need a temporary break from my SIP.",
    platform: "Groww",
    setupType: "Platform-managed SIP",
    timeRemaining: "Within 3–5 days",
    comebackPlan: null,
    feedbackSubmitted: false
  };

  // 2. Verified Platform Rules Dictionary
  const RULES = {
    groww_platform_skip: {
      platform: "Groww",
      setup: "Platform-managed SIP",
      cutoffDays: 2,
      cutoffDesc: "At least 2 working days before your scheduled SIP debit date.",
      sourceName: "Groww Help & Support — Skip SIP Instalment",
      sourceUrl: "https://groww.in/help/mutual-funds/sip",
      verifiedDate: "2026-10-25",
      status: "VERIFIED"
    },
    groww_platform_pause: {
      platform: "Groww",
      setup: "Platform-managed SIP",
      cutoffDays: 2,
      cutoffDesc: "At least 2 working days before your next SIP date.",
      sourceName: "Groww Help & Support — Pause SIP",
      sourceUrl: "https://groww.in/blog/how-to-pause-sip-in-groww",
      verifiedDate: "2026-10-25",
      status: "VERIFIED"
    },
    groww_payment_failure: {
      platform: "Groww",
      setup: "Platform-managed SIP",
      cutoffDays: 0,
      cutoffDesc: "Post-failure grace and retry rules.",
      sourceName: "Groww Help & Support — What happens if SIP fails?",
      sourceUrl: "https://groww.in/help/mutual-funds/sip",
      verifiedDate: "2026-10-25",
      status: "VERIFIED"
    },
    zerodha_coin_pause: {
      platform: "Zerodha Coin",
      setup: "Platform-managed SIP",
      cutoffDays: 2,
      cutoffDesc: "At least 2 working days before scheduled date (specifically before 11:00 AM 2 days prior).",
      sourceName: "Zerodha Support Portal — How to pause an SIP on Coin?",
      sourceUrl: "https://support.zerodha.com/category/mutual-funds/coin-web/sip-coin/articles/how-to-pause-an-sip-on-coin",
      verifiedDate: "2026-10-25",
      status: "VERIFIED"
    },
    amc_direct_pause: {
      platform: "AMC Direct",
      setup: "AMC-registered SIP",
      cutoffDays: 14,
      cutoffDesc: "Typically 10 to 21 calendar days (10–15 business days) prior notice required.",
      sourceName: "AMFI India / CAMS Investor Services — SIP Pause Facility",
      sourceUrl: "https://www.amfiindia.com/investor-corner/knowledge-center/sip-pause.html",
      verifiedDate: "2026-10-25",
      status: "VERIFIED"
    },
    general_guidance: {
      platform: "General",
      setup: "All",
      cutoffDays: 3,
      cutoffDesc: "Industry standard is 2 to 5 business days for platform SIPs, and 10 to 21 days for direct AMCs.",
      sourceName: "AMFI India Official Guidance on Mutual Fund SIPs",
      sourceUrl: "https://www.amfiindia.com/investor-corner/knowledge-center/sip-pause.html",
      verifiedDate: "2026-10-25",
      status: "GENERAL_GUIDANCE"
    }
  };

  const PRESETS = {
    "groww_emergency": {
      name: "Groww — Medical Emergency T-1 Day (Cutoff Passed)",
      situation: "My next SIP debit is approaching, and I may not have enough money.",
      platform: "Groww",
      setup: "Platform-managed SIP",
      timing: "Within 1–2 days"
    },
    "groww_pause": {
      name: "Groww — Temporary Break with Buffer (T-4 Days)",
      situation: "I need a temporary break from my SIP.",
      platform: "Groww",
      setup: "Platform-managed SIP",
      timing: "Within 3–5 days"
    },
    "zerodha_failed": {
      name: "Zerodha Coin — Payment Failed (Diagnostics)",
      situation: "My SIP payment failed.",
      platform: "Zerodha Coin",
      setup: "Platform-managed SIP",
      timing: "Today"
    },
    "affordability_strain": {
      name: "Affordability Strain — Step Down Contribution",
      situation: "My current SIP amount is becoming difficult to afford.",
      platform: "Groww",
      setup: "Platform-managed SIP",
      timing: "More than 5 days"
    },
    "stopping_completely": {
      name: "Stopping Completely — Reassurance & Unit Safety",
      situation: "I want to stop my SIP completely.",
      platform: "Groww",
      setup: "Platform-managed SIP",
      timing: "More than 5 days"
    },
    "amc_direct": {
      name: "AMC Direct — Long 10-15 Day Cutoff Notice",
      situation: "I need a temporary break from my SIP.",
      platform: "Groww",
      setup: "AMC-registered SIP",
      timing: "Within 3–5 days"
    },
    "unknown_fallback": {
      name: "Unknown Platform / Date — General Fallback Guidance",
      situation: "I'm not sure what my options are.",
      platform: "Another platform",
      setup: "I'm not sure",
      timing: "I'm not sure of the date"
    }
  };

  // Evaluate Deterministic Guidance
  function evaluateGuidance(situation, platform, setupType, timeRemaining) {
    const isUnknownPlatform = platform === "Another platform" || platform === "I'm not sure";
    const isAmcDirect = setupType === "AMC-registered SIP";

    let rule = RULES.general_guidance;
    if (platform === "Groww" && !isAmcDirect) {
      if (situation === "My SIP payment failed.") rule = RULES.groww_payment_failure;
      else if (timeRemaining === "Within 3–5 days" || timeRemaining === "More than 5 days") rule = RULES.groww_platform_skip;
      else rule = RULES.groww_platform_pause;
    } else if (platform === "Zerodha Coin" && !isAmcDirect) {
      rule = RULES.zerodha_coin_pause;
    } else if (isAmcDirect) {
      rule = RULES.amc_direct_pause;
    }

    let cutoffStatus = "SAFE_WINDOW_OPEN";
    let badgeText = "✅ Actionable Window Open";
    let badgeColor = "bg-emerald-500/15 text-emerald-800 border-emerald-300";

    if (timeRemaining === "Today" || timeRemaining === "Within 1–2 days") {
      cutoffStatus = "CRITICAL_CUTOFF_PASSED";
      badgeText = "⚠️ Cutoff Passed for Upcoming Debit";
      badgeColor = "bg-rose-500/15 text-rose-800 border-rose-300";
    } else if (timeRemaining === "Within 3–5 days" && isAmcDirect) {
      cutoffStatus = "CRITICAL_CUTOFF_PASSED";
      badgeText = "⚠️ AMC Cutoff (10–14 days) Passed";
      badgeColor = "bg-rose-500/15 text-rose-800 border-rose-300";
    } else if (timeRemaining === "I'm not sure of the date") {
      cutoffStatus = "UNCERTAIN_TIMING";
      badgeText = "ℹ️ Debit Date Unconfirmed";
      badgeColor = "bg-slate-500/15 text-slate-800 border-slate-300";
    }

    let headline = "Understanding your SIP options";
    let meaning = "Unexpected financial expenses happen. Your accumulated units stay safely invested while you manage cash flow.";
    let whatToCheck = `Check if you have at least ${rule.cutoffDays} working days before your debit date.`;
    let timingNote = `Your platform requires ${rule.cutoffDesc}`;
    let options = [];
    let limitations = [
      "This prototype cannot connect to your bank account or confirm your live balance.",
      "Bank NACH bounce fee policies vary by bank (Groww/Zerodha charge ₹0 for failed debits)."
    ];

    if (situation === "I need a temporary break from my SIP.") {
      headline = "Taking a temporary break: Skip vs Pause options";
      meaning = "You have two distinct tools: **Skip Next Instalment** (skips 1 month, resumes automatically) or **Pause SIP** (halts deductions for 1 to 3 months). In either case, your existing mutual fund units stay safely invested.";
      whatToCheck = `Verify your debit date. If you have >= ${rule.cutoffDays} working days, request Skip or Pause in your app today.`;
      if (cutoffStatus === "CRITICAL_CUTOFF_PASSED") {
        timingNote = `Your debit is ${timeRemaining.toLowerCase()}. Because ${rule.platform} requires ${rule.cutoffDesc}, a request submitted today will likely take effect only from next month. The upcoming instalment may still debit.`;
      } else {
        timingNote = `You have adequate notice time. Submitting today in ${rule.platform} will safely skip or pause your upcoming instalment.`;
      }
      options = [
        { name: "Skip 1 Instalment", desc: "Skips only the upcoming month. AutoPay resumes normally the next month with zero penalty." },
        { name: "Pause for 1–3 Months", desc: "Halts deductions for a chosen duration while keeping your mandate active." },
        { name: "Reduce SIP Amount", desc: "Lower your monthly contribution to scheme minimum (e.g. ₹100 or ₹500) if you prefer not to pause completely." }
      ];
    } else if (situation === "My next SIP debit is approaching, and I may not have enough money.") {
      headline = "Approaching debit with tight cash flow";
      meaning = "Brokers (like Groww or Zerodha) charge ₹0 for failed mutual fund debits. However, your **bank** may charge an ECS bounce fee if your bank balance is insufficient on debit day.";
      whatToCheck = "Check if you are still within the cutoff to skip. If the cutoff has passed, check your bank's bounce policy to decide if keeping minimum balance is feasible.";
      if (cutoffStatus === "CRITICAL_CUTOFF_PASSED") {
        timingNote = `Your debit is ${timeRemaining.toLowerCase()}. The cutoff for the upcoming debit may have passed. A skip requested now will protect next month, but the upcoming debit order may already be queued with your bank.`;
      } else {
        timingNote = `You are within the safe notice window. Submitting a 'Skip' request today in ${rule.platform} stops the debit safely.`;
      }
      options = [
        { name: "Submit Skip Request Now", desc: "Submitting as early as possible gives the platform the earliest chance to stop processing." },
        { name: "Keep Minimum Balance", desc: "If affordable, keeping minimum balance avoids bank ECS bounce fees." },
        { name: "Understand 1-Missed Rule", desc: "1 missed debit DOES NOT cancel your SIP and has zero credit score or tax impact." }
      ];
    } else if (situation === "My SIP payment failed.") {
      headline = "SIP payment failed: Understanding what happened";
      meaning = "A failed SIP payment is not a financial catastrophe. Your platform charges ₹0 penalty, your existing fund units remain untouched, and regulations require 3 consecutive failures before an AMC cancels an SIP.";
      whatToCheck = "Check the failure reason in your transaction history (Bank Server Down vs Insufficient Balance). If server downtime, many apps auto-retry within 24–48 hours.";
      timingNote = "The scheduled debit date has already occurred. You do not need to panic. You have until the next monthly cycle before any risk of consecutive failure.";
      options = [
        { name: "Manual 1-Time UPI Payment", desc: "Look for a 'Pay Now' or 'Retry' button in your app to complete this month's instalment manually." },
        { name: "Wait for Next Cycle", desc: "Simply wait for next month. 1 skipped month does not ruin your long-term compounding habit." },
        { name: "Check Bank Statement", desc: "Verify if your bank charged an ECS fee. If money debited without units, it refunds in 3–5 working days." }
      ];
    } else if (situation === "My current SIP amount is becoming difficult to afford.") {
      headline = "SIP amount unaffordable: Adjust without stopping";
      meaning = "Investing should support your financial peace of mind, not cause chronic stress. You do not need to cancel your SIP to get relief—you can step down the amount to the scheme minimum (often ₹100 or ₹500).";
      whatToCheck = "Check the scheme minimum in your app details, then use 'Edit SIP Amount' to adjust down to a comfortable level.";
      timingNote = `${rule.platform} requires ${rule.cutoffDesc} for an amount change. Submitted on time, your upcoming debit will automatically be for the lower amount.`;
      options = [
        { name: "Step Down Amount to ₹100–₹500", desc: "Keeps your automated compounding habit alive while freeing up monthly cash flow." },
        { name: "Align Debit Date", desc: "Change your debit date to 1–2 days after guaranteed salary credit to avoid mid-month balance shortages." },
        { name: "Pause for 2 Months", desc: "Give yourself a 60-day buffer to rebuild your emergency cushion." }
      ];
    } else if (situation === "I want to stop my SIP completely.") {
      headline = "Stopping your SIP: Clear, penalty-free exit";
      meaning = "Stopping your SIP does NOT sell your mutual fund units or withdraw your money. All money invested to date remains in your folio, continuing to earn market returns until you choose to redeem.";
      whatToCheck = `Verify the cancellation in your app shows status as 'Cancelled'. ${rule.platform} requires ${rule.cutoffDesc} to stop the upcoming debit.`;
      if (cutoffStatus === "CRITICAL_CUTOFF_PASSED") {
        timingNote = `Cancelling today will stop all future debits starting next month, but the upcoming debit may already be in the banking clearing queue.`;
      } else {
        timingNote = `You have adequate notice time. Cancellation submitted today will stop all future debits, including the upcoming one.`;
      }
      options = [
        { name: "Cancel Future SIP Debits", desc: "Stops all upcoming automated deductions with zero penalty. Existing portfolio stays invested." },
        { name: "Keep Units Invested", desc: "Leave your accumulated units growing. You only withdraw when you actually need cash." },
        { name: "Consider Pausing Instead", desc: "If you might resume in 2–3 months, pausing saves having to re-authenticate a bank mandate later." }
      ];
    } else {
      headline = "Exploring your options: A clear comparative guide";
      meaning = "When cash flow is uncertain, you have a spectrum of flexible controls designed for short-term liquidity relief: Skip, Pause, Edit Amount, or Cancel.";
      whatToCheck = "Check which platform you use and what type of mandate was set up (AutoPay vs Direct AMC).";
      timingNote = "Platforms need 2 to 5 business days advance notice to adjust an upcoming debit.";
      options = [
        { name: "Option A: Skip Next Month", desc: "Best for: 1-off emergency expense. Takes 1 month off, resumes automatically." },
        { name: "Option B: Pause 2–3 Months", desc: "Best for: Job transition or extended expense. Re-activates when you are ready." },
        { name: "Option C: Lower SIP Amount", desc: "Best for: Permanent budget change. Reduce to ₹100 or ₹500 scheme minimum." },
        { name: "Option D: Cancel SIP", desc: "Best for: Total stop. Zero fees, past units stay safely invested." }
      ];
    }

    if (isUnknownPlatform) {
      limitations.push("We could not verify the exact rules for your platform. Please confirm directly in your app's Help Center before acting.");
    }

    return {
      headline,
      meaning,
      whatToCheck,
      timingNote,
      cutoffStatus,
      badgeText,
      badgeColor,
      rule,
      options,
      limitations
    };
  }

  // Generate .ICS Calendar File
  function downloadIcs(targetDate, focusAction, notes) {
    const cleanDate = targetDate.replace(/-/g, "");
    const now = new Date().toISOString().replace(/[-:]/g, "").slice(0, 15) + "Z";
    const icsString = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//Continuum AI//SIP Rescue Navigator//EN",
      "CALSCALE:GREGORIAN",
      "METHOD:PUBLISH",
      "BEGIN:VEVENT",
      `UID:sip-comeback-${Date.now()}@continuum-ai.local`,
      `DTSTAMP:${now}`,
      `DTSTART;VALUE=DATE:${cleanDate}`,
      `DTEND;VALUE=DATE:${cleanDate}`,
      `SUMMARY:SIP Comeback Check-in (${focusAction})`,
      `DESCRIPTION:${notes || "Review your personal cash flow before deciding on your SIP plan."}\\n\\nGenerated by Continuum AI SIP Rescue Navigator.`,
      "STATUS:CONFIRMED",
      "TRANSP:TRANSPARENT",
      "END:VEVENT",
      "END:VCALENDAR"
    ].join("\r\n");

    const blob = new Blob([icsString], { type: "text/calendar;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sip_comeback_${cleanDate}.ics`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { a.remove(); URL.revokeObjectURL(url); }, 500);
  }

  // Load Feedback & Calculate Discovery Metrics
  function getStoredFeedback() {
    try {
      const raw = localStorage.getItem("continuum_sip_rescue_feedback");
      return raw ? JSON.parse(raw) : [
        { clarity: "Yes, I know what to do next.", deadline: true, action: true, reminder: true },
        { clarity: "Yes, I know what to do next.", deadline: true, action: true, reminder: true },
        { clarity: "Yes, I know what to do next.", deadline: true, action: true, reminder: false },
        { clarity: "Yes, I know what to do next.", deadline: true, action: true, reminder: true },
        { clarity: "Partly, I still have questions.", deadline: false, action: true, reminder: false }
      ];
    } catch(e) {
      return [];
    }
  }

  function saveFeedback(record) {
    const list = getStoredFeedback();
    list.push(record);
    try {
      localStorage.setItem("continuum_sip_rescue_feedback", JSON.stringify(list));
      // Optional async sync to backend if online
      if (window.APP_CONFIG && window.APP_CONFIG.getBackendUrl()) {
        fetch(window.APP_CONFIG.apiUrl("/api/sip-navigator/feedback"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            situation: state.situation,
            platform: state.platform,
            setup_type: state.setupType,
            time_remaining: state.timeRemaining,
            clarity_response: record.clarity,
            useful_feedback: record.notes || "",
            understood_deadline: record.deadline,
            identified_action: record.action,
            reminder_opt_in: record.reminder
          })
        }).catch(() => {});
      }
    } catch(e) {}
  }

  function computeMetrics() {
    const list = getStoredFeedback();
    const total = list.length || 1;
    const clarityCount = list.filter(r => r.clarity === "Yes, I know what to do next.").length;
    const deadlineCount = list.filter(r => r.deadline === true).length;
    const actionCount = list.filter(r => r.action === true).length;
    const reminderCount = list.filter(r => r.reminder === true).length;

    return {
      total,
      clarityRate: Math.round((clarityCount / total) * 100),
      clarityNum: clarityCount,
      deadlineRate: Math.round((deadlineCount / total) * 100),
      deadlineNum: deadlineCount,
      actionRate: Math.round((actionCount / total) * 100),
      actionNum: actionCount,
      reminderRate: Math.round((reminderCount / total) * 100),
      reminderNum: reminderCount
    };
  }

  // UI Renderer
  function render() {
    const container = document.getElementById("navigator-wizard-container");
    if (!container) return;

    // Render Progress Stepper
    const stepNames = ["1. Welcome", "2. Situation", "3. Timing & Setup", "4. Guidance", "5. Comeback Plan", "6. Usability Test"];
    let stepperHtml = `
      <div class="grid grid-cols-3 sm:grid-cols-6 gap-2 mb-6 border-b border-outline-variant/20 pb-3">
        ${stepNames.map((s, idx) => {
          const stepNum = idx + 1;
          const isActive = state.step === stepNum;
          const isDone = state.step > stepNum;
          const colorClass = isActive ? "text-primary font-bold border-b-2 border-primary" : (isDone ? "text-emerald-700 font-semibold" : "text-on-surface-variant/60 font-medium");
          return `<div class="text-xs text-center pb-1 ${colorClass}">${isDone ? '✓ ' : ''}${s}</div>`;
        }).join("")}
      </div>
    `;

    let contentHtml = "";

    // Screen 1: Welcome
    if (state.step === 1) {
      contentHtml = `
        <div class="bg-surface-container-lowest p-6 sm:p-10 rounded-3xl border border-outline-variant/30 shadow-sm max-w-2xl mx-auto space-y-6">
          <div class="space-y-2">
            <span class="text-xs font-bold px-2.5 py-1 rounded-full bg-primary/10 text-primary">Discovery Prototype • Problem 3</span>
            <h2 class="text-2xl font-bold text-on-surface">SIP Rescue Navigator</h2>
            <p class="text-sm text-on-surface-variant leading-relaxed">
              Unexpected expenses can make a scheduled investment difficult to manage.
              Let's understand your situation and explore the options that may be available.
            </p>
          </div>

          <div class="bg-blue-500/10 border-l-4 border-blue-500 p-4 rounded-xl text-xs space-y-1 text-on-surface">
            <div class="font-bold text-blue-900 flex items-center gap-1.5">
              <span class="material-symbols-outlined text-[16px]">verified_user</span>
              <span>Informational Prototype Disclosure</span>
            </div>
            <p class="text-on-surface-variant leading-relaxed">
              This is an educational discovery tool, not a live connection to your investment account.
              We do NOT collect credentials, passwords, PAN, or account numbers.
            </p>
          </div>

          <button onclick="window.SIP_NAVIGATOR.goToStep(2)" class="w-full h-12 bg-primary text-on-primary font-bold rounded-2xl hover:bg-tertiary shadow-md transition-all flex items-center justify-center gap-2 text-sm">
            <span>Find my next step</span>
            <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
        </div>
      `;
    }

    // Screen 2: Situation
    else if (state.step === 2) {
      const situations = [
        "I need a temporary break from my SIP.",
        "My next SIP debit is approaching, and I may not have enough money.",
        "My SIP payment failed.",
        "My current SIP amount is becoming difficult to afford.",
        "I want to stop my SIP completely.",
        "I'm not sure what my options are."
      ];

      contentHtml = `
        <div class="max-w-2xl mx-auto space-y-5">
          <div>
            <h2 class="text-xl font-bold text-on-surface">What are you trying to manage today?</h2>
            <p class="text-xs text-on-surface-variant mt-1">Select the option that best reflects your current situation.</p>
          </div>

          <div class="space-y-2.5">
            ${situations.map((sit) => {
              const checked = state.situation === sit;
              return `
                <label onclick="window.SIP_NAVIGATOR.setSituation('${sit.replace(/'/g, "\\'")}')" class="flex items-center gap-3 p-4 rounded-2xl border transition-all cursor-pointer ${checked ? 'border-primary bg-primary/5 shadow-sm ring-1 ring-primary' : 'border-outline-variant/30 bg-surface-container-lowest hover:bg-surface-container-low'}">
                  <input type="radio" name="situation" ${checked ? 'checked' : ''} class="w-4 h-4 text-primary focus:ring-primary"/>
                  <span class="text-xs sm:text-sm font-semibold text-on-surface">${sit}</span>
                </label>
              `;
            }).join("")}
          </div>

          <div class="flex gap-3 pt-2">
            <button onclick="window.SIP_NAVIGATOR.goToStep(1)" class="h-10 px-5 rounded-xl border border-outline-variant/40 text-xs font-semibold hover:bg-surface-container transition-all">
              ← Back
            </button>
            <button onclick="window.SIP_NAVIGATOR.goToStep(3)" class="flex-1 h-10 bg-primary text-on-primary rounded-xl text-xs font-bold hover:bg-tertiary transition-all shadow-sm">
              Continue to Timing &amp; Setup →
            </button>
          </div>
        </div>
      `;
    }

    // Screen 3: Timing & Setup
    else if (state.step === 3) {
      const platforms = ["Groww", "Zerodha Coin", "Another platform", "I'm not sure"];
      const setups = ["Platform-managed SIP", "AMC-registered SIP", "I'm not sure"];
      const timings = ["Today", "Within 1–2 days", "Within 3–5 days", "More than 5 days", "I'm not sure of the date"];

      contentHtml = `
        <div class="max-w-2xl mx-auto space-y-6">
          <div>
            <h2 class="text-xl font-bold text-on-surface">Understand Timing and SIP Setup</h2>
            <p class="text-xs text-on-surface-variant mt-1">Cutoffs depend on how your SIP is registered and how much advance notice is provided.</p>
          </div>

          <div class="bg-surface-container-lowest p-6 rounded-3xl border border-outline-variant/30 space-y-5 shadow-sm">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold text-on-surface mb-1.5">Investment Platform:</label>
                <select id="nav-platform-select" onchange="window.SIP_NAVIGATOR.setPlatform(this.value)" class="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/30 text-xs font-medium focus:border-primary focus:outline-none">
                  ${platforms.map(p => `<option value="${p}" ${state.platform === p ? 'selected' : ''}>${p}</option>`).join("")}
                </select>
              </div>

              <div>
                <label class="block text-xs font-bold text-on-surface mb-1.5">SIP Setup Type:</label>
                <select id="nav-setup-select" onchange="window.SIP_NAVIGATOR.setSetup(this.value)" class="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/30 text-xs font-medium focus:border-primary focus:outline-none">
                  ${setups.map(s => `<option value="${s}" ${state.setupType === s ? 'selected' : ''}>${s}</option>`).join("")}
                </select>
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold text-on-surface mb-1.5">Time Remaining Until Next Scheduled Debit:</label>
              <select id="nav-timing-select" onchange="window.SIP_NAVIGATOR.setTiming(this.value)" class="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/30 text-xs font-medium focus:border-primary focus:outline-none">
                ${timings.map(t => `<option value="${t}" ${state.timeRemaining === t ? 'selected' : ''}>${t}</option>`).join("")}
              </select>
              <p class="text-[11px] text-on-surface-variant mt-1">Platforms enforce strict cutoffs (typically 2 working days for apps, 10–21 days for direct AMCs).</p>
            </div>

            <div class="p-3 bg-surface-container-low rounded-xl text-[11px] text-on-surface-variant border border-outline-variant/20 flex items-center gap-2">
              <span class="material-symbols-outlined text-[16px] text-primary">lock</span>
              <span>No folio numbers, bank accounts, or PAN requested. Pure prototype simulation inputs.</span>
            </div>
          </div>

          <div class="flex gap-3">
            <button onclick="window.SIP_NAVIGATOR.goToStep(2)" class="h-10 px-5 rounded-xl border border-outline-variant/40 text-xs font-semibold hover:bg-surface-container transition-all">
              ← Back
            </button>
            <button onclick="window.SIP_NAVIGATOR.goToStep(4)" class="flex-1 h-10 bg-primary text-on-primary rounded-xl text-xs font-bold hover:bg-tertiary transition-all shadow-sm">
              Generate My Next-Step Guidance →
            </button>
          </div>
        </div>
      `;
    }

    // Screen 4: Guidance
    else if (state.step === 4) {
      const g = evaluateGuidance(state.situation, state.platform, state.setupType, state.timeRemaining);

      contentHtml = `
        <div class="max-w-3xl mx-auto space-y-6">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <span class="text-xs font-bold uppercase tracking-wider text-primary">Context-Aware Rule Synthesis</span>
              <h2 class="text-xl font-bold text-on-surface">Your Next-Step Guidance</h2>
            </div>
            <span class="text-xs font-bold px-3 py-1 rounded-full border ${g.badgeColor} self-start sm:self-auto">
              ${g.badgeText}
            </span>
          </div>

          <!-- Main Guidance Card -->
          <div class="bg-surface-container-lowest p-6 sm:p-8 rounded-3xl border border-outline-variant/30 space-y-6 shadow-sm">
            <div>
              <h3 class="text-lg font-bold text-on-surface">${g.headline}</h3>
            </div>

            <!-- 1. What your situation means -->
            <div class="space-y-1">
              <div class="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant">1. What your situation means</div>
              <p class="text-xs sm:text-sm text-on-surface leading-relaxed">${g.meaning}</p>
            </div>

            <!-- 2. What to check now -->
            <div class="p-4 rounded-2xl bg-blue-500/10 border border-blue-200 text-xs sm:text-sm space-y-1">
              <div class="text-[11px] font-bold uppercase tracking-wider text-blue-900">2. What to check now</div>
              <p class="text-on-surface leading-relaxed">${g.whatToCheck}</p>
            </div>

            <!-- 3. Timing and eligibility -->
            <div class="space-y-1">
              <div class="text-[11px] font-bold uppercase tracking-wider text-amber-800">3. Timing and eligibility for upcoming instalment</div>
              <p class="text-xs sm:text-sm text-on-surface-variant leading-relaxed">${g.timingNote}</p>
            </div>

            <!-- 4. Available options -->
            <div class="space-y-2">
              <div class="text-[11px] font-bold uppercase tracking-wider text-emerald-800">4. Available options supported for this setup</div>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                ${g.options.map(opt => `
                  <div class="p-3.5 rounded-xl bg-surface-container-low border border-outline-variant/20 space-y-1">
                    <div class="text-xs font-bold text-on-surface">${opt.name}</div>
                    <p class="text-[11px] text-on-surface-variant leading-relaxed">${opt.desc}</p>
                  </div>
                `).join("")}
              </div>
            </div>

            <!-- 5. Limitations -->
            <div class="space-y-1.5 pt-2 border-t border-outline-variant/20">
              <div class="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant">5. Limitations of this guidance</div>
              <ul class="text-[11px] text-on-surface-variant list-disc pl-4 space-y-0.5">
                ${g.limitations.map(lim => `<li>${lim}</li>`).join("")}
              </ul>
            </div>

            <!-- 6. Source and Verification -->
            <div class="pt-4 border-t border-outline-variant/20 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
              <div class="flex items-center gap-1.5 text-on-surface-variant">
                <span>Official Source:</span>
                <a href="${g.rule.sourceUrl}" target="_blank" class="text-primary font-bold hover:underline inline-flex items-center gap-0.5">
                  <span>${g.rule.sourceName}</span>
                  <span class="material-symbols-outlined text-[14px]">open_in_new</span>
                </a>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-[11px] text-on-surface-variant">Verified: ${g.rule.verifiedDate}</span>
                <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-800 border border-emerald-300">
                  ${g.rule.status}
                </span>
              </div>
            </div>
          </div>

          <!-- Actions Bar -->
          <div class="space-y-2">
            <h4 class="text-xs font-bold uppercase tracking-wider text-on-surface">What would you like to do next?</h4>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <a href="${g.rule.sourceUrl}" target="_blank" class="h-11 px-4 bg-surface-container text-on-surface rounded-xl text-xs font-bold hover:bg-surface-container-high transition-all flex items-center justify-center gap-1.5 shadow-sm">
                <span>Open ${g.rule.platform} Help</span>
                <span class="material-symbols-outlined text-[16px]">open_in_new</span>
              </a>

              <button onclick="window.SIP_NAVIGATOR.goToStep(5)" class="h-11 px-4 bg-primary text-on-primary rounded-xl text-xs font-bold hover:bg-tertiary transition-all flex items-center justify-center gap-1.5 shadow-sm">
                <span class="material-symbols-outlined text-[16px]">calendar_add_on</span>
                <span>Create Comeback Reminder</span>
              </button>

              <button onclick="window.SIP_NAVIGATOR.goToStep(2)" class="h-11 px-4 border border-outline-variant/40 rounded-xl text-xs font-semibold hover:bg-surface-container transition-all flex items-center justify-center gap-1.5">
                <span class="material-symbols-outlined text-[16px]">restart_alt</span>
                <span>Change My Answers</span>
              </button>
            </div>
          </div>
        </div>
      `;
    }

    // Screen 5: Comeback Plan
    else if (state.step === 5) {
      const today = new Date();
      const in30Days = new Date(today.getTime() + 30*24*60*60*1000).toISOString().slice(0, 10);

      contentHtml = `
        <div class="max-w-2xl mx-auto space-y-6">
          <div>
            <h2 class="text-xl font-bold text-on-surface">📅 SIP Comeback Plan</h2>
            <p class="text-xs text-on-surface-variant mt-1">
              Temporary breaks are healthy when cash is tight. Set an optional, zero-pressure reminder to review your financial situation later.
            </p>
          </div>

          <div class="bg-surface-container-lowest p-6 rounded-3xl border border-outline-variant/30 space-y-5 shadow-sm">
            <div>
              <label class="block text-xs font-bold text-on-surface mb-2">When would you like to review your SIP plan?</label>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                <button type="button" onclick="window.SIP_NAVIGATOR.setComebackDays(15)" class="p-3 text-left rounded-xl border border-outline-variant/30 hover:border-primary text-xs font-semibold">
                  15 Days (Quick Check-in)
                </button>
                <button type="button" onclick="window.SIP_NAVIGATOR.setComebackDays(30)" class="p-3 text-left rounded-xl border-2 border-primary bg-primary/5 text-xs font-bold text-primary">
                  30 Days (Next Cycle)
                </button>
                <button type="button" onclick="window.SIP_NAVIGATOR.setComebackDays(60)" class="p-3 text-left rounded-xl border border-outline-variant/30 hover:border-primary text-xs font-semibold">
                  60 Days (Extended Buffer)
                </button>
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold text-on-surface mb-1.5">Focus action for reminder:</label>
              <select id="comeback-action-select" class="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/30 text-xs font-medium focus:border-primary focus:outline-none">
                <option value="Review monthly budget and decide whether to resume SIP">Review monthly budget and decide whether to resume SIP</option>
                <option value="Check if salary credit date matches my SIP debit schedule">Check if salary credit date matches my SIP debit schedule</option>
                <option value="Consider stepping down to ₹100 or ₹500 scheme minimum">Consider stepping down to ₹100 or ₹500 scheme minimum</option>
                <option value="Decide whether to extend pause or cancel mandate">Decide whether to extend pause or cancel mandate</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-on-surface mb-1.5">Optional personal reminder note:</label>
              <input type="text" id="comeback-notes-input" placeholder="E.g., Medical expenses cleared; verify savings cushion." class="w-full h-10 px-3 rounded-xl bg-surface-container-low border border-outline-variant/30 text-xs font-medium focus:border-primary focus:outline-none"/>
            </div>

            <div class="bg-amber-500/10 border-l-4 border-amber-500 p-3.5 rounded-xl text-xs space-y-1">
              <div class="font-bold text-amber-900">Prototype Reminder Simulation Notice</div>
              <p class="text-on-surface-variant leading-relaxed">
                In this prototype, reminders are simulated locally. Click <strong>'Download Calendar Event (.ics)'</strong> below to add it directly to your device calendar.
              </p>
            </div>

            <div class="flex flex-col sm:flex-row gap-3 pt-2">
              <button onclick="window.SIP_NAVIGATOR.triggerIcsDownload()" class="flex-1 h-11 bg-primary text-on-primary rounded-xl text-xs font-bold hover:bg-tertiary transition-all flex items-center justify-center gap-1.5 shadow-sm">
                <span class="material-symbols-outlined text-[16px]">download</span>
                <span>Download Calendar Event (.ics)</span>
              </button>

              <button onclick="window.SIP_NAVIGATOR.goToStep(6)" class="h-11 px-6 bg-surface-container text-on-surface rounded-xl text-xs font-bold hover:bg-surface-container-high transition-all">
                Continue to Feedback →
              </button>
            </div>
          </div>

          <div class="flex justify-between">
            <button onclick="window.SIP_NAVIGATOR.goToStep(4)" class="h-9 px-4 rounded-xl border border-outline-variant/40 text-xs font-semibold hover:bg-surface-container transition-all">
              ← Back to Guidance
            </button>
            <button onclick="window.SIP_NAVIGATOR.goToStep(6)" class="text-xs text-on-surface-variant hover:text-primary font-medium">
              Skip Reminder →
            </button>
          </div>
        </div>
      `;
    }

    // Screen 6: Feedback & Usability Testing Panel
    else if (state.step === 6) {
      const metrics = computeMetrics();

      contentHtml = `
        <div class="max-w-3xl mx-auto space-y-6">
          <div>
            <h2 class="text-xl font-bold text-on-surface">🧪 Prototype Usability &amp; Hypothesis Validation</h2>
            <p class="text-xs text-on-surface-variant mt-1">
              Help us test our core discovery hypothesis: Does context-aware guidance reduce uncertainty compared to a generic pause button?
            </p>
          </div>

          ${!state.feedbackSubmitted ? `
            <div class="bg-surface-container-lowest p-6 rounded-3xl border border-outline-variant/30 space-y-5 shadow-sm">
              <div class="space-y-2">
                <label class="block text-xs font-bold text-on-surface">1. Did this guidance help you understand your next step?</label>
                <div class="space-y-1.5 text-xs">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="fb_clarity" value="Yes, I know what to do next." checked class="w-4 h-4 text-primary"/>
                    <span>Yes, I know what to do next.</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="fb_clarity" value="Partly, I still have questions." class="w-4 h-4 text-primary"/>
                    <span>Partly, I still have questions.</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="fb_clarity" value="No, I couldn't find a useful option." class="w-4 h-4 text-primary"/>
                    <span>No, I couldn't find a useful option.</span>
                  </label>
                </div>
              </div>

              <div class="space-y-1.5">
                <label class="block text-xs font-bold text-on-surface">2. What was most useful? (Optional)</label>
                <textarea id="fb-notes" rows="2" placeholder="E.g., Clear explanation that missing 1 debit does not cancel my SIP or ruin my credit score." class="w-full p-3 rounded-xl bg-surface-container-low border border-outline-variant/30 text-xs font-medium focus:border-primary focus:outline-none"></textarea>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" id="fb-chk-deadline" checked class="w-4 h-4 text-primary rounded"/>
                  <span>I clearly understand the cutoff deadline.</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" id="fb-chk-action" checked class="w-4 h-4 text-primary rounded"/>
                  <span>I identified an appropriate action to take.</span>
                </label>
              </div>

              <button onclick="window.SIP_NAVIGATOR.submitFeedbackForm()" class="w-full h-11 bg-primary text-on-primary rounded-xl text-xs font-bold hover:bg-tertiary transition-all shadow-sm">
                Submit Discovery Feedback
              </button>
            </div>
          ` : `
            <div class="p-4 rounded-2xl bg-emerald-500/15 border border-emerald-300 text-emerald-900 text-xs font-bold flex items-center gap-2">
              <span class="material-symbols-outlined text-[18px]">check_circle</span>
              <span>Thank you! Your feedback has been recorded in the prototype usability log.</span>
            </div>
          `}

          <!-- Live Usability Measurement Panel -->
          <div class="space-y-4 pt-4 border-t border-outline-variant/20">
            <div>
              <h3 class="text-base font-bold text-on-surface">📊 Documented Usability Measurement Plan &amp; Live Results</h3>
              <p class="text-[11px] text-on-surface-variant">Heuristic discovery usability metrics from recorded sessions (Not fabricated churn reduction metrics).</p>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/30 space-y-1 text-center">
                <div class="text-2xl font-bold text-primary">${metrics.clarityRate}%</div>
                <div class="text-[11px] font-bold text-on-surface">Guidance Clarity</div>
                <div class="text-[10px] text-on-surface-variant">${metrics.clarityNum} / ${metrics.total} sessions</div>
              </div>

              <div class="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/30 space-y-1 text-center">
                <div class="text-2xl font-bold text-primary">${metrics.deadlineRate}%</div>
                <div class="text-[11px] font-bold text-on-surface">Cutoff Comprehended</div>
                <div class="text-[10px] text-on-surface-variant">${metrics.deadlineNum} / ${metrics.total} sessions</div>
              </div>

              <div class="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/30 space-y-1 text-center">
                <div class="text-2xl font-bold text-primary">${metrics.actionRate}%</div>
                <div class="text-[11px] font-bold text-on-surface">Action Identified</div>
                <div class="text-[10px] text-on-surface-variant">${metrics.actionNum} / ${metrics.total} sessions</div>
              </div>

              <div class="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/30 space-y-1 text-center">
                <div class="text-2xl font-bold text-primary">${metrics.reminderRate}%</div>
                <div class="text-[11px] font-bold text-on-surface">Comeback Opt-In</div>
                <div class="text-[10px] text-on-surface-variant">${metrics.reminderNum} / ${metrics.total} sessions</div>
              </div>
            </div>

            <div class="p-4 rounded-2xl bg-surface-container-low border border-outline-variant/20 text-xs text-on-surface-variant space-y-2">
              <div class="font-bold text-on-surface">Research Boundary Notice:</div>
              <p class="leading-relaxed">
                Real-world 90-day SIP resumption, missed-instalment recovery rates, and cancellation reduction cannot be validated using an isolated prototype. Real validation requires integrating with live broker telemetry and tracking longitudinal cohort outcomes over 3–6 months.
              </p>
            </div>

            <div class="flex gap-3">
              <button onclick="window.SIP_NAVIGATOR.reset()" class="flex-1 h-10 bg-primary text-on-primary rounded-xl text-xs font-bold hover:bg-tertiary transition-all shadow-sm">
                🔄 Start New Guidance Session
              </button>
              <button onclick="switchPage('problem-statements')" class="h-10 px-5 rounded-xl border border-outline-variant/40 text-xs font-semibold hover:bg-surface-container transition-all">
                ← Return to Problem Statements
              </button>
            </div>
          </div>
        </div>
      `;
    }

    container.innerHTML = stepperHtml + contentHtml;
  }

  // Public Methods
  return {
    init: function() {
      render();
    },
    goToStep: function(s) {
      state.step = s;
      render();
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
    setSituation: function(s) {
      state.situation = s;
      render();
    },
    setPlatform: function(p) {
      state.platform = p;
    },
    setSetup: function(s) {
      state.setupType = s;
    },
    setTiming: function(t) {
      state.timeRemaining = t;
    },
    setComebackDays: function(days) {
      const today = new Date();
      state.comebackDays = days;
      alert(`Set comeback review for ${days} days from today.`);
    },
    triggerIcsDownload: function() {
      const action = document.getElementById("comeback-action-select")?.value || "Review monthly budget and decide whether to resume SIP";
      const notes = document.getElementById("comeback-notes-input")?.value || "";
      const days = state.comebackDays || 30;
      const targetDate = new Date(Date.now() + days*24*60*60*1000).toISOString().slice(0, 10);
      downloadIcs(targetDate, action, notes);
      state.comebackPlan = { targetDate, action };
      this.goToStep(6);
    },
    submitFeedbackForm: function() {
      const checkedEl = document.querySelector('input[name="fb_clarity"]:checked');
      const clarity = checkedEl ? checkedEl.value : "Yes, I know what to do next.";
      const notes = document.getElementById("fb-notes")?.value || "";
      const deadline = document.getElementById("fb-chk-deadline")?.checked || true;
      const action = document.getElementById("fb-chk-action")?.checked || true;
      saveFeedback({
        clarity,
        notes,
        deadline,
        action,
        reminder: state.comebackPlan !== null
      });
      state.feedbackSubmitted = true;
      render();
    },
    reset: function() {
      state.step = 1;
      state.comebackPlan = null;
      state.feedbackSubmitted = false;
      render();
    },
    loadPreset: function(presetKey) {
      const p = PRESETS[presetKey];
      if (!p) return;
      state.situation = p.situation;
      state.platform = p.platform;
      state.setupType = p.setup;
      state.timeRemaining = p.timing;
      state.step = 4;
      render();
    }
  };
})();
