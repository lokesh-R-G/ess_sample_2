from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll.repositories.base_repository import BaseRepository
from app.payroll.models.employee_salary_structure import EmployeeSalaryStructureModel

class EmployeeSalaryStructureRepository(BaseRepository[EmployeeSalaryStructureModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'employee_salary_structures', EmployeeSalaryStructureModel)
