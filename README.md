<p align="center">
  <img src="frontend-react/public/favicon.svg" width="80" alt="NCAI Logo"/>
</p>

<h1 align="center">AI Insurance Cold Calling Agent</h1>

<p align="center">
  <em>AI-powered outbound cold calling system for health insurance lead qualification</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white" alt="React 18"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL 16"/>
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" alt="Docker Compose"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License MIT"/>
</p>

---

## About

This system automates the initial insurance lead conversation using an AI voice agent. It can call leads, engage them in natural conversations, understand their responses, qualify their interest, and log call results in real time.

The system combines LLMs, RAG, speech recognition, text to speech, and PSTN telephony into an end to end AI pipeline. It supports multi LLM fallback across Groq, Gemini, Ollama, OpenAI, and Anthropic, with Whisper and gTTS for speech processing and SignalWire for phone calls.

The goal is to automate the initial lead qualification process while keeping the system flexible, observable, and scalable for insurance workflows.

---

## How It Works

The system follows an end to end voice AI pipeline:

1. **Lead Calling**
   The system initiates outbound calls to insurance leads through SignalWire.

2. **Speech Recognition**
   The lead's speech is captured and converted into text using OpenAI Whisper.

3. **Context & Retrieval**
   Relevant insurance information is retrieved from the knowledge base using RAG and pgvector.

4. **LLM Processing**
   The conversation is processed by the configured LLM. The system supports multiple LLM providers with fallback handling.

5. **Voice Response**
   The generated response is converted back into speech using ElevenLabs or gTTS.

6. **Conversation Tracking**
   Call transcripts, lead information, sentiment, and call outcomes are stored for later analysis.

7. **Real Time Monitoring**
   The dashboard provides real time visibility into calls, conversations, and lead activity.

---

## Features

| Category | Details |
|----------|---------|
| **AI Conversation Engine** | Multi-provider LLM with automatic fallback chain, RAG-enhanced responses, objection handling |
| **Text-to-Speech** | ElevenLabs API (primary) with automatic gTTS fallback |
| **Speech-to-Text** | Local OpenAI Whisper model (no API cost) |
| **Telephony Integration** | Outbound PSTN calls via SignalWire (Twilio SDK), TwiML call flow, status webhooks |
| **Lead Management** | CRUD operations, CSV bulk upload, campaign assignment, status tracking (pending/contacted/interested/not-interested) |
| **Campaign Management** | Draft/Active/Paused/Completed lifecycle, configurable scripts, progress tracking |
| **Lead Scoring** | Prioritization engine based on language, call history, time-of-day, response rate |
| **Real-Time Dashboard** | WebSocket-powered live updates, bar/line charts (Recharts), key metrics overview |
| **Call Logging** | Full transcript storage, sentiment analysis, AI-generated summaries |
| **JWT Authentication** | Role-based access (admin/agent), auto-refresh tokens, bcrypt password hashing |
| **RAG Knowledge Base** | Insurance document indexing with Google embeddings, LangChain text splitting |
| **Test Pipeline** | Local AI pipeline testing without telephony — text or microphone input |
| **Containerized Deployment** | Docker Compose for local prod, Render (free tier) config included |

---

## System Architecture

The system follows an end to end voice AI architecture that connects telephony, speech processing, retrieval, LLM reasoning, and data storage.

```
text
Insurance Lead
      │
      ▼
SignalWire / PSTN
      │
      ▼
Speech to Text
   (Whisper)
      │
      ▼
Conversation Processing
      │
      ├──► RAG / pgvector
      │         │
      │         ▼
      │    Relevant Context
      │
      ▼
LLM Layer
(Groq / Gemini / Ollama / OpenAI / Anthropic)
      │
      ▼
Text to Speech
(ElevenLabs / gTTS)
      │
      ▼
Voice Response
      │
      ▼
Insurance Lead

      │
      ▼
PostgreSQL
(Calls, Leads, Transcripts,
Sentiment & Outcomes)

      │
      ▼
React Dashboard
(Real Time Monitoring)

### Conversation Flow

---

Inbound Audio (PSTN)
    → Whisper STT (local transcription)
    → MultiLLMService.generate_response()
        → Gemini → Groq → Ollama → OpenAI → Anthropic (fallback chain)
        → RAG context injected from knowledge base
    → TextToSpeechService.synthesize()
        → ElevenLabs API (primary) → gTTS (fallback)
    → Audio served via /api/calls/audio-response/{id}
    → Transcript + Sentiment → stored in PostgreSQL
    → WebSocket event → Dashboard live update

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Uvicorn, SQLAlchemy 2.0 (async), Pydantic, Celery |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide |
| **Database** | PostgreSQL 16 + pgvector, Asyncpg, Alembic |
| **LLM** | Groq (Llama 3 70B), Google Gemini, Ollama, OpenAI, Anthropic |
| **TTS** | ElevenLabs API, gTTS (Google Translate) |
| **STT** | OpenAI Whisper (local, base model) |
| **Telephony** | SignalWire (Twilio SDK), TwiML, ngrok |
| **Auth** | JWT (python-jose), bcrypt (passlib) |
| **Infrastructure** | Docker Compose, Nginx, Render, Redis |

```

