from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee_government_id import EmployeeGovernmentIdModel

from motor.motor_asyncio import AsyncIOMotorDatabase

class EmployeeGovernmentIdRepository(BaseRepository[EmployeeGovernmentIdModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_government_ids", EmployeeGovernmentIdModel)
