/**
 * Fax Proxy — Cloudflare Worker
 *
 * Sits between your browser and the Phaxio API to fix CORS.
 * Browser  →  https://your-worker.workers.dev/v2.1/faxes
 * Worker   →  https://api.phaxio.com/v2.1/faxes
 *
 * HOW TO DEPLOY (no CLI needed):
 * 1. Go to https://dash.cloudflare.com → Workers & Pages → Create Application → Create Worker
 * 2. Delete the default code, paste this entire file
 * 3. Click "Save and Deploy"
 * 4. Copy the *.workers.dev URL shown at the top
 * 5. Open the Fax app → Settings → paste that URL into "Cloudflare Worker URL"
 */

const PHAXIO_BASE = "https://api.phaxio.com";

const CORS = {
  "Access-Control-Allow-Origin":  "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Authorization, Content-Type",
  "Access-Control-Max-Age":       "86400",
};

export default {
  async fetch(request) {

    // Handle preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }

    // Build the upstream URL: strip worker origin, forward path + query
    const url      = new URL(request.url);
    const upstream = new URL(PHAXIO_BASE + url.pathname + url.search);

    // Forward the request as-is (auth header comes from the browser)
    const proxied = new Request(upstream, {
      method:  request.method,
      headers: request.headers,
      body:    request.method !== "GET" ? request.body : undefined,
      // Required for multipart file uploads
      duplex:  "half",
    });

    const response = await fetch(proxied);

    // Return Phaxio's response + CORS headers
    return new Response(response.body, {
      status:  response.status,
      headers: { ...Object.fromEntries(response.headers), ...CORS },
    });

  },
};
