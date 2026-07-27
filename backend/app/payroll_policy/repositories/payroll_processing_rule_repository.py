from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll_policy.repositories.base_repository import BaseRepository
from app.payroll_policy.models.payroll_processing_rule import PayrollProcessingRuleModel

class PayrollProcessingRuleRepository(BaseRepository[PayrollProcessingRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "payroll_processing_rules", PayrollProcessingRuleModel)
