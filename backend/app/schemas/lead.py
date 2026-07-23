import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class LeadCreate(BaseModel):
    name: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=20)
    language: str = Field(default="urdu", max_length=10)
    extra_data: dict | None = None


class LeadUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    language: str | None = None
    status: str | None = None
    extra_data: dict | None = None


class LeadResponse(BaseModel):
    id: uuid.UUID
    name: str
    phone: str
    language: str
    status: str
    extra_data: dict | None
    assigned_campaign_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    total: int
    leads: list[LeadResponse]
