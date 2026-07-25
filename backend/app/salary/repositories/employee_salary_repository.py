from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee_salary import EmployeeSalaryModel

class EmployeeSalaryRepository(BaseRepository[EmployeeSalaryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_salarys", EmployeeSalaryModel)
