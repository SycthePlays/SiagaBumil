# SigapBumil — maternal risk triage for village midwives

**Track:** Health
**Team:** Danish Ahmad Satria (solo)
**Live demo:** _GitHub Pages link_ · **Demo video:** _link_ · **Run it in Colab:** _notebooks/walkthrough.ipynb link_ · **Code:** this repository

> This project is a prototype and is not medical advice.

<!-- Claude Code: fill every _placeholder_ in Phase 6 using numbers from results/summary.json only. Keep to ~1 page. -->

## The problem

_2–3 sentences: Indonesia's maternal mortality (189 per 100,000 live births, 2020 Census); the bidan desa as first line of care; six numbers, borderline one by one, dangerous in combination; a missed high-risk mother is the costly error._

## What we built

_Input → output → how a bidan uses it. Six vitals in Indonesian units → Rujuk sekarang / Cek ulang / Rutin, with top reasons. Runs offline in the browser on a phone; stores nothing._

## What we added

_Started from: own idea (maternal health risk, not a suggested project). Added: (1) own user + setting (bidan desa, Indonesian units, offline, bilingual); (2) own question — duplicate-row leakage in a widely used public dataset; (3) ML vs a simple clinical-threshold rule; (4) age-group check (<20 / 20–35 / >35, "4 Terlalu"); (5) test on a separately collected dataset._

## How it works

**Data:** _UCI Maternal Health Risk — N raw rows → N after removing duplicates (N conflicting); class balance; 80/20 stratified split, test set used once._
**Model:** _Standardized multinomial logistic regression (interpretable, runs in the browser); compared with a tree ensemble. Decision threshold tuned on cross-validation for ≥90% high-risk recall. Explanations = per-feature contribution to the high-risk score._

## Results

| Approach | High-risk recall | Missed high-risk (FN) | False alarms (FP) | Macro-F1 |
|---|---|---|---|---|
| Always "low risk" (B0) | | | | |
| Clinical threshold rule (B1) | | | | |
| Logistic regression (deployed) | | | | |
| Tree ensemble | | | | |

_Held-out test set, n = __._

**Findings**
- _Duplicate leakage: accuracy __ with duplicates vs __ after dedupe._
- _Age groups: high-risk recall __ / __ / __ (n = __ / __ / __)._
- _External dataset: __ (or: why it was skipped)._

**Where it fails:** _1–2 concrete missed cases and why we think it happens._

**Limitations:** labels are assigned risk levels, not real outcomes; data from rural Bangladesh, not Indonesia; small sample after deduplication; six vitals only; thresholds favour recall, so false alarms are higher by design.

## What we'd do next

_1–2 concrete steps, e.g. validate with an Indonesian clinic dataset that has real outcomes; add gestational age and Hb._

## Sources

- Ahmed, M. (2020). *Maternal Health Risk* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5DP5D (CC BY 4.0)
- _External dataset citation (if used)_
- UNFPA Indonesia — maternal mortality figure: https://indonesia.unfpa.org/en/node/164180
- _Clinical threshold sources for the rule baseline_
- Libraries: pandas, NumPy, scikit-learn, matplotlib, ucimlrepo
- AI tools: Claude (planning and design discussion), Claude Code (code generation and documentation), used under the hackathon rules; all code reviewed and understood by the author.
