"""How Beside grows with each child: merge turn memory into the profile."""

import json
from datetime import datetime
from typing import Any

from app.models import Child


def _loads_list(raw: str) -> list[str]:
    try:
        data = json.loads(raw or "[]")
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def profile_blob(child: Child) -> str:
    return (
        f"Name: {child.name}; age: {child.age}; interest: {child.interest}; "
        f"skill: {child.skill_focus}; affect: {child.affect}; "
        f"sessions: {child.session_count}; "
        f"what_clicked: {_loads_list(child.what_clicked)}; "
        f"what_stuck: {_loads_list(child.what_stuck)}; "
        f"misconceptions: {_loads_list(child.misconceptions)}; "
        f"notes: {child.notes}"
    )


def merge_memory(child: Child, memory_update: dict[str, Any], affect: str | None) -> Child:
    def merge(field: str, key: str) -> str:
        current = _loads_list(getattr(child, field))
        incoming = memory_update.get(key) or []
        if isinstance(incoming, str):
            incoming = [incoming]
        merged = list(dict.fromkeys([*current, *[str(x) for x in incoming if x]]))[-12:]
        return json.dumps(merged)

    child.what_clicked = merge("what_clicked", "what_clicked")
    child.what_stuck = merge("what_stuck", "what_stuck")
    child.misconceptions = merge("misconceptions", "misconceptions")
    notes = memory_update.get("notes")
    if notes:
        child.notes = str(notes)[:1000]
    if affect:
        child.affect = affect
    child.updated_at = datetime.utcnow()
    return child


def history_blob(turns: list) -> str:
    if not turns:
        return "(no prior turns)"
    lines = []
    for t in turns[-8:]:
        lines.append(f"child: {t.child_message}")
        lines.append(f"tutor[{t.move or '?'}]: {t.tutor_reply}")
    return "\n".join(lines)