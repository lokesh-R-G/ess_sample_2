from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.salary_policy import SalaryPolicyModel

class SalaryPolicyRepository(BaseRepository[SalaryPolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "salary_policys", SalaryPolicyModel)
