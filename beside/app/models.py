from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


def _uuid() -> str:
    return str(uuid4())


class Child(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    name: str
    age: int = 10
    interest: str = "stories"
    skill_focus: str = "arithmetic"
    affect: str = "unknown"
    what_clicked: str = Field(default="[]", sa_column=Column(Text))
    what_stuck: str = Field(default="[]", sa_column=Column(Text))
    misconceptions: str = Field(default="[]", sa_column=Column(Text))
    notes: str = Field(
        default="New learner. Build trust first.",
        sa_column=Column(Text),
    )
    session_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TutorSession(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    child_id: str = Field(index=True)
    skill: str = "arithmetic"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    active: bool = True


class Turn(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    session_id: str = Field(index=True)
    child_id: str = Field(index=True)
    child_message: str = Field(sa_column=Column(Text))
    tutor_reply: str = Field(sa_column=Column(Text))
    affect: Optional[str] = None
    move: Optional[str] = None
    micro_goal: Optional[str] = None
    memory_update_json: str = Field(default="{}", sa_column=Column(Text))
    human_rating: Optional[str] = None  # me | not_me | null
    human_better_reply: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)