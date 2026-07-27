from motor.motor_asyncio import AsyncIOMotorDatabase
from app.notification.repositories.base_repository import BaseRepository
from app.notification.models.notification_delivery_log import NotificationDeliveryLogModel

class NotificationDeliveryLogRepository(BaseRepository[NotificationDeliveryLogModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'notification_delivery_logs', NotificationDeliveryLogModel)
