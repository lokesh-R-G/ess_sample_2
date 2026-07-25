from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.salary_structure_version import SalaryStructureVersionModel

class SalaryStructureVersionRepository(BaseRepository[SalaryStructureVersionModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "salary_structure_versions", SalaryStructureVersionModel)
