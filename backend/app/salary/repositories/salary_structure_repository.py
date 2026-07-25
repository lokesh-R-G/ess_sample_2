from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.salary_structure import SalaryStructureModel

class SalaryStructureRepository(BaseRepository[SalaryStructureModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "salary_structures", SalaryStructureModel)
