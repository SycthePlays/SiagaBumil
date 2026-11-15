# DESIGN.md — AI / ML design

Decisions for the SigapBumil model. If a decision changes, update this file and note why in `HANDOFF.md`.

---

## 1. Task

- **Input:** one antenatal visit = 6 vitals: `Age` (years), `SystolicBP` (mmHg), `DiastolicBP` (mmHg), `BS` (blood sugar, mmol/L), `BodyTemp` (°F), `HeartRate` (bpm).
- **Target:** `RiskLevel` ∈ {low risk, mid risk, high risk} → encoded `low`, `mid`, `high`.
- **Type:** 3-class tabular classification. A binary view (**high vs not-high**) is used for the triage decision and for the external dataset.
- **Priority metric:** **high-risk recall** (catch high-risk mothers), subject to keeping false alarms reasonable.

## 2. Features

| Feature | Source | Note |
|---|---|---|
| Age, SystolicBP, DiastolicBP, BS, BodyTemp, HeartRate | dataset | raw |
| PulsePressure | SBP − DBP | engineered |
| MAP (mean arterial pressure) | DBP + (SBP − DBP)/3 | engineered |
| AgeGroup (<20, 20–35, >35) | from Age | **analysis only**, not a model input |

Check whether engineered features help in CV. Keep them only if they do; record the result here.

**Result (Phase 2, CV on train):** not kept. At ≥ 0.90 high-risk recall the 6 raw vitals gave 63 false alarms, raw + PulsePressure + MAP gave 65. Both are linear combinations of SBP and DBP, so a linear model gains nothing. **The deployed model uses the 6 raw vitals only**; `model.json.features` lists 6, and the web app's `addFeatures()` step has nothing to add.

**Deploy decision (Phase 2, CV on train):** M2 (default random forest) beat M1 in CV (44 vs 63 false alarms at 0.90 recall), which triggers the §5 rule. M1 is still deployed for explainability, an exact browser port and no extra dependency; the write-up states that the forest scored better. `t_refer = 0.1964`, `t_recheck = 0.5`.

## 3. Preprocessing

1. Load UCI Maternal Health Risk (`fetch_ucirepo(id=863)`); keep a raw copy in `data/raw/`.
2. Sanity checks: missing values, impossible values (e.g. HeartRate < 40, SBP < 60). Log every fix in `DATA.md`.
3. **Deduplicate** exact duplicate rows. Count and report:
   - rows before / after,
   - conflicting duplicates (same 6 vitals, different label) — decide keep-majority or drop, and log.
4. Stratified **80/20 train/test split** on deduped data, `random_state=42`. Save to `data/processed/`. **Test set is locked** until `05_final_eval.py`.
5. Inside every model: `StandardScaler` fitted on training folds only (use a `Pipeline`).

## 4. Baselines

- **B0 — majority class:** always predict the most common class (likely "low"). Shows why accuracy alone is misleading.
- **B1 — simplified clinical rule** (single-number cutoffs, no learning):
  - **high** if SBP ≥ 140 **or** DBP ≥ 90 (hypertension in pregnancy) **or** BS ≥ 11.1 mmol/L (≈200 mg/dL random glucose) **or** BodyTemp ≥ 100.4 °F (fever)
  - **mid** if SBP 130–139 **or** DBP 80–89 **or** BS 7.8–11.0 mmol/L **or** HeartRate > 100
  - **low** otherwise
  - These are simplified general cutoffs, **not an official clinical guideline**. Cite sources in `README.md`. The point is to test "does ML add anything over what a careful bidan could do with fixed thresholds?"

## 5. Models

| ID | Model | Settings | Role |
|---|---|---|---|
| M1 | Logistic Regression (multinomial) | `StandardScaler` → `LogisticRegression(class_weight="balanced", max_iter=1000)` | **deployed model** — interpretable, exact JS port |
| M2 | Tree ensemble | `RandomForestClassifier(class_weight="balanced")` or `HistGradientBoostingClassifier` — small grid only | comparison: can a non-linear model find more? |

- Model selection: **5-fold stratified CV on the training set**, out-of-fold predictions.
- **Deploy M1** unless M2 beats it by > 5 percentage points of high-risk recall at a similar false-alarm count. If so, record the decision; export M2 with `m2cgen` to JS and use rule-based reasons. Default plan: **deploy M1**.

## 6. Decision layer (triage)

From class probabilities `P(low), P(mid), P(high)`:

```
if P(high) >= t_refer:                       action = "Rujuk sekarang"   (Refer now)
elif argmax == "mid" or P(mid)+P(high) >= t_recheck:
                                             action = "Cek ulang 1–2 hari" (Recheck)
else:                                        action = "Rutin"            (Routine)
```

