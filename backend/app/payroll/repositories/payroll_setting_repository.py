from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll.repositories.base_repository import BaseRepository
from app.payroll.models.payroll_setting import PayrollSettingModel
from app.domain_models import PayrollSettings
from datetime import datetime
from typing import Optional

class PayrollSettingRepository(BaseRepository[PayrollSettingModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'payroll_settings', PayrollSettingModel)

    async def get_active_setting(self, target_date: datetime) -> Optional[PayrollSettings]:
        """Fetch the active global payroll setting for the given date."""
        query = {
            "effectiveFrom": {"$lte": target_date},
            "$or": [
                {"effectiveTo": None},
                {"effectiveTo": {"$gt": target_date}},
                {"effectiveUntil": None},  # handle potential variations
                {"effectiveUntil": {"$gt": target_date}}
            ],
            "status": "Active"
        }
        # Sort by effectiveFrom descending to get the most recent active setting
        doc = await self.collection.find_one(query, sort=[("effectiveFrom", -1)])
        if doc:
            return PayrollSettings(**{**doc, "_id": str(doc["_id"])})
        return None
