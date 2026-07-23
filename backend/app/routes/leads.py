import uuid
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.lead import Lead, LeadStatus
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadListResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/leads", tags=["Leads"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(lead_data: LeadCreate, db: AsyncSession = Depends(get_db)):
    lead = Lead(
        name=lead_data.name,
        phone=lead_data.phone,
        language=lead_data.language,
        extra_data=lead_data.extra_data,
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.post("/bulk-upload", status_code=201)
async def bulk_upload_leads(
    file: UploadFile = File(...),
    campaign_id: str = Form(None),
    campaign_id_q: str | None = Query(None, alias="campaign_id"),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted")

    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    resolved_campaign_id = campaign_id or campaign_id_q

    leads = []
    errors = []
    row_number = 0

    for row in reader:
        row_number += 1
        name = row.get("name", row.get("Name", "")).strip()
        phone = row.get("phone", row.get("Phone", row.get("number", row.get("Number", "")))).strip()

        if not name or not phone:
            errors.append(f"Row {row_number}: missing name or phone")
            continue

        lead = Lead(
            name=name,
            phone=phone,
            language=row.get("language", row.get("Language", "urdu")).strip().lower(),
            status=LeadStatus.pending,
            assigned_campaign_id=uuid.UUID(resolved_campaign_id) if resolved_campaign_id else None,
            extra_data=row,
        )
        leads.append(lead)

    db.add_all(leads)
    await db.commit()

    return {
        "total_uploaded": len(leads),
        "errors": errors,
        "campaign_id": resolved_campaign_id,
    }


@router.get("", response_model=LeadListResponse)
async def list_leads(
    status: str | None = Query(None),
    campaign_id: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    query = select(Lead)

    if status:
        query = query.where(Lead.status == LeadStatus(status))
    if campaign_id:
        query = query.where(Lead.assigned_campaign_id == uuid.UUID(campaign_id))
    if search:
        query = query.where(
            Lead.name.ilike(f"%{search}%") | Lead.phone.ilike(f"%{search}%")
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.order_by(Lead.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    leads = result.scalars().all()

    return LeadListResponse(total=total, leads=leads)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: uuid.UUID,
    update_data: LeadUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(lead, key, value)

    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    await db.delete(lead)
    await db.commit()
