# HANDOFF.md — session log

Claude Code: update this at the **end of every session/phase**. Newest entry on top.

---

## Current status

- **Phase:** 1 done → next is Phase 2 (baselines + models)
- **Last updated:** Sun Nov 15, 18:30 WIB
- **Next step:** `pipeline/03_baselines.py` (B0, B1 on train CV), then `04_models.py` (LR + default random forest, 5-fold CV, threshold tuning).
- **Blockers:** none. Repo: https://github.com/SycthePlays/SiagaBumil (branch `main`).
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
- [ ] Phase 3 additions (developer review): bootstrap 95% CI for high-risk recall; CV results beside test results; "conflicting duplicates removed" in limitations (already added to `DESIGN.md` §11 and `README.md`).
- [ ] Deploy M1 (LR) vs M2 (tree) — decide after Phase 2 CV (`DESIGN.md` §5)
- [ ] Keep engineered features (PulsePressure, MAP)? — decide from CV
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

### Phase 2 — Baselines + models
- 

### Phase 3 — Results + experiments
- 

### Phase 5 — Web app
- 

---

## Log

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
