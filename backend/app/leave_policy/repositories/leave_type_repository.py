from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_type import LeaveTypeModel

class LeaveTypeRepository(BaseRepository[LeaveTypeModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_types", LeaveTypeModel)
