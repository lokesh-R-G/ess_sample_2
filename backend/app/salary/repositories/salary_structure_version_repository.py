from motor.motor_asyncio import AsyncIOMotorDatabase
from app.salary.repositories.base_repository import BaseRepository
from app.salary.models.salary_structure_version import SalaryStructureVersionModel

class SalaryStructureVersionRepository(BaseRepository[SalaryStructureVersionModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "salary_structure_versions", SalaryStructureVersionModel)
