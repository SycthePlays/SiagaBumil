# HANDOFF.md — session log

Claude Code: update this at the **end of every session/phase**. Newest entry on top.

---

## Current status

- **Phase:** 0 — Setup
- **Last updated:** Sun Nov 15, 11:05 WIB
- **Next step:** follow `SETUP.md` (local + Claude Code), create folders, pin requirements, set up `.venv`, then start Phase 1 (`pipeline/01_load_clean.py`).
- **Blockers:** none

---

## Open issues / decisions pending

- [ ] External dataset (Mojumdar, Mendeley) — usable? licence? units? (`DATA.md` §4)
- [ ] Deploy M1 (LR) vs M2 (tree) — decide after Phase 2 CV (`DESIGN.md` §5)
- [ ] Keep engineered features (PulsePressure, MAP)? — decide from CV

---

## How to explain to judges (fill after each phase)

*3–5 plain-language bullets per phase so the developer can defend every part.*

### Phase 1 — Data
- 

### Phase 2 — Baselines + models
- 

### Phase 3 — Results + experiments
- 

### Phase 5 — Web app
- 

---

## Log

### Sun Nov 15, 11:05 — planning update
- Submission clarified: public GitHub repo = code **and** write-up (README). Colab is optional → add `notebooks/walkthrough.ipynb` in Phase 6.
- Website = showcase, not required; AI pipeline + evaluation first.
- Data roles fixed (training / testing / detection) — see `DATA.md` §2.
- Reproducibility: commit UCI CSV, `web/model.json`, `models/sigapbumil_lr.joblib`, `results/`; pin versions; Colab clones the repo (no uploads).
- Added `SETUP.md` (VS Code + Claude Code, GitHub Pages, Colab, HF fallback). Timeline shifted ~1 h.

### Sun Nov 15 — Phase 0
- Planning done in chat; docs written (CLAUDE.md, PLAN.md, DESIGN.md, DATA.md, WEB-SPEC.md, README.md skeleton).
- Deploy target decided: static site on GitHub Pages with in-browser LR inference (no backend). Fallback: Gradio on Hugging Face Spaces.
