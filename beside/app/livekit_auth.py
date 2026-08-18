"""Mint LiveKit access tokens for Beside classroom voice sessions."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import timedelta

from livekit import api


AGENT_NAME = "beside-tutor"


def _clean_env(name: str) -> str:
    """Strip whitespace and accidental quotes from .env values."""
    value = (os.getenv(name) or "").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1].strip()
    return value


@dataclass(frozen=True)
class LiveKitConfig:
    url: str
    api_key: str
    api_secret: str


def get_livekit_config() -> LiveKitConfig | None:
    url = _clean_env("LIVEKIT_URL")
    key = _clean_env("LIVEKIT_API_KEY")
    secret = _clean_env("LIVEKIT_API_SECRET")
    if not url or not key or not secret:
        return None
    return LiveKitConfig(url=url, api_key=key, api_secret=secret)


def room_name_for_session(session_id: str) -> str:
    return f"beside-{session_id}"


def session_id_from_room(room: str) -> str | None:
    prefix = "beside-"
    if not room.startswith(prefix):
        return None
    return room[len(prefix) :] or None


def mint_child_token(
    *,
    config: LiveKitConfig,
    session_id: str,
    child_id: str,
    child_name: str,
) -> dict[str, str]:
    """Return url, token, and room for the child participant.

    Room name encodes session_id (`beside-{session_id}`) so the agent can load
    the learner without putting agent-dispatch metadata in the JWT (that field
    causes \"invalid token\" on some LiveKit Cloud builds).
    """
    room = room_name_for_session(session_id)

    token = (
        api.AccessToken(config.api_key, config.api_secret)
        .with_identity(f"child-{child_id}")
        .with_name(child_name)
        .with_ttl(timedelta(hours=2))
        .with_attributes(
            {
                "child_id": child_id,
                "session_id": session_id,
            }
        )
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .with_room_config(
            api.RoomConfiguration(
                agents=[
                    api.RoomAgentDispatch(
                        agent_name=AGENT_NAME,
                    )
                ]
            )
        )
        .to_jwt()
    )

    return {"url": config.url, "token": token, "room": room}
