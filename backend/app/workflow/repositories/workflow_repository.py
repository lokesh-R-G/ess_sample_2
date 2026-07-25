from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from bson import ObjectId

class WorkflowRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["workflows"]
        
    async def create(self, data: dict, session=None):
        data["createdAt"] = datetime.now(timezone.utc)
        data["updatedAt"] = data["createdAt"]
        res = await self.collection.insert_one(data, session=session)
        return str(res.inserted_id)
        
    async def update_status(self, wf_id: str, status: str, session=None):
        await self.collection.update_one(
            {"_id": ObjectId(wf_id)},
            {"$set": {"status": status, "updatedAt": datetime.now(timezone.utc)}},
            session=session
        )
