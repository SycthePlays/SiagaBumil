# PLAN.md — phases and timeline

All times **WIB (UTC+7)**. Deadline Mon Nov 16 11:59 WIB. **Hard stop 11:30.**
Rule: if a step is stuck > 30 min, take the fallback and log it in `HANDOFF.md`.

> **Scope cuts (Sun 18:00, ~6 h behind schedule)** — these override any other doc:
> - **E3 external dataset: dropped.** No Mendeley download, no external test. README says "skipped for time".
> - **Tree-model grid search: skipped.** M2 = one `RandomForestClassifier(class_weight="balanced", random_state=42)` with default settings, comparison only.
> - **Hugging Face fallback: dropped.** GitHub Pages is the only deploy target.
> - **Dark mode: dropped.**
>
> Timeline below is re-based on the real start (Sun 18:00).

---

## Phase 0 — Setup · Sun 18:00–18:15 ✅
See `SETUP.md` for step-by-step tool setup.
- [ ] Public repo `sigapbumil` created (README, Python .gitignore, MIT) — **developer: the local folder is not a git repo yet**
- [ ] Repo cloned locally; GitHub sign-in works (`git push` succeeds) — **developer**
- [x] Docs present: CLAUDE.md, PLAN.md, DESIGN.md, DATA.md, WEB-SPEC.md, HANDOFF.md, SETUP.md, README.md, requirements.txt
- [x] Claude Code extension installed + signed in
- [x] Folders: data/raw, data/processed, models, notebooks, pipeline, results, web, tests
- [x] `.venv` + `pip install -r requirements.txt` works; **versions pinned** in requirements.txt

## Phase 1 — Data · Sun 18:15–18:30 ✅
- [x] `01_load_clean.py`: load UCI 863, save raw CSV to `data/raw/` (committed), inspect, sanity checks
- [x] Count + drop duplicates; count conflicting duplicates → `DATA.md` §5 filled
- [x] `02_split.py`: stratified 80/20 → `data/processed/`
- [x] ~~External dataset check~~ — cut (E3 dropped)
- [x] `tests/test_no_leak.py`, `tests/test_units.py` — 5 passed
- **Done when:** clean train/test files exist, cleaning log filled, tests pass.

## Phase 2 — Baselines + models · Sun 18:30–19:45
- [ ] `03_baselines.py`: B0 majority, B1 clinical rule (CV on train)
- [ ] `04_models.py`: M1 LR, M2 random forest (defaults, no grid); 5-fold CV; out-of-fold predictions
- [ ] Threshold tuning for high-risk recall ≥ 0.90 → `results/threshold_curve.png`
- [ ] CV comparison table → `results/cv_comparison.json`
- **Done when:** one table compares B0, B1, M1, M2 on CV (high recall, FN, FP, macro-F1).

## Phase 3 — Own contribution + final eval · Sun 19:45–21:00
- [ ] `05_final_eval.py`: run **once** on test → `results/test_metrics.json`, confusion matrices
- [ ] **Bootstrap 95% CI for high-risk recall** on the test set (only 20 high-risk rows → one miss = 5 points)
- [ ] **Show CV results next to test results** in every results table (`summary.json`, README, web)
- [ ] Limitations (README + web): add **"conflicting duplicates removed → remaining data is cleaner than real life, results may be slightly optimistic"**
- [ ] `06_experiments.py`: E1 duplicate leakage, E2 age groups, E4 failure cases (~~E3 external~~ cut)
- [ ] `results/summary.json`
- [ ] HANDOFF.md: "How to explain to judges" bullets for every result
- **Done when:** all results files exist and are frozen.

## Phase 4 — Export + parity · Sun 21:00–21:30
- [ ] `07_export.py` → `web/model.json`, `web/test_cases.json`, `models/sigapbumil_lr.joblib`
- [ ] Commit model files + `results/` (needed for Colab and judges)
- [ ] `tests/test_parity.mjs` passes
- **Done when:** JS predictions = Python predictions.

## Phase 5 — Web app + deploy · Sun 21:30–00:30
- [ ] `web/index.html`, `style.css`, `app.js` per `WEB-SPEC.md` (no dark mode)
- [ ] Bilingual labels, units, validation, examples, result card, reasons, How-it-works, limitations
- [ ] `.github/workflows/pages.yml`; Pages source = GitHub Actions
- [ ] Test on phone + incognito + offline reload
- **No fallback host.** If Pages is blocked, the repo + README + video are still a complete submission (the website is not required).
- **Done when:** a stranger can open the public URL and get a result.

## Sleep · 00:30–06:00

## Phase 6 — Write-up + Colab walkthrough · Mon 06:00–07:30
- [ ] Fill `README.md` (hackathon template) from `results/summary.json`; external dataset line → "skipped for time"
- [ ] Disclaimer, limitations, sources (datasets, libraries, Claude, Claude Code), links (live site, video, Colab)
- [ ] `notebooks/walkthrough.ipynb` per `DESIGN.md` §10 → run all in a **fresh** Colab runtime → File → Save a copy in GitHub (outputs visible) → `git pull` locally. *First thing to cut if Monday runs late — Colab is optional.*
- **Done when:** a judge understands the project in 2 minutes.

## Phase 7 — Demo video · Mon 07:30–09:00
Screen recording + voice, ≤ 2:00, upload to YouTube **unlisted**.
| Time | Content |
|---|---|
| 0:00–0:15 | Problem: maternal deaths in Indonesia; the bidan's decision moment |
| 0:15–1:15 | Demo: borderline mother → *Rujuk sekarang* + reasons; routine case |
| 1:15–1:45 | How it works: data, LR vs rule baseline, recall/FN/FP, duplicate-leakage finding |
| 1:45–2:00 | One limitation + next step (validate on Indonesian clinic data with real outcomes) |

## Phase 8 — Submit · Mon 09:00–11:30
- [ ] **09:00 submit v1** — form fields:
  - Track: **Health**
  - Code: GitHub repo link (public)
  - Write-up: same repo link (README) — or a Google Doc / PDF copy of it
  - Demo video: YouTube unlisted link
  - Live demo + Colab links: inside README (and on the form if there is a field)
  - What we added: own user/setting, duplicate-leakage finding, label-noise finding, ML vs rule, age groups
  - Credits: datasets, libraries, Claude, Claude Code
  - Team details: name, email, school — spelled correctly
- [ ] 09:00–10:30 polish → resubmit
- [ ] 10:30–11:30 open every link in incognito; check names/emails; final resubmit
- [ ] **11:30 hard stop**
