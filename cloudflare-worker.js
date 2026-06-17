/**
 * Fax Proxy — Cloudflare Worker (Sinch Fax API)
 *
 * Proxies browser → fax.api.sinch.com to fix CORS.
 *
 * DEPLOY:
 * 1. dash.cloudflare.com → Workers & Pages → Create → Start with Hello World
 * 2. Delete default code, paste this file, Save and Deploy
 * 3. Copy *.workers.dev URL → paste into Fax App Settings → Cloudflare Worker URL
 *
 * TEST: https://your-worker.workers.dev/ping
 *       should return: {"ok":true,"message":"Fax proxy is alive"}
 */

const SINCH_FAX = "https://fax.api.sinch.com";

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

  // Preflight
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS });
  }

  // Health check
  if (url.pathname === "/ping") {
    return new Response(JSON.stringify({ ok: true, message: "Fax proxy is alive" }), {
      status: 200,
      headers: { "Content-Type": "application/json", ...CORS },
    });
  }

  // Proxy to Sinch Fax API
  const target = SINCH_FAX + url.pathname + url.search;

  const headers = {};
  for (const [key, val] of request.headers.entries()) {
    if (key !== "host") headers[key] = val;
  }

  let body = null;
  if (!["GET", "HEAD"].includes(request.method)) {
    body = await request.arrayBuffer();
  }

  const upstream = await fetch(target, {
    method:  request.method,
    headers: headers,
    body:    body,
  });

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
