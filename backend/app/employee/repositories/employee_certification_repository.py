from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee_certification import EmployeeCertificationModel

class EmployeeCertificationRepository(BaseRepository[EmployeeCertificationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'employee_certifications', EmployeeCertificationModel)
