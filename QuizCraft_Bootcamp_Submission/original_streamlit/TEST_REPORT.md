# QuizCraft — Test report

## Validation performed while assembling the project

| Check | Result | What was validated |
|---|---|---|
| Python syntax (`py_compile`) | PASS | `app.py`, `quiz_engine.py`, `tests/test_quiz_engine.py` |
| Offline unit tests (`pytest`) | **17 passed** | Question format, answer keys, quiz counts, prompts, fake Gemini responses, output retry, evidence verification, CSV/JSON exports, MCQ scoring |
| Basic app smoke test | PASS under a local Streamlit interface stub | Main script loads in the empty-quiz and preloaded-demo scenarios |
| Gemini live API test | **NOT RUN** | No personal API key was provided |
| Browser/UI test using real Streamlit | **NOT RUN** | External package installation is blocked in the construction environment |

The offline unit tests ran with real Pydantic 2.13.5 and pytest 9.0.2. A tiny **temporary local import stub** was used for the `google-genai` interface because this environment could not download packages. The smoke test also used a temporary Streamlit interface stub, **not a real browser**. These stubs are **not** included in the deliverable and are **not** part of the shipped project.

## How to confirm on your own computer

Once you install dependencies as described in `README.md`:

```bash
python -m pytest -q
streamlit run app.py
```

Then verify the offline demo and, once you configure your own `GEMINI_API_KEY`, generate a live 6-question quiz from `sample_lesson.txt`. Check the generated answer key, edit one question, approve it, and download a CSV.

## Expected limitations

- The model may return an unsupported claim or ambiguous question; teacher verification is required.
- Short answers are not automatically graded.
- Google Gemini free-tier quotas vary and may change.
- The app intentionally does not store quizzes in a persistent database.
