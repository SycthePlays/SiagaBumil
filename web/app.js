// SigapBumil - the page: form, validation, language, drawing the result.
//
// ALL model math is in inference.js (the file the parity test checks against
// Python). This file never computes a probability itself.
// Nothing typed here is stored or sent anywhere: no cookies, no storage, and
// the only network requests are this site's own files.

import { MGDL_PER_MMOL, toModelUnits, predict, decide, explain, dangerSigns } from "./inference.js";

// ---- every word on the page, in both languages -----------------------------
const STR = {
  id: {
    tagline: "Bantu bidan memutuskan rujukan lebih cepat",
    badge: "Prototipe · Veritas AI Hackathon 2026",
    checkerTitle: "Periksa tanda vital",
    examples: "Contoh (data sintetis)",
    chips: { routine: "Rutin", borderline: "Borderline", high: "Berisiko tinggi" },
    age: "Usia", years: "tahun",
    bp: "Tekanan darah", sbp: "Sistolik", sbpHint: "angka atas", dbp: "Diastolik", dbpHint: "angka bawah",
    sugar: "Gula darah", sugarHint: "gula darah sewaktu", switchUnit: "Ganti satuan gula darah",
    temp: "Suhu tubuh", pulse: "Nadi", pulseHint: "denyut per menit",
    check: "Periksa", reset: "Reset",
    errRange: (lo, hi) => `Isi antara ${lo}–${hi}`,
    errBp: "Sistolik harus lebih besar dari diastolik",
    resultTitle: "Hasil",
    empty: "Masukkan tanda vital untuk melihat hasil",
    loadError: "Model gagal dimuat. Periksa koneksi, lalu muat ulang.",
    reload: "Muat ulang",
    action: {
      refer: ["Rujuk sekarang", "Rujuk ke puskesmas/rumah sakit hari ini"],
      recheck: ["Cek ulang 1–2 hari", "Ukur ulang tanda vital dalam 1–2 hari"],
      routine: ["Rutin", "Lanjutkan kunjungan antenatal rutin"],
    },
    lineRefer2: (a, b) => `Kombinasi ${a} dan ${b} menunjukkan risiko tinggi.`,
    lineRefer1: (a) => `Nilai ${a} menunjukkan risiko tinggi.`,
    lineRefer0: "Model menilai risiko tinggi.",
    lineRecheck: "Belum risiko tinggi, tetapi tanda vital perlu dipantau.",
    lineRoutine: "Tanda vital tidak menunjukkan risiko tinggi.",
    probTitle: "Perkiraan model",
    classes: { low: "Risiko rendah", mid: "Risiko sedang", high: "Risiko tinggi" },
    whyTitle: "Mengapa?",
    noFactors: "Tidak ada faktor risiko menonjol",
    above: "di atas rata-rata data latih", below: "di bawah rata-rata data latih",
    outOfRange: "di luar rentang umum",
    dangerTitle: "Tanda bahaya",
    considerReferral: "Pertimbangkan rujukan.",
    dangerNote: "Peringatan ini memakai batas klinis tetap, terpisah dari model.",
    disclaimer: "Prototipe, bukan nasihat medis.",
    howTitle: "Cara kerja",
    steps: [
      ["6 tanda vital", "usia, tekanan darah, gula darah, suhu, nadi"],
      ["Model AI (regresi logistik)", "berjalan di ponsel ini, tanpa internet"],
      ["Tindakan", "Rujuk sekarang, Cek ulang atau Rutin, dengan alasannya"],
    ],
    thApproach: "Pendekatan", thRecall: "Tertangkap", thFn: "Terlewat (FN)", thFp: "Alarm palsu (FP)",
    rows: {
      B0_majority: "Selalu “risiko rendah”",
      B1_clinical_rule: "Aturan klinis sederhana",
      M1_logreg_triage: "Regresi logistik (dipakai)",
      M2_random_forest_triage: "Random forest (tidak dipakai)",
    },
    caption: (t, c) => `Kelas risiko tinggi. Angka atas: data uji (n=${t.n}, ${t.n_high} risiko tinggi). ` +
      `CV: validasi silang pada data latih (n=${c.n}, ${c.n_high} risiko tinggi).`,
    findingsTitle: "Temuan utama",
    fLeak: (share, before, after) => `Kebocoran duplikat: ${share} baris uji di dataset mentah juga ada di ` +
      `data latih. Akurasi random forest ${before} dengan duplikat, ${after} setelah dibersihkan.`,
    fAges: (a, b, c) => `Kelompok usia (validasi silang), ibu berisiko tinggi yang tertangkap: ` +
      `${a} di bawah 20 tahun, ${b} usia 20–35, ${c} di atas 35.`,
    fSmall: (caught, n, lo) => `Sampel uji kecil: ${caught} dari ${n} ibu berisiko tinggi tertangkap, ` +
      `tetapi dengan hanya ${n} kasus, angka sebenarnya bisa serendah ${lo}.`,
    fExternal: "Uji pada dataset lain: dilewati karena waktu.",
    altConfusion: "Matriks kebingungan pada data uji: tindakan model dibanding label sebenarnya",
    altThreshold: "Kurva ambang: ibu berisiko tinggi yang tertangkap dan alarm palsu di tiap ambang rujukan",
    limitsTitle: "Keterbatasan",
    limits: (rows, refer, n) => [
      "Label adalah tingkat risiko yang ditetapkan, bukan hasil klinis nyata.",
      "Data dari pedesaan Bangladesh, bukan Indonesia.",
      `Sampel kecil setelah duplikat dihapus (${rows} baris).`,
      "Baris dengan tanda vital sama tetapi label berbeda dihapus, jadi hasil bisa sedikit terlalu optimis.",
      "Hanya enam tanda vital.",
      `Disetel agar jarang melewatkan risiko tinggi, jadi sering merujuk (${refer} dari ${n} pada validasi silang).`,
      "Bukan alat medis.",
    ],
    privacy: "Data tidak disimpan.",
    credits: "Data dan alat:",
    repoLink: "Lihat kode & laporan lengkap",
  },
  en: {
    tagline: "Helping village midwives decide referrals faster.",
    badge: "Prototype · Veritas AI Hackathon 2026",
    checkerTitle: "Check vitals",
    examples: "Examples (synthetic)",
    chips: { routine: "Routine", borderline: "Borderline", high: "High risk" },
    age: "Age", years: "years",
    bp: "Blood pressure", sbp: "Systolic", sbpHint: "top number", dbp: "Diastolic", dbpHint: "bottom number",
    sugar: "Blood sugar", sugarHint: "random blood sugar", switchUnit: "Switch blood sugar unit",
    temp: "Body temperature", pulse: "Pulse", pulseHint: "beats per minute",
    check: "Check", reset: "Reset",
    errRange: (lo, hi) => `Enter ${lo}–${hi}`,
    errBp: "Systolic must be higher than diastolic",
    resultTitle: "Result",
    empty: "Enter vitals to see the result",
    loadError: "The model failed to load. Check your connection, then reload.",
    reload: "Reload",
    action: {
      refer: ["Refer now", "Refer to puskesmas/hospital today"],
      recheck: ["Recheck in 1–2 days", "Recheck vitals in 1–2 days"],
      routine: ["Routine", "Continue routine antenatal visits"],
    },
    lineRefer2: (a, b) => `The combination of ${a} and ${b} points to high risk.`,
    lineRefer1: (a) => `The ${a} value points to high risk.`,
    lineRefer0: "The model rates this as high risk.",
    lineRecheck: "Not high risk yet, but the vitals need watching.",
    lineRoutine: "The vitals do not point to high risk.",
    probTitle: "Model estimate",
    classes: { low: "Low risk", mid: "Mid risk", high: "High risk" },
    whyTitle: "Why?",
    noFactors: "No strong risk factors",
    above: "above the training average", below: "below the training average",
    outOfRange: "outside common range",
    dangerTitle: "Danger sign",
    considerReferral: "Consider referral.",
    dangerNote: "This warning uses fixed clinical cutoffs, separate from the model.",
    disclaimer: "This project is a prototype and is not medical advice.",
    howTitle: "How it works",
    steps: [
      ["6 vital signs", "age, blood pressure, blood sugar, temperature, pulse"],
      ["AI model (logistic regression)", "runs on this phone, no internet needed"],
      ["Action", "Refer now, Recheck or Routine, with the reasons"],
    ],
    thApproach: "Approach", thRecall: "Caught", thFn: "Missed (FN)", thFp: "False alarms (FP)",
    rows: {
      B0_majority: "Always “low risk”",
      B1_clinical_rule: "Simple clinical rule",
      M1_logreg_triage: "Logistic regression (deployed)",
      M2_random_forest_triage: "Random forest (not deployed)",
    },
    caption: (t, c) => `High-risk class. Top number: test set (n=${t.n}, ${t.n_high} high risk). ` +
      `CV: cross-validation on the training set (n=${c.n}, ${c.n_high} high risk).`,
    findingsTitle: "Key findings",
    fLeak: (share, before, after) => `Duplicate leakage: ${share} of test rows in the raw dataset also appear ` +
      `in the training rows. Random forest accuracy is ${before} with duplicates, ${after} after cleaning.`,
    fAges: (a, b, c) => `Age groups (cross-validation), high-risk mothers caught: ` +
      `${a} under 20, ${b} aged 20–35, ${c} over 35.`,
    fSmall: (caught, n, lo) => `Small test sample: ${caught} of ${n} high-risk mothers were caught, ` +
      `but with only ${n} cases the true rate could be as low as ${lo}.`,
    fExternal: "Test on a separate dataset: skipped for time.",
    altConfusion: "Confusion matrix on the test set: the model's action against the true label",
    altThreshold: "Threshold curve: high-risk mothers caught and false alarms at each referral threshold",
    limitsTitle: "Limitations",
    limits: (rows, refer, n) => [
      "Labels are assigned risk levels, not real outcomes.",
      "Data from rural Bangladesh, not Indonesia.",
      `Small sample after removing duplicates (${rows} rows).`,
      "Rows with the same vitals but different labels were removed, so results may be slightly optimistic.",
      "Six vitals only.",
      `Tuned to rarely miss high risk, so it refers often (${refer} of ${n} in cross-validation).`,
      "Not a medical device.",
    ],
    privacy: "Nothing you enter is stored.",
    credits: "Data and tools:",
    repoLink: "See code and full write-up",
  },
};

