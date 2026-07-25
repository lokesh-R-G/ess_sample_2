from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.employee_education import EmployeeEducationCreate, EmployeeEducationUpdate
from bson import ObjectId

class EmployeeEducationValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_educations"]
        
    async def validate_create(self, data: EmployeeEducationCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeEducationUpdate):
        pass 
