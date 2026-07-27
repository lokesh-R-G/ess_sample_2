from motor.motor_asyncio import AsyncIOMotorDatabase
from app.salary.repositories.base_repository import BaseRepository
from app.salary.models.employee_salary_history import EmployeeSalaryHistoryModel

class EmployeeSalaryHistoryRepository(BaseRepository[EmployeeSalaryHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_salary_history", EmployeeSalaryHistoryModel)
