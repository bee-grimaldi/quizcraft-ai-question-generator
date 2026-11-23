# QuizCraft — Bootcamp presentation and submission guide

## 60–90 second demo script

1. **Problem (10 seconds):** "Teachers often spend time turning notes into practice questions. QuizCraft helps draft an assessment in seconds, while leaving final control with the teacher."
2. **Input (15 seconds):** Load `sample_lesson.txt` and choose six mixed questions, intermediate difficulty, and English.
3. **AI step (20 seconds):** Generate with Gemini. Mention that structured JSON and Pydantic validation check the expected format. **If API access is unavailable, use the clearly labeled prewritten offline demo and do not claim it was AI generated live.**
4. **Teacher review (20 seconds):** Edit one question, change an answer option, approve it, and download CSV with answer key.
5. **Student preview (15 seconds):** Answer an MCQ, submit, and show the MCQ score and suggested answer for a written question.
6. **Limitations (10 seconds):** Human review is necessary; short answers are not auto-graded; API free tier has usage limits.

## Project description for your slides

**Title:** QuizCraft — AI Question Generator

**Problem:** Teachers need fast, customizable practice questions derived from lesson notes.

**Solution:** A Streamlit application that sends authorized lesson text to Gemini, receives structured questions, and provides an editing/approval workflow before exporting or trying the questions.

**Input:** Lesson text, question count, question type, difficulty, language.

**Output:** Multiple-choice and short-answer questions, correct answers, explanations, supporting excerpts, and CSV/JSON downloads.

**Technology stack:** Python, Streamlit, Google Gemini API, Pydantic, Git/GitHub.

**Responsible AI:** Key protection, input privacy, clearly labeled demo content, source-based prompts, and teacher review.

## Screenshots to capture (from the actual running app)

- [ ] Generate tab with sample lesson and question settings.
- [ ] Teacher review tab with questions, options, answer key, and approval checkbox.
- [ ] Exported CSV opened in Excel or a spreadsheet viewer.
- [ ] Student preview tab showing an MCQ score.
- [ ] Terminal output showing `python -m pytest -q` tests passing.

## Submission checklist

- [ ] `app.py` and `quiz_engine.py`
- [ ] `requirements.txt`
- [ ] `README.md`
- [ ] GitHub repository URL (never include `.env`)
- [ ] Sample lesson + source description
- [ ] 3–5 screenshots
- [ ] Unit-test results and known limitations
- [ ] A short presentation/demo

## If Gemini isn't working during the demo

Use **Open offline demo**. The demo questions are manually authored; show the teacher workflow and explain that the `generate_quiz()` function is wired to Gemini and requires working credentials and a network connection. Avoid claiming that the demo data came from a live model call.
