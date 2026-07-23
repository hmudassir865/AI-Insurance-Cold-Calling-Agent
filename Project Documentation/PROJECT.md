# AI Health Insurance Cold Calling Agent

An AI-powered outbound cold calling system for health insurance lead qualification. Supports multi-LLM fallback, local STT/TTS, and SignalWire telephony.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Python 3.12), Uvicorn |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Recharts |
| **Database** | PostgreSQL 16, SQLAlchemy (async) |
| **LLM** | Groq (Llama 3 70B) primary, Google Gemini fallback, Ollama local fallback |
| **TTS** | ElevenLabs → gTTS (free fallback) |
| **STT** | OpenAI Whisper (local) |
| **Telephony** | SignalWire (Twilio SDK) + ngrok tunnel |
| **Auth** | JWT access/refresh tokens |
| **Real-time** | WebSocket (dashboard updates) |
| **Deployment** | Docker Compose, Render |

---

## Directory Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point, CORS, middleware
│   │   ├── config.py               # Settings from .env
│   │   ├── database.py             # Async SQLAlchemy engine + session
│   │   ├── ws_manager.py           # WebSocket connection manager
│   │   ├── celery_app.py           # Celery task queue (optional)
│   │   ├── __init__.py             # aiohttp DNS patch
│   │   ├── routes/
│   │   │   ├── auth.py             # Login, register, token refresh
│   │   │   ├── calls.py            # Initiate, process-speech, audio, test endpoints
│   │   │   ├── leads.py            # CRUD leads + bulk upload
│   │   │   ├── campaigns.py        # CRUD campaigns
│   │   │   ├── analytics.py        # Dashboard stats
│   │   │   └── rag.py              # Knowledge base management
│   │   ├── services/
│   │   │   ├── voice_service.py    # SignalWire calls, TwiML generation
│   │   │   ├── conversation_service.py  # AI conversation flow
│   │   │   ├── multi_llm_service.py     # Multi-provider LLM (direct httpx)
│   │   │   ├── tts_service.py           # Text-to-speech (ElevenLabs + gTTS)
│   │   │   ├── stt_service.py           # Speech-to-text (Whisper)
│   │   │   ├── rag_service.py           # RAG knowledge base queries
│   │   │   ├── lead_scoring.py          # Lead qualification engine
│   │   │   ├── cache_service.py         # Redis cache with in-memory fallback
│   │   │   └── voice_service_asterisk.py # Asterisk SIP testing (unused)
│   │   ├── models/
│   │   │   ├── user.py             # User model
│   │   │   ├── lead.py             # Lead model
│   │   │   ├── campaign.py         # Campaign model
│   │   │   └── call_log.py         # Call log model
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── middleware/
│   │   │   ├── logging_mw.py       # Request logging
│   │   │   ├── error_handler.py    # Global exception handler
│   │   │   └── rate_limit.py       # Rate limiting
│   │   └── utils/
│   │       ├── auth.py             # JWT encoding/decoding
│   │       ├── dependencies.py     # FastAPI dependency injection
│   │       ├── helpers.py          # Utility functions
│   │       └── logging_setup.py    # Structlog configuration
│   ├── alembic/                    # DB migrations
│   ├── tests/                      # Test files
│   ├── .env                        # Environment variables
│   └── requirements.txt
├── frontend-react/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx       # Dashboard + Test Call UI with audio
│   │   │   ├── Leads.tsx           # Lead management
│   │   │   ├── Campaigns.tsx       # Campaign management
│   │   │   ├── CallHistory.tsx     # Call logs + transcripts
│   │   │   ├── Settings.tsx        # System settings
│   │   │   └── Login.tsx           # Login page
│   │   ├── api/
│   │   │   ├── client.ts           # HTTP client with JWT auto-refresh
│   │   │   ├── calls.ts            # Call API (initiate, history, test)
│   │   │   ├── leads.ts            # Lead CRUD API
│   │   │   ├── campaigns.ts        # Campaign API
│   │   │   ├── analytics.ts        # Dashboard stats API
│   │   │   └── auth.ts             # Auth API
│   │   ├── hooks/useWebSocket.ts   # WebSocket hook
│   │   ├── context/AuthContext.tsx  # Auth state provider
│   │   ├── components/             # Shared UI components
│   │   └── types/index.ts          # TypeScript interfaces
│   ├── vite.config.ts              # Vite + proxy config
│   └── package.json
├── scripts/
│   ├── seed_data.py                # Seed leads + campaign
│   ├── seed_admin.py               # Seed admin user
│   ├── seed_knowledge.py           # Seed RAG documents
│   └── sample_leads.csv            # Sample leads template
├── docker-compose.yml              # PostgreSQL + backend
├── docker-compose.asterisk.yml     # Asterisk SIP server
├── nginx.conf                      # Nginx reverse proxy
├── render.yaml                     # Render deployment config
└── PROJECT.md                      # This file
```

---

## Setup & Running

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 16
- ngrok (for SignalWire webhooks)

### 1. Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend

```powershell
cd frontend-react
npm install
npm run dev
```

### 3. Database

```powershell
# Create database
psql -U postgres -c "CREATE DATABASE insurance_cold_calling;"

