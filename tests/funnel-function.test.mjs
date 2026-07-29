import test from "node:test";
import assert from "node:assert/strict";
import { onRequestPost } from "../functions/api/ai-workflow-blueprint.js";

const validLead = {
  firstName: "QA",
  lastName: "Funnel Test",
  email: "qa+augentic-funnel@example.com",
  company: "Augentic AI QA",
  role: "COO / Operations Leader",
  companySize: "50-199 employees",
  department: "Operations",
  workflow: "QA-only test of the workflow assessment funnel",
  monthlyVolume: "500-2,000 items",
  hoursPerMonth: "200",
  loadedHourlyCost: "60",
  repeatableShareValue: "75",
  systems: "CRM and ticketing platform",
  desiredOutcome: "Reduce cycle time",
  budgetReadiness: "Exploring budget",
  timeline: "Within 90 days",
  website: "",
  sourcePage: "/ai-workflow-roi-blueprint/",
  utmSource: "qa"
};

function context(body, fetchImpl, env = { AUGENTIC_LEAD_WEBHOOK_URL: "https://example.test/hook" }) {
  return {
    request: new Request("https://augenticai.com/api/ai-workflow-blueprint", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body)
    }),
    env,
    fetch: fetchImpl
  };
}

test("accepts a valid lead only after downstream capture succeeds", async () => {
  let forwarded;
  const fetchImpl = async (_url, options) => {
    forwarded = JSON.parse(options.body);
    return new Response(JSON.stringify({ accepted: true }), { status: 200 });
  };

  const response = await onRequestPost(context(validLead, fetchImpl));
  const payload = await response.json();

  assert.equal(response.status, 202);
  assert.equal(payload.accepted, true);
  assert.equal(forwarded.brand, "Augentic AI");
  assert.equal(forwarded.offer, "AI Workflow ROI Blueprint");
  assert.equal(forwarded.email, validLead.email);
});

test("accepts the reduced value-first payload and forwards diagnostic evidence", async () => {
  let forwarded;
  const minimalLead = {
    firstName: "QA",
    lastName: "Diagnostic",
    email: "qa+diagnostic@example.com",
    company: "Augentic AI QA",
    role: "CIO / CTO / IT Leader",
    workflow: "Route and resolve recurring support requests",
    monthlyVolume: "1000",
    hoursPerMonth: "200",
    loadedHourlyCost: "60",
    repeatableShareValue: "75",
    systems: "CRM, ticketing, email",
    desiredOutcome: "Reduce cycle time",
    diagnosticScore: "78",
    diagnosticBand: "strong",
    annualHours: "2400",
    recoverableHours: "1260",
    capacityValue: "75600",
    website: ""
  };
  const response = await onRequestPost(context(minimalLead, async (_url, options) => {
    forwarded = JSON.parse(options.body);
    return new Response(null, { status: 200 });
  }));

  assert.equal(response.status, 202);
  assert.equal(forwarded.diagnosticScore, 78);
  assert.equal(forwarded.diagnosticBand, "strong");
  assert.equal(forwarded.capacityValue, 75600);
  assert.equal(forwarded.companySize, "");
  assert.ok(forwarded.submissionId);
});

test("rejects incomplete or invalid leads before forwarding", async () => {
  let calls = 0;
  const response = await onRequestPost(context({ ...validLead, email: "not-an-email" }, async () => {
    calls += 1;
    return new Response(null, { status: 200 });
  }));

  assert.equal(response.status, 400);
  assert.equal(calls, 0);
});

test("does not claim success when downstream capture fails", async () => {
  const response = await onRequestPost(context(validLead, async () => new Response("down", { status: 503 })));
  const payload = await response.json();

  assert.equal(response.status, 502);
  assert.equal(payload.accepted, false);
});

test("silently accepts honeypot submissions without forwarding", async () => {
  let calls = 0;
  const response = await onRequestPost(context({ ...validLead, website: "https://spam.example" }, async () => {
    calls += 1;
    return new Response(null, { status: 200 });
  }));

  assert.equal(response.status, 202);
  assert.equal(calls, 0);
});
