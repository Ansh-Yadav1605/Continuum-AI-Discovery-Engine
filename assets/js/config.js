// assets/js/config.js
// Continuum AI — Centralized Environment-Aware API Configuration
// Supports seamless local development and production deployment (Vercel + Railway).

window.APP_CONFIG = (function() {
  const LOCAL_DEV_DEFAULT = "http://127.0.0.1:8000";

  function isLocalEnvironment() {
    const host = window.location.hostname;
    return host === "localhost" || host === "127.0.0.1" || host === "" || host === "0.0.0.0";
  }

  function getBackendUrl() {
    // 1. Manual User Override (stored in localStorage for easy Vercel testing)
    const customUrl = localStorage.getItem("continuum_backend_url");
    if (customUrl && customUrl.trim()) {
      return customUrl.trim().replace(/\/$/, "");
    }

    // 2. Globally injected environment variable (e.g. window.BACKEND_API_URL)
    if (window.BACKEND_API_URL && window.BACKEND_API_URL.trim()) {
      return window.BACKEND_API_URL.trim().replace(/\/$/, "");
    }

    // 3. Localhost development fallback
    if (isLocalEnvironment()) {
      return LOCAL_DEV_DEFAULT;
    }

    // 4. In deployed production (Vercel):
    // DO NOT silently fall back to localhost!
    console.warn(
      "[Continuum AI] Production environment detected without a configured Backend API URL. " +
      "Configure window.BACKEND_API_URL or enter your deployed Railway URL in Settings."
    );
    return "";
  }

  function apiUrl(endpoint) {
    const base = getBackendUrl();
    const cleanEndpoint = endpoint.startsWith("/") ? endpoint : "/" + endpoint;
    if (!base) {
      // In production without backend, return relative endpoint (handles reverse proxy)
      return cleanEndpoint;
    }
    return base + cleanEndpoint;
  }

  function setBackendUrl(url) {
    if (!url || !url.trim()) {
      localStorage.removeItem("continuum_backend_url");
    } else {
      localStorage.setItem("continuum_backend_url", url.trim().replace(/\/$/, ""));
    }
    updateDownloadLinks();
  }

  function updateDownloadLinks() {
    const links = document.querySelectorAll("a[data-api-endpoint]");
    links.forEach(link => {
      const endpoint = link.getAttribute("data-api-endpoint");
      if (endpoint) {
        link.href = apiUrl(endpoint);
      }
    });
  }

  return {
    isLocalEnvironment,
    getBackendUrl,
    apiUrl,
    setBackendUrl,
    updateDownloadLinks
  };
})();
