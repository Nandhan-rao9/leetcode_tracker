// classic script; expose global
(function () {
  async function hmacSha256Hex(secretString, messageString) {
    const enc = new TextEncoder();
    const key = await crypto.subtle.importKey(
      "raw",
      enc.encode(secretString),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );
    const sig = await crypto.subtle.sign("HMAC", key, enc.encode(messageString));
    const bytes = new Uint8Array(sig);
    return Array.from(bytes).map(b => b.toString(16).padStart(2, "0")).join("");
  }
  window.hmacSha256Hex = hmacSha256Hex;
})();
