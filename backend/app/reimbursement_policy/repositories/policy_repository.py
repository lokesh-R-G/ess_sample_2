from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from app.reimbursement_policy.models.policy_version import PolicyVersionModel

class PolicyRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.collection = db[collection_name]
        
    async def get_active_policy(self, target_date: datetime):
        doc = await self.collection.find_one({
            "effectiveFrom": {"$lte": target_date},
            "$or": [{"effectiveUntil": {"$gt": target_date}}, {"effectiveUntil": None}],
            "status": "Active"
        })
        return PolicyVersionModel(**doc) if doc else None
        
    async def insert_new_version(self, data: dict, session=None):
        result = await self.collection.insert_one(data, session=session)
        return str(result.inserted_id)
        
    async def end_date_current_version(self, target_date: datetime, session=None):
        await self.collection.update_many(
            {"effectiveUntil": None, "status": "Active"},
            {"$set": {"effectiveUntil": target_date, "status": "Archived"}},
            session=session
        )
