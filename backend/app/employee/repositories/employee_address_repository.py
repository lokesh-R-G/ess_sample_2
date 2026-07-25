from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.employee_address import EmployeeAddressModel

class EmployeeAddressRepository(BaseRepository[EmployeeAddressModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employee_address", EmployeeAddressModel)
