/**
 * Fax Proxy — Cloudflare Worker
 * Proxies requests from the browser to api.phaxio.com, adding CORS headers.
 *
 * DEPLOY:
 * 1. dash.cloudflare.com → Workers & Pages → Create → Create Worker
 * 2. Delete default code, paste this entire file, click Deploy
 * 3. Copy the *.workers.dev URL → paste into Fax App Settings → Cloudflare Worker URL
 */

const PHAXIO = "https://api.phaxio.com";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin":  "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Authorization, Content-Type",
  "Access-Control-Max-Age":       "86400",
};

export default {
  async fetch(request) {

    // Preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    const url      = new URL(request.url);
    const upstream = PHAXIO + url.pathname + url.search;

    // Forward headers — strip host so Phaxio doesn't reject it
    const headers = new Headers();
    for (const [key, val] of request.headers.entries()) {
      if (key.toLowerCase() !== "host") headers.set(key, val);
    }

    const init = {
      method:   request.method,
      headers,
      redirect: "follow",
    };

    // Attach body for non-GET requests (file uploads, form posts)
    if (!["GET", "HEAD"].includes(request.method)) {
      init.body = request.body;
    }

    const resp = await fetch(upstream, init);

    // Rebuild response with CORS headers added
    const body    = await resp.arrayBuffer();
    const outHdrs = new Headers(resp.headers);
    for (const [k, v] of Object.entries(CORS_HEADERS)) outHdrs.set(k, v);

    return new Response(body, { status: resp.status, headers: outHdrs });
  },
};
