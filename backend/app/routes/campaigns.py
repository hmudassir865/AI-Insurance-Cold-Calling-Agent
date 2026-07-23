import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.campaign import Campaign, CampaignStatus
from app.models.lead import Lead
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
)

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
):
    campaign = Campaign(
        name=campaign_data.name,
        script_template=campaign_data.script_template,
        greeting_message=campaign_data.greeting_message,
        closing_message=campaign_data.closing_message,
        status=CampaignStatus.draft,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    query = select(Campaign)

    if status:
        query = query.where(Campaign.status == CampaignStatus(status))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.order_by(Campaign.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    campaigns = result.scalars().all()

    return CampaignListResponse(total=total, campaigns=campaigns)


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: uuid.UUID,
    update_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(campaign, key, value)

    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    lead_count = await db.scalar(
        select(func.count())
        .select_from(Lead)
        .where(
            Lead.assigned_campaign_id == campaign_id,
            Lead.status == "pending",
        )
    )

    campaign.status = CampaignStatus.active
    campaign.total_leads = lead_count or 0
    await db.commit()
    await db.refresh(campaign)

    return {
        "message": f"Campaign '{campaign.name}' started with {lead_count} leads",
        "lead_count": lead_count,
    }


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.status = CampaignStatus.paused
    await db.commit()
    return {"message": f"Campaign '{campaign.name}' paused"}


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    await db.delete(campaign)
    await db.commit()
