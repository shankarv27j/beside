import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.crew.llm_config import llm_status
from app.db import get_session, init_db
from app.livekit_auth import get_livekit_config, mint_child_token
from app.services import (
    create_child,
    get_child,
    get_session as get_tutor_session,
    list_children,
    get_or_start_session,
    list_turns,
    process_turn,
    rate_turn,
    start_session,
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Beside", version="0.2.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def _lists(child):
    def load(raw: str):
        try:
            data = json.loads(raw or "[]")
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    return load(child.what_clicked), load(child.what_stuck), load(child.misconceptions)


@app.get("/health")
def health():
    return {"ok": True, **llm_status()}


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_session)):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"children": list_children(db)},
    )


@app.post("/children")
def children_create(
    name: str = Form(...),
    age: int = Form(...),
    interest: str = Form(...),
    skill_focus: str = Form("arithmetic"),
    db: Session = Depends(get_session),
):
    child = create_child(
        db,
        name=name,
        age=age,
        interest=interest,
        skill_focus=skill_focus,
    )
    return RedirectResponse(f"/children/{child.id}/session", status_code=303)


@app.get("/children/{child_id}/session", response_class=HTMLResponse)
def classroom(
    child_id: str,
    request: Request,
    db: Session = Depends(get_session),
):
    child = get_child(db, child_id)
    if not child:
        raise HTTPException(404, "Child not found")
    session = get_or_start_session(db, child)
    turns = list_turns(db, session.id)
    clicked, stuck, misconceptions = _lists(child)
    return templates.TemplateResponse(
        request,
        "classroom.html",
        {
            "child": child,
            "session": session,
            "turns": turns,
            "clicked": clicked,
            "stuck": stuck,
            "misconceptions": misconceptions,
        },
    )


@app.post("/children/{child_id}/session/new")
def classroom_new(child_id: str, db: Session = Depends(get_session)):
    child = get_child(db, child_id)
    if not child:
        raise HTTPException(404, "Child not found")
    start_session(db, child)
    return RedirectResponse(f"/children/{child_id}/session", status_code=303)


@app.get("/sessions/{session_id}", response_class=HTMLResponse)
def session_view(
    session_id: str,
    request: Request,
    db: Session = Depends(get_session),
):
    session = get_tutor_session(db, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    child = get_child(db, session.child_id)
    if not child:
        raise HTTPException(404, "Child not found")
    turns = list_turns(db, session.id)
    clicked, stuck, misconceptions = _lists(child)
    return templates.TemplateResponse(
        request,
        "classroom.html",
        {
            "child": child,
            "session": session,
            "turns": turns,
            "clicked": clicked,
            "stuck": stuck,
            "misconceptions": misconceptions,
        },
    )


@app.post("/sessions/{session_id}/livekit/token")
def livekit_token(session_id: str, db: Session = Depends(get_session)):
    """Mint a LiveKit join token and dispatch the beside-tutor voice agent."""
    config = get_livekit_config()
    if not config:
        raise HTTPException(
            503,
            "LiveKit is not configured. Set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET in .env",
        )

    session = get_tutor_session(db, session_id)
    if not session or not session.active:
        raise HTTPException(404, "Active session not found")
    child = get_child(db, session.child_id)
    if not child:
        raise HTTPException(404, "Child not found")

    payload = mint_child_token(
        config=config,
        session_id=session.id,
        child_id=child.id,
        child_name=child.name,
    )
    return JSONResponse(payload)


@app.post("/sessions/{session_id}/turns")
def session_turn(
    session_id: str,
    request: Request,
    message: str = Form(...),
    db: Session = Depends(get_session),
):
    """Process one child message.

    Server call stays synchronous (simpler + safe with SQLite sessions).
    Speed comes from MENTOR_MODE=fast (1 LLM call).
    Browser uses fetch + a thinking banner so the wait feels intentional.
    """
    status = llm_status()
    if status["provider"] in {"openai", "groq"} and not status.get("ready"):
        missing = "OPENAI_API_KEY" if status["provider"] == "openai" else "GROQ_API_KEY"
        raise HTTPException(400, f"Set {missing} or use LLM_PROVIDER=ollama")

    session = get_tutor_session(db, session_id)
    if not session or not session.active:
        raise HTTPException(404, "Active session not found")
    child = get_child(db, session.child_id)
    if not child:
        raise HTTPException(404, "Child not found")

    try:
        turn = process_turn(
            db,
            child=child,
            session=session,
            child_message=message.strip(),
        )
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc

    wants_json = "application/json" in request.headers.get("accept", "").lower()
    if wants_json:
        return JSONResponse(
            {
                "ok": True,
                "turn": {
                    "id": turn.id,
                    "child_message": turn.child_message,
                    "tutor_reply": turn.tutor_reply,
                    "move": turn.move,
                    "affect": turn.affect,
                },
                "redirect": f"/sessions/{session_id}",
            }
        )

    return RedirectResponse(f"/sessions/{session_id}", status_code=303)


@app.post("/turns/{turn_id}/rate")
def turn_rate(
    turn_id: str,
    rating: str = Form(...),
    next: str = Form("/"),
    db: Session = Depends(get_session),
):
    if rating not in {"me", "not_me"}:
        raise HTTPException(400, "rating must be me or not_me")
    turn = rate_turn(db, turn_id, rating)
    if not turn:
        raise HTTPException(404, "Turn not found")
    return RedirectResponse(next or f"/sessions/{turn.session_id}", status_code=303)


@app.get("/children/{child_id}/parent", response_class=HTMLResponse)
def parent_view(
    child_id: str,
    request: Request,
    db: Session = Depends(get_session),
):
    child = get_child(db, child_id)
    if not child:
        raise HTTPException(404, "Child not found")
    clicked, stuck, misconceptions = _lists(child)
    return templates.TemplateResponse(
        request,
        "parent.html",
        {
            "child": child,
            "clicked": clicked,
            "stuck": stuck,
            "misconceptions": misconceptions,
        },
    )