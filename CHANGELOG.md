# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-11

### Added
- Multi-LLM provider support with automatic fallback (Gemini → Groq → Ollama → OpenAI → Anthropic)
- Real-time WebSocket dashboard with Recharts visualizations
- RAG knowledge base for insurance document context
- Lead scoring engine (Hot/Warm/Cool/Cold tiers)
- Local Whisper STT integration
- gTTS fallback for ElevenLabs TTS
- Asterisk SIP PBX integration option
- Celery background task processing
- Redis caching with in-memory fallback
- Rate limiting middleware
- Structured logging with structlog
- Sentry error tracking
- Prometheus metrics endpoint
- CORS and security middleware

### Changed
- Migrated from single-provider LLM to multi-provider service
- Upgraded React frontend from Streamlit to TypeScript SPA
- Replaced synchronous SQLAlchemy with async engine (asyncpg)
- Updated PostgreSQL to version 16 with pgvector

### Fixed
- Graceful degradation when Redis is unavailable
- LLM provider timeout and retry handling
- Audio response caching for concurrent access

## [1.0.0] - 2026-01-15

### Added
- Initial release with basic cold calling functionality
- FastAPI backend with SQLAlchemy ORM
- Streamlit dashboard
- Single-provider LLM integration (Groq)
- SignalWire telephony integration
- JWT authentication
- Lead and campaign management
