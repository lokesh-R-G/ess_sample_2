from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_closing import LeaveClosingModel

class LeaveClosingRepository(BaseRepository[LeaveClosingModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_closings", LeaveClosingModel)
