from motor.motor_asyncio import AsyncIOMotorDatabase
from app.allowance.repositories.base_repository import BaseRepository
from app.allowance.models.allowance_history import AllowanceHistoryModel

class AllowanceHistoryRepository(BaseRepository[AllowanceHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'allowance_history', AllowanceHistoryModel)
