# DATA.md — datasets, roles, cleaning log

Public data only. No real patient records from anyone we know, any clinic, school or family.

---

## 1. What one row means

One pregnant woman at one antenatal checkup → 6 vitals (features) + an assigned risk level (label).
Features must be things a **bidan desa can measure in a village**: age, BP cuff, glucometer, thermometer, pulse.

---

## 2. Training vs testing vs detection

| Stage | Data | Model learns from it? |
|---|---|---|
| **Training** | UCI Maternal Health Risk, deduped, **80% train split**. CV, model choice and threshold tuning all happen inside it | **Yes — the only training data** |
| **Testing** | UCI 20% held-out test (run once) | No |
| | Mendeley Mojumdar et al. 2024 — external check, shared features only, high vs not-high (run once, if usable) | No |
| | UCI raw with duplicates — leakage experiment E1 only | No |
| **Detection (live app)** | 6 vitals typed by the bidan (mg/dL, °C → converted in browser) | No — frozen model, inputs never stored |
| | Synthetic demo examples, labelled "Contoh / Example" | No — demo only, never in metrics |
| **Not data** | Chayan dataset (optional v2) · MMR statistics (write-up context) · clinical cutoffs (define rule baseline B1) | No |

### Commit policy (so Colab and judges can reproduce)
- Commit `data/raw/maternal_health_risk.csv` (UCI, CC BY 4.0, ~30 KB) with attribution.
- External dataset: commit **only if its licence allows**; otherwise gitignore it, document download steps below, and keep its saved results in `results/`.
- Never upload data to Colab by hand — the notebook clones the repo.

---

## 3. Datasets and roles

| Role | Dataset | Link | Licence | Status |
|---|---|---|---|---|
| **Main train + test** | UCI Maternal Health Risk (Ahmed, 2020), id 863 — rural Bangladesh hospitals/clinics via IoT risk monitoring; Age, SystolicBP, DiastolicBP, BS (mmol/L), BodyTemp (°F), HeartRate, RiskLevel (low/mid/high) | https://archive.ics.uci.edu/dataset/863/maternal+health+risk | CC BY 4.0 | to load |
| **External test (E3)** | Mendeley "Maternal Health Risk Assessment Dataset" (Mojumdar et al., 2024) — rural Bangladesh; Age, SBP, DBP, BS, Body Temp, BMI, Previous Complications, Pre-existing Diabetes, Gestational Diabetes, Mental Health, Heart Rate, Risk Level (High/Low) | https://data.mendeley.com/datasets/p5w98dvbbk/1 | check on page | to check |
| Optional v2 only | Mendeley "Maternal Health and High-Risk Pregnancy Dataset" (Chayan, 2024) — adds gravida, weight/height, gestational age, anemia, fetal heart rate; high-risk vs not | https://data.mendeley.com/datasets/8k9pvpmykk/1 | check on page | skip unless time |
| Rule baseline cutoffs | general clinical thresholds (BP ≥140/90 etc.) — see `DESIGN.md` §4 | cite in README | — | — |
| Problem context | Indonesia MMR 189 / 100,000 live births (2020 Census, UNFPA Indonesia) | https://indonesia.unfpa.org/en/node/164180 | — | — |
| Demo examples | **synthetic** cases written by us, Indonesian units | `web/` | ours | labelled "synthetic" in UI; never used in metrics |

**Trap:** many Kaggle datasets are re-uploads of the same UCI file (also 1,014 rows). They are **not** a new source. Do not use them for E3.

---

## 4. Checks for the external dataset (first 30 min of Phase 1)

- [ ] Downloaded manually → `data/raw/external_mojumdar/` (commit only if licence allows; otherwise gitignore + document download steps here)
- [ ] Row count: ____
- [ ] Licence: ____
- [ ] Units — BS in mmol/L? Body temp in °F or °C? ____
- [ ] Missing values: ____
- [ ] Label values and mapping → `high` vs `not-high`: ____
- [ ] Overlap check: are any rows identical to UCI rows? (if many → not independent; report) ____
- **If unusable after 30 min:** drop E3, note it below, rely on E1 (duplicate leakage) + E2 (age groups) as the "own question".

---

## 5. Cleaning log (fill as you go)

| Step | Rows before | Rows after | Decision + reason |
|---|---|---|---|
| Load UCI raw | — | 1014 | no missing values; classes low 406 · mid 336 · high 272 |
| Drop exact duplicates | 1014 | 452 | 562 rows are exact copies (same 6 vitals + same label); keep one of each |
| Conflicting duplicates | 452 | 381 | 35 sets of identical vitals carry different labels (71 rows). True label unknown → drop the whole group. Keep-majority rejected: the counts come from copied rows and many are 2-vs-2 ties |
| Implausible values | 381 | 380 | 1 row with HeartRate = 7 bpm removed. 7 rows with Age > 60 kept and flagged (limitation) |
| Train / test split | 380 | train 304 / test 76 | stratified 80/20, random_state=42 |

Class balance after cleaning: low 203 · mid 76 · high 101
Train: low 162 · mid 61 · high 81 — Test: low 41 · mid 15 · high 20

All numbers above come from `results/cleaning_log.json` (written by `pipeline/01_load_clean.py` and `02_split.py`).

**E3 external dataset: dropped for time (Sun 18:00).** §4 below was not run.

---

## 6. Unit conversions (used by the web app)

- Blood sugar: **mmol/L = mg/dL ÷ 18.016** (Indonesia commonly reports mg/dL)
- Temperature: **°F = °C × 9/5 + 32**
