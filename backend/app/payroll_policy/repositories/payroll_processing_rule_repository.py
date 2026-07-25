from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.payroll_processing_rule import PayrollProcessingRuleModel

class PayrollProcessingRuleRepository(BaseRepository[PayrollProcessingRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "payroll_processing_rules", PayrollProcessingRuleModel)
