import os

from crewai import LLM
from openai import OpenAI


def get_llm() -> LLM:
    """CrewAI LLM (used when MENTOR_MODE=crew)."""
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    if provider == "openai":
        model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        return LLM(model=f"openai/{model}")

    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return LLM(
        model=f"ollama/{model}",
        base_url=base_url,
    )


def get_openai_client() -> tuple[OpenAI, str]:
    """OpenAI-compatible client for fast single-call mentor.

    Works with Ollama (local) or OpenAI cloud via LLM_PROVIDER.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    if provider == "openai":
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY")), os.getenv(
            "OPENAI_MODEL_NAME", "gpt-4o-mini"
        )

    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    return OpenAI(base_url=base, api_key="ollama"), model


def mentor_mode() -> str:
    return os.getenv("MENTOR_MODE", "fast").strip().lower()


def llm_status() -> dict:
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    mode = mentor_mode()
    if provider == "openai":
        return {
            "provider": "openai",
            "mentor_mode": mode,
            "model": os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
            "ready": bool(os.getenv("OPENAI_API_KEY")),
        }
    return {
        "provider": "ollama",
        "mentor_mode": mode,
        "model": os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "ready": True,
    }