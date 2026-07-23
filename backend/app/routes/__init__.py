from app.routes.leads import router as leads_router
from app.routes.campaigns import router as campaigns_router
from app.routes.calls import router as calls_router
from app.routes.analytics import router as analytics_router
from app.routes.auth import router as auth_router
from app.routes.rag import router as rag_router

__all__ = ["leads_router", "campaigns_router", "calls_router", "analytics_router", "auth_router", "rag_router"]
