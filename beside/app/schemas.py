from typing import Any, Optional

from pydantic import BaseModel, Field


class TurnRequest(BaseModel):
    child_name: str = Field(default="Asha", min_length=1, max_length=40)
    age: int = Field(default=10, ge=8, le=14)
    skill: str = Field(default="arithmetic", description="reading | writing | arithmetic")
    interest: str = Field(default="cricket")
    profile: str = Field(default="New learner. Build trust first.")
    history: str = Field(default="(no prior turns)")
    child_message: str = Field(min_length=1, max_length=2000)


class TurnResponse(BaseModel):
    reply: str
    affect: Optional[str] = None
    move: Optional[str] = None
    micro_goal: Optional[str] = None
    memory_update: dict[str, Any] = Field(default_factory=dict)
    debug: dict[str, Any] = Field(default_factory=dict)