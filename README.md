# SigapBumil — maternal risk triage for village midwives

> This project is a prototype and is not medical advice.

**Track:** Health · **Team:** Danish Ahmad Satria (solo)
**Live demo:** https://sycthePlays.github.io/SigapBumil/ · **Demo video:** _link to be added_ · **Colab walkthrough:** [notebooks/walkthrough.ipynb](https://colab.research.google.com/github/SycthePlays/SigapBumil/blob/main/notebooks/walkthrough.ipynb) · **Code:** this repository
**One-page write-up:** [WRITEUP.md](WRITEUP.md) (this README is the longer version)

## The problem

Indonesia's maternal mortality ratio was 189 deaths per 100,000 live births (2020 Population Census, via UNFPA Indonesia). In villages the first line of antenatal care is the *bidan desa* (village midwife): one midwife, many mothers, basic tools. She already measures the vitals. The hard part is reading them together: blood pressure 135/88, raised blood sugar, age 37 and a fast pulse each look borderline alone, but the combination can signal danger. A high-risk mother who is not referred in time is the costly error; a false alarm costs a trip to the puskesmas (community health centre).

## What we built

A web app for the bidan's phone. She types six vitals in the units she already uses (age, systolic and diastolic blood pressure in mmHg, blood sugar in mg/dL, temperature in °C, pulse) and gets one action: **Rujuk sekarang** (refer now), **Cek ulang** (recheck in 1–2 days) or **Rutin** (routine care). The result also shows the three class probabilities, the vitals that raised the risk most, and a separate **danger-sign** warning when any single vital passes a fixed cutoff. It runs fully in the browser, works offline after the first load, is in Bahasa Indonesia with an English toggle, and stores nothing.

## What we added

Own idea, not a suggested project. On top of a public dataset we added:

1. **Own user and setting:** the bidan desa at the moment she decides on referral; Indonesian units, offline, bilingual.
2. **Duplicate leakage:** how much do repeated rows in this widely used dataset inflate reported scores?
3. **Label noise:** how many identical sets of vitals carry different risk labels?
4. **ML against a clinical rule:** compared at the same high-risk recall, not by accuracy.
5. **Age groups:** under 20, 20–35 and over 35, following Indonesia's "4 Terlalu" message.

## How it works

**Data.** UCI Maternal Health Risk: 1014 rows. We removed 562 exact duplicate rows (452 left), then 35 groups of identical vitals with conflicting labels (71 rows) and 1 impossible value (heart rate 7). That leaves 380 rows: 203 low, 76 mid, 101 high. Stratified 80/20 split: 304 train (81 high-risk), 76 test (20 high-risk). Duplicates were removed before splitting, and the test set was used only for the final evaluation.

**Model.** Standardize the six vitals, then multinomial logistic regression (`class_weight="balanced"`). It is compared with "always low risk" (B0), a fixed clinical-cutoff rule (B1) and a default random forest.

**Decision.** Refer when P(high) ≥ 0.1964; otherwise recheck when "mid" is the most likely class or P(mid) + P(high) ≥ 0.5; otherwise routine. The referral cutoff was tuned with 5-fold cross-validation on the training rows only: the highest value that still catches 90% of high-risk mothers.

**Explanation.** For each vital, coefficient for "high" × standardized value; the top three positive ones are shown. The danger-sign warning is a plain rule, separate from the model: systolic ≥ 140 mmHg, diastolic ≥ 90 mmHg, temperature ≥ 38 °C or blood sugar ≥ 200 mg/dL.

The fever warning matches the 'demam tinggi' danger sign in Buku KIA (Kementerian Kesehatan RI). Blood pressure and blood sugar cutoffs follow WHO, because the Buku KIA danger-sign list is symptom-based (e.g. severe headache, blurred vision), not number-based.

**In the browser.** The model is exported as plain numbers (`web/model.json`) and run by `web/inference.js`. A test checks that JavaScript and scikit-learn agree to within 1e-6 on 30 cases.

## Results

High-risk class. CV = 5-fold cross-validation on the 304 training rows (81 high-risk). Test = 76 held-out rows (20 high-risk).

| Approach | CV recall | CV missed (FN) | CV false alarms (FP) | Test recall | Test missed (FN) | Test false alarms (FP) |
|---|---|---|---|---|---|---|
| Always "low risk" (B0) | 0% | 81 | 0 | 0% | 20 | 0 |
| Clinical rule (B1) | 90% | 8 | 72 | 85% | 3 | 14 |
| Logistic regression, plain | 59% | 33 | 18 | 75% | 5 | 3 |
| **Logistic regression, triage (deployed)** | **90%** | **8** | **63** | **100%** | **0** | **8** |
| Random forest, plain | 75% | 20 | 19 | 95% | 1 | 1 |
| Random forest, triage | 90% | 8 | 44 | 100% | 0 | 4 |

