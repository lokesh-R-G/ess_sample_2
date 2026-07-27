from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave.repositories.base_repository import BaseRepository
from app.leave.models.leave_type import LeaveTypeModel

class LeaveTypeRepository(BaseRepository[LeaveTypeModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'leave_types', LeaveTypeModel)
