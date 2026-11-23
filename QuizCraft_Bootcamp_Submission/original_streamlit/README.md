# 🧠 QuizCraft — AI Question Generator

**Generative AI Bootcamp | Project 20**

A working Python/Streamlit app that converts lesson notes into multiple-choice and short-answer questions using the **Google Gemini API**. Teachers can edit the generated questions, verify the suggested answers, mark questions as approved, and download a CSV/JSON answer key. A student-preview tab provides MCQ scoring and written-answer self-review.

## Features

- Paste lesson notes or upload a `.txt` / `.md` file.
- Choose **2–12 questions**, multiple-choice, short-answer, or a mixture.
- Choose **Beginner / Intermediate / Advanced** and **English / Spanish**.
- Generate structured questions using **Gemini 3.5 Flash-Lite** and the official `google-genai` SDK.
- Include the answer key, brief explanations, and supporting lesson excerpts.
- **Teacher review:** edit options, questions, explanations, correct answers, approve/unapprove, or delete.
- **Student preview:** answer MCQs and written questions; automatic MCQ score, written-answer model key.
- Export all questions or approved questions as **CSV (Excel-friendly) or JSON**.
- **Offline demo:** explore six prewritten questions without an API key or internet access.
- Includes offline tests that **do not spend API credits**.

## Architecture

```text
Streamlit (interface)
       |
       v
quiz_engine.py (prompt, output validation, scoring, exports)
       |
       v
Google Gemini API (AI generation)
       |
       v
Current browser session (temporary quiz state)
       |
       v
CSV / JSON download (saved deliverable)
```

No database is required. The app does not persist lessons or quizzes to a database; Streamlit holds the current session in memory. Export the quiz if you need to keep it.

## 1. Get a free Gemini API key

1. Open [Google AI Studio — API keys](https://aistudio.google.com/api-keys).
2. Sign in to your Google account.
3. Create a Gemini API key (free-tier availability and limits depend on the model/account/region).
4. **Never share your key, put it into screenshots, or upload your `.env` to GitHub.**

See [official Gemini pricing and free tiers](https://ai.google.dev/gemini-api/docs/pricing).

> **Privacy:** Google's free API tier may be used to improve Google's products. Use public, fictitious, or properly authorized lesson notes. Don't paste confidential student, medical, or company data.

## 2. Install and run (Windows)

You need **Python 3.10+**, a terminal such as PowerShell, and internet access when calling Gemini.

```powershell
cd AI_Question_Generator
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

In `.env`, enter your actual key:

```dotenv
GEMINI_API_KEY=your_real_key_goes_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Then launch:

```powershell
streamlit run app.py
```

If activation is blocked by PowerShell policy, skip the activation and use the virtual environment explicitly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

## 3. Install and run (macOS / Linux)

```bash
cd AI_Question_Generator
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` in your favorite editor, set `GEMINI_API_KEY=...`, then run:

```bash
streamlit run app.py
```

### Troubleshooting: model not found (404)

Google limits access to older Gemini 2.5 models for new API projects. If your
app displays `Gemini could not access model`, make sure your `.env` contains:

```dotenv
GEMINI_MODEL=gemini-3.5-flash-lite
```

Save `.env`, completely stop and restart Streamlit, and confirm that the
sidebar displays `Model: gemini-3.5-flash-lite`. If it still fails, open
[Google AI Studio](https://aistudio.google.com) and check which models your
project supports. Model names and free-tier availability can change.

## 4. Try the app

**Generate tab:** click **Load sample lesson**, set six mixed questions, and click **Generate questions with Gemini**. If you do not have a key, click **Open offline demo** (prewritten questions, not AI output).

**Teacher review tab:** open a question, change its wording or option, choose the correct answer, check **Approved for student use**, and click **Save changes**. Download the questions as CSV/JSON.

**Student preview tab:** take the quiz and click **Check answers**. Only multiple-choice questions are automatically scored; short answers require human/self review.

## 5. Run tests

From the project folder:

```bash
python -m pytest -q
```

The tests verify input validation, MCQ and short-answer formats, type distribution, Gemini response parsing with a fake API client, a retry on malformed model output, answer-key consistency, CSV/JSON exports, and scoring. **No real Gemini requests occur in the tests.** See `TEST_REPORT.md` for the checks performed during project preparation and what to verify locally.

## Project files

```text
AI_Question_Generator/
├── app.py                    # Streamlit web app and interface
├── quiz_engine.py            # Gemini integration, models, scoring, exporting
├── requirements.txt          # Python packages
├── .env.example              # Example API key configuration (safe to commit)
├── .gitignore                # Prevents accidentally committing secrets
├── .streamlit/
│   └── config.toml           # Colors and UI theme
├── sample_lesson.txt         # Public, sample AI lesson
├── tests/
│   └── test_quiz_engine.py   # Offline unit tests
├── PRESENTATION_GUIDE.md     # Demo outline and submission checklist
├── TEST_REPORT.md            # Tests completed and remaining live checks
└── README.md
```

**Sample input source:** `sample_lesson.txt` is an original, non-confidential educational summary created for this demonstration. No private user data is included.

## Technical choices

- **Python**: main programming language.
- **Streamlit**: fast web application interface, avoiding custom HTML/JS.
- **Gemini Developer API**: generates questions from teacher notes.
- **`google-genai` SDK + Pydantic**: request a structured JSON schema, then validate the result before showing it.
- **Session state**: keep generated and edited questions available while navigating tabs.
- **CSV/JSON**: make question banks easy to save and inspect.
- **Git/GitHub**: commit code, tests, sample notes, and documentation without credentials.

## Limitations / known issues

1. Questions and explanations are **AI-generated** and may be wrong, ambiguous, or insufficiently supported. A teacher should review them.
2. Supporting quotes are removed if they cannot be matched to the provided notes, but matching a quote does **not** prove the model's whole answer is correct.
3. Short answers are **not automatically graded** because worded answers need interpretation.
4. There are request/token limits on the Gemini free tier; a 429 / quota response means the limit was reached.
5. Lesson files must be UTF-8 `.txt` or `.md`. PDFs and Word files are not included in this MVP.
6. No account system, shared storage, or long-term history is included; current data is lost when the session ends unless downloaded.
7. Quiz validation checks structure, question count, and answer key consistency, but does not independently fact-check Gemini responses.

## Optional: publish on Streamlit Community Cloud

1. Push the project to GitHub **without `.env`**.
2. In Streamlit Community Cloud, deploy `app.py` from the repository.
3. Under application **Secrets**, enter:

```toml
GEMINI_API_KEY = "your-real-key"
GEMINI_MODEL = "gemini-3.5-flash-lite"
```

4. Save and redeploy. **Do not put real keys into public repository files.** See [Streamlit secrets documentation](https://docs.streamlit.io/develop/api-reference/connections/st.secrets).

## Useful documentation

- [Gemini Python SDK](https://googleapis.github.io/python-genai/)
- [Gemini models and pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Streamlit docs](https://docs.streamlit.io/)

---

**Bootcamp category:** OpenAI/Hugging Face Model Integration — selected assignment: *Project 20: AI Question Generator.* This solution uses **Gemini instead of the suggested APIs** to meet the same functional requirements. Verify with your instructor that substitutions are permitted if a named provider is mandatory.
