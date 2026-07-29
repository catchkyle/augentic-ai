const ALLOWED_EVENTS = new Set([
  "offer_view",
  "hero_cta_click",
  "sample_brief_click",
  "sample_brief_view",
  "funnel_form_start",
  "funnel_validation_error",
  "preliminary_result_view",
  "full_review_start",
  "funnel_form_submit",
  "generate_lead",
  "funnel_form_error",
  "thank_you_view",
  "priority_review_click"
]);

const ALLOWED_KEYS = new Set([
  "eventName",
  "offerId",
  "sessionId",
  "step",
  "scoreBand",
  "utmSource",
  "utmMedium",
  "utmCampaign",
  "sourcePage"
]);

const clean = (value, max = 160) => String(value ?? "").trim().slice(0, max);
const json = (body, status) => new Response(JSON.stringify(body), {
  status,
  headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
});

export async function onRequestPost(context) {
  const requestOrigin = new URL(context.request.url).origin;
  const suppliedOrigin = context.request.headers.get("origin");
  if (suppliedOrigin && suppliedOrigin !== requestOrigin) {
    return json({ accepted: false }, 403);
  }
  if (!context.env?.FUNNEL_DB) {
    return json({ accepted: false }, 503);
  }

  let data;
  try {
    data = await context.request.json();
  } catch {
    return json({ accepted: false }, 400);
  }

  const keys = Object.keys(data || {});
  if (keys.some((key) => !ALLOWED_KEYS.has(key))) {
    return json({ accepted: false }, 400);
  }

  const eventName = clean(data.eventName, 80);
  const sessionId = clean(data.sessionId, 80);
  if (!ALLOWED_EVENTS.has(eventName) || !/^[a-f0-9-]{36}$/i.test(sessionId)) {
    return json({ accepted: false }, 400);
  }

  try {
    await context.env.FUNNEL_DB.prepare(`
      INSERT INTO funnel_events (
        event_name, offer_id, session_id, step, score_band,
        utm_source, utm_medium, utm_campaign, source_page, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      eventName,
      clean(data.offerId, 100),
      sessionId,
      clean(data.step, 40),
      clean(data.scoreBand, 20),
      clean(data.utmSource, 120),
      clean(data.utmMedium, 120),
      clean(data.utmCampaign, 160),
      clean(data.sourcePage, 240),
      new Date().toISOString()
    ).run();
  } catch {
    return json({ accepted: false }, 503);
  }

  return new Response(null, { status: 204, headers: { "cache-control": "no-store" } });
}

export function onRequestGet() {
  return json({ accepted: false }, 405);
}
