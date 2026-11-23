"""FastAPI web server. Vercel detects the `app` object in this file.

Endpoints are URLs the browser can call:
  GET  /api/health   -> check whether the server is ready
  GET  /api/sample   -> get safe sample lesson notes
  GET  /api/demo     -> offline demo questions (no Gemini call)
  POST /api/generate -> call Gemini and return structured questions
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles

from quiz_service import DEFAULT_MODEL, SAMPLE_LESSON, GenerationRequest, GeminiServiceError, Quiz, demo_quiz, generate_quiz

load_dotenv(Path(__file__).parent / ".env")
app = FastAPI(title="QuizCraft API", version="1.0.0")


@app.get("/api/health")
def health() -> dict:
    # IMPORTANT: Only report whether a key exists; never return the actual key.
    return {
        "status": "ok",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()),
        "access_code_required": bool(os.getenv("DEMO_ACCESS_CODE", "").strip()),
        "model": os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
    }


@app.get("/api/sample")
def sample() -> dict:
    return {"lesson": SAMPLE_LESSON}


@app.get("/api/demo", response_model=Quiz)
def demo() -> Quiz:
    return demo_quiz()


@app.post("/api/generate", response_model=Quiz)
def generate(request: GenerationRequest, x_demo_access: str | None = Header(default=None)) -> Quiz:
    # Optional classroom access code prevents casual misuse of a public Gemini key.
    expected = os.getenv("DEMO_ACCESS_CODE", "").strip()
    if expected and not secrets.compare_digest(x_demo_access or "", expected):
        raise HTTPException(status_code=401, detail="Enter the classroom access code to generate questions.")
    try:
        return generate_quiz(
            request=request,
            api_key=os.getenv("GEMINI_API_KEY", "").strip(),
            model_name=os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL,
        )
    except GeminiServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


# Locally, FastAPI serves the frontend. On Vercel, /public files can be served
# from its CDN. The API routes must come BEFORE this catch-all static mount.
PUBLIC = Path(__file__).parent / "public"
if PUBLIC.is_dir():
    app.mount("/", StaticFiles(directory=PUBLIC, html=True), name="frontend")
