import uvicorn
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.models import User  # noqa: F401 - ensure models are imported
from app.routes import leads_router, campaigns_router, calls_router, analytics_router, auth_router, rag_router
from app.middleware.logging_mw import RequestLoggingMiddleware
from app.middleware.error_handler import ErrorHandlingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.logging_setup import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    import aiohttp
    if not hasattr(aiohttp, "ClientConnectorDNSError"):
        aiohttp.ClientConnectorDNSError = aiohttp.ClientConnectorError

    setup_logging(settings.ENVIRONMENT)
    await init_db()
    if settings.SENTRY_DSN:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        )
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Middleware order: outermost first
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=settings.RATE_LIMIT_PER_MINUTE)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https://.*\.ngrok-free\.(app|dev)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth_router)
app.include_router(leads_router)
app.include_router(campaigns_router)
app.include_router(calls_router)
app.include_router(analytics_router)
app.include_router(rag_router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
    }


@app.get("/api/health/ready")
async def readiness_check():
    """Kubernetes-style readiness probe."""
    from app.database import async_session
    from sqlalchemy import text

    try:
        async with async_session() as db:
            await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "not ready", "detail": str(e)})


@app.get("/api/health/live")
async def liveness_check():
    """Kubernetes-style liveness probe."""
    return {"status": "alive"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