// ---- the form: accepted range for each field (WEB-SPEC 4.2) ----------------
const FIELDS = [
  { id: "age", min: 10, max: 60 },
  { id: "sbp", min: 60, max: 200 },
  { id: "dbp", min: 40, max: 140 },
  { id: "sugar", min: 40, max: 500 }, // mg/dL; 2.2-27.8 when the unit is mmol/L
  { id: "temp", min: 34, max: 42 },
  { id: "pulse", min: 40, max: 160 },
];

// Usual ranges, used ONLY for the small amber dot in the result summary.
// The model does not use them. Age follows "4 Terlalu" (under 20 / over 35).
const COMMON = { age: [20, 35], sbp: [90, 139], dbp: [60, 89], sugar_mgdl: [70, 199], temp_c: [36, 37.9], pulse: [60, 100] };

const ICONS = { refer: "⚠", recheck: "↻", routine: "✓" };

// ---- page state (kept in memory only) --------------------------------------
let lang = "id";
let sugarUnit = "mgdl";   // or "mmol"
let model = null;         // model.json
let results = null;       // results.json
let loadFailed = false;
let lastInput = null;     // the vitals behind the result on screen
const touched = new Set(); // fields the bidan has left, so errors do not show too early

const $ = (id) => document.getElementById(id);
const round1 = (v) => Math.round(v * 10) / 10;
const pct = (v) => Math.round(v * 100) + "%";

