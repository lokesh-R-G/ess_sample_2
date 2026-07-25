from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_history import LeaveHistoryModel

class LeaveHistoryRepository(BaseRepository[LeaveHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_history", LeaveHistoryModel)
