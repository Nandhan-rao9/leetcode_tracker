// content.js — content script injected by popup. No imports.
// Injects "injected.js" into the page context and calls it via postMessage.
// Uses window.hmacSha256Hex from hmac.js.

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const JITTER = () => Math.floor(Math.random() * 250);

function ensureInjectedOnce() {
  if (window.__lcInjectedLoaded) return;
  const script = document.createElement("script");
  script.src = chrome.runtime.getURL("injected.js");
  script.async = false;
  document.documentElement.appendChild(script);
  window.__lcInjectedLoaded = true;
}

// Robust page-context GraphQL with retries/backoff + operationName
async function rpcGraphQL(query, variables, { label = "gql", operationName = undefined, retries = 6 } = {}) {
  ensureInjectedOnce();
  const id = Math.random().toString(36).slice(2);

  for (let attempt = 0; attempt <= retries; attempt++) {
    const p = new Promise((resolve, reject) => {
      function onMsg(ev) {
        const m = ev.data;
        if (!m || m.__lc !== true || m.type !== "LC_GQL_RES" || m.id !== id) return;
        window.removeEventListener("message", onMsg);

        if (!m.ok) {
          const err = new Error(`GraphQL fetch failed: ${m.status || 0}`);
          err.status = m.status || 0;
          return reject(err);
        }
        if (m.data && m.data.errors) {
          return reject(new Error("GraphQL error: " + (m.data.errors[0]?.message || "unknown")));
        }
        resolve(m.data);
      }
      window.addEventListener("message", onMsg);
      window.postMessage({ __lc: true, type: "LC_GQL", id, query, variables, operationName }, "*");
    });

    try {
      return await p;
    } catch (e) {
      const status = e.status || 0;
      if (![403, 429, 500, 502, 503, 504, 0].includes(status) || attempt === retries) {
        throw e;
      }
      const delay = (300 + JITTER()) * Math.pow(2, attempt);
      chrome.runtime.sendMessage({
        type: "LC_PROGRESS",
        done: Math.min(74, 50 + attempt * 4),
        total: 100,
        note: `${label}: retry ${attempt + 1}/${retries} after ${delay}ms (status ${status})`
      });
      await sleep(delay);
    }
  }
}

// Confirm login (shows username) — helps debug “0 fetched”
async function getUserStatus() {
  const QUERY = `
    query userStatus {
      userStatus {
        isSignedIn
        username
      }
    }`;
  const data = await rpcGraphQL(QUERY, {}, { label: "userStatus", operationName: "userStatus", retries: 3 });
  return data?.userStatus || { isSignedIn: false, username: null };
}

// Iterate recent submissions (GraphQL pagination + throttle)
async function* iterateSubmissions(lastDays = 150) {
  const cutoff = Date.now() - lastDays * 24 * 3600 * 1000;
  let offset = 0;
  let lastKey = null;
  const limit = 20;

  const QUERY = `
    query Submissions($offset: Int!, $limit: Int!, $lastKey: String) {
      submissionList(offset: $offset, limit: $limit, lastKey: $lastKey) {
        hasNext
        lastKey
        submissions {
          id
          statusDisplay
          lang
          timestamp
          title
          titleSlug
        }
      }
    }`;

  while (true) {
    const data = await rpcGraphQL(QUERY, { offset, limit, lastKey }, { label: "submissions", operationName: "Submissions" });
    const page = data?.submissionList;
    const subs = page?.submissions || [];
    if (!subs.length) break;

    for (const s of subs) {
      const tsMs = (s.timestamp ? parseInt(s.timestamp, 10) : 0) * 1000;
      if (tsMs < cutoff) return; // stop when older than cutoff
      yield s;
    }

    if (!page.hasNext) break;
    lastKey = page.lastKey || null;
    offset += limit;
    await sleep(800 + JITTER());
  }
}

// Problem meta (difficulty + tags)
async function fetchProblemMeta(slug) {
  const q = `
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        title
        titleSlug
        difficulty
        topicTags { name }
      }
    }`;
  const vars = { titleSlug: slug };
  const data = await rpcGraphQL(q, vars, { label: `meta:${slug}`, operationName: "questionData", retries: 4 });
  const qd = data?.question;
  return {
    title: qd?.title || slug,
    difficulty: qd?.difficulty || null,
    lcTags: (qd?.topicTags || []).map(t => t.name),
  };
}

