from motor.motor_asyncio import AsyncIOMotorDatabase
from app.salary.repositories.base_repository import BaseRepository
from app.salary.models.employee_salary_component import EmployeeSalaryComponentModel

class EmployeeSalaryComponentRepository(BaseRepository[EmployeeSalaryComponentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_salary_components", EmployeeSalaryComponentModel)
