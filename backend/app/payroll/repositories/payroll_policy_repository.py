from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll.repositories.base_repository import BaseRepository
from app.payroll.models.payroll_policy import PayrollPolicyModel

class PayrollPolicyRepository(BaseRepository[PayrollPolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'payroll_policies', PayrollPolicyModel)
