from motor.motor_asyncio import AsyncIOMotorDatabase
from app.deduction.repositories.base_repository import BaseRepository
from app.deduction.models.deduction_history import DeductionHistoryModel

class DeductionHistoryRepository(BaseRepository[DeductionHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'deduction_history', DeductionHistoryModel)
