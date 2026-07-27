from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll.repositories.base_repository import BaseRepository
from app.payroll.models.salary_component_group import SalaryComponentGroupModel

class SalaryComponentGroupRepository(BaseRepository[SalaryComponentGroupModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'salary_component_groups', SalaryComponentGroupModel)
