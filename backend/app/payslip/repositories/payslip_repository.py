from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone
from app.payslip.models.payslip_model import PayslipModel

class PayslipRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["payslips"]
        self.version_collection = db["payslip_versions"]
        
    async def create(self, data: dict, session=None):
        now = datetime.now(timezone.utc)
        data["createdAt"] = now
        data["updatedAt"] = now
        result = await self.collection.insert_one(data, session=session)
        
        # Also store in version history
        data["payslipId"] = str(result.inserted_id)
        data.pop("_id", None)
        await self.version_collection.insert_one(data, session=session)
        
        return str(result.inserted_id)
        
    async def update_status(self, payslip_id: str, new_status: str, session=None):
        await self.collection.update_one(
            {"_id": ObjectId(payslip_id)},
            {"$set": {"status": new_status, "updatedAt": datetime.now(timezone.utc)}},
            session=session
        )
