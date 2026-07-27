from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll.repositories.base_repository import BaseRepository
from app.payroll.models.salary_structure import SalaryStructureModel

class SalaryStructureRepository(BaseRepository[SalaryStructureModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'salary_structures', SalaryStructureModel)