// ---- form ------------------------------------------------------------------
function range(f) {
  return f.id === "sugar" && sugarUnit === "mmol" ? [2.2, 27.8] : [f.min, f.max];
}

// Number("") is 0 and Number("12abc") is NaN: both fail the range check below.
function readField(id) {
  return Number($(id).value.trim().replace(",", ".")); // accept "36,7" as well as "36.7"
}

function fieldError(f) {
  const v = readField(f.id);
  const [lo, hi] = range(f);
  return v >= lo && v <= hi ? "" : STR[lang].errRange(lo, hi);
}

// Shows messages and switches the Check button on only when everything is valid.
function validate(showAll = false) {
  let ok = true;
  for (const f of FIELDS) {
    const err = fieldError(f);
    if (err) ok = false;
    const show = err && (showAll || touched.has(f.id));
    $(f.id + "-err").textContent = show ? err : "";
    $(f.id).setAttribute("aria-invalid", show ? "true" : "false");
  }
  const [sbp, dbp] = [FIELDS[1], FIELDS[2]];
  const bpWrong = !fieldError(sbp) && !fieldError(dbp) && readField("sbp") <= readField("dbp");
  $("bp-err").textContent = bpWrong ? STR[lang].errBp : "";
  if (bpWrong) ok = false;
  $("check").disabled = !ok || !model;
  return ok;
}

