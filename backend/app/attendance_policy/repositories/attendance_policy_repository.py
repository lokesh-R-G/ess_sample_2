from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_policy.repositories.base_repository import BaseRepository
from app.attendance_policy.models.attendance_policy import AttendancePolicyModel

class AttendancePolicyRepository(BaseRepository[AttendancePolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_policys", AttendancePolicyModel)
