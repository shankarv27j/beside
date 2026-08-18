import os

from crewai import LLM
from openai import OpenAI


def _provider() -> str:
    return os.getenv("LLM_PROVIDER", "ollama").strip().lower()


def get_llm() -> LLM:
    """CrewAI LLM (used when MENTOR_MODE=crew)."""
    provider = _provider()

    if provider == "openai":
        model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        return LLM(model=f"openai/{model}")

    if provider == "groq":
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        return LLM(model=f"groq/{model}")

    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return LLM(
        model=f"ollama/{model}",
        base_url=base_url,
    )


def get_chat_client() -> tuple[OpenAI, str]:
    """OpenAI-compatible client for the fast mentor path."""
    provider = _provider()

    if provider == "openai":
        return (
            OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
            os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
        )

    if provider == "groq":
        return (
            OpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
            ),
            os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        )

    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    return OpenAI(base_url=base, api_key="ollama"), model


# Back-compat alias
def get_openai_client() -> tuple[OpenAI, str]:
    return get_chat_client()


def mentor_mode() -> str:
    return os.getenv("MENTOR_MODE", "fast").strip().lower()


def llm_status() -> dict:
    provider = _provider()
    mode = mentor_mode()
    if provider == "openai":
        return {
            "provider": "openai",
            "mentor_mode": mode,
            "model": os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
            "ready": bool(os.getenv("OPENAI_API_KEY")),
        }
    if provider == "groq":
        return {
            "provider": "groq",
            "mentor_mode": mode,
            "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            "ready": bool(os.getenv("GROQ_API_KEY")),
        }
    return {
        "provider": "ollama",
        "mentor_mode": mode,
        "model": os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "ready": True,
    }
