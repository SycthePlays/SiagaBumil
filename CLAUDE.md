# SigapBumil — CLAUDE.md

> **Scope cuts in `HANDOFF.md` override this and other docs** (E3 external dataset, tree grid search, Hugging Face fallback and dark mode are all cut).

Project brief for Claude Code. **Read this file first, then `HANDOFF.md` (current status), then `PLAN.md` (what to do next).** Detailed specs live in the other docs (see §8).

---

## 1. One-liner

**SigapBumil** ("sigap" = alert/ready, "bumil" = *ibu hamil*, pregnant woman) is a maternal risk triage prototype for Indonesian village midwives (*bidan desa*). It takes six vital signs a bidan already measures at an antenatal visit and returns **Rujuk sekarang / Cek ulang / Rutin** (Refer now / Recheck / Routine), tuned to rarely miss a high-risk mother, with the reasons behind each result.

> This project is a prototype and is not medical advice.

---

## 2. Hackathon context

- **Event:** Veritas AI International High School Hackathon 2026 — **AI + Health track**. Solo entry.
- **Deadline:** Sun Nov 15, 11:59 PM ET = **Mon Nov 16, 11:59 WIB**. Hard internal stop: **11:30 WIB**.
- **Submission:** public GitHub repo (code + results visible), one-page write-up (`README.md`), optional ≤2-min demo video, credits for every dataset, model, library and AI tool (including Claude / Claude Code).
  - The brief accepts **Colab OR GitHub** for code, and allows the **GitHub README as the write-up** → the public repo link covers both required items.
  - **Colab is optional**: one walkthrough notebook (`notebooks/walkthrough.ipynb`, outputs saved) is added at the end as a one-click extra for judges.
  - The website is **not required** — it is the showcase (clarity + impact). The AI pipeline + evaluation is the project (technical quality). Build in that order.
- **Rules that shape this project:**
  - AI/ML must do the main job, not just decorate a website.
  - All work done during the hackathon weekend.
  - Public or synthetic data only. **No real patient records, ever.**
  - Report honest results, including weak ones.
  - Health track must report **missed cases (false negatives) and false alarms (false positives) separately**, name the user, and include the disclaimer line above.
- **Every project must answer:** who is it for · what goes in / what comes out · does it beat a simple baseline · where does it fail.
- **Judging:** technical quality, impact, creativity, clarity. Projects are compared on what they *add*: own user, own data, own question, and how fairly they test. An honest modest result beats an unexplained high one.

---

## 3. Background — the problem

- Indonesia's maternal mortality ratio was **189 deaths per 100,000 live births** (2020 Population Census, via UNFPA Indonesia), substantially higher than other Southeast Asian countries.
- In villages the first line of antenatal care is the **bidan desa**: one midwife, many pregnant women, basic tools (BP cuff, glucometer, thermometer).
- **Measuring is not the gap. Interpreting is.** The bidan sees six numbers; each may look borderline on its own, but the *combination* can signal danger (e.g. BP 135/88 + raised blood sugar + age 37 + fast pulse). Single-number rules miss this.
- The costly error is a **missed high-risk mother** (false negative) who is not referred in time. A false alarm costs a trip to the puskesmas; a miss can cost a life.
- Indonesia's "4 Terlalu" maternal-health message flags pregnancies that are *too young* (<20) or *too old* (>35) — we check the model separately for these age groups.

---

## 4. User and moment

- **User:** a bidan desa during a routine antenatal visit, on her phone, possibly with weak internet.
- **Moment:** vitals have just been measured; she must decide **today** whether to refer the mother to the puskesmas/hospital, ask her to come back for a recheck, or continue routine care.
- **Design consequences:** mobile-first, Bahasa Indonesia first (English toggle), Indonesian units (blood sugar in **mg/dL**, temperature in **°C**), works offline, stores nothing.

---

## 5. What we are trying to find (research questions)

| # | Question | Why judges care |
|---|---|---|
| RQ1 | Does ML beat (a) "always low risk" and (b) a simple clinical-threshold rule at catching high-risk mothers? | Baseline comparison is mandatory |
| RQ2 | How much do **duplicate rows** in the public dataset inflate reported accuracy? | Leakage catch = technical quality + honesty |
| RQ3 — **cut** (skipped for time) | Does the frozen model hold up on a **different dataset** collected separately? | "Own data / new situation" |
| RQ4 | Does high-risk recall differ for mothers **<20, 20–35, >35**? | Track asks for equal performance across groups |
| RQ5 | Which vitals drive each prediction, and where does the model fail? | Explainability + required failure analysis |

---

## 6. Solution overview

**Data at a glance** (details in `DATA.md`):

