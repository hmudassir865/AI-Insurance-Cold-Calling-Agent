import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    name: str = Field(..., max_length=255)
    script_template: str
    greeting_message: str | None = None
    closing_message: str | None = None


class CampaignUpdate(BaseModel):
    name: str | None = None
    script_template: str | None = None
    greeting_message: str | None = None
    closing_message: str | None = None
    status: str | None = None


class CampaignResponse(BaseModel):
    id: uuid.UUID
    name: str
    script_template: str
    greeting_message: str | None
    closing_message: str | None
    status: str
    total_leads: int
    processed_leads: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CampaignListResponse(BaseModel):
    total: int
    campaigns: list[CampaignResponse]
