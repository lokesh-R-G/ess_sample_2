from motor.motor_asyncio import AsyncIOMotorDatabase
from app.allowance.repositories.base_repository import BaseRepository
from app.allowance.models.employee_allowance import EmployeeAllowanceModel

class EmployeeAllowanceRepository(BaseRepository[EmployeeAllowanceModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'employee_allowances', EmployeeAllowanceModel)
