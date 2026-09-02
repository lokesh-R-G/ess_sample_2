from typing import List
from datetime import datetime, timezone
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_v2.models.dirty_queue import AttendanceDirtyQueueModel

class DirtyQueueService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db.attendance_dirty_queue

    def _utc_now(self):
        return datetime.now(timezone.utc)

    async def push(self, employee_id: str, employee_code: str, from_date: str, to_date: str, reason: str, trigger: str):
        """Push a new record to the dirty queue."""
        dirty_id = str(uuid.uuid4())
        model = AttendanceDirtyQueueModel(
            dirtyId=dirty_id,
            employeeId=employee_id,
            employeeCode=employee_code,
            fromDate=from_date,
            toDate=to_date,
            reason=reason,
            trigger=trigger,
            status="PENDING",
            createdAt=self._utc_now()
        )
        await self.collection.insert_one(model.dict())
        return dirty_id

    async def get_pending_records(self, limit: int = 100) -> List[AttendanceDirtyQueueModel]:
        """Fetch pending records to process."""
        cursor = self.collection.find({"status": "PENDING"}).sort("createdAt", 1).limit(limit)
        records = await cursor.to_list(length=limit)
        return [AttendanceDirtyQueueModel(**r) for r in records]

    async def mark_processing(self, dirty_id: str):
        await self.collection.update_one(
            {"dirtyId": dirty_id},
            {"$set": {"status": "PROCESSING"}}
        )

    async def mark_completed(self, dirty_id: str):
        await self.collection.update_one(
            {"dirtyId": dirty_id},
            {"$set": {"status": "COMPLETED", "processedAt": self._utc_now()}}
        )

    async def mark_failed(self, dirty_id: str, error: str):
        await self.collection.update_one(
            {"dirtyId": dirty_id},
            {"$set": {"status": "FAILED", "processedAt": self._utc_now(), "error": error}}
        )
