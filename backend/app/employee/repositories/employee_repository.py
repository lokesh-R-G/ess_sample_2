from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee import EmployeeModel

class EmployeeRepository(BaseRepository[EmployeeModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employees", EmployeeModel)
