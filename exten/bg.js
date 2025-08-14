// bg.js — service worker (MV3). Does the backend upload to avoid CORS issues in content scripts.

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  (async () => {
    if (msg?.type !== "LC_UPLOAD") return;

    try {
      const res = await fetch(`${msg.backendUrl}/import/leetcode`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "X-Signature": msg.signature
        },
        body: msg.body
      });

      const text = await res.text();
      let json;
      try { json = JSON.parse(text); } catch { json = { raw: text }; }

      sendResponse({ ok: res.ok, status: res.status, data: json });
    } catch (e) {
      // Network/CORS/DNS errors land here
      sendResponse({ ok: false, status: 0, error: String(e) });
    }
  })();

  return true; // keep channel open for async sendResponse
});
