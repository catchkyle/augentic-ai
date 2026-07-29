const REQUIRED_FIELDS = [
  "firstName",
  "lastName",
  "email",
  "company",
  "role",
  "companySize",
  "department",
  "workflow",
  "monthlyVolume",
  "hoursPerMonth",
  "systems",
  "desiredOutcome",
  "budgetReadiness",
  "timeline"
];

const jsonResponse = (body, status) => new Response(JSON.stringify(body), {
  status,
  headers: { "content-type": "application/json; charset=utf-8" }
});

const clean = (value, max = 500) => String(value ?? "").trim().slice(0, max);

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!env?.AUGENTIC_LEAD_WEBHOOK_URL) {
    return jsonResponse({ accepted: false, error: "Lead capture is unavailable." }, 503);
  }

  let data;
  try {
    data = await request.json();
  } catch {
    return jsonResponse({ accepted: false, error: "Invalid request." }, 400);
  }

  if (clean(data.website, 100)) {
    return jsonResponse({ accepted: true }, 202);
  }

  const missing = REQUIRED_FIELDS.filter((field) => !clean(data[field]));
  if (missing.length || !/^\S+@\S+\.\S+$/.test(clean(data.email, 254))) {
    return jsonResponse({ accepted: false, error: "Complete all required fields." }, 400);
  }

  const lead = {
    brand: "Augentic AI",
    offer: "AI Workflow ROI Blueprint",
    formType: "ai-workflow-roi-blueprint",
    firstName: clean(data.firstName, 80),
    lastName: clean(data.lastName, 80),
    email: clean(data.email, 254),
    company: clean(data.company, 160),
    role: clean(data.role, 120),
    companySize: clean(data.companySize, 80),
    department: clean(data.department, 120),
    workflow: clean(data.workflow, 1200),
    monthlyVolume: clean(data.monthlyVolume, 120),
    hoursPerMonth: clean(data.hoursPerMonth, 120),
    systems: clean(data.systems, 800),
    desiredOutcome: clean(data.desiredOutcome, 160),
    budgetReadiness: clean(data.budgetReadiness, 120),
    timeline: clean(data.timeline, 120),
    primaryRisk: clean(data.primaryRisk, 400),
    sourcePage: clean(data.sourcePage, 500),
    referrer: clean(data.referrer, 500),
    utmSource: clean(data.utmSource, 120),
    utmMedium: clean(data.utmMedium, 120),
    utmCampaign: clean(data.utmCampaign, 160),
    submittedAt: new Date().toISOString()
  };

  const downstreamFetch = context.fetch || fetch;
  let downstream;
  try {
    downstream = await downstreamFetch(env.AUGENTIC_LEAD_WEBHOOK_URL, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(lead)
    });
  } catch {
    return jsonResponse({ accepted: false, error: "We could not accept your request. Please try again." }, 502);
  }

  if (!downstream.ok) {
    return jsonResponse({ accepted: false, error: "We could not accept your request. Please try again." }, 502);
  }

  return jsonResponse({ accepted: true }, 202);
}

export function onRequestGet() {
  return jsonResponse({ accepted: false, error: "Method not allowed." }, 405);
}
