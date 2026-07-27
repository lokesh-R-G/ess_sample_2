from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_policy.repositories.base_repository import BaseRepository
from app.attendance_policy.models.attendance_policy_history import AttendancePolicyHistoryModel

class AttendancePolicyHistoryRepository(BaseRepository[AttendancePolicyHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_policy_history", AttendancePolicyHistoryModel)
