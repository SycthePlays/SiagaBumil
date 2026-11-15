# WEB-SPEC.md — SigapBumil web app

Static site in `web/`, deployed by GitHub Pages. Plain HTML/CSS/JS, no framework, no build step, no backend.

---

## 1. Principles

- **Mobile-first** — the bidan uses a phone. Test at 360 px width.
- **Bahasa Indonesia default**, English toggle (judges read English). All labels bilingual via a small dictionary in `app.js`.
- **Offline after first load**: all logic + `model.json` local. No CDN fonts required (system font stack is fine).
- **Privacy**: no storage of inputs, no cookies, no analytics, no network requests except loading the site's own files.
- **Disclaimer on every result**: *"Prototipe, bukan nasihat medis. / This project is a prototype and is not medical advice."*

---

## 2. Page sections (single page)

1. **Header** — logo wordmark "SigapBumil", one-line tagline: *"Bantu bidan memutuskan rujukan lebih cepat"* / *"Helping village midwives decide referrals faster."* Language toggle ID | EN.
2. **Checker (main)**
   - Inputs (number fields, with unit labels and sane ranges):
     | Field | Unit | Range accepted |
     |---|---|---|
     | Usia / Age | tahun / years | 10–60 |
     | Tekanan darah sistolik / Systolic BP | mmHg | 60–200 |
     | Tekanan darah diastolik / Diastolic BP | mmHg | 40–140 |
     | Gula darah / Blood sugar | **mg/dL** (toggle mmol/L) | 40–500 mg/dL |
     | Suhu tubuh / Body temperature | **°C** | 34–42 |
     | Nadi / Pulse | bpm | 40–160 |
   - Validation: inline message if out of range or SBP ≤ DBP; button disabled until valid.
   - Example buttons (**synthetic**, labelled "Contoh / Example"): *Rutin*, *Borderline*, *Berisiko tinggi*.
   - Button: **"Periksa / Check"**.
3. **Result card**
   - Big action: 🟥 **Rujuk sekarang** (Refer now) / 🟨 **Cek ulang 1–2 hari** (Recheck in 1–2 days) / 🟩 **Rutin** (Routine visit).
   - Probability bars: low / mid / high.
   - "Mengapa? / Why?" — top 3 reasons from the explanation (e.g. "Tekanan darah sistolik tinggi").
   - Values flagged outside common ranges are highlighted.
   - Disclaimer line.
4. **How it works** (collapsible, for judges)
   - 3-step graphic: vitals → model → action.
   - Results table: B0, B1 rule, LR, tree model — high-risk recall, missed cases, false alarms (numbers read from `model.json.metrics` / static text generated from `results/summary.json`).
   - Key findings: duplicate leakage, age groups, external test — one sentence each.
   - Images from `results/` (confusion matrix, threshold curve) copied into `web/img/`.
5. **Limitations** — labels are assigned risk not outcomes; Bangladesh data; small sample; not a medical device.
6. **Footer** — credits (UCI dataset, scikit-learn, Claude / Claude Code), GitHub link, disclaimer.

---

## 3. Logic in `app.js`

```
readInputs() → validate()
toModelUnits(): mg/dL→mmol/L (÷18.016), °C→°F (×9/5+32)
addFeatures(): PulsePressure, MAP
predict(): z=(x−mean)/scale; logits=coef·z+intercept; softmax
decide(): thresholds from model.json (see DESIGN.md §6)
explain(): top 3 positive w_high,k × z_k → labels from model.json.feature_labels
render()
```

- `model.json` loaded once with `fetch('model.json')`.
- Same math as Python; verified by `tests/test_parity.mjs` against `test_cases.json`.

---

## 4. Look and feel

- Clean, calm, clinical: white/off-white background, one accent (teal/deep green), red/amber/green only for the action card.
- Large tap targets (≥44 px), large result text, high contrast.
- Respect `prefers-color-scheme` (dark mode) if time allows — optional.

---

## 5. Deploy

- `.github/workflows/pages.yml`: on push to `main`, upload `web/` as the Pages artifact and deploy (actions/upload-pages-artifact + actions/deploy-pages).
- Repo Settings → Pages → Source: **GitHub Actions**.
- After deploy: open the URL in an incognito window and on a phone; check offline reload (airplane mode after first load).
