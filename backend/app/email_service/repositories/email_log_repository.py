from app.email_service.repositories.base_repository import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.email_service.models.email_log import EmailLogModel

class EmailLogRepository(BaseRepository[EmailLogModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "email_logs", EmailLogModel)

