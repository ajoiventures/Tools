const https = require("https");
const { Readable } = require("stream");

// Sinch / Phaxio credentials — set these in Netlify Dashboard → Environment Variables
const API_KEY    = process.env.PHAXIO_API_KEY    || "d633c79a-c3db-40ce-8298-8b385d0799cb";
const API_SECRET = process.env.PHAXIO_API_SECRET || "q_IyRpb3MqmGB5rJY2bGnXt-dG";

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: JSON.stringify({ success: false, message: "Method not allowed" }) };
  }

  try {
    // Parse multipart form data
    const contentType = event.headers["content-type"] || "";
    const boundary = contentType.split("boundary=")[1];
    if (!boundary) throw new Error("Missing multipart boundary");

    const body = Buffer.from(event.body, event.isBase64Encoded ? "base64" : "utf8");
    const parts = parseMultipart(body, boundary);

    const to      = parts.to?.value?.trim();
    const cover   = parts.cover?.value?.trim();
    const filePart = parts.file;

    if (!to)       throw new Error("Missing fax number");
    if (!filePart) throw new Error("Missing file");

    // Normalize number
    let digits = to.replace(/\D/g, "");
    if (digits.length === 10) digits = "1" + digits;
    if (digits.length !== 11) throw new Error("Invalid fax number: " + to);

    // Build multipart body for Phaxio
    const phaxBoundary = "----PhaxioBoundary" + Date.now();
    const chunks = [];

    const addField = (name, value) => {
      chunks.push(
        `--${phaxBoundary}\r\nContent-Disposition: form-data; name="${name}"\r\n\r\n${value}\r\n`
      );
    };

    addField("to[0]", `+${digits}`);
    if (cover) addField("cover_page_text", cover);

    // File part
    const mime = filePart.contentType || "application/octet-stream";
    const fname = filePart.filename || "document.pdf";
    const fileHeader =
      `--${phaxBoundary}\r\n` +
      `Content-Disposition: form-data; name="file[0]"; filename="${fname}"\r\n` +
      `Content-Type: ${mime}\r\n\r\n`;

    const textPart  = Buffer.from(chunks.join(""), "utf8");
    const fileHdr   = Buffer.from(fileHeader, "utf8");
    const footer    = Buffer.from(`\r\n--${phaxBoundary}--\r\n`, "utf8");
    const postBody  = Buffer.concat([textPart, fileHdr, filePart.data, footer]);

    // Call Phaxio
    const result = await phaxioRequest(postBody, phaxBoundary, API_KEY, API_SECRET);
    const json   = JSON.parse(result);

    if (!json.success) throw new Error(json.message || "Phaxio error");

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ success: true, fax_id: json.data?.id }),
    };

  } catch (err) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ success: false, message: err.message }),
    };
  }
};

// ── Minimal multipart parser ──────────────────────────────────────────────────
function parseMultipart(body, boundary) {
  const sep    = Buffer.from("--" + boundary);
  const parts  = {};
  let pos = 0;

  while (pos < body.length) {
    const sepIdx = body.indexOf(sep, pos);
    if (sepIdx === -1) break;
    pos = sepIdx + sep.length;

    if (body[pos] === 45 && body[pos + 1] === 45) break; // "--"
    if (body[pos] === 13) pos += 2; // \r\n

    // Find header end
    const headerEnd = body.indexOf(Buffer.from("\r\n\r\n"), pos);
    if (headerEnd === -1) break;
    const headerStr = body.slice(pos, headerEnd).toString("utf8");
    pos = headerEnd + 4;

    // Find next boundary
    const nextSep = body.indexOf(sep, pos);
    const dataEnd = nextSep === -1 ? body.length : nextSep - 2; // strip \r\n before boundary
    const data    = body.slice(pos, dataEnd);
    pos = nextSep === -1 ? body.length : nextSep;

    // Parse headers
    const dispMatch   = headerStr.match(/Content-Disposition:[^\r\n]*/i)?.[0] || "";
    const nameMatch   = dispMatch.match(/name="([^"]+)"/);
    const fnameMatch  = dispMatch.match(/filename="([^"]+)"/);
    const ctMatch     = headerStr.match(/Content-Type:\s*([^\r\n]+)/i);

    if (!nameMatch) continue;
    const name = nameMatch[1];

    if (fnameMatch) {
      parts[name] = { filename: fnameMatch[1], contentType: ctMatch?.[1]?.trim(), data };
    } else {
      parts[name] = { value: data.toString("utf8") };
    }
  }

  return parts;
}

// ── HTTPS request to Phaxio ───────────────────────────────────────────────────
function phaxioRequest(body, boundary, key, secret) {
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(`${key}:${secret}`).toString("base64");
    const req  = https.request({
      hostname: "api.phaxio.com",
      path:     "/v2.1/faxes",
      method:   "POST",
      headers:  {
        "Authorization":  `Basic ${auth}`,
        "Content-Type":   `multipart/form-data; boundary=${boundary}`,
        "Content-Length": body.length,
      },
    }, (res) => {
      const chunks = [];
      res.on("data", c => chunks.push(c));
      res.on("end",  () => resolve(Buffer.concat(chunks).toString("utf8")));
    });
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}
