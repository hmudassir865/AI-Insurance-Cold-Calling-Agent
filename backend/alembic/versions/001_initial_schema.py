"""Initial schema with users, leads, campaigns, call_logs, knowledge_base."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), server_default="agent"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False, index=True),
        sa.Column("language", sa.String(10), nullable=False, server_default="urdu"),
        sa.Column("status", sa.String(20), nullable=False, index=True, server_default="pending"),
        sa.Column("extra_data", postgresql.JSONB, nullable=True),
        sa.Column("assigned_campaign_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("script_template", sa.Text, nullable=False),
        sa.Column("greeting_message", sa.Text, nullable=True),
        sa.Column("closing_message", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("total_leads", sa.Integer, server_default="0"),
        sa.Column("processed_leads", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "call_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id"), nullable=False, index=True),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="initiated"),
        sa.Column("transcript", postgresql.JSONB, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("sentiment_score", sa.Float, nullable=True),
        sa.Column("lead_status", sa.String(20), nullable=True),
        sa.Column("recording_path", sa.String(500), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("extra_data", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "insurance_knowledge_base",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("embedding", postgresql.ARRAY(sa.Float), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("insurance_knowledge_base")
    op.drop_table("call_logs")
    op.drop_table("campaigns")
    op.drop_table("leads")
    op.drop_table("users")
