from motor.motor_asyncio import AsyncIOMotorDatabase
from app.organization.repositories.base_repository import BaseRepository
from app.organization.models.department import DepartmentModel

class DepartmentRepository(BaseRepository[DepartmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "departments", DepartmentModel)
