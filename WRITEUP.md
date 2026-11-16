# SigapBumil — maternal risk triage for village midwives

> This project is a prototype and is not medical advice.

**Track:** Health · **Team:** Danish Ahmad Satria (solo) · **Live demo:** https://sycthePlays.github.io/SigapBumil/ · **[Demo video (Google Drive)](https://drive.google.com/file/d/1e8caWtkl-DfvraemdiYMSoS-icgIKdax/view?usp=sharing)** · **[Colab walkthrough](https://colab.research.google.com/github/SycthePlays/SigapBumil/blob/main/notebooks/walkthrough.ipynb)** · **Code:** https://github.com/SycthePlays/SigapBumil · **Full write-up:** [README.md](README.md)

## The problem

Indonesia's maternal mortality ratio was 189 per 100,000 live births (2020 Census, via UNFPA Indonesia). The first line of village care is the *bidan desa* (village midwife). She already measures the vitals; the hard part is reading them together. Several borderline numbers can add up to danger, and a missed high-risk mother is the costly error.

## What we built

A phone web app. The bidan types six vitals in Indonesian units (age, blood pressure, blood sugar, temperature, pulse) and gets **Rujuk sekarang** (refer now), **Cek ulang** (recheck) or **Rutin** (routine), with the vitals that raised the risk and a separate danger-sign warning. It runs offline, in English and Indonesian, and stores nothing.

## What we added

Own idea. We added: (1) our own user and setting; (2) a duplicate-leakage check on a widely used public dataset; (3) a label-noise count; (4) ML compared with a clinical rule at the same recall; (5) an age-group check (in the README).

## How it works

**Data:** UCI Maternal Health Risk, 1014 rows. After removing 562 exact duplicates, 35 conflicting-label groups (71 rows) and 1 impossible value, 380 remain: 304 train (81 high-risk), 76 test (20 high-risk). **Model:** standardized multinomial logistic regression. **Decision:** refer when P(high) ≥ 0.1964, a cutoff tuned by 5-fold cross-validation (CV) on the training rows to catch 90% of high-risk mothers. **Reasons:** coefficient × standardized value. The browser version matches scikit-learn to within 1e-6.

## Results

High-risk class. FN = missed high-risk mothers, FP = false alarms.

| Approach | CV recall | CV FN | CV FP | Test recall | Test FN | Test FP |
|---|---|---|---|---|---|---|
| Always "low risk" (baseline) | 0% | 81 | 0 | 0% | 20 | 0 |
| Clinical rule (baseline) | 90% | 8 | 72 | 85% | 3 | 14 |
| **Logistic regression, triage (deployed)** | 90% | 8 | 63 | 100% | 0 | 8 |
| Random forest, triage (not deployed) | 90% | 8 | 44 | 100% | 0 | 4 |

Expect about 90% recall (CV). The test result is 20 of 20, but with 20 cases the 95% Wilson interval is 84–100%.

- **Leakage:** 79% of raw test rows also appear in training. Random forest accuracy: 0.87 with duplicates, 0.80 after cleaning.
- **ML against the rule:** same 90% CV recall, false alarms 72 → 63, a modest gain. The random forest reaches 44 but gives no per-patient reasons, so it is not deployed.
## Where it fails

Mothers labelled high-risk whose six vitals all look normal; one abnormal value among normal ones (e.g. diastolic 95), which the danger-sign warning covers; fever cases, which cause false alarms.

## Limitations

- **Assigned labels, not outcomes:** the model copies the original labelling; it does not predict complications.
- **Bangladesh data, not Indonesia:** the same six vitals allow retraining on puskesmas data.
- **Small sample (380 rows, 20 high-risk in test):** one miss moves test recall by 5 points.
- **35 conflicting-label groups removed:** results may be slightly optimistic.
- **Refers often (136 of 304 in CV):** a false alarm costs a trip to the puskesmas; a miss can cost a life.
- Six vitals only; not tested with bidan yet; not a medical device.

## Who it helps

Village midwives (a second check with reasons, offline), puskesmas coordinators (one explainable referral rule) and researchers (evidence of duplicate inflation). It complements Buku KIA and the midwife's judgement; it does not replace them.

## Next steps

(1) Field trial with bidan at a puskesmas; (2) retrain and validate on Indonesian data with real outcomes; (3) add gestational age and haemoglobin.

## Sources

Ahmed, M. (2020), *Maternal Health Risk*, UCI Machine Learning Repository, https://doi.org/10.24432/C5DP5D (CC BY 4.0). UNFPA Indonesia, https://indonesia.unfpa.org/en/node/164180. Rule cutoffs: WHO (2011) and WHO (2013); danger signs: Buku KIA (Kemenkes RI); full references in [README.md](README.md#sources). Libraries: pandas, NumPy, scikit-learn, matplotlib, ucimlrepo, joblib, pytest. AI tools: Claude and Claude Code assisted with planning, code and documentation; all reviewed by the author.