---

```

## The Hardest Engineering Challenge

One of the most challenging parts of this project was getting the voice and telephony pipeline to work reliably.

At different stages of development, the agent was not producing the expected voice response and outbound calls were not working correctly. The challenge was not limited to a single component — the issue involved the interaction between the telephony, speech processing, and voice generation layers.

Instead of treating it as a single error, I broke the pipeline into smaller components and tested each stage independently:

1. Verified that the outbound call was being initiated correctly.
2. Checked whether the incoming speech was being captured and converted to text.
3. Verified that the LLM was generating the expected response.
4. Tested whether the generated response was reaching the text to speech layer.
5. Checked whether the generated audio was being returned correctly through the telephony flow.
6. Tested the complete pipeline again after isolating and fixing the failing component.

This experience taught me an important lesson about building AI applications:

> **When multiple systems are connected together, debugging the complete pipeline requires understanding how each component interacts with the others.**

It also reinforced my approach to engineering:

**Learn → Build → Test → Break → Debug → Understand → Share**

```
---

## Project Structure

```
AI_Insurance_Cold_Calling_Agent/
├── backend/                          # FastAPI application
│   ├── app/
│   │   ├── main.py                   # Entry point, CORS, middleware
│   │   ├── config.py                 # Settings from .env
│   │   ├── database.py               # Async SQLAlchemy engine
│   │   ├── ws_manager.py             # WebSocket manager
│   │   ├── celery_app.py             # Celery task queue
│   │   ├── routes/                   # API route handlers
│   │   │   ├── auth.py               # Login, register, refresh
│   │   │   ├── calls.py              # Call initiation, TwiML, test
│   │   │   ├── leads.py              # Lead CRUD + bulk upload
│   │   │   ├── campaigns.py          # Campaign CRUD
│   │   │   ├── analytics.py          # Dashboard stats
│   │   │   └── rag.py                # Knowledge base
│   │   ├── services/                 # Business logic layer
│   │   │   ├── voice_service.py       # SignalWire + TwiML
│   │   │   ├── conversation_service.py# Conversation orchestration
│   │   │   ├── multi_llm_service.py   # Multi-provider LLM
│   │   │   ├── tts_service.py         # ElevenLabs + gTTS
│   │   │   ├── stt_service.py         # Whisper transcription
│   │   │   ├── rag_service.py         # RAG queries
│   │   │   ├── lead_scoring.py        # Lead prioritization
│   │   │   └── cache_service.py       # Redis + in-memory cache
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   ├── schemas/                  # Pydantic request/response
│   │   ├── middleware/               # Logging, error handling, rate limit
│   │   └── utils/                    # JWT, dependencies, helpers
│   ├── alembic/                      # Database migrations
│   ├── tests/                        # Test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend-react/                   # React SPA
│   ├── src/
│   │   ├── pages/                    # Dashboard, Leads, Campaigns, etc.
│   │   ├── api/                      # HTTP client, API modules
│   │   ├── hooks/                    # Custom hooks (useWebSocket)
│   │   ├── context/                  # Auth context provider
│   │   ├── components/               # Shared UI components
│   │   └── types/                    # TypeScript interfaces
│   ├── vite.config.ts
│   └── package.json
├── frontend/                         # Streamlit dashboard (secondary)
│   ├── app.py
│   ├── pages/
│   └── utils/
├── scripts/                          # Utility scripts
│   ├── seed_admin.py                 # Create admin user
│   ├── seed_data.py                  # Seed leads + campaign
│   ├── seed_knowledge.py             # Seed RAG documents
│   ├── sample_leads.csv              # CSV template
│   └── init_db.sql                   # Manual schema SQL
├── asterisk-config/                  # Asterisk SIP PBX config
├── data/                             # Recordings and lead files
├── docker-compose.yml                # Main Docker services
├── docker-compose.asterisk.yml       # Asterisk SIP server
├── nginx.conf                        # Reverse proxy config
├── render.yaml                       # Render deployment config
├── test_ai_pipeline.py               # Local AI pipeline test
└── generate_srs.py                   # SRS document generator
```

