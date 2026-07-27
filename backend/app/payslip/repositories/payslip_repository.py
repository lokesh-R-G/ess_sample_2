from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payslip.repositories.base_repository import BaseRepository
from app.payslip.models.payslip import PayslipModel

class PayslipRepository(BaseRepository[PayslipModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'payslips', PayslipModel)
