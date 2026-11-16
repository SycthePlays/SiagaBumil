# WEB-SPEC.md — SigapBumil web app

Static site in `web/`, deployed by GitHub Pages. Plain HTML/CSS/JS, no framework, no build step, no backend.
**Claude Code: read this whole file before starting Phase 5.** The website is the showcase — it must look calm, trustworthy and finished, but the AI pipeline (Phases 1–4) comes first. Cap Phase 5 at ~3.5 h.

---

## 1. Principles

- **Mobile-first** — the bidan uses a phone. Design at 360 px width first, then scale up.
- **English default, Indonesian toggle** (changed Mon Nov 16: judges read English; the bidan can switch to Indonesian in one tap). Toggle order **EN | ID**. The choice lasts only while the page is open; it is not saved. All text bilingual via one dictionary object in `app.js` (`STR.id`, `STR.en`). No hard-coded UI strings in HTML.
- **Offline after first load**: all logic + `model.json` local; a tiny service worker (`sw.js`) caches the site files. System font stack — no web fonts, no CDN.
- **Privacy**: no storage of inputs, no cookies, no analytics, no network requests except the site's own files. Say so in the footer: *"Data tidak disimpan / Nothing you enter is stored."*
- **Disclaimer on every result**: *"Prototipe, bukan nasihat medis. / This project is a prototype and is not medical advice."*
- **Never rely on colour alone**: every action state has colour + icon + text.

---

## 2. Visual identity

**Mood:** calm clinical tool, not a flashy startup page. Think "printed health card from the puskesmas, made digital": clean, warm, readable in sunlight.

**Name / wordmark:** "Sigap**Bumil**" — "Sigap" in text colour, "Bumil" in primary colour, bold. Small heart-pulse line icon (inline SVG) before it.

**Colour tokens** (define on `:root` in `style.css`; use tokens only, no raw hex elsewhere):

| Token | Light | Use |
|---|---|---|
| `--bg` | `#FAFAF7` | page background (warm off-white) |
| `--surface` | `#FFFFFF` | cards |
| `--text` | `#1C1917` | body text |
| `--muted` | `#57534E` | labels, hints |
| `--border` | `#E7E5E4` | card + input borders |
| `--primary` | `#0F766E` | brand teal: buttons, links, focus ring |
| `--primary-soft` | `#CCFBF1` | selected toggles, chips |
| `--refer` / `--refer-bg` | `#B91C1C` / `#FEF2F2` | Rujuk sekarang |
| `--recheck` / `--recheck-bg` | `#B45309` / `#FFFBEB` | Cek ulang |
| `--routine` / `--routine-bg` | `#15803D` / `#F0FDF4` | Rutin |

Dark mode (`@media (prefers-color-scheme: dark)`) was optional — **cut**.

