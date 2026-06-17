/**
 * Fax Proxy — Cloudflare Worker
 *
 * DEPLOY:
 * 1. dash.cloudflare.com → Workers & Pages → Create → Create Worker
 * 2. Delete ALL default code, paste this entire file
 * 3. Click "Save and Deploy"
 * 4. Copy the *.workers.dev URL → paste into Fax App Settings → Cloudflare Worker URL
 *
 * TEST: open https://your-worker.workers.dev/ping in your browser
 *       you should see: {"ok":true,"message":"Fax proxy is alive"}
 */

const PHAXIO = "https://api.phaxio.com";

const CORS = {
  "Access-Control-Allow-Origin":  "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Authorization, Content-Type",
};

addEventListener("fetch", event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);

  // ── Preflight ──────────────────────────────────────────────────────────────
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS });
  }

  // ── Health check ───────────────────────────────────────────────────────────
  if (url.pathname === "/ping") {
    return new Response(JSON.stringify({ ok: true, message: "Fax proxy is alive" }), {
      status: 200,
      headers: { "Content-Type": "application/json", ...CORS },
    });
  }

  // ── Proxy to Phaxio ────────────────────────────────────────────────────────
  const target = PHAXIO + url.pathname + url.search;

  // Copy headers, drop host
  const headers = {};
  for (const [key, val] of request.headers.entries()) {
    if (key !== "host") headers[key] = val;
  }

  // Read body as buffer so it can be forwarded cleanly
  let body = null;
  if (request.method !== "GET" && request.method !== "HEAD") {
    body = await request.arrayBuffer();
  }

  const upstream = await fetch(target, {
    method:  request.method,
    headers: headers,
    body:    body,
  });

  // Copy response, add CORS headers
  const resHeaders = {};
  for (const [key, val] of upstream.headers.entries()) {
    resHeaders[key] = val;
  }
  Object.assign(resHeaders, CORS);

  const resBody = await upstream.arrayBuffer();

  return new Response(resBody, {
    status:  upstream.status,
    headers: resHeaders,
  });
}