---

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 16
- Docker & Docker Compose (optional, for production-like setup)
- ngrok account (for SignalWire webhook tunnel)
- API keys: [Groq](https://console.groq.com/keys), [Gemini](https://aistudio.google.com/apikey), [ElevenLabs](https://elevenlabs.io), [SignalWire](https://signalwire.com)

---

## Quick Start

### 1. Database Setup

```powershell
psql -U postgres -c "CREATE DATABASE insurance_cold_calling;"
```

### 2. Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` from the template below, then run:

```powershell
# Run migrations
alembic upgrade head

# Seed initial data
python ..\scripts\seed_admin.py      # Creates admin@ncai.com / Admin@123
python ..\scripts\seed_data.py       # Creates sample leads + campaign
python ..\scripts\seed_knowledge.py  # Populates RAG knowledge base

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend

```powershell
cd frontend-react
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### 4. ngrok (SignalWire Webhooks)

```powershell
ngrok http http://localhost:8000 --domain=your-domain.ngrok-free.dev
```

Update `SIGNALWIRE_WEBHOOK_BASE_URL` in `backend/.env` with the ngrok URL.

---

## Docker Compose (Production-like)

```powershell
docker-compose up -d
```

Starts: PostgreSQL 16, Redis, FastAPI backend, Celery worker, Celery beat, Streamlit frontend, Nginx reverse proxy.

Optional Asterisk SIP PBX:

```powershell
docker-compose -f docker-compose.asterisk.yml up -d
```

---

## Environment Variables

Create `backend/.env`:

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

## API Overview

Full interactive API documentation at `http://localhost:8000/docs` (Swagger UI).

| Endpoint Group | Description |
|----------------|-------------|
| `POST /api/auth/*` | Login, register, token refresh |
| `GET/POST/PATCH/DELETE /api/leads/*` | Lead CRUD + CSV bulk upload |
| `GET/POST/PATCH /api/campaigns/*` | Campaign management |
| `POST /api/calls/initiate` | Start outbound SignalWire call |
| `POST /api/calls/test-local/{lead_id}` | Test AI pipeline (no telephony) |
| `GET /api/calls/history` | Paginated call logs |
| `GET /api/analytics/dashboard` | Dashboard statistics |
| `GET/POST/DELETE /api/rag/*` | Knowledge base management |
| `WS /ws` | Real-time call status updates |

---

## Testing the AI Pipeline

### Option A: Automated Test Script

```powershell
python test_ai_pipeline.py
```

### Option B: API Endpoints (PowerShell)

```powershell
# Login
$token = (Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
  -Method Post -Body '{"email":"admin@ncai.com","password":"Admin@123"}' `
  -ContentType "application/json").access_token

# Start test call
$lead = (Invoke-RestMethod -Uri "http://localhost:8000/api/leads?page_size=1" `
  -Headers @{Authorization="Bearer $token"}).leads[0]
$call = Invoke-RestMethod -Uri "http://localhost:8000/api/calls/test-local/$($lead.id)" `
  -Headers @{Authorization="Bearer $token"} -Method Post

# Send message
$r = Invoke-RestMethod -Uri "http://localhost:8000/api/calls/test-process-speech?call_log_id=$($call.call_log_id)&text=Tell%20me%20about%20plans" `
  -Headers @{Authorization="Bearer $token"} -Method Post
$r.ai_response   # AI reply text
$r.audio_url     # Audio file URL for playback
```

---

## LLM Provider Fallback Chain

```
1. Gemini (Google, free tier)      — primary if key works
2. Groq (Llama 3 70B, free tier)   — current active provider
3. Ollama (local, free)            — runs offline, no API key
4. OpenAI (GPT-4o, paid)           — needs API key
5. Anthropic (Claude, paid)        — needs API key
```

The service automatically falls through providers with exponential backoff retries (3 attempts per provider).

---

## Deployment

### Render

The `render.yaml` file defines the full deployment configuration:

- **PostgreSQL 16** managed database (free tier)
- **FastAPI backend** web service with health check at `/health`
- **React frontend** static site with SPA routing

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

---

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@ncai.com | Admin@123 |

---

## Roadmap

- [x] Multi-LLM provider fallback
- [x] Local STT/TTS (Whisper + gTTS)
- [x] SignalWire PSTN integration
- [x] Lead scoring engine
- [x] Real-time WebSocket dashboard
- [x] RAG knowledge base
- [x] Docker Compose deployment
- [ ] SMS follow-up automation
- [ ] Voice cloning for consistent brand voice
- [ ] A/B testing for campaign scripts
- [ ] Salesforce/HubSpot CRM integration
- [ ] Multi-language support beyond English/Urdu
- [ ] Advanced analytics with ML-based lead prediction

---

## Author

👨‍💻 **Mudassir Hussain**
- Email: hmudassir865@gmail.com
- Github: [GitHub](https://github.com/hmudassir865)
- Kaggle: [Kaggle](https://www.kaggle.com/hmudassir865)
- LinkedIn: [LinkedIn](https://www.linkedin.com/in/mudassir-hussain-877347207/)

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built as part of the NCAI Internship Project
- Groq for free-tier LLM inference
- Google for free Gemini API access
- SignalWire for developer-friendly telephony APIs
