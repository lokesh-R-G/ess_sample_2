from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_v2.repositories.base_repository import BaseRepository
from app.attendance_v2.models.attendance_engine_health import AttendanceEngineHealthModel

class AttendanceEngineHealthRepository(BaseRepository[AttendanceEngineHealthModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_engine_health", AttendanceEngineHealthModel)
