# PLAN.md — phases and timeline

All times **WIB (UTC+7)**. Deadline Mon Nov 16 11:59 WIB. **Hard stop 11:30.**
Rule: if a step is stuck > 30 min, take the fallback and log it in `HANDOFF.md`.

---

## Phase 0 — Setup · Sun 10:00–10:30
- [ ] Public repo `sigapbumil` created (README, Python .gitignore, MIT)
- [ ] Docs committed: CLAUDE.md, PLAN.md, DESIGN.md, DATA.md, WEB-SPEC.md, HANDOFF.md, README.md, requirements.txt
- [ ] Folders: data/raw, data/processed, pipeline, results, web, tests
- [ ] `.venv` + `pip install -r requirements.txt` works
- **Done when:** Claude Code opens the repo and has read CLAUDE.md.

## Phase 1 — Data · 10:30–11:30
- [ ] `01_load_clean.py`: load UCI 863, save raw, inspect, sanity checks
- [ ] Count + drop duplicates; count conflicting duplicates → fill `DATA.md` §4
- [ ] `02_split.py`: stratified 80/20 → `data/processed/`
- [ ] Download + check external dataset (`DATA.md` §3) — max 30 min, else drop E3
- [ ] `tests/test_no_leak.py`, `tests/test_units.py`
- **Done when:** clean train/test files exist, cleaning log filled, tests pass.

## Phase 2 — Baselines + models · 11:30–13:30
- [ ] `03_baselines.py`: B0 majority, B1 clinical rule (CV on train)
- [ ] `04_models.py`: M1 LR, M2 tree; 5-fold CV; out-of-fold predictions
- [ ] Threshold tuning for high-risk recall ≥ 0.90 → `results/threshold_curve.png`
- [ ] CV comparison table → `results/cv_comparison.json`
- **Done when:** one table compares B0, B1, M1, M2 on CV (high recall, FN, FP, macro-F1).

## Break · 13:30–14:30

## Phase 3 — Own contribution + final eval · 14:30–17:30
- [ ] `05_final_eval.py`: run **once** on test → `results/test_metrics.json`, confusion matrices
- [ ] `06_experiments.py`: E1 duplicate leakage, E2 age groups, E3 external, E4 failure cases
- [ ] `results/summary.json`
- [ ] HANDOFF.md: "How to explain to judges" bullets for every result
- **Done when:** all results files exist and are frozen.

## Phase 4 — Export + parity · 17:30–18:30
- [ ] `07_export.py` → `web/model.json`, `web/test_cases.json`
- [ ] `tests/test_parity.mjs` passes
- **Done when:** JS predictions = Python predictions.

## Phase 5 — Web app + deploy · 18:30–22:00
- [ ] `web/index.html`, `style.css`, `app.js` per `WEB-SPEC.md`
- [ ] Bilingual labels, units, validation, examples, result card, reasons, How-it-works, limitations
- [ ] `.github/workflows/pages.yml`; Pages source = GitHub Actions
- [ ] Test on phone + incognito + offline reload
- **Fallback (if blocked by 21:00):** Gradio app on Hugging Face Spaces using the saved model.
- **Done when:** a stranger can open the public URL and get a result.

## Phase 6 — Write-up · 22:00–23:30
- [ ] Fill `README.md` (hackathon template) from `results/summary.json`
- [ ] Disclaimer, limitations, sources (datasets, libraries, Claude, Claude Code), links (live site, video)
- **Done when:** a judge understands the project in 2 minutes.

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
- [ ] **08:00 submit v1**: repo link, write-up (README), live site, video, credits
- [ ] 08:00–10:30 polish → resubmit
- [ ] 10:30–11:30 open every link in incognito; check names/emails; final resubmit
- [ ] **11:30 hard stop**
