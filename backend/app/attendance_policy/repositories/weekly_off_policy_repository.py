from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.attendance_policy.models.weekly_off_policy import WeeklyOffPolicyModel

class WeeklyOffPolicyRepository(BaseRepository[WeeklyOffPolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "weekly_off_policies", WeeklyOffPolicyModel)
