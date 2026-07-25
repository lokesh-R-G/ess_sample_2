from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee_salary_component import EmployeeSalaryComponentModel

class EmployeeSalaryComponentRepository(BaseRepository[EmployeeSalaryComponentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_salary_components", EmployeeSalaryComponentModel)