# Run migrations
cd backend
alembic upgrade head

# Seed data
python scripts/seed_admin.py
python scripts/seed_data.py
```

### 4. ngrok (for SignalWire)

```powershell
ngrok http http://localhost:8000 --domain=your-domain.ngrok-free.dev
```

Update `SIGNALWIRE_WEBHOOK_BASE_URL` in `backend/.env` with the ngrok URL.

---

## Environment Variables

`backend/.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/insurance_cold_calling

# Google Gemini (FREE - https://aistudio.google.com/apikey)
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash

# Groq (FREE - https://console.groq.com/keys)
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Ollama (local, optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b

# SignalWire
SIGNALWIRE_SPACE=your_space.signalwire.com
SIGNALWIRE_PROJECT_ID=your_project_id
SIGNALWIRE_AUTH_TOKEN=your_token
SIGNALWIRE_PHONE_NUMBER=+1xxxxxxxxxx
SIGNALWIRE_WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok-free.dev

# ElevenLabs (FREE - https://elevenlabs.io)
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Whisper (local, FREE)
WHISPER_MODEL=base

# JWT
JWT_SECRET_KEY=your_secret_key_here
```

---

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/login` | Login (email + password) |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/refresh` | Refresh access token |

### Leads
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/leads` | List leads (paginated) |
| GET | `/api/leads/{id}` | Get lead details |
| POST | `/api/leads` | Create lead |
| PATCH | `/api/leads/{id}` | Update lead |
| DELETE | `/api/leads/{id}` | Delete lead |
| POST | `/api/leads/bulk-upload` | Upload CSV leads |

### Campaigns
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/campaigns` | List campaigns |
| POST | `/api/campaigns` | Create campaign |
| PATCH | `/api/campaigns/{id}` | Update campaign |
| POST | `/api/campaigns/{id}/activate` | Activate campaign |

### Calls
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/calls/initiate` | Start outbound call (SignalWire) |
| POST | `/api/calls/test-local/{lead_id}` | Start test call (no SignalWire) |
| POST | `/api/calls/test-process-speech` | Send text to AI pipeline |
| GET | `/api/calls/audio-response/{id}` | Get generated audio file |
| GET | `/api/calls/history` | List call logs |
| POST | `/api/calls/status` | SignalWire status webhook |
| POST | `/api/calls/outbound-twiml/{id}` | TwiML greeting endpoint |
| POST | `/api/calls/process-speech` | TwiML speech processing |

### Analytics
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/analytics/dashboard` | Dashboard stats (calls, leads, conversion) |

### RAG
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/rag/query` | Query knowledge base |
| POST | `/api/rag/index` | Index a document |
| DELETE | `/api/rag/documents/{id}` | Delete a document |

### WebSocket
| Path | Description |
|------|-------------|
| `/ws` | Real-time call status updates |

---

## LLM Provider Fallback Chain

1. **Gemini** (Google, free tier) — primary if key works
2. **Groq** (Llama 3 70B, free tier) — current active provider
3. **Ollama** (local, free) — runs offline, no API key needed
4. **OpenAI** (GPT-4o, paid) — needs API key
5. **Anthropic** (Claude, paid) — needs API key

The service automatically falls through providers if one fails (quota, timeout, network error).

---

## Audio Flow

```
User input (text/mic)
    → MultiLLMService.generate_response()
    → TextToSpeechService.synthesize()
        → ElevenLabs API (if key works)
        → gTTS fallback (free, offline)
    → Audio stored in memory
    → URL returned: /api/calls/audio-response/{id}
    → Frontend plays via <audio> element
```

---

## Known Issues

| Issue | Status |
|-------|--------|
| SignalWire trial blocks unverified outbound calls | Need $5 credit or verify numbers |
| ElevenLabs free tier 402 | gTTS fallback active |
| Gemini quota exhausted | Groq is primary |
| Old backend PID may block port 8000 | Restart required |
| gTTS debug logging spam | Console noise, not a bug |
| Redis not running | cache_service degrades gracefully |

---

## Testing the AI Pipeline

```powershell
# 1. Login
$token = (Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
  -Method Post -Body '{"email":"admin@ncai.com","password":"Admin@123"}' `
  -ContentType "application/json").access_token

# 2. Start test call
$lead = (Invoke-RestMethod -Uri "http://localhost:8000/api/leads?page_size=1" `
  -Headers @{Authorization="Bearer $token"}).leads[0]
$call = Invoke-RestMethod -Uri "http://localhost:8000/api/calls/test-local/$($lead.id)" `
  -Headers @{Authorization="Bearer $token"} -Method Post

# 3. Send a message
$r = Invoke-RestMethod -Uri "http://localhost:8000/api/calls/test-process-speech?call_log_id=$($call.call_log_id)&text=Tell%20me%20about%20plans" `
  -Headers @{Authorization="Bearer $token"} -Method Post
$r.ai_response  # AI reply text
$r.audio_url    # Audio file URL
```
