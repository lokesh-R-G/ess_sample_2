from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.attendance import AttendanceModel

class AttendanceRepository(BaseRepository[AttendanceModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendances", AttendanceModel)
