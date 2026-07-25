from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee_family import EmployeeFamilyModel

class EmployeeFamilyRepository(BaseRepository[EmployeeFamilyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_familys", EmployeeFamilyModel)
