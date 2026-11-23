"""FastAPI endpoint tests using an in-process test client (no public server)."""
from fastapi.testclient import TestClient
import index

client = TestClient(index.app)


def test_root_serves_frontend():
    response = client.get('/')
    assert response.status_code == 200
    assert 'QuizCraft' in response.text


def test_frontend_assets():
    assert client.get('/style.css').status_code == 200
    assert client.get('/app.js').status_code == 200


def test_health_never_leaks_api_key(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY', 'do-not-expose-me')
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['gemini_configured'] is True
    assert 'do-not-expose-me' not in response.text


def test_get_sample_lesson():
    r = client.get('/api/sample')
    assert r.status_code == 200
    assert 'Generative AI' in r.json()['lesson']


def test_demo_endpoint():
    r = client.get('/api/demo')
    assert r.status_code == 200
    assert r.json()['source'] == 'demo'
    assert len(r.json()['questions']) == 6


def test_generate_rejects_invalid_lessons():
    r = client.post('/api/generate', json={'lesson': 'abc', 'total': 6})
    assert r.status_code == 422


def test_generate_without_key_shows_clear_error(monkeypatch):
    monkeypatch.delenv('DEMO_ACCESS_CODE', raising=False)
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    lesson = client.get('/api/sample').json()['lesson']
    r = client.post('/api/generate', json={'lesson': lesson, 'total': 6})
    assert r.status_code == 503
    assert 'not configured' in r.json()['detail']


def test_generate_delegates_to_service(monkeypatch):
    monkeypatch.delenv('DEMO_ACCESS_CODE', raising=False)
    from quiz_service import demo_quiz
    monkeypatch.setenv('GEMINI_API_KEY', 'fake-key')
    def fake_generate(**kwargs):
        assert kwargs['api_key'] == 'fake-key'
        q = demo_quiz()
        q.source = 'gemini'
        return q
    monkeypatch.setattr(index, 'generate_quiz', fake_generate)
    lesson = client.get('/api/sample').json()['lesson']
    r = client.post('/api/generate', json={'lesson': lesson, 'total': 6})
    assert r.status_code == 200
    assert r.json()['source'] == 'gemini'


def test_optional_access_code(monkeypatch):
    monkeypatch.setenv('DEMO_ACCESS_CODE', 'secret-class-code')
    monkeypatch.setenv('GEMINI_API_KEY', 'fake-key')
    lesson = client.get('/api/sample').json()['lesson']
    response = client.post('/api/generate', json={'lesson': lesson})
    assert response.status_code == 401
    assert 'classroom access code' in response.json()['detail']
    assert 'secret-class-code' not in client.get('/api/health').text

    from quiz_service import demo_quiz
    monkeypatch.setattr(index, 'generate_quiz', lambda **kwargs: demo_quiz())
    ok = client.post('/api/generate', json={'lesson': lesson}, headers={'X-Demo-Access':'secret-class-code'})
    assert ok.status_code == 200