| Stage | Data | Model learns from it? |
|---|---|---|
| Training | UCI Maternal Health Risk, deduped, **80% train split** (CV + threshold tuning inside it) | **Yes** — the only training data |
| Testing | UCI 20% held-out test (once) · Mendeley external dataset (**cut**) · UCI raw-with-duplicates (leakage experiment only) | No |
| Detection (live app) | 6 vitals typed by the bidan, converted in the browser · synthetic demo examples | No — frozen model, nothing stored |

```
INPUT (bidan form, Indonesian units)
  age · systolic BP · diastolic BP · blood sugar (mg/dL) · temperature (°C) · pulse
        │  convert: mg/dL → mmol/L (÷ 18.016), °C → °F (× 9/5 + 32)  [dataset units]
        ▼
FEATURES  Age, SystolicBP, DiastolicBP, BS, BodyTemp, HeartRate
          + PulsePressure = SBP − DBP
          + MAP = DBP + (SBP − DBP) / 3
        ▼
MODEL     Standardize → multinomial Logistic Regression (deployed)
          compared against: B0 majority class, B1 clinical rule, M2 tree ensemble
        ▼
DECISION  P(high) ≥ t_refer                → "Rujuk sekarang" (red)
          else predicted mid / P(mid+high) ≥ t_recheck → "Cek ulang 1–2 hari" (amber)
          else                              → "Rutin" (green)
          thresholds tuned on cross-validation for high-risk recall ≥ ~0.90
        ▼
EXPLAIN   per-feature contribution to the "high" logit (coef × standardized value)
          → top 3 reasons shown in plain language
        ▼
OUTPUT    action card + class probabilities + top reasons + disclaimer
```

Full model spec: `DESIGN.md`. Data decisions: `DATA.md`. UI spec: `WEB-SPEC.md`.

**Deployment:** static website in `web/` served by **GitHub Pages**. The trained model is exported to `web/model.json` (scaler + coefficients + thresholds) and **inference runs in the browser in plain JavaScript** — no server, no database, no network calls, works offline after first load. *(Fallback if the web build fails: Gradio app on Hugging Face Spaces — **cut**.)* No Vercel, no Supabase.

---

## 7. Repo structure

```
sigapbumil/
├── CLAUDE.md            # this file — project brief + rules for Claude Code
├── README.md            # public write-up (hackathon template) — final deliverable
├── PLAN.md              # phases, timeline, checklists
├── DESIGN.md            # AI/ML design: features, baselines, models, metrics, export
├── DATA.md              # datasets, roles, licences, cleaning log
├── WEB-SPEC.md          # web app spec (UI, units, states, privacy)
├── HANDOFF.md           # session log: done / next / open issues / judge-ready explanations
├── SETUP.md             # tooling: VS Code + Claude Code, GitHub, Pages, Colab, Hugging Face (fallback — cut)
├── requirements.txt     # pinned versions
├── data/
│   ├── raw/             # original files, untouched (UCI CSV committed with attribution)
│   └── processed/       # deduped data, train/test split files
├── models/
│   └── sigapbumil_lr.joblib # sklearn copy of the trained model (committed)
├── notebooks/
│   └── walkthrough.ipynb    # Colab walkthrough: clone repo → load trained model → predict → show results (outputs saved)
├── pipeline/            # numbered scripts, run in order
│   ├── 01_load_clean.py     # load, inspect, count + drop duplicates, sanity checks
│   ├── 02_split.py          # stratified 80/20 split → data/processed (test locked)
│   ├── 03_baselines.py      # B0 majority, B1 clinical rule (CV on train)
│   ├── 04_models.py         # LR + tree model (grid search: cut), 5-fold CV, threshold tuning
│   ├── 05_final_eval.py     # ONLY script that touches the test set; run once
│   ├── 06_experiments.py    # duplicate-leakage test, age groups, external dataset (cut)
│   ├── 07_export.py         # write web/model.json + web/test_cases.json
│   └── run_all.py
├── results/             # metrics *.json + plots *.png (all README numbers come from here)
├── web/                 # static site for GitHub Pages
│   ├── index.html
│   ├── style.css
│   ├── app.js           # unit conversion, inference, decision, explanation, UI
│   ├── sw.js            # service worker (offline cache)
│   ├── model.json       # exported model
│   ├── results.json     # copy of results/summary.json for the "How it works" section
│   ├── test_cases.json  # cases with Python-computed expected outputs
│   └── img/             # result plots copied from results/, favicon
├── tests/
│   ├── test_no_leak.py      # no test row appears in train
│   ├── test_units.py        # mg/dL↔mmol/L, °C↔°F
│   └── test_parity.mjs      # JS inference == Python inference on test_cases.json
└── .github/workflows/pages.yml   # deploy web/ to GitHub Pages
```

---

## 8. Docs map — keep these updated

