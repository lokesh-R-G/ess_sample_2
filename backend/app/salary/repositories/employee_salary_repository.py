from motor.motor_asyncio import AsyncIOMotorDatabase
from app.salary.repositories.base_repository import BaseRepository
from app.salary.models.employee_salary import EmployeeSalaryModel

class EmployeeSalaryRepository(BaseRepository[EmployeeSalaryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_salarys", EmployeeSalaryModel)
