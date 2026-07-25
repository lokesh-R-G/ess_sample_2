from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.salary_rule import SalaryRuleModel

class SalaryRuleRepository(BaseRepository[SalaryRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "salary_rules", SalaryRuleModel)
