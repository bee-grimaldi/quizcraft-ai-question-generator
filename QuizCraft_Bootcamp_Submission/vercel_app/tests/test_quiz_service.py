"""Run: python -m pytest -q   (these tests never call Google)"""
import json

import httpx
import pytest
from pydantic import ValidationError

from quiz_service import (
    DEFAULT_MODEL, GenerationRequest, GeminiServiceError, Question,
    SAMPLE_LESSON, demo_quiz, desired_counts, generate_quiz, make_prompt,
    validate_generated_quiz,
)


def config(**kwargs):
    return GenerationRequest(lesson=SAMPLE_LESSON, **kwargs)


def test_unsupported_count_rejected():
    with pytest.raises(ValidationError):
        config(total=20)


def test_lesson_must_have_enough_text():
    with pytest.raises(ValidationError):
        GenerationRequest(lesson="too short")


@pytest.mark.parametrize('mode,expected', [
    ('Mixed',(3,3)), ('Multiple choice',(6,0)), ('Short answer',(0,6))
])
def test_question_counts(mode, expected):
    assert desired_counts(config(mode=mode)) == expected


def test_prompt_mentions_constraints_and_lesson():
    prompt = make_prompt(config(difficulty='Advanced', language='Spanish'))
    assert 'Spanish' in prompt and 'Advanced' in prompt
    assert 'LESSON START' in prompt and SAMPLE_LESSON in prompt


def test_demo_is_clearly_labeled_and_has_six_items():
    quiz = demo_quiz()
    assert quiz.source == 'demo'
    assert len(quiz.questions) == 6
    assert sum(q.question_type == 'multiple_choice' for q in quiz.questions) == 3


def test_correct_answer_derived_from_selected_option():
    question = demo_quiz().questions[0].model_dump()
    question['correct_option'] = 'B'
    validated = Question.model_validate(question)
    assert validated.suggested_answer == question['options'][1]


def test_invalid_mcq_options_rejected():
    raw = demo_quiz().questions[0].model_dump()
    raw['options'] = ['One']
    with pytest.raises(ValidationError):
        Question.model_validate(raw)


def test_unknown_source_excerpt_hidden():
    raw = demo_quiz().model_dump()
    raw['questions'][0]['source_excerpt'] = 'Totally fabricated evidence.'
    quiz = validate_generated_quiz(raw, config())
    assert quiz.questions[0].source_excerpt == ''
    assert quiz.source == 'gemini'
    assert all(not q.approved for q in quiz.questions)


def test_mismatched_question_count_rejected():
    raw = demo_quiz().model_dump()
    raw['questions'].pop()
    with pytest.raises(ValueError):
        validate_generated_quiz(raw, config())


def mock_transport(handler):
    return httpx.MockTransport(handler)


def json_response(quiz):
    return {'candidates': [{'content': {'parts': [{'text': json.dumps(quiz.model_dump())}]}}]}


def test_mocked_gemini_generates_quiz_with_secret_in_header():
    seen = {}
    def handler(request):
        seen['key'] = request.headers.get('x-goog-api-key')
        seen['url'] = str(request.url)
        seen['body'] = json.loads(request.content)
        return httpx.Response(200, json=json_response(demo_quiz()))
    result = generate_quiz(config(), 'secret-test-key', transport=mock_transport(handler))
    assert result.source == 'gemini'
    assert len(result.questions) == 6
    assert seen['key'] == 'secret-test-key'
    assert DEFAULT_MODEL in seen['url']
    assert seen['body']['generationConfig']['responseMimeType'] == 'application/json'
    assert 'responseSchema' in seen['body']['generationConfig']


@pytest.mark.parametrize('status,message', [(404,'unavailable'),(429,'quota'),(401,'rejected')])
def test_remote_errors_are_readable(status, message):
    def handler(request): return httpx.Response(status, json={'error': 'secret details'})
    with pytest.raises(GeminiServiceError, match=message):
        generate_quiz(config(), 'test-key', transport=mock_transport(handler))


def test_missing_key_rejected_without_network():
    with pytest.raises(GeminiServiceError, match='not configured'):
        generate_quiz(config(), '')


def test_malformed_json_retries_once():
    counter = {'calls': 0}
    def handler(request):
        counter['calls'] += 1
        if counter['calls'] == 1:
            return httpx.Response(200, json={'candidates': [{'content': {'parts': [{'text':'not json'}]}}]})
        return httpx.Response(200, json=json_response(demo_quiz()))
    result = generate_quiz(config(), 'test-key', transport=mock_transport(handler))
    assert len(result.questions) == 6
    assert counter['calls'] == 2
