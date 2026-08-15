import json
import re
from typing import Any

from crewai import Crew, Process
from dotenv import load_dotenv

from .agents import build_agents
from .tasks import build_tasks

load_dotenv()


def _extract_json(text: str) -> dict[str, Any]:
    if not text:
        return {}
    text = str(text).strip()
    # Strip markdown fences small local models often add
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    # Some local models emit {{...}} instead of {...}
    if text.startswith("{{") and text.endswith("}}"):
        text = text[1:-1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            candidate = match.group(0)
            if candidate.startswith("{{") and candidate.endswith("}}"):
                candidate = candidate[1:-1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                return {"raw": text}
        return {"raw": text}


def run_mentor_turn(
    *,
    child_name: str,
    age: int,
    skill: str,
    interest: str,
    profile: str,
    history: str,
    child_message: str,
) -> dict[str, Any]:
    """Run Observer -> Strategist -> Tutor -> Memory for one child message."""
    agents = build_agents()
    tasks = build_tasks(agents)

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    inputs = {
        "child_name": child_name,
        "age": age,
        "skill": skill,
        "interest": interest or "stories",
        "profile": profile or "New learner. Build trust first.",
        "history": history or "(no prior turns)",
        "child_message": child_message,
    }

    result = crew.kickoff(inputs=inputs)

    # Prefer the Tutor task output (3rd task); fall back to final raw.
    tutor_raw = ""
    strategist_raw = ""
    observer_raw = ""
    memory_raw = ""
    try:
        task_outputs = result.tasks_output  # type: ignore[attr-defined]
        if task_outputs and len(task_outputs) >= 4:
            observer_raw = str(task_outputs[0])
            strategist_raw = str(task_outputs[1])
            tutor_raw = str(task_outputs[2])
            memory_raw = str(task_outputs[3])
        else:
            tutor_raw = str(result)
    except Exception:
        tutor_raw = str(result)

    observer = _extract_json(observer_raw)
    strategist = _extract_json(strategist_raw)
    tutor = _extract_json(tutor_raw)
    memory = _extract_json(memory_raw)

    reply = tutor.get("reply") or tutor.get("raw") or str(result)

    return {
        "reply": reply,
        "affect": observer.get("affect"),
        "move": strategist.get("move"),
        "micro_goal": strategist.get("micro_goal"),
        "memory_update": memory,
        "debug": {
            "observer": observer,
            "strategist": strategist,
            "tutor": tutor,
            "memory": memory,
        },
    }