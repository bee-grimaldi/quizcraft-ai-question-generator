"""QuizCraft: Gemini-powered question generator for a Generative AI bootcamp.

Run with: streamlit run app.py
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError

from quiz_engine import (
    DEFAULT_MODEL,
    MAX_LESSON_CHARS,
    MIN_LESSON_CHARS,
    Question,
    QuizGenerationError,
    demo_quiz,
    export_csv,
    export_json,
    generate_quiz,
    score_multiple_choice,
)

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

st.set_page_config(
    page_title="QuizCraft | AI Question Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 1180px; padding-top: 1.6rem; padding-bottom: 4rem;}
      .app-hero {
        padding: 31px 36px;
        background: linear-gradient(116deg, #27214E 0%, #5043AD 58%, #7868E6 100%);
        border-radius: 23px; color: white; margin-bottom: 1.35rem;
        box-shadow: 0 13px 32px rgba(73, 58, 166, 0.17);
      }
      .app-hero .eyebrow {font-weight: 700; letter-spacing: .14em; font-size: 11px;
        opacity: .82; text-transform: uppercase; margin-bottom: 9px;}
      .app-hero h1 {font-size: clamp(2rem, 3.5vw, 3.2rem); line-height: 1.11;
        margin: 0 0 .75rem 0; color: #FFFFFF; font-weight: 750;}
      .app-hero p {margin: 0; color: #E3DFFF; font-size: 1.05rem; max-width: 740px;}
      .accent-label {display: inline-block; border: 1px solid #DCD7FF;
        background: #F1EEFF; color: #4834A6; border-radius: 30px;
        padding: 5px 12px; font-size: .82rem; font-weight: 650; margin: 8px 0;}
      div[data-testid="stMetric"] {border: 1px solid #E4E6F3; border-radius: 13px;
        background: #FFFFFF; padding: 12px 16px;}
      div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 15px;}
      .tiny-note {color: #666885; font-size: .86rem;}
      #MainMenu {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


def get_api_key() -> str:
    """Support local .env files and Streamlit Community Cloud secrets."""
    environment_key = os.getenv("GEMINI_API_KEY", "").strip()
    if environment_key:
        return environment_key
    try:
        return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except (FileNotFoundError, OSError, KeyError):
        return ""


def reset_quiz(quiz_obj, origin: str) -> None:
    """Install a new quiz in the active browser session."""
    saved = quiz_obj.model_dump()
    for question in saved["questions"]:
        question["approved"] = False
    st.session_state["quiz"] = saved
    st.session_state["quiz_origin"] = origin
    st.session_state["quiz_version"] += 1
    st.session_state.pop("preview_checked", None)


def mark_quiz_edited() -> None:
    st.session_state["quiz_version"] += 1
    st.session_state.pop("preview_checked", None)


def load_offline_demo() -> None:
    """Button callback runs before widgets are created on the next app rerun."""
    reset_quiz(demo_quiz(), "Offline demo — prewritten questions")
    st.session_state["lesson_text"] = (ROOT / "sample_lesson.txt").read_text(encoding="utf-8")
    st.session_state["notice"] = "Offline demo loaded. Visit **Teacher review** or **Student preview**."


for key, initial in (
    ("lesson_text", ""),
    ("quiz", None),
    ("quiz_origin", ""),
    ("quiz_version", 0),
):
    if key not in st.session_state:
        st.session_state[key] = initial

api_key = get_api_key()
model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

with st.sidebar:
    st.markdown("## 🧠 QuizCraft")
    st.caption("Your AI-powered assessment studio")
    st.divider()
    st.subheader("Question settings")
    total = st.slider("Number of questions", min_value=2, max_value=12, value=6)
    mode = st.selectbox(
        "Question types", ["Mixed", "Multiple choice", "Short answer"]
    )
    difficulty = st.select_slider(
        "Difficulty", options=["Beginner", "Intermediate", "Advanced"], value="Intermediate"
    )
    language = st.selectbox("Output language", ["English", "Spanish"])
    st.divider()
    st.subheader("AI connection")
    if api_key:
        st.success("Gemini key found", icon="✅")
    else:
        st.info("Gemini key not configured yet.", icon="🔑")
        st.markdown("[Create a key in Google AI Studio](https://aistudio.google.com/api-keys)")
        st.caption("Add `GEMINI_API_KEY` to a local `.env` file. See README.md.")
    st.caption(f"Model: `{model_name}`")
    st.divider()
    st.caption("🔒 Do not upload confidential data. Review AI answers before using them.")

st.markdown(
    """
    <div class="app-hero">
      <div class="eyebrow">GENERATIVE AI · BOOTCAMP PROJECT 20</div>
      <h1>Turn lesson notes into<br>great practice questions.</h1>
      <p>Generate questions with Gemini, refine them as a teacher, then preview the quiz
      as a student — all in one simple workspace.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

