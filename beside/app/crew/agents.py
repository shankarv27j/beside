from pathlib import Path

from crewai import Agent

from .llm_config import get_llm

OS_PATH = Path(__file__).with_name("mentoring_os.md")


def _load_os() -> str:
    return OS_PATH.read_text(encoding="utf-8")


def build_agents() -> dict[str, Agent]:
    os_text = _load_os()
    llm = get_llm()

    observer = Agent(
        role="Observer",
        goal="Infer how the child feels and why they may be stuck.",
        backstory=(
            "You are the perception layer of a devoted mentor. "
            "You never speak to the child. You only diagnose affect and evidence.\n\n"
            f"Follow this Mentoring OS:\n{os_text}"
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    strategist = Agent(
        role="Strategist",
        goal="Choose exactly one pedagogy move and one micro-goal for this turn.",
        backstory=(
            "You are the decision layer of a devoted mentor. "
            "You never speak to the child. You pick the next move.\n\n"
            f"Follow this Mentoring OS:\n{os_text}"
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    tutor = Agent(
        role="Tutor",
        goal="Speak to the child warmly, briefly, and without shame.",
        backstory=(
            "You are the voice of Beside: a 1:1 AI tutor that sits beside the child. "
            "You alone speak to the child. Sound like a patient human mentor.\n\n"
            f"Follow this Mentoring OS:\n{os_text}"
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    memory_writer = Agent(
        role="Memory Writer",
        goal="Propose durable updates to the child's long-term profile.",
        backstory=(
            "You are the memory layer of a devoted mentor. "
            "You never speak to the child. You record what clicked, what stuck, "
            "and any misconception for next session.\n\n"
            f"Follow this Mentoring OS:\n{os_text}"
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    return {
        "observer": observer,
        "strategist": strategist,
        "tutor": tutor,
        "memory_writer": memory_writer,
    }