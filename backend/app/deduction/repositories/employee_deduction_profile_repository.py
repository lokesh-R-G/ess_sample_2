from motor.motor_asyncio import AsyncIOMotorDatabase
from app.deduction.repositories.base_repository import BaseRepository
from app.deduction.models.employee_deduction_profile import EmployeeDeductionProfileModel

class EmployeeDeductionProfileRepository(BaseRepository[EmployeeDeductionProfileModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_deduction_profiles", EmployeeDeductionProfileModel)