notice = st.session_state.pop("notice", None)
if notice:
    st.success(notice)

tab_generate, tab_review, tab_preview = st.tabs(
    ["✨ Generate", "📝 Teacher review", "🎓 Student preview"]
)

with tab_generate:
    left, right = st.columns([1.7, 1], gap="large")
    with left:
        st.subheader("1. Add your lesson")
        st.caption("Paste a lesson or upload a UTF-8 `.txt` or `.md` file.")
        upload_col, sample_col = st.columns([1.4, 1])
        with upload_col:
            uploaded = st.file_uploader(
                "Upload lesson", type=["txt", "md"], label_visibility="collapsed"
            )
        with sample_col:
            if st.button("📚 Load sample lesson", use_container_width=True):
                st.session_state["lesson_text"] = (ROOT / "sample_lesson.txt").read_text(
                    encoding="utf-8"
                )
                st.session_state.pop("notice", None)

        if uploaded is not None:
            raw = uploaded.getvalue()
            fingerprint = hashlib.sha256(raw).hexdigest()
            if st.session_state.get("upload_fingerprint") != fingerprint:
                try:
                    st.session_state["lesson_text"] = raw.decode("utf-8-sig")
                    st.session_state["upload_fingerprint"] = fingerprint
                except UnicodeDecodeError:
                    st.error("Please upload a UTF-8 encoded text file.")

        lesson_text = st.text_area(
            "Lesson notes",
            key="lesson_text",
            height=310,
            placeholder=(
                "Paste your lesson here…\n\n"
                "For example: Generative AI models learn patterns from data…"
            ),
        )
        lesson_size = len(lesson_text.strip())
        st.caption(
            f"{lesson_size:,} characters · allowed: "
            f"{MIN_LESSON_CHARS:,}–{MAX_LESSON_CHARS:,} characters"
        )
        submitted = st.button(
            "✨ Generate questions with Gemini", type="primary", use_container_width=True
        )
        if submitted:
            if not api_key:
                st.error("Add your Gemini API key to `.env` first, or use the offline demo.")
            else:
                try:
                    with st.spinner("Creating and checking your questions…"):
                        generated = generate_quiz(
                            lesson=lesson_text,
                            total=total,
                            mode=mode,
                            difficulty=difficulty,
                            language=language,
                            api_key=api_key,
                            model_name=model_name,
                        )
                    reset_quiz(generated, "Gemini AI")
                    st.session_state["notice"] = (
                        "Quiz created! Open **Teacher review** to edit and approve your questions."
                    )
                    st.rerun()
                except QuizGenerationError as exc:
                    st.error(str(exc))
                except Exception as exc:
                    error = str(exc).lower()
                    if "429" in error or "resource_exhausted" in error or "quota" in error:
                        st.error(
                            "Gemini's free-tier rate limit was reached. Try again later or use the demo quiz."
                        )
                    elif "api_key_invalid" in error or "api key not valid" in error or "401" in error:
                        st.error("The Gemini API key appears invalid. Check the key in your `.env` file.")
                    elif "404" in error or "not found" in error:
                        st.error(
                            f"Gemini could not access model `{model_name}`. "
                            "Check the model setting in your `.env` file and "
                            "whether your Google AI Studio project can use it. "
                            "For new projects, try `gemini-3.5-flash-lite`, then restart Streamlit."
                        )
                    else:
                        st.error(
                            "Gemini could not generate this quiz. Check the internet connection, "
                            "API key, and model availability."
                        )
                        st.caption(f"Technical error type: `{type(exc).__name__}`")

    with right:
        with st.container(border=True):
            st.markdown("#### ⚡ No API key yet?")
            st.write(
                "You can explore every screen with **six prewritten example questions**. "
                "They are clearly labeled as demo data, not Gemini output."
            )
            st.button(
                "🚀 Open offline demo",
                use_container_width=True,
                on_click=load_offline_demo,
            )
        with st.container(border=True):
            st.markdown("#### How it works")
            st.markdown(
                "**01** · Provide lesson notes  \n"
                "**02** · Choose the number, type, and difficulty  \n"
                "**03** · Generate with Google Gemini  \n"
                "**04** · Review and approve each answer  \n"
                "**05** · Export CSV/JSON or try student preview"
            )
        with st.container(border=True):
            st.markdown("#### Grounded in your notes")
            st.write(
                "The AI is asked to use only your material and include supporting "
                "source excerpts. These excerpts are checked against the input, but "
                "**you should still verify each answer**."
            )
    if st.session_state["quiz"]:
        st.divider()
        quiz_here = st.session_state["quiz"]
        st.markdown(
            f"**Current quiz:** {quiz_here['title']} · "
            f"{len(quiz_here['questions'])} questions · {st.session_state['quiz_origin']}"
        )

