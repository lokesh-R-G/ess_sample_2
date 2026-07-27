from motor.motor_asyncio import AsyncIOMotorDatabase
from app.notification.repositories.base_repository import BaseRepository
from app.notification.models.notification_template import NotificationTemplateModel

class NotificationTemplateRepository(BaseRepository[NotificationTemplateModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'notification_templates', NotificationTemplateModel)