function readInputs() {
  const sugar = readField("sugar");
  return {
    age: readField("age"), sbp: readField("sbp"), dbp: readField("dbp"),
    sugar_mgdl: sugarUnit === "mmol" ? sugar * MGDL_PER_MMOL : sugar,
    temp_c: readField("temp"), pulse: readField("pulse"),
  };
}

function fillExample(input) {
  sugarUnit = "mgdl"; // examples are written in mg/dL
  $("age").value = input.age;
  $("sbp").value = input.sbp;
  $("dbp").value = input.dbp;
  $("sugar").value = input.sugar_mgdl;
  $("temp").value = input.temp_c;
  $("pulse").value = input.pulse;
  FIELDS.forEach((f) => touched.add(f.id));
  renderStatic();
}

function toggleSugarUnit() {
  const v = readField("sugar");
  const toMmol = sugarUnit === "mgdl";
  sugarUnit = toMmol ? "mmol" : "mgdl";
  if (v > 0) $("sugar").value = toMmol ? round1(v / MGDL_PER_MMOL) : Math.round(v * MGDL_PER_MMOL);
  renderStatic();
  renderResult();
}

// ---- result card -----------------------------------------------------------
// A model feature -> the value and unit the bidan typed (not dataset units).
function shown(feature) {
  const S = STR[lang], i = lastInput;
  return {
    Age: [i.age, S.years],
    SystolicBP: [i.sbp, "mmHg"],
    DiastolicBP: [i.dbp, "mmHg"],
    BS: sugarUnit === "mmol" ? [round1(i.sugar_mgdl / MGDL_PER_MMOL), "mmol/L"] : [Math.round(i.sugar_mgdl), "mg/dL"],
    BodyTemp: [i.temp_c, "°C"],
    HeartRate: [i.pulse, "bpm"],
  }[feature];
}

// Danger cutoffs are stored in dataset units (mmol/L, Fahrenheit); show them in the bidan's units.
function cutoffShown(feature) {
  const c = model.danger_cutoffs[feature];
  if (feature === "BS") return sugarUnit === "mmol" ? c : Math.round(c * MGDL_PER_MMOL);
  if (feature === "BodyTemp") return round1(((c - 32) * 5) / 9);
  return c;
}

const label = (feature) => model.feature_labels[feature][lang];

function oneLine(action, reasons) {
  const S = STR[lang];
  if (action === "routine") return S.lineRoutine;
  if (action === "recheck") return S.lineRecheck;
  const names = reasons.map((r) => label(r.feature).toLowerCase());
  if (names.length >= 2) return S.lineRefer2(names[0], names[1]);
  return names.length ? S.lineRefer1(names[0]) : S.lineRefer0;
}