with tab_review:
    quiz = st.session_state["quiz"]
    if not quiz:
        st.info("No quiz yet. Generate questions or load the offline demo in the Generate tab.")
    else:
        st.subheader("2. Review and refine")
        st.caption(
            "Check each question, edit anything unclear, and approve it when ready. "
            "Answers from generative AI can contain mistakes."
        )
        st.markdown(f"### {quiz['title']}")
        st.markdown(f"<span class='accent-label'>{st.session_state['quiz_origin']}</span>", unsafe_allow_html=True)
        questions = quiz["questions"]
        approved_count = sum(bool(q.get("approved", False)) for q in questions)
        metric_a, metric_b, metric_c = st.columns(3)
        metric_a.metric("Questions", len(questions))
        metric_b.metric("Approved", approved_count)
        metric_c.metric("Need review", len(questions) - approved_count)
        st.write("")
        approve_col, reset_col, export_col = st.columns([1, 1, 1.7])
        with approve_col:
            if st.button("✅ Approve all", use_container_width=True):
                for question in questions:
                    question["approved"] = True
                mark_quiz_edited()
                st.rerun()
        with reset_col:
            if st.button("↩ Mark all as draft", use_container_width=True):
                for question in questions:
                    question["approved"] = False
                mark_quiz_edited()
                st.rerun()
        with export_col:
            export_scope = st.selectbox(
                "Export selection",
                options=["All questions", "Approved only"],
                label_visibility="collapsed",
            )
        only_approved = export_scope == "Approved only"
        export_count = approved_count if only_approved else len(questions)
        csv_col, json_col = st.columns(2)
        with csv_col:
            st.download_button(
                "⬇ Download CSV + answer key",
                data=export_csv(quiz, approved_only=only_approved),
                file_name="quizcraft_questions.csv",
                mime="text/csv",
                use_container_width=True,
                disabled=(export_count == 0),
            )
        with json_col:
            st.download_button(
                "⬇ Download JSON",
                data=export_json(quiz, approved_only=only_approved),
                file_name="quizcraft_questions.json",
                mime="application/json",
                use_container_width=True,
                disabled=(export_count == 0),
            )
        if export_count == 0:
            st.warning("No questions are approved. Approve some questions or export all questions.")
        st.divider()
        version = st.session_state["quiz_version"]
        for idx, q in enumerate(questions):
            kind_label = "Multiple choice" if q["question_type"] == "multiple_choice" else "Short answer"
            status_label = "✅ Approved" if q.get("approved", False) else "🟡 Draft"
            with st.expander(
                f"Q{idx + 1} · {kind_label} · {status_label} · {q['question'][:72]}",
                expanded=(idx == 0),
            ):
                with st.form(key=f"edit_question_{version}_{idx}"):
                    edited_question = st.text_area("Question", value=q["question"], height=85)
                    if q["question_type"] == "multiple_choice":
                        opt_cols = st.columns(2)
                        edited_options: list[str] = []
                        for option_number, letter in enumerate("ABCD"):
                            with opt_cols[option_number % 2]:
                                edited_options.append(
                                    st.text_input(
                                        f"Option {letter}",
                                        value=q["options"][option_number],
                                    )
                                )
                        edited_correct = st.selectbox(
                            "Correct option", list("ABCD"),
                            index="ABCD".index(q["correct_option"]),
                        )
                        edited_answer = edited_options["ABCD".index(edited_correct)]
                    else:
                        edited_options = []
                        edited_correct = ""
                        edited_answer = st.text_area(
                            "Suggested answer", value=q["suggested_answer"], height=90
                        )
                    edited_explanation = st.text_area(
                        "Answer explanation", value=q["explanation"], height=90
                    )
                    edited_source = st.text_input(
                        "Supporting excerpt from notes (optional)",
                        value=q.get("source_excerpt", ""),
                    )
                    edited_approved = st.checkbox(
                        "Approved for student use", value=bool(q.get("approved", False))
                    )
                    saved = st.form_submit_button("💾 Save changes", type="primary")
                if saved:
                    revised = {
                        "question_type": q["question_type"],
                        "question": edited_question,
                        "options": edited_options,
                        "correct_option": edited_correct,
                        "suggested_answer": edited_answer,
                        "explanation": edited_explanation,
                        "source_excerpt": edited_source,
                    }
                    try:
                        validated = Question.model_validate(revised)
                    except ValidationError as exc:
                        st.error("Please complete all fields and provide valid answer options.")
                        st.caption(str(exc.errors()[0].get("msg", "Invalid question.")))
                    else:
                        quiz["questions"][idx] = {
                            **validated.model_dump(), "approved": edited_approved
                        }
                        mark_quiz_edited()
                        st.session_state["notice"] = f"Question {idx + 1} saved."
                        st.rerun()
                if len(questions) > 1:
                    if st.button("🗑 Delete question", key=f"delete_{version}_{idx}"):
                        quiz["questions"].pop(idx)
                        mark_quiz_edited()
                        st.rerun()
        st.caption("Changes are stored in your current browser session. Download a file to keep your work.")

