from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.department import DepartmentModel

class DepartmentRepository(BaseRepository[DepartmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "departments", DepartmentModel)