function summaryHtml() {
  const S = STR[lang], i = lastInput;
  const out = (key) => i[key] < COMMON[key][0] || i[key] > COMMON[key][1];
  const [sugar, sugarUnitText] = shown("BS");
  const items = [
    [`${i.age} ${S.years}`, out("age")],
    [`${i.sbp}/${i.dbp} mmHg`, out("sbp") || out("dbp")],
    [`${sugar} ${sugarUnitText}`, out("sugar_mgdl")],
    [`${i.temp_c} °C`, out("temp_c")],
    [`${i.pulse} bpm`, out("pulse")],
  ];
  const dot = `<span class="dot" role="img" aria-label="${S.outOfRange}"></span>`;
  const legend = items.some(([, flagged]) => flagged)
    ? `<p class="legend"><span class="dot" aria-hidden="true"></span> ${S.outOfRange}</p>` : "";
  return `<ul class="summary">${items.map(([text, flagged]) => `<li>${text}${flagged ? dot : ""}</li>`).join("")}</ul>${legend}`;
}

function renderResult() {
  const S = STR[lang], box = $("result-body");
  const disclaimer = `<p class="disclaimer">${S.disclaimer}</p>`;
  if (loadFailed) {
    box.innerHTML = `<p class="empty">${S.loadError}</p><button type="button" class="btn-primary" id="reload">${S.reload}</button>`;
    $("reload").onclick = () => location.reload();
    return;
  }
  if (!model || !lastInput) {
    box.innerHTML = `<p class="empty">${S.empty}</p>${disclaimer}`;
    return;
  }

  // The model runs here, through inference.js.
  const x = toModelUnits(lastInput);
  const proba = predict(model, x);          // [P(low), P(mid), P(high)]
  const action = decide(model, proba);      // "refer" | "recheck" | "routine"
  const reasons = explain(model, x);        // top 3 vitals that raised the risk
  const dangers = dangerSigns(model, x);    // single vitals past a fixed cutoff

  let html = "";
  if (dangers.length) {
    const lines = dangers.map((f) => {
      const [value, unit] = shown(f);
      return `<li>${label(f)} ${value} ${unit} ≥ ${cutoffShown(f)}</li>`;
    });
    html += `<div class="danger"><strong><span aria-hidden="true">⚠</span> ${S.dangerTitle}</strong>
      <ul>${lines.join("")}</ul>
      ${action !== "refer" ? `<p><strong>${S.considerReferral}</strong></p>` : ""}
      <p>${S.dangerNote}</p></div>`;
  }

  const [title, sub] = S.action[action];
  html += `<div class="banner ${action}"><span class="icon" aria-hidden="true">${ICONS[action]}</span>
    <div><strong>${title}</strong><span class="sub">${sub}</span></div></div>
    <p>${oneLine(action, reasons)}</p>${summaryHtml()}`;

  html += `<h3>${S.probTitle}</h3>` + model.classes.map((c, k) =>
    `<div class="bar-row"><span>${S.classes[c]}</span>
      <div class="track"><div class="fill ${c}" style="width:${pct(proba[k])}"></div></div>
      <span class="pct">${pct(proba[k])}</span></div>`).join("");

  // "Why?" only where it helps: for Rutin the top "reason" is usually just age.
  if (action !== "routine" && reasons.length) {
    html += `<h3>${S.whyTitle}</h3><ul class="reasons">` + reasons.map((r) => {
      const [value, unit] = shown(r.feature);
      const k = model.features.indexOf(r.feature);
      const isAbove = r.value > model.scaler.mean[k];
      return `<li>${label(r.feature)} ${value} ${unit} <span role="img" aria-label="${isAbove ? S.above : S.below}">${isAbove ? "↑" : "↓"}</span></li>`;
    }).join("") + "</ul>";
  } else {
    html += `<p>${S.noFactors}</p>`;
  }
  box.innerHTML = html + disclaimer;
}

