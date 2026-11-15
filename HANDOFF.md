# HANDOFF.md — session log

Claude Code: update this at the **end of every session/phase**. Newest entry on top.

---

## Current status

- **Phase:** 5 built and checked locally → waiting for developer's ok to commit + push; then enable Pages and test on a real phone
- **Last updated:** Sun Nov 15, 21:25 WIB
- **Next step:** after push: repo Settings → Pages → Source = **GitHub Actions**, open the public URL in incognito and on a phone, run Lighthouse. Then Phase 6 (README from `results/summary.json`).
- **Blockers:** none. Repo: https://github.com/SycthePlays/SigapBumil (branch `main`). Pages URL (Phase 5): https://sycthePlays.github.io/SigapBumil/
- **Commit rule:** end of every phase → show `git status` + summary + proposed message, wait for "ya"/"ok", then commit and push (`CLAUDE.md` §11).

---

## Scope cuts (Sun 18:00) — override DESIGN.md / DATA.md / WEB-SPEC.md / SETUP.md / CLAUDE.md

Started ~6 h late. Where another doc still mentions these, this list wins:

| Cut | Was | Now |
|---|---|---|
| E3 external dataset (RQ3) | test frozen model on Mendeley Mojumdar data | **dropped**; README + web "key findings" say skipped for time |
| Tree-model grid search | small grid for M2 | **one default** `RandomForestClassifier(class_weight="balanced", random_state=42)`, comparison only |
| Hugging Face Space | fallback host | **dropped**; GitHub Pages only |
| Dark mode | optional | **dropped** |

---

## Open issues / decisions pending

- [x] Git/GitHub connected; Phase 0+1 committed on top of the existing upload history (no force push).
- [x] Phase 3 additions (developer review): bootstrap 95% CI + Wilson interval; CV beside test in `summary.json`; "conflicting duplicates removed" in limitations.
- [ ] **Deploy M1 (LR) vs M2 (forest)** — M1 kept by default; M2 was stronger in CV. Developer to confirm (see log 20:15).
- [x] Engineered features (PulsePressure, MAP) — dropped, no gain in CV. `web/model.json` will list 6 features.
- [ ] README "What we added" item (5) "test on a separately collected dataset" must be removed in Phase 6 (E3 cut)
- [x] ~~External dataset usable?~~ — cut

---

## How to explain to judges (fill after each phase)

*3–5 plain-language bullets per phase so the developer can defend every part.*

### Phase 1 — Data
- **More than half the public file is copies.** 1,014 rows, but 562 are exact repeats of another row. Only 452 are distinct. Most projects using this dataset split it as-is, so the same row sits in both training and test and the score looks better than it is. We removed copies *before* splitting.
- **The labels disagree with themselves.** 35 sets of identical vitals (71 rows) carry different risk labels — the same six numbers called "low" in one row and "mid" or "high" in another. We cannot know which is right, so we removed all of them and report the count. It also means no model can be perfect on this data: the labels are noisy.
- **One impossible value removed:** a heart rate of 7 bpm. Seven rows with age over 60 were kept (unlikely pregnancies, but we did not want to delete data on a guess) — listed as a limitation.
- **What is left: 380 rows** (203 low, 76 mid, 101 high) → 304 train / 76 test, same class mix in both. The test set is locked until the final evaluation.
- **Be honest about size:** the test set has only **20 high-risk mothers**, so one missed case moves recall by 5 points. Small numbers → wide uncertainty.

### Phase 2 — Baselines + models (cross-validation on 304 training rows, 81 high-risk)
- **"Always low risk" (B0) is 53% accurate and catches 0 of 81 high-risk mothers.** That is why we do not judge by accuracy.
- **The fixed clinical rule (B1) is a strong baseline:** it catches 73 of 81 (90%) but raises 72 false alarms.
- **Logistic regression answering low/mid/high directly only catches 59%.** So we do not use its top answer; we refer whenever P(high) ≥ 0.1964, the highest cutoff that still catches 90% in CV. At that point it raises 63 false alarms.
- **Honest comparison at the same 90% recall: rule 72 false alarms, our model 63, random forest 44.** Our deployed model beats the rule only modestly. The random forest is clearly better.
- **We still deploy logistic regression** because every result can be explained ("systolic BP raised the score") and the exact same math runs in the browser offline. This choice was made from CV, before the test set was opened, and we say openly that the forest scored better.
- **Extra features (pulse pressure, MAP) did not help** (65 vs 63 false alarms), so we dropped them. They are just sums of systolic and diastolic, which a linear model can already build itself.

