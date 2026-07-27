from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_policy.repositories.base_repository import BaseRepository
from app.attendance_policy.models.shift_attendance_policy import ShiftAttendancePolicyModel

class ShiftAttendancePolicyRepository(BaseRepository[ShiftAttendancePolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "shift_attendance_policys", ShiftAttendancePolicyModel)
