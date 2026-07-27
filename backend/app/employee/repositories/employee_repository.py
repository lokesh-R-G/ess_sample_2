from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee import EmployeeModel

class EmployeeRepository(BaseRepository[EmployeeModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employees", EmployeeModel)
