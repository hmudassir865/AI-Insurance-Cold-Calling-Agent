from celery import Celery
from app.config import settings

celery_app = Celery(
    "insurance_cold_calling",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Karachi",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    worker_max_tasks_per_child=200,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_call_task(self, lead_id: str, campaign_id: str | None = None):
    """Async call processing task with retries."""
    try:
        from app.services.conversation_service import ConversationService
        import asyncio

        service = ConversationService()
        # Actual call processing logic here
        return {"status": "completed", "lead_id": lead_id}
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task
def cleanup_old_records(days: int = 90):
    """Periodic cleanup of old call logs and recordings."""
    import asyncio
    from app.database import async_session
    from app.models.call_log import CallLog
    from sqlalchemy import delete

    async def _cleanup():
        async with async_session() as db:
            from sqlalchemy.sql import func
            cutoff = func.now() - func.make_interval(0, 0, 0, days)
            await db.execute(
                delete(CallLog).where(CallLog.created_at < cutoff)
            )
            await db.commit()

    asyncio.run(_cleanup())
