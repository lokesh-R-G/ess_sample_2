from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee_personal import EmployeePersonalCreate, EmployeePersonalUpdate
from bson import ObjectId

class EmployeePersonalValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_personals"]
        
    async def validate_create(self, data: EmployeePersonalCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeePersonalUpdate):
        pass 
