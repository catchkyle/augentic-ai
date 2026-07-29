import test from "node:test";
import assert from "node:assert/strict";
import { calculateDiagnostic } from "../assets/blueprint-diagnostic.js";

test("calculates a conservative preliminary workflow result from operating inputs", () => {
  const result = calculateDiagnostic({
    monthlyVolume: 1000,
    hoursPerMonth: 200,
    loadedHourlyCost: 60,
    repeatableShare: 75,
    systemsCount: 3,
    desiredOutcome: "Increase capacity or throughput"
  });

  assert.deepEqual(result, {
    annualHours: 2400,
    recoverableHours: 1260,
    capacityValue: 75600,
    score: 78,
    band: "strong",
    recommendation: "Investigate a controlled pilot"
  });
});

test("clamps unsafe inputs and returns a measurement-first recommendation", () => {
  const result = calculateDiagnostic({
    monthlyVolume: -50,
    hoursPerMonth: 20,
    loadedHourlyCost: 45,
    repeatableShare: 25,
    systemsCount: 8,
    desiredOutcome: ""
  });

  assert.equal(result.annualHours, 240);
  assert.equal(result.recoverableHours, 42);
  assert.equal(result.capacityValue, 1890);
  assert.equal(result.score, 20);
  assert.equal(result.band, "measure");
  assert.equal(result.recommendation, "Measure or redesign the workflow first");
});
