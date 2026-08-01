from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee_address import EmployeeAddressModel

class EmployeeAddressRepository(BaseRepository[EmployeeAddressModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_addresses", EmployeeAddressModel)
