from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from app.database import get_db
from app.models.lead import Lead, LeadStatus
from app.models.call_log import CallLog
from app.models.campaign import Campaign, CampaignStatus
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"], dependencies=[Depends(get_current_user)])


@router.get("/dashboard")
async def dashboard(
    days: int = Query(7, ge=1, le=90),
    campaign_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.sql import extract

    base_filter = CallLog.created_at >= func.now() - func.make_interval(0, 0, 0, days)

    total_calls = await db.scalar(
        select(func.count()).select_from(CallLog).where(base_filter)
    )

    total_calls = total_calls or 0

    lead_count = await db.scalar(
        select(func.count()).select_from(Lead)
    )

    conversion_result = await db.execute(
        select(
            func.count().filter(Lead.status == LeadStatus.interested).label("interested"),
            func.count().filter(Lead.status == LeadStatus.not_interested).label("not_interested"),
            func.count().filter(Lead.status == LeadStatus.callback).label("callback"),
            func.count().filter(Lead.status == LeadStatus.pending).label("pending"),
        ).select_from(Lead)
    )
    row = conversion_result.one()

    conversion_rate = (
        (row.interested / total_calls * 100) if total_calls > 0 else 0
    )

    avg_duration = await db.scalar(
        select(func.avg(CallLog.duration_seconds)).where(
            base_filter, CallLog.duration_seconds.isnot(None)
        )
    )

    avg_sentiment = await db.scalar(
        select(func.avg(CallLog.sentiment_score)).where(
            base_filter, CallLog.sentiment_score.isnot(None)
        )
    )

    daily_stats = await db.execute(
        select(
            func.date(CallLog.created_at).label("date"),
            func.count().label("calls"),
            func.avg(CallLog.duration_seconds).label("avg_duration"),
            func.avg(CallLog.sentiment_score).label("avg_sentiment"),
        )
        .where(base_filter)
        .group_by(func.date(CallLog.created_at))
        .order_by(func.date(CallLog.created_at))
    )

    daily_data = [
        {
            "date": str(row.date),
            "calls": row.calls,
            "avg_duration": float(row.avg_duration) if row.avg_duration else 0,
            "avg_sentiment": float(row.avg_sentiment) if row.avg_sentiment else 0,
        }
        for row in daily_stats
    ]

    return {
        "total_calls": total_calls,
        "total_leads": lead_count or 0,
        "conversion_rate": round(conversion_rate, 2),
        "avg_call_duration_seconds": round(float(avg_duration), 1) if avg_duration else 0,
        "avg_sentiment_score": round(float(avg_sentiment), 2) if avg_sentiment else 0,
        "lead_breakdown": {
            "interested": row.interested,
            "not_interested": row.not_interested,
            "callback": row.callback,
            "pending": row.pending,
        },
        "daily_stats": daily_data,
    }


@router.get("/campaigns")
async def campaign_analytics(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            Campaign.id,
            Campaign.name,
            Campaign.status,
            Campaign.total_leads,
            Campaign.processed_leads,
            func.count(CallLog.id).label("total_calls"),
            func.avg(CallLog.sentiment_score).label("avg_sentiment"),
        )
        .outerjoin(CallLog, CallLog.campaign_id == Campaign.id)
        .group_by(Campaign.id, Campaign.name, Campaign.status, Campaign.total_leads, Campaign.processed_leads)
    )

    campaigns = []
    for row in result:
        conversion = (
            (row.processed_leads / row.total_leads * 100) if row.total_leads > 0 else 0
        )
        campaigns.append({
            "id": str(row.id),
            "name": row.name,
            "status": row.status.value if hasattr(row.status, "value") else row.status,
            "total_leads": row.total_leads,
            "processed_leads": row.processed_leads,
            "total_calls": row.total_calls,
            "avg_sentiment": round(float(row.avg_sentiment), 2) if row.avg_sentiment else 0,
            "conversion_rate": round(conversion, 2),
        })

    return {"campaigns": campaigns}
