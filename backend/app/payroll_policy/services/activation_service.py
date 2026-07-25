from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from ..repositories.policy_repository import PolicyRepository

class PolicyActivationService:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.repo = PolicyRepository(db, collection_name)
        
    async def activate_new_policy(self, config_data: dict, reason: str, user_id: str):
        now = datetime.now(timezone.utc)
        # Lock old version, insert new immutable version
        await self.repo.end_date_current_version(now)
        
        new_policy = {
            "version": int(now.timestamp()),
            "effectiveFrom": now,
            "effectiveUntil": None,
            "status": "Active",
            "createdBy": user_id,
            "reason": reason,
            "configData": config_data
        }
        return await self.repo.insert_new_version(new_policy)
