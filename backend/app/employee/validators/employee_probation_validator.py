from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.employee_probation import EmployeeProbationCreate, EmployeeProbationUpdate
from bson import ObjectId

class EmployeeProbationValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_probations"]
        
    async def validate_create(self, data: EmployeeProbationCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeProbationUpdate):
        pass 
