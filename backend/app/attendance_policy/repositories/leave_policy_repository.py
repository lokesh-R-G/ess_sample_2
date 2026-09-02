from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.attendance_policy.models.leave_policy import LeavePolicy

class LeavePolicyRepository(BaseRepository[LeavePolicy]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_policies", LeavePolicy)