with tab_preview:
    quiz = st.session_state["quiz"]
    if not quiz:
        st.info("No quiz yet. Generate questions or load the offline demo first.")
    else:
        st.subheader("3. Try your quiz as a student")
        st.write("Multiple-choice answers receive an automatic score. Short answers are self-reviewed.")
        approved_questions = [q for q in quiz["questions"] if q.get("approved", False)]
        if approved_questions:
            scope = st.radio(
                "Questions to preview", ["Approved questions", "All questions (including drafts)"],
                horizontal=True,
            )
            visible_questions = (
                approved_questions if scope == "Approved questions" else quiz["questions"]
            )
        else:
            scope = "All questions (including drafts)"
            visible_questions = quiz["questions"]
            st.info("No questions have been approved, so this preview includes draft questions.")
        st.markdown(f"### {quiz['title']}")
        responses = {}
        version = st.session_state["quiz_version"]
        with st.form(key=f"student_form_{version}_{len(visible_questions)}"):
            for idx, q in enumerate(visible_questions):
                st.markdown(f"**Question {idx + 1}** · {q['question']}")
                if q["question_type"] == "multiple_choice":
                    options = q["options"]
                    choice = st.radio(
                        f"Answer for question {idx + 1}",
                        options=["", "A", "B", "C", "D"],
                        format_func=lambda code, opts=options: (
                            "Choose an answer" if not code else f"{code}. {opts['ABCD'.index(code)]}"
                        ),
                        key=f"student_mcq_{version}_{idx}",
                    )
                    responses[idx] = choice
                else:
                    responses[idx] = st.text_area(
                        f"Your answer to question {idx + 1}",
                        height=90,
                        key=f"student_written_{version}_{idx}",
                    )
                st.divider()
            checked = st.form_submit_button("✅ Check answers", type="primary", use_container_width=True)
        if checked:
            st.session_state["preview_checked"] = {
                "version": version,
                "scope": scope,
                "responses": responses,
            }
        result = st.session_state.get("preview_checked")
        if result and result["version"] == version and result["scope"] == scope:
            chosen_responses = result["responses"]
            correct, possible = score_multiple_choice(visible_questions, chosen_responses)
            st.divider()
            if possible:
                st.metric("Multiple-choice score", f"{correct} / {possible}")
                st.progress(correct / possible)
            for idx, q in enumerate(visible_questions):
                if q["question_type"] == "multiple_choice":
                    selected = chosen_responses.get(idx, "")
                    is_correct = selected == q["correct_option"]
                    st.markdown(
                        f"**Q{idx + 1}: {'✅ Correct' if is_correct else '❌ Incorrect or unanswered'}**"
                    )
                    st.write(f"Correct answer: **{q['correct_option']}. {q['suggested_answer']}**")
                else:
                    st.markdown(f"**Q{idx + 1}: Written answer — compare with the model answer**")
                    st.write(f"Your answer: {chosen_responses.get(idx) or '(no answer)'}")
                    st.write(f"Suggested answer: **{q['suggested_answer']}**")
                st.caption(q["explanation"])
            st.caption(
                "Only multiple-choice answers are automatically graded. "
                "A teacher should evaluate written answers and verify all AI-generated answer keys."
            )

st.divider()
st.caption(
    "QuizCraft · Project 20: AI Question Generator · Python + Streamlit + Google Gemini · "
    "Questions are kept in your current Streamlit session; download them to save a copy."
)
