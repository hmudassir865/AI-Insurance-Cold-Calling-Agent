import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Enum as SAEnum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base

import enum


class LeadStatus(str, enum.Enum):
    pending = "pending"
    called = "called"
    interested = "interested"
    not_interested = "not_interested"
    callback = "callback"
    busy = "busy"
    wrong_number = "wrong_number"
    dnc = "dnc"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    language: Mapped[str] = mapped_column(
        String(10), nullable=False, default="urdu"
    )
    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(LeadStatus, name="lead_status"),
        default=LeadStatus.pending,
        index=True,
    )
    extra_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    assigned_campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
