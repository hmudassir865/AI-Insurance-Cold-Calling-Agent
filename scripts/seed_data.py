"""
Seed script to populate initial test data.

Usage: python scripts/seed_data.py
"""

import asyncio
import uuid
import sys
from datetime import datetime

import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import async_session, init_db
from app.models.lead import Lead, LeadStatus
from app.models.campaign import Campaign, CampaignStatus
from app.models.call_log import CallLog


SAMPLE_LEADS = [
    {"name": "Alina Yuk", "phone": "+12012030907", "language": "english"},
    {"name": "Hassan Hazazi", "phone": "+12012032058", "language": "english"},
    {"name": "Wasilia Konlakis", "phone": "+12012030920", "language": "english"},
    {"name": "William Torres", "phone": "+12012039500", "language": "english"},
    {"name": "Sandra Vizcaino", "phone": "+12012042247", "language": "english"},
    {"name": "Sonya Perez", "phone": "+12012042812", "language": "english"},
    {"name": "Jamie Duva", "phone": "+12012042866", "language": "english"},
    {"name": "George Schultz", "phone": "+12012042880", "language": "english"},
    {"name": "Monisha Williams", "phone": "+12012042897", "language": "english"},
    {"name": "Sarah Lopez", "phone": "+12012046049", "language": "english"},
]

SAMPLE_SCRIPT = """Hello! I'm calling from NCAI Insurance regarding our health insurance plans.

We offer comprehensive coverage from basic hospitalization to full family plans.
Plans start from as low as $50/month.

Would you like me to tell you more about our plans?"""


async def seed():
    await init_db()
    async with async_session() as db:
        campaign = Campaign(
            name="Health Insurance Q1 Outreach",
            script_template=SAMPLE_SCRIPT,
            greeting_message="Hello! I'm calling from NCAI Insurance about health insurance plans.",
            closing_message="Thank you for your time! Have a great day.",
            status=CampaignStatus.draft,
            total_leads=len(SAMPLE_LEADS),
        )
        db.add(campaign)
        await db.flush()

        for lead_data in SAMPLE_LEADS:
            lead = Lead(
                name=lead_data["name"],
                phone=lead_data["phone"],
                language=lead_data["language"],
                status=LeadStatus.pending,
                assigned_campaign_id=campaign.id,
            )
            db.add(lead)

        await db.commit()
        print(f"Seeded {len(SAMPLE_LEADS)} leads and 1 campaign successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