- Tune `t_refer` on **out-of-fold CV predictions**: the highest threshold that keeps high-risk recall ≥ 0.90 (if unreachable, report the best achievable and say so).
- Plot recall vs number of false alarms across thresholds → `results/threshold_curve.png`.
- `t_recheck` default 0.5; adjust only with CV evidence.

## 7. Explanation

For the deployed LR, per input:
- `z_k` = standardized feature value, `w_high,k` = coefficient of feature k for class `high`.
- contribution_k = `w_high,k × z_k`. Top 3 positive contributions = "what raised the risk".
- Map to plain language, e.g. `SystolicBP` → "Tekanan darah sistolik tinggi / High systolic blood pressure".
- Global view: plot coefficients → `results/coefficients.png`.

## 8. Evaluation (all saved to `results/`)

**Final test set (run once, `05_final_eval.py`)** — for B0, B1, M1, M2:
- accuracy, macro-F1, per-class precision/recall,
- **high-risk: recall, false negatives (count), false positives (count)**,
- confusion matrices → `results/confusion_*.png`,
- triage-level results with the chosen thresholds,
- optional: bootstrap 95% CI for high-risk recall (test set is small, ~20% of deduped rows).

**Experiments (`06_experiments.py`):**
- **E1 duplicate leakage:** same M1 pipeline, split *before* vs *after* dedupe → compare test accuracy. Expected: raw split looks better because duplicates sit on both sides.
- **E2 age groups:** high-risk recall and n per group (<20, 20–35, >35). Flag small n honestly.
- **E3 external dataset:** freeze M1, apply to the external dataset (shared features only), evaluate as high vs not-high. See `DATA.md` for mapping and units. Skip and document if the dataset is unusable.
- **E4 failure cases:** 3–5 test-set errors (prioritise missed high-risk), with vitals, prediction, truth, and a short hypothesis why.

Write a machine-readable summary to `results/summary.json` (README pulls numbers from here).

## 9. Export → `web/model.json`

```json
{
  "version": "1.0",
  "trained_on": "UCI Maternal Health Risk (deduped), train split",
  "features": ["Age","SystolicBP","DiastolicBP","BS","BodyTemp","HeartRate","PulsePressure","MAP"],
  "units": {"BS": "mmol/L", "BodyTemp": "F"},
  "scaler": {"mean": [], "scale": []},
  "classes": ["low","mid","high"],
  "coef": [[], [], []],
  "intercept": [0, 0, 0],
  "thresholds": {"t_refer": 0.0, "t_recheck": 0.5},
  "feature_labels": {"SystolicBP": {"id": "Tekanan darah sistolik", "en": "Systolic blood pressure"}},
  "metrics": {"test_high_recall": 0.0, "test_high_fn": 0, "test_high_fp": 0}
}
```

- Also save the fitted sklearn pipeline to `models/sigapbumil_lr.joblib` (committed). `model.json` is the version-independent source of truth; the joblib copy needs the pinned scikit-learn version.
- Class order in `coef`/`intercept` must match `classes` (reorder from `clf.classes_`).
- Inference in JS: `z = (x − mean) / scale` → `logits = coef · z + intercept` → softmax.
- `web/test_cases.json`: ~30 inputs + Python probabilities; `tests/test_parity.mjs` asserts JS matches within 1e-6.

## 10. Colab walkthrough (`notebooks/walkthrough.ipynb`)

Purpose: judges see the trained model working and the results, in one click, with outputs already visible.

1. `git clone` the repo, `cd`, `pip install -r requirements.txt` (fresh runtime every time — no uploads).
2. Load `web/model.json`; a short `predict()` in NumPy using the same math as `app.js`; run 3 synthetic examples (routine / borderline / high).
3. Optional: `python pipeline/run_all.py` to show the pipeline reproduces the same metrics.
4. Display `results/summary.json` and the key plots (baseline table, confusion matrix, threshold curve, leakage comparison).
5. Run all → save to GitHub with outputs → open from GitHub in incognito to confirm outputs show.

## 11. Known limitations (must appear in README)

- Labels are **assigned risk levels, not real outcomes**: the model imitates the original labelling, it does not predict complications.
- Data from rural **Bangladesh**, not Indonesia; small sample after dedupe.
- Six vitals only; no gestational age, Hb, proteinuria, history.
- Thresholds tuned for recall → more false alarms by design.
- **Conflicting duplicates removed** (35 sets of identical vitals with different labels, 71 rows): the ambiguous cases are gone, so the remaining data is cleaner than real life and results may be slightly optimistic.
- Test set has only 20 high-risk rows → report a bootstrap 95% CI and show CV results beside test results.
