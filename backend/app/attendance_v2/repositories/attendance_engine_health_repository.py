from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.attendance_engine_health import AttendanceEngineHealthModel

class AttendanceEngineHealthRepository(BaseRepository[AttendanceEngineHealthModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_engine_health", AttendanceEngineHealthModel)
