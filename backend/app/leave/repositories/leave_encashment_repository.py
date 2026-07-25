from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_encashment import LeaveEncashmentModel

class LeaveEncashmentRepository(BaseRepository[LeaveEncashmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_encashments", LeaveEncashmentModel)
