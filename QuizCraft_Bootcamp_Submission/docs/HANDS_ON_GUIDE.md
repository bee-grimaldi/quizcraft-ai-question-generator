# Hands-on guide: learn QuizCraft by changing it

The goal is **not only to submit** QuizCraft; it's to understand enough to explain and modify it confidently. This is a short beginner-friendly coding lab you can do in VS Code. All example questions and lesson text are non-confidential.

## 0. The mental model

Think of the app as a restaurant:

| Software piece | Restaurant analogy | In this project |
|---|---|---|
| **HTML** | Tables/menu visible to customers | The form and question cards in `public/index.html`. |
| **CSS** | Interior design | Colors, spacing and layout in `public/style.css`. |
| **JavaScript** | Waiter | Collects button clicks and sends requests in `public/app.js`. |
| **FastAPI / Python** | Kitchen | Checks the order, uses Gemini, returns a quiz in `index.py`. |
| **Gemini model** | Recipe assistant | Generates new questions based on lesson notes. |
| **Pydantic** | Quality inspector | Rejects incomplete or malformed questions in `quiz_service.py`. |
| **GitHub** | Versioned recipe book | Stores your project code and history. |
| **Vercel** | Restaurant storefront | Hosts the site and Python backend online. |

**Important:** The API is simply an agreed way for two programs to exchange data. Our browser calls a URL, and Python returns JSON: a structured text format with fields such as `"question"`, `"options"` and `"correct_option"`.

### How the data moves

```text
Teacher types lesson notes
  → JS takes lesson text + settings
  → POST /api/generate sends JSON
  → FastAPI validates with GenerationRequest
  → quiz_service.make_prompt() creates clear AI instructions
  → Gemini returns question JSON
  → Pydantic checks number, types, options and answer keys
  → Browser displays questions
  → Teacher edits and approves
  → Student preview; downloads CSV or JSON
```

## Lab 1 — Run it and understand the input (10 minutes)

1. Follow `DEPLOY_TO_VERCEL.md`, section A. If you don't have a valid key yet, use **Try offline demo**.
2. Click **Load sample lesson** and change Questions to `4`, Format to `Mixed`, Difficulty to `Beginner`.
3. Generate if Gemini works; otherwise inspect the demo questions.
4. Open `public/index.html` and search for `id="question-count"`. This is the dropdown you just used.
5. In `public/app.js`, search for `function quizConfig()`. It reads the values from the HTML elements and builds a JavaScript object.

**Try it yourself:** Change the default `<option selected>6</option>` to `<option selected>4</option>` and refresh the page. **Expected result:** the form now starts at 4 questions.

**What to say in class:** “The frontend collects user settings into an object. When the user clicks Generate, it sends those settings as JSON to the Python backend.”

## Lab 2 — Learn the backend (10 minutes)

Open `vercel_app/index.py`. Locate:

```python
@app.post('/api/generate', response_model=Quiz)
def generate(request: GenerationRequest, x_demo_access: str | None = Header(default=None)) -> Quiz:
    ...
```

- `@app.post('/api/generate')`: creates a POST endpoint — a URL that accepts data.
- `request: GenerationRequest`: asks Pydantic to check the incoming lesson, question count, difficulty, etc.
- `response_model=Quiz`: documents/validates the shape of what we send back.
- `x_demo_access`: an optional access code header; no API key is sent from the browser.

**Try it yourself:** Open `http://127.0.0.1:8000/docs`. FastAPI creates interactive API documentation automatically. Find `/api/sample`, click **Try it out → Execute**, and inspect the JSON result. Then click `/api/health`. It shows whether a Gemini key is configured **without revealing it**.

**What to say in class:** “FastAPI acts as a secure intermediary between the browser and Gemini.”

## Lab 3 — Understand prompt engineering (15 minutes)

Open `vercel_app/quiz_service.py`, find `make_prompt()`.

This function creates a text instruction containing five things: **role** (teacher), **task** (create quiz), **context** (lesson), **constraints** (ground answers in notes), and **output format** (JSON, specific question types). This is called **prompt engineering**.

Search for this line:

```python
Cover DIFFERENT concepts; avoid ambiguous wording and obvious distractors.
```

**Try it yourself:** Add this *inside the triple-quoted prompt*:

```text
Prefer questions that test understanding rather than memorizing definitions.
```

