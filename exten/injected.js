// injected.js — runs in the real page context
// Listens for LC_GQL messages, performs fetch with cookies/csrf, replies via LC_GQL_RES

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

  window.addEventListener("message", async (ev) => {
    const msg = ev.data;
    if (!msg || msg.__lc !== true || msg.type !== "LC_GQL") return;
    if (ev.source !== window) return;

    try {
      const out = await doGraphQL(msg.query, msg.variables, msg.operationName);
      window.postMessage({
        __lc: true,
        type: "LC_GQL_RES",
        id: msg.id,
        ok: out.ok,
        status: out.status,
        data: out.json
      }, "*");
    } catch (e) {
      window.postMessage({
        __lc: true,
        type: "LC_GQL_RES",
        id: msg.id,
        ok: false,
        status: 0,
        error: String(e)
      }, "*");
    }
  });
})();
