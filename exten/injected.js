// injected.js — runs in the real page context
// Handles LC_GQL (GraphQL POST) and LC_FETCH (generic GET/POST) for first-party requests.

(function () {
  function getCsrf() {
    try {
      return (document.cookie.split("; ").find(c => c.startsWith("csrftoken=")) || "").split("=")[1] || "";
    } catch {
      return "";
    }
  }

  async function doGraphQL(query, variables, operationName) {
    const res = await fetch("https://leetcode.com/graphql/", {
      method: "POST",
      credentials: "include",
      headers: {
        "content-type": "application/json",
        "x-csrftoken": getCsrf(),
        "referer": location.origin + "/"
      },
      body: JSON.stringify({ query, variables, operationName })
    });
    const text = await res.text();
    let json;
    try { json = JSON.parse(text); } catch { json = { raw: text }; }
    return { status: res.status, ok: res.ok, json };
  }

  async function doFetch(method, url, body) {
    const res = await fetch(url, {
      method,
      credentials: "include",
      headers: {
        "content-type": body ? "application/json" : undefined,
        "x-csrftoken": getCsrf(),
        "referer": location.origin + "/"
      },
      body: body ? JSON.stringify(body) : undefined
    });
    const text = await res.text();
    let json;
    try { json = JSON.parse(text); } catch { json = { raw: text }; }
    return { status: res.status, ok: res.ok, json };
  }

  window.addEventListener("message", async (ev) => {
    const msg = ev.data;
    if (!msg || msg.__lc !== true) return;
    if (ev.source !== window) return;

    try {
      if (msg.type === "LC_GQL") {
        const out = await doGraphQL(msg.query, msg.variables, msg.operationName);
        window.postMessage({ __lc: true, type: "LC_GQL_RES", id: msg.id, ok: out.ok, status: out.status, data: out.json }, "*");
      } else if (msg.type === "LC_FETCH") {
        const out = await doFetch(msg.method || "GET", msg.url, msg.body);
        window.postMessage({ __lc: true, type: "LC_FETCH_RES", id: msg.id, ok: out.ok, status: out.status, data: out.json }, "*");
      }
    } catch (e) {
      window.postMessage({ __lc: true, type: msg.type + "_RES", id: msg.id, ok: false, status: 0, error: String(e) }, "*");
    }
  });
})();