### Phase 3 — Results + experiments (test set: 76 rows, 20 high-risk, opened once)
- **Test result:** SigapBumil referred **20 of 20** high-risk mothers with **8 false alarms**; the rule referred 17 of 20 with 14 false alarms. No high-risk mother was sent to "routine".
- **20 of 20 is not "100% recall".** With only 20 cases the honest range is about **84%–100%** (Wilson interval). Cross-validation on 81 cases says about 90%. Quote the CV number as the expectation and the test number as "consistent with it". The test set turned out easier than CV.
- **Duplicate leakage (our own question):** in the raw file, **160 of 203 test rows (79%)** have vitals that also sit in the training part. The random forest looks like **0.87** accuracy on the raw file but **0.80** after cleaning (CV: 0.85 → 0.75). Logistic regression is *not* inflated (0.60 → 0.71) because it cannot memorise rows. So high scores reported on this dataset with tree models are partly memory.
- **Age groups:** on test, recall is 100% in all three groups, but the groups hold only 4, 10 and 6 high-risk mothers. In CV: <20 → 0.94, 20–35 → 0.91, >35 → 0.87 (4 of 30 missed). A small gap for older mothers, too few cases to call it real.
- **Where it fails:** (1) high-risk mothers whose six vitals all look normal, e.g. age 34, BP 110/70, sugar 7.0, 98 °F: the rule misses her too, so the label depends on something outside our six numbers or is noise. (2) One abnormal number among normal ones, e.g. age 40, BP 120/**95**: the rule catches it, our model does not, because a linear model averages the normal values against the bad one. (3) False alarms are mostly fever (101–103 °F) cases labelled low or mid.

### Phase 5 — Web app
- **The website does no AI of its own.** `app.js` is only the form and the drawing. Every probability comes from `inference.js`, the same file the parity test checks against Python, so the phone gives the same answer as scikit-learn.
- **Nothing leaves the phone.** No server, no cookies, no storage. The only requests are the site's own files; after the first visit a service worker serves them from a local copy, so it opens with no internet.
- **Two separate signals on the result card.** The action banner is the model. The red "Tanda bahaya" box is a plain rule (one vital past a fixed cutoff). It exists because the linear model can let normal values hide one very bad number.
- **The Borderline example is the story:** 135/88, sugar 150, pulse 92, age 37. No single number passes a cutoff (no danger box), but the model says Rujuk sekarang at 48% high risk.
- **Every number in "Cara kerja" is read from `results.json`** at load time (table, leakage, age groups, the 84% lower bound). None are typed into the page.

---

## Log

### Sun Nov 15, 21:25 — Phase 5 built (web app), not yet deployed
- Phase 4 committed and pushed (`0dab03e`). Follow-ups from the developer applied: "Tidak ada faktor risiko menonjol / No strong risk factors" replaces "Why?" on Rutin; README limitation "refers often (136 of 304 in CV)"; SETUP says Node 22.7+.
- New: `web/index.html`, `style.css`, `app.js`, `sw.js`, `img/favicon.svg`, `.github/workflows/pages.yml`. No dark mode.
- **Checked in Chrome at 360 px and 1280 px (local server):** 3 example chips give the same action and percentages as `test_cases.json`; SBP ≤ DBP, out-of-range and empty fields keep the Check button off with a message; ID/EN switches every string including a result on screen; danger box only on the high-risk example; disclaimer on every result; requests are own files only; no cookies or storage; no horizontal scroll; reload with the network set to Offline still loads the page and model.
- **Not checked yet:** real phone, public URL in incognito, Lighthouse accessibility score.
- Service worker serves the cached copy first and refreshes it in the background, so a new push shows up on the second visit, not the first.
- Added beyond the spec text: sugar value converts when the unit is switched; decimal comma accepted ("36,7"); arrow in "Why?" points down when the value is below the training average.

### Sun Nov 15, 20:50 — Phase 4 done (export + parity)
- New: `pipeline/07_export.py`, `web/inference.js`, `tests/test_parity.mjs`; `run_all.py` now runs 07 and the Node parity test. Outputs: `web/model.json`, `web/results.json`, `web/test_cases.json` (30 cases: 3 demos, 9 fixed, 18 random), `web/img/` (4 plots), `models/sigapbumil_lr.joblib`.
- **Model unchanged:** after a full `run_all.py` rebuild, `git status results data` showed no differences from the Phase 2+3 commit. `common.py` only gained `B1_HIGH_CUTOFFS` (same four numbers the rule already used).
- **Parity:** JS vs scikit-learn on 30 cases, max probability difference 2.2e-16; action, top-3 reasons and danger signs all equal. `pytest -q` → 5 passed.
- **Demo examples** (synthetic, in `model.json.examples`): routine `25, 110/70, 110 mg/dL, 36.7 °C, 72` → Rutin; borderline `37, 135/88, 150 mg/dL, 36.8 °C, 92` → **Rujuk** with no danger sign; high `38, 150/95, 250 mg/dL, 37.0 °C, 88` → Rujuk + 3 danger signs.
- **Design choice:** model math is in `web/inference.js` (ES module) instead of inside `app.js`, so the parity test runs the real site code, not a copy. `WEB-SPEC.md` updated. Needs Node ≥ 22.7 for the test.
- **Danger sign** added to `WEB-SPEC.md` §4.3: single-vital warning (SBP ≥ 140, DBP ≥ 90, ≥ 38 °C, ≥ 200 mg/dL), independent of the model. Boundary cases (exactly 140/90/200/38.0 and one step below) are in the parity test.
- **For Phase 5:** the model refers easily by design (threshold 0.1964): e.g. age 35, 128/84, 130 mg/dL → Rujuk. In CV it referred 136 of 304. Say this in the UI/limitations. "Why?" is hidden for Rutin (top reason there is age, which confuses).
- README: added "Honest notes" (forest stronger but not deployed; test evaluation ran twice, identical numbers).

### Sun Nov 15, 20:15 — Phase 2 + Phase 3 done
- New: `pipeline/common.py`, `03_baselines.py`, `04_models.py`, `05_final_eval.py`, `06_experiments.py`, `run_all.py`. `python pipeline/run_all.py` rebuilds everything; `pytest -q` → 5 passed.
- Results: `results/summary.json` (CV beside test for every approach), `cv_comparison.json`, `test_metrics.json`, `experiments.json`, `threshold_curve.png`, `coefficients.png`, `confusion_{b1,m1,m2,m1_triage}.png`, `leakage.png`.
- **Decisions (all from CV, before the test set was opened):** features = 6 raw vitals (engineered dropped); `t_refer = 0.1964`, `t_recheck = 0.5`; deploy M1.
- **Open decision for the developer:** DESIGN.md §5 says switch to M2 if it beats M1 by > 5 points recall at similar false alarms. In CV it does (0.753 vs 0.593 as a plain classifier; 44 vs 63 false alarms at 90% recall). Kept M1 for explainability, exact browser port, no new dependency, and time. Switching to M2 means exporting 100 trees to JSON and giving up coefficient-based reasons.
- **Test set honesty:** `05_final_eval.py` ran twice. Second run was a clean rebuild after adding a Wilson interval (reporting only). Features and thresholds were not changed between runs; numbers are identical.
- **scikit-learn pinned to 1.8.0** (was 1.9.1): Windows Application Control on the dev laptop blocked two 1.9.1 binaries. Policy was not changed or bypassed.
- Bootstrap 95% CI is saved (`high_recall_ci95`) but collapses to [1.00, 1.00] when every case is caught, so the write-up should quote the Wilson interval (`high_recall_wilson95`).

### Sun Nov 15, 18:30 — Phase 0 + Phase 1 done
- Scope cuts applied (table above); `PLAN.md` re-timed from the real 18:00 start.
- Phase 0: renamed `CLAUDE (4).md` → `CLAUDE.md`; created folders; `.venv` on Python 3.12.6; `requirements.txt` pinned (pandas 3.1.1, numpy 2.5.4, scikit-learn 1.9.1, matplotlib 3.11.2, ucimlrepo 0.0.7, joblib 1.6.0, pytest 9.2.0).
- Phase 1: `pipeline/01_load_clean.py`, `pipeline/02_split.py`, `pipeline/units.py`, `tests/test_no_leak.py`, `tests/test_units.py`, `pytest.ini`. Outputs: `data/raw/maternal_health_risk.csv`, `data/processed/{clean,train,test}.csv`, `results/cleaning_log.json`. `pytest -q` → 5 passed.
- **Decision — conflicting duplicates: drop the whole group** (not keep-majority). Reason: majority would have to be counted from the repeated rows, which are likely copy artefacts, and many groups are 2-vs-2 ties. Dropping also guarantees each set of vitals appears once, so train and test can never share one. Cost: 71 rows, including 11 high-risk label rows.
- **Decision — ages > 60 kept** (7 rows), flagged as a limitation rather than deleted.
- 18:50 — developer review applied: scope-cut pointer at top of `CLAUDE.md`, approval-before-commit rule in `CLAUDE.md` §11, Phase 3 additions in `PLAN.md`, `.DS_Store` in `.gitignore`. No "(1)"-style duplicate files left locally; the remote's `CLAUDE (4).md` is renamed to `CLAUDE.md` by this commit.

### Sun Nov 15, 11:05 — planning update
- Submission clarified: public GitHub repo = code **and** write-up (README). Colab is optional → add `notebooks/walkthrough.ipynb` in Phase 6.
- Website = showcase, not required; AI pipeline + evaluation first.
- Data roles fixed (training / testing / detection) — see `DATA.md` §2.
- Reproducibility: commit UCI CSV, `web/model.json`, `models/sigapbumil_lr.joblib`, `results/`; pin versions; Colab clones the repo (no uploads).
- Added `SETUP.md` (VS Code + Claude Code, GitHub Pages, Colab, HF fallback). Timeline shifted ~1 h.

### Sun Nov 15 — Phase 0
- Planning done in chat; docs written (CLAUDE.md, PLAN.md, DESIGN.md, DATA.md, WEB-SPEC.md, README.md skeleton).
- Deploy target decided: static site on GitHub Pages with in-browser LR inference (no backend). Fallback: Gradio on Hugging Face Spaces.
