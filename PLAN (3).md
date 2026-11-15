# PLAN.md — phases and timeline

All times **WIB (UTC+7)**. Deadline Mon Nov 16 11:59 WIB. **Hard stop 11:30.**
Rule: if a step is stuck > 30 min, take the fallback and log it in `HANDOFF.md`.

---

## Phase 0 — Setup · Sun 11:15–11:45
See `SETUP.md` for step-by-step tool setup.
- [ ] Public repo `sigapbumil` created (README, Python .gitignore, MIT)
- [ ] Docs committed: CLAUDE.md, PLAN.md, DESIGN.md, DATA.md, WEB-SPEC.md, HANDOFF.md, SETUP.md, README.md, requirements.txt
- [ ] Repo cloned locally, opened in VS Code; GitHub sign-in works (`git push` succeeds)
- [ ] Claude Code extension installed + signed in
- [ ] Folders: data/raw, data/processed, models, notebooks, pipeline, results, web, tests
- [ ] `.venv` + `pip install -r requirements.txt` works; **versions pinned** in requirements.txt
- **Done when:** Claude Code opens the repo and has read CLAUDE.md.

> Timeline note: setup starts ~1 h later than first planned. Phases 1–3 below are shifted; if Phase 3 runs late, cut E3 (external dataset) before cutting anything else.

## Phase 1 — Data · 11:45–12:45
- [ ] `01_load_clean.py`: load UCI 863, save raw CSV to `data/raw/` (committed), inspect, sanity checks
- [ ] Count + drop duplicates; count conflicting duplicates → fill `DATA.md` §5
- [ ] `02_split.py`: stratified 80/20 → `data/processed/`
- [ ] Download + check external dataset (`DATA.md` §4) — max 30 min, else drop E3
- [ ] `tests/test_no_leak.py`, `tests/test_units.py`
- **Done when:** clean train/test files exist, cleaning log filled, tests pass.

## Phase 2 — Baselines + models · 12:45–14:30
- [ ] `03_baselines.py`: B0 majority, B1 clinical rule (CV on train)
- [ ] `04_models.py`: M1 LR, M2 tree; 5-fold CV; out-of-fold predictions
- [ ] Threshold tuning for high-risk recall ≥ 0.90 → `results/threshold_curve.png`
- [ ] CV comparison table → `results/cv_comparison.json`
- **Done when:** one table compares B0, B1, M1, M2 on CV (high recall, FN, FP, macro-F1).

## Break · 14:30–15:00

## Phase 3 — Own contribution + final eval · 15:00–17:45
- [ ] `05_final_eval.py`: run **once** on test → `results/test_metrics.json`, confusion matrices
- [ ] `06_experiments.py`: E1 duplicate leakage, E2 age groups, E3 external, E4 failure cases
- [ ] `results/summary.json`
- [ ] HANDOFF.md: "How to explain to judges" bullets for every result
- **Done when:** all results files exist and are frozen.

## Phase 4 — Export + parity · 17:45–18:30
- [ ] `07_export.py` → `web/model.json`, `web/test_cases.json`, `models/sigapbumil_lr.joblib`
- [ ] Commit model files + `results/` (needed for Colab and judges)
- [ ] `tests/test_parity.mjs` passes
- **Done when:** JS predictions = Python predictions.

## Phase 5 — Web app + deploy · 18:30–22:00
- [ ] `web/index.html`, `style.css`, `app.js` per `WEB-SPEC.md`
- [ ] Bilingual labels, units, validation, examples, result card, reasons, How-it-works, limitations
- [ ] `.github/workflows/pages.yml`; Pages source = GitHub Actions
- [ ] Test on phone + incognito + offline reload
- **Fallback (if blocked by 21:00):** Gradio app on Hugging Face Spaces using the saved model.
- **Done when:** a stranger can open the public URL and get a result.

## Phase 6 — Write-up + Colab walkthrough · 22:00–23:45
- [ ] Fill `README.md` (hackathon template) from `results/summary.json`
- [ ] Disclaimer, limitations, sources (datasets, libraries, Claude, Claude Code), links (live site, video, Colab)
- [ ] `notebooks/walkthrough.ipynb` per `DESIGN.md` §10 → run all in a **fresh** Colab runtime → File → Save a copy in GitHub (outputs visible) → `git pull` locally
- **Done when:** a judge understands the project in 2 minutes, and the notebook shows outputs when opened from GitHub in incognito.

## Sleep · 00:00–06:00

## Phase 7 — Demo video · Mon 06:00–07:30
Screen recording + voice, ≤ 2:00, upload to YouTube **unlisted**.
| Time | Content |
|---|---|
| 0:00–0:15 | Problem: maternal deaths in Indonesia; the bidan's decision moment |
| 0:15–1:15 | Demo: borderline mother → *Rujuk sekarang* + reasons; routine case |
| 1:15–1:45 | How it works: data, LR vs rule baseline, recall/FN/FP, duplicate-leakage finding |
| 1:45–2:00 | One limitation + next step (validate on Indonesian clinic data with real outcomes) |

## Phase 8 — Submit · Mon 08:00–11:30
- [ ] **08:00 submit v1** — form fields:
  - Track: **Health**
  - Code: GitHub repo link (public)
  - Write-up: same repo link (README) — or a Google Doc / PDF copy of it
  - Demo video: YouTube unlisted link
  - Live demo + Colab links: inside README (and on the form if there is a field)
  - What we added: own user/setting, duplicate-leakage finding, ML vs rule, age groups, external test
  - Credits: datasets, libraries, Claude, Claude Code
  - Team details: name, email, school — spelled correctly
- [ ] 08:00–10:30 polish → resubmit
- [ ] 10:30–11:30 open every link in incognito; check names/emails; final resubmit
- [ ] **11:30 hard stop**
