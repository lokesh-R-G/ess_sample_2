from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.payroll_run import PayrollRunModel

class PayrollRunRepository(BaseRepository[PayrollRunModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "payroll_runs", PayrollRunModel)
