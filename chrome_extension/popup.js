/**
 * popup.js — SIP Discovery Assistant Chrome Extension Logic
 * Captures selected text from active tab, previews it, and sends it to the local FastAPI receiver upon user approval.
 */

const DEFAULT_SERVER_URL = "http://127.0.0.1:8000";
const DEFAULT_AUTH_TOKEN = "sip_dev_token_groww_2026";

const textInput = document.getElementById("input-text");
const sourceLabelInput = document.getElementById("input-source-label");
const sourceUrlInput = document.getElementById("input-source-url");
const charCounter = document.getElementById("char-counter");
const statusBar = document.getElementById("status-bar");

const btnApprove = document.getElementById("btn-approve");
const btnDiscard = document.getElementById("btn-discard");
const btnToggleSettings = document.getElementById("btn-toggle-settings");
const captureSection = document.getElementById("capture-section");
const settingsSection = document.getElementById("settings-section");

const serverUrlInput = document.getElementById("input-server-url");
const authTokenInput = document.getElementById("input-auth-token");
const btnSaveSettings = document.getElementById("btn-save-settings");
const settingsStatus = document.getElementById("settings-status");

// Update character counter
function updateCharCount() {
  const len = textInput.value.length;
  charCounter.textContent = `${len.toLocaleString()} / 10,000 chars`;
  if (len > 10000) {
    charCounter.style.color = "#EF4444";
  } else {
    charCounter.style.color = "#64748B";
  }
}

textInput.addEventListener("input", updateCharCount);

// Detect friendly source label from URL
function detectSourceLabel(url) {
  try {
    const u = new URL(url);
    const host = u.hostname.toLowerCase();
    if (host.includes("reddit.com")) return "Reddit Community";
    if (host.includes("play.google.com")) return "Google Play Store";
    if (host.includes("groww.in")) return "Groww Official / Community";
    if (host.includes("twitter.com") || host.includes("x.com")) return "X / Twitter";
    if (host.includes("quora.com")) return "Quora Discussions";
    if (host.includes("sebi.gov.in")) return "SEBI Regulatory Guidance";
    return host.replace("www.", "");
  } catch (e) {
    return "Webpage Research";
  }
}

// Show status message helper
function showStatus(msg, type = "success") {
  statusBar.textContent = msg;
  statusBar.className = `status-msg status-${type}`;
  statusBar.classList.remove("hidden");
}

// Initialize popup on open
document.addEventListener("DOMContentLoaded", async () => {
  // Load saved settings
  chrome.storage.local.get(["serverUrl", "authToken"], (items) => {
    serverUrlInput.value = items.serverUrl || DEFAULT_SERVER_URL;
    authTokenInput.value = items.authToken || DEFAULT_AUTH_TOKEN;
  });

  // Query active tab
  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    if (!tabs || tabs.length === 0) return;
    const activeTab = tabs[0];
    sourceUrlInput.value = activeTab.url || "";
    sourceLabelInput.value = detectSourceLabel(activeTab.url || "");

    // Inject script to extract selected text
    if (activeTab.id && activeTab.url && !activeTab.url.startsWith("chrome://")) {
      try {
        const results = await chrome.scripting.executeScript({
          target: { tabId: activeTab.id },
          func: () => window.getSelection().toString()
        });

        if (results && results[0] && results[0].result && results[0].result.trim()) {
          textInput.value = results[0].result.trim();
          updateCharCount();
        } else {
          showStatus("No text highlighted on page. Highlight quote or type here.", "warn");
        }
      } catch (err) {
        showStatus("Note: Cannot auto-extract on this protected tab. You can paste quotes manually.", "warn");
      }
    }
  });
});

// Approve & Save handler
btnApprove.addEventListener("click", async () => {
  const text = textInput.value.trim();
  if (!text) {
    showStatus("Error: Selected text cannot be empty.", "error");
    return;
  }

  if (text.length > 10000) {
    showStatus("Error: Text exceeds 10,000 character limit.", "error");
    return;
  }

  btnApprove.disabled = true;
  btnApprove.textContent = "Saving...";

  chrome.storage.local.get(["serverUrl", "authToken"], async (config) => {
    const serverUrl = config.serverUrl || DEFAULT_SERVER_URL;
    const authToken = config.authToken || DEFAULT_AUTH_TOKEN;

    const payload = {
      text: text,
      source_url: sourceUrlInput.value.trim(),
      source: sourceLabelInput.value.trim() || "Browser Research",
      collected_at: new Date().toISOString(),
      auth_token: authToken
    };

    try {
      const response = await fetch(`${serverUrl}/api/collect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (response.status === 201) {
        const data = await response.json();
        if (data.duplicate_status === "exact_duplicate") {
          showStatus("⚠️ Saved! (Flagged as duplicate of an existing record)", "warn");
        } else {
          showStatus("✅ Saved successfully to local research database!", "success");
        }
        setTimeout(() => {
          window.close();
        }, 1600);
      } else if (response.status === 401) {
        showStatus("❌ Auth error (401). Check Extension Auth Token in Settings.", "error");
      } else if (response.status === 422) {
        showStatus("❌ Validation error: Invalid text length or format.", "error");
      } else {
        showStatus(`❌ Server returned error code: ${response.status}`, "error");
      }
    } catch (err) {
      showStatus("❌ Server unreachable. Make sure run_server.py is running on port 8000.", "error");
    } finally {
      btnApprove.disabled = false;
      btnApprove.textContent = "Approve & Save";
    }
  });
});

// Discard handler
btnDiscard.addEventListener("click", () => {
  textInput.value = "";
  updateCharCount();
  showStatus("Selection discarded.", "warn");
  setTimeout(() => window.close(), 600);
});

// Toggle Settings
btnToggleSettings.addEventListener("click", () => {
  captureSection.classList.toggle("hidden");
  settingsSection.classList.toggle("hidden");
});

// Save Settings handler
btnSaveSettings.addEventListener("click", () => {
  const url = serverUrlInput.value.trim() || DEFAULT_SERVER_URL;
  const token = authTokenInput.value.trim() || DEFAULT_AUTH_TOKEN;

  chrome.storage.local.set({ serverUrl: url, authToken: token }, () => {
    settingsStatus.textContent = "Settings saved successfully!";
    settingsStatus.className = "status-msg status-success";
    settingsStatus.classList.remove("hidden");
    setTimeout(() => {
      settingsStatus.classList.add("hidden");
      captureSection.classList.remove("hidden");
      settingsSection.classList.add("hidden");
    }, 1000);
  });
});
