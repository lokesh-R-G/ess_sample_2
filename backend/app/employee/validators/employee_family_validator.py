from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.employee_family import EmployeeFamilyCreate, EmployeeFamilyUpdate
from bson import ObjectId

class EmployeeFamilyValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_familys"]
        
    async def validate_create(self, data: EmployeeFamilyCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeFamilyUpdate):
        pass 
