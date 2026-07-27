from motor.motor_asyncio import AsyncIOMotorDatabase
from app.compliance.repositories.base_repository import BaseRepository
from app.compliance.models.employee_esi_profile import EmployeeEsiProfileModel

class EmployeeEsiProfileRepository(BaseRepository[EmployeeEsiProfileModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'employee_esi_profiles', EmployeeEsiProfileModel)
