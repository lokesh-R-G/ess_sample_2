from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee_contact import EmployeeContactModel

class EmployeeContactRepository(BaseRepository[EmployeeContactModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_contacts", EmployeeContactModel)
