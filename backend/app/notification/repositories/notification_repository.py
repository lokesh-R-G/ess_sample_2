from motor.motor_asyncio import AsyncIOMotorDatabase
from app.notification.repositories.base_repository import BaseRepository
from app.notification.models.notification import NotificationModel

class NotificationRepository(BaseRepository[NotificationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'notifications', NotificationModel)
