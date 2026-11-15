// SigapBumil inference - the model, running in the browser.
//
// Pure functions, no page access, so the SAME file is used by the website
// (web/app.js) and by the parity test (tests/test_parity.mjs), which checks
// that these functions give the same numbers as Python.
//
// Everything about the model (feature order, weights, thresholds, cutoffs)
// is read from model.json. Nothing is hard-coded here.

export const MGDL_PER_MMOL = 18.016; // glucose: 1 mmol/L = 18.016 mg/dL

// What the bidan types (Indonesian units) -> what the model was trained on
// (the dataset uses mmol/L and Fahrenheit).
export function toModelUnits(input) {
  const x = {
    Age: input.age,
    SystolicBP: input.sbp,
    DiastolicBP: input.dbp,
    BS: input.sugar_mgdl / MGDL_PER_MMOL,
    BodyTemp: (input.temp_c * 9) / 5 + 32,
    HeartRate: input.pulse,
  };
  // Engineered features: only used if model.json lists them (currently it does not).
  x.PulsePressure = x.SystolicBP - x.DiastolicBP;
  x.MAP = x.DiastolicBP + x.PulsePressure / 3;
  return x;
}

// Standardize: how far is each vital from the training average, in standard deviations.
function standardize(model, x) {
  return model.features.map((f, k) => (x[f] - model.scaler.mean[k]) / model.scaler.scale[k]);
}

// Logistic regression: one score per class, then softmax turns scores into
// probabilities that add up to 1. Returns [P(low), P(mid), P(high)].
export function predict(model, x) {
  const z = standardize(model, x);
  const logits = model.coef.map(
    (row, c) => row.reduce((sum, w, k) => sum + w * z[k], model.intercept[c])
  );
  const max = Math.max(...logits); // subtract the max first so exp() cannot overflow
  const exps = logits.map((v) => Math.exp(v - max));
  const total = exps.reduce((a, b) => a + b, 0);
  return exps.map((v) => v / total);
}

// Probabilities -> action for the bidan (DESIGN.md section 6).
export function decide(model, proba) {
  const [low, mid, high] = model.classes.map((c) => proba[model.classes.indexOf(c)]);
  const { t_refer, t_recheck } = model.thresholds;
  if (high >= t_refer) return "refer";
  const midIsTop = mid > low && mid > high;
  if (midIsTop || mid + high >= t_recheck) return "recheck";
  return "routine";
}

// "Why?": each vital's push on the high-risk score = weight x standardized value.
// Returns the top 3 that RAISED the risk, biggest first.
export function explain(model, x) {
  const z = standardize(model, x);
  const wHigh = model.coef[model.classes.indexOf("high")];
  return model.features
    .map((feature, k) => ({ feature, value: x[feature], contribution: wHigh[k] * z[k] }))
    .filter((r) => r.contribution > 0)
    .sort((a, b) => b.contribution - a.contribution)
    .slice(0, 3);
}

// Danger sign: any SINGLE vital past a fixed clinical cutoff. Independent of
// the model, so one very abnormal number is never hidden by normal ones.
export function dangerSigns(model, x) {
  return Object.keys(model.danger_cutoffs).filter((f) => x[f] >= model.danger_cutoffs[f]);
}
