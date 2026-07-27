from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave.repositories.base_repository import BaseRepository
from app.leave.models.leave_adjustment import LeaveAdjustmentModel

class LeaveAdjustmentRepository(BaseRepository[LeaveAdjustmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_adjustments", LeaveAdjustmentModel)
