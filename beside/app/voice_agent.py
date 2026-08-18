"""Beside LiveKit voice agent.

STT (LiveKit Inference) → Beside process_turn → TTS (LiveKit Inference).

Run from beside/ (second terminal, alongside uvicorn):

  .\\.venv\\Scripts\\python.exe -m app.voice_agent

Uses agent name `beside-tutor` so FastAPI token dispatch finds this worker.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, inference
from livekit.agents.llm import StopResponse
from livekit.plugins import silero
from sqlmodel import Session

from app.db import engine, init_db
from app.livekit_auth import AGENT_NAME, session_id_from_room
from app.services import get_child, get_session as get_tutor_session, process_turn


def _mentor_reply(child_id: str, session_id: str, message: str) -> str:
    """Run the existing Beside mentor brain in a worker thread (SQLite-safe)."""
    init_db()
    with Session(engine) as db:
        child = get_child(db, child_id)
        session = get_tutor_session(db, session_id)
        if not child or not session:
            return "I lost the lesson for a second. Try typing in the classroom."
        turn = process_turn(
            db,
            child=child,
            session=session,
            child_message=message.strip(),
        )
        return (turn.tutor_reply or "I'm listening. Try that again?").strip()


def _resolve_ids(ctx: agents.JobContext) -> tuple[str, str, str]:
    """Resolve child/session from room name and participant attributes."""
    session_id = session_id_from_room(ctx.room.name) or ""
    child_id = ""
    child_name = "friend"

    for p in ctx.room.remote_participants.values():
        attrs = dict(p.attributes or {})
        if attrs.get("session_id"):
            session_id = attrs["session_id"]
        if attrs.get("child_id"):
            child_id = attrs["child_id"]
        if p.name:
            child_name = p.name
        break

    if session_id and not child_id:
        init_db()
        with Session(engine) as db:
            session = get_tutor_session(db, session_id)
            if session:
                child = get_child(db, session.child_id)
                if child:
                    child_id = child.id
                    child_name = child.name

    return child_id, session_id, child_name


class BesideTutor(Agent):
    def __init__(self, *, child_id: str, session_id: str, child_name: str) -> None:
        super().__init__(
            instructions=(
                "You are Beside, a warm 1:1 tutor. Keep replies short. "
                "Never invent answers outside the mentor brain."
            )
        )
        self.child_id = child_id
        self.session_id = session_id
        self.child_name = child_name

    async def on_enter(self) -> None:
        await self.session.say(
            f"Hi {self.child_name}. I'm beside you. What should we work on?",
            allow_interruptions=True,
        )

    async def on_user_turn_completed(self, turn_ctx, new_message) -> None:
        text = (new_message.text_content or "").strip()
        if not text:
            raise StopResponse()

        reply = await asyncio.to_thread(
            _mentor_reply,
            self.child_id,
            self.session_id,
            text,
        )
        await self.session.say(reply, allow_interruptions=True)
        # Skip stock LLM — Beside's process_turn already produced the reply.
        raise StopResponse()


server = AgentServer()


@server.rtc_session(agent_name=AGENT_NAME)
async def beside_tutor(ctx: agents.JobContext) -> None:
    # Wait briefly for the child participant so attributes are available.
    for _ in range(20):
        if ctx.room.remote_participants:
            break
        await asyncio.sleep(0.25)

    child_id, session_id, child_name = _resolve_ids(ctx)
    if not child_id or not session_id:
        await ctx.connect()
        return

    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3", language="en"),
        tts=inference.TTS(model="inworld/inworld-tts-2", voice="Ashley"),
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=BesideTutor(
            child_id=child_id,
            session_id=session_id,
            child_name=child_name,
        ),
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
