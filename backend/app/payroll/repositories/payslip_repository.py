from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.payslip import PayslipModel

class PayslipRepository(BaseRepository[PayslipModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "payslips", PayslipModel)
