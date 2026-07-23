"""Seed admin user for production."""
import asyncio
from app.database import async_session
from app.models.user import User
from app.utils.auth import hash_password
from sqlalchemy import select


async def seed_admin():
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == "admin@ncai.com"))
        if result.scalar_one_or_none():
            print("Admin user already exists")
            return

        admin = User(
            email="admin@ncai.com",
            hashed_password=hash_password("Admin@123"),
            full_name="System Administrator",
            role="admin",
        )
        db.add(admin)
        await db.commit()
        print("Admin user created: admin@ncai.com / Admin@123")


if __name__ == "__main__":
    asyncio.run(seed_admin())
