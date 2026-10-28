/**
 * sip-rescue-mvp/js/components/FeedbackModal.js
 * 
 * Screen Five: Lightweight, Privacy-Conscious Feedback Component
 * 
 * Questions:
 * 1. "Did this help you understand what to do next?"
 *    - Yes, I know my next step
 *    - Partly, I still have questions
 *    - No, I couldn't find a suitable option
 * 2. Optional: "What was confusing or could be improved?"
 * 
 * Privacy:
 * Stored strictly in local browser storage (localStorage).
 * Never collects PAN, folio numbers, account numbers, or bank passwords.
 */

export function renderFeedbackWidget({ situation = "General", onClose }) {
  const container = document.createElement("div");
  container.className = "feedback-widget";

  let selectedOption = null;
  let isSubmitted = false;

  function updateView() {
    container.innerHTML = "";

    if (!isSubmitted) {
      container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div class="feedback-title">Did this help you understand what to do next?</div>
          ${onClose ? `<button class="btn btn-subtle btn-sm" id="btn-close-feedback">✕</button>` : ''}
        </div>

        <div class="feedback-options">
          <button type="button" class="feedback-btn" data-val="Yes, I know my next step">
            👍 Yes, I know my next step
          </button>
          <button type="button" class="feedback-btn" data-val="Partly, I still have questions">
            🤔 Partly, I still have questions
          </button>
          <button type="button" class="feedback-btn" data-val="No, I couldn't find a suitable option">
            👎 No, I couldn't find a suitable option
          </button>
        </div>

        <div id="feedback-details-box" style="display: none; margin-top: 12px;">
          <label style="display: block; font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px;">
            What was confusing or could be improved? (Optional)
          </label>
          <textarea class="form-input" id="feedback-comment" rows="2" placeholder="Tell us what was unclear about the platform rules or timings..."></textarea>
          
          <div style="display: flex; justify-content: flex-end; margin-top: 10px;">
            <button class="btn btn-primary btn-sm" id="btn-submit-feedback">
              Submit Feedback
            </button>
          </div>
        </div>

        <div style="font-size: 11px; color: var(--text-dim); margin-top: 10px;">
          🔒 Privacy notice: Feedback is stored strictly locally for usability research. No personal or financial identifiers are logged.
        </div>
      `;

      if (onClose) {
        container.querySelector("#btn-close-feedback")?.addEventListener("click", () => onClose());
      }

      const buttons = container.querySelectorAll(".feedback-btn");
      const detailsBox = container.querySelector("#feedback-details-box");

      buttons.forEach(btn => {
        btn.addEventListener("click", () => {
          buttons.forEach(b => b.classList.remove("selected"));
          btn.classList.add("selected");
          selectedOption = btn.getAttribute("data-val");
          detailsBox.style.display = "block";
        });
      });

      container.querySelector("#btn-submit-feedback")?.addEventListener("click", () => {
        const comment = container.querySelector("#feedback-comment").value;
        const entry = {
          id: "fb-" + Date.now(),
          situation,
          response: selectedOption,
          comment,
          timestamp: new Date().toISOString()
        };

        try {
          const list = JSON.parse(localStorage.getItem("sip_rescue_feedback_mvp") || "[]");
          list.push(entry);
          localStorage.setItem("sip_rescue_feedback_mvp", JSON.stringify(list));
        } catch (e) {
          console.warn("Storage unavailable", e);
        }

        isSubmitted = true;
        updateView();
      });
    } else {
      container.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 6px 0;">
          <div style="display: flex; align-items: center; gap: 8px; font-size: 13.5px; color: var(--primary); font-weight: 600;">
            <span>✓</span>
            <span>Thank you for your feedback! It helps improve SIP guidance for Indian investors.</span>
          </div>
          ${onClose ? `<button class="btn btn-subtle btn-sm" id="btn-done-feedback">Close</button>` : ''}
        </div>
      `;

      if (onClose) {
        container.querySelector("#btn-done-feedback")?.addEventListener("click", () => onClose());
      }
    }
  }

  updateView();
  return container;
}
