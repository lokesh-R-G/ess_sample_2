from motor.motor_asyncio import AsyncIOMotorDatabase
from app.ctc.repositories.base_repository import BaseRepository
from app.ctc.models.employee_ctc import EmployeeCtcModel

class EmployeeCtcRepository(BaseRepository[EmployeeCtcModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'employee_ctc', EmployeeCtcModel)
