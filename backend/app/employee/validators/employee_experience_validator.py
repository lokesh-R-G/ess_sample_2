from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee_experience import EmployeeExperienceCreate, EmployeeExperienceUpdate
from bson import ObjectId

class EmployeeExperienceValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_experiences"]
        
    async def validate_create(self, data: EmployeeExperienceCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeExperienceUpdate):
        pass 
