"""Fast path: one LLM call instead of 4 CrewAI agents.

Same outputs (reply, affect, move, memory). Much lower latency for a working classroom.
Uses Ollama native /api/chat, or OpenAI-compatible chat (OpenAI / Groq).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import httpx

from app.crew.llm_config import get_chat_client

OS_PATH = Path(__file__).with_name("mentoring_os.md")


def _load_os() -> str:
    return OS_PATH.read_text(encoding="utf-8")


def _extract_json(text: str) -> dict[str, Any]:
    if not text:
        return {}
    text = str(text).strip()
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    if text.startswith("{{") and text.endswith("}}"):
        text = text[1:-1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return {"raw": text}
        candidate = match.group(0)
        if candidate.startswith("{{") and candidate.endswith("}}"):
            candidate = candidate[1:-1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return {"raw": text}


def _chat(messages: list[dict[str, str]]) -> str:
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    if provider in {"openai", "groq"}:
        client, model = get_chat_client()
        completion = client.chat.completions.create(
            model=model,
            temperature=0.5,
            messages=messages,
        )
        return completion.choices[0].message.content or "{}"

    # Ollama native API (avoids broken /v1 llama-server path on some installs)
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    with httpx.Client(timeout=180.0) as client:
        res = client.post(
            f"{base}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.5},
            },
        )
        res.raise_for_status()
        data = res.json()
        return (data.get("message") or {}).get("content") or "{}"


def run_fast_mentor_turn(
    *,
    child_name: str,
    age: int,
    skill: str,
    interest: str,
    profile: str,
    history: str,
    child_message: str,
) -> dict[str, Any]:
    os_text = _load_os()

    system = (
        "You are Beside, a devoted 1:1 tutor for one child. "
        "Do the full mentoring loop in ONE response: observe, choose a move, reply, update memory.\n\n"
        f"{os_text}\n\n"
        "Return ONLY valid JSON with this shape:\n"
        "{\n"
        '  "affect": "confused|scared|bored|engaged|proud|unknown",\n'
        '  "move": "diagnose|hint|scaffold|reframe|retreat|celebrate|check",\n'
        '  "micro_goal": "one tiny next step",\n'
        '  "reply": "what the child hears (short, warm, no shame)",\n'
        '  "memory_update": {\n'
        '    "what_clicked": ["..."],\n'
        '    "what_stuck": ["..."],\n'
        '    "misconceptions": ["..."],\n'
        '    "notes": "one sentence"\n'
        "  }\n"
        "}"
    )

    user = (
        f"Child name: {child_name}\n"
        f"Age: {age}\n"
        f"Skill focus: {skill}\n"
        f"Interest: {interest or 'stories'}\n"
        f"Profile: {profile or 'New learner. Build trust first.'}\n"
        f"Recent history:\n{history or '(no prior turns)'}\n"
        f"Child just said: {child_message}\n"
    )

    raw = _chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
    )
    data = _extract_json(raw)

    memory = data.get("memory_update") or {}
    if not isinstance(memory, dict):
        memory = {"raw": memory}

    reply = data.get("reply")
    if not reply:
        reply = data.get("raw") or raw

    return {
        "reply": str(reply),
        "affect": data.get("affect"),
        "move": data.get("move"),
        "micro_goal": data.get("micro_goal"),
        "memory_update": memory,
        "debug": {"mode": "fast", "raw": data},
    }