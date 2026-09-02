from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.attendance_v2.models.correction_log import CorrectionLogModel
from datetime import datetime, timezone
import uuid

class CorrectionLogRepository(BaseRepository[CorrectionLogModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "correction_logs", CorrectionLogModel)

    async def create_correction(self, data: dict, created_by: str = None) -> CorrectionLogModel:
        now = datetime.now(timezone.utc)
        data["createdAt"] = now
        data["createdBy"] = created_by
        data["correctionCode"] = f"CORR_{uuid.uuid4().hex[:8].upper()}"
        
        # We find the max correction version for this entityCode to increment
        query = {"entityCode": data["entityCode"], "deletedAt": None}
        highest = await self.collection.find_one(query, sort=[("correctionVersion", -1)])
        
        if highest and "correctionVersion" in highest:
            data["correctionVersion"] = highest["correctionVersion"] + 1
        else:
            data["correctionVersion"] = 1
            
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return self.model_class(**data)
