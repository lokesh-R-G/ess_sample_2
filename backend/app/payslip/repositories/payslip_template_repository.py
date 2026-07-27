from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payslip.repositories.base_repository import BaseRepository
from app.payslip.models.payslip_template import PayslipTemplateModel

class PayslipTemplateRepository(BaseRepository[PayslipTemplateModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'payslip_templates', PayslipTemplateModel)
