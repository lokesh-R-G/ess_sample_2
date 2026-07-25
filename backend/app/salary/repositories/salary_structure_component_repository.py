from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.salary_structure_component import SalaryStructureComponentModel

class SalaryStructureComponentRepository(BaseRepository[SalaryStructureComponentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "salary_structure_components", SalaryStructureComponentModel)