// ---- how it works + limitations (numbers come from results.json) -----------
function renderHow() {
  if (!results) return;
  const S = STR[lang], r = results.results, e = results.experiments;
  const m1 = r.M1_logreg_triage;

  const steps = S.steps.map(([head, text]) => `<li><strong>${head}</strong><small>${text}</small></li>`).join("");
  const rows = Object.keys(S.rows).map((key) => {
    const t = r[key].test, c = r[key].cv;
    const cell = (a, b) => `<td>${a}<small>CV ${b}</small></td>`;
    return `<tr${key === results.deploy + "_logreg_triage" ? ' class="deployed"' : ""}><td>${S.rows[key]}</td>` +
      cell(pct(t.high_recall), pct(c.high_recall)) + cell(t.high_fn, c.high_fn) + cell(t.high_fp, c.high_fp) + "</tr>";
  }).join("");

  const leak = e.E1_duplicate_leakage, forest = leak.models.M2_random_forest;
  const ages = e.E2_age_groups.cv;
  const caught = (g) => `${g.n_high - g.high_fn}/${g.n_high}`;
  const findings = [
    S.fLeak(pct(leak.raw_test_share_also_in_train), pct(forest.with_duplicates_holdout.accuracy), pct(forest.after_cleaning_holdout.accuracy)),
    S.fAges(caught(ages["<20"]), caught(ages["20-35"]), caught(ages[">35"])),
    S.fSmall(m1.test.n_high - m1.test.high_fn, m1.test.n_high, pct(m1.test.high_recall_wilson95[0])),
    S.fExternal,
  ];

  $("how-body").innerHTML = `<ol class="steps">${steps}</ol>
    <div class="table-wrap"><table>
      <caption>${S.caption(m1.test, m1.cv)}</caption>
      <thead><tr><th>${S.thApproach}</th><th>${S.thRecall}</th><th>${S.thFn}</th><th>${S.thFp}</th></tr></thead>
      <tbody>${rows}</tbody></table></div>
    <h3>${S.findingsTitle}</h3><ul>${findings.map((f) => `<li>${f}</li>`).join("")}</ul>
    <div class="plots">
      <figure><img src="img/confusion_m1_triage.png" loading="lazy" alt="${S.altConfusion}"><figcaption>${S.altConfusion}</figcaption></figure>
      <figure><img src="img/threshold_curve.png" loading="lazy" alt="${S.altThreshold}"><figcaption>${S.altThreshold}</figcaption></figure>
    </div>`;

  const cv = m1.cv;
  $("limits-list").innerHTML = S.limits(results.data.clean_rows, cv.actions.refer, cv.n).map((t) => `<li>${t}</li>`).join("");
}

// ---- language + static text ------------------------------------------------
function renderStatic() {
  const S = STR[lang];
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = S[node.dataset.i18n]; });
  document.querySelectorAll("[data-lang]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === lang)));
  $("sugar-unit").textContent = (sugarUnit === "mmol" ? "mmol/L" : "mg/dL") + " ⇄";
  $("sugar-unit").setAttribute("aria-label", S.switchUnit);
  if (model) {
    $("chips").innerHTML = model.examples.map((ex, k) => `<button type="button" class="chip" data-example="${k}">${S.chips[ex.id]}</button>`).join("");
  }
  validate();
}

function renderAll() {
  renderStatic();
  renderResult();
  renderHow();
}

// ---- start -----------------------------------------------------------------
async function loadModel() {
  try {
    const load = (url) => fetch(url).then((res) => {
      if (!res.ok) throw new Error(url);
      return res.json();
    });
    [model, results] = await Promise.all([load("model.json"), load("results.json")]);
  } catch {
    loadFailed = true;
  }
  renderAll();
}

$("form").addEventListener("input", () => validate());
$("form").addEventListener("focusout", (event) => {
  if (event.target.tagName === "INPUT") { touched.add(event.target.id); validate(); }
});
$("form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (!validate(true)) return;
  lastInput = readInputs();
  renderResult();
  $("result").scrollIntoView({ block: "nearest" }); // on a phone the result sits below the form
});
$("reset").addEventListener("click", () => {
  $("form").reset();
  touched.clear();
  lastInput = null;
  renderStatic();
  renderResult();
});
$("chips").addEventListener("click", (event) => {
  const k = event.target.dataset.example;
  if (k !== undefined) fillExample(model.examples[k].input);
});
$("sugar-unit").addEventListener("click", toggleSugarUnit);
document.querySelector(".lang").addEventListener("click", (event) => {
  if (!event.target.dataset.lang) return;
  lang = event.target.dataset.lang;
  renderAll(); // redraws everything, including a result already on screen
});

$("how").open = window.matchMedia("(min-width: 768px)").matches; // open by default on desktop
renderAll();
loadModel();

// Offline: the service worker keeps a copy of the site's own files.
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
