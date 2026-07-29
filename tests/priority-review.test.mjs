import test from "node:test";
import assert from "node:assert/strict";
import { onRequestPost } from "../functions/api/blueprint-priority-review.js";

const submissionId = "0e0ecb67-a227-4e20-b18c-104799544168";
function context(body, fetchImpl, env = {}) {
  return {
    request: new Request("https://augenticai.com/api/blueprint-priority-review", {
      method: "POST",
      headers: { "content-type": "application/json", origin: "https://augenticai.com" },
      body: JSON.stringify(body)
    }),
    env: { AUGENTIC_LEAD_WEBHOOK_URL: "https://example.test/hook", ...env },
    fetch: fetchImpl
  };
}

test("queues a priority review without collecting contact information again", async () => {
  let forwarded;
  const response = await onRequestPost(context({ submissionId }, async (_url, options) => {
    forwarded = JSON.parse(options.body);
    return new Response(null, { status: 200 });
  }));
  const body = await response.json();

  assert.equal(response.status, 202);
  assert.equal(body.accepted, true);
  assert.equal(forwarded.formType, "ai-workflow-blueprint-priority-review");
  assert.equal(forwarded.submissionId, submissionId);
  assert.equal(Object.hasOwn(forwarded, "email"), false);
});

test("returns a configured HTTPS scheduling link after queuing", async () => {
  const response = await onRequestPost(context(
    { submissionId },
    async () => new Response(null, { status: 200 }),
    { AUGENTIC_BOOKING_URL: "https://calendar.example.com/augentic" }
  ));
  const body = await response.json();
  assert.equal(body.bookingUrl, "https://calendar.example.com/augentic");
});

test("rejects invalid submission identifiers before forwarding", async () => {
  let calls = 0;
  const response = await onRequestPost(context({ submissionId: "bad" }, async () => {
    calls += 1;
    return new Response(null, { status: 200 });
  }));
  assert.equal(response.status, 400);
  assert.equal(calls, 0);
});