"Plain" takes the most likely class; "triage" refers when P(high) passes the tuned cutoff. **Read the CV recall (about 90%) as the expectation.** The test result is 20 of 20, but with only 20 cases the 95% Wilson interval is 84–100%.

**Findings**

1. **Duplicate leakage.** In the raw file, 160 of 203 test rows (79%) also appear in the training rows. The random forest scores 0.87 accuracy with duplicates and 0.80 after cleaning. Logistic regression is not inflated (0.60 with duplicates, 0.71 after cleaning). High scores reported on this dataset with tree models are partly memorised rows.
2. **Label noise.** 35 groups of identical vitals carry different risk labels (71 rows). We removed them and report the count; no model can be perfect on labels that disagree with themselves.
3. **ML against the rule.** At the same 90% CV recall, false alarms drop from 72 (rule) to 63 (our model): a modest gain. The random forest reaches 44 but is not deployed, because it gives no per-patient reasons from coefficients and is harder to port exactly to the browser.
4. **Age groups.** No meaningful gap. CV: 15 of 16 caught under 20, 32 of 35 at 20–35, 26 of 30 over 35. Test: 4 of 4, 10 of 10, 6 of 6. The groups are small.

**Where it fails** (dataset units: mmol/L, °F)

- **Normal-looking vitals labelled high.** Age 34, BP 110/70, blood sugar 7.0, 98 °F was labelled high; the model said recheck and the rule said low. The label depends on something outside the six vitals, or is noise.
- **One abnormal value among normal ones.** Age 40, BP 120/95, blood sugar 7.0 was labelled high; the model said routine because a linear model lets the normal values outweigh the diastolic 95. The danger-sign warning covers this case.
- **Fever cases cause false alarms.** Mothers at 101–103 °F labelled low or mid were referred.

**Limitations**

- Labels are assigned risk levels, not real outcomes.
- Data from rural Bangladesh, not Indonesia.
- 380 rows after cleaning; only 20 high-risk mothers in the test set.
- Rows with conflicting labels were removed, so the data is cleaner than reality and results may be slightly optimistic.
- 7 rows with age over 60 were kept.
- Tuned to rarely miss high risk, so it refers often (136 of 304 in CV).
- Six vitals only.
- Not tested with real users yet.
- Not a medical device.

**Honest notes**

- **The test evaluation ran twice.** The second run was a clean rebuild after we added a Wilson confidence interval to the report. Features, model and thresholds were not changed in between, and the numbers are identical.
- **The random forest decision was made from cross-validation**, before the test set was opened.
- **scikit-learn is pinned to 1.8.0**, not the newer 1.9.1, because a Windows Application Control policy on the development laptop blocked two 1.9.1 binaries.
- **A test on a separately collected dataset was planned and skipped for time.**

## What we'd do next

- A field trial with bidan at a puskesmas: is the result clear, and does it change the referral decision?
- Validate on Indonesian data with real outcomes.
- Add gestational age and haemoglobin (Hb).

## How to run

Needs Python 3.10+ and Node.js 22.7+.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python pipeline/run_all.py          # cleaning, models, evaluation, export, parity test
pytest -q                           # Python tests
node tests/test_parity.mjs          # JavaScript = Python check
python -m http.server -d web 8000   # site at http://localhost:8000
```

All numbers above come from `results/summary.json`, written by the pipeline.

## Sources

- **Dataset:** Ahmed, M. (2020). *Maternal Health Risk* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5DP5D (CC BY 4.0)
- **Maternal mortality figure:** UNFPA Indonesia, https://indonesia.unfpa.org/en/node/164180
- **Cutoffs for the rule baseline (B1) and danger signs.** These are simplified general cutoffs, not an official guideline:
  - Blood pressure ≥ 140/90 mmHg: WHO (2011). *WHO recommendations for prevention and treatment of pre-eclampsia and eclampsia.* https://www.who.int/publications/i/item/9789241548335
  - Random blood sugar ≥ 11.1 mmol/L (200 mg/dL): WHO (2013). *Diagnostic criteria and classification of hyperglycaemia first detected in pregnancy* (WHO/NMH/MND/13.2). https://www.who.int/publications/i/item/WHO-NMH-MND-13.2
  - Temperature ≥ 38.0 °C (100.4 °F): the common clinical definition of fever.
  - The "mid" band (BP 130–139 or 80–89, blood sugar 7.8–11.0 mmol/L, pulse over 100) is our own simplification.
- **Libraries:** pandas, NumPy, scikit-learn, matplotlib, ucimlrepo, joblib, pytest. The web app uses no libraries.
- **AI tools:** Claude (planning and design discussion), Claude Code (code generation and documentation), used under the hackathon rules; all code reviewed and understood by the author.
