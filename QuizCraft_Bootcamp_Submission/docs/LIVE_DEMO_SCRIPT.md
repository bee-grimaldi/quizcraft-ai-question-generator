# QuizCraft — Live demo and speaking notes

## 3–4 minute live demonstration

**Before class:** Open the deployed Vercel URL, keep the link handy, have your classroom access code (if enabled), and confirm Gemini generation works. Keep the offline demo as backup. Use the sample lesson; no private information.

| Time | What you do on screen | What you say |
|---|---|---|
| 0:00–0:25 | Show the landing page | “QuizCraft is an AI Question Generator for teachers. It turns lesson notes into editable practice assessments.” |
| 0:25–0:55 | Click **Load sample lesson**, choose 4 Mixed questions, difficulty Beginner | “We control the topic, number, question type, difficulty, and language before calling the model.” |
| 0:55–1:30 | Click **Generate with Gemini**; if the API fails, click **Try offline demo** | “Python prepares the prompt, calls Gemini server-side, then validates the structured JSON.” |
| 1:30–2:05 | Show multiple-choice questions and suggested answers; edit a question and approve it | “Teacher review is required. The AI proposes content; the teacher owns the final decision.” |
| 2:05–2:40 | Open **Student preview**, answer MCQs, click **Check my answers** | “MCQs are scored automatically; written answers show a reference response but require human evaluation.” |
| 2:40–3:05 | Open **Export**, download CSV or JSON | “Reviewed questions can be downloaded for use in other systems.” |
| 3:05–3:35 | Open `/api/health` or show architecture slide | “The browser never receives my Gemini key. It stays in Vercel environment variables.” |

**Opening statement (memorize):** “My project solves the repetitive task of creating practice questions from lesson materials. It uses Gemini to generate draft questions, Python to validate the output, and a teacher approval step before student practice.”

**Closing statement:** “The main lesson is that generative AI should be one component in a controlled workflow: clear prompts, structured outputs, validation, and human review. Next, I'd add logins, persistent quiz history, and analysis of student performance.”

## What your instructor may ask

1. **Where does Python appear?** `index.py` is FastAPI; `quiz_service.py` makes the Gemini request, constructs the prompt, and validates output with Pydantic.
2. **What does Gemini do?** Creates question text, options, suggested answers, explanations, and evidence excerpts based on the supplied lesson.
3. **Is this fine-tuning?** No. This uses prompting at inference time; the base model isn't retrained.
4. **What is the difference between prompt and response schema?** The prompt explains the educational task; the schema forces the structure of the JSON answer.
5. **What if Gemini returns an error?** The server sends a readable error, and the app has a clearly identified offline sample.
6. **Do you use NumPy or Pandas?** No. They are not required for Project 20. Python, FastAPI, Pydantic, httpx, and pytest are directly relevant here. Pandas/NumPy would be useful for later student-performance analytics.
7. **Where is the API key?** In a local `.env` or a Vercel environment variable; never in frontend JavaScript or GitHub.
8. **Does the system guarantee correct answers?** No; Pydantic checks structure, source excerpts are matched against the lesson, and the teacher approves educational correctness.
9. **Where is the database?** There isn't one in this MVP. Edits are kept in the open browser session and exported as files.
10. **Why Vercel and not GitHub Pages?** Vercel runs Python FastAPI; GitHub Pages is static and can't protect a Gemini key in server code.

## Backup plan for live class

If the free Gemini API reaches a rate limit or model availability error: tell the instructor the live API is temporarily unavailable, click **Try offline demo**, and demonstrate teacher review, student preview, and export. **Never say the demo questions were generated live** — they are prewritten sample data.

## Personalize your presentation

After publishing, replace the placeholders in the PowerPoint:

- GitHub: `https://github.com/YOUR_USERNAME/quizcraft-ai-question-generator`
- Vercel: paste the **real URL** from the Vercel dashboard.
- Add your own screenshot of the deployed app and a successful Gemini generation if you want to show proof of live deployment.
