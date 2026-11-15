# SETUP.md — tools and connections

**GitHub is the single source of truth.** Code locally, push to GitHub; everything else pulls from it.

```
VS Code + Claude Code (local)  ──push──►  GitHub (public repo)
                                             ├──► GitHub Pages   (live site — main plan)
                                             ├──► Google Colab   (walkthrough notebook — optional extra)
                                             └──► Hugging Face   (Gradio Space — fallback only)
```

> **Public repo rule:** never put API keys, tokens or passwords in any file, notebook or commit. Use GitHub Secrets or the git password prompt only.

---

## 1. Local machine

Install: **Git**, **VS Code**, **Python 3.10+**, **Node.js** (for the JS parity test).

```bash
git clone https://github.com/SycthePlays/SigapBumil.git
cd SigapBumil
code .
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

GitHub auth for pushing: VS Code → Accounts icon (bottom-left) → sign in with GitHub (or `gh auth login` with GitHub CLI).

## 2. Claude Code in VS Code

1. Extensions view (`Ctrl+Shift+X` / `Cmd+Shift+X`) → search **"Claude Code"** → publisher **Anthropic** (`anthropic.claude-code`) → Install.
2. Open any file in the repo → click the **Spark** icon (it only appears when a file is open).
3. Sign in with your Claude account (browser opens).
4. If it doesn't show: restart VS Code or Command Palette → "Developer: Reload Window".
5. The panel bundles its own Claude Code; the `claude` command in the terminal needs the separate CLI install (not required).
6. First prompt:
   > Read CLAUDE.md, HANDOFF.md and PLAN.md. Do Phase 0, then Phase 1. Stop after Phase 1 and show results.
7. Approve edits and commands yourself; don't enable any skip-permissions mode.

Docs: https://code.claude.com/docs/en/vs-code

## 3. GitHub Pages (live site)

- Claude Code writes `.github/workflows/pages.yml` in Phase 5 (deploys `web/` on push to `main`).
- Repo → Settings → Pages → Source: **GitHub Actions**.
- URL: `https://sycthePlays.github.io/SigapBumil/` — test in incognito, on a phone, and offline after first load.

## 4. Google Colab (walkthrough notebook)

Why things "disappear" in Colab: the runtime is temporary — uploaded files are wiped when it disconnects/resets. The notebook file (code + saved outputs) persists. So **never upload by hand; clone the repo**.

```python
!git clone https://github.com/SycthePlays/SigapBumil.git
%cd SigapBumil
!pip install -q -r requirements.txt
```

- The trained model is already in the repo (`web/model.json`, `models/sigapbumil_lr.joblib`) → load it, predict, show `results/`.
- Save: **File → Save a copy in GitHub** → authorize → repo `sigapbumil`, branch `main`, path `notebooks/walkthrough.ipynb`, keep "Include a link to Colab" checked.
- Run all cells **before** saving so outputs are visible. Then `git pull` locally.
- Open later: Colab → File → Open notebook → GitHub tab → paste repo URL.
- Don't push from inside Colab with a token; edit code locally.

## 5. Hugging Face Space (fallback only — if Pages blocked by 21:00)

1. huggingface.co → New Space → SDK **Gradio** → Public → name `sigapbumil`.
2. Settings → Access Tokens → new token, role **Write**.
3. Push app files to the Space's own git repo:
   ```bash
   git clone https://huggingface.co/spaces/<hf-username>/sigapbumil hf-space
   # copy app.py, requirements.txt, model file into hf-space/
   cd hf-space && git add . && git commit -m "Add Gradio app" && git push
   ```
   Use the **HF token** when git asks for a password.
4. Optional auto-sync: store the token as GitHub secret `HF_TOKEN` and have Claude Code write a GitHub Action that pushes to the Space.

## 6. Not used

- **Vercel, Supabase**: not needed (no backend, no database; storing health inputs would create privacy risk).
- **Veritas hosting**: none exists; the hackathon only needs links (code, write-up, optional video).