**Typography:** system stack (`system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`).
- Body 16 px / 1.5. Labels 14 px muted. Section titles 20 px semibold.
- Result action text **28 px bold** (must be readable at arm's length).
- Numbers in inputs: `font-variant-numeric: tabular-nums`.

**Shape & spacing:** 8 px spacing scale (8/16/24/32). Cards `border-radius: 16px`, 1 px border, very soft shadow. Inputs and buttons ≥ 48 px tall. Page side padding 16 px on mobile.

---

## 3. Layout

- **Mobile (< 768 px):** single column, max-width 480 px, centred: header → checker card → result card (appears below, auto-scrolls into view) → how it works → limitations → footer.
- **Desktop (≥ 768 px):** max-width 1040 px; checker card (left, ~45%) and result card (right, sticky) side by side; sections below span full width.
- No horizontal scroll at 360 px. Test at 360, 768, 1280.

---

## 4. Page sections

### 4.1 Header
- Wordmark + tagline: *"Bantu bidan memutuskan rujukan lebih cepat"* / *"Helping village midwives decide referrals faster."*
- Language toggle **EN | ID**, English selected on first load (segmented control, top-right). Switching language re-renders all text, including an existing result.
- Small badge: *"Prototipe · Veritas AI Hackathon 2026"*.

### 4.2 Checker card (main)
Inputs — numeric fields (`inputmode="decimal"`), label above, unit as a suffix inside the field, hint text below:

| Field | Unit | Accepted range | Hint |
|---|---|---|---|
| Usia / Age | tahun / years | 10–60 | |
| Tekanan darah sistolik / Systolic BP | mmHg | 60–200 | angka atas / top number |
| Tekanan darah diastolik / Diastolic BP | mmHg | 40–140 | angka bawah / bottom number |
| Gula darah / Blood sugar | **mg/dL** (toggle → mmol/L) | 40–500 mg/dL (2.2–27.8 mmol/L) | gula darah sewaktu / random |
| Suhu tubuh / Body temperature | **°C** | 34–42 | |
| Nadi / Pulse | bpm | 40–160 | denyut per menit / per minute |

- Systolic + diastolic sit side by side as one "Tekanan darah / Blood pressure" group (`120 / 80`), stacked on very narrow screens.
- **Validation:** on blur and on submit; inline red message under the field (e.g. *"Isi antara 60–200 / Enter 60–200"*); SBP must be > DBP. Check button disabled until all valid.
- **Example chips** (labelled *"Contoh (data sintetis) / Examples (synthetic)"*): **Rutin**, **Borderline**, **Berisiko tinggi**. Tapping fills the form; does not auto-submit.
- Buttons: primary **"Periksa / Check"** (full width on mobile); secondary text button **"Reset"**.

### 4.3 Result card
States:
1. **Empty** (before first check): soft illustration-free placeholder — *"Masukkan tanda vital untuk melihat hasil / Enter vitals to see the result"*.
2. **Result:**
   - **Action banner** (tinted background, left colour bar, icon + 28 px text):
     - ⚠ **Rujuk sekarang** — *Refer to puskesmas/hospital today* (`--refer`)
     - ↻ **Cek ulang 1–2 hari** — *Recheck vitals in 1–2 days* (`--recheck`)
     - ✓ **Rutin** — *Continue routine antenatal visits* (`--routine`)
   - One-line plain explanation under the banner (e.g. *"Kombinasi tekanan darah dan gula darah menunjukkan risiko tinggi."*).
   - **Probability bars**: three horizontal bars Low / Mid / High with % labels (bars animate width on render; respect `prefers-reduced-motion`).
   - **"Mengapa? / Why?"**: top 3 reasons as a list, each with the patient's value and a small arrow ↑ (e.g. *"Tekanan darah sistolik 150 mmHg ↑"*).
   - Inputs outside common ranges highlighted with a small amber dot in the summary, with the label *"Rentang umum, bukan diagnosis / Common range, not a diagnosis"*.
   - Disclaimer line (muted, 13 px) — always visible on the card.
   - **"Tanda bahaya / Danger sign" warning** (added Phase 4) — a separate box above the action banner, shown when **any single vital** passes a fixed cutoff, **independent of the model**:
     - Systolic BP ≥ 140 mmHg · Diastolic BP ≥ 90 mmHg · Temperature ≥ 38 °C · Blood sugar ≥ 200 mg/dL
     - Why: the model is linear and can let several normal values outweigh one very abnormal one (seen in CV: BP 120/95 was not referred). The warning makes sure one dangerous number is never hidden.
     - Cutoffs are read from `model.json.danger_cutoffs` (dataset units: mmol/L, °F; same as baseline B1) via `dangerSigns()` in `inference.js`. Show them in the bidan's units.
     - Style: `--refer` colour + ⚠ icon + text; lists each vital that passed, with its value (e.g. *"Tekanan darah diastolik 95 mmHg ≥ 90"*). It does **not** change the model's action or probabilities; when the action is not "Rujuk sekarang", add the line *"Pertimbangkan rujukan / Consider referral"*.
   - **"Mengapa? / Why?" is shown only for Rujuk and Cek ulang.** For Rutin the list is replaced by the text *"Tidak ada faktor risiko menonjol / No strong risk factors"* (the "top reason" for a healthy 25-year-old would be her age, which is confusing).
3. **Error** (model failed to load): friendly message + "Muat ulang / Reload" button.

Result region has `aria-live="polite"` so screen readers announce it.

### 4.4 How it works (collapsible `<details>`, open by default on desktop)
- **3-step diagram** (inline SVG or simple flex cards): *6 tanda vital → model AI (regresi logistik) → tindakan*.
- **Results table** from `web/results.json` (copied from `results/summary.json` in `07_export.py`): B0 majority, B1 clinical rule, LR (deployed), tree model — high-risk recall, missed cases (FN), false alarms (FP). Highlight the deployed row.
- **Key findings**, one sentence + one number each: duplicate leakage, age groups, external dataset (or "skipped because…").
- Images copied from `results/` into `web/img/`: confusion matrix, threshold curve. `loading="lazy"`, alt text.
- Link: *"Lihat kode & laporan lengkap / See code and full write-up"* → GitHub repo.

### 4.5 Closing cards (replaces the single Limitations card, Mon Nov 16)
Four cards, in this order, numbers read from `results.json`: (1) **Limits (reported as they are)**: each limit with its consequence; (2) **Benefits and next steps**: who it helps, the "complements Buku KIA" line, numbered next steps; (3) **Use of AI**; (4) **Data sources** with links (UCI, WHO 2011, WHO 2013, Buku KIA, UNFPA).

Original short list, for reference: labels are assigned risk not outcomes · data from rural Bangladesh, not Indonesia · small sample after removing duplicates · six vitals only · tuned to catch high risk, so more false alarms · not a medical device.

### 4.6 Footer
Credits (UCI dataset with link, scikit-learn, Claude / Claude Code), GitHub link, privacy line, disclaimer.

---

## 5. Logic in `app.js`

```
loadModel()     fetch('model.json') + fetch('results.json') once; show error state on failure
readInputs() → validate()
toModelUnits()  mg/dL→mmol/L (÷18.016) unless mmol/L toggle; °C→°F (×9/5+32)
addFeatures()   PulsePressure = SBP−DBP; MAP = DBP + (SBP−DBP)/3   (only those listed in model.json.features)
predict()       z=(x−mean)/scale; logits=coef·z+intercept; softmax (subtract max first)
decide()        thresholds from model.json (DESIGN.md §6)
explain()       top 3 positive w_high,k × z_k → labels from model.json.feature_labels[lang]
render()        result card; re-render on language toggle
```

- **Phase 4 update:** the model math lives in `web/inference.js` (already written and parity-tested); `app.js` loads it with `<script type="module">` and only does UI. The model uses the **6 raw vitals** (engineered features were dropped in CV). Example chips come from `model.json.examples`; the "Borderline" chip gives **Rujuk sekarang** with no danger sign (the combination, not one number, is risky).
- Feature order always taken from `model.json.features` — never hard-coded.
- Same math as Python; verified by `tests/test_parity.mjs` against `test_cases.json`.
- Keep `app.js` readable: small named functions, comments explaining *why* (the developer must explain it to judges).

---

## 6. Files

```
web/
├── index.html     # semantic HTML: header, main (checker + result), sections, footer
├── style.css      # tokens on :root, mobile-first, one breakpoint at 768px
├── app.js         # UI: form, validation, render + STR dictionary (id/en); imports inference.js
├── inference.js   # model math only (toModelUnits, predict, decide, explain, dangerSigns); ES module,
│                  #   the same file is tested against Python by tests/test_parity.mjs
├── sw.js          # service worker: cache-first for site files (offline); refreshes the copy in the background
├── model.json     # from pipeline/07_export.py
├── results.json   # from pipeline/07_export.py (copy of results/summary.json)
├── test_cases.json
└── img/           # confusion matrix, threshold curve, favicon (SVG)
```

---

## 7. Accessibility checklist

- Every input has a visible `<label>`; errors linked with `aria-describedby`.
- Visible focus ring (`--primary`, 2 px) on all interactive elements.
- Contrast ≥ 4.5:1 for text (the tokens above meet this on their backgrounds).
- Tap targets ≥ 44 px. Works with keyboard only (Enter submits).
- `lang` attribute on `<html>` switches between `id` and `en`.

---

## 8. Deploy

- `.github/workflows/pages.yml`: on push to `main`, upload `web/` as the Pages artifact and deploy (`actions/upload-pages-artifact` + `actions/deploy-pages`).
- Repo Settings → Pages → Source: **GitHub Actions**.

## 9. Acceptance checklist (Phase 5 done when all pass)

- [ ] Opens from the public URL in an incognito window.
- [ ] Works on a real phone at 360 px; no horizontal scroll.
- [ ] Each example chip gives the expected action (matches Python on the same input).
- [ ] Invalid inputs blocked with clear messages; SBP ≤ DBP rejected.
- [ ] ID ↔ EN toggle changes every string, including an existing result.
- [ ] Reload in airplane mode after first visit still works (service worker).
- [ ] Disclaimer visible on every result; no network calls besides own files (check DevTools → Network).
- [ ] Lighthouse (mobile): Accessibility ≥ 90.
