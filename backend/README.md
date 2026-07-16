# AI Receptionist Agent (Python)

Text-first appointment booking agent. No frontend yet. Voice (Vapi), Google Calendar, Sheets, and email come next.

## What this project does

```
You (terminal / API)
    → FastAPI
    → LangGraph ReAct agent (GPT-4o)
    → Tools: check_availability, book_appointment
    → In-memory session + activity log
```

Flow:

1. Create a session with patient name, phone, reason
2. Agent greets and offers a slot (calls `check_availability`)
3. You negotiate ("No, Friday at 5")
4. Agent checks again, then calls `book_appointment`
5. Mock Calendar / Sheets / Email print to the server console
6. Activity log shows every step (demo proof)

## Project structure

```
backend/
├── .env                 # your secrets (not committed)
├── .env.example         # template
├── pyproject.toml       # dependencies
├── README.md            # this file
├── scripts/
│   └── chat_cli.py      # interactive terminal test
└── src/
    ├── main.py          # FastAPI app
    ├── config.py        # typed settings from .env
    ├── models/          # Booking, Session, etc.
    ├── services/        # in-memory session store
    ├── agent/
    │   ├── prompts.py   # system prompt
    │   ├── tools.py     # check_availability, book_appointment
    │   └── graph.py     # LangGraph agent loop
    └── api/
        ├── schemas.py   # request/response models
        └── routes.py    # /api/sessions, /api/chat
```

## Setup (one time)

### 1. Python 3.11+

```powershell
python --version
```

### 2. Virtual environment

```powershell
cd "D:\Agentic AI Projects\AI Voice Assistant\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -e .
```

### 4. API key

Copy `.env.example` → `.env` if needed, then set:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
CLINIC_NAME=XYZ Clinic
```

Get a key: https://platform.openai.com/api-keys

## Run the server

```powershell
cd "D:\Agentic AI Projects\AI Voice Assistant\backend"
.\.venv\Scripts\Activate.ps1
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- Health: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs

## How to test

### Option A — Interactive CLI (best)

With the server running, open a **second** terminal:

```powershell
cd "D:\Agentic AI Projects\AI Voice Assistant\backend"
.\.venv\Scripts\Activate.ps1
python -m scripts.chat_cli
```

Example conversation:

```
Patient name: Mehak
Phone: +919876543210
Reason: Dental checkup

Agent: Hello Mehak, I'm calling from XYZ Clinic... Tomorrow at 4 PM work?

You: No, Friday around 5
Agent: Friday at 5 is available. Shall I book that?

You: Yes
Agent: Done! I've booked your appointment for Friday at 5 PM.
```

Watch the **server terminal** for mock logs:

```
[tool] check_availability → ...
[Calendar] MOCK create event: ...
[Sheets] MOCK append row: ...
[Email] MOCK confirmation ...
```

### Option B — curl / PowerShell

**Start session:**

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/sessions `
  -ContentType "application/json" `
  -Body '{"name":"Mehak","phone":"+919876543210","reason":"Dental checkup"}'
```

Copy `session_id` from the response.

**Continue chat:**

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/chat `
  -ContentType "application/json" `
  -Body '{"session_id":"PASTE_ID","message":"No, Friday at 5 works"}'
```

**Confirm:**

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/chat `
  -ContentType "application/json" `
  -Body '{"session_id":"PASTE_ID","message":"Yes, book it"}'
```

### Option C — Swagger

1. Open http://127.0.0.1:8000/docs
2. Try `POST /api/sessions`
3. Then `POST /api/chat` with the returned `session_id`

## What is already complete

| Piece | Status |
|-------|--------|
| Config from `.env` | Done |
| LangGraph tool-calling agent | Done |
| `check_availability` (mock slots) | Done |
| `book_appointment` (mock side-effects) | Done |
| Multi-turn memory | Done |
| Activity log for demos | Done |
| FastAPI + Swagger | Done |
| Terminal chat CLI | Done |
| Frontend / website | Not yet |
| Real Vapi phone calls | Not yet |
| Real Google Calendar / Sheets | Not yet |
| Real Email / SMS | Not yet |

## What you should do next (to make it “production complete”)

### Step 1 — Prove the agent works (today)

1. Put `OPENAI_API_KEY` in `.env`
2. Run uvicorn
3. Run `python -m scripts.chat_cli`
4. Negotiate a slot and get `is_booked: true`

### Step 2 — Connect Vapi (real phone call)

1. Create account at https://dashboard.vapi.ai
2. Buy / attach a phone number
3. Create an assistant that calls your `/api` tools (or mirrors the same prompt + tools)
4. Fill `VAPI_*` in `.env`
5. Add outbound-call trigger when a session starts (or when a future form is submitted)

### Step 3 — Real Google Calendar + Sheets

1. Create a Google Cloud service account
2. Share a calendar + sheet with that account
3. Replace the MOCK prints in `src/agent/tools.py` → `book_appointment` with Calendar insert + Sheets append

### Step 4 — Email / SMS

1. SendGrid for email
2. Twilio for SMS
3. Wire them after a successful `book_appointment`

### Step 5 — Frontend (last)

Simple form: Name, Phone, Reason → `POST /api/sessions` (or a new `/api/book` that also triggers Vapi).

The agent is already the hard part — the UI only starts the session.

## API cheat sheet

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Server + key status |
| POST | `/api/sessions` | Start booking + agent greeting |
| POST | `/api/chat` | Send patient message |
| GET | `/api/sessions/{id}` | Status + activity log |
| GET | `/api/sessions` | List all sessions |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `OPENAI_API_KEY not set` | Add key to `.env`, restart uvicorn |
| `ModuleNotFoundError: src` | Run from `backend/` with venv; `pip install -e .` |
| Agent ignores tools | Use `gpt-4o` (or another strong tool-calling model) |
| Sessions disappear on restart | Expected — store is in-memory; add Redis/DB later |
| Execution policy on Activate.ps1 | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |

## Design notes (why this shape)

- **LangGraph ReAct** — agent can think → call tool → observe → reply (not a single prompt)
- **Pydantic everywhere** — validated inputs/outputs
- **Mock integrations first** — prove booking logic before wiring Google/Vapi
- **Activity log** — demo proof of orchestration without a frontend
