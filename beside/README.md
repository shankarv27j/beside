# Beside — classroom app + CrewAI mentor brain

1:1 AI tutor with a real UI. Each child has a lasting learner model so the tutor **grows with them**.

## How it grows with each child

```text
Session 1: child struggles → Memory Writer logs what stuck / what clicked
     ↓ saved in SQLite (later Postgres)
Session 2: profile + history loaded into the crew
     ↓
Tutor starts from who THIS child is, not from zero
```

Stored per child:
- what_clicked
- what_stuck
- misconceptions
- notes, affect, skill focus, session count

That compounding memory is the “grows with each child” product.

## Interfaces

| Phase | Interface | Status |
|---|---|---|
| **Now** | Text classroom (FastAPI + Streamlit) | Working |
| **Now** | Voice classroom (LiveKit) | Working — see below |
| **Next** | Stronger presence | Camera optional, richer voice |

Same mentor brain (`process_turn`). Text and voice both write learner memory.

## Voice classroom (LiveKit)

You need **two terminals** and LiveKit Cloud keys in `.env`.

**Terminal 1 — website**
```powershell
cd C:\Users\SHANKAR-KRISHNA\primerycomb\beside
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — voice agent**
```powershell
cd C:\Users\SHANKAR-KRISHNA\primerycomb\beside
.\.venv\Scripts\python.exe -m app.voice_agent dev
```

Then open http://localhost:8000 → create/open a child → **Join video call** (camera + mic) or **Voice only** → speak.

Flow: mic/camera → LiveKit → STT → Beside `process_turn` → TTS. The AI tutor is voice-only for now (placeholder tile); your camera shows in the call stage. Refresh the page to see turns in the transcript.

STT/TTS use **LiveKit Inference** (billed on your LiveKit Cloud project). The mentor reply uses your `LLM_PROVIDER` (Ollama, OpenAI, or Groq).

### Groq (free tier, much faster than local Ollama)

1. Create a key at [console.groq.com](https://console.groq.com)
2. Put in `.env`:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
GROQ_MODEL=openai/gpt-oss-20b
MENTOR_MODE=fast
```

Smarter options: `openai/gpt-oss-120b` or `qwen/qwen3.6-27b`  
(Older IDs like `llama-3.1-8b-instant` were retired by Groq.)  
Restart uvicorn (and the voice agent) after changing `.env`.

Switch to OpenAI anytime:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL_NAME=gpt-4o-mini
MENTOR_MODE=fast
```

## Your next step: videos of you mentoring

1. Record (with consent) how you unstick a real student  
2. Transcribe + label: situation → your move → what you said  
3. Store as an **example bank**  
4. Inject top similar examples into the fast mentor prompt (RAG later)  

That is how the model becomes a replica of you, not just a generic tutor.

## UI options

### Streamlit (text classroom)
```powershell
cd C:\Users\SHANKAR-KRISHNA\primerycomb\beside
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

### FastAPI + Jinja (text + LiveKit voice)
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
http://localhost:8000

Same mentor brain + SQLite memory either way.  

## Project layout

```text
beside/
  app/
    main.py           # UI + routes + LiveKit token
    livekit_auth.py   # mint join tokens + agent dispatch
    voice_agent.py    # LiveKit worker: STT → process_turn → TTS
    models.py         # Child, Session, Turn
    memory.py         # merge profile across turns
    services.py       # create child, process turn
    crew/             # Observer → Strategist → Tutor → Memory
    templates/        # Jinja classroom UI
    static/
  data/beside.db      # created on first run
```

## Human in the loop

Under each tutor reply: **That’s me** / **Not me**.  
Those ratings are how you teach the system your style before fine-tuning.