// Build payload for backend
async function buildImportBatch(userId, rawSubs) {
  const bySlug = new Map();

  for (const s of rawSubs) {
    if ((s.statusDisplay || "").toLowerCase() !== "accepted") continue;
    const slug = s.titleSlug;
    if (!slug) continue;

    const tsMs = (s.timestamp ? parseInt(s.timestamp, 10) : 0) * 1000;
    const item = bySlug.get(slug);
    if (!item || tsMs > item.tsMs) {
      bySlug.set(slug, {
        slug,
        title: s.title || slug.replace(/-/g, " "),
        url: `https://leetcode.com/problems/${slug}/`,
        lang: s.lang || null,
        submittedAt: new Date(tsMs).toISOString(),
        tsMs
      });
    }
  }

  const items = [];
  for (const it of bySlug.values()) {
    try {
      const meta = await fetchProblemMeta(it.slug);
      items.push({
        slug: it.slug,
        title: meta.title || it.title,
        url: it.url,
        difficulty: meta.difficulty,
        lcTags: meta.lcTags,
        lang: it.lang,
        submittedAt: it.submittedAt
      });
    } catch {
      items.push({
        slug: it.slug,
        title: it.title,
        url: it.url,
        difficulty: null,
        lcTags: [],
        lang: it.lang,
        submittedAt: it.submittedAt
      });
    }
    await sleep(120);
  }

  items.sort((a, b) => new Date(b.submittedAt) - new Date(a.submittedAt));
  return { userId, items };
}

// Send to backend with HMAC
async function postBatch(backendUrl, secret, batch) {
  const body = JSON.stringify(batch);
  const hex = await window.hmacSha256Hex(secret, body);
  const sig = "sha256=" + hex;
  const res = await fetch(`${backendUrl}/import/leetcode`, {
    method: "POST",
    headers: { "content-type": "application/json", "X-Signature": sig },
    body
  });
  if (!res.ok) throw new Error("Backend error " + res.status);
  return res.json();
}

// Progress → popup
function sendProgress(done, total, note) {
  chrome.runtime.sendMessage({ type: "LC_PROGRESS", done, total, note });
}
function sendDone(inserted, duplicates, errors, total) {
  chrome.runtime.sendMessage({ type: "LC_DONE", inserted, duplicates, errors, total });
}

// Listen to popup trigger
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type !== "LC_SYNC") return;
  const { backendUrl, sharedSecret, userId } = msg;

  (async () => {
    try {
      // sanity: logged-in check
      const st = await getUserStatus().catch(() => ({ isSignedIn: false }));
      if (!st.isSignedIn) {
        sendProgress(0, 100, "Not logged in. Open https://leetcode.com and sign in first.");
        sendDone(0, 0, 0, 0);
        return;
      }

      sendProgress(0, 100, `Fetching recent submissions for ${st.username || "you"}…`);
      const subs = [];
      for await (const s of iterateSubmissions(150)) {
        subs.push(s);
        if (subs.length % 20 === 0) sendProgress(Math.min(subs.length, 50), 100, `Pulled ${subs.length} submissions…`);
      }

      if (subs.length === 0) {
        sendProgress(55, 100, "No recent submissions found (last 150 days) or access blocked temporarily.");
      } else {
        sendProgress(55, 100, `Fetched ${subs.length}. Building batch…`);
      }

      const batch = await buildImportBatch(userId, subs);
      sendProgress(75, 100, `Enriched ${batch.items.length} problems. Uploading…`);

      const result = await postBatch(backendUrl, sharedSecret, batch);
      const { stats } = result || {};
      const inserted = stats?.insertedSubmissions ?? 0;
      const duplicates = stats?.duplicatesSkipped ?? 0;
      const errors = stats?.errors ?? 0;

      sendDone(inserted, duplicates, errors, batch.items.length);
    } catch (e) {
      sendDone(0, 0, 1, 0);
      chrome.runtime.sendMessage({ type: "LC_PROGRESS", done: 0, total: 100, note: "Error: " + (e.message || e) });
    }
  })();

  sendResponse({ ok: true });
  return true;
});
