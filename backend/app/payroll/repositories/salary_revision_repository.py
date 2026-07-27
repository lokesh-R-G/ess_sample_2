from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll.repositories.base_repository import BaseRepository
from app.payroll.models.salary_revision import SalaryRevisionModel

class SalaryRevisionRepository(BaseRepository[SalaryRevisionModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'salary_revisions', SalaryRevisionModel)
