import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Health Insurance Cold Calling Agent"
    DEBUG: bool = False
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/insurance_cold_calling"
    )

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    LLM_FALLBACK_ENABLED: bool = os.getenv("LLM_FALLBACK_ENABLED", "true").lower() == "true"

    SIGNALWIRE_SPACE: str = os.getenv("SIGNALWIRE_SPACE", "")
    SIGNALWIRE_PROJECT_ID: str = os.getenv("SIGNALWIRE_PROJECT_ID", "")
    SIGNALWIRE_AUTH_TOKEN: str = os.getenv("SIGNALWIRE_AUTH_TOKEN", "")
    SIGNALWIRE_PHONE_NUMBER: str = os.getenv("SIGNALWIRE_PHONE_NUMBER", "")
    SIGNALWIRE_WEBHOOK_BASE_URL: str = os.getenv("SIGNALWIRE_WEBHOOK_BASE_URL", "")

    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")

    RAG_EMBEDDING_MODEL: str = "models/embedding-001"
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 50
    MAX_CALL_DURATION_SECONDS: int = 600
    MAX_RESPONSE_TIMEOUT_SECONDS: int = 10

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))

    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    MAX_CONCURRENT_CALLS: int = int(os.getenv("MAX_CONCURRENT_CALLS", "10"))

    CALL_RECORDING_ENABLED: bool = os.getenv("CALL_RECORDING_ENABLED", "true").lower() == "true"
    CALL_MAX_RETRIES: int = int(os.getenv("CALL_MAX_RETRIES", "3"))
    CALL_RETRY_DELAY_MINUTES: int = int(os.getenv("CALL_RETRY_DELAY_MINUTES", "30"))

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
