from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee_probation import EmployeeProbationModel

class EmployeeProbationRepository(BaseRepository[EmployeeProbationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_probations", EmployeeProbationModel)
