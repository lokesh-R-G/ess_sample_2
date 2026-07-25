from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee_reporting import EmployeeReportingModel

class EmployeeReportingRepository(BaseRepository[EmployeeReportingModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_reportings", EmployeeReportingModel)
