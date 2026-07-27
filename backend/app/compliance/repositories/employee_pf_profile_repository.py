from motor.motor_asyncio import AsyncIOMotorDatabase
from app.compliance.repositories.base_repository import BaseRepository
from app.compliance.models.employee_pf_profile import EmployeePfProfileModel

class EmployeePfProfileRepository(BaseRepository[EmployeePfProfileModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'employee_pf_profiles', EmployeePfProfileModel)
