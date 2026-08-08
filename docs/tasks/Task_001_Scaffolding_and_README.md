# Task 001: Project Scaffolding, Environment Setup, and README

**For:** Codex (execution steps below)
**Prerequisite (User — do this BEFORE handing this file to Codex):**
1. Create a new empty GitHub repository (public or private, your call).
2. Clone it to your local machine.
3. Open the cloned repo folder in your terminal/editor — this is the working directory Codex should operate in.
4. Have your confidential Syn Bank CSVs (transactional, SWIFT, trade finance) ready on your local machine, but **do not place them in the repo yet** — Codex will create the correct folder for them in this task, and you'll drop them in only after `.gitignore` is confirmed working (see Testing section).
5. Attach or paste the finished `README.md` content (the detailed version with team, build phases, owners, and checkpoints already drafted) alongside this task file — Codex needs it verbatim for Step 5 below, it will not write its own.

---

## Why?

This is a 9-day hackathon build across two people with no prior finance background. Before any data or modeling work starts, we need a clean, reproducible project structure that:
- Keeps confidential client data (CSVs) out of git history — a leak here would violate the hackathon's confidentiality rules.
- Uses a dependency setup (`venv` + `requirements.txt`) that judges can reproduce trivially when they clone the repo, since a "requirements file or equivalent" is an explicit deliverable in the brief.
- Has a README that documents the team, the problem, the architecture, and — critically — tracks build progress phase by phase, since this doc is what both teammates and (eventually) judges will read first.

Getting this right now avoids painful git history cleanup later if data gets committed by accident.

---

## Steps for Codex

### 1. Create folder structure
At the repo root, create:
```
data/                  # local-only, gitignored — raw CSVs live here
notebooks/              # exploratory + final reproducible notebook(s)
src/                     # reusable Python modules (ingestion, clustering, wallet calc, genai)
dashboard/               # Streamlit app
docs/
  tasks/                 # archive of every Codex task markdown file used in this project
outputs/                 # generated artifacts: charts, exported briefings, final PDF/PPTX drafts
```
Add a `.gitkeep` file inside `data/` and `outputs/` so the empty folders are tracked by git even though their contents won't be.

### 2. Create `.gitignore`
At repo root, create `.gitignore` with at minimum:
```
# Environments
venv/
.venv/
__pycache__/
*.pyc

# Secrets
.env

# Confidential data — never commit real data files
data/*
!data/.gitkeep

# OS/editor cruft
.DS_Store
.vscode/
.ipynb_checkpoints/
```

### 3. Create `requirements.txt`
Pin loose (no exact versions yet, just the core set — we'll tighten later):
```
pandas
numpy
scikit-learn
streamlit
plotly
google-generativeai
python-dotenv
pytest
```

### 4. Create `.env.example`
```
GEMINI_API_KEY=your_key_here
```
This is a template only — the real `.env` (gitignored) will hold the actual key later, added by the user, not Codex.

### 5. Add `README.md`
**Do not generate a new README from scratch.** A finished, detailed README has
already been written and reviewed separately — it includes the team, problem
statement, design-decision rationale, a 9-phase build plan with owners/subtasks/
checkpoints per phase, tech stack, evaluation alignment, and a Progress Log section.

The user will paste or attach that finished `README.md` content alongside this task
file. Copy it into the repo root **verbatim** as `README.md`. Do not summarize,
shorten, or restructure it.

If the finished README content is missing when this task is run, stop and ask the
user for it rather than generating a placeholder — a generated placeholder would
conflict with and likely get overwritten by the real one, wasting the effort.

### 6. Add the update-instruction comment (for all future tasks)
Add this as an HTML comment directly under the title `# Syn Bank Share of Wallet
Intelligence Engine` in `README.md`, so it doesn't render visibly but guides every
future task:
```
<!-- Codex: at the end of every task markdown file executed in this project, update
README.md as follows: (1) tick the completed subtask checkboxes under the relevant
phase's detailed section, (2) flip that phase's Status in the "Build Phases" summary
table to the correct state (⬜ Not started / 🟨 In progress / ✅ Done), (3) once the
phase's checkpoint testing has been confirmed passing by the user, change that
phase's checkpoint marker from 🔲 to ✅ and prefix it "passed", (4) append a new
one-line dated entry to the "## Progress Log" section at the bottom summarising what
was done. Do not skip any of these four — they can drift out of sync with each other
if only some are updated. -->
```
The `## Progress Log` section already exists at the bottom of the provided README
with one entry for the planning phase — leave it in place and append to it, don't
overwrite it.

### 7. Initial commit
Stage and commit everything created in this task (folder structure, `.gitignore`, `requirements.txt`, `.env.example`, `README.md`) with commit message:
`chore: project scaffolding, env setup, and README`

Do NOT commit any real data files — none should exist in the repo yet at this stage.

---

## Testing Instructions (for you, the User — verify before moving to Task 002)

1. **Folder structure check**: run `ls -la` (or open the folder in your file explorer) and confirm `data/`, `notebooks/`, `src/`, `dashboard/`, `docs/tasks/`, `outputs/` all exist.
2. **Venv check**: run `python -m venv venv && source venv/bin/activate` (or the Windows equivalent) and confirm it activates without error.
3. **Install check**: run `pip install -r requirements.txt` and confirm it completes without errors.
4. **Gitignore check — this is the important one given the confidential data**:
   - Drop one of your real (confidential) CSV files into `data/`.
   - Run `git status`. The CSV must **NOT** appear as an untracked/staged file. Only `data/.gitkeep` should ever be tracked.
   - If the CSV shows up in `git status`, STOP — do not commit or push. Go back and fix `.gitignore` before proceeding (see Debugging note below).
5. **README check**: open `README.md` on GitHub (after pushing) and confirm it renders cleanly — headings, the Build Phases summary table, every per-phase checklist, the checkpoint markers, and code blocks should all display properly, not as raw markdown text. Confirm it's the full detailed version (with per-phase owners and checkpoints) and not a shorter placeholder — this is the easiest place for the wrong file to slip in if Codex ignored Step 5's instruction to use the provided version.
6. **Env check**: confirm `.env.example` exists and is tracked by git, but if you create a real `.env` file with an actual key in it, confirm `git status` does NOT show `.env` as trackable.

### If something breaks (debugging steps)
- If the CSV still shows up under `git status` despite being in `data/`: check that the `.gitignore` pattern is exactly `data/*` with `!data/.gitkeep` as an exception line directly under it, and that `.gitignore` sits at the repo **root**, not inside a subfolder.
- If `.gitignore` rules aren't taking effect on a file that was previously committed accidentally: that means git is still tracking it from before — this needs `git rm --cached <file>` to untrack it, then commit that removal, before `.gitignore` will take effect on it going forward. If this happens, stop and flag it before pushing, since it means the file was briefly in git history.
- If `pip install` fails: check the Python version with `python --version` — this project targets Python 3.10+. If you're on an older version, note it and we'll adjust.

---

## Next Task
Once all testing checks above pass, move to **Task 002 — Data Ingestion & Profiling**.
