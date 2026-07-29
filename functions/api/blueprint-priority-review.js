const json = (body, status) => new Response(JSON.stringify(body), {
  status,
  headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
});

export async function onRequestPost(context) {
  const requestOrigin = new URL(context.request.url).origin;
  const suppliedOrigin = context.request.headers.get("origin");
  if (suppliedOrigin && suppliedOrigin !== requestOrigin) {
    return json({ accepted: false, error: "Invalid origin." }, 403);
  }
  if (!context.env?.AUGENTIC_LEAD_WEBHOOK_URL) {
    return json({ accepted: false, error: "Scheduling is unavailable." }, 503);
  }

  let data;
  try {
    data = await context.request.json();
  } catch {
    return json({ accepted: false, error: "Invalid request." }, 400);
  }

  const submissionId = String(data?.submissionId || "").trim();
  if (!/^[a-f0-9-]{36}$/i.test(submissionId)) {
    return json({ accepted: false, error: "Invalid request." }, 400);
  }

  const downstreamFetch = context.fetch || fetch;
  try {
    const downstream = await downstreamFetch(context.env.AUGENTIC_LEAD_WEBHOOK_URL, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        brand: "Augentic AI",
        offer: "AI Workflow ROI Blueprint",
        formType: "ai-workflow-blueprint-priority-review",
        submissionId,
        requestedAt: new Date().toISOString()
      })
    });
    if (!downstream.ok) {
      return json({ accepted: false, error: "We could not queue the request." }, 502);
    }
  } catch {
    return json({ accepted: false, error: "We could not queue the request." }, 502);
  }

  let bookingUrl = "";
  try {
    const candidate = new URL(String(context.env.AUGENTIC_BOOKING_URL || ""));
    if (candidate.protocol === "https:") bookingUrl = candidate.toString();
  } catch {}

  return json({ accepted: true, ...(bookingUrl ? { bookingUrl } : {}) }, 202);
}

export function onRequestGet() {
  return json({ accepted: false, error: "Method not allowed." }, 405);
}
