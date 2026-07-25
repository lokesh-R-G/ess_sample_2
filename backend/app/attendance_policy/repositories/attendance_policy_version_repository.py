from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.attendance_policy_version import AttendancePolicyVersionModel

class AttendancePolicyVersionRepository(BaseRepository[AttendancePolicyVersionModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_policy_versions", AttendancePolicyVersionModel)
