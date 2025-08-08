import { BACKEND_URL, SHARED_SECRET, USER_ID } from "./config.js";

const $ = (s) => document.querySelector(s);
const logEl = $("#log");
const statusEl = $("#status");
const barFill = $("#barFill");
const syncBtn = $("#syncBtn");

function log(s) {
  logEl.textContent += s + "\n";
  logEl.scrollTop = logEl.scrollHeight;
}

function setProgress(done, total) {
  const pct = total ? Math.floor((done / total) * 100) : 0;
  barFill.style.width = pct + "%";
  statusEl.textContent = `Progress: ${done}/${total} (${pct}%)`;
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function ensureContentScripts(tabId) {
  await chrome.scripting.executeScript({ target: { tabId }, files: ["hmac.js"] });
  await chrome.scripting.executeScript({ target: { tabId }, files: ["content.js"] });
}


syncBtn.addEventListener("click", async () => {
  logEl.textContent = "";
  setProgress(0, 100);
  statusEl.textContent = "Preparing…";

  const tab = await getActiveTab();
  if (!tab || !tab.id) {
    log("No active tab. Open any page on https://leetcode.com and try again.");
    return;
  }
  if (!/^https:\/\/leetcode\.com\//.test(tab.url || "")) {
    log("Please open a LeetCode tab before syncing.");
    return;
  }

  try {
    // 1) Inject content scripts now
    await ensureContentScripts(tab.id);

    // 2) Now message the injected content script
    const resp = await chrome.tabs.sendMessage(tab.id, {
      type: "LC_SYNC",
      backendUrl: BACKEND_URL,
      sharedSecret: SHARED_SECRET,
      userId: USER_ID
    });

    if (!resp) {
      log("No response from content script. Reload the LeetCode tab and try again.");
      return;
    }
  } catch (e) {
    log("Could not connect to the content script. Reload the LeetCode tab and click Sync again.");
    console.error(e);
  }
});

// progress events from content.js
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "LC_PROGRESS") {
    setProgress(msg.done, msg.total);
    if (msg.note) log(msg.note);
  }
  if (msg.type === "LC_DONE") {
    setProgress(msg.total, msg.total);
    log(`Done. Inserted: ${msg.inserted}, Duplicates: ${msg.duplicates}, Errors: ${msg.errors}`);
  }
});
