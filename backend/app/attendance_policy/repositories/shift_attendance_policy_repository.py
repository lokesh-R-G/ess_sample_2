from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.shift_attendance_policy import ShiftAttendancePolicyModel

class ShiftAttendancePolicyRepository(BaseRepository[ShiftAttendancePolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "shift_attendance_policys", ShiftAttendancePolicyModel)
