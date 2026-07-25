from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.employee_confirmation import EmployeeConfirmationCreate, EmployeeConfirmationUpdate
from bson import ObjectId

class EmployeeConfirmationValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_confirmations"]
        
    async def validate_create(self, data: EmployeeConfirmationCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeConfirmationUpdate):
        pass 
