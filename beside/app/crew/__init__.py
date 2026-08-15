import os

from .crew import run_mentor_turn as run_crew_mentor_turn
from .fast_mentor import run_fast_mentor_turn
from .llm_config import mentor_mode


def run_mentor_turn(**kwargs):
    """Dispatch to fast (1 call) or crew (4 agents) based on MENTOR_MODE."""
    if mentor_mode() == "crew":
        return run_crew_mentor_turn(**kwargs)
    return run_fast_mentor_turn(**kwargs)


__all__ = ["run_mentor_turn", "run_fast_mentor_turn", "run_crew_mentor_turn"]