Restart the server and generate questions from the same lesson. Compare with the previous output; results vary because LLMs are probabilistic.

**What to say in class:** “Prompt design matters: it determines what context the model uses, which outputs we expect, and what rules it should follow.”

## Lab 4 — Understand structured data and validation (15 minutes)

Open `quiz_service.py` and look at:

```python
class GenerationRequest(BaseModel):
    lesson: str = Field(min_length=80, max_length=20_000)
    total: int = Field(default=6, ge=2, le=12)
```

- `BaseModel` is from **Pydantic**, a Python library for validating data.
- `ge=2` means “greater than or equal to 2”.
- `le=12` means “less than or equal to 12”.
- A user entering `99` questions will receive a validation error instead of crashing the server.

Also find the `Question` validator: for a multiple-choice question, it checks there are exactly four different options and that the correct letter is A, B, C or D.

**Try it yourself:** In `/docs`, send `total: 99` to `/api/generate`, with a sample lesson above 80 characters. Expect **HTTP 422 (validation error)** before Gemini is called. This uses no API tokens.

**What to say in class:** “A language model is not guaranteed to follow instructions. We validate its output before showing it to the user.”

## Lab 5 — Testing and deployment (15–20 minutes)

1. Open `vercel_app/tests/test_quiz_service.py`. Find the test for a malformed question and the test for HTTP 429.
2. Run `python -m pytest -q` in the `vercel_app` directory (after installing `requirements-dev.txt`).
3. Look for **26 passed**. Tests do not call the paid/free Gemini service; they use a fake HTTP transport.
4. Commit one of your changes:

```powershell
git add .
git commit -m "Make question instructions more conceptual"
git push
```

5. If your repo is linked to Vercel, the push will trigger a new deployment. See `DEPLOY_TO_VERCEL.md`.

**What to say in class:** “Automated tests help me detect regressions without paying for model requests. Git stores changes; Vercel publishes them.”

## Optional mini-challenge (choose one)

- **Easy — 5 min:** Change the purple theme color by editing `--purple` in `public/style.css` and also update `.hero` background colors.
- **Medium — 10 min:** Change the minimum lesson length from 80 to 100 characters in both `GenerationRequest` and the frontend validation message. Update `test_lesson_must_have_enough_text` and rerun tests.
- **Medium — 10 min:** Explain why `approved = False` is set on every Gemini-generated question, even if Gemini suggests it is correct.
- **Stretch:** Add a `topic` property to each question, extend the structured JSON schema and frontend review, and show a count of questions by topic. This introduces data analysis; Pandas/NumPy aren't required for Project 20 but could be added in a future version.

## Key concepts in one-minute explanations

- **Model vs API:** The model generates text; the API is how programs send it requests. The API key authorizes access.
- **Frontend vs backend:** The frontend runs in the visitor's browser. The backend runs on a server. The key belongs on the server.
- **POST vs GET:** GET requests information; POST sends information to be processed.
- **JSON:** A predictable field/value format programs can parse (`{ "title": "My quiz" }`).
- **Prompt:** Written instructions and context provided to the model.
- **Hallucination:** A plausible but unsupported AI statement. We add grounding and human review, not a guarantee of accuracy.
- **Pydantic:** Python library that checks values and types at input/output boundaries.
- **pytest:** Python tool that runs repeatable automated tests.
- **Git commit:** A named snapshot of your source code history.
- **Vercel:** Hosting service that runs the Python server and distributes the frontend.

## Test your understanding — answer aloud

1. Why can't the browser contact Gemini using a secret API key safely?
2. Which file receives `/api/generate`?
3. Which file builds the Gemini prompt?
4. What happens if the AI returns only three questions when six were requested?
5. Does the app automatically grade written answers? Why not?
6. What is the difference between the offline demo and the Gemini-generated quiz?
7. Why is GitHub Pages unsuitable for the Python backend?
8. What would you need to add for real teachers and students to save progress between sessions?

**Suggested answers:** 1) Browser code and network requests can be inspected; 2) `index.py`; 3) `quiz_service.py` → `make_prompt()`; 4) Python validation rejects it; 5) No, subjective responses need human review; 6) Demo is prewritten and doesn't contact AI; 7) no server-side Python/API-key protection; 8) authentication, database, per-user storage, and more security controls.
