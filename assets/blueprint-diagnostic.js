const finite = (value, fallback = 0) => {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
};

const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));

export function calculateDiagnostic(input = {}) {
  const monthlyVolume = clamp(finite(input.monthlyVolume), 0, 10000000);
  const hoursPerMonth = clamp(finite(input.hoursPerMonth), 0, 100000);
  const loadedHourlyCost = clamp(finite(input.loadedHourlyCost), 0, 10000);
  const repeatableShare = clamp(finite(input.repeatableShare), 0, 100);
  const systemsCount = clamp(Math.round(finite(input.systemsCount, 1)), 1, 100);

  const annualHours = Math.round(hoursPerMonth * 12);
  const recoverableHours = Math.round(annualHours * (repeatableShare / 100) * 0.7);
  const capacityValue = Math.round(recoverableHours * loadedHourlyCost);

  const economicsScore = hoursPerMonth >= 500 ? 30 : hoursPerMonth >= 250 ? 26 : hoursPerMonth >= 100 ? 20 : hoursPerMonth >= 50 ? 12 : 5;
  const repeatabilityScore = repeatableShare >= 90 ? 25 : repeatableShare >= 75 ? 22 : repeatableShare >= 50 ? 15 : 8;
  const volumeScore = monthlyVolume >= 10000 ? 20 : monthlyVolume >= 2000 ? 18 : monthlyVolume >= 500 ? 15 : monthlyVolume >= 100 ? 10 : 5;
  const complexityScore = systemsCount <= 2 ? 15 : systemsCount <= 4 ? 11 : 2;
  const outcomeScore = String(input.desiredOutcome || "").trim() ? 10 : 0;
  const score = economicsScore + repeatabilityScore + volumeScore + complexityScore + outcomeScore;

  const band = score >= 70 ? "strong" : score >= 45 ? "validate" : "measure";
  const recommendation = band === "strong"
    ? "Investigate a controlled pilot"
    : band === "validate"
      ? "Validate the workflow and integration boundary"
      : "Measure or redesign the workflow first";

  return { annualHours, recoverableHours, capacityValue, score, band, recommendation };
}
