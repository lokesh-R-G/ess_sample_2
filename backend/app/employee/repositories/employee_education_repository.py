from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee_education import EmployeeEducationModel

class EmployeeEducationRepository(BaseRepository[EmployeeEducationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_educations", EmployeeEducationModel)
