import test from "node:test";
import assert from "node:assert/strict";
import { onRequestPost } from "../functions/api/funnel-event.js";

function context(body, { origin = "https://augenticai.com", db } = {}) {
  return {
    request: new Request("https://augenticai.com/api/funnel-event", {
      method: "POST",
      headers: { "content-type": "application/json", origin },
      body: JSON.stringify(body)
    }),
    env: { FUNNEL_DB: db }
  };
}

function recordingDb() {
  const calls = [];
  return {
    calls,
    prepare(sql) {
      return {
        bind(...values) {
          calls.push({ sql, values });
          return { run: async () => ({ success: true }) };
        }
      };
    }
  };
}

const validEvent = {
  eventName: "preliminary_result_view",
  offerId: "ai_workflow_roi_blueprint",
  sessionId: "f35956cb-73a7-4a34-9063-a0206f0fc26f",
  step: "result",
  scoreBand: "strong",
  utmSource: "linkedin",
  utmMedium: "social",
  utmCampaign: "blueprint",
  sourcePage: "/ai-workflow-roi-blueprint/"
};

test("stores an allowlisted non-PII funnel event in D1", async () => {
  const db = recordingDb();
  const response = await onRequestPost(context(validEvent, { db }));

  assert.equal(response.status, 204);
  assert.equal(db.calls.length, 1);
  assert.match(db.calls[0].sql, /INSERT INTO funnel_events/);
  assert.ok(db.calls[0].values.includes("preliminary_result_view"));
  assert.ok(db.calls[0].values.includes("strong"));
});

test("accepts the full conversion milestone allowlist", async () => {
  for (const eventName of ["hero_cta_click", "sample_brief_view", "thank_you_view", "priority_review_click"]) {
    const db = recordingDb();
    const response = await onRequestPost(context({ ...validEvent, eventName }, { db }));
    assert.equal(response.status, 204, eventName);
    assert.equal(db.calls.length, 1, eventName);
  }
});

test("rejects event payloads containing personal information", async () => {
  const db = recordingDb();
  const response = await onRequestPost(context({ ...validEvent, email: "person@example.com" }, { db }));
  assert.equal(response.status, 400);
  assert.equal(db.calls.length, 0);
});

test("rejects cross-origin and unknown events before writing", async () => {
  const db = recordingDb();
  const crossOrigin = await onRequestPost(context(validEvent, { db, origin: "https://evil.example" }));
  const unknown = await onRequestPost(context({ ...validEvent, eventName: "arbitrary_event" }, { db }));
  assert.equal(crossOrigin.status, 403);
  assert.equal(unknown.status, 400);
  assert.equal(db.calls.length, 0);
});
