# QuizCraft — AI Question Generator (Project 20)

**A ready-to-run bootcamp submission and a project you can learn from.**

QuizCraft turns teacher lesson notes into multiple-choice and short-answer practice questions using Google's Gemini API. The teacher can edit and approve questions, students can preview the approved quiz, and the teacher can export a CSV or JSON question bank.

## Where to start

| File / folder | Purpose |
|---|---|
| **`vercel_app/`** | The version to run, study, upload to GitHub, and deploy on Vercel (recommended). |
| `vercel_app/index.py` | FastAPI endpoints; handles the browser's requests. |
| `vercel_app/quiz_service.py` | Builds the prompt, calls Gemini, validates the generated questions. |
| `vercel_app/public/` | User interface written in HTML, CSS, JavaScript. |
| `vercel_app/tests/` | Offline automated tests of the backend. |
| **`presentation/QuizCraft_Bootcamp_Presentation.pptx`** | Editable class presentation. |
| **`docs/HANDS_ON_GUIDE.md`** | Learn and modify the code in 5 exercises. |
| **`docs/DEPLOY_TO_VERCEL.md`** | Step-by-step GitHub and Vercel deployment, including screenshots checklist. |
| **`docs/LIVE_DEMO_SCRIPT.md`** | Three-minute class demo and likely instructor questions. |
| `original_streamlit/` | A backup of the earlier Streamlit-only version (not deployable to GitHub Pages). |

## Quick start (Windows PowerShell)

Open a terminal in the `vercel_app` folder:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
notepad .env
```

Set your own Gemini API key in `.env`. Keep this file private.

```ini
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
DEMO_ACCESS_CODE=
```

Start the local website:

```powershell
.venv\Scripts\python.exe -m uvicorn index:app --reload
```

Open **http://127.0.0.1:8000/**. Explore the **Try offline demo** button even if Gemini is temporarily unavailable.

Run the automated tests in a separate terminal:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

macOS/Linux commands, deployment steps, and troubleshooting are in `docs/DEPLOY_TO_VERCEL.md`.

## Architecture at a glance

```text
Browser (HTML/CSS/JavaScript)
  |
  | POST /api/generate { lesson, total, mode, difficulty, language }
  v
Python FastAPI             <-- GEMINI_API_KEY stored in server environment
  |
  v
Quiz service (Pydantic validation + carefully written prompt)
  |
  | HTTPS request with private x-goog-api-key header
  v
Google Gemini API
  |
  | JSON question bank
  v
Python checks question counts, correct options, source excerpts
  |
  v
Browser: teacher reviews -> student preview -> CSV / JSON export
```

## Requirements covered

- Accept teacher lesson text (paste or upload .txt / .md).
- Generate multiple-choice and short-answer questions using Gemini.
- Include correct answers and explanations.
- Provide an editable teacher review, with explicit approval.
- Show approved questions in student preview; grade multiple-choice only.
- Export CSV/JSON; clearly identify prewritten offline demo questions.
- Use Git/GitHub source control and deploy a Python API on Vercel.
- Include PowerPoint, a demo script, and tests.

## Important limits

This is a **class prototype**, not a production exam platform. Edits are not saved to a database and disappear when the browser is refreshed; download the questions before closing the page. Students can inspect the answer keys in their browser (do not use it for a secure exam). Written answers are displayed for self-review, not automatically graded. AI outputs may be incorrect even after structural validation, so a teacher must verify them. No rate-limiting, user login, or persistent audit log is implemented. For a public demo, use a nontrivial `DEMO_ACCESS_CODE` in Vercel and monitor your Gemini API quota; a simple access code is not a production security control.

**Do not upload real student records, medical information, secrets, or confidential company materials.** On Gemini free-tier projects, Google may use submitted content to improve products, subject to Google's applicable terms.

## Verification status

- **26 automated offline backend/API tests passed** locally using mocked Gemini responses.
- Local FastAPI service successfully responded to root `/` and `/api/health`.
- Static JavaScript passed Node syntax validation.
- **Not yet verified:** real Gemini generation with your API key, real-browser end-to-end interaction, and deployment on your Vercel account. Your own live demo should verify these steps.

Reference docs: [FastAPI on Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing), [Vercel environment variables](https://vercel.com/docs/environment-variables).
