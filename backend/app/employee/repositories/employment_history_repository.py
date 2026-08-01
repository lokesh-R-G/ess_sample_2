from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employment_history import EmploymentHistoryModel

class EmploymentHistoryRepository(BaseRepository[EmploymentHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_employment_histories", EmploymentHistoryModel)
