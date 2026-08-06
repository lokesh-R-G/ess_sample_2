from datetime import datetime, timezone, date
from typing import List, Optional
from pydantic import BaseModel, Field

class DirtyQueueModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    fromDate: date
    toDate: date
    reason: str
    status: str = "PENDING"
    createdAt: Optional[datetime] = None
    processedAt: Optional[datetime] = None

class DirtyQueueService:
    def __init__(self, db):
        self.db = db
        self.collection = db.attendance_dirty_queue

    def _utc_now(self):
        return datetime.now(timezone.utc)

    async def mark_dirty(self, employee_id: str, from_date: date, to_date: date, reason: str):
        doc = {
            "employeeId": employee_id,
            "fromDate": datetime.combine(from_date, datetime.min.time()),
            "toDate": datetime.combine(to_date, datetime.max.time()),
            "reason": reason,
            "status": "PENDING",
            "createdAt": self._utc_now()
        }
        await self.collection.insert_one(doc)

    async def get_pending_batch(self, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"status": "PENDING"}).sort([("createdAt", 1)]).limit(limit)
        return await cursor.to_list(length=limit)

    async def mark_processed(self, queue_id: str):
        from bson import ObjectId
        await self.collection.update_one(
            {"_id": ObjectId(queue_id) if isinstance(queue_id, str) else queue_id},
            {"$set": {"status": "PROCESSED", "processedAt": self._utc_now()}}
        )
