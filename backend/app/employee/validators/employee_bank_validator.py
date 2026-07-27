from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee_bank import EmployeeBankCreate, EmployeeBankUpdate
from bson import ObjectId

class EmployeeBankValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_banks"]
        
    async def validate_create(self, data: EmployeeBankCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeBankUpdate):
        pass 
