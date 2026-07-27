from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee_emergency_contact import EmployeeEmergencyContactModel

class EmployeeEmergencyContactRepository(BaseRepository[EmployeeEmergencyContactModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_emergency_contacts", EmployeeEmergencyContactModel)
