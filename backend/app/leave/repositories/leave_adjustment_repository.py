from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_adjustment import LeaveAdjustmentModel

class LeaveAdjustmentRepository(BaseRepository[LeaveAdjustmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_adjustments", LeaveAdjustmentModel)
