from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll.repositories.base_repository import BaseRepository
from app.payroll.models.payroll_cycle import PayrollCycleModel

class PayrollCycleRepository(BaseRepository[PayrollCycleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'payroll_cycles', PayrollCycleModel)
