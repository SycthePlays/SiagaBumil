// Parity test: the browser code must give the same answers as Python.
//
// Run:  node tests/test_parity.mjs        (Node 22.7 or newer)
//
// web/test_cases.json holds inputs plus the answers Python (scikit-learn)
// gave. We run the SAME file the website uses (web/inference.js) on those
// inputs and compare: probabilities within 1e-6, same action, same reasons,
// same danger signs.
import { readFileSync } from "node:fs";
import { toModelUnits, predict, decide, explain, dangerSigns } from "../web/inference.js";

const web = new URL("../web/", import.meta.url);
const model = JSON.parse(readFileSync(new URL("model.json", web), "utf8"));
const cases = JSON.parse(readFileSync(new URL("test_cases.json", web), "utf8"));
const TOLERANCE = 1e-6;

let maxDiff = 0;
const failures = [];
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

cases.forEach((c, i) => {
  const x = toModelUnits(c.input);
  const proba = predict(model, x);
  const diff = Math.max(...proba.map((p, k) => Math.abs(p - c.proba[k])));
  maxDiff = Math.max(maxDiff, diff);

  const got = {
    action: decide(model, proba),
    reasons: explain(model, x).map((r) => r.feature),
    danger_signs: dangerSigns(model, x),
  };
  if (diff > TOLERANCE) failures.push(`case ${i}: probability differs by ${diff}`);
  for (const key of Object.keys(got)) {
    if (!same(got[key], c[key])) {
      failures.push(`case ${i}: ${key} JS=${JSON.stringify(got[key])} Python=${JSON.stringify(c[key])}`);
    }
  }
});

// The example chips on the website must give the action Python expects.
for (const ex of model.examples) {
  const action = decide(model, predict(model, toModelUnits(ex.input)));
  console.log(`demo ${ex.id.padEnd(10)} -> ${action}`);
  if (action !== ex.expected_action) failures.push(`demo ${ex.id}: ${action} != ${ex.expected_action}`);
}

console.log(`cases: ${cases.length} | max probability difference: ${maxDiff.toExponential(2)} (limit ${TOLERANCE})`);
if (cases.length < 30) failures.push(`expected at least 30 cases, found ${cases.length}`);
if (failures.length) {
  console.error("PARITY FAILED\n" + failures.join("\n"));
  process.exit(1);
}
console.log("PARITY OK: JS matches Python on every case (probabilities, action, reasons, danger signs)");
