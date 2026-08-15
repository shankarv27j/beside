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

## Interfaces now → face to face later

| Phase | Interface | What you add |
|---|---|---|
| **Now** | Web classroom (this app) | Text chat + learner panel + parent view + “That’s me / Not me” |
| **Next** | Voice classroom | Whisper (child speaks) + TTS (tutor speaks). Same crew underneath |
| **Later** | Face to face feel | Camera optional, avatar/talking head, or LiveKit if a human jumps in |

Same mentor brain. Only the I/O layer changes (text → voice → richer presence).

## Latency: what we changed

| Before | After (default) |
|---|---|
| 4 CrewAI agents per message (30–120s) | **1 model call** (`MENTOR_MODE=fast`) |
| Frozen form submit | **Thinking banner** + optimistic child bubble via `fetch` |
| Crew only | Fast path now; set `MENTOR_MODE=crew` to compare |

**Async?** Browser side yes (`fetch` + UI). Server stays a normal sync request for SQLite safety. That is enough for a working local app. Later: queues / streaming if you need more.

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

### Streamlit (recommended for you)
```powershell
cd C:\Users\SHANKAR-KRISHNA\primerycomb\beside
.\.venv\Scripts\python.exe -m pip install streamlit
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```
Opens a Python-native classroom: Home, Classroom (chat + learner model), Parent view, That’s me / Not me.

### FastAPI + Jinja (older HTML UI)
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
http://localhost:8000

Same mentor brain + SQLite memory either way.  

## Project layout

```text
beside/
  app/
    main.py           # UI + routes
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
