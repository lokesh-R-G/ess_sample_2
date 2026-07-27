from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_policy.repositories.base_repository import BaseRepository
from app.attendance_policy.models.late_policy import LatePolicyModel

class LatePolicyRepository(BaseRepository[LatePolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "late_policys", LatePolicyModel)
