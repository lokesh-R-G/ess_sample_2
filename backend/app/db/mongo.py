from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..core.config import get_settings


settings = get_settings()
client = AsyncIOMotorClient(settings.mongo_uri) if settings.mongo_uri else None


def get_database() -> AsyncIOMotorDatabase:
    if client is None:
        raise RuntimeError("MONGODB_URI is not configured")
    return client[settings.mongo_db_name]


async def init_indexes() -> None:
    db = get_database()
    await db.users.create_index([("empId", 1)], unique=True)
    # Ensure raw log de-duplication by fingerprint and by empId+timestamp
    await db.attendance_logs.create_index([("fingerprint", 1)], unique=True)
    await db.attendance_logs.create_index([("empId", 1), ("timestamp", 1)], unique=True)
    await db.attendance.create_index([("empId", 1), ("date", 1)], unique=True)
    await db.attendance.create_index([("empId", 1), ("date", -1)])
