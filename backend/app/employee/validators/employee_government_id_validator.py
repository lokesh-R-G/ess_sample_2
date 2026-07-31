from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee_government_id import EmployeeGovernmentIdCreate, EmployeeGovernmentIdUpdate

class EmployeeGovernmentIdValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def validate_create(self, data: EmployeeGovernmentIdCreate):
        pass
        
    async def validate_update(self, id: str, data: EmployeeGovernmentIdUpdate):
        pass
