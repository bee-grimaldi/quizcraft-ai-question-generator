"""Offline tests; no key or network access required."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from quiz_engine import (
    Question,
    QuizGenerationError,
    demo_quiz,
    export_csv,
    export_json,
    generate_quiz,
    question_counts,
    score_multiple_choice,
)

SAMPLE_LESSON = (Path(__file__).parents[1] / "sample_lesson.txt").read_text(encoding="utf-8")


class FakeModelAPI:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return next(self.responses)


class FakeClient:
    def __init__(self, responses):
        self.models = FakeModelAPI(responses)


def test_demo_quiz_has_complete_answer_keys():
    quiz = demo_quiz()
    assert len(quiz.questions) == 6
    normalized_lesson = " ".join(SAMPLE_LESSON.casefold().split())
    assert all(" ".join(q.source_excerpt.casefold().split()) in normalized_lesson for q in quiz.questions)
    assert sum(q.question_type == "multiple_choice" for q in quiz.questions) == 3
    assert all(q.suggested_answer and q.explanation for q in quiz.questions)


@pytest.mark.parametrize(
    "total,mode,expected",
    [(6, "Mixed", (3, 3)), (5, "Mixed", (3, 2)),
     (7, "Multiple choice", (7, 0)), (4, "Short answer", (0, 4))],
)
def test_question_type_distribution(total, mode, expected):
    assert question_counts(total, mode) == expected


def test_invalid_question_counts():
    with pytest.raises(QuizGenerationError):
        question_counts(13, "Mixed")
    with pytest.raises(QuizGenerationError):
        question_counts(6, "unknown")


def test_multiple_choice_answer_key_stays_synced_to_option():
    question = demo_quiz().questions[0].model_dump()
    question["correct_option"] = "B"
    validated = Question.model_validate(question)
    assert validated.suggested_answer == validated.options[1]


def test_invalid_mcq_options_rejected():
    question = demo_quiz().questions[0].model_dump()
    question["options"] = ["only one choice"]
    with pytest.raises(ValidationError):
        Question.model_validate(question)


def test_short_answer_must_include_expected_answer():
    question = demo_quiz().questions[3].model_dump()
    question["suggested_answer"] = "  "
    with pytest.raises(ValidationError):
        Question.model_validate(question)


def test_generate_quiz_parsed_structured_response():
    fake = FakeClient([SimpleNamespace(parsed=demo_quiz(), text=None)])
    quiz = generate_quiz(
        lesson=SAMPLE_LESSON,
        total=6,
        mode="Mixed",
        difficulty="Intermediate",
        language="English",
        api_key="",
        client=fake,
    )
    assert len(quiz.questions) == 6
    assert fake.models.calls[0]["model"] == "gemini-3.5-flash-lite"
    assert fake.models.calls[0]["config"].response_mime_type == "application/json"
    assert "LESSON START" in fake.models.calls[0]["contents"]


def test_generate_quiz_json_fallback():
    quiz_data = demo_quiz().model_dump()
    fake = FakeClient([SimpleNamespace(parsed=None, text=json.dumps(quiz_data))])
    result = generate_quiz(
        lesson=SAMPLE_LESSON,
        total=6,
        mode="Mixed",
        difficulty="Beginner",
        language="English",
        api_key="",
        client=fake,
    )
    assert result.title == quiz_data["title"]


def test_generation_retries_invalid_response_once():
    incomplete = demo_quiz().model_dump()
    incomplete["questions"] = incomplete["questions"][:3]
    fake = FakeClient([
        SimpleNamespace(parsed=incomplete, text=None),
        SimpleNamespace(parsed=demo_quiz(), text=None),
    ])
    result = generate_quiz(
        lesson=SAMPLE_LESSON,
        total=6,
        mode="Mixed",
        difficulty="Advanced",
        language="Spanish",
        api_key="",
        client=fake,
    )
    assert len(result.questions) == 6
    assert len(fake.models.calls) == 2


def test_source_excerpt_not_in_lesson_is_removed():
    data = demo_quiz().model_dump()
    data["questions"][0]["source_excerpt"] = "This sentence definitely does not exist."
    fake = FakeClient([SimpleNamespace(parsed=data, text=None)])
    result = generate_quiz(
        lesson=SAMPLE_LESSON,
        total=6,
        mode="Mixed",
        difficulty="Beginner",
        language="English",
        api_key="",
        client=fake,
    )
    assert result.questions[0].source_excerpt == ""
    assert result.questions[1].source_excerpt


def test_invalid_lesson_length_is_rejected_before_call():
    with pytest.raises(QuizGenerationError):
        generate_quiz(
            lesson="too short", total=6, mode="Mixed",
            difficulty="Beginner", language="English", api_key="123",
        )


def test_exports_approved_only_filter_and_excel_bom():
    data = demo_quiz().model_dump()
    for q in data["questions"]:
        q["approved"] = False
    data["questions"][0]["approved"] = True
    json_data = json.loads(export_json(data, approved_only=True))
    assert json_data["total_questions"] == 1
    assert json_data["questions"][0]["approved"] is True
    csv_bytes = export_csv(data, approved_only=True)
    assert csv_bytes.startswith(b"\xef\xbb\xbf")
    rows = list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig"))))
    assert len(rows) == 1
    assert rows[0]["correct_option"] == "A"


def test_csv_export_escapes_possible_spreadsheet_formula():
    data = demo_quiz().model_dump()
    data["questions"][0]["question"] = "=1+1"
    csv_data = export_csv(data).decode("utf-8-sig")
    assert "'=1+1" in csv_data


def test_student_scoring_ignores_written_questions():
    questions = demo_quiz().model_dump()["questions"]
    score, total = score_multiple_choice(questions, {0: "A", 1: "B", 2: "D", 3: "anything"})
    assert (score, total) == (2, 3)
