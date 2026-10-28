/**
 * sip-rescue-mvp/js/components/ComebackPlan.js
 * 
 * Screen Four: Comeback Plan
 * Supportive, practical, and non-pressuring continuity tool.
 * 
 * Features:
 * - Stated reason for pausing or stopping
 * - Review date picker with 15/30/60/90-day presets
 * - Suggested checklist before restarting
 * - Option to revise SIP amount or schedule
 * - Calendar reminder with .ics download
 * - Supportive messaging: "Restart when it fits your financial situation"
 */

export function renderComebackPlan({ contextData = null, onNavigateHome }) {
  const container = document.createElement("div");
  container.className = "comeback-screen-container";

  // Pre-fill reason if passed from wizard context
  const statedReason = (contextData && contextData.situation) 
    ? contextData.situation 
    : "Managing temporary cash flow tightness";

  // Default review date: 30 days ahead
  const defaultDateObj = new Date(Date.now() + 30 * 24 * 3600 * 1000);
  const defaultDateStr = defaultDateObj.toISOString().split("T")[0];

  let isSaved = false;
  let savedPlan = null;

  function updateView() {
    container.innerHTML = "";
    if (!isSaved) {
      renderForm();
    } else {
      renderConfirmation();
    }
  }

  function renderForm() {
    const card = document.createElement("div");
    card.className = "comeback-main-card";

    card.innerHTML = `
      <div class="screen-page-header" style="margin-bottom: 20px;">
        <div>
          <div class="breadcrumb-nav">
            <span class="breadcrumb-item">Dashboard</span>
            <span class="breadcrumb-sep">/</span>
            <span class="breadcrumb-active">Comeback Plan</span>
          </div>
          <h1 class="screen-page-title">Personal Financial Review Plan</h1>
          <p class="screen-page-subtitle">
            Restart when it fits your financial situation. Never feel pressured to resume before you can comfortably afford it.
          </p>
        </div>
      </div>

      <!-- Supportive Purpose Card -->
      <div class="comeback-intro-banner">
        <div class="intro-banner-icon">🌱</div>
        <div>
          <div style="font-size: 15px; font-weight: 700; color: #065f46; margin-bottom: 2px;">
            Investing should support your life, not cause stress
          </div>
          <p style="font-size: 13px; color: #047857; line-height: 1.5;">
            Pausing or reducing an investment during difficult periods is responsible financial management. This plan helps you set a peaceful reflection point to re-evaluate your monthly cash flow.
          </p>
        </div>
      </div>

      <!-- Form: Stated Reason -->
      <div class="form-group">
        <label class="form-label">Your stated reason for pausing or reviewing</label>
        <div class="form-help">Captured from your recent continuity assessment:</div>
        <input type="text" class="form-input" id="input-stated-reason" value="${statedReason}" />
      </div>

      <!-- Form: Review Date -->
      <div class="form-group">
        <label class="form-label">When would you like to review your cash flow?</label>
        <div class="date-preset-pills">
          <button type="button" class="btn btn-secondary btn-sm btn-preset-date" data-days="15">In 15 Days</button>
          <button type="button" class="btn btn-secondary btn-sm btn-preset-date active" data-days="30">In 30 Days (Recommended)</button>
          <button type="button" class="btn btn-secondary btn-sm btn-preset-date" data-days="60">In 2 Months</button>
          <button type="button" class="btn btn-secondary btn-sm btn-preset-date" data-days="90">In 3 Months</button>
        </div>
        <input type="date" class="form-input" id="input-review-date" value="${defaultDateStr}" min="${new Date().toISOString().split('T')[0]}" style="max-width: 280px; margin-top: 8px;" />
      </div>

      <!-- Suggested Checklist Before Restarting -->
      <div class="checklist-card" style="margin-bottom: 24px;">
        <div class="checklist-title">Suggested Checklist Before Restarting:</div>
        <ul class="careful-list">
          <li><strong>Emergency buffer:</strong> Ensure you have sufficient cash in your savings account for essential expenses before restarting debits.</li>
          <li><strong>Check amount suitability:</strong> Consider restarting at a smaller monthly amount (e.g. ₹500 or ₹1,000) rather than your previous full commitment.</li>
          <li><strong>Verify bank mandate:</strong> Check that your bank mandate is active so you do not encounter unexpected presentation issues.</li>
          <li><strong>Zero guilt:</strong> If your cash flow remains tight when the review date arrives, extending your pause is completely valid.</li>
        </ul>
      </div>

      <!-- Optional Revised Amount Consideration -->
      <div class="form-group">
        <label class="form-label">Consider a comfortable monthly restart amount (Optional)</label>
        <div class="form-help">Most Indian equity schemes accept SIPs from ₹500/month.</div>
        <div style="display: flex; gap: 10px; max-width: 320px;">
          <input type="number" class="form-input" id="input-target-amount" placeholder="e.g. 1000" min="100" step="100" />
          <span style="display: flex; align-items: center; font-size: 13px; color: var(--text-muted);">₹ / month</span>
        </div>
      </div>

      <!-- Personal Notes -->
      <div class="form-group">
        <label class="form-label">Personal Reflection Notes (Optional)</label>
        <textarea class="form-input" id="input-reminder-notes" rows="2" placeholder="e.g. Check salary status, medical expenses, or emergency savings before unpausing..."></textarea>
      </div>

      <!-- Actions -->
      <div class="wizard-actions-bar">
        <button class="btn btn-subtle" id="btn-cancel-comeback">Cancel & Return to Overview</button>
        <button class="btn btn-primary" id="btn-save-comeback">
          <span>Set My Comeback Reminder</span>
        </button>
      </div>
    `;

    // Presets
    card.querySelectorAll(".btn-preset-date").forEach(btn => {
      btn.addEventListener("click", () => {
        card.querySelectorAll(".btn-preset-date").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const days = parseInt(btn.getAttribute("data-days"), 10);
        const target = new Date(Date.now() + days * 24 * 3600 * 1000);
        card.querySelector("#input-review-date").value = target.toISOString().split("T")[0];
      });
    });

    card.querySelector("#btn-cancel-comeback").addEventListener("click", () => onNavigateHome());

    card.querySelector("#btn-save-comeback").addEventListener("click", () => {
      const dateVal = card.querySelector("#input-review-date").value;
      const reasonVal = card.querySelector("#input-stated-reason").value;
      const notesVal = card.querySelector("#input-reminder-notes").value;
      const targetAmt = card.querySelector("#input-target-amount").value;

      savedPlan = {
        id: "plan-" + Date.now(),
        reviewDate: dateVal,
        reason: reasonVal,
        notes: notesVal,
        targetAmount: targetAmt,
        createdAt: new Date().toISOString()
      };

      try {
        const existing = JSON.parse(localStorage.getItem("sip_rescue_comeback_plans") || "[]");
        existing.push(savedPlan);
        localStorage.setItem("sip_rescue_comeback_plans", JSON.stringify(existing));
      } catch (e) {
        console.warn("Local storage unavailable", e);
      }

      isSaved = true;
      updateView();
    });

    container.appendChild(card);
  }

  function renderConfirmation() {
    const card = document.createElement("div");
    card.className = "comeback-main-card";

    card.innerHTML = `
      <div style="text-align: center; margin-bottom: 24px;">
        <div style="font-size: 42px; margin-bottom: 8px;">✅</div>
        <h2 style="font-size: 22px; font-weight: 700; color: var(--text-main); margin-bottom: 4px;">
          Comeback Review Reminder Set
        </h2>
        <p style="font-size: 14px; color: var(--text-muted);">
          Your personal review milestone is scheduled for <strong>${savedPlan.reviewDate}</strong>.
        </p>
      </div>

      <div class="comeback-confirmation-card">
        <div style="font-size: 14px; font-weight: 700; color: #065f46; margin-bottom: 6px;">
          Focus: ${savedPlan.reason}
        </div>
        <div style="font-size: 13px; color: #047857; line-height: 1.5;">
          ${savedPlan.notes ? `<em>"${savedPlan.notes}"</em><br>` : ''}
          ${savedPlan.targetAmount ? `Planned restart amount when ready: <strong>₹${parseInt(savedPlan.targetAmount).toLocaleString("en-IN")}/month</strong>` : ''}
        </div>

        <div class="comeback-honest-notice">
          ℹ️ <strong>Demonstration Mode Notice:</strong>
          This reminder is stored in your local browser storage. Because this prototype does not collect sensitive contact information, automated SMS or push notifications will not be dispatched. Download the calendar invite below to link with your personal phone or computer calendar.
        </div>
      </div>

      <div class="confirmation-actions-row">
        <button class="btn btn-secondary" id="btn-download-ics">
          📅 Download .ics Calendar File
        </button>
        <button class="btn btn-primary" id="btn-return-overview">
          Return to Overview
        </button>
      </div>
    `;

    card.querySelector("#btn-return-overview").addEventListener("click", () => onNavigateHome());
    card.querySelector("#btn-download-ics").addEventListener("click", () => downloadIcsCalendar(savedPlan));

    container.appendChild(card);
  }

  function downloadIcsCalendar(plan) {
    const dtParts = plan.reviewDate.split("-");
    const y = dtParts[0];
    const m = dtParts[1];
    const d = dtParts[2];
    const dtStamp = `${y}${m}${d}T090000Z`;

    const icsContent = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//SIP Rescue//Comeback Plan Reminder//EN",
      "BEGIN:VEVENT",
      `UID:${plan.id}@siprescue.local`,
      `DTSTAMP:${dtStamp}`,
      `DTSTART:${dtStamp}`,
      `SUMMARY:SIP Rescue: Review Monthly Budget & SIP Status`,
      `DESCRIPTION:Review mutual fund SIP options and personal cash flow without pressure.\\nReason: ${plan.reason}\\nNotes: ${plan.notes || 'None'}\\n\\nGenerated by SIP Rescue - A SIP Continuity Assistant.`,
      "STATUS:CONFIRMED",
      "END:VEVENT",
      "END:VCALENDAR"
    ].join("\r\n");

    const blob = new Blob([icsContent], { type: "text/calendar;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `sip_rescue_review_${plan.reviewDate}.ics`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  updateView();
  return container;
}
