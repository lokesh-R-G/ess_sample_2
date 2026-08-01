from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee_bank import EmployeeBankModel

class EmployeeBankRepository(BaseRepository[EmployeeBankModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_bank_accounts", EmployeeBankModel)