| File | Owner of… | Update when |
|---|---|---|
| `HANDOFF.md` | current status, next step, open issues | **end of every session / phase** |
| `PLAN.md` | phase checklist + timeline | tick boxes as phases finish |
| `DESIGN.md` | model decisions and why | any modelling decision changes |
| `DATA.md` | dataset facts, cleaning log | any data decision |
| `WEB-SPEC.md` | UI behaviour | UI changes |
| `README.md` | public write-up | Phase 6 (filled from `results/`) |
| `SETUP.md` | tool connections and accounts | setup changes |

---

## 9. Stack and commands

- **Python 3.10+**: pandas, numpy, scikit-learn, matplotlib, ucimlrepo, joblib, pytest (see `requirements.txt`). Do not add dependencies without asking.
- In Phase 0, **pin exact versions** in `requirements.txt` from the local environment (`pip freeze` for these packages) so the committed joblib model and the Colab notebook behave the same everywhere.
- **Web**: plain HTML/CSS/JS, no framework, no build step. Node only for `tests/test_parity.mjs`.

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python pipeline/run_all.py          # runs 01→07 (05 runs final eval once)
pytest -q                           # python tests
node tests/test_parity.mjs          # JS vs Python parity
python -m http.server -d web 8000   # preview site at http://localhost:8000
```

---

## 10. Non-negotiable rules

1. **Test set is touched once**, only in `05_final_eval.py`. All model choice and threshold tuning uses cross-validation on the training set. Never re-tune after seeing test results; if something changes, say so in `HANDOFF.md` and `README.md`.
2. **Deduplicate before splitting.** Exact duplicate rows go; conflicting duplicates (same vitals, different label) are counted and reported.
3. `random_state=42` everywhere. Scripts must be re-runnable and deterministic.
4. **Every number in `README.md` must come from a file in `results/`** produced by the pipeline. No hand-typed metrics.
5. Always report **false negatives and false positives for the high-risk class separately**, plus per-class recall, next to the baselines.
6. Report weak or negative findings plainly (e.g. "ML barely beats the rule", "performance drops on the external dataset").
7. **No real patient data. No storage, analytics, cookies or network calls in the web app.** Demo examples are synthetic and labelled as such.
8. The disclaimer line *"This project is a prototype and is not medical advice."* appears in `README.md` and on every result screen of the web app.
9. Keep code simple and commented with the *why*. The developer is a beginner and must explain every part to judges.
10. Do not build backends, databases, auth, Vercel or Supabase integrations.
11. Credit every dataset, library and AI tool (Claude, Claude Code) in `README.md` → Sources.
12. Commit after each phase with a clear message.
13. **The repo is public: never write API keys, tokens or passwords into any file, notebook or commit.** Use GitHub Secrets or the git password prompt only.
14. **Everything needed to reproduce lives in the repo** (UCI CSV, `web/model.json`, `models/*.joblib`, `results/`). Colab must work from a fresh runtime via `git clone` — no manual uploads.
15. **Priority:** pipeline + evaluation first (Phases 1–4), website second (Phase 5, capped ~3.5 h), polish last.

---

## 11. Working style with the developer

- Developer: solo high-school student, beginner in ML, communicates in English/Indonesian. Prefers terse, direct answers.
- Work **one phase at a time** (see `PLAN.md`). At the end of each phase:
  1. show the key results (table/plot paths),
  2. write 3–5 bullet **"How to explain this to judges"** notes into `HANDOFF.md`,
  3. update `HANDOFF.md` → Done / Next / Open issues,
  4. commit — **with approval**: at the end of every phase show `git status`, a short change summary and a proposed commit message, then WAIT for the developer's "ya"/"ok" before committing and pushing. Never push without approval.
- **Before Phase 5, read `WEB-SPEC.md` in full** and follow its design tokens, layout, states and acceptance checklist. Don't invent a different visual style.
- If a step blocks for more than ~30 minutes (e.g. a dataset won't load), stop and propose the fallback in `PLAN.md` instead of pushing on.
- Ask before any irreversible or scope-changing action.

---

## 12. Definition of done

- [ ] Pipeline runs end to end from a clean clone; tests pass.
- [ ] `results/` contains: baseline vs model table, confusion matrices, threshold plot, duplicate-leakage comparison, age-group table, external-test result (**cut**), failure cases.
- [ ] Web app live on GitHub Pages, works on a phone, offline after first load, disclaimer visible.
- [ ] JS and Python give the same predictions on `test_cases.json`.
- [ ] `notebooks/walkthrough.ipynb` runs from a fresh Colab runtime and is saved with outputs visible.
- [ ] `README.md` follows the hackathon template, all numbers from `results/`, limitations and sources complete.
- [ ] Demo video (≤2 min) uploaded unlisted; all links open in an incognito window.
