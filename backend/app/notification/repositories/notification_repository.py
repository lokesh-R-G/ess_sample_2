from motor.motor_asyncio import AsyncIOMotorDatabase
from app.notification.repositories.base_repository import BaseRepository
from app.notification.models.notification import NotificationModel

class NotificationRepository(BaseRepository[NotificationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'notifications', NotificationModel)

    async def setup_indexes(self):
        await self.collection.create_index([("recipientEmployeeId", 1), ("createdAt", -1)])
        await self.collection.create_index([("recipientEmployeeId", 1), ("isRead", 1)])

    async def get_by_recipient(self, recipient_employee_id: str, limit: int = 20, skip: int = 0):
        cursor = self.collection.find({"recipientEmployeeId": recipient_employee_id}).sort("createdAt", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self.model_class(**self._prepare_doc(doc)) for doc in docs]

    async def count_unread(self, recipient_employee_id: str) -> int:
        return await self.collection.count_documents({"recipientEmployeeId": recipient_employee_id, "isRead": False})

    async def mark_read(self, notification_id: str, recipient_employee_id: str) -> bool:
        from bson import ObjectId
        from datetime import datetime, timezone
        if not ObjectId.is_valid(notification_id):
            return False
        result = await self.collection.update_one(
            {"_id": ObjectId(notification_id), "recipientEmployeeId": recipient_employee_id},
            {"$set": {"isRead": True, "readAt": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0

    async def mark_all_read(self, recipient_employee_id: str) -> int:
        from datetime import datetime, timezone
        result = await self.collection.update_many(
            {"recipientEmployeeId": recipient_employee_id, "isRead": False},
            {"$set": {"isRead": True, "readAt": datetime.now(timezone.utc)}}
        )
        return result.modified_count
