from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee_bank import EmployeeBankModel

class EmployeeBankRepository(BaseRepository[EmployeeBankModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_banks", EmployeeBankModel)
