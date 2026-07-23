import uuid
from datetime import datetime
from pydantic import BaseModel


class CallLogResponse(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    campaign_id: uuid.UUID | None
    duration_seconds: int | None
    status: str
    transcript: list | None
    summary: str | None
    sentiment_score: float | None
    lead_status: str | None
    recording_path: str | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CallLogListResponse(BaseModel):
    total: int
    call_logs: list[CallLogResponse]
