from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employment_history import EmploymentHistoryModel

class EmploymentHistoryRepository(BaseRepository[EmploymentHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employment_history", EmploymentHistoryModel)
