# SigapBumil — maternal risk triage for village midwives

> This project is a prototype and is not medical advice.

**Track:** Health · **Team:** Danish Ahmad Satria (solo) · **Live demo:** https://sycthePlays.github.io/SigapBumil/ · **Code and full write-up:** [README.md](README.md)

## The problem

Indonesia's maternal mortality ratio was 189 deaths per 100,000 live births (2020 Census, via UNFPA Indonesia). In villages the first line of care is the *bidan desa* (village midwife). She already measures the vitals; the hard part is reading them together. Several borderline numbers can add up to danger, and a high-risk mother who is not referred in time is the costly error.

## What we built

A phone web app. The bidan types six vitals in Indonesian units (age, blood pressure, blood sugar in mg/dL, temperature in °C, pulse) and gets **Rujuk sekarang** (refer now), **Cek ulang** (recheck) or **Rutin** (routine), with the vitals that raised the risk and a separate danger-sign warning. It runs offline in the browser, in Bahasa Indonesia and English, and stores nothing.

## What we added

Own idea. We added: (1) our own user and setting; (2) a duplicate-leakage check on a widely used public dataset; (3) a label-noise count; (4) ML compared with a clinical rule at the same recall; (5) an age-group check (under 20, 20–35, over 35).

## How it works

**Data:** UCI Maternal Health Risk, 1014 rows. After removing 562 exact duplicates, 35 groups with conflicting labels (71 rows) and 1 impossible value, 380 rows remain: 304 train (81 high-risk), 76 test (20 high-risk). **Model:** standardized multinomial logistic regression. **Decision:** refer when P(high) ≥ 0.1964, a cutoff tuned by 5-fold cross-validation (CV) on the training rows to catch 90% of high-risk mothers. **Reasons:** coefficient × standardized value for each vital. The same arithmetic runs in JavaScript and matches scikit-learn to within 1e-6.

## Results

High-risk class. FN = missed high-risk mothers, FP = false alarms.

| Approach | CV recall | CV FN | CV FP | Test recall | Test FN | Test FP |
|---|---|---|---|---|---|---|
| Always "low risk" (baseline) | 0% | 81 | 0 | 0% | 20 | 0 |
| Clinical rule (baseline) | 90% | 8 | 72 | 85% | 3 | 14 |
| **Logistic regression, triage (deployed)** | 90% | 8 | 63 | 100% | 0 | 8 |
| Random forest, triage (not deployed) | 90% | 8 | 44 | 100% | 0 | 4 |

Expect about 90% recall (CV). The test result is 20 of 20, but with 20 cases the 95% Wilson interval is 84–100%.

- **Leakage:** 79% of raw test rows also appear in the training rows. Random forest accuracy is 0.87 with duplicates and 0.80 after cleaning.
- **ML against the rule:** same 90% CV recall, false alarms 72 → 63, a modest gain. The random forest reaches 44 but gives no per-patient reasons, so it is not deployed.
- **Age groups (CV):** 15 of 16, 32 of 35 and 26 of 30 caught. No meaningful gap; small groups.

## Where it fails

Mothers labelled high-risk whose six vitals all look normal; one abnormal value among normal ones (e.g. diastolic 95), which the danger-sign warning covers; fever cases, which cause false alarms.

## Limitations

Labels are assigned risk levels, not real outcomes. Data from rural Bangladesh, not Indonesia. Only 380 rows and 20 high-risk test cases. Conflicting rows were removed, so the data is cleaner than reality. It refers often by design (136 of 304 in CV). Six vitals only. Not tested with real users. Not a medical device.

## Next steps

A field trial with bidan at a puskesmas; validation on Indonesian data with real outcomes; adding gestational age and haemoglobin.

## Sources

Ahmed, M. (2020), *Maternal Health Risk*, UCI Machine Learning Repository, https://doi.org/10.24432/C5DP5D (CC BY 4.0). UNFPA Indonesia, https://indonesia.unfpa.org/en/node/164180. Rule cutoffs: WHO (2011) and WHO (2013), full references in [README.md](README.md#sources). Libraries: pandas, NumPy, scikit-learn, matplotlib, ucimlrepo, joblib, pytest. AI tools: Claude (planning and design), Claude Code (code and documentation); all code reviewed and understood by the author.
