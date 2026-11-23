# Deploy QuizCraft on Vercel — guided checklist

> **Why Vercel?** GitHub Pages hosts static HTML/JS and cannot safely run the Python backend that holds your Gemini API key. Vercel supports Python FastAPI apps. The GitHub repository stores your code; Vercel serves the app online.

## A. Run locally first (Windows PowerShell)

1. Extract the ZIP (do not upload the ZIP to GitHub as a single file).
2. Open **VS Code → File → Open Folder** → choose `QuizCraft_Bootcamp_Submission/vercel_app`.
3. Open a terminal in that folder and run:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
notepad .env
```

4. Inside `.env`, replace `put_your_key_here` with the key from <https://aistudio.google.com/api-keys>. Set the model to `gemini-3.5-flash-lite`. For local development, leave `DEMO_ACCESS_CODE=` empty.
5. Run:

```powershell
.venv\Scripts\python.exe -m uvicorn index:app --reload
```

6. Open <http://127.0.0.1:8000/>. First click **Try offline demo**. Then **Load sample lesson → Generate with Gemini** (requires key/network).
7. Open <http://127.0.0.1:8000/api/health>. It should show `"status":"ok"` and `"gemini_configured":true`; it should **never show your key**.
8. With the server running, use a second terminal to run:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

**macOS/Linux equivalent:** create env with `python3 -m venv .venv`, install with `.venv/bin/python -m pip install -r requirements-dev.txt`, copy with `cp .env.example .env`, start with `.venv/bin/python -m uvicorn index:app --reload`.

## B. Publish the source on GitHub

1. Go to <https://github.com/new>, create a repository such as `quizcraft-ai-question-generator`, and **leave it empty** (skip adding a README because one already exists).
2. Open a terminal in the **submission root** `QuizCraft_Bootcamp_Submission` (one level above `vercel_app`). Run:

```powershell
git init
git branch -M main
git add .
git status
git commit -m "Build QuizCraft question generator and Vercel API"
git remote add origin https://github.com/YOUR_USERNAME/quizcraft-ai-question-generator.git
git push -u origin main
```

Change `YOUR_USERNAME` to your GitHub username. `git status` should NOT show `.env` or `.venv/` as staged files. If it does, stop and fix `.gitignore` before pushing.

**What each command means:** `git init` starts version tracking; `git add` stages changes; `git commit` saves a snapshot; `git remote add` points to your repository; `git push` publishes the commits. Each future push can trigger a new Vercel deployment.

**No Git installed?** Download Git from <https://git-scm.com/downloads> or use GitHub's **Add file → Upload files** to upload the *unpacked folder contents*, preserving `vercel_app/` as a subdirectory. Do not include `.env`.

## C. Import into Vercel

1. Go to <https://vercel.com/new>, sign in (GitHub is convenient) and select **Add New → Project**.
2. Import the `quizcraft-ai-question-generator` GitHub repository.
3. Set **Root Directory** to **`vercel_app`** (critical). Vercel should detect the FastAPI `app` object in `index.py` automatically. You normally do not need a custom build command or output directory.
4. Before clicking Deploy, open **Environment Variables** and add:

| Name | Value | Why |
|---|---|---|
| `GEMINI_API_KEY` | Your real Google AI Studio key | Lets **Python server** call Gemini. Never put it in browser JavaScript. |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` | Uses the newer supported model. |
| `DEMO_ACCESS_CODE` | A random private access code (optional but recommended publicly) | Limits casual public generation on your quota. |

5. Click **Deploy**. Vercel builds the Python function and serves `public/` static assets.
6. Open the deployment URL that **Vercel shows you**. Its format is typically `https://your-project.vercel.app`, but do not assume your exact URL.
7. If you add or change an environment variable **after** deployment, redeploy for the new value to take effect.

References: [Vercel FastAPI guide](https://vercel.com/docs/frameworks/backend/fastapi), [Git repository deployments](https://vercel.com/docs/git), [Environment variables](https://vercel.com/docs/environment-variables).

## D. Verify the public deployment (this completes the class requirement)

- [ ] Open your actual Vercel URL from a different browser window.
- [ ] Open `/api/health` and confirm server status and model; never expose the API key.
- [ ] Click **Try offline demo** — prewritten questions appear.
- [ ] Open **Teacher review**, edit an answer, and approve a question.
- [ ] Open **Student preview**, select answers, and click **Check my answers**.
- [ ] Open **Export** and download CSV or JSON.
- [ ] Add sample lesson notes and generate at least two **real** questions with Gemini. Enter the classroom access code if enabled.
- [ ] Save screenshots of the home page, generated quiz, approved questions, and score or export.
- [ ] Paste the **actual GitHub URL** and **actual Vercel URL** into your presentation before presenting.

## E. Common problems

| Symptom | What to check |
|---|---|
| Vercel shows 404 | Root Directory must be `vercel_app`; `index.py` must define `app = FastAPI(...)`; static files live in `public/`. |
| Gemini key missing | Add `GEMINI_API_KEY` to Vercel Project Settings → Environment Variables; then redeploy. |
| Gemini model unavailable | In Vercel Settings verify `GEMINI_MODEL=gemini-3.5-flash-lite`, verify key/model access in AI Studio, then redeploy. |
| Rate limit (429) | Free-tier quota exhausted; reduce requests or use **offline demo** to present. |
| Access code required | Enter your `DEMO_ACCESS_CODE` in the frontend field. Don't share publicly. |
| App works locally but not on Vercel | Check Vercel → Deployments → logs; confirm the `vercel_app` root and environment variables. |
| PowerShell won't activate the venv | Use `.venv\Scripts\python.exe` commands directly; activation is not required. |
| CSV empty | Approve one or more questions or uncheck “only approved”. |

## F. Known limitations and security notes

- Teacher changes live in browser memory, not a database. Download exports before closing/refreshing.
- No real user authentication, anti-abuse rate limiting, or persistent storage. `DEMO_ACCESS_CODE` is an **optional classroom guard**, not full security.
- Do not run a public deployment with a valuable paid key without access controls, budgets, monitoring, and quotas.
- Gemini model output can contain mistakes despite validation. A teacher must review correctness.
- Do not put `.env` into Git or paste your key into screenshots, presentations, or chat.

**Deployment status:** The files are ready for GitHub/Vercel. They have **not** been deployed to your accounts; you must log in and complete B–D to obtain a real public URL.
