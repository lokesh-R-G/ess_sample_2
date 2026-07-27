from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate
from bson import ObjectId

class EmployeeValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employees"]
        
    async def validate_create(self, data: EmployeeCreate):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: EmployeeUpdate):
        pass 